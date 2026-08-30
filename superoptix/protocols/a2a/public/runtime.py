"""AgentRuntime that serves the public SuperOptiX catalogue skills.

Implements the same ``AgentRuntime`` protocol as the compiled-pipeline adapter,
so the existing A2A server serves it with no special casing.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from superoptix.protocols.a2a.public.skills import (
    PUBLIC_SKILL_DEFINITIONS,
    agent_card_review,
    framework_a2a_readiness,
)
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry

_CARD_HINTS = ("agent card", "agent-card", "card review", "review my card", '"skills"')


def _route(query: str) -> str:
    """Pick a skill for a free-text A2A message."""
    text = (query or "").lower()
    if "{" in text and "}" in text:
        return "agent-card-review"
    if any(hint in text for hint in _CARD_HINTS):
        return "agent-card-review"
    return "framework-a2a-readiness"


class PublicCatalogueRuntime:
    """Serve the deterministic public skills over A2A."""

    def __init__(self, target: Any = None):
        # `target` is unused: this runtime has no underlying pipeline. The
        # parameter exists so the runtime registry can construct it uniformly.
        self._target = target

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        query = str(inputs.get("query") or inputs.get("input") or "").strip()
        skill = str(inputs.get("skill") or "").strip() or _route(query)
        if skill == "agent-card-review":
            result = agent_card_review(query)
        else:
            result = framework_a2a_readiness(query)
        result.setdefault("skill", skill)
        return result

    async def stream(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> AsyncIterator[Dict[str, Any]]:
        yield await self.invoke(inputs, context=context)

    async def cancel(self, task_id: str, context: RuntimeContext | None = None) -> bool:
        # Skills are synchronous and complete within a single turn.
        return False

    async def metadata(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "name": "SuperOptiX",
                "description": (
                    "The A2A interoperability layer for agent frameworks. "
                    "Reports A2A readiness for major agent frameworks and reviews "
                    "Agent Cards for conformance and discoverability"
                ),
                "version": "1.0",
            },
            "spec": {"tasks": []},
            "skills": PUBLIC_SKILL_DEFINITIONS,
        }

    async def capabilities(self) -> Dict[str, Any]:
        return {"streaming": True, "cancel": False, "task_context": True}


runtime_registry.register("superoptix_public", PublicCatalogueRuntime)
