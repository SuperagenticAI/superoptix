from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from pydantic import BaseModel

from superoptix.harness import HarnessAgent, LocalSandbox, SandboxPolicy, discover_context
from superoptix.harness.backends.codex import CodexHarnessBackend
from superoptix.harness.backends.deepagents import (
    DeepAgentsHarnessBackend,
    _create_deepagents_backend,
    _resolve_deepagents_config,
)
from superoptix.harness.backends.google_adk import GoogleADKHarnessBackend
from superoptix.harness.backends.openai import OpenAIHarnessBackend
from superoptix.harness.backends.pydantic_ai import (
    PydanticAIHarnessBackend,
    _build_agent_capability_kwargs,
)
from superoptix.harness.session import resolve_backend
from superoptix.harness.tools import (
    HarnessTool,
    create_builtin_tools,
    to_deepagents_tools,
    to_pydantic_ai_tools,
)
from superoptix.harness.types import HarnessRunResult


class _Answer(BaseModel):
    answer: str
    confidence: float


class _FakeBackend:
    name = "fake"

    def __init__(self):
        self.calls = []

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        return HarnessRunResult(
            text=(
                "done\n"
                "---RESULT_START---\n"
                '{"answer": "yes", "confidence": 0.9}\n'
                "---RESULT_END---"
            ),
            metadata={"framework": self.name},
        )


def test_discover_context_loads_markdown_files(tmp_path):
    (tmp_path / "AGENTS.md").write_text("Base instructions", encoding="utf-8")
    skill_dir = tmp_path / ".agents" / "skills" / "triage"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: triage\ndescription: classify issues\n---\nDo triage.",
        encoding="utf-8",
    )
    roles_dir = tmp_path / ".agents" / "roles"
    roles_dir.mkdir(parents=True)
    (roles_dir / "reviewer.md").write_text(
        "---\nmodel: openai/gpt-4o-mini\n---\nReview carefully.",
        encoding="utf-8",
    )

    context = discover_context(tmp_path)

    assert "Base instructions" in context.system_prompt
    assert "triage" in context.skills
    assert context.skills["triage"].description == "classify issues"
    assert context.roles["reviewer"].model == "openai/gpt-4o-mini"


