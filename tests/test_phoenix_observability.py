"""Tests for Phoenix observability integration."""

from __future__ import annotations

import sys
import types

from superoptix.observability.enhanced_tracer import EnhancedSuperOptixTracer
from superoptix.observability import phoenix as phoenix_helpers
from superoptix.observability.phoenix import (
    get_phoenix_config,
    instrument_framework_with_phoenix,
    normalize_phoenix_endpoint,
    setup_phoenix,
    setup_phoenix_for_spec,
)
from superoptix.observability.unified_interface import (
    ObservabilityBackend,
    UnifiedObservability,
)
from superoptix.runners.crewai_runtime_helpers import (
    run_with_optional_rlm as run_crewai_with_optional_rlm,
)
from superoptix.runners.openai_runtime_helpers import (
    run_with_optional_rlm as run_openai_with_optional_rlm,
)


class _FakeSpan:
    def __init__(self):
        self.attributes = {}
        self.input = None
        self.output = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_input(self, value):
        self.input = value

    def set_output(self, value):
        self.output = value


class _FakeTracer:
    def __init__(self):
        self.spans = []

    def start_as_current_span(self, name):
        span = _FakeSpan()
        span.name = name
        self.spans.append(span)
        return span


class _FakeTracerProvider:
    def __init__(self):
        self.tracer = _FakeTracer()

    def get_tracer(self, name):
        return self.tracer


def _install_fake_phoenix(monkeypatch):
    phoenix_helpers._PHOENIX_HANDLE_CACHE.clear()
    phoenix_helpers._PHOENIX_INSTRUMENTED_FRAMEWORKS.clear()
    register_calls = []

    phoenix_mod = types.ModuleType("phoenix")
    phoenix_otel_mod = types.ModuleType("phoenix.otel")

    def fake_register(**kwargs):
        register_calls.append(kwargs)
        return _FakeTracerProvider()

    phoenix_otel_mod.register = fake_register

    openinference_mod = types.ModuleType("openinference")
    openinference_instr_mod = types.ModuleType("openinference.instrumentation")

    class _SessionContext:
        def __init__(self, session_id):
            self.session_id = session_id

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def using_session(*, session_id):
        return _SessionContext(session_id)

    openinference_instr_mod.using_session = using_session

    monkeypatch.setitem(sys.modules, "phoenix", phoenix_mod)
    monkeypatch.setitem(sys.modules, "phoenix.otel", phoenix_otel_mod)
    monkeypatch.setitem(sys.modules, "openinference", openinference_mod)
    monkeypatch.setitem(
        sys.modules, "openinference.instrumentation", openinference_instr_mod
    )

    return register_calls


def _install_fake_instrumentor(
    monkeypatch,
    *,
    module_name: str,
    class_name: str,
    instrument_calls: list[tuple[str, object]],
):
    parts = module_name.split(".")
    for idx in range(1, len(parts)):
        package_name = ".".join(parts[:idx])
        monkeypatch.setitem(
            sys.modules, package_name, sys.modules.get(package_name, types.ModuleType(package_name))
        )

    instrumentor_mod = types.ModuleType(module_name)

    class _Instrumentor:
        def instrument(self, *, tracer_provider):
            instrument_calls.append((module_name, tracer_provider))

    setattr(instrumentor_mod, class_name, _Instrumentor)
    monkeypatch.setitem(sys.modules, module_name, instrumentor_mod)


def test_normalize_phoenix_endpoint():
    assert (
        normalize_phoenix_endpoint("http://localhost:6006")
        == "http://localhost:6006/v1/traces"
    )
    assert (
        normalize_phoenix_endpoint("http://localhost:6006/v1/traces")
        == "http://localhost:6006/v1/traces"
    )
    assert (
        normalize_phoenix_endpoint("http://localhost:4317", protocol="grpc")
        == "http://localhost:4317"
    )


def test_setup_phoenix_registers_with_normalized_endpoint(monkeypatch):
    register_calls = _install_fake_phoenix(monkeypatch)

    handle = setup_phoenix(
        agent_id="demo-agent",
        project_name="demo-project",
        endpoint="http://localhost:6006",
        batch=True,
    )

    assert handle is not None
    assert register_calls
    assert register_calls[0]["project_name"] == "demo-project"
    assert register_calls[0]["endpoint"] == "http://localhost:6006/v1/traces"
    assert register_calls[0]["set_global_tracer_provider"] is False


def test_get_phoenix_config_respects_cli_backend(monkeypatch):
    monkeypatch.setenv("SUPEROPTIX_OBSERVE_BACKEND", "phoenix")
    cfg = get_phoenix_config({})
    assert cfg["enabled"] is True
    assert cfg["auto_instrument"] is True


