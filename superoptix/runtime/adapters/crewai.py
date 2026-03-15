"""CrewAI-specific runtime adapter."""

from __future__ import annotations

from typing import Any, Dict

from superoptix.runtime.adapters.pipeline import CompiledPipelineRuntimeAdapter
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry


class CrewAIRuntimeAdapter(CompiledPipelineRuntimeAdapter):
    """Runtime adapter for CrewAI pipelines."""

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        payload = await super().invoke(inputs, context=context)
        payload.setdefault("framework", "crewai")
        return payload

    async def metadata(self) -> Dict[str, Any]:
        payload = await super().metadata()
        payload.setdefault("metadata", {})
        payload["metadata"].setdefault("framework", "crewai")
        return payload

    async def capabilities(self) -> Dict[str, Any]:
        caps = await super().capabilities()
        caps["framework"] = "crewai"
        return caps


runtime_registry.register("crewai", CrewAIRuntimeAdapter)