def test_local_sandbox_read_search_and_path_boundary(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('needle')\n", encoding="utf-8")
    sandbox = LocalSandbox(tmp_path)

    assert "app.py" in sandbox.glob("**/*.py")
    assert "needle" in sandbox.grep("needle", include="*.py")
    assert "print" in sandbox.read("src/app.py")
    with pytest.raises(ValueError):
        sandbox.read("../outside.txt")


def test_local_sandbox_write_and_shell_require_policy(tmp_path):
    sandbox = LocalSandbox(tmp_path)

    with pytest.raises(PermissionError):
        sandbox.write("out.txt", "hello")
    with pytest.raises(PermissionError):
        sandbox.bash("echo hello")

    enabled = LocalSandbox(
        tmp_path,
        policy=SandboxPolicy(allow_write=True, allow_shell=True),
    )
    assert "Wrote" in enabled.write("out.txt", "hello")
    assert enabled.bash("cat out.txt")["stdout"] == "hello"


def test_builtin_tools_follow_sandbox_policy(tmp_path):
    read_only = create_builtin_tools(LocalSandbox(tmp_path))
    assert [tool.name for tool in read_only] == ["read", "grep", "glob"]

    full = create_builtin_tools(
        LocalSandbox(
            tmp_path,
            policy=SandboxPolicy(allow_write=True, allow_shell=True),
        )
    )
    assert [tool.name for tool in full] == [
        "read",
        "grep",
        "glob",
        "write",
        "edit",
        "bash",
    ]


def test_deepagents_tool_conversion_skips_native_tool_names():
    builtin = HarnessTool(
        name="grep",
        description="native grep",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "skip",
    )
    custom = HarnessTool(
        name="lookup_customer",
        description="Lookup a customer",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "ok",
    )

    converted = to_deepagents_tools([builtin, custom])

    assert len(converted) == 1
    assert converted[0].__name__ == "lookup_customer"


def test_pydantic_ai_tool_conversion(monkeypatch):
    captured = []

    class _Tool:
        def __init__(self, function, **kwargs):
            self.function = function
            self.kwargs = kwargs
            captured.append(kwargs)

    fake_pydantic_ai = ModuleType("pydantic_ai")
    fake_pydantic_ai.Tool = _Tool
    monkeypatch.setitem(sys.modules, "pydantic_ai", fake_pydantic_ai)

    converted = to_pydantic_ai_tools(
        [
            HarnessTool(
                name="read",
                description="read",
                parameters={"type": "object", "properties": {}, "required": []},
                execute=lambda args: "ok",
            )
        ]
    )

    assert len(converted) == 1
    assert captured == [{"name": "read", "description": "read"}]


def test_resolve_backend_includes_codex_deepagents_and_pydantic_ai():
    assert resolve_backend("codex").name == "codex"
    assert resolve_backend("deepagents").name == "deepagents"
    assert resolve_backend("pydantic-ai").name == "pydantic_ai"


@pytest.mark.asyncio
async def test_harness_session_prompt_stores_state_and_parses_result(tmp_path):
    backend = _FakeBackend()
    agent = HarnessAgent(name="demo", cwd=tmp_path, backend=backend)
    session = await agent.session("s1")

    parsed = await session.prompt("Return structured output", result_type=_Answer)

    assert parsed.answer == "yes"
    assert parsed.confidence == 0.9
    assert len(session.state.messages) == 2
    assert backend.calls[0]["agent_name"] == "demo"
    assert backend.calls[0]["cwd"] == tmp_path.resolve()
    assert isinstance(backend.calls[0]["sandbox"], LocalSandbox)
    assert [tool.name for tool in backend.calls[0]["tools"]] == ["read", "grep", "glob"]


@pytest.mark.asyncio
async def test_codex_backend_runs_exec_with_sandbox_policy(monkeypatch, tmp_path):
    calls = {}

    class _FakeProcess:
        returncode = 0

        async def communicate(self):
            return b"stdout fallback", b""

    async def fake_create_subprocess_exec(*args, **kwargs):
        calls["args"] = list(args)
        calls["kwargs"] = kwargs
        output_index = calls["args"].index("--output-last-message") + 1
        Path(calls["args"][output_index]).write_text("codex-result", encoding="utf-8")
        return _FakeProcess()

    monkeypatch.setattr(
        "superoptix.harness.backends.codex.asyncio.create_subprocess_exec",
        fake_create_subprocess_exec,
    )
    sandbox = LocalSandbox(tmp_path, policy=SandboxPolicy(allow_write=True))

    result = await CodexHarnessBackend().run(
        prompt="fix it",
        system_prompt="system",
        agent_name="demo",
        cwd=tmp_path,
        sandbox=sandbox,
        model_config={"model": "gpt-test", "codex_bin": "/bin/codex"},
    )

    assert result.text == "codex-result"
    assert result.metadata["sandbox"] == "workspace-write"
    assert calls["args"][:2] == ["/bin/codex", "exec"]
    assert calls["args"][calls["args"].index("--sandbox") + 1] == "workspace-write"
    assert calls["args"][calls["args"].index("--model") + 1] == "gpt-test"
    assert calls["args"][calls["args"].index("--cd") + 1] == str(tmp_path.resolve())
    assert "System instructions" in calls["args"][-1]


@pytest.mark.asyncio
async def test_codex_backend_defaults_to_read_only(monkeypatch, tmp_path):
    calls = {}

    class _FakeProcess:
        returncode = 0

        async def communicate(self):
            return b"plain stdout", b""

    async def fake_create_subprocess_exec(*args, **kwargs):  # noqa: ARG001
        calls["args"] = list(args)
        return _FakeProcess()

    monkeypatch.setattr(
        "superoptix.harness.backends.codex.asyncio.create_subprocess_exec",
        fake_create_subprocess_exec,
    )

    result = await CodexHarnessBackend().run(
        prompt="inspect",
        system_prompt="",
        agent_name="demo",
        cwd=tmp_path,
    )

    assert result.text == "plain stdout"
    assert calls["args"][calls["args"].index("--sandbox") + 1] == "read-only"


@pytest.mark.asyncio
async def test_harness_session_includes_recent_history(tmp_path):
    backend = _FakeBackend()
    agent = HarnessAgent(name="demo", cwd=tmp_path, backend=backend)
    session = await agent.session("s1")

    await session.prompt("first")
    await session.prompt("second")

    assert "Conversation so far" in backend.calls[1]["prompt"]
    assert "user: first" in backend.calls[1]["prompt"]


@pytest.mark.asyncio
async def test_harness_skill_runs_discovered_skill_with_args(tmp_path):
    skill_dir = tmp_path / ".agents" / "skills" / "triage"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: triage\n---\nClassify issue {{ issue }}.",
        encoding="utf-8",
    )
    backend = _FakeBackend()
    agent = HarnessAgent(name="demo", cwd=tmp_path, backend=backend)
    session = await agent.session("s1")

    await session.skill("triage", args={"issue": 123})

    assert "Classify issue" in backend.calls[0]["prompt"]
    assert '"issue": 123' in backend.calls[0]["prompt"]


