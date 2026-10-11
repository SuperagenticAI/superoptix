"""Judge advice cannot create release approval or erase an existing rejection."""
import copy

import pytest
from superoptix.gauge import apply_jev_judgment
from superoptix.quality.jev import DispositionJudgment, heuristic_disposition_from_evaluate


def record(verdict="hold", result="pass", sealed=True):
    return {
        "decision": {"verdict": verdict, "actor": "reviewer@example.com", "rationale": "Prior decision."},
        "task_set": {"sealed": sealed},
        "gates": [{"id": "policy.hard_rules", "result": result}],
        "assurance": {},
        "measures": [],
    }


@pytest.mark.parametrize("prior,choice,gate,sealed,expected", [
    ("hold", "accept", "pass", True, "hold"),
    ("reject", "accept", "pass", True, "reject"),
    ("reject", "warn", "pass", True, "reject"),
    ("ship", "accept", "fail", True, "hold"),
    ("ship", "accept", "pass", False, "hold"),
    ("ship", "accept", "pass", True, "ship"),
    ("ship", "warn", "pass", True, "hold"),
    ("hold", "reject", "pass", True, "reject"),
])
def test_advice_preserves_release_boundaries(prior, choice, gate, sealed, expected):
    aqr = record(prior, gate, sealed)
    gates = copy.deepcopy(aqr["gates"])
    apply_jev_judgment(aqr, DispositionJudgment(choice=choice, confidence=0.99, model="judge@1", source="typesafe-live"))
    assert aqr["decision"]["verdict"] == expected
    assert aqr["gates"] == gates
    assert "Prior decision." in aqr["decision"]["rationale"]


def test_heuristic_cannot_pin_a_model_or_retain_ship():
    aqr = record("ship")
    apply_jev_judgment(aqr, heuristic_disposition_from_evaluate(passed=10, total=10))
    assert aqr["decision"]["verdict"] == "hold"
    assert "judge" not in aqr["assurance"]
    assert aqr["x-superoptix"]["jev"]["source"] == "heuristic-evaluate"
    assert aqr["x-superoptix"]["jev"]["confidence_kind"] == "proxy"


@pytest.mark.parametrize("gates", [[], [{"id": "answer.grounded", "result": "pass"}]])
def test_acceptance_requires_deterministic_checks(gates):
    aqr = record("ship")
    aqr["gates"] = gates
    apply_jev_judgment(aqr, DispositionJudgment(choice="accept", confidence=0.99, source="typesafe-live"))
    assert aqr["decision"]["verdict"] == "hold"


@pytest.mark.parametrize("available", [False, True])
def test_cli_fallback_records_source_without_model_pin(monkeypatch, available):
    from superoptix.cli.commands.agent import _apply_optional_jev
    from superoptix.quality import jev
    monkeypatch.setattr(jev, "typesafe_available", lambda: available)
    if available:
        from superoptix.quality import typesafe_adapter
        monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
        def unavailable(*args, **kwargs):
            raise RuntimeError("test service failure")
        monkeypatch.setattr(typesafe_adapter, "judge_evaluation_summary", unavailable)
    else:
        monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    aqr = _apply_optional_jev(record(), results=[{"status": "passed"}] * 10, model="requested-judge@1")
    assert aqr["decision"]["verdict"] == "hold"
    assert "judge" not in aqr["assurance"]
    disposition = aqr["x-superoptix"]["jev"]["disposition"]
    assert disposition["source"] == "heuristic-evaluate"
    assert disposition["model"] is None
