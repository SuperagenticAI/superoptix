"""Held-out split for GEPA optimization (SuperOptiX 2.0).

GEPA selects candidates on its validation set. When that set is the training
set, the reported gain is measured on the same items the optimizer was tuned
on and overstates what transfers to new inputs (arXiv:2610.09239). This module
carves a seeded held-out split out of the scenarios before optimization so
seed and optimized programs can be scored on items GEPA never saw.

The split digest is a sha256 over the canonical content of the held-out items.
It identifies the sealed set without publishing it, and the SuperGauge record
uses it as evidence for ``assurance.holdout_sealed``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

DEFAULT_VALSET_FRACTION = 0.2
MIN_HELDOUT = 2
MIN_TRAIN = 2


def example_payload(example: Any) -> Any:
    """Return a JSON-friendly view of one example for hashing."""
    if hasattr(example, "toDict") and callable(example.toDict):
        try:
            return example.toDict()
        except Exception:
            pass
    if hasattr(example, "__dataclass_fields__"):
        return asdict(example)
    if isinstance(example, dict):
        return dict(example)
    return repr(example)


def example_id(example: Any) -> str:
    """Stable content id for one example (sha256 of canonical JSON)."""
    payload = json.dumps(example_payload(example), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def split_digest(examples: Sequence[Any]) -> str:
    """Order-independent digest of a set of examples."""
    ids = sorted(example_id(ex) for ex in examples)
    return "sha256:" + hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


@dataclass
class HoldoutSplit:
    """Result of splitting examples into optimization and held-out sets."""

    train: List[Any]
    heldout: List[Any]
    fraction: float
    seed: int
    digest: Optional[str]
    heldout_ids: List[str] = field(default_factory=list)
    fallback_reason: Optional[str] = None

    @property
    def has_heldout(self) -> bool:
        return bool(self.heldout)

    def metadata(self) -> Dict[str, Any]:
        return {
            "valset_fraction": self.fraction,
            "seed": self.seed,
            "train_size": len(self.train),
            "heldout_size": len(self.heldout),
            "split_digest": self.digest,
            "heldout_ids": list(self.heldout_ids),
            "fallback_reason": self.fallback_reason,
        }


def split_holdout(
    examples: Sequence[Any],
    fraction: float = DEFAULT_VALSET_FRACTION,
    seed: int = 0,
    *,
    min_heldout: int = MIN_HELDOUT,
    min_train: int = MIN_TRAIN,
    identities: Optional[Sequence[Any]] = None,
) -> HoldoutSplit:
    """Split ``examples`` into a training part and a seeded held-out part.

    Small datasets cannot afford a held-out split. When the split would leave
    fewer than ``min_heldout`` held-out items or fewer than ``min_train``
    training items, every example is used for training, nothing is held out,
    a warning is logged and ``fallback_reason`` says why. Callers must then
    report the gain as train-only.

    ``identities`` optionally gives, per example, the payload hashed for the
    held-out ids and digest (for example the raw playbook scenario
    ``{**input, **expected_output}`` before retrieval augmentation), so the
    evaluator can recompute the same digest from the playbook.
    """
    items = list(examples)
    keys = list(identities) if identities is not None else items
    if len(keys) != len(items):
        raise ValueError("identities must have one entry per example")
    try:
        fraction = float(fraction)
    except (TypeError, ValueError):
        fraction = DEFAULT_VALSET_FRACTION
    seed = int(seed or 0)

    reason: Optional[str] = None
    if fraction <= 0:
        reason = "gepa.valset_fraction is 0; held-out evaluation disabled"
    elif fraction >= 1:
        reason = "gepa.valset_fraction must be below 1"
    else:
        n_heldout = max(min_heldout, int(round(len(items) * fraction)))
        if len(items) - n_heldout < min_train:
            reason = (
                f"dataset too small for a held-out split ({len(items)} examples; "
                f"need at least {min_heldout + min_train})"
            )

    if reason is not None:
        logger.warning("GEPA held-out split skipped: %s", reason)
        return HoldoutSplit(
            train=items,
            heldout=[],
            fraction=fraction,
            seed=seed,
            digest=None,
            fallback_reason=reason,
        )

    order = list(range(len(items)))
    random.Random(seed).shuffle(order)
    heldout_idx = set(order[:n_heldout])
    train = [ex for i, ex in enumerate(items) if i not in heldout_idx]
    heldout = [ex for i, ex in enumerate(items) if i in heldout_idx]
    heldout_keys = [k for i, k in enumerate(keys) if i in heldout_idx]
    return HoldoutSplit(
        train=train,
        heldout=heldout,
        fraction=fraction,
        seed=seed,
        digest=split_digest(heldout_keys),
        heldout_ids=sorted(example_id(k) for k in heldout_keys),
    )


def scenario_identity(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Identity payload of a playbook scenario: ``{**input, **expected_output}``."""
    inputs = scenario.get("input", {}) or {}
    expected = scenario.get("expected_output", {}) or {}
    return {**inputs, **expected}


