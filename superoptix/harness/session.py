"""Stateful SuperOptiX harness sessions."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from superoptix.harness.backends.codex import CodexHarnessBackend
from superoptix.harness.backends.deepagents import DeepAgentsHarnessBackend
from superoptix.harness.backends.google_adk import GoogleADKHarnessBackend
from superoptix.harness.backends.openai import OpenAIHarnessBackend
from superoptix.harness.backends.pydantic_ai import PydanticAIHarnessBackend
from superoptix.harness.context import discover_context
from superoptix.harness.sandbox import LocalSandbox, SandboxPolicy
from superoptix.harness.store import InMemorySessionStore, SessionState, SessionStore
from superoptix.harness.tools import HarnessTool, create_builtin_tools
from superoptix.harness.types import HarnessBackend, HarnessContext, HarnessRunResult


HEADLESS_PREAMBLE = (
    "You are running in a headless agent harness. Work autonomously, make "
    "reasonable assumptions, and return the final answer directly."
)

_RESULT_RE = re.compile(
    r"---RESULT_START---\s*\n(?P<body>[\s\S]*?)---RESULT_END---",
    re.MULTILINE,
)


class HarnessAgent:
    """Agent factory for stateful harness sessions."""

    def __init__(
        self,
        *,
        name: str,
        cwd: str | Path | None = None,
        backend: str | HarnessBackend = "openai",
        model: str | None = None,
        model_config: dict[str, Any] | None = None,
        spec_data: dict[str, Any] | None = None,
        context: HarnessContext | None = None,
        store: SessionStore | None = None,
        sandbox: LocalSandbox | None = None,
        tools: list[HarnessTool] | None = None,
        enable_tools: bool = True,
        allow_write: bool = False,
        allow_shell: bool = False,
    ):
        self.name = name
        self.cwd = Path(cwd or Path.cwd()).expanduser().resolve()
        self.context = context or discover_context(self.cwd)
        self.backend = resolve_backend(backend)
        self.model = model
        self.model_config = dict(model_config or {})
        self.spec_data = dict(spec_data or {})
        self.store = store or InMemorySessionStore()
        self.sandbox = sandbox or LocalSandbox(
            self.cwd,
            policy=SandboxPolicy(allow_write=allow_write, allow_shell=allow_shell),
        )
        self.tools = list(tools or [])
        if enable_tools:
            self.tools = [*create_builtin_tools(self.sandbox), *self.tools]

    async def session(
        self,
        session_id: str = "default",
        *,
        role: str | None = None,
    ) -> "HarnessSession":
        state = await self.store.load(session_id)
        if state is None:
            state = SessionState(session_id=session_id)
            await self.store.save(state)
        return HarnessSession(agent=self, state=state, role=role)


class HarnessSession:
    """One stateful conversation with a harness agent."""

    def __init__(
        self,
        *,
        agent: HarnessAgent,
        state: SessionState,
        role: str | None = None,
    ):
        self.agent = agent
        self.state = state
        self.role = role

    async def prompt(
        self,
        text: str,
        *,
        result_type: Any | None = None,
        role: str | None = None,
    ) -> HarnessRunResult | Any:
        """Run one prompt turn."""
        prompt_text = self._build_prompt(text, result_type=result_type)
        system_prompt = self._build_system_prompt(role=role)
        full_prompt = self._with_history(prompt_text)

        self.state.append("user", text, kind="prompt")
        result = await self.agent.backend.run(
            prompt=full_prompt,
            system_prompt=system_prompt,
            agent_name=self.agent.name,
            cwd=self.agent.cwd,
            sandbox=self.agent.sandbox,
            model=self._resolve_model(role=role),
            model_config=self.agent.model_config,
            spec_data=self.agent.spec_data,
            tools=self.agent.tools,
        )
        self.state.append(
            "assistant",
            result.text,
            kind="prompt",
            framework=result.metadata.get("framework"),
        )
        await self.agent.store.save(self.state)

        if result_type is not None:
            return parse_structured_result(result.text, result_type)
        return result

    async def skill(
        self,
        name: str,
        *,
        args: dict[str, Any] | None = None,
        result_type: Any | None = None,
        role: str | None = None,
    ) -> HarnessRunResult | Any:
        """Run a discovered Markdown skill."""
        skill = self.agent.context.skills.get(name)
        if skill is None:
            available = ", ".join(sorted(self.agent.context.skills)) or "(none)"
            raise KeyError(f"Skill '{name}' not found. Available skills: {available}")

        parts = [skill.instructions.strip()]
        if args:
            parts.append("Arguments:\n" + json.dumps(args, indent=2, sort_keys=True))
        return await self.prompt(
            "\n\n".join(part for part in parts if part),
            result_type=result_type,
            role=role,
        )

    async def task(
        self,
        text: str,
        *,
        role: str | None = None,
        result_type: Any | None = None,
    ) -> HarnessRunResult | Any:
        """Run a child session with independent conversation history."""
        task_id = f"task:{self.state.session_id}:{uuid.uuid4().hex[:12]}"
        child = await self.agent.session(task_id, role=role or self.role)
        result = await child.prompt(text, result_type=result_type, role=role)
        self.state.append(
            "assistant",
            result.text if isinstance(result, HarnessRunResult) else str(result),
            kind="task",
            task_session_id=task_id,
        )
        await self.agent.store.save(self.state)
        return result

    async def shell(
        self,
        command: str,
        *,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Run a local shell command from the agent working directory."""
        result = await asyncio.to_thread(
            self.agent.sandbox.bash,
            command,
            timeout=timeout,
        )
        self.state.append(
            "tool",
            json.dumps(result, sort_keys=True),
            kind="shell",
            command=command,
        )
        await self.agent.store.save(self.state)
        return result

    def _build_system_prompt(self, *, role: str | None = None) -> str:
        role_name = role or self.role
        parts = [self.agent.context.system_prompt]
        if role_name:
            selected = self.agent.context.roles.get(role_name)
            if selected is None:
                available = ", ".join(sorted(self.agent.context.roles)) or "(none)"
                raise KeyError(
                    f"Role '{role_name}' not found. Available roles: {available}"
                )
            parts.append(f"<role name=\"{selected.name}\">\n{selected.instructions}\n</role>")
        return "\n\n".join(part for part in parts if part).strip()

    def _resolve_model(self, *, role: str | None = None) -> str | None:
        role_name = role or self.role
        if role_name and role_name in self.agent.context.roles:
            return self.agent.context.roles[role_name].model or self.agent.model
        return self.agent.model

    def _build_prompt(self, text: str, *, result_type: Any | None = None) -> str:
        parts = [HEADLESS_PREAMBLE, "", text.strip()]
        if result_type is not None:
            parts.extend(
                [
                    "",
                    "When complete, output the final result between these exact "
                    "delimiters:",
                    "---RESULT_START---",
                    "<result>",
                    "---RESULT_END---",
                ]
            )
        return "\n".join(parts).strip()

    def _with_history(self, text: str) -> str:
        if not self.state.messages:
            return text
        history: list[str] = []
        for message in self.state.messages[-12:]:
            if message.role in {"user", "assistant"} and message.content:
                history.append(f"{message.role}: {message.content}")
        if not history:
            return text
        return "Conversation so far:\n" + "\n\n".join(history) + "\n\nNext:\n" + text


