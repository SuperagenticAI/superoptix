"""Runtime adapters for compiled SuperOptiX agents."""

from superoptix.runtime.adapters.crewai import CrewAIRuntimeAdapter
from superoptix.runtime.adapters.dspy import DSPyRuntimeAdapter
from superoptix.runtime.adapters.google_adk import GoogleADKRuntimeAdapter
from superoptix.runtime.adapters.pipeline import CompiledPipelineRuntimeAdapter
from superoptix.runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter

__all__ = [
    "CompiledPipelineRuntimeAdapter",
    "CrewAIRuntimeAdapter",
    "DSPyRuntimeAdapter",
    "GoogleADKRuntimeAdapter",
    "PydanticAIRuntimeAdapter",
]
