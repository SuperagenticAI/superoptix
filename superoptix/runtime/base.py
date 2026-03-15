"""Base runtime contract for framework-neutral agent execution."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Protocol


@dataclass
class RuntimeContext:
    """Structured context passed from protocols into runtimes."""

    task_id: str | None = None
    context_id: str | None = None
    protocol: str = "a2a"
    metadata: Dict[str, Any] = field(default_factory=dict)
    request: Any | None = None


def ensure_runtime_context(
    context: RuntimeContext | Mapping[str, Any] | None,
) -> RuntimeContext | None:
    """Normalize dict-style context into a RuntimeContext object."""
    if context is None:
        return None
    if isinstance(context, RuntimeContext):
        return context
    return RuntimeContext(
        task_id=context.get("task_id"),
        context_id=context.get("context_id"),
        protocol=str(context.get("protocol", "a2a")),
        metadata=dict(context.get("metadata", {}) or {}),
        request=context.get("request"),
    )


class AgentRuntime(Protocol):
    """Framework-neutral runtime contract used by protocol integrations."""

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        """Invoke the underlying agent."""

    async def stream(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Optionally stream incremental runtime results."""

    async def cancel(
        self,
        task_id: str,
        context: RuntimeContext | None = None,
    ) -> bool:
        """Optionally cancel an in-flight task."""

    async def metadata(self) -> Dict[str, Any]:
        """Return metadata used for runtime inspection and card generation."""

    async def capabilities(self) -> Dict[str, Any]:
        """Return runtime capabilities such as streaming or cancellation support."""
