"""Built-in SuperGauge conformance precheck used by ``super agent test``.

Mirrors the L1 presence and L2 rules of SuperGauge ``conformance/check.py`` at
the pinned revision (``gauge_checks.SUPERGAUGE_CHECKER_REV``, tag
checker-v0.1.0), including the ``--require-ship`` release rules so the CLI can
gate without network access. It is a precheck, not the authority: pass
``--checker /path/to/supergauge/conformance/check.py`` (or set
``SUPERGAUGE_CHECKER``) to run the pinned upstream checker as well. The
SuperOptiX test suite runs the upstream checker on generated records, which
keeps the two in step.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LEVELS = ("L1", "L2", "L3", "L4")
_DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
_REQUIRED = (
    "supergauge record_id emitted_at profile subject "
    "task_set measures gates assurance decision"
).split()
# Judged measures in the SuperGauge registry (type: judged) at the pinned rev.
JUDGED = frozenset({"answer.grounded", "robustness.multi_turn"})


def check_levels(record: Dict[str, Any]) -> Dict[str, List[str]]:
    failures: Dict[str, List[str]] = {lv: [] for lv in LEVELS}
    for key in _REQUIRED:
        if key not in record:
            failures["L1"].append(f"missing required block: {key}")
    subject = record.get("subject") or {}
    task_set = record.get("task_set") or {}
    for name, value in (
        ("subject.harness_digest", subject.get("harness_digest")),
        ("task_set.manifest_digest", task_set.get("manifest_digest")),
    ):
        if value is not None and not _DIGEST.match(str(value)):
            failures["L1"].append(f"{name} is not a full sha256 digest")
    for m in record.get("measures") or []:
        if str(m.get("id", "")).startswith("x-"):
            failures["L2"].append(f"x- measure {m.get('id')} caps the record at L1")

    gates = record.get("gates") or []
    if not gates:
        failures["L2"].append("no gates recorded")
    for gate in gates:
        if gate.get("id") in JUDGED:
            failures["L2"].append(f"gate {gate.get('id')} is model-graded")
    if not task_set.get("sealed"):
        failures["L2"].append("held-out split is not sealed")
    if not task_set.get("held_out"):
        failures["L2"].append("no held-out split recorded")
    if not task_set.get("canary_ids"):
        failures["L2"].append("no contamination probes recorded")
    if (record.get("decision") or {}).get("verdict") == "ship":
        failed = [g.get("id") for g in gates if g.get("result") != "pass"]
        if failed:
            failures["L2"].append(
                "ship verdict with failing gates: " + ", ".join(failed)
            )
    reported = {m.get("id") for m in record.get("measures") or []}
    for gate in gates:
        if gate.get("floor") is not None and gate.get("id") not in reported:
            failures["L2"].append(f"gate {gate.get('id')} has a floor but no measure")

    for gate in gates:
        if gate.get("floor") is None:
            continue
        matches = [
            m
            for m in record.get("measures") or []
            if m.get("id") == gate.get("id")
            and (gate.get("split") is None or m.get("split") == gate["split"])
        ]
        if len(matches) != 1:
            failures["L2"].append(f"gate {gate.get('id')} needs one matching measure")
            continue
        value = matches[0].get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            failures["L2"].append(f"gate {gate.get('id')} needs a numeric value")
        elif gate.get("result") == "pass" and value < gate["floor"]:
            failures["L2"].append(f"gate {gate.get('id')} reports pass below its floor")

    by_id = {m.get("id"): m for m in record.get("measures") or []}
    phk = by_id.get("reliability.pass_hat_k")
    if phk is None or (phk.get("k") or 0) < 2:
        failures["L3"].append("reliability.pass_hat_k with k >= 2 not reported")
    assurance = record.get("assurance") or {}
    if not assurance.get("evaluator_independent"):
        failures["L3"].append("assurance.evaluator_independent is not asserted")
    decision = record.get("decision") or {}
    evidence = assurance.get("evidence") or {}
    if not decision.get("signature"):
        failures["L4"].append("record is unsigned")
    if not decision.get("rolls_back_to"):
        failures["L4"].append("no rollback target recorded")
    if not (
        evidence.get("replayable") and evidence.get("ledger") and evidence.get("events")
    ):
        failures["L4"].append("no replayable ledger with an event count")
    return failures


def highest_level(failures: Dict[str, List[str]]) -> Optional[str]:
    reached = None
    for lv in LEVELS:
        if failures[lv]:
            break
        reached = lv
    return reached


def release_blockers(record: Dict[str, Any], reached: Optional[str]) -> List[str]:
    """``--require-ship`` rules: L2+, ship verdict, named actor, passing gates."""
    from superoptix.gauge_checks import named_actor

    decision = record.get("decision") or {}
    blockers = []
    if decision.get("verdict") != "ship":
        blockers.append("release requires decision.verdict: ship")
    if not named_actor(decision.get("actor")):
        blockers.append("release requires a named decision.actor")
    gates = record.get("gates") or []
    if not gates or any(g.get("result") != "pass" for g in gates):
        blockers.append("release requires passing deterministic gates")
    if reached is None or LEVELS.index(reached) < LEVELS.index("L2"):
        blockers.append("release requires L2 or higher")
    return blockers


def gate_exit_code(
    record: Dict[str, Any], level: str
) -> Tuple[int, Optional[str], Dict[str, List[str]]]:
    """Exit code with ``check.py --level LEVEL --require-ship`` semantics.

    0 when the release is allowed and the level is met, otherwise 1. Release
    blockers are returned under the ``release`` key.
    """
    failures = check_levels(record)
    reached = highest_level(failures)
    failures["release"] = release_blockers(record, reached)
    if failures["release"]:
        return 1, reached, failures
    if reached is None or LEVELS.index(reached) < LEVELS.index(level):
        return 1, reached, failures
    return 0, reached, failures


def run_upstream_checker(checker: str, record_path: str | Path, level: str) -> int:
    """Run a pinned SuperGauge check.py with --level and --require-ship."""
    path = Path(os.path.expanduser(checker))
    if not path.exists():
        raise FileNotFoundError(f"SuperGauge checker not found: {path}")
    proc = subprocess.run(
        [
            sys.executable,
            str(path),
            str(record_path),
            "--level",
            level,
            "--require-ship",
        ],
        check=False,
    )
    return proc.returncode
