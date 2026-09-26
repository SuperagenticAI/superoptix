"""Optional quality-control adapters (Jev / System One) for SuperOptiX.

Core mapping and soft-hold logic live here and do not require ``dspy[typesafe]``.
Live TypeSafe / Jev calls are loaded lazily from
``superoptix.quality.typesafe_adapter`` when the optional extra is installed.

Ownership split with SuperGauge:
- SuperGauge owns AQR shape, gate policy, assurance pinning, RFC 0004 / 0005.
- SuperOptiX owns optional adapters, Propose-Don't-Judge admission wiring,
  ReAnchor version tags, and AQR emission when evaluate / card-review asks.
"""

from __future__ import annotations

from superoptix.quality.admission import admit_proposal
from superoptix.quality.jev import (
    CHOICE_TO_VERDICT,
    DEFAULT_JUDGE_ID,
    DEFAULT_MIN_CONFIDENCE,
    DispositionJudgment,
    ThresholdVersion,
    choice_to_verdict,
    digest_pack_bytes,
    heuristic_disposition_from_evaluate,
    heuristic_disposition_from_findings,
    pin_assurance_judge,
    resolve_verdict,
    typesafe_available,
)

__all__ = [
    "CHOICE_TO_VERDICT",
    "DEFAULT_JUDGE_ID",
    "DEFAULT_MIN_CONFIDENCE",
    "DispositionJudgment",
    "ThresholdVersion",
    "admit_proposal",
    "choice_to_verdict",
    "digest_pack_bytes",
    "heuristic_disposition_from_evaluate",
    "heuristic_disposition_from_findings",
    "pin_assurance_judge",
    "resolve_verdict",
    "typesafe_available",
]
