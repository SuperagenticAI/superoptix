"""Introspect a CrewAI Crew or Agent into the adapt IR.

Skills are derived from the crew's tasks where it has them, because a task is
the closest thing CrewAI has to a named capability a caller would invoke. A
bare Agent falls back to its role.
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


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    value = getattr(obj, name, default)
    return default if value is None else value


def _is_crew(obj: Any) -> bool:
    return type(obj).__name__ == "Crew" and hasattr(obj, "agents")


def _is_agent(obj: Any) -> bool:
    return type(obj).__name__ == "Agent" and hasattr(obj, "role")


def _task_skill(task: Any, index: int) -> Skill:
    raw_name = str(_attr(task, "name", "") or "").strip()
    description = str(_attr(task, "description", "") or "").strip()
    expected = str(_attr(task, "expected_output", "") or "").strip()

    label = raw_name or first_sentence(description, 60) or f"Task {index + 1}"
    text = description or label
    if expected:
        text = f"{text} Returns: {expected}"

    agent = _attr(task, "agent")
    tags = ["crewai", "task"]
    if agent is not None:
        role = str(_attr(agent, "role", "") or "").strip()
        if role:
            tags.append(slugify(role, "agent"))

    return Skill(
        id=slugify(raw_name or label, f"task-{index + 1}"),
        name=label,
        description=first_sentence(text),
        tags=tags,
        examples=[expected] if expected else [],
        output_modes=["text/plain", "application/json"],
    )


def _agent_skill(agent: Any, index: int = 0) -> Skill:
    role = str(_attr(agent, "role", "") or "").strip() or f"Agent {index + 1}"
    goal = str(_attr(agent, "goal", "") or "").strip()
    backstory = str(_attr(agent, "backstory", "") or "").strip()

    description = goal or backstory or f"Act as {role}"
    tools = _attr(agent, "tools", []) or []
    tags = ["crewai", "agent", slugify(role, "agent")]
    if tools:
        tags.append("tools")

    return Skill(
        id=slugify(role, f"agent-{index + 1}"),
        name=role,
        description=first_sentence(description),
        tags=tags,
        examples=[first_sentence(goal, 120)] if goal and goal != description else [],
        output_modes=["text/plain", "application/json"],
    )


class CrewAIIntrospector:
    """Reads CrewAI Crews and Agents."""

    framework = "crewai"

    def matches(self, obj: Any) -> bool:
        return _is_crew(obj) or _is_agent(obj)

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        if _is_crew(obj):
            return self._from_crew(obj, entrypoint)
        if _is_agent(obj):
            return self._from_agent(obj, entrypoint)
        raise AdaptError(
            f"{entrypoint} resolved to {type(obj).__name__}, which is not a "
            "CrewAI Crew or Agent."
        )

    def _from_crew(self, crew: Any, entrypoint: str) -> AgentSpec:
        tasks = list(_attr(crew, "tasks", []) or [])
        agents = list(_attr(crew, "agents", []) or [])

        skills: List[Skill] = [_task_skill(t, i) for i, t in enumerate(tasks)]
        if not skills:
            skills = [_agent_skill(a, i) for i, a in enumerate(agents)]
        if not skills:
            raise AdaptError(
                f"{entrypoint} is a Crew with no tasks or agents to describe."
            )

        name = str(_attr(crew, "name", "") or "").strip() or entrypoint.split(":")[-1]
        roles = [str(_attr(a, "role", "")).strip() for a in agents]
        roles = [r for r in roles if r]
        description = (
            f"CrewAI crew of {len(agents)} agent(s): {', '.join(roles)}."
            if roles
            else f"CrewAI crew exposing {len(skills)} capability(ies)."
        )

        metadata: Dict[str, Any] = {
            "agentCount": len(agents),
            "taskCount": len(tasks),
        }
        return AgentSpec(
            name=name,
            description=description,
            framework=self.framework,
            entrypoint=entrypoint,
            skills=skills,
            metadata=metadata,
        )

    def _from_agent(self, agent: Any, entrypoint: str) -> AgentSpec:
        skill = _agent_skill(agent)
        return AgentSpec(
            name=skill.name,
            description=skill.description,
            framework=self.framework,
            entrypoint=entrypoint,
            skills=[skill],
            metadata={"agentCount": 1, "taskCount": 0},
        )


register(CrewAIIntrospector())
