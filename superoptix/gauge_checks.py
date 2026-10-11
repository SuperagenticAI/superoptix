"""Deterministic SuperGauge measures, gates and integrity for SuperOptiX (2.0).

SuperGauge owns the record schema, measure registry and gate policy; this
module fills them from what a SuperOptiX evaluation actually produced. Every
helper returns ``None`` (or omits the entry) when the run did not produce the
data a measure needs. Nothing here defaults a measure, invents a gate or
promotes judged evidence to a gate.

Measure and gate ids come from the SuperGauge registry as of
SuperagenticAI/supergauge PR #6 (merged as a5920cc, tag checker-v0.1.0):
``output.parse_rate``, ``reliability.beats_trivial_baseline``,
``reliability.pass_hat_k``, ``trajectory.valid``, ``tool.correctness`` and
``assurance.holdout_sealed``.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

# SuperGauge checker pin: tag checker-v0.1.0 (squash merge of PR #6).
SUPERGAUGE_CHECKER_TAG = "checker-v0.1.0"
SUPERGAUGE_CHECKER_REV = "a5920cce2f81b55673756860143ba39835d35f1a"

# Deterministic measures SuperOptiX may gate on. Judged measures never appear.
DETERMINISTIC_GATE_IDS = (
    "output.parse_rate",
    "reliability.beats_trivial_baseline",
    "reliability.pass_hat_k",
    "trajectory.valid",
    "tool.correctness",
    "assurance.holdout_sealed",
)

# SuperOptiX local default floors. SuperGauge publishes no floors at 0.1
# (SPEC section 4.3); these are implementer floors, recorded in each gate so a
# reader sees exactly what was enforced. Override per playbook
# (spec.quality.gates) or per run (--gate-floor ID=VALUE).
DEFAULT_FLOORS: Dict[str, float] = {
    "output.parse_rate": 0.95,
    "reliability.pass_hat_k": 0.6,
    "trajectory.valid": 0.9,
    "tool.correctness": 0.9,
}

TRIVIAL_BASELINE_ID = "echo-input"
BASELINE_MEASURE = "task.completion"


def _digest(payload: Any) -> str:
    text = json.dumps(payload, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _snake(name: str) -> str:
    text = re.sub(r"[^0-9a-zA-Z]+", "_", str(name)).strip("_")
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    return text.lower()


# ---------------------------------------------------------------------------
# Sealed held-out split (B1)
# ---------------------------------------------------------------------------


@dataclass
class SealResult:
    """Outcome of checking the evaluated scenarios against the GEPA split."""

    sealed: bool
    reason: str
    digest: Optional[str] = None
    heldout_ids: List[str] = field(default_factory=list)
    held_in: int = 0
    held_out: int = 0


def is_canary(scenario: Dict[str, Any]) -> bool:
    """A contamination probe: a scenario marked ``canary: true``."""
    return bool(scenario.get("canary"))


def seal_holdout(
    scenarios: Sequence[Dict[str, Any]],
    holdout_record: Optional[Dict[str, Any]],
) -> SealResult:
    """Derive ``sealed`` from the GEPA held-out split, never from a flag alone.

    Sealed is true only when a held-out record written by
    ``super agent optimize`` exists, it carries a digest, every held-out id is
    still present in the playbook, and the digest recomputed from the current
    playbook content equals the recorded one.
    """
    from superoptix.optimizers.holdout import (
        example_id,
        scenario_identity,
        split_digest,
    )

    candidates = [s for s in scenarios if isinstance(s, dict) and not is_canary(s)]
    if not holdout_record:
        return SealResult(
            False,
            "no held-out split recorded; run super agent optimize (GEPA) first",
            held_in=len(candidates),
        )
    digest = holdout_record.get("split_digest")
    ids = list(holdout_record.get("heldout_ids") or [])
    if not digest or not ids:
        reason = holdout_record.get("fallback_reason") or "held-out split is empty"
        return SealResult(
            False, f"no held-out split: {reason}", held_in=len(candidates)
        )

    wanted = set(ids)
    identities = [scenario_identity(s) for s in candidates]
    present = [ident for ident in identities if example_id(ident) in wanted]
    found = {example_id(ident) for ident in present}
    if found != wanted:
        return SealResult(
            False,
            f"{len(wanted - found)} held-out scenario(s) changed or removed since optimization",
            digest=digest,
        )
    recomputed = split_digest(present)
    if recomputed != digest:
        return SealResult(False, "held-out digest mismatch", digest=digest)
    return SealResult(
        True,
        "held-out split from the GEPA run; never passed to the optimizer",
        digest=digest,
        heldout_ids=sorted(found),
        held_in=len(candidates) - len(present),
        held_out=len(present),
    )


# ---------------------------------------------------------------------------
# output.parse_rate (B2)
# ---------------------------------------------------------------------------


def declared_output_contract(spec: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Output fields the playbook declares, or None when it declares none.

    The runner's default ``response`` field is not a declared contract, so it
    does not count (output.parse_rate: no contract, no measure).
    """
    tasks = spec.get("tasks") or []
    if isinstance(tasks, list) and tasks and isinstance(tasks[0], dict):
        outs = tasks[0].get("outputs") or []
        fields = [f for f in outs if isinstance(f, dict) and f.get("name")]
        if fields:
            return fields
    outs = spec.get("output_fields") or []
    fields = [f for f in outs if isinstance(f, dict) and f.get("name")]
    return fields or None