def _as_float(value: Any) -> float:
    score = getattr(value, "score", value)
    try:
        return float(score)
    except (TypeError, ValueError):
        return 0.0


def score_dspy_program(
    program: Any, examples: Sequence[Any], metric: Callable[..., Any]
) -> Optional[float]:
    """Mean metric score of a DSPy program over examples. None if empty."""
    if not examples:
        return None
    total = 0.0
    for ex in examples:
        try:
            inputs = ex.inputs() if hasattr(ex, "inputs") else ex
            pred = program(**dict(inputs))
            total += _as_float(metric(ex, pred))
        except Exception as exc:  # a failed item scores zero, like GEPA
            logger.debug("held-out scoring failed for one item: %s", exc)
    return total / len(examples)


def gain_report(
    seed_train: Optional[float],
    optimized_train: Optional[float],
    seed_heldout: Optional[float],
    optimized_heldout: Optional[float],
) -> Dict[str, Any]:
    """Reported (train) gain next to held-out gain."""

    def diff(a: Optional[float], b: Optional[float]) -> Optional[float]:
        if a is None or b is None:
            return None
        return round(b - a, 4)

    def r(x: Optional[float]) -> Optional[float]:
        return None if x is None else round(x, 4)

    return {
        "seed_train_score": r(seed_train),
        "optimized_train_score": r(optimized_train),
        "reported_gain": diff(seed_train, optimized_train),
        "seed_heldout_score": r(seed_heldout),
        "optimized_heldout_score": r(optimized_heldout),
        "heldout_gain": diff(seed_heldout, optimized_heldout),
    }


HOLDOUT_RECORD_VERSION = 1


def write_holdout_record(path: Any, split: HoldoutSplit, gains: Dict[str, Any]) -> None:
    """Write split metadata (ids and digest, never content) to ``path``."""
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"version": HOLDOUT_RECORD_VERSION, **split.metadata(), **gains}
    target.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def read_holdout_record(path: Any) -> Optional[Dict[str, Any]]:
    """Read a held-out record written by :func:`write_holdout_record`."""
    from pathlib import Path

    target = Path(path)
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def predictor_instructions(program: Any) -> Dict[str, str]:
    """Map each named predictor of a DSPy program to its signature instructions."""
    out: Dict[str, str] = {}
    named = getattr(program, "named_predictors", None)
    if not callable(named):
        return out
    try:
        pairs = list(named())
    except Exception:
        return out
    for name, pred in pairs:
        sig = getattr(pred, "signature", None)
        text = getattr(sig, "instructions", None)
        if text is None:
            text = getattr(pred, "instructions", "")
        out[str(name)] = str(text or "")
    return out


UNCHANGED_SEED_WARNING = (
    "GEPA returned the unchanged seed program (no instruction changed and no "
    "score gain). The reflection model may have returned invalid structured "
    "JSON proposals. Treat this run as zero gain."
)


def unchanged_seed_report(
    seed_program: Any,
    optimized_program: Any,
    gains: Optional[Dict[str, Any]] = None,
    *,
    tolerance: float = 1e-9,
) -> Dict[str, Any]:
    """Advisory check: did GEPA return the seed program or produce zero gain?

    ``unchanged_seed`` is true when every predictor's instructions equal the
    seed's. ``zero_gain`` is true when the held-out gain (or the train gain
    if there is no held-out split) is known and not above ``tolerance``.
    ``warning`` is set when either holds. This is advisory and never a gate.
    """
    gains = gains or {}
    seed_instr = predictor_instructions(seed_program)
    opt_instr = predictor_instructions(optimized_program)
    compared = bool(seed_instr) and bool(opt_instr)
    changed = sorted(
        name
        for name in set(seed_instr) | set(opt_instr)
        if seed_instr.get(name) != opt_instr.get(name)
    )
    unchanged = compared and not changed

    gain = gains.get("heldout_gain")
    gain_source = "heldout"
    if gain is None:
        gain = gains.get("reported_gain")
        gain_source = "train"
    if gain is None:
        gain_source = None
    zero_gain = gain is not None and float(gain) <= tolerance

    warning = None
    if unchanged:
        warning = UNCHANGED_SEED_WARNING
    elif zero_gain:
        warning = (
            f"GEPA produced no {gain_source} gain ({float(gain):+.4f}) although "
            f"instructions changed for: {', '.join(changed) or 'n/a'}."
        )
    return {
        "unchanged_seed": unchanged,
        "instructions_compared": compared,
        "changed_predictors": changed,
        "zero_gain": zero_gain,
        "gain_source": gain_source,
        "warning": warning,
    }
