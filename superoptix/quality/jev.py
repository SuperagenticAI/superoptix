"""Jev / System One quality-control mapping for Agent Quality Records.

Shared vocabulary (SuperGauge RFC 0004):
  Choice accept / warn / reject  →  AQR decision ship / hold / reject
  (warn maps to hold / soft-hold)

Judged scores, Noul, and confidence MUST NEVER alone hard-gate ship.
Soft-hold on low confidence is emitter policy recorded in decision.rationale.
Deterministic gates stay independent (compose SuperQode or real policy probes
for a path to L2). This module does not invent fake gates.

References:
  https://github.com/SuperagenticAI/supergauge/blob/main/rfcs/0004-jev-systemone-interop.md
  https://github.com/SuperagenticAI/supergauge/blob/main/rfcs/0005-test-integrity-reward-hack.md
  https://github.com/SuperagenticAI/supergauge/blob/main/docs/emitters/jev-systemone.md
  https://github.com/SuperagenticAI/supergauge/blob/main/packs/assurance-export.md
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping

ChoiceLabel = Literal["accept", "warn", "reject"]
VerdictLabel = Literal["ship", "hold", "reject"]

CHOICE_TO_VERDICT: dict[str, VerdictLabel] = {
    "accept": "ship",
    "warn": "hold",
    "reject": "reject",
}

DEFAULT_JUDGE_ID = "typesafe/jev@1"
DEFAULT_MIN_CONFIDENCE = 0.75
DEFAULT_MODEL_HINT = "jev-1.13.0"


@dataclass(frozen=True)
class DispositionJudgment:
    """Typed disposition independent of whether ``dspy[typesafe]`` is installed.

    Mirrors System One Choice fields so AQR emission works with mocked or live
    answers. Optional ``score`` / ``noul`` are recorded as judged signals only.
    """

    choice: ChoiceLabel
    confidence: float
    probabilities: Mapping[str, float] | None = None
    score: float | None = None
    score_level: int | None = None
    noul: float | None = None
    model: str | None = None
    pack_digest: str | None = None
    judge_id: str = DEFAULT_JUDGE_ID
    rationale: str | None = None
    source: str = "heuristic"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.probabilities is not None:
            payload["probabilities"] = dict(self.probabilities)
        return payload


@dataclass(frozen=True)
class ThresholdVersion:
    """Version tag for ReAnchor / threshold moves (Prefactor: Jev swap = component change).

    Keep outcome evidence so later calibration can compare versions without
    rewriting the question pack in place.
    """

    version: str
    min_confidence: float = DEFAULT_MIN_CONFIDENCE
    choice_weights: Mapping[str, float] | None = None
    score_cuts: tuple[float, ...] | None = None
    previous_version: str | None = None
    evidence_ref: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": self.version,
            "min_confidence": self.min_confidence,
        }
        if self.choice_weights is not None:
            payload["choice_weights"] = dict(self.choice_weights)
        if self.score_cuts is not None:
            payload["score_cuts"] = list(self.score_cuts)
        if self.previous_version:
            payload["previous_version"] = self.previous_version
        if self.evidence_ref:
            payload["evidence_ref"] = self.evidence_ref
        if self.notes:
            payload["notes"] = self.notes
        return payload


def typesafe_available() -> bool:
    """Return True when ``dspy.experimental`` decision types import cleanly."""
    try:
        from dspy.experimental import Choice, Score, TypeSafe  # noqa: F401
    except Exception:
        return False
    return True


def digest_pack_bytes(data: bytes | str | Mapping[str, Any]) -> str:
    """Content-address a frozen question pack as ``sha256:...`` (SPEC §7)."""
    if isinstance(data, Mapping):
        payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    elif isinstance(data, str):
        payload = data.encode()
    else:
        payload = data
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def choice_to_verdict(choice: str) -> VerdictLabel:
    """Map Choice accept/warn/reject to AQR ship/hold/reject."""
    key = str(choice).strip().lower()
    if key not in CHOICE_TO_VERDICT:
        raise ValueError(
            f"Unknown Choice label {choice!r}; expected accept, warn, or reject"
        )
    return CHOICE_TO_VERDICT[key]


def resolve_verdict(
    choice: str,
    confidence: float,
    *,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> tuple[VerdictLabel, str | None]:
    """Resolve AQR verdict with soft-hold on low confidence.

    Soft-hold applies only when the mapped Choice would otherwise ship.
    Confidence never becomes a deterministic gate entry.
    """
    verdict = choice_to_verdict(choice)
    conf = float(confidence)
    if verdict == "ship" and conf < float(min_confidence):
        return (
            "hold",
            (
                f"Soft-hold: Choice accept with confidence {conf:.2f} below "
                f"emitter min_confidence {float(min_confidence):.2f}. "
                "Deterministic gates (if any) are unchanged; judged confidence "
                "does not alone hard-gate ship."
            ),
        )
    return verdict, None


def pin_assurance_judge(
    assurance: dict[str, Any] | None,
    *,
    model: str,
    pack_digest: str | None = None,
    judge_id: str = DEFAULT_JUDGE_ID,
    human_agreement_kappa: float | None = None,
    sampled: int | None = None,
    calibration_ece: float | None = None,
) -> dict[str, Any]:
    """Populate ``assurance.judge`` per SuperGauge RFC 0004.

    Prefer a versioned model id (for example ``jev-1.13.0``) over aliases such
    as ``jev-latest``.
    """
    block = dict(assurance or {})
    judge: dict[str, Any] = {
        "id": judge_id,
        "model": model,
    }
    if pack_digest:
        judge["pack_digest"] = pack_digest
    if human_agreement_kappa is not None:
        judge["human_agreement_kappa"] = float(human_agreement_kappa)
    if sampled is not None:
        judge["sampled"] = int(sampled)
    if calibration_ece is not None:
        judge["calibration_ece"] = float(calibration_ece)
    block["judge"] = judge
    return block


def heuristic_disposition_from_evaluate(
    *,
    passed: int,
    total: int,
    confidence: float | None = None,
) -> DispositionJudgment:
    """Derive a Choice-shaped disposition from BDD evaluate totals (no API call).

    Used when ``--gauge-jev`` is set but a live TypeSafe call is unavailable, so
    AQR still records a typed disposition. Live Jev answers replace this when
    the optional adapter runs successfully.
    """
    if total <= 0:
        return DispositionJudgment(
            choice="warn",
            confidence=0.0 if confidence is None else float(confidence),
            rationale="No scored scenarios; holding for review.",
            source="heuristic-evaluate",
        )
    rate = passed / total
    if rate >= 0.9:
        choice: ChoiceLabel = "accept"
    elif rate < 0.5:
        choice = "reject"
    else:
        choice = "warn"
    # Confidence proxy from sample size and margin; not a calibrated probability.
    margin = abs(rate - 0.5) * 2.0
    sample = min(1.0, total / 10.0)
    derived = 0.35 + 0.55 * margin * sample
    conf = float(confidence) if confidence is not None else round(derived, 3)
    return DispositionJudgment(
        choice=choice,
        confidence=conf,
        probabilities={
            "accept": round(rate, 3),
            "warn": round(max(0.0, 1.0 - abs(rate - 0.7) * 2), 3),
            "reject": round(1.0 - rate, 3),
        },
        rationale=(
            f"Heuristic disposition from evaluate: {passed}/{total} passed "
            f"(rate={rate:.3f}). Replace with live Jev Choice when configured."
        ),
        source="heuristic-evaluate",
    )


def heuristic_disposition_from_findings(
    *,
    score: int | float,
    findings: list[Mapping[str, Any]] | None = None,
) -> DispositionJudgment:
    """Map agent-card-review severity findings to Choice accept/warn/reject."""
    findings = list(findings or [])
    highs = sum(1 for f in findings if str(f.get("severity") or "").lower() == "high")
    mediums = sum(
        1 for f in findings if str(f.get("severity") or "").lower() == "medium"
    )
    value = float(score)
    if highs or value < 50:
        choice: ChoiceLabel = "reject"
    elif mediums or value < 80:
        choice = "warn"
    else:
        choice = "accept"
    # Map 0-100 card score onto [0, 1] confidence-shaped signal for soft-hold.
    conf = round(min(1.0, max(0.0, value / 100.0)), 3)
    return DispositionJudgment(
        choice=choice,
        confidence=conf,
        score=value,
        rationale=(
            f"Card-review disposition from score {value}/100 with "
            f"{highs} high and {mediums} medium finding(s)."
        ),
        source="heuristic-card-review",
    )


def judgment_from_choice_object(
    obj: Any, *, model: str | None = None
) -> DispositionJudgment:
    """Normalize a DSPy Choice instance or Mapping into DispositionJudgment."""
    if isinstance(obj, DispositionJudgment):
        return obj
    if isinstance(obj, Mapping):
        choice = str(obj.get("choice") or obj.get("value") or "").lower()
        return DispositionJudgment(
            choice=choice,  # type: ignore[arg-type]
            confidence=float(obj.get("confidence") or 0.0),
            probabilities=obj.get("probabilities"),
            score=obj.get("score"),
            score_level=obj.get("level") or obj.get("score_level"),
            noul=obj.get("noul"),
            model=obj.get("model") or model,
            pack_digest=obj.get("pack_digest"),
            judge_id=str(obj.get("judge_id") or DEFAULT_JUDGE_ID),
            rationale=obj.get("rationale"),
            source=str(obj.get("source") or "mapping"),
        )
    value = getattr(obj, "value", None)
    if value is None and hasattr(obj, "choice"):
        value = getattr(obj, "choice")
    confidence = float(getattr(obj, "confidence", 0.0) or 0.0)
    probs = getattr(obj, "probabilities", None)
    return DispositionJudgment(
        choice=str(value).lower(),  # type: ignore[arg-type]
        confidence=confidence,
        probabilities=dict(probs) if probs else None,
        model=model,
        source="typesafe-choice",
    )
