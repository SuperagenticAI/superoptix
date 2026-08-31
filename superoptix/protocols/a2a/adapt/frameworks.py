"""Introspectors for the remaining six frameworks.

Each is small because the IR and every emitter are shared: a framework needs one
reader in, and gets the Agent Card, the server and the routing metric for free.
That is the payoff of treating SuperSpec as an intermediate representation
rather than something a person writes.

Object shapes here were read from the installed packages, not inferred:

- **OpenAI Agents SDK** — ``Agent`` with ``name`` / ``instructions`` /
  ``handoff_description`` / ``tools``; each tool carries ``name`` and
  ``description``.
- **Pydantic AI** — ``Agent`` with ``name``, ``_instructions`` (a list) and a
  ``_function_toolset.tools`` mapping.
- **Google ADK** — ``Agent`` with ``name`` / ``description`` / ``instruction`` /
  ``tools`` / ``sub_agents``.
- **Microsoft Agent Framework** — ``Agent`` with ``name`` / ``description`` /
  ``instructions`` / ``tools``.
- **Claude Agent SDK** — ``AgentDefinition`` (``description`` / ``prompt`` /
  ``tools``) or ``ClaudeAgentOptions`` (``system_prompt`` / ``allowed_tools``).
- **DeepAgents** — a compiled LangGraph, so subagents are the readable surface;
  each has ``name`` / ``description`` / ``system_prompt``.
"""

from __future__ import annotations

from typing import Any, Dict, List

from superoptix.protocols.a2a.adapt.base import (
    AdaptError,
    AgentSpec,
    Skill,
    first_sentence,
    register,
    slugify,
)


def _text(obj: Any, *names: str) -> str:
    """First non-empty string among the named attributes or mapping keys."""
    for name in names:
        value = getattr(obj, name, None)
        if value is None and isinstance(obj, dict):
            value = obj.get(name)
        if isinstance(value, (list, tuple)):
            value = " ".join(str(v) for v in value if isinstance(v, str))
        if callable(value):
            continue
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _tool_skills(tools: Any, *, framework: str) -> List[Skill]:
    """A tool is a named capability, which is exactly what a skill is."""
    skills: List[Skill] = []
    items = tools.values() if isinstance(tools, dict) else (tools or [])
    for index, tool in enumerate(items):
        name = _text(tool, "name", "__name__") or f"tool-{index + 1}"
        description = _text(tool, "description", "__doc__")
        if not description:
            continue
        skills.append(
            Skill(
                id=slugify(name, f"tool-{index + 1}"),
                name=name,
                description=first_sentence(description),
                tags=[framework, "tool"],
                output_modes=["text/plain", "application/json"],
            )
        )
    return skills


def _agent_skill(
    *, name: str, instructions: str, framework: str, fallback_id: str
) -> Skill:
    return Skill(
        id=slugify(name, fallback_id),
        name=name,
        description=first_sentence(instructions or f"Act as {name}"),
        tags=[framework, "agent"],
        output_modes=["text/plain", "application/json"],
    )


class _AttrIntrospector:
    """Shared implementation for frameworks that expose a flat agent object."""

    framework = ""
    class_names: tuple[str, ...] = ()
    name_attrs: tuple[str, ...] = ("name",)
    instruction_attrs: tuple[str, ...] = ("instructions",)
    description_attrs: tuple[str, ...] = ("description",)
    tools_attr = "tools"

    def matches(self, obj: Any) -> bool:
        return type(obj).__name__ in self.class_names

    def _tools(self, obj: Any) -> Any:
        return getattr(obj, self.tools_attr, None)

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        if not self.matches(obj):
            raise AdaptError(
                f"{entrypoint} resolved to {type(obj).__name__}, which is not a "
                f"{self.framework} agent."
            )
        fallback = entrypoint.split(":")[-1].split(".")[-1]
        name = _text(obj, *self.name_attrs) or fallback
        instructions = _text(obj, *self.instruction_attrs)
        description = _text(obj, *self.description_attrs) or instructions

        skills = _tool_skills(self._tools(obj), framework=self.framework)
        if not skills:
            skills = [
                _agent_skill(
                    name=name,
                    instructions=description or instructions,
                    framework=self.framework,
                    fallback_id=fallback,
                )
            ]

        return AgentSpec(
            name=name,
            description=first_sentence(description or f"{self.framework} agent {name}"),
            framework=self.framework,
            entrypoint=entrypoint,
            skills=skills,
            metadata={"toolCount": len(skills)},
        )


class OpenAIAgentsIntrospector(_AttrIntrospector):
    framework = "openai"
    class_names = ("Agent",)
    instruction_attrs = ("instructions",)
    description_attrs = ("handoff_description", "instructions")

    def matches(self, obj: Any) -> bool:
        # Three frameworks call their class `Agent`. CrewAI has `role`;
        # Pydantic AI has `_function_toolset` and exposes `instructions` as a
        # method. `handoffs` belongs to the OpenAI SDK alone.
        return (
            type(obj).__name__ == "Agent"
            and hasattr(obj, "handoffs")
            and hasattr(obj, "instructions")
            and not hasattr(obj, "role")
        )


class PydanticAIIntrospector(_AttrIntrospector):
    framework = "pydantic-ai"
    class_names = ("Agent", "AgentRunner")
    instruction_attrs = ("_instructions", "_system_prompts")
    description_attrs = ("_instructions", "_system_prompts")

    def matches(self, obj: Any) -> bool:
        return type(obj).__name__ == "Agent" and hasattr(obj, "_function_toolset")

    def _tools(self, obj: Any) -> Any:
        toolset = getattr(obj, "_function_toolset", None)
        return getattr(toolset, "tools", None) if toolset is not None else None