def resolve_backend(backend: str | HarnessBackend) -> HarnessBackend:
    """Resolve a backend name to an implementation."""
    if not isinstance(backend, str):
        return backend

    key = backend.strip().lower().replace("-", "_")
    if key in {"openai", "openai_agents"}:
        return OpenAIHarnessBackend()
    if key in {"google", "google_adk", "adk"}:
        return GoogleADKHarnessBackend()
    if key in {"codex", "codex_cli"}:
        return CodexHarnessBackend()
    if key in {"deepagents", "deep_agents", "langchain_deepagents"}:
        return DeepAgentsHarnessBackend()
    if key in {"pydantic_ai", "pydanticai"}:
        return PydanticAIHarnessBackend()
    raise ValueError(
        "Harness backend must be one of: openai, google-adk, codex, deepagents, pydantic-ai"
    )


def parse_structured_result(text: str, result_type: Any) -> Any:
    """Extract and validate a delimited structured result."""
    matches = list(_RESULT_RE.finditer(text or ""))
    if not matches:
        raise ValueError("No ---RESULT_START--- / ---RESULT_END--- block found.")

    raw = matches[-1].group("body").strip()
    value: Any = raw
    if raw.startswith("{") or raw.startswith("["):
        value = json.loads(raw)

    return TypeAdapter(result_type).validate_python(value)