def test_setup_phoenix_for_spec_uses_spec_values(monkeypatch):
    register_calls = _install_fake_phoenix(monkeypatch)
    spec_data = {
        "phoenix": {
            "enabled": True,
            "project_name": "spec-project",
            "endpoint": "http://localhost:7007",
            "protocol": "http/protobuf",
            "batch": False,
            "auto_instrument": True,
        }
    }

    handle = setup_phoenix_for_spec(agent_id="demo", spec_data=spec_data)

    assert handle is not None
    assert register_calls
    assert register_calls[0]["project_name"] == "spec-project"
    assert register_calls[0]["endpoint"] == "http://localhost:7007/v1/traces"
    assert register_calls[0]["auto_instrument"] is True
    assert register_calls[0]["batch"] is False


def test_instrument_framework_with_phoenix_registers_once(monkeypatch):
    _install_fake_phoenix(monkeypatch)
    instrument_calls = []
    _install_fake_instrumentor(
        monkeypatch,
        module_name="openinference.instrumentation.openai_agents",
        class_name="OpenAIAgentsInstrumentor",
        instrument_calls=instrument_calls,
    )

    handle = setup_phoenix(agent_id="demo-agent", project_name="demo-project")

    assert handle is not None
    assert instrument_framework_with_phoenix(handle, "openai_agents") is True
    assert instrument_framework_with_phoenix(handle, "openai_agents") is True
    assert len(instrument_calls) == 1
    assert instrument_calls[0][1] is handle["tracer_provider"]


def test_instrument_framework_with_phoenix_returns_false_without_module(monkeypatch):
    _install_fake_phoenix(monkeypatch)
    handle = setup_phoenix(agent_id="demo-agent", project_name="demo-project")

    assert handle is not None
    assert instrument_framework_with_phoenix(handle, "crewai") is False


def test_enhanced_tracer_logs_to_phoenix(monkeypatch):
    _install_fake_phoenix(monkeypatch)

    tracer = EnhancedSuperOptixTracer(
        agent_id="demo-agent",
        enable_external_tracing=True,
        observability_backend="phoenix",
        auto_load=False,
    )

    assert "phoenix" in tracer.external_tracers

    tracer.add_event(
        event_type="custom_event",
        component="unit_test",
        data={"answer": 42, "ok": True},
        status="success",
    )

    phoenix_handle = tracer.external_tracers["phoenix"]
    spans = phoenix_handle["tracer"].spans
    assert len(spans) == 1
    assert spans[0].attributes["superoptix.component"] == "unit_test"
    assert spans[0].attributes["superoptix.data.answer"] == 42


def test_unified_observability_accepts_phoenix_backend(monkeypatch):
    _install_fake_phoenix(monkeypatch)

    obs = UnifiedObservability(
        agent_id="demo-agent",
        backend=ObservabilityBackend.PHOENIX,
        enable_external=True,
        auto_load=False,
    )

    assert obs.backend == ObservabilityBackend.PHOENIX
    assert "phoenix" in obs.tracer.external_tracers


def test_openai_runtime_helper_logs_phoenix_span(monkeypatch):
    _install_fake_phoenix(monkeypatch)
    instrument_calls = []
    _install_fake_instrumentor(
        monkeypatch,
        module_name="openinference.instrumentation.openai_agents",
        class_name="OpenAIAgentsInstrumentor",
        instrument_calls=instrument_calls,
    )

    agents_mod = types.ModuleType("agents")

    class _FakeRunner:
        @staticmethod
        async def run(agent, input):
            return {"agent": getattr(agent, "name", "agent"), "input": input}

    agents_mod.Runner = _FakeRunner
    monkeypatch.setitem(sys.modules, "agents", agents_mod)

    class _Agent:
        name = "openai-demo"

    result = __import__("asyncio").run(
        run_openai_with_optional_rlm(
            agent=_Agent(),
            prompt="hello",
            spec_data={"phoenix": {"enabled": True}},
            model_name="gpt-4o-mini",
        )
    )

    assert result["input"] == "hello"
    assert len(instrument_calls) == 1


def test_crewai_runtime_helper_logs_phoenix_span(monkeypatch):
    _install_fake_phoenix(monkeypatch)
    instrument_calls = []
    _install_fake_instrumentor(
        monkeypatch,
        module_name="openinference.instrumentation.crewai",
        class_name="CrewAIInstrumentor",
        instrument_calls=instrument_calls,
    )

    class _Crew:
        name = "crewai-demo"

        def kickoff(self, inputs):
            return {"raw": f"done:{inputs['query']}"}

    output = run_crewai_with_optional_rlm(
        crew=_Crew(),
        prompt="hello",
        spec_data={"phoenix": {"enabled": True}},
        model_name="gpt-4o-mini",
        task_description="Task",
    )

    assert "done:hello" in output
    assert len(instrument_calls) == 1