class GoogleADKIntrospector(_AttrIntrospector):
    framework = "google-adk"
    class_names = ("Agent", "LlmAgent", "SequentialAgent", "ParallelAgent")
    instruction_attrs = ("instruction",)
    description_attrs = ("description", "instruction")

    def matches(self, obj: Any) -> bool:
        return type(obj).__name__ in self.class_names and hasattr(obj, "instruction")

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        spec = super().introspect(obj, entrypoint=entrypoint)
        # Sub-agents are routable capabilities in their own right.
        for index, sub in enumerate(getattr(obj, "sub_agents", None) or []):
            name = _text(sub, "name") or f"sub-agent-{index + 1}"
            description = _text(sub, "description", "instruction")
            if description:
                spec.skills.append(
                    Skill(
                        id=slugify(name, f"sub-agent-{index + 1}"),
                        name=name,
                        description=first_sentence(description),
                        tags=[self.framework, "sub-agent"],
                        output_modes=["text/plain", "application/json"],
                    )
                )
        return spec


class MicrosoftIntrospector(_AttrIntrospector):
    framework = "microsoft"
    class_names = ("Agent", "ChatAgent", "BaseAgent")
    instruction_attrs = ("instructions",)
    description_attrs = ("description", "instructions")

    def matches(self, obj: Any) -> bool:
        return (
            type(obj).__name__ in self.class_names
            and hasattr(obj, "description")
            and hasattr(obj, "instructions")
            and hasattr(obj, "id")
        )


class ClaudeSDKIntrospector:
    """Reads a Claude Agent SDK AgentDefinition or ClaudeAgentOptions."""

    framework = "claude-sdk"

    def matches(self, obj: Any) -> bool:
        return type(obj).__name__ in ("AgentDefinition", "ClaudeAgentOptions")

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        if not self.matches(obj):
            raise AdaptError(
                f"{entrypoint} resolved to {type(obj).__name__}, which is not a "
                "Claude Agent SDK AgentDefinition or ClaudeAgentOptions."
            )
        fallback = entrypoint.split(":")[-1].split(".")[-1]
        description = _text(obj, "description", "prompt", "system_prompt")
        if not description:
            raise AdaptError(
                f"{entrypoint} has no description, prompt or system_prompt to "
                "describe it to other agents."
            )

        skills = _tool_skills(getattr(obj, "tools", None), framework=self.framework)
        if not skills:
            named = [
                str(t) for t in (getattr(obj, "allowed_tools", None) or []) if str(t)
            ]
            skills = [
                Skill(
                    id=slugify(fallback, "claude-agent"),
                    name=fallback.replace("_", " ").title(),
                    description=first_sentence(description),
                    tags=[self.framework, "agent", *named[:5]],
                    output_modes=["text/plain", "application/json"],
                )
            ]

        return AgentSpec(
            name=fallback,
            description=first_sentence(description),
            framework=self.framework,
            entrypoint=entrypoint,
            skills=skills,
            metadata={"toolCount": len(skills)},
        )


class DeepAgentsIntrospector:
    """Reads a DeepAgents graph through its subagents.

    ``create_deep_agent`` returns a compiled LangGraph, so the graph itself has
    little to say about capability. The subagents do: each is named and
    described precisely so the parent can route to it.
    """

    framework = "deepagents"

    def matches(self, obj: Any) -> bool:
        name = type(obj).__name__
        return name in ("CompiledStateGraph", "CompiledGraph") or (
            hasattr(obj, "invoke") and hasattr(obj, "get_graph")
        )

    @staticmethod
    def _subagents(obj: Any) -> List[Any]:
        for attr in ("subagents", "_subagents", "sub_agents"):
            found = getattr(obj, attr, None)
            if found:
                return list(found)
        return []

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        fallback = entrypoint.split(":")[-1].split(".")[-1]
        skills: List[Skill] = []
        for index, sub in enumerate(self._subagents(obj)):
            source: Dict[str, Any] = sub if isinstance(sub, dict) else sub.__dict__
            name = str(source.get("name") or f"subagent-{index + 1}")
            description = str(
                source.get("description") or source.get("system_prompt") or ""
            ).strip()
            if not description:
                continue
            skills.append(
                Skill(
                    id=slugify(name, f"subagent-{index + 1}"),
                    name=name,
                    description=first_sentence(description),
                    tags=[self.framework, "subagent"],
                    output_modes=["text/plain", "application/json"],
                )
            )

        if not skills:
            raise AdaptError(
                f"{entrypoint} is a DeepAgents graph with no subagents carrying a "
                "description. Give its subagents descriptions, or adapt them "
                "individually — a graph alone tells a caller nothing about what "
                "it can do."
            )

        return AgentSpec(
            name=fallback,
            description=f"DeepAgents graph with {len(skills)} subagent(s): "
            + ", ".join(s.name for s in skills),
            framework=self.framework,
            entrypoint=entrypoint,
            skills=skills,
            metadata={"subagentCount": len(skills)},
        )


for _introspector in (
    OpenAIAgentsIntrospector(),
    PydanticAIIntrospector(),
    GoogleADKIntrospector(),
    MicrosoftIntrospector(),
    ClaudeSDKIntrospector(),
    DeepAgentsIntrospector(),
):
    register(_introspector)
