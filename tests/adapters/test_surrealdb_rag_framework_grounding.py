"""Integration-style RAG grounding tests for SurrealDB demo playbooks."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEMO_DIR = Path("superoptix/agents/demo")
GROUNDING_QUERY = "What is NEON-FOX-742?"
SEEDED_DOC = "NEON-FOX-742 is a seeded SurrealDB memory token. token retrieval success"


def _load_playbook(filename: str) -> dict[str, Any]:
    path = DEMO_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _compile_pipeline(
    framework: str, playbook: dict[str, Any], tmp_path: Path
) -> Path:
    registry = _load_local_framework_registry()
    output_path = tmp_path / f"{framework}_pipeline.py"
    registry.compile_agent(framework, playbook, str(output_path))
    assert output_path.exists()
    return output_path


def _load_local_framework_registry():
    module_name = "superoptix.adapters._framework_registry_local_for_tests"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached.FrameworkRegistry

    module_path = REPO_ROOT / "superoptix" / "adapters" / "framework_registry.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.FrameworkRegistry


def _import_compiled_module(module_path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _get_pipeline_class(module: ModuleType):
    for name, obj in module.__dict__.items():
        if (
            isinstance(obj, type)
            and name.endswith("Pipeline")
            and obj.__module__ == module.__name__
        ):
            return obj
    raise AssertionError(f"No generated Pipeline class found in {module.__name__}")


def _patch_seeded_surrealdb_retrieval(
    monkeypatch: pytest.MonkeyPatch, rag_mixin_cls: type
) -> dict[str, Any]:
    state: dict[str, Any] = {"calls": []}

    def _fake_setup(self, spec_data: dict[str, Any]) -> bool:  # noqa: ARG001
        return True

    async def _fake_retrieve(self, query: str, top_k: int | None = None) -> list[str]:
        state["calls"].append({"query": query, "top_k": top_k})
        return [SEEDED_DOC]

    monkeypatch.setattr(rag_mixin_cls, "setup_rag", _fake_setup)
    monkeypatch.setattr(rag_mixin_cls, "retrieve_context", _fake_retrieve)
    return state


@pytest.mark.asyncio
async def test_openai_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_openai_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("openai", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    class _FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeRunner:
        @staticmethod
        async def run(agent, input):  # noqa: ARG001
            captured["prompts"].append(input)
            return SimpleNamespace(final_output="token retrieval success")

    fake_agents = ModuleType("agents")
    fake_agents.Agent = _FakeAgent
    fake_agents.Runner = _FakeRunner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)

    module = _import_compiled_module(pipeline_path, "test_openai_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_claude_sdk_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_claude_sdk_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("claude-sdk", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    class _ClaudeAgentOptions:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _TextBlock:
        def __init__(self, text: str):
            self.text = text

    class _AssistantMessage:
        def __init__(self, content):
            self.content = content

    class _ResultMessage:
        pass

    class _ToolUseBlock:
        pass

    class _ToolResultBlock:
        pass

    class _ThinkingBlock:
        pass

    async def _fake_query(prompt: str, options):  # noqa: ARG001
        captured["prompts"].append(prompt)
        yield _AssistantMessage([_TextBlock("token retrieval success")])
        yield _ResultMessage()

    fake_claude_sdk = ModuleType("claude_agent_sdk")
    fake_claude_sdk.ClaudeAgentOptions = _ClaudeAgentOptions
    fake_claude_sdk.ClaudeSDKClient = object
    fake_claude_sdk.query = _fake_query
    fake_claude_sdk.AssistantMessage = _AssistantMessage
    fake_claude_sdk.ResultMessage = _ResultMessage
    fake_claude_sdk.TextBlock = _TextBlock
    fake_claude_sdk.ToolUseBlock = _ToolUseBlock
    fake_claude_sdk.ToolResultBlock = _ToolResultBlock
    fake_claude_sdk.ThinkingBlock = _ThinkingBlock
    fake_claude_sdk.tool = lambda *args, **kwargs: None
    fake_claude_sdk.create_sdk_mcp_server = lambda *args, **kwargs: None
    fake_claude_sdk.SdkMcpTool = object
    monkeypatch.setitem(sys.modules, "claude_agent_sdk", fake_claude_sdk)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    module = _import_compiled_module(pipeline_path, "test_claude_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert "token retrieval success" in result["retrieved_response"]
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_microsoft_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_microsoft_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("microsoft", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    class _FakeOpenAIChatClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeAzureOpenAIChatClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeResponse:
        def __init__(self, text: str):
            self.text = text

    class _FakeAgent:
        def __init__(self, chat_client, name: str, instructions: str, tools=None):
            self.chat_client = chat_client
            self.name = name
            self.instructions = instructions
            self.tools = tools

        async def run(self, user_message: str):
            captured["prompts"].append(user_message)
            return _FakeResponse("token retrieval success")

    fake_agent_framework = ModuleType("agent_framework")
    fake_agent_framework.Agent = _FakeAgent
    fake_agent_framework.ChatAgent = _FakeAgent
    fake_agent_framework_openai = ModuleType("agent_framework.openai")
    fake_agent_framework_openai.OpenAIChatClient = _FakeOpenAIChatClient
    fake_agent_framework_azure = ModuleType("agent_framework.azure")
    fake_agent_framework_azure.AzureOpenAIChatClient = _FakeAzureOpenAIChatClient
    monkeypatch.setitem(sys.modules, "agent_framework", fake_agent_framework)
    monkeypatch.setitem(sys.modules, "agent_framework.openai", fake_agent_framework_openai)
    monkeypatch.setitem(sys.modules, "agent_framework.azure", fake_agent_framework_azure)

    module = _import_compiled_module(
        pipeline_path, "test_microsoft_surrealdb_pipeline"
    )
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_deepagents_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_deepagents_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("deepagents", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    fake_langchain_chat = ModuleType("langchain.chat_models")
    fake_langchain_chat.init_chat_model = lambda model: {"model": model}
    monkeypatch.setitem(sys.modules, "langchain.chat_models", fake_langchain_chat)

    class _FakeDeepAgent:
        def invoke(self, payload: dict[str, Any]):
            prompt = payload["messages"][0]["content"]
            captured["prompts"].append(prompt)
            return {"messages": [SimpleNamespace(content="token retrieval success")]}

    fake_deepagents_graph = ModuleType("superoptix.vendor.deepagents.graph")
    fake_deepagents_graph.create_deep_agent = lambda **kwargs: _FakeDeepAgent()  # noqa: ARG005
    monkeypatch.setitem(
        sys.modules, "superoptix.vendor.deepagents.graph", fake_deepagents_graph
    )

    fake_deepagents_helpers = ModuleType("superoptix.runners.deepagents_runtime_helpers")
    fake_deepagents_helpers.build_instructions = lambda spec: "test instructions"  # noqa: ARG005
    fake_deepagents_helpers.resolve_model = lambda language_model, model_config=None: "anthropic:claude-sonnet-4-20250514"  # noqa: ARG005
    monkeypatch.setitem(
        sys.modules, "superoptix.runners.deepagents_runtime_helpers", fake_deepagents_helpers
    )

    module = _import_compiled_module(pipeline_path, "test_deepagents_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_pydantic_ai_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_pydanticai_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("pydantic-ai", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    class _FakeModelSettings:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def run(self, prompt: str):
            captured["prompts"].append(prompt)
            return SimpleNamespace(output="token retrieval success", messages=[])

    fake_pydantic_ai = ModuleType("pydantic_ai")
    fake_pydantic_ai.Agent = _FakeAgent
    monkeypatch.setitem(sys.modules, "pydantic_ai", fake_pydantic_ai)

    fake_pydantic_ai_settings = ModuleType("pydantic_ai.settings")
    fake_pydantic_ai_settings.ModelSettings = _FakeModelSettings
    monkeypatch.setitem(sys.modules, "pydantic_ai.settings", fake_pydantic_ai_settings)

    fake_pydantic_helpers = ModuleType("superoptix.runners.pydantic_runtime_helpers")
    fake_pydantic_helpers.build_stackone_tools = lambda spec_data, framework="pydantic_ai": []  # noqa: ARG005
    fake_pydantic_helpers.build_instructions = lambda spec_data: "test instructions"  # noqa: ARG005
    fake_pydantic_helpers.get_pydantic_rlm_config = lambda spec_data: {"enabled": False}  # noqa: ARG005

    async def _fake_run_agent_with_optional_rlm(
        *,
        agent,
        prompt,
        spec_data,
        model_name,
        logfire_enabled=True,
    ):  # noqa: ARG001
        captured["prompts"].append(prompt)
        return SimpleNamespace(output="token retrieval success", messages=[])

    fake_pydantic_helpers.run_agent_with_optional_rlm = _fake_run_agent_with_optional_rlm
    fake_pydantic_helpers.resolve_model = (
        lambda language_model, model_config=None: "ollama:llama3.1:8b"  # noqa: ARG005
    )
    monkeypatch.setitem(
        sys.modules, "superoptix.runners.pydantic_runtime_helpers", fake_pydantic_helpers
    )

    module = _import_compiled_module(pipeline_path, "test_pydantic_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


def test_crewai_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_crewai_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("crewai", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    class _FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeTask:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeCrew:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def kickoff(self, inputs: dict[str, Any]):
            captured["prompts"].append(str(inputs.get("query", "")))
            return {"raw": "token retrieval success"}

    class _FakeProcess:
        sequential = "sequential"

    fake_crewai = ModuleType("crewai")
    fake_crewai.Agent = _FakeAgent
    fake_crewai.Crew = _FakeCrew
    fake_crewai.Process = _FakeProcess
    fake_crewai.Task = _FakeTask
    monkeypatch.setitem(sys.modules, "crewai", fake_crewai)

    fake_crewai_helpers = ModuleType("superoptix.runners.crewai_runtime_helpers")
    fake_crewai_helpers.build_instructions = lambda spec: "test instructions"  # noqa: ARG005
    fake_crewai_helpers.build_task_description = lambda spec: "task desc"  # noqa: ARG005
    fake_crewai_helpers.create_crewai_llm = (
        lambda model, language_model: {"model": model}  # noqa: ARG005
    )
    fake_crewai_helpers.extract_crewai_output = lambda result: "token retrieval success"  # noqa: ARG005
    fake_crewai_helpers.resolve_model = (
        lambda language_model, model_config=None: "ollama/llama3.1:8b"  # noqa: ARG005
    )
    monkeypatch.setitem(
        sys.modules, "superoptix.runners.crewai_runtime_helpers", fake_crewai_helpers
    )

    module = _import_compiled_module(pipeline_path, "test_crewai_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_google_adk_surrealdb_rag_prompt_grounding(tmp_path: Path, monkeypatch):
    playbook = _load_playbook("rag_surrealdb_adk_demo_playbook.yaml")
    pipeline_path = _compile_pipeline("google-adk", playbook, tmp_path)

    captured: dict[str, Any] = {"prompts": []}

    fake_adk_helpers = ModuleType("superoptix.runners.google_adk_runtime_helpers")
    fake_adk_helpers.create_agent_runner = lambda **kwargs: (  # noqa: ARG005
        object(),
        object(),
        {"model": "gemini-2.5-flash", "tool_count": 0, "app_name": "test_app"},
    )
    fake_adk_helpers.get_google_adk_rlm_config = (
        lambda spec_data: {"enabled": False}  # noqa: ARG005
    )

    async def _fake_run_agent_with_optional_rlm(
        *,
        agent,
        runner,
        prompt,
        spec_data,
        model_name,
        app_name,
        logfire_enabled=True,
    ):  # noqa: ARG001
        captured["prompts"].append(prompt)
        return "token retrieval success"

    fake_adk_helpers.run_agent_with_optional_rlm = _fake_run_agent_with_optional_rlm
    monkeypatch.setitem(
        sys.modules, "superoptix.runners.google_adk_runtime_helpers", fake_adk_helpers
    )

    module = _import_compiled_module(pipeline_path, "test_adk_surrealdb_pipeline")
    rag_state = _patch_seeded_surrealdb_retrieval(monkeypatch, module.RAGMixin)
    pipeline_cls = _get_pipeline_class(module)
    pipeline = pipeline_cls()

    result = await pipeline.run(knowledge_query=GROUNDING_QUERY)

    assert result["retrieved_response"] == "token retrieval success"
    assert rag_state["calls"] == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert len(captured["prompts"]) == 1
    prompt = captured["prompts"][0]
    assert "Retrieved context:" in prompt
    assert SEEDED_DOC in prompt
    assert f"User query:\n{GROUNDING_QUERY}" in prompt


@pytest.mark.asyncio
async def test_dspy_surrealdb_rag_prompt_grounding():
    """DSPy runner path: retrieval context is fetched and appended to query."""
    from superoptix.runners.dspy_runner import DSPyRunner

    playbook = _load_playbook("rag_surrealdb_dspy_demo_playbook.yaml")
    spec_data = playbook.get("spec", {})

    calls: list[dict[str, Any]] = []

    class _FakeRAGHelper:
        async def retrieve_context(
            self, query: str, top_k: int | None = None
        ) -> list[str]:
            calls.append({"query": query, "top_k": top_k})
            return [SEEDED_DOC]

    runner = DSPyRunner.__new__(DSPyRunner)
    runner._rag_initialized = True
    runner._rag_enabled = True
    runner._rag_helper = _FakeRAGHelper()

    context_text = await runner._retrieve_context_text(spec_data, GROUNDING_QUERY)
    augmented_query = runner._augment_query_with_context(GROUNDING_QUERY, context_text)

    assert calls == [{"query": GROUNDING_QUERY, "top_k": 5}]
    assert SEEDED_DOC in context_text
    assert "Relevant Context:" in augmented_query
    assert SEEDED_DOC in augmented_query
    assert GROUNDING_QUERY in augmented_query
