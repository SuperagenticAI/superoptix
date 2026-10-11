"""Held-out GEPA split (2.0, arXiv:2610.09239)."""

import sys
import types

import superoptix  # noqa: F401  (import superoptix before dspy)
import dspy
from superoptix.optimizers.holdout import (
    gain_report,
    read_holdout_record,
    score_dspy_program,
    split_digest,
    split_holdout,
    write_holdout_record,
)


def _examples(n):
    return [dspy.Example(q=f"q{i}", a=f"a{i}").with_inputs("q") for i in range(n)]


def test_split_is_seeded_disjoint_and_sized():
    ex = _examples(20)
    a = split_holdout(ex, 0.2, seed=7)
    b = split_holdout(ex, 0.2, seed=7)
    c = split_holdout(ex, 0.2, seed=8)
    assert len(a.heldout) == 4 and len(a.train) == 16
    assert a.digest == b.digest and a.digest.startswith("sha256:")
    assert a.digest != c.digest
    train_ids = {e.q for e in a.train}
    assert not train_ids & {e.q for e in a.heldout}
    assert a.fallback_reason is None and a.has_heldout


def test_digest_is_order_independent_and_content_sensitive():
    ex = _examples(5)
    assert split_digest(ex) == split_digest(list(reversed(ex)))
    changed = ex[:-1] + [dspy.Example(q="q4", a="other").with_inputs("q")]
    assert split_digest(ex) != split_digest(changed)


def test_small_dataset_falls_back_with_reason(caplog):
    ex = _examples(3)
    s = split_holdout(ex, 0.2)
    assert s.heldout == [] and len(s.train) == 3
    assert s.digest is None
    assert "too small" in s.fallback_reason


def test_fraction_zero_disables():
    s = split_holdout(_examples(20), 0)
    assert not s.has_heldout and "disabled" in s.fallback_reason


def test_minimum_heldout_size_applies():
    s = split_holdout(_examples(8), 0.05)
    assert len(s.heldout) == 2


def test_score_program_and_gain_report():
    ex = _examples(4)

    def program(q):
        return dspy.Prediction(a="a0" if q == "q0" else "x")

    def metric(example, pred, *args, **kwargs):
        return 1.0 if pred.a == example.a else 0.0

    assert score_dspy_program(program, ex, metric) == 0.25
    assert score_dspy_program(program, [], metric) is None
    g = gain_report(0.5, 0.9, 0.5, 0.55)
    assert g["reported_gain"] == 0.4 and g["heldout_gain"] == 0.05
    assert gain_report(0.5, 0.9, None, None)["heldout_gain"] is None


def test_holdout_record_round_trip_has_no_content(tmp_path):
    s = split_holdout(_examples(10), 0.2, seed=1)
    path = tmp_path / "x_holdout.json"
    write_holdout_record(path, s, gain_report(0.1, 0.2, 0.1, 0.1))
    rec = read_holdout_record(path)
    assert rec["split_digest"] == s.digest
    assert rec["heldout_size"] == 2
    text = path.read_text()
    assert '"q' not in text and '"a' not in text.replace('"a2', "")
    assert read_holdout_record(tmp_path / "missing.json") is None


def test_routing_optimizer_never_shows_heldout_cases_to_gepa(monkeypatch):
    from superoptix.protocols.a2a.routing import optimize as opt
    from superoptix.protocols.a2a.routing.queries import RoutingCase
    from superoptix.protocols.a2a.routing.router import SkillRef

    seen = {}

    def fake_optimize_anything(seed, *, dataset, valset, **kwargs):
        seen["dataset"] = list(dataset)
        seen["valset"] = list(valset)
        return types.SimpleNamespace(best_candidate=dict(seed))

    fake = types.ModuleType("gepa.optimize_anything")
    fake.optimize_anything = fake_optimize_anything
    for name in ("EngineConfig", "GEPAConfig", "ReflectionConfig"):
        setattr(fake, name, lambda *a, **k: None)
    monkeypatch.setitem(sys.modules, "gepa.optimize_anything", fake)

    skills = [
        SkillRef(agent="a", skill_id=s, name=s, description=f"{s} things")
        for s in ("billing", "refunds")
    ]
    cases = [
        RoutingCase(query=f"{s} question {i}", expected=f"a:{s}", source="t")
        for i in range(5)
        for s in ("billing", "refunds")
    ]
    result = opt.optimize_routing(
        skills, cases, reflection_lm=lambda *a, **k: "", valset_fraction=0.2
    )
    heldout_n = result.heldout_size
    assert heldout_n == 2 and result.train_size == 8
    assert len(seen["dataset"]) == 8 and seen["valset"] == seen["dataset"]
    assert result.split_digest and result.heldout_improvement is not None
    assert "held-out" in result.summary()


def test_identities_drive_ids_and_match_playbook_recompute():
    from superoptix.optimizers.holdout import example_id, scenario_identity

    scenarios = [
        {"input": {"q": f"q{i}"}, "expected_output": {"a": f"a{i}"}} for i in range(10)
    ]
    augmented = [
        dspy.Example(q="CONTEXT " + s["input"]["q"], a=s["expected_output"]["a"])
        for s in scenarios
    ]
    split = split_holdout(
        augmented, 0.2, seed=3, identities=[scenario_identity(s) for s in scenarios]
    )
    recomputed = sorted(
        example_id(scenario_identity(s))
        for s in scenarios
        if example_id(scenario_identity(s)) in set(split.heldout_ids)
    )
    assert recomputed == split.heldout_ids
    assert (
        split_digest(
            [
                scenario_identity(s)
                for s in scenarios
                if example_id(scenario_identity(s)) in set(split.heldout_ids)
            ]
        )
        == split.digest
    )