@pytest.mark.asyncio
async def test_openai_backend_routes_to_openai_agents(monkeypatch):
    captured = {}

    def fake_build_openai_agent(**kwargs):
        captured["agent_kwargs"] = kwargs
        return {"agent": kwargs["name"]}

    class _Runner:
        @staticmethod
        async def run(agent, input, **kwargs):  # noqa: A002
            assert agent == {"agent": "demo"}
            assert input == "hello"
            assert kwargs == {"run_config": "run-config"}
            return SimpleNamespace(final_output="openai-result")

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    monkeypatch.setitem(sys.modules, "agents", fake_agents)
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.resolve_model",
        lambda language_model, model_config=None: "resolved-model",
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.build_openai_agent",
        fake_build_openai_agent,
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.build_openai_run_config",
        lambda *args, **kwargs: "run-config",
    )

    result = await OpenAIHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
    )

    assert result.text == "openai-result"
    assert result.metadata["framework"] == "openai"
    assert result.metadata["model"] == "resolved-model"
    assert captured["agent_kwargs"]["tools"] == []


@pytest.mark.asyncio
async def test_openai_backend_converts_harness_tools(monkeypatch):
    captured = {}

    def fake_build_openai_agent(**kwargs):
        captured["agent_kwargs"] = kwargs
        return {"agent": kwargs["name"]}

    class _Runner:
        @staticmethod
        async def run(agent, input, **kwargs):  # noqa: A002, ARG004
            return SimpleNamespace(final_output="openai-result")

    def fake_function_tool(*args, **kwargs):  # noqa: ARG001
        def decorate(func):
            return {"name": kwargs.get("name_override"), "func": func}

        return decorate

    fake_agents = ModuleType("agents")
    fake_agents.Runner = _Runner
    fake_agents.function_tool = fake_function_tool
    monkeypatch.setitem(sys.modules, "agents", fake_agents)
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.resolve_model",
        lambda language_model, model_config=None: "resolved-model",
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.build_openai_agent",
        fake_build_openai_agent,
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.openai.build_openai_run_config",
        lambda *args, **kwargs: None,
    )
    tool = HarnessTool(
        name="read",
        description="read",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "ok",
    )

    await OpenAIHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        tools=[tool],
    )

    assert captured["agent_kwargs"]["tools"][0]["name"] == "read"


@pytest.mark.asyncio
async def test_google_adk_backend_routes_to_adk_helpers(monkeypatch):
    calls = {}

    def fake_create_agent_runner(**kwargs):
        calls["create"] = kwargs
        return "agent", "runner", {"model": "gemini", "app_name": "app"}

    async def fake_run_agent_with_optional_rlm(**kwargs):
        calls["run"] = kwargs
        return "adk-result"

    monkeypatch.setattr(
        "superoptix.harness.backends.google_adk.create_agent_runner",
        fake_create_agent_runner,
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.google_adk.run_agent_with_optional_rlm",
        fake_run_agent_with_optional_rlm,
    )

    result = await GoogleADKHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        model="gemini-2.5-flash",
    )

    assert result.text == "adk-result"
    assert calls["create"]["model_config"] == {"model": "gemini-2.5-flash"}
    assert calls["create"]["extra_tools"] == []
    assert calls["run"]["prompt"] == "hello"
    assert calls["run"]["app_name"] == "app"


@pytest.mark.asyncio
async def test_google_adk_backend_converts_harness_tools(monkeypatch):
    calls = {}

    def fake_create_agent_runner(**kwargs):
        calls["create"] = kwargs
        return "agent", "runner", {"model": "gemini", "app_name": "app"}

    async def fake_run_agent_with_optional_rlm(**kwargs):  # noqa: ARG001
        return "adk-result"

    monkeypatch.setattr(
        "superoptix.harness.backends.google_adk.create_agent_runner",
        fake_create_agent_runner,
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.google_adk.run_agent_with_optional_rlm",
        fake_run_agent_with_optional_rlm,
    )
    tool = HarnessTool(
        name="grep",
        description="grep",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "ok",
    )

    await GoogleADKHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        tools=[tool],
    )

    assert calls["create"]["extra_tools"][0].__name__ == "grep"


