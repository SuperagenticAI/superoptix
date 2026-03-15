"""Pydantic AI-specific runtime adapter."""

from __future__ import annotations

from typing import Any, Dict

from superoptix.runtime.adapters.pipeline import CompiledPipelineRuntimeAdapter
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry


class PydanticAIRuntimeAdapter(CompiledPipelineRuntimeAdapter):
    """Runtime adapter for Pydantic AI pipelines."""

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        payload = await super().invoke(inputs, context=context)
        payload.setdefault("framework", "pydantic_ai")
        return payload

    async def metadata(self) -> Dict[str, Any]:
        payload = await super().metadata()
        payload.setdefault("metadata", {})
        payload["metadata"].setdefault("framework", "pydantic-ai")
        return payload

    async def capabilities(self) -> Dict[str, Any]:
        caps = await super().capabilities()
        caps["framework"] = "pydantic-ai"
        return caps


runtime_registry.register("pydantic_ai", PydanticAIRuntimeAdapter)
