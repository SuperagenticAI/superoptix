"""SuperOptiX Observability and Monitoring Module.

Provides comprehensive observability with:
- Base tracer (MLFlow, LangFuse)
- Enhanced tracer (W&B, agent-specific metrics)
- Cost tracking
- Protocol usage monitoring
- Multi-framework comparison
"""

from .callbacks import SuperOptixCallback
from .debugger import InteractiveDebugger
from .tracer import SuperOptixTracer, TraceEvent

# Enhanced tracer with agent-specific metrics
try:
    from .enhanced_tracer import (
        EnhancedSuperOptixTracer,
        AgentMetrics,
        GEPAOptimizationMetrics,
        ProtocolUsageMetrics,
    )

    ENHANCED_TRACER_AVAILABLE = True
except ImportError:
    ENHANCED_TRACER_AVAILABLE = False

# Optional imports that require additional dependencies
try:
    from .dashboard import MultiAgentObservabilityDashboard, ObservabilityDashboard
except ImportError:
    ObservabilityDashboard = None
    MultiAgentObservabilityDashboard = None

from .enhanced_adapter import ObservabilityEnhancedDSPyAdapter

__all__ = [
    "SuperOptixTracer",
    "TraceEvent",
    "SuperOptixCallback",
    "InteractiveDebugger",
    "ObservabilityEnhancedDSPyAdapter",
]

# Add enhanced tracer if available
if ENHANCED_TRACER_AVAILABLE:
    __all__.extend(
        [
            "EnhancedSuperOptixTracer",
            "AgentMetrics",
            "GEPAOptimizationMetrics",
            "ProtocolUsageMetrics",
        ]
    )

# Add to __all__ only if successfully imported
if ObservabilityDashboard is not None:
    __all__.append("ObservabilityDashboard")

if MultiAgentObservabilityDashboard is not None:
    __all__.append("MultiAgentObservabilityDashboard")
