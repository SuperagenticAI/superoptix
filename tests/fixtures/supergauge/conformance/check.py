#!/usr/bin/env python3
"""SuperGauge conformance checker.

Reads one Agent Quality Record and reports the highest level it meets.

    python conformance/check.py record.yaml
    python conformance/check.py record.yaml --level L2   # exit non-zero below L2
    python conformance/check.py record.yaml --level L2 --require-ship
                                         # also exit non-zero unless verdict is ship

Levels are cumulative and self-asserted. This script reproduces the claim; it
issues no approval and prints no percentage.

Requires: pyyaml. jsonschema is optional and, when present, is used for L1.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SPEC_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SPEC_ROOT / "schema" / "agent-quality-record.schema.json"
REGISTRY_DIR = SPEC_ROOT / "measures"

LEVELS = ("L1", "L2", "L3", "L4")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")

# Measures that are graded by a model, and so may never back a gate. The
# registry front matter (`type: judged`) is the source of truth; this floor
# keeps the check meaningful if the script is vendored without measures/.
MODEL_GRADED_FLOOR = {"answer.grounded", "robustness.multi_turn"}
TYPE_LINE = re.compile(r"^type:\s*(\S+)\s*$", re.MULTILINE)


def judged_measures() -> set[str]:
    judged = set(MODEL_GRADED_FLOOR)
    for path in REGISTRY_DIR.glob("*.md"):
        head = path.read_text(encoding="utf-8").split("\n---", 1)[0]
        match = TYPE_LINE.search(head)
        if match and match.group(1) == "judged":
            judged.add(path.stem)
    return judged


MODEL_GRADED = judged_measures()


class Result:
    def __init__(self) -> None:
        self.failures: dict[str, list[str]] = {lv: [] for lv in LEVELS}

    def fail(self, level: str, message: str) -> None:
        self.failures[level].append(message)

    @property
    def level(self) -> str | None:
        highest = None
        for lv in LEVELS:
            if self.failures[lv]:
                break
            highest = lv
        return highest


def load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".json"}:
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml is required to read YAML records: pip install pyyaml")

    # YAML resolves ISO-8601 scalars into datetimes. The record carries them as
    # RFC 3339 strings, so that resolver is removed for this load.
    class RecordLoader(yaml.SafeLoader):
        pass

    RecordLoader.yaml_implicit_resolvers = {
        key: [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]
        for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    return yaml.load(text, Loader=RecordLoader)


def check_l1(record: dict[str, Any], result: Result) -> None:
    """Schema-valid, with digests that are actually digests."""
    try:
        import jsonschema
    except ImportError:
        required = (
            "supergauge record_id emitted_at profile subject "
            "task_set measures gates assurance decision"
        ).split()
        for key in required:
            if key not in record:
                result.fail("L1", f"missing required block: {key}")
    else:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(record), key=str):
            path = "/".join(str(p) for p in error.absolute_path) or "(root)"
            result.fail("L1", f"{path}: {error.message}")

    # A placeholder digest passes a pattern check in a hand-written record but
    # means the record describes nothing verifiable.
    subject = record.get("subject") or {}
    for field, value in (
        ("subject.harness_digest", subject.get("harness_digest")),
        (
            "task_set.manifest_digest",
            (record.get("task_set") or {}).get("manifest_digest"),
        ),
    ):
        if value is not None and not DIGEST.match(str(value)):
            result.fail("L1", f"{field} is not a full sha256 digest")


def check_l2(record: dict[str, Any], result: Result) -> None:
    """Gates enforced, held-out sealed and fingerprinted, probes present."""
    task_set = record.get("task_set") or {}
    gates = record.get("gates") or []
    decision = record.get("decision") or {}

    if not gates:
        result.fail("L2", "no gates recorded")

    for gate in gates:
        if gate.get("id") in MODEL_GRADED:
            result.fail(
                "L2", f"gate {gate.get('id')} is model-graded and cannot back a gate"
            )

    if not task_set.get("sealed"):
        result.fail("L2", "held-out split is not sealed")
    if not task_set.get("held_out"):
        result.fail("L2", "no held-out split recorded")
    if not task_set.get("canary_ids"):
        result.fail("L2", "no contamination probes recorded")

    if decision.get("verdict") == "ship":
        failed = [g.get("id") for g in gates if g.get("result") != "pass"]
        if failed:
            result.fail(
                "L2", f"ship verdict with failing gates: {', '.join(map(str, failed))}"
            )

    # Every gate has to point at a measure the record actually reports.
    reported = {m.get("id") for m in record.get("measures") or []}
    for gate in gates:
        gid = gate.get("id")
        if gate.get("floor") is not None and gid not in reported:
            result.fail(
                "L2", f"gate {gid} sets a floor but no such measure is reported"
            )
    for failure in gate_floor_failures(record):
        result.fail("L2", failure)


def gate_floor_failures(record: dict[str, Any]) -> list[str]:
    """Compare recorded minimum floors with their matching measures."""
    failures = []
    for gate in record.get("gates") or []:
        floor = gate.get("floor")
        if floor is None:
            continue
        gid = gate.get("id")
        matches = [
            m
            for m in record.get("measures") or []
            if m.get("id") == gid
            and (gate.get("split") is None or m.get("split") == gate["split"])
        ]
        if len(matches) != 1:
            failures.append(f"gate {gid} requires one matching measure for its floor")
            continue
        value = matches[0].get("value")
        if any(
            isinstance(n, bool)
            or not isinstance(n, (int, float))
            or not math.isfinite(n)
            for n in (floor, value)
        ):
            failures.append(f"gate {gid} requires finite numeric floor and value")
        elif gate.get("result") == "pass" and value < floor:
            failures.append(f"gate {gid} reports pass below its floor")
    return failures


def check_l3(record: dict[str, Any], result: Result) -> None:
    """Reliability as pass^k, judge pinned, evaluator independence asserted."""
    measures = record.get("measures") or []
    assurance = record.get("assurance") or {}

    by_id = {m.get("id"): m for m in measures}
    pass_hat_k = by_id.get("reliability.pass_hat_k")
    if pass_hat_k is None:
        result.fail("L3", "reliability.pass_hat_k not reported")
    elif not pass_hat_k.get("k"):
        result.fail("L3", "reliability.pass_hat_k reported without k")
    elif pass_hat_k["k"] < 2:
        result.fail("L3", "reliability.pass_hat_k requires k of at least 2")

    if not assurance.get("evaluator_independent"):
        result.fail("L3", "assurance.evaluator_independent is not asserted")

    if any(m.get("id") in MODEL_GRADED for m in measures):
        judge = assurance.get("judge")
        if not judge:
            result.fail("L3", "model-graded measures reported without a judge record")
        else:
            if not judge.get("id") or not judge.get("model"):
                result.fail("L3", "judge record does not pin an id and a model")
            if judge.get("human_agreement_kappa") is None:
                result.fail("L3", "judge record carries no human agreement statistic")


def check_l4(record: dict[str, Any], result: Result) -> None:
    """Signed, and reproducible from the referenced ledger by a third party."""
    decision = record.get("decision") or {}
    evidence = (record.get("assurance") or {}).get("evidence") or {}

    if not decision.get("signature"):
        result.fail("L4", "record is unsigned")
    if not decision.get("rolls_back_to"):
        result.fail("L4", "no rollback target recorded")
    if not evidence.get("replayable"):
        result.fail("L4", "evidence is not marked replayable")
    if not evidence.get("ledger"):
        result.fail("L4", "no ledger referenced")
    if not evidence.get("events"):
        result.fail("L4", "ledger referenced without an event count")


def registered_measures() -> set[str]:
    return {p.stem for p in REGISTRY_DIR.glob("*.md")}


def release_failures(record: dict[str, Any]) -> list[str]:
    """Check recorded release approval after conformance validation."""
    decision = record.get("decision") or {}
    failures = []
    if decision.get("verdict") != "ship":
        failures.append("release requires decision.verdict: ship")
    actor = decision.get("actor")
    if (
        not isinstance(actor, str)
        or not actor.strip()
        or actor.strip().lower() == "unknown"
    ):
        failures.append("release requires a named decision.actor")
    gates = record.get("gates") or []
    if not gates or any(g.get("result") != "pass" for g in gates):
        failures.append("release requires passing deterministic gates")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an Agent Quality Record.")
    parser.add_argument("record", type=Path)
    parser.add_argument(
        "--level", choices=LEVELS, help="exit non-zero below this level"
    )
    parser.add_argument(
        "--require-ship",
        action="store_true",
        help="require L2 or higher, a ship verdict, a named actor and passing gates",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    record = load(args.record)
    result = Result()
    check_l1(record, result)
    check_l2(record, result)
    check_l3(record, result)
    check_l4(record, result)

    if not args.quiet:
        for lv in LEVELS:
            failures = result.failures[lv]
            mark = "pass" if not failures else "fail"
            print(f"{lv}  {mark}")
            for failure in failures:
                print(f"      {failure}")

        known = registered_measures()
        if known:
            unknown = [
                m.get("id")
                for m in record.get("measures") or []
                if m.get("id") not in known
                and not str(m.get("id", "")).startswith("x-")
            ]
            if unknown:
                print(
                    f"\nnote: measures not in the registry: {', '.join(map(str, unknown))}"
                )

        print(f"\nhighest level met: {result.level or 'none'}")

    if args.require_ship:
        blockers = release_failures(record)
        if result.level is None or LEVELS.index(result.level) < LEVELS.index("L2"):
            blockers.append("release requires L2 or higher")
        if blockers:
            if not args.quiet:
                for blocker in blockers:
                    print(f"release blocked: {blocker}")
            return 1

    if args.level:
        reached = result.level
        if reached is None or LEVELS.index(reached) < LEVELS.index(args.level):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
