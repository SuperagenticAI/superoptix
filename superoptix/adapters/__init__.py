"""
Framework adapters for multi-framework support.

This module provides adapters that convert framework-specific agents into
framework-agnostic BaseComponent instances, enabling universal optimization
with GEPA and other DSPy optimizers.
"""

from .framework_registry import (
    CrewAIFrameworkAdapter,
    DeepAgentsFrameworkAdapter,
    DSPyFrameworkAdapter,
    FrameworkAdapter,
    FrameworkRegistry,
    GoogleADKFrameworkAdapter,
    MicrosoftFrameworkAdapter,
    OpenAIFrameworkAdapter,
)
from .stackone_adapter import StackOneBridge

__all__ = [
    "FrameworkRegistry",
    "FrameworkAdapter",
    "DSPyFrameworkAdapter",
    "MicrosoftFrameworkAdapter",
    "OpenAIFrameworkAdapter",
    "DeepAgentsFrameworkAdapter",
    "CrewAIFrameworkAdapter",
    "GoogleADKFrameworkAdapter",
    "StackOneBridge",
]
