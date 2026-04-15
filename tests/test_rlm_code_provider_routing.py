"""Tests for framework RLM provider routing with `rlm_code`."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

from superoptix.runners import openai_runtime_helpers as openai_helpers
from superoptix.runners import pydantic_runtime_helpers as pydantic_helpers


def test_build_openai_agent_sandbox_unavailable_falls_back(monkeypatch):
    class _Agent:
        def __init__(self, **kwargs):  # noqa: ANN003
            self.kwargs = kwargs

    fake_agents = ModuleType("agents")
    fake_agents.Agent = _Agent
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    agent = openai_helpers.build_openai_agent(
        name="demo",
        instructions="test",
        model="gpt-4o-mini",
        tools=[],
        spec_data={"openai_agent": {"sandbox": {"enabled": True}}},
    )

    assert isinstance(agent, _Agent)
    assert agent.kwargs["name"] == "demo"
    assert agent.kwargs["instructions"] == "test"


@pytest.mark.asyncio
async def test_openai_rlm_code_replace_skips_framework_runner(monkeypatch):
    async def _fake_rlm_code_completion(*, prompt, config, model_name):  # noqa: ARG001
        return "rlm-code-final", None

    monkeypatch.setattr(
        openai_helpers,
        "run_rlm_code_completion",
        _fake_rlm_code_completion,
    )

    calls = {"runner": 0}

    class _Runner:
        @staticmethod
        async def run(agent, input):  # noqa: ARG001
            calls["runner"] += 1
            return "runner-result"

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    spec = {
        "openai_agent": {
            "rlm": {
                "enabled": True,
                "provider": "rlm_code",
                "mode": "replace",
            }
        }
    }

    result = await openai_helpers.run_with_optional_rlm(
        agent=object(),
        prompt="hello",
        spec_data=spec,
        model_name="gpt-4o-mini",
    )

    assert result == "rlm-code-final"
    assert calls["runner"] == 0


@pytest.mark.asyncio
async def test_openai_rlm_code_failure_falls_back_to_direct_when_native_missing(monkeypatch):
    async def _fake_rlm_code_completion(*, prompt, config, model_name):  # noqa: ARG001
        return None, "simulated failure"

    monkeypatch.setattr(
        openai_helpers,
        "run_rlm_code_completion",
        _fake_rlm_code_completion,
    )

    calls = {"inputs": []}

    class _Runner:
        @staticmethod
        async def run(agent, input):  # noqa: ARG001
            calls["inputs"].append(input)
            return "fallback-direct"

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    # Force `from rlm import RLM` to fail on fallback path.
    monkeypatch.setitem(sys.modules, "rlm", ModuleType("rlm"))

    spec = {
        "openai_agent": {
            "rlm": {
                "enabled": True,
                "provider": "rlm_code",
                "mode": "assist",
            }
        }
    }

    result = await openai_helpers.run_with_optional_rlm(
        agent=object(),
        prompt="hello",
        spec_data=spec,
        model_name="gpt-4o-mini",
    )

    assert result == "fallback-direct"
    assert calls["inputs"] == ["hello"]


@pytest.mark.asyncio
async def test_pydantic_rlm_code_assist_augments_prompt(monkeypatch):
    async def _fake_rlm_code_completion(*, prompt, config, model_name):  # noqa: ARG001
        return "draft from rlm_code", None

    monkeypatch.setattr(
        pydantic_helpers,
        "run_rlm_code_completion",
        _fake_rlm_code_completion,
    )

    class _Agent:
        def __init__(self):
            self.prompts: list[str] = []

        async def run(self, prompt: str):
            self.prompts.append(prompt)
            return SimpleNamespace(output="agent-result")

    agent = _Agent()
    spec = {
        "pydantic_ai": {
            "rlm": {
                "enabled": True,
                "provider": "rlm_code",
                "mode": "assist",
            }
        }
    }

    result = await pydantic_helpers.run_agent_with_optional_rlm(
        agent=agent,
        prompt="original prompt",
        spec_data=spec,
        model_name="openai:gpt-4o-mini",
    )

    assert result.output == "agent-result"
    assert len(agent.prompts) == 1
    assert "original prompt" in agent.prompts[0]
    assert "draft from rlm_code" in agent.prompts[0]


@pytest.mark.asyncio
async def test_openai_native_provider_does_not_route_to_rlm_code(monkeypatch):
    calls = {"rlm_code": 0, "runner_inputs": []}

    async def _fake_rlm_code_completion(*, prompt, config, model_name):  # noqa: ARG001
        calls["rlm_code"] += 1
        return "unexpected", None

    monkeypatch.setattr(
        openai_helpers,
        "run_rlm_code_completion",
        _fake_rlm_code_completion,
    )

    class _FakeRLM:
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def completion(self, prompt: str):  # noqa: ARG002
            return SimpleNamespace(response="native-openai-draft")

    fake_rlm_module = ModuleType("rlm")
    fake_rlm_module.RLM = _FakeRLM
    monkeypatch.setitem(sys.modules, "rlm", fake_rlm_module)

    class _Runner:
        @staticmethod
        async def run(agent, input):  # noqa: ARG001
            calls["runner_inputs"].append(input)
            return "runner-native"

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    spec = {
        "openai_agent": {
            "rlm": {
                "enabled": True,
                "provider": "native",
                "mode": "assist",
            }
        }
    }

    result = await openai_helpers.run_with_optional_rlm(
        agent=object(),
        prompt="native prompt",
        spec_data=spec,
        model_name="gpt-4o-mini",
    )

    assert result == "runner-native"
    assert calls["rlm_code"] == 0
    assert len(calls["runner_inputs"]) == 1
    assert "native-openai-draft" in calls["runner_inputs"][0]


@pytest.mark.asyncio
async def test_pydantic_native_provider_does_not_route_to_rlm_code(monkeypatch):
    calls = {"rlm_code": 0}

    async def _fake_rlm_code_completion(*, prompt, config, model_name):  # noqa: ARG001
        calls["rlm_code"] += 1
        return "unexpected", None

    monkeypatch.setattr(
        pydantic_helpers,
        "run_rlm_code_completion",
        _fake_rlm_code_completion,
    )

    class _FakeRLM:
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def completion(self, prompt: str):  # noqa: ARG002
            return SimpleNamespace(response="native-rlm-final")

    fake_rlm_module = ModuleType("rlm")
    fake_rlm_module.RLM = _FakeRLM
    monkeypatch.setitem(sys.modules, "rlm", fake_rlm_module)

    spec = {
        "pydantic_ai": {
            "rlm": {
                "enabled": True,
                "provider": "native",
                "mode": "replace",
            }
        }
    }

    result = await pydantic_helpers.run_agent_with_optional_rlm(
        agent=object(),
        prompt="original prompt",
        spec_data=spec,
        model_name="openai:gpt-4o-mini",
    )

    assert result == "native-rlm-final"
    assert calls["rlm_code"] == 0


@pytest.mark.asyncio
async def test_openai_run_passes_sandbox_run_config_when_available(monkeypatch):
    sentinel_run_config = object()
    monkeypatch.setattr(
        openai_helpers,
        "build_openai_run_config",
        lambda spec_data, default_workflow_name="": sentinel_run_config,  # noqa: ARG005
    )

    calls = {"run_config": None}

    class _Runner:
        @staticmethod
        async def run(agent, input, **kwargs):  # noqa: ARG001
            calls["run_config"] = kwargs.get("run_config")
            return "runner-with-sandbox"

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    result = await openai_helpers.run_with_optional_rlm(
        agent=object(),
        prompt="sandbox prompt",
        spec_data={"openai_agent": {"sandbox": {"enabled": True}}},
        model_name="gpt-4o-mini",
    )

    assert result == "runner-with-sandbox"
    assert calls["run_config"] is sentinel_run_config
