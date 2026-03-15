"""Tests for native protocol config and A2A exposure helpers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.mappers import normalize_agent_card
from superoptix.protocols.config import extract_protocol_entries, uses_protocol_runtime
from superoptix.runtime import RuntimeContext, runtime_registry
from superoptix.runtime.adapters import (
    CompiledPipelineRuntimeAdapter,
    CrewAIRuntimeAdapter,
    DSPyRuntimeAdapter,
    GoogleADKRuntimeAdapter,
    PydanticAIRuntimeAdapter,
)


def test_extract_protocol_entries_merges_legacy_mcp_servers():
    spec = {
        "protocols": [{"type": "a2a", "url": "https://planner.example.com"}],
        "mcp_servers": ["mcp://localhost:8080/github"],
    }

    entries = extract_protocol_entries(spec)

    assert entries == [
        {"type": "a2a", "url": "https://planner.example.com"},
        {"type": "mcp", "url": "mcp://localhost:8080/github"},
    ]


def test_uses_protocol_runtime_detects_native_protocols():
    assert uses_protocol_runtime({"tool_backend": "protocols"}) is True
    assert uses_protocol_runtime({"tool_backend": "agenspy"}) is True
    assert uses_protocol_runtime({"protocols": [{"type": "a2a", "url": "https://x"}]}) is True
    assert uses_protocol_runtime({"tool_backend": "dspy"}) is False


def test_build_a2a_agent_card_payload_from_playbook():
    payload = build_a2a_agent_card_payload(
        metadata={"name": "Research Agent", "version": "1.2.3"},
        spec={
            "persona": {"goal": "Answer research questions"},
            "tasks": [
                {
                    "name": "research",
                    "instruction": "Investigate the user request",
                }
            ],
        },
        agent_url="https://agents.example.com/research",
    )

    assert payload["name"] == "Research Agent"
    assert payload["supportedInterfaces"][0]["protocolVersion"] == "1.0"
    assert payload["supportedInterfaces"][0]["protocolBinding"] == "HTTP+JSON"
    assert payload["skills"][0]["id"] == "research"
    assert payload["skills"][0]["examples"] == ["Investigate the user request"]
    assert payload["capabilities"]["extendedAgentCard"] is False


def test_normalize_agent_card_upgrades_legacy_shape():
    payload = normalize_agent_card(
        {
            "name": "Legacy Agent",
            "url": "https://agent.example.com/a2a/jsonrpc",
            "protocol_version": "0.3.0",
            "preferred_transport": "JSONRPC",
            "capabilities": {
                "streaming": True,
                "push_notifications": False,
                "state_transition_history": True,
            },
            "supports_authenticated_extended_card": False,
            "skills": [],
        }
    )

    assert payload["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"
    assert payload["supportedInterfaces"][0]["protocolVersion"] == "0.3.0"
    assert payload["capabilities"]["pushNotifications"] is False
    assert payload["capabilities"]["stateTransitionHistory"] is True


class _SyncPipeline:
    metadata = {"name": "Sync"}
    spec = {"tasks": []}

    def run(self, **inputs):
        return {"response": inputs["query"].upper()}


class _AsyncPipeline:
    metadata = {"name": "Async"}
    spec = {"tasks": []}

    async def run(self, **inputs):
        return {"response": inputs["query"].lower()}


class _ContextAwarePipeline:
    metadata = {"name": "ContextAware"}
    spec = {"tasks": []}

    def __init__(self):
        self.seen = None

    def run(self, query: str, task_id: str | None = None, context_id: str | None = None):
        self.seen = (query, task_id, context_id)
        return {"response": query}


class _StreamingPipeline:
    metadata = {"name": "Streamer"}
    spec = {"tasks": []}

    async def stream(self, query: str, **_: str) -> AsyncIterator[dict]:
        yield {"response": f"chunk:{query}:1"}
        yield {"response": f"chunk:{query}:2"}


class _CancelablePipeline:
    metadata = {"name": "Cancelable"}
    spec = {"tasks": []}

    def __init__(self):
        self.cancelled = []

    def run(self, **inputs):
        return {"response": inputs["query"]}

    async def cancel(self, task_id: str, **kwargs):
        self.cancelled.append((task_id, kwargs.get("context_id")))
        return True


class _FakePrediction:
    def __init__(self, response: str):
        self.response = response


class _FakeDSPyProgram:
    def __call__(self, query: str):
        return _FakePrediction(f"dspy:{query}")


class _FakeDSPyModule:
    metadata = {"name": "DSPy Minimal"}
    spec = {"tasks": []}

    def build_program(self):
        return _FakeDSPyProgram()


def test_pipeline_runtime_adapter_supports_sync_pipeline():
    runtime = CompiledPipelineRuntimeAdapter(_SyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))

    assert result == {"response": "HELLO"}


def test_pipeline_runtime_adapter_supports_async_pipeline():
    runtime = CompiledPipelineRuntimeAdapter(_AsyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))

    assert result == {"response": "hello"}


def test_pipeline_runtime_adapter_passes_context_fields():
    pipeline = _ContextAwarePipeline()
    runtime = CompiledPipelineRuntimeAdapter(pipeline)

    result = asyncio.run(
        runtime.invoke(
            {"query": "Hello"},
            context=RuntimeContext(task_id="t-1", context_id="c-1"),
        )
    )

    assert result == {"response": "Hello"}
    assert pipeline.seen == ("Hello", "t-1", "c-1")


def test_pipeline_runtime_adapter_streams_when_pipeline_supports_stream():
    runtime = CompiledPipelineRuntimeAdapter(_StreamingPipeline())

    async def _collect():
        return [chunk async for chunk in runtime.stream({"query": "hi"})]

    chunks = asyncio.run(_collect())

    assert chunks == [
        {"response": "chunk:hi:1"},
        {"response": "chunk:hi:2"},
    ]


def test_pipeline_runtime_adapter_cancels_when_pipeline_supports_cancel():
    pipeline = _CancelablePipeline()
    runtime = CompiledPipelineRuntimeAdapter(pipeline)

    cancelled = asyncio.run(
        runtime.cancel("task-7", context=RuntimeContext(context_id="ctx-9"))
    )

    assert cancelled is True
    assert pipeline.cancelled == [("task-7", "ctx-9")]


def test_dspy_runtime_adapter_supports_build_program_modules():
    runtime = DSPyRuntimeAdapter(_FakeDSPyModule())

    result = asyncio.run(runtime.invoke({"query": "hello"}))
    caps = asyncio.run(runtime.capabilities())

    assert result["response"] == "dspy:hello"
    assert result["framework"] == "dspy"
    assert caps["framework"] == "dspy"


def test_pydantic_ai_runtime_adapter_adds_framework_metadata():
    runtime = PydanticAIRuntimeAdapter(_AsyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))
    metadata = asyncio.run(runtime.metadata())

    assert result["framework"] == "pydantic_ai"
    assert metadata["metadata"]["framework"] == "pydantic-ai"


def test_crewai_runtime_adapter_adds_framework_metadata():
    runtime = CrewAIRuntimeAdapter(_SyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))
    metadata = asyncio.run(runtime.metadata())

    assert result["framework"] == "crewai"
    assert metadata["metadata"]["framework"] == "crewai"


def test_google_adk_runtime_adapter_adds_framework_metadata():
    runtime = GoogleADKRuntimeAdapter(_SyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))
    metadata = asyncio.run(runtime.metadata())

    assert result["framework"] == "google_adk"
    assert metadata["metadata"]["framework"] == "google-adk"


def test_runtime_registry_exposes_framework_specific_adapters():
    assert "compiled_pipeline" in runtime_registry.registered()
    assert "crewai" in runtime_registry.registered()
    assert "dspy" in runtime_registry.registered()
    assert "google_adk" in runtime_registry.registered()
    assert "pydantic_ai" in runtime_registry.registered()