@pytest.mark.asyncio
async def test_pydantic_ai_backend_routes_to_agent(monkeypatch):
    captured = {}

    class _FakeTool:
        def __init__(self, function, **kwargs):
            self.function = function
            self.kwargs = kwargs

    class _FakeAgent:
        def __init__(self, *args, **kwargs):
            captured["agent_args"] = args
            captured["agent_kwargs"] = kwargs

    fake_pydantic_ai = ModuleType("pydantic_ai")
    fake_pydantic_ai.Agent = _FakeAgent
    fake_pydantic_ai.Tool = _FakeTool
    monkeypatch.setitem(sys.modules, "pydantic_ai", fake_pydantic_ai)
    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.resolve_model",
        lambda language_model, model_config=None: "openai:gpt-4o",
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.build_stackone_tools",
        lambda spec, framework="pydantic_ai": [],
    )

    async def fake_run_agent_with_optional_rlm(**kwargs):
        captured["run"] = kwargs
        return SimpleNamespace(output="pydantic-result")

    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.run_agent_with_optional_rlm",
        fake_run_agent_with_optional_rlm,
    )
    tool = HarnessTool(
        name="read",
        description="read",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "ok",
    )

    result = await PydanticAIHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        tools=[tool],
    )

    assert result.text == "pydantic-result"
    assert result.metadata == {
        "framework": "pydantic_ai",
        "model": "openai:gpt-4o",
        "tool_count": 1,
        "usage_limits": False,
        "capability_count": 0,
    }
    assert captured["agent_args"] == ("openai:gpt-4o",)
    assert captured["agent_kwargs"]["instructions"] == "system"
    assert captured["agent_kwargs"]["name"] == "demo"
    assert captured["agent_kwargs"]["tools"][0].kwargs["name"] == "read"
    assert captured["run"]["run_kwargs"] == {}
    assert captured["run"]["prompt"] == "hello"
    assert captured["run"]["model_name"] == "openai:gpt-4o"


@pytest.mark.asyncio
async def test_pydantic_ai_backend_passes_usage_limits(monkeypatch):
    captured = {}

    class _FakeUsageLimits:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _FakeAgent:
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

    fake_pydantic_ai = ModuleType("pydantic_ai")
    fake_pydantic_ai.Agent = _FakeAgent
    fake_usage = ModuleType("pydantic_ai.usage")
    fake_usage.UsageLimits = _FakeUsageLimits
    monkeypatch.setitem(sys.modules, "pydantic_ai", fake_pydantic_ai)
    monkeypatch.setitem(sys.modules, "pydantic_ai.usage", fake_usage)
    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.resolve_model",
        lambda language_model, model_config=None: "openai:gpt-4o",
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.to_pydantic_ai_tools",
        lambda tools: [],
    )
    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.build_stackone_tools",
        lambda spec, framework="pydantic_ai": [],
    )

    async def fake_run_agent_with_optional_rlm(**kwargs):
        captured["run"] = kwargs
        return "limited-result"

    monkeypatch.setattr(
        "superoptix.harness.backends.pydantic_ai.run_agent_with_optional_rlm",
        fake_run_agent_with_optional_rlm,
    )

    result = await PydanticAIHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        model_config={
            "pydantic_usage_limits": {
                "request_limit": 3,
                "tool_calls_limit": 8,
                "count_tokens_before_request": True,
            }
        },
    )

    usage_limits = captured["run"]["run_kwargs"]["usage_limits"]
    assert usage_limits.kwargs == {
        "request_limit": 3,
        "tool_calls_limit": 8,
        "count_tokens_before_request": True,
    }
    assert result.metadata["usage_limits"] is True


def test_pydantic_ai_code_mode_requires_capability_api():
    class _AgentWithoutCapabilities:
        def __init__(self, model, **kwargs):  # noqa: ARG002
            pass

    with pytest.raises(ImportError, match="does not expose capabilities"):
        _build_agent_capability_kwargs(
            model_config={"pydantic_code_mode": True},
            agent_cls=_AgentWithoutCapabilities,
        )


def test_deepagents_local_sandbox_backend_maps_files_and_shell(monkeypatch, tmp_path):
    _install_fake_deepagents_protocol(monkeypatch)
    (tmp_path / "input.txt").write_text("alpha\nneedle\n", encoding="utf-8")
    sandbox = LocalSandbox(
        tmp_path,
        policy=SandboxPolicy(allow_write=True, allow_shell=True),
    )

    backend = _create_deepagents_backend(sandbox)

    read_result = backend.read("/input.txt")
    assert read_result.file_data["content"].startswith("alpha")

    grep_result = backend.grep("needle", "/")
    assert grep_result.matches == [
        {"path": "/input.txt", "line": 2, "text": "needle"}
    ]

    write_result = backend.write("/created.txt", "created")
    assert write_result.path == "/created.txt"
    assert (tmp_path / "created.txt").read_text(encoding="utf-8") == "created"

    execute_result = backend.execute("cat created.txt")
    assert execute_result.output == "created"
    assert execute_result.exit_code == 0


