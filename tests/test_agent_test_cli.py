"""CLI surface for SuperGauge 2.0: super agent test, evaluate and optimize flags."""

from __future__ import annotations

import sys

import pytest

import superoptix  # noqa: F401  (import superoptix before dspy)

from tests.test_gauge_l2 import _scenarios, _write_playbook



def test_cli_has_test_command_and_flags(capsys):
    from superoptix.cli.main import main

    for argv in (
        ["super", "agent", "test", "--help"],
        ["super", "agent", "evaluate", "--help"],
        ["super", "agent", "optimize", "--help"],
    ):
        sys.argv = argv
        with pytest.raises(SystemExit):
            main()
    out = capsys.readouterr().out
    assert "--gate" in out and "--k" in out and "--gauge-gates" in out
    assert out.count("--gauge-out") >= 3


def test_gate_floor_parsing():
    from superoptix.cli.commands.agent import _parse_gate_floors

    assert _parse_gate_floors(["output.parse_rate=0.99"]) == {"output.parse_rate": 0.99}
    with pytest.raises(ValueError):
        _parse_gate_floors(["nope"])


def test_minimal_evaluator_emits_gauge_fields(tmp_path):
    from superoptix.cli.commands.agent import _gauge_results, _MinimalDSPyBDDEvaluator

    scenarios = _scenarios(n=2, canaries=1)
    path, _ = _write_playbook(tmp_path, scenarios)

    class Module:
        @staticmethod
        def build_program():
            return lambda query: {"answer": "answer " + query.split()[-1]}

    ev = _MinimalDSPyBDDEvaluator(Module, path)
    out = ev.run_bdd_test_suite()
    rows = _gauge_results(out["bdd_results"]["detailed_results"])
    assert rows[0]["parsed"] is True and rows[0]["sid"] == rows[0]["id"]
    assert rows[2]["canary"] is True
    assert isinstance(rows[0]["baseline_passed"], bool)


_PIPELINE = '''
class _Program:
    def __call__(self, query):
        if query.startswith("unanswerable"):
            return {"answer": "I do not know"}
        return {"answer": "answer " + query.split()[-1]}

    def load(self, path):
        pass


def build_program():
    return _Program()
'''


def _project(tmp_path, monkeypatch, *, with_holdout=True):
    import yaml

    from superoptix.optimizers.holdout import (
        gain_report,
        scenario_identity,
        split_holdout,
        write_holdout_record,
    )
    from tests.test_gauge_l2 import PLAYBOOK

    root = tmp_path / "proj"
    agent = root / "demo" / "agents" / "bot"
    (agent / "pipelines").mkdir(parents=True)
    (agent / "playbook").mkdir()
    (root / ".super").write_text("project: demo\n")
    (agent / "pipelines" / "bot_pipeline.py").write_text(_PIPELINE)
    scenarios = _scenarios(n=10, canaries=2)
    pb = {**PLAYBOOK, "spec": {**PLAYBOOK["spec"], "feature_specifications": {"scenarios": scenarios}}}
    (agent / "playbook" / "bot_playbook.yaml").write_text(yaml.safe_dump(pb))
    if with_holdout:
        usable = [s for s in scenarios if not s.get("canary")]
        split = split_holdout(usable, 0.2, identities=[scenario_identity(s) for s in usable])
        write_holdout_record(
            agent / "pipelines" / "bot_holdout.json", split, gain_report(0, 0, 0, 0)
        )
    monkeypatch.chdir(root)
    return root


def _run_cli(argv):
    from superoptix.cli.main import main

    sys.argv = ["super", *argv]
    with pytest.raises(SystemExit) as exc:
        main()
    return exc.value.code


def test_agent_test_end_to_end_ships_and_passes_pinned_checker(tmp_path, monkeypatch):
    import subprocess

    from tests.test_gauge_l2 import CHECKER

    root = _project(tmp_path, monkeypatch)
    code = _run_cli(
        [
            "agent", "test", "bot", "--k", "2", "--gauge-out", "rec.yaml",
            "--checker", str(CHECKER), "--actor", "release-bot@example.com",
        ]
    )
    assert code == 0
    for name in ("rec.yaml", "rec.ledger.jsonl", "rec.superoptix.json"):
        assert (root / name).exists(), name
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(root / "rec.yaml"), "--level", "L2", "--require-ship"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout
    rec = __import__("yaml").safe_load((root / "rec.yaml").read_text())
    assert rec["decision"]["actor"] == "release-bot@example.com"


def test_agent_test_without_split_exits_two(tmp_path, monkeypatch):
    import yaml

    root = _project(tmp_path, monkeypatch, with_holdout=False)
    assert _run_cli(["agent", "test", "bot", "--gauge-out", "rec.yaml"]) == 1
    rec = yaml.safe_load((root / "rec.yaml").read_text())
    assert rec["task_set"]["sealed"] is False and rec["decision"]["verdict"] == "hold"


def test_evaluate_gauge_out_still_works(tmp_path, monkeypatch):
    import yaml

    root = _project(tmp_path, monkeypatch)
    from superoptix.cli.main import main

    sys.argv = ["super", "agent", "evaluate", "bot", "--gauge-out", "ev.yaml"]
    try:
        main()
    except SystemExit as exc:
        assert not exc.code
    rec = yaml.safe_load((root / "ev.yaml").read_text())
    assert rec["gates"] == [] and rec["decision"]["verdict"] == "hold"
    assert rec["task_set"]["sealed"] is False
