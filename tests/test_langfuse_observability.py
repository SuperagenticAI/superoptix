"""Contract tests for the optional Langfuse SDK v4 bridge."""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from superoptix.observability import langfuse as bridge
from superoptix.observability.enhanced_tracer import EnhancedSuperOptixTracer


class FakeClient:
    def __init__(self):
        self.active = []
        self.records = []
        self.flushes = 0

    @contextmanager
    def start_as_current_observation(self, **kwargs):
        record = {**kwargs, "parent": self.active[-1] if self.active else None}
        self.records.append(record)
        self.active.append(record)

        class Span:
            def update(self, **changes):
                record.update(changes)

        try:
            yield Span()
        finally:
            self.active.pop()

    def flush(self):
        self.flushes += 1


def make_tracer(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(bridge, "setup_langfuse", lambda: client)
    tracer = EnhancedSuperOptixTracer(
        "demo", enable_external_tracing=True,
        observability_backend="langfuse", auto_load=False,
    )
    return tracer, client


def test_nested_operations_and_safe_content(monkeypatch):
    monkeypatch.delenv("SUPEROPTIX_LANGFUSE_CAPTURE_CONTENT", raising=False)
    tracer, client = make_tracer(monkeypatch)
    with tracer.trace_operation("agent_run", "agent.demo", query="private query"):
        with tracer.trace_operation("retrieve", "retriever", operation="retrieve"):
            tracer.add_event("tool_result", "tool", {"status": "success", "output": "secret"})

    assert [record["name"] for record in client.records] == [
        "agent_run", "retrieve", "tool_result"
    ]
    assert client.records[0]["as_type"] == "agent"
    assert client.records[1]["parent"] is client.records[0]
    assert client.records[2]["parent"] is client.records[1]
    assert "query" not in client.records[0]["metadata"]
    assert "output" not in client.records[2]["metadata"]
    assert len(tracer.traces) == 5


def test_error_marks_observation_without_changing_exception(monkeypatch):
    tracer, client = make_tracer(monkeypatch)
    with pytest.raises(ValueError, match="private detail"):
        with tracer.trace_operation("agent_run", "agent.demo"):
            raise ValueError("private detail")

    assert client.records[0]["level"] == "ERROR"
    assert client.records[0]["status_message"] == "ValueError"
    assert tracer.performance_stats["total_errors"] == 1


def test_flush_and_missing_credentials(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    assert bridge.setup_langfuse() is None
    client = FakeClient()
    bridge.flush(client)
    assert client.flushes == 1


def test_exporter_failure_does_not_fail_agent(monkeypatch):
    class BrokenClient:
        def start_as_current_observation(self, **kwargs):
            raise RuntimeError("exporter unavailable")

    monkeypatch.setattr(bridge, "setup_langfuse", BrokenClient)
    tracer = EnhancedSuperOptixTracer(
        "demo", enable_external_tracing=True,
        observability_backend="langfuse", auto_load=False,
    )
    with tracer.trace_operation("agent_run", "agent.demo"):
        tracer.add_event("progress", "agent.demo", {"status": "success"})

    assert tracer.performance_stats["total_operations"] == 1
    assert len(tracer.traces) == 3


def test_otel_payload_mask_preserves_metrics(monkeypatch):
    pytest.importorskip("langfuse")
    monkeypatch.delenv("SUPEROPTIX_LANGFUSE_CAPTURE_CONTENT", raising=False)
    params = SimpleNamespace(spans={
        "span": SimpleNamespace(attributes={
            "input.value": "private prompt",
            "gen_ai.prompt.0.content": "private prompt",
            "gen_ai.usage.input_tokens": 12,
        }),
    })
    result = bridge.mask_otel_spans(params=params)
    deleted = result.span_patches["span"].delete_attributes
    assert "input.value" in deleted
    assert "gen_ai.prompt.0.content" in deleted
    assert "gen_ai.usage.input_tokens" not in deleted