def contract_digest(contract: Sequence[Dict[str, Any]]) -> str:
    return _digest(
        [
            {"name": _snake(f.get("name")), "type": str(f.get("type") or "str")}
            for f in contract
        ]
    )


_TYPE_CHECKS = {
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool": lambda v: isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "list": lambda v: isinstance(v, (list, tuple)),
    "array": lambda v: isinstance(v, (list, tuple)),
    "dict": lambda v: isinstance(v, dict),
    "object": lambda v: isinstance(v, dict),
}


def _field_value(result: Any, name: str) -> Any:
    if isinstance(result, dict):
        return result.get(name)
    try:
        return getattr(result, name)
    except Exception:
        try:
            return result[name]
        except Exception:
            return None


def output_parsed(result: Any, contract: Sequence[Dict[str, Any]]) -> bool:
    """True when every declared output field is present, non-empty and typed.

    Checked on the program output as returned; nothing is repaired here.
    """
    if result is None or isinstance(result, str):
        return False
    for spec in contract:
        value = _field_value(result, _snake(spec.get("name")))
        if value is None or (isinstance(value, str) and not value.strip()):
            return False
        check = _TYPE_CHECKS.get(str(spec.get("type") or "").lower())
        if check is not None and not check(value):
            return False
    return True


def parse_rate_measure(
    results: Sequence[Dict[str, Any]],
    contract: Optional[Sequence[Dict[str, Any]]],
    split: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not contract:
        return None
    flags = [r["parsed"] for r in results if isinstance(r.get("parsed"), bool)]
    if not flags:
        return None
    entry: Dict[str, Any] = {
        "id": "output.parse_rate",
        "value": round(sum(flags) / len(flags), 3),
        "n": len(flags),
        "schema_digest": contract_digest(contract),
    }
    if split:
        entry["split"] = split
    return entry


# ---------------------------------------------------------------------------
# reliability.beats_trivial_baseline (B2)
# ---------------------------------------------------------------------------


def beats_baseline_measure(
    *,
    candidate_value: float,
    baseline_value: float,
    n: int,
    baseline_id: str = TRIVIAL_BASELINE_ID,
    measure: str = BASELINE_MEASURE,
    margin: float = 0.0,
    split: Optional[str] = None,
) -> Dict[str, Any]:
    """Strict comparison c > b + m, with the baseline object SuperGauge requires."""
    entry: Dict[str, Any] = {
        "id": "reliability.beats_trivial_baseline",
        "value": bool(candidate_value > baseline_value + margin),
        "n": int(n),
        "baseline": {
            "id": baseline_id,
            "value": round(float(baseline_value), 3),
            "measure": measure,
            "candidate_value": round(float(candidate_value), 3),
            "margin": float(margin),
        },
    }
    if split:
        entry["split"] = split
    return entry


# ---------------------------------------------------------------------------
# reliability.pass_hat_k (B2)
# ---------------------------------------------------------------------------


def pass_hat_k_measures(
    runs: Sequence[Sequence[Dict[str, Any]]],
    split: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """pass^k and pass@k across k independent runs (k >= 2), keyed by result id."""
    per_task: Dict[str, List[bool]] = {}
    for run in runs:
        for result in run:
            if result.get("status") in {"passed", "failed"}:
                key = str(result.get("id") or "")
                per_task.setdefault(key, []).append(result["status"] == "passed")
    k = len(runs)
    complete = {t: r for t, r in per_task.items() if len(r) == k}
    if k < 2 or not complete:
        return []
    n = len(complete)
    out = []
    for mid, fn in (("reliability.pass_hat_k", all), ("reliability.pass_at_k", any)):
        entry = {
            "id": mid,
            "value": round(sum(1 for r in complete.values() if fn(r)) / n, 3),
            "k": k,
            "n": n,
        }
        if split:
            entry["split"] = split
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# tool.correctness and trajectory.valid (B2), from recorded tool calls only
# ---------------------------------------------------------------------------


def tool_calls_from_trajectory(trajectory: Any) -> Optional[List[Dict[str, Any]]]:
    """Read DSPy ReAct ``trajectory`` (tool_name_i / tool_args_i / observation_i)."""
    if not isinstance(trajectory, dict):
        return None
    calls = []
    i = 0
    while f"tool_name_{i}" in trajectory:
        name = trajectory.get(f"tool_name_{i}")
        if name and name != "finish":
            calls.append(
                {
                    "name": str(name),
                    "arguments": trajectory.get(f"tool_args_{i}") or {},
                    "observation": trajectory.get(f"observation_{i}"),
                }
            )
        i += 1
    return calls if i else None


def _call_key(call: Dict[str, Any]) -> str:
    return json.dumps(
        [call.get("name"), call.get("arguments")], sort_keys=True, default=str
    )


def tool_correctness_measure(
    results: Sequence[Dict[str, Any]],
    declared_tools: Optional[Iterable[str]],
    split: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Existence and redundancy checks over recorded tool calls.

    Schema checks are skipped (tools carry no published argument schema in the
    playbook) and selection is checked only where a scenario declares
    ``expected_tools``. Runs with zero invocations are excluded.
    """
    if declared_tools is None:
        return None
    surface = {str(t) for t in declared_tools}
    total = good = 0
    for result in results:
        calls = result.get("tool_calls")
        if not calls:
            continue
        expected = result.get("expected_tools")
        seen: Dict[str, Any] = {}
        for call in calls:
            total += 1
            ok = call.get("name") in surface
            if expected and call.get("name") not in set(expected):
                ok = False
            key = _call_key(call)
            if key in seen and seen[key] == call.get("observation"):
                ok = False
            seen[key] = call.get("observation")
            good += int(ok)
    if not total:
        return None
    entry: Dict[str, Any] = {
        "id": "tool.correctness",
        "value": round(good / total, 3),
        "n": total,
    }
    if split:
        entry["split"] = split
    return entry


def trajectory_valid(
    calls: Sequence[Dict[str, Any]], constraints: Dict[str, Any]
) -> bool:
    names = [c.get("name") for c in calls]
    for step in constraints.get("required_steps") or []:
        if step not in names:
            return False
    for step in constraints.get("forbidden_steps") or []:
        if step in names:
            return False
    max_steps = constraints.get("max_steps")
    if max_steps is not None and len(calls) > int(max_steps):
        return False
    if constraints.get("no_cycles"):
        threshold = int(constraints.get("cycle_threshold", 2))
        counts: Dict[str, int] = {}
        for call in calls:
            key = _call_key(call)
            counts[key] = counts.get(key, 0) + 1
            if counts[key] > threshold:
                return False
    return True


def trajectory_measure(
    results: Sequence[Dict[str, Any]], split: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Only over scenarios that declare ``trajectory`` constraints and recorded calls."""
    flags = [
        trajectory_valid(r.get("tool_calls") or [], r["trajectory_constraints"])
        for r in results
        if r.get("trajectory_constraints") and r.get("tool_calls") is not None
    ]
    if not flags:
        return None
    entry: Dict[str, Any] = {
        "id": "trajectory.valid",
        "value": round(sum(flags) / len(flags), 3),
        "n": len(flags),
    }
    if split:
        entry["split"] = split
    return entry


# ---------------------------------------------------------------------------
# Gates, integrity and decision (B2, B3)
# ---------------------------------------------------------------------------


def build_gates(
    measures: Sequence[Dict[str, Any]],
    floors: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """One deterministic gate per reported deterministic measure.

    Floors apply to rate measures; boolean measures pass when true. Judged
    measures are never gated.
    """
    floors = {**DEFAULT_FLOORS, **(floors or {})}
    gates: List[Dict[str, Any]] = []
    for m in measures:
        mid = m.get("id")
        if mid not in DETERMINISTIC_GATE_IDS or mid == "reliability.pass_at_k":
            continue
        value = m.get("value")
        gate: Dict[str, Any] = {"id": mid, "source": "native"}
        if isinstance(value, bool):
            gate["result"] = "pass" if value else "fail"
        else:
            floor = floors.get(mid)
            if floor is None:
                continue
            gate["floor"] = float(floor)
            gate["result"] = "pass" if float(value) >= float(floor) else "fail"
        if m.get("split"):
            gate["split"] = m["split"]
        gates.append(gate)
    return gates


def canary_outcomes(results: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Canary probes are unpassable by design: expected fail."""
    return [
        {
            "id": str(r["id"]),
            "expected": "fail",
            "observed": "pass" if r.get("status") == "passed" else "fail",
        }
        for r in results
        if r.get("canary") and r.get("status") in {"passed", "failed"}
    ]


def decide(record: Dict[str, Any], actor: str) -> Dict[str, Any]:
    """Deterministic release policy for ``super agent test``.

    ship only when there is at least one gate, every gate passes, the
    held-out split is sealed, at least one canary was recorded and none fired.
    Otherwise hold, with the reasons. Judged evidence plays no part here.
    """
    reasons: List[str] = []
    gates = record.get("gates") or []
    task_set = record.get("task_set") or {}
    integrity = (record.get("assurance") or {}).get("integrity") or {}
    if not gates:
        reasons.append("no deterministic gates")
    failed = [g["id"] for g in gates if g.get("result") != "pass"]
    if failed:
        reasons.append("failing gates: " + ", ".join(failed))
    if not task_set.get("sealed"):
        reasons.append("held-out split not sealed")
    if not task_set.get("canary_ids"):
        reasons.append("no contamination probes (canary scenarios)")
    if not named_actor(actor):
        reasons.append(
            "no named release actor (set SUPEROPTIX_RELEASE_ACTOR or --actor)"
        )
    fired = [
        c["id"]
        for c in integrity.get("canaries") or []
        if c["observed"] != c["expected"]
    ]
    if fired:
        reasons.append("canary probes passed: " + ", ".join(fired))
    verdict = "hold" if reasons else "ship"
    rationale = (
        "All deterministic gates passed on the sealed held-out split; no canary fired."
        if verdict == "ship"
        else "Hold: " + "; ".join(reasons) + "."
    )
    record["decision"] = {"verdict": verdict, "actor": actor, "rationale": rationale}
    return record


def named_actor(actor: Any) -> bool:
    """SuperGauge release approval needs a named actor, not empty or unknown."""
    return (
        isinstance(actor, str)
        and bool(actor.strip())
        and actor.strip().lower() != "unknown"
    )


def release_actor(explicit: Optional[str] = None) -> str:
    """Who approves: --actor, SUPEROPTIX_RELEASE_ACTOR, GITHUB_ACTOR, USER."""
    import os

    for value in (
        explicit,
        os.environ.get("SUPEROPTIX_RELEASE_ACTOR"),
        os.environ.get("GITHUB_ACTOR"),
        os.environ.get("USER"),
    ):
        if value and value.strip():
            return value.strip()
    return "unknown"


def mechanical_override(record: Dict[str, Any], judged_pass: bool) -> bool:
    """RFC 0005: a judged PASS loses to failing deterministic integrity.

    Returns True (and sets ``assurance.integrity.mechanical_override``) when a
    judged acceptance was overridden because a gate failed or a canary fired.
    """
    gates = record.get("gates") or []
    integrity = dict((record.get("assurance") or {}).get("integrity") or {})
    deterministic_fail = any(g.get("result") != "pass" for g in gates) or any(
        c["observed"] != c["expected"] for c in integrity.get("canaries") or []
    )
    overridden = bool(judged_pass and deterministic_fail)
    if judged_pass:
        integrity["mechanical_override"] = overridden
        record.setdefault("assurance", {})["integrity"] = integrity
    return overridden
