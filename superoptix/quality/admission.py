"""Propose-Don't-Judge admission helpers for GEPA / optimizers.

The optimizer proposes candidates. A frozen referee admits via Score / Choice
when the optional typesafe path is configured. Confidence alone never hard-gates
admission to "ship"; low confidence soft-holds for human review.

This module does not import ``dspy[typesafe]`` at load time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Mapping

from superoptix.quality.jev import (
    DEFAULT_MIN_CONFIDENCE,
    DispositionJudgment,
    choice_to_verdict,
    judgment_from_choice_object,
    resolve_verdict,
)

AdmissionAction = Literal["admit", "hold", "reject"]


@dataclass(frozen=True)
class AdmissionResult:
    action: AdmissionAction
    verdict: str
    rationale: str
    judgment: DispositionJudgment | None = None
    metric_value: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "verdict": self.verdict,
            "rationale": self.rationale,
            "judgment": self.judgment.to_dict() if self.judgment else None,
            "metric_value": self.metric_value,
        }


def admit_proposal(
    proposal: Any = None,
    *,
    referee: DispositionJudgment | Mapping[str, Any] | Any | None = None,
    metric_value: float | None = None,
    metric_floor: float | None = None,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    referee_fn: Callable[[Any], Any] | None = None,
) -> AdmissionResult:
    """Admit or hold a proposed candidate.

    Priority:
    1. ``referee_fn(proposal)`` when provided (may return Choice / Mapping).
    2. Explicit ``referee`` judgment.
    3. Scalar ``metric_value`` vs optional ``metric_floor`` (legacy path; not
       a System One hard gate on confidence).

    Soft-hold: Choice accept with low confidence → hold, not admit.
    """
    judgment: DispositionJudgment | None = None

    if referee_fn is not None and referee is None:
        referee = referee_fn(proposal)

    if referee is not None:
        judgment = judgment_from_choice_object(referee)
        verdict, soft = resolve_verdict(
            judgment.choice,
            judgment.confidence,
            min_confidence=min_confidence,
        )
        if verdict == "ship":
            action: AdmissionAction = "admit"
        elif verdict == "reject":
            action = "reject"
        else:
            action = "hold"
        rationale = soft or judgment.rationale or (
            f"Referee Choice {judgment.choice!r} → AQR {verdict}"
        )
        return AdmissionResult(
            action=action,
            verdict=verdict,
            rationale=rationale,
            judgment=judgment,
            metric_value=metric_value,
        )

    if metric_value is not None and metric_floor is not None:
        if float(metric_value) >= float(metric_floor):
            return AdmissionResult(
                action="admit",
                verdict="ship",
                rationale=(
                    f"Metric {metric_value} met floor {metric_floor}. "
                    "No System One referee was configured."
                ),
                metric_value=float(metric_value),
            )
        return AdmissionResult(
            action="reject",
            verdict="reject",
            rationale=f"Metric {metric_value} below floor {metric_floor}.",
            metric_value=float(metric_value),
        )

    return AdmissionResult(
        action="hold",
        verdict="hold",
        rationale="No referee Choice/Score and no metric floor; holding proposal.",
        metric_value=metric_value,
    )


def map_choice_label(choice: str) -> str:
    """Public helper: Choice label → AQR verdict string."""
    return choice_to_verdict(choice)
