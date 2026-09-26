"""Lazy ``dspy[typesafe]`` adapter for optional Jev / System One calls.

Not imported by default. Install with::

    pip install "superoptix[typesafe]"
    # or: pip install "dspy[typesafe]>=3.4"

Requires DSPy 3.4+ for ``dspy.experimental`` Choice / Score / Noul / ReAnchor /
TypeSafe. Set ``TYPESAFE_API_KEY``. Prefer a versioned model id such as
``jev-1.13.0`` over ``jev-latest`` when pinning assurance.judge.model.
"""

from __future__ import annotations

from typing import Any

from superoptix.quality.jev import (
    DEFAULT_JUDGE_ID,
    DEFAULT_MODEL_HINT,
    DispositionJudgment,
    ThresholdVersion,
    digest_pack_bytes,
)


class TypesafeUnavailable(ImportError):
    """Raised when the optional typesafe extra is not installed."""


def _import_experimental() -> tuple[Any, Any, Any, Any, Any]:
    try:
        from dspy.experimental import Choice, Noul, ReAnchor, Score, TypeSafe
    except ImportError as exc:  # pragma: no cover - exercised via typesafe_available
        raise TypesafeUnavailable(
            "dspy[typesafe] is not available. Install with "
            '`pip install "superoptix[typesafe]"` (needs DSPy 3.4+) and set '
            "TYPESAFE_API_KEY."
        ) from exc
    return Choice, Score, Noul, ReAnchor, TypeSafe


def release_disposition_type() -> Any:
    """Choice type for release disposition: accept / warn / reject."""
    Choice, *_rest = _import_experimental()
    return Choice[
        ("accept", "Ship: quality bar met for this emitter policy."),
        ("warn", "Hold / soft-hold: needs human review before ship."),
        ("reject", "Reject: do not ship on this evidence."),
    ]


def card_review_score_type() -> Any:
    """Score rubric aligned with card-review severity bands."""
    _Choice, Score, _Noul, _ReAnchor, _TypeSafe = _import_experimental()
    return Score[
        "reject-band: serious conformance or discoverability gaps",
        "warn-band: medium issues; review before publishing the card",
        "accept-band: card is publishable under local policy",
    ]


def make_typesafe_lm(model: str | None = None, **kwargs: Any) -> Any:
    """Construct ``dspy.experimental.TypeSafe`` without importing at module load."""
    *_rest, TypeSafe = _import_experimental()
    return TypeSafe(model or DEFAULT_MODEL_HINT, **kwargs)


def judge_evaluation_summary(
    summary: str,
    *,
    model: str | None = None,
    pack: dict[str, Any] | None = None,
) -> DispositionJudgment:
    """Ask Jev for a release Disposition Choice over an evaluation summary.

    Uses ``dspy.Predict`` with a Choice field. Callers must have
    ``TYPESAFE_API_KEY`` set. On failure, callers should fall back to
    ``heuristic_disposition_from_evaluate``.
    """
    import dspy

    _Choice, _Score, _Noul, _ReAnchor, TypeSafe = _import_experimental()
    Disposition = release_disposition_type()
    lm = TypeSafe(model or DEFAULT_MODEL_HINT)
    pack = pack or {
        "id": "superoptix/evaluate-disposition@1",
        "questions": {
            "disposition": {
                "type": "choice",
                "options": ["accept", "warn", "reject"],
            }
        },
    }
    pack_digest = digest_pack_bytes(pack)

    class ReleaseDisposition(dspy.Signature):
        """Judge whether this agent evaluation supports ship, soft-hold, or reject."""

        evaluation_summary: str = dspy.InputField()
        disposition: Disposition = dspy.OutputField()

    predict = dspy.Predict(ReleaseDisposition)
    with dspy.context(lm=lm):
        result = predict(evaluation_summary=summary)

    answer = result.disposition
    value = getattr(answer, "value", answer)
    confidence = float(getattr(answer, "confidence", 0.0) or 0.0)
    probs = getattr(answer, "probabilities", None)
    resolved_model = getattr(lm, "model", None) or model or DEFAULT_MODEL_HINT
    return DispositionJudgment(
        choice=str(value).lower(),  # type: ignore[arg-type]
        confidence=confidence,
        probabilities=dict(probs) if probs else None,
        model=str(resolved_model),
        pack_digest=pack_digest,
        judge_id=DEFAULT_JUDGE_ID,
        rationale="Live Jev Choice over evaluation summary.",
        source="typesafe-live",
    )


def reanchor_version_tag(
    *,
    version: str,
    program: Any | None = None,
    metric: Any | None = None,
    trainset: Any | None = None,
) -> dict[str, Any]:
    """Return a version-tagged ReAnchor / threshold note.

    Prefactor: swapping the Jev / TypeSafe component is a component change;
    keep prior outcome evidence under ``evidence_ref`` rather than silently
    rewriting thresholds. When ReAnchor cannot run (missing extra or args),
    returns the version tag only.
    """
    note = ThresholdVersion(
        version=version,
        notes=(
            "ReAnchor calibrates Choice weights / Score cuts / Noul thresholds. "
            "Tag every move; retain prior evidence for calibration. "
            "Jev model or pack swap is a component change (Prefactor)."
        ),
    )
    if program is None or metric is None or trainset is None:
        return note.to_dict()
    _Choice, _Score, _Noul, ReAnchor, _TypeSafe = _import_experimental()
    optimizer = ReAnchor()
    optimized = optimizer.compile(program, trainset=trainset, metric=metric)
    payload = note.to_dict()
    payload["reanchor_applied"] = True
    payload["program_type"] = type(optimized).__name__
    return payload
