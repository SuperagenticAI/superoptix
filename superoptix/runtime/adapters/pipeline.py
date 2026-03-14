"""Generic runtime adapter for compiled SuperOptiX pipelines."""

from __future__ import annotations

import inspect
from typing import Any, Dict

from superoptix.runtime.base import AgentRuntime
from superoptix.runtime.registry import runtime_registry


class CompiledPipelineRuntimeAdapter(AgentRuntime):
    """Wrap a compiled SuperOptiX pipeline behind the AgentRuntime contract."""

    def __init__(self, pipeline: Any):
        self.pipeline = pipeline

    async def invoke(
        self, inputs: Dict[str, Any], context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        del context  # Reserved for future session/task propagation.
        if not hasattr(self.pipeline, "run"):
            raise AttributeError("Pipeline does not expose a run() method")

        result = self.pipeline.run(**inputs)
        if inspect.isawaitable(result):
            result = await result

        if isinstance(result, dict):
            return result
        if isinstance(result, str):
            return {"response": result}
        return {"response": str(result)}

    async def metadata(self) -> Dict[str, Any]:
        metadata = getattr(self.pipeline, "metadata", {}) or {}
        spec = getattr(self.pipeline, "spec", {}) or {}
        return {
            "metadata": metadata if isinstance(metadata, dict) else {},
            "spec": spec if isinstance(spec, dict) else {},
        }

    async def capabilities(self) -> Dict[str, Any]:
        return {
            "streaming": hasattr(self.pipeline, "stream"),
            "cancel": hasattr(self.pipeline, "cancel"),
        }


runtime_registry.register("compiled_pipeline", CompiledPipelineRuntimeAdapter)
