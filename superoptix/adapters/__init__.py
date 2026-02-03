"""
Framework adapters for multi-framework support.

This module provides adapters that convert framework-specific agents into
framework-agnostic BaseComponent instances, enabling universal optimization
with GEPA and other DSPy optimizers.

StackOne Integration Features:
- StackOneBridge: Convert tools to DSPy, Pydantic AI, OpenAI, LangChain, Google ADK, Semantic Kernel
- StackOneToolSetWrapper: MCP-backed dynamic tool discovery with glob filtering
- StackOneFeedbackTool: Collect user feedback on tool performance
- ImplicitFeedbackManager: LangSmith integration for behavioral feedback
- ToolIndex: Hybrid BM25 + TF-IDF search for tool discovery
- FileUploadHandler: Automatic file upload handling
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
from .stackone_adapter import (
    StackOneBridge,
    StackOneToolSetWrapper,
    StackOneFeedbackTool,
    StackOneOptimizableComponent,
    ImplicitFeedbackManager,
    ToolIndex,
    ToolSearchResult,
    FileUploadHandler,
    FeedbackInput,
    configure_implicit_feedback,
)

__all__ = [
    # Framework adapters
    "FrameworkRegistry",
    "FrameworkAdapter",
    "DSPyFrameworkAdapter",
    "MicrosoftFrameworkAdapter",
    "OpenAIFrameworkAdapter",
    "DeepAgentsFrameworkAdapter",
    "CrewAIFrameworkAdapter",
    "GoogleADKFrameworkAdapter",
    # StackOne integration
    "StackOneBridge",
    "StackOneToolSetWrapper",
    "StackOneFeedbackTool",
    "StackOneOptimizableComponent",
    "ImplicitFeedbackManager",
    "ToolIndex",
    "ToolSearchResult",
    "FileUploadHandler",
    "FeedbackInput",
    "configure_implicit_feedback",
]
