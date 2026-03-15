"""Generic runtime adapter for compiled SuperOptiX pipelines."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
import inspect
from typing import Any, Dict

from superoptix.runtime.base import AgentRuntime, RuntimeContext, ensure_runtime_context
from superoptix.runtime.registry import runtime_registry


def _normalize_runtime_result(result: Any) -> Dict[str, Any]:
    """Coerce framework results into a dict payload."""
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        return {"response": result}
    if hasattr(result, "toDict") and callable(result.toDict):
        try:
            payload = result.toDict()
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    if hasattr(result, "model_dump") and callable(result.model_dump):
        try:
            payload = result.model_dump()
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    if hasattr(result, "response"):
        return {"response": getattr(result, "response")}
    return {"response": str(result)}


def _context_kwargs(context: RuntimeContext | None) -> Dict[str, Any]:
    if context is None:
        return {}
    payload = {
        "context": context,
        "runtime_context": context,
        "task_id": context.task_id,
        "context_id": context.context_id,
    }
    return {k: v for k, v in payload.items() if v is not None}


def _call_with_supported_kwargs(
    func: Any,
    /,
    **kwargs: Any,
) -> Any:
    """Call a function while filtering kwargs to what it accepts."""
    signature = inspect.signature(func)
    parameters = signature.parameters.values()
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters):
        return func(**kwargs)

    accepted = {
        name: value for name, value in kwargs.items() if name in signature.parameters
    }
    return func(**accepted)


class CompiledPipelineRuntimeAdapter(AgentRuntime):
    """Wrap a compiled SuperOptiX pipeline behind the AgentRuntime contract."""

    def __init__(self, pipeline: Any):
        self.pipeline = pipeline

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        if not hasattr(self.pipeline, "run"):
            raise AttributeError("Pipeline does not expose a run() method")

        runtime_context = ensure_runtime_context(context)
        result = _call_with_supported_kwargs(
            self.pipeline.run,
            **inputs,
            **_context_kwargs(runtime_context),
        )
        if inspect.isawaitable(result):
            result = await result

        return _normalize_runtime_result(result)

    async def stream(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> AsyncIterator[Dict[str, Any]]:
        if not hasattr(self.pipeline, "stream"):
            result = await self.invoke(inputs, context=context)
            yield result
            return

        runtime_context = ensure_runtime_context(context)
        stream_result = _call_with_supported_kwargs(
            self.pipeline.stream,
            **inputs,
            **_context_kwargs(runtime_context),
        )

        if inspect.isawaitable(stream_result):
            stream_result = await stream_result

        if hasattr(stream_result, "__aiter__"):
            async for chunk in stream_result:
                yield _normalize_runtime_result(chunk)
            return

        if isinstance(stream_result, Iterator):
            for chunk in stream_result:
                yield _normalize_runtime_result(chunk)
            return

        yield _normalize_runtime_result(stream_result)

    async def cancel(
        self,
        task_id: str,
        context: RuntimeContext | None = None,
    ) -> bool:
        if not hasattr(self.pipeline, "cancel"):
            return False

        runtime_context = ensure_runtime_context(context)
        result = _call_with_supported_kwargs(
            self.pipeline.cancel,
            task_id=task_id,
            **_context_kwargs(runtime_context),
        )
        if inspect.isawaitable(result):
            result = await result
        return bool(result if result is not None else True)

    async def metadata(self) -> Dict[str, Any]:
        metadata = getattr(self.pipeline, "metadata", {}) or {}
        spec = getattr(self.pipeline, "spec", {}) or {}
        return {
            "metadata": dict(metadata) if isinstance(metadata, dict) else {},
            "spec": dict(spec) if isinstance(spec, dict) else {},
        }

    async def capabilities(self) -> Dict[str, Any]:
        return {
            "streaming": hasattr(self.pipeline, "stream"),
            "cancel": hasattr(self.pipeline, "cancel"),
            "task_context": True,
        }


runtime_registry.register("compiled_pipeline", CompiledPipelineRuntimeAdapter)
