"""SuperGauge 2.0: sealed holdout, deterministic gates, integrity, conformance.

Generated records are checked with the SuperGauge conformance checker vendored
at a pinned revision (tests/fixtures/supergauge/PIN.md).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import superoptix  # noqa: F401  (import superoptix before dspy)
from superoptix import gauge_checks as gc
from superoptix.gauge import apply_jev_judgment, assemble_record, write_record
from superoptix.gauge_conformance import gate_exit_code
from superoptix.optimizers.holdout import (
    example_id,
    gain_report,
    scenario_identity,
    split_holdout,
    write_holdout_record,
)
from superoptix.quality.jev import DispositionJudgment

CHECKER = Path(__file__).parent / "fixtures" / "supergauge" / "conformance" / "check.py"


def _scenarios(n=10, canaries=2):
    out = [
        {
            "name": f"s{i}",
            "input": {"query": f"question {i}"},
            "expected_output": {"answer": f"answer {i}"},
        }
        for i in range(n)
    ]
    out += [
        {
            "name": f"canary_{j}",
            "canary": True,
            "input": {"query": f"unanswerable {j}"},
            "expected_output": {"answer": f"secret {j}"},
        }
        for j in range(canaries)
    ]
    return out


PLAYBOOK = {
    "spec": {
        "language_model": {"provider": "openai", "model": "gpt-test"},
        "tasks": [
            {
                "name": "t",
                "inputs": [{"name": "query", "type": "str"}],
                "outputs": [{"name": "answer", "type": "str"}],
            }
        ],
        "tools": [{"name": "search"}],
    }
}


def _write_playbook(tmp_path, scenarios):
    pb = {**PLAYBOOK}
    pb["spec"] = {**PLAYBOOK["spec"], "feature_specifications": {"scenarios": scenarios}}
    path = tmp_path / "agent_playbook.yaml"
    path.write_text(yaml.safe_dump(pb), encoding="utf-8")
    return path, pb


def _holdout_record(tmp_path, scenarios):
    usable = [s for s in scenarios if not s.get("canary")]
    split = split_holdout(
        usable, 0.2, seed=0, identities=[scenario_identity(s) for s in usable]
    )
    path = tmp_path / "agent_holdout.json"
    write_holdout_record(path, split, gain_report(0.5, 0.8, 0.5, 0.6))
    return yaml.safe_load(path.read_text())


def _results(scenarios, *, passed=True, parsed=True, canary_passed=False, baseline=False):
    rows = []
    for s in scenarios:
        canary = bool(s.get("canary"))
        ok = canary_passed if canary else passed
        rows.append(
            {
                "id": example_id(scenario_identity(s)),
                "sid": example_id(scenario_identity(s)),
                "name": s["name"],
                "status": "passed" if ok else "failed",
                "canary": canary,
                "parsed": parsed,
                "baseline_passed": baseline,
                "success_condition": "superoptix.bdd.minimal@1",
            }
        )
    return rows


def _record(tmp_path, *, k=3, holdout=True, **result_kwargs):
    scenarios = _scenarios()
    path, pb = _write_playbook(tmp_path, scenarios)
    runs = [_results(scenarios, **result_kwargs) for _ in range(k)]
    return assemble_record(
        agent_name="demo",
        playbook_path=path,
        playbook=pb,
        scenarios=scenarios,
        runs=runs,
        framework="dspy",
        seal_requested=True,
        holdout_record=_holdout_record(tmp_path, scenarios) if holdout else None,
        deterministic_gates=True,
        actor="ci@example",
        ledger=str(tmp_path / "record.ledger.jsonl"),
        ledger_events=12 * k,
    )


def _check(record, tmp_path, *args):
    out = tmp_path / "record.yaml"
    write_record(record, out)
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(out), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


# --- B1 sealed holdout ------------------------------------------------------


def test_sealed_derives_from_gepa_split(tmp_path):
    rec = _record(tmp_path)
    ts = rec["task_set"]
    assert ts["sealed"] is True and ts["held_out"] == 2 and ts["held_in"] == 8
    assert ts["manifest_digest"] == rec["x-superoptix"]["holdout"]["split_digest"]
    assert {"id": "assurance.holdout_sealed", "value": True} in rec["measures"]
    tc = [m for m in rec["measures"] if m["id"] == "task.completion"][0]
    assert tc["split"] == "held-out" and tc["n"] == 2


def test_no_split_means_not_sealed_with_reason(tmp_path):
    rec = _record(tmp_path, holdout=False)
    assert rec["task_set"]["sealed"] is False
    assert "no held-out split" in rec["x-superoptix"]["holdout"]["reason"]
    assert {"id": "assurance.holdout_sealed", "value": False} in rec["measures"]
    assert rec["decision"]["verdict"] == "hold"


def test_edited_heldout_scenario_breaks_seal(tmp_path):
    scenarios = _scenarios()
    hold = _holdout_record(tmp_path, scenarios)
    victim = next(
        s for s in scenarios if example_id(scenario_identity(s)) in hold["heldout_ids"]
    )
    victim["expected_output"] = {"answer": "edited"}
    seal = gc.seal_holdout(scenarios, hold)
    assert not seal.sealed and "changed or removed" in seal.reason


def test_fired_canary_unseals_and_holds(tmp_path):
    rec = _record(tmp_path, canary_passed=True)
    assert rec["task_set"]["sealed"] is False
    assert rec["assurance"]["integrity"]["canaries"][0]["observed"] == "pass"
    assert rec["decision"]["verdict"] == "hold"


# --- B2 deterministic gates -------------------------------------------------


def test_gates_are_deterministic_and_canonical(tmp_path):
    rec = _record(tmp_path)
    ids = {g["id"] for g in rec["gates"]}
    assert ids == {
        "output.parse_rate",
        "reliability.beats_trivial_baseline",
        "reliability.pass_hat_k",
        "assurance.holdout_sealed",
    }
    assert all(not g["id"].startswith("x-") for g in rec["gates"])
    base = [m for m in rec["measures"] if m["id"] == "reliability.beats_trivial_baseline"][0]
    assert base["baseline"]["id"] == "echo-input" and base["value"] is True
    parse = [m for m in rec["measures"] if m["id"] == "output.parse_rate"][0]
    assert parse["schema_digest"].startswith("sha256:")
    # No tool calls or trajectory constraints were recorded: those are omitted.
    reported = {m["id"] for m in rec["measures"]}
    assert "tool.correctness" not in reported and "trajectory.valid" not in reported
    assert rec["decision"]["verdict"] == "ship"


def test_no_contract_no_parse_rate():
    assert gc.parse_rate_measure([{"parsed": True}], None) is None
    assert gc.declared_output_contract({"tasks": [{"name": "t"}]}) is None


def test_output_parsed_checks_presence_and_type():
    contract = [{"name": "answer", "type": "str"}, {"name": "Count", "type": "int"}]
    assert gc.output_parsed({"answer": "x", "count": 3}, contract)
    assert not gc.output_parsed({"answer": "", "count": 3}, contract)
    assert not gc.output_parsed({"answer": "x", "count": "3"}, contract)
    assert not gc.output_parsed("raw text", contract)


def test_baseline_tie_does_not_beat():
    m = gc.beats_baseline_measure(candidate_value=0.5, baseline_value=0.5, n=4)
    assert m["value"] is False


def test_single_run_has_no_pass_hat_k(tmp_path):
    rec = _record(tmp_path, k=1)
    assert "reliability.pass_hat_k" not in {m["id"] for m in rec["measures"]}


def test_tool_correctness_and_trajectory_from_recorded_calls():
    traj = {
        "tool_name_0": "search",
        "tool_args_0": {"q": "a"},
        "observation_0": "r",
        "tool_name_1": "search",
        "tool_args_1": {"q": "a"},
        "observation_1": "r",
        "tool_name_2": "finish",
        "tool_args_2": {},
    }
    calls = gc.tool_calls_from_trajectory(traj)
    assert [c["name"] for c in calls] == ["search", "search"]
    m = gc.tool_correctness_measure([{"tool_calls": calls}], ["search"])
    assert m["value"] == 0.5 and m["n"] == 2  # second call is redundant
    assert gc.tool_correctness_measure([{"tool_calls": calls}], None) is None
    t = gc.trajectory_measure(
        [{"tool_calls": calls, "trajectory_constraints": {"max_steps": 1}}]
    )
    assert t["value"] == 0.0
    assert gc.trajectory_measure([{"tool_calls": calls}]) is None


def test_failing_parse_rate_fails_gate_and_holds(tmp_path):
    rec = _record(tmp_path, parsed=False)
    gate = [g for g in rec["gates"] if g["id"] == "output.parse_rate"][0]
    assert gate["result"] == "fail" and gate["floor"] == 0.95
    assert rec["decision"]["verdict"] == "hold"


# --- B3 integrity and Jev ---------------------------------------------------


def _accept(model="jev-1.13.1", requested="jev-latest"):
    return DispositionJudgment(
        choice="accept",
        confidence=0.95,
        model=model,
        requested_model=requested,
        model_served=True,
        source="typesafe-live",
        pack_digest="sha256:" + "a" * 64,
    )


def test_judged_accept_over_failing_gate_sets_mechanical_override(tmp_path):
    rec = apply_jev_judgment(_record(tmp_path, parsed=False), _accept())
    assert rec["assurance"]["integrity"]["mechanical_override"] is True
    assert rec["decision"]["verdict"] == "hold"
    assert "RFC 0005" in rec["decision"]["rationale"]


def test_judge_records_served_model_and_keeps_ship(tmp_path):
    rec = apply_jev_judgment(_record(tmp_path), _accept())
    assert rec["decision"]["verdict"] == "ship"
    assert rec["assurance"]["judge"]["model"] == "jev-1.13.1"
    jev = rec["x-superoptix"]["jev"]
    assert jev["requested_model"] == "jev-latest" and jev["model_source"] == "served"
    assert rec["assurance"]["integrity"]["mechanical_override"] is False
    assert all(g["id"] not in {"answer.grounded"} for g in rec["gates"])


def test_jev_warn_soft_holds_a_passing_record(tmp_path):
    warn = DispositionJudgment(choice="warn", confidence=0.9, source="typesafe-live", model="jev-1.13.0")
    rec = apply_jev_judgment(_record(tmp_path), warn)
    assert rec["decision"]["verdict"] == "hold"


def test_served_model_helper():
    from superoptix.quality.typesafe_adapter import served_model

    class LM:
        history = [{"response_model": "jev-1.13.2"}]

    assert served_model(LM()) == "jev-1.13.2"
    assert served_model(object()) is None


# --- B4 conformance with the pinned SuperGauge checker ----------------------


def test_upstream_reference_example_passes():
    ref = CHECKER.parent.parent / "l3-superoptix-hardened-ship.yaml"
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(ref), "--level", "L2", "--require-ship", "--quiet"]
    )
    assert proc.returncode == 0


def test_passing_fixture_meets_l2_and_ships(tmp_path):
    rec = _record(tmp_path)
    code, out = _check(rec, tmp_path, "--level", "L2", "--require-ship")
    assert code == 0, out
    assert "measures not in the registry" not in out
    assert gate_exit_code(rec, "L2")[0] == 0


def test_written_record_is_schema_valid_and_metadata_goes_to_sidecar(tmp_path):
    from superoptix.gauge import sidecar_path

    rec = _record(tmp_path)
    out = tmp_path / "record.yaml"
    write_record(rec, out)
    assert "x-superoptix" not in yaml.safe_load(out.read_text())
    assert "holdout" in yaml.safe_load(sidecar_path(out).read_text())["x-superoptix"]
    assert rec["subject"]["authority"]["grant_digest"].startswith("sha256:")


def test_failing_fixture_fails_checker(tmp_path):
    rec = _record(tmp_path, parsed=False)
    code, out = _check(rec, tmp_path, "--level", "L2", "--require-ship")
    assert code == 1, out
    assert "release blocked" in out
    assert gate_exit_code(rec, "L2")[0] == 1


def test_unsealed_fixture_is_below_l2(tmp_path):
    rec = _record(tmp_path, holdout=False)
    code, out = _check(rec, tmp_path, "--level", "L2")
    assert code == 1, out
    assert "held-out split is not sealed" in out
    code, _, failures = gate_exit_code(rec, "L2")
    assert code == 1 and any("not sealed" in f for f in failures["L2"])
    code, out = _check(rec, tmp_path, "--level", "L2", "--require-ship")
    assert code == 1 and "release blocked" in out


def test_unnamed_actor_cannot_ship(tmp_path, monkeypatch):
    for var in ("SUPEROPTIX_RELEASE_ACTOR", "GITHUB_ACTOR", "USER"):
        monkeypatch.delenv(var, raising=False)
    scenarios = _scenarios()
    path, pb = _write_playbook(tmp_path, scenarios)
    rec = assemble_record(
        agent_name="demo",
        playbook_path=path,
        playbook=pb,
        scenarios=scenarios,
        runs=[_results(scenarios) for _ in range(3)],
        framework="dspy",
        seal_requested=True,
        holdout_record=_holdout_record(tmp_path, scenarios),
        deterministic_gates=True,
        ledger=str(tmp_path / "l.jsonl"),
        ledger_events=36,
    )
    assert rec["decision"]["verdict"] == "hold"
    assert "named release actor" in rec["decision"]["rationale"]
    assert gate_exit_code(rec, "L2")[0] == 1


def test_builtin_precheck_matches_upstream_levels(tmp_path):
    from superoptix.gauge_conformance import check_levels, highest_level

    for kwargs in ({}, {"parsed": False}, {"holdout": False}, {"k": 1}):
        rec = _record(tmp_path, **kwargs)
        out_path = tmp_path / "r.yaml"
        write_record(rec, out_path)
        proc = subprocess.run(
            [sys.executable, str(CHECKER), str(out_path)], capture_output=True, text=True
        )
        upstream = proc.stdout.strip().splitlines()[-1].split(":")[-1].strip()
        assert highest_level(check_levels(rec)) == (None if upstream == "none" else upstream), kwargs
