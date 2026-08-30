"""Tests for UniversalGEPA API mode selection and compatibility behavior."""

import sys
import types

import pytest

import superoptix.optimizers.universal_gepa as ug
from superoptix.core.base_component import BaseComponent


class DummyComponent(BaseComponent):
    """Minimal BaseComponent for UniversalGEPA tests."""

    def __init__(self):
        super().__init__(
            name="dummy_component",
            description="dummy",
            input_fields=["query"],
            output_fields=["response"],
            variable="initial prompt",
            variable_type="instruction",
            framework="openai",
        )

    def forward(self, **inputs):
        return {"response": f"reply: {inputs.get('query', '')}"}


def _metric(inputs, outputs, gold, component_name=None):
    return {"score": 1.0, "feedback": "ok"}


class _FakeGEPAResult:
    def __init__(self, candidate_text="optimized prompt", score=0.91):
        self.candidates = [{"dummy_component": candidate_text}]
        self.val_aggregate_scores = [score]

    @property
    def best_idx(self):
        return 0


def _sample_data():
    return [{"inputs": {"query": "hello"}, "outputs": {"response": "world"}}]


def test_universal_gepa_defaults_to_legacy_api(monkeypatch):
    calls = {"legacy": 0}

    def _fake_legacy_optimize(**kwargs):
        calls["legacy"] += 1
        return _FakeGEPAResult()

    monkeypatch.setattr(ug, "optimize", _fake_legacy_optimize)

    optimizer = ug.UniversalGEPA(
        metric=_metric,
        auto="light",
        reflection_lm=lambda _: "reflection",
    )
    result = optimizer.compile(
        component=DummyComponent(),
        trainset=_sample_data(),
        valset=_sample_data(),
    )

    assert calls["legacy"] == 1
    assert result.best_variable == "optimized prompt"
    assert result.best_score == pytest.approx(0.91)


def test_optimize_anything_opt_in_falls_back_to_legacy_when_unavailable(monkeypatch):
    calls = {"legacy": 0}

    def _fake_legacy_optimize(**kwargs):
        calls["legacy"] += 1
        return _FakeGEPAResult(candidate_text="legacy fallback prompt", score=0.77)

    monkeypatch.setattr(ug, "optimize", _fake_legacy_optimize)
    # Force `from gepa.optimize_anything import ...` to raise ImportError.
    # Deleting the entry is no longer enough: gepa 0.1.4+ ships the module, so a
    # delitem simply lets the import succeed again. Binding the name to None makes
    # the import machinery raise, which is what "unavailable" means here.
    monkeypatch.setitem(sys.modules, "gepa.optimize_anything", None)

    optimizer = ug.UniversalGEPA(
        metric=_metric,
        auto="light",
        reflection_lm=lambda _: "reflection",
        gepa_api="optimize_anything",
    )
    result = optimizer.compile(
        component=DummyComponent(),
        trainset=_sample_data(),
        valset=_sample_data(),
    )

    assert calls["legacy"] == 1
    assert result.best_variable == "legacy fallback prompt"
    assert result.best_score == pytest.approx(0.77)


def test_optimize_anything_opt_in_uses_new_api_when_available(monkeypatch):
    calls = {"optimize_anything": 0}

    def _legacy_should_not_run(**kwargs):
        raise AssertionError("legacy optimize should not be called when optimize_anything is available")

    monkeypatch.setattr(ug, "optimize", _legacy_should_not_run)

    fake_module = types.ModuleType("gepa.optimize_anything")

    class EngineConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class ReflectionConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class MergeConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class GEPAConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    def optimize_anything(**kwargs):
        calls["optimize_anything"] += 1
        return _FakeGEPAResult(candidate_text="oa prompt", score=0.88)

    fake_module.EngineConfig = EngineConfig
    fake_module.ReflectionConfig = ReflectionConfig
    fake_module.MergeConfig = MergeConfig
    fake_module.GEPAConfig = GEPAConfig
    fake_module.optimize_anything = optimize_anything
    monkeypatch.setitem(sys.modules, "gepa.optimize_anything", fake_module)

    optimizer = ug.UniversalGEPA(
        metric=_metric,
        auto="light",
        reflection_lm=lambda _: "reflection",
        gepa_api="optimize_anything",
    )
    result = optimizer.compile(
        component=DummyComponent(),
        trainset=_sample_data(),
        valset=_sample_data(),
    )

    assert calls["optimize_anything"] == 1
    assert result.best_variable == "oa prompt"
    assert result.best_score == pytest.approx(0.88)


def test_invalid_gepa_api_raises():
    with pytest.raises(ValueError, match="Unsupported GEPA API"):
        ug.UniversalGEPA(
            metric=_metric,
            auto="light",
            reflection_lm=lambda _: "reflection",
            gepa_api="unsupported",
        )
