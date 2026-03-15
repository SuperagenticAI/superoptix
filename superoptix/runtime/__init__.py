"""Framework-neutral runtime subsystem for SuperOptiX."""

from superoptix.runtime.adapters import (
    CompiledPipelineRuntimeAdapter,
    CrewAIRuntimeAdapter,
    DSPyRuntimeAdapter,
    GoogleADKRuntimeAdapter,
    PydanticAIRuntimeAdapter,
)
from superoptix.runtime.base import AgentRuntime, RuntimeContext, ensure_runtime_context
from superoptix.runtime.registry import RuntimeRegistry, runtime_registry

__all__ = [
    "AgentRuntime",
    "RuntimeContext",
    "CompiledPipelineRuntimeAdapter",
    "CrewAIRuntimeAdapter",
    "DSPyRuntimeAdapter",
    "GoogleADKRuntimeAdapter",
    "PydanticAIRuntimeAdapter",
    "RuntimeRegistry",
    "ensure_runtime_context",
    "runtime_registry",
]