@pytest.mark.asyncio
async def test_deepagents_backend_routes_to_create_deep_agent(monkeypatch, tmp_path):
    _install_fake_deepagents_protocol(monkeypatch)
    captured = {}

    class _FakeAgent:
        async def ainvoke(self, inputs, config=None):
            captured["inputs"] = inputs
            captured["config"] = config
            return {"messages": [SimpleNamespace(content="deep-result")]}

    def fake_create_deep_agent(**kwargs):
        captured["create"] = kwargs
        return _FakeAgent()

    fake_deepagents = ModuleType("deepagents")
    fake_deepagents.create_deep_agent = fake_create_deep_agent
    monkeypatch.setitem(sys.modules, "deepagents", fake_deepagents)

    tool = HarnessTool(
        name="lookup_customer",
        description="Lookup a customer",
        parameters={"type": "object", "properties": {}, "required": []},
        execute=lambda args: "ok",
    )
    sandbox = LocalSandbox(tmp_path, policy=SandboxPolicy(allow_shell=True))

    result = await DeepAgentsHarnessBackend().run(
        prompt="hello",
        system_prompt="system",
        agent_name="demo",
        sandbox=sandbox,
        model_config={"provider": "openai", "model": "gpt-4o"},
        tools=[tool],
    )

    assert result.text == "deep-result"
    assert result.metadata["framework"] == "deepagents"
    assert result.metadata["model"] == "openai:gpt-4o"
    assert captured["create"]["name"] == "demo"
    assert captured["create"]["system_prompt"] == "system"
    assert captured["create"]["backend"] is not None
    assert captured["create"]["skills"] is None
    assert captured["create"]["memory"] is None
    assert captured["create"]["checkpointer"] is None
    assert captured["create"]["debug"] is False
    assert captured["create"]["tools"][0].__name__ == "lookup_customer"
    assert captured["inputs"]["messages"][0]["content"] == "hello"
    assert captured["config"] == {"configurable": {"thread_id": "demo"}}


def test_deepagents_config_discovers_skills_memory_and_permissions(
    monkeypatch,
    tmp_path,
):
    (tmp_path / "AGENTS.md").write_text("project memory", encoding="utf-8")
    skill_dir = tmp_path / ".agents" / "skills"
    skill_dir.mkdir(parents=True)
    (skill_dir / "review.md").write_text("review skill", encoding="utf-8")

    class _FilesystemPermission:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_deepagents = ModuleType("deepagents")
    fake_deepagents.FilesystemPermission = _FilesystemPermission
    monkeypatch.setitem(sys.modules, "deepagents", fake_deepagents)

    config = _resolve_deepagents_config(
        model_config={
            "deepagents": {
                "checkpointer": "none",
                "debug": True,
                "thread_id": "session-1",
            }
        },
        spec_data=None,
        cwd=tmp_path,
        sandbox=LocalSandbox(tmp_path),
    )

    assert config["skills"] == ["/.agents/skills"]
    assert config["memory"] == ["/AGENTS.md"]
    assert config["permissions"][0].kwargs == {
        "operations": ["write"],
        "paths": ["/**"],
        "mode": "deny",
    }
    assert config["debug"] is True
    assert config["thread_id"] == "session-1"


def _install_fake_deepagents_protocol(monkeypatch):
    protocol = ModuleType("deepagents.backends.protocol")

    class _Result:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class SandboxBackendProtocol:
        pass

    protocol.EditResult = _Result
    protocol.ExecuteResponse = _Result
    protocol.FileDownloadResponse = _Result
    protocol.FileUploadResponse = _Result
    protocol.GlobResult = _Result
    protocol.GrepResult = _Result
    protocol.LsResult = _Result
    protocol.ReadResult = _Result
    protocol.SandboxBackendProtocol = SandboxBackendProtocol
    protocol.WriteResult = _Result

    backends = ModuleType("deepagents.backends")
    backends.protocol = protocol
    monkeypatch.setitem(sys.modules, "deepagents.backends", backends)
    monkeypatch.setitem(sys.modules, "deepagents.backends.protocol", protocol)
