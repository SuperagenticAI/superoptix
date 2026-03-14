"""Tests for native protocol config and A2A exposure helpers."""

from __future__ import annotations

import asyncio

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.config import extract_protocol_entries, uses_protocol_runtime
from superoptix.runtime.adapters import CompiledPipelineRuntimeAdapter


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
    assert payload["protocol_version"] == "0.3.0"
    assert payload["skills"][0]["id"] == "research"
    assert payload["skills"][0]["examples"] == ["Investigate the user request"]


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


def test_pipeline_runtime_adapter_supports_sync_pipeline():
    runtime = CompiledPipelineRuntimeAdapter(_SyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))

    assert result == {"response": "HELLO"}


def test_pipeline_runtime_adapter_supports_async_pipeline():
    runtime = CompiledPipelineRuntimeAdapter(_AsyncPipeline())

    result = asyncio.run(runtime.invoke({"query": "Hello"}))

    assert result == {"response": "hello"}
