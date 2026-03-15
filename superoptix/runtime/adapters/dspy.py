"""DSPy-specific runtime adapter."""

from __future__ import annotations

from typing import Any, Dict

from superoptix.runtime.adapters.pipeline import (
    CompiledPipelineRuntimeAdapter,
    _normalize_runtime_result,
)
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry


class DSPyRuntimeAdapter(CompiledPipelineRuntimeAdapter):
    """Runtime adapter for DSPy pipelines or minimal DSPy program modules."""

    def __init__(self, target: Any):
        super().__init__(target)
        self._program = None
        if not hasattr(target, "run") and hasattr(target, "build_program"):
            self._program = target.build_program()

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        if self._program is None:
            result = await super().invoke(inputs, context=context)
            result.setdefault("framework", "dspy")
            return result

        if callable(self._program):
            result = self._program(**inputs)
        elif hasattr(self._program, "forward") and callable(self._program.forward):
            result = self._program.forward(**inputs)
        else:
            raise TypeError("DSPy program is not callable")

        payload = _normalize_runtime_result(result)
        payload.setdefault("framework", "dspy")
        return payload

    async def metadata(self) -> Dict[str, Any]:
        if self._program is None:
            payload = await super().metadata()
        else:
            metadata = getattr(self.pipeline, "metadata", {}) or {}
            spec = getattr(self.pipeline, "spec", {}) or {}
            payload = {
                "metadata": metadata if isinstance(metadata, dict) else {},
                "spec": spec if isinstance(spec, dict) else {},
            }
        payload.setdefault("metadata", {})
        payload["metadata"].setdefault("framework", "dspy")
        return payload

    async def capabilities(self) -> Dict[str, Any]:
        caps = await super().capabilities()
        caps["framework"] = "dspy"
        if self._program is not None:
            caps["streaming"] = False
            caps["cancel"] = False
        return caps


runtime_registry.register("dspy", DSPyRuntimeAdapter)
