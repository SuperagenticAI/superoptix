"""A2A (Agent2Agent) protocol support for SuperOptiX."""

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.client import A2AClient
from superoptix.protocols.a2a.server import create_a2a_fastapi_app
from superoptix.runtime import AgentRuntime
from superoptix.runtime.adapters import CompiledPipelineRuntimeAdapter

__all__ = [
    "A2AClient",
    "AgentRuntime",
    "CompiledPipelineRuntimeAdapter",
    "build_a2a_agent_card_payload",
    "create_a2a_fastapi_app",
]
