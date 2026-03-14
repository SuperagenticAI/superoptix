"""Base runtime contract for framework-neutral agent execution."""

from __future__ import annotations

from typing import Any, Dict, Protocol


class AgentRuntime(Protocol):
    """Framework-neutral runtime contract used by protocol integrations."""

    async def invoke(
        self, inputs: Dict[str, Any], context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Invoke the underlying agent."""

    async def metadata(self) -> Dict[str, Any]:
        """Return metadata used for runtime inspection and card generation."""

    async def capabilities(self) -> Dict[str, Any]:
        """Return runtime capabilities such as streaming or cancellation support."""

