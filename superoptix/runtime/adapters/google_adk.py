"""Google ADK-specific runtime adapter."""

from __future__ import annotations

from typing import Any, Dict

from superoptix.runtime.adapters.pipeline import CompiledPipelineRuntimeAdapter
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry


class GoogleADKRuntimeAdapter(CompiledPipelineRuntimeAdapter):
    """Runtime adapter for Google ADK pipelines."""

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        payload = await super().invoke(inputs, context=context)
        payload.setdefault("framework", "google_adk")
        return payload

    async def metadata(self) -> Dict[str, Any]:
        payload = await super().metadata()
        payload.setdefault("metadata", {})
        payload["metadata"].setdefault("framework", "google-adk")
        return payload

    async def capabilities(self) -> Dict[str, Any]:
        caps = await super().capabilities()
        caps["framework"] = "google-adk"
        return caps


runtime_registry.register("google_adk", GoogleADKRuntimeAdapter)
