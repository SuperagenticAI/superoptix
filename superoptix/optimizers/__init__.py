"""
SuperOptiX Optimizers Module.

This module provides optimization algorithms for SuperOptiX agents.

Key Optimizers:
- UniversalGEPA: Framework-agnostic GEPA optimizer for all frameworks
- MCP Adapter: GEPA adapter for optimizing MCP tool usage (vendored from GEPA PR #105)
- RAG Adapter: GEPA adapter for optimizing RAG pipelines (vendored from GEPA)
"""

from superoptix.optimizers.universal_gepa import (
    UniversalGEPA,
    UniversalGEPAResult,
    UniversalGEPAMetric,
    ScoreWithFeedback,
    BaseComponentAdapter,
)

# MCP Adapter - Vendored from GEPA PR #105
# https://github.com/gepa-ai/gepa/pull/105
try:
    from superoptix.optimizers.gepa_mcp_adapter import (
        MCPAdapter,
        MCPDataInst,
        MCPOutput,
        MCPTrajectory,
    )

    _MCP_ADAPTER_AVAILABLE = True
except ImportError:
    _MCP_ADAPTER_AVAILABLE = False
    MCPAdapter = None
    MCPDataInst = None
    MCPOutput = None
    MCPTrajectory = None

# RAG Adapter - Vendored from GEPA
# Provides RAG optimization with any vector store
try:
    from superoptix.optimizers.gepa_rag_adapter import (
        GenericRAGAdapter,
        RAGDataInst,
        RAGOutput,
        RAGTrajectory,
        RAGPipeline,
        VectorStoreInterface,
        ChromaVectorStore,
        WeaviateVectorStore,
        RAGEvaluationMetrics,
    )

    _RAG_ADAPTER_AVAILABLE = True
except ImportError:
    _RAG_ADAPTER_AVAILABLE = False
    GenericRAGAdapter = None
    RAGDataInst = None
    RAGOutput = None
    RAGTrajectory = None
    RAGPipeline = None
    VectorStoreInterface = None
    ChromaVectorStore = None
    WeaviateVectorStore = None
    RAGEvaluationMetrics = None

__all__ = [
    "UniversalGEPA",
    "UniversalGEPAResult",
    "UniversalGEPAMetric",
    "ScoreWithFeedback",
    "BaseComponentAdapter",
    # MCP Adapter (optional, requires 'mcp' package)
    "MCPAdapter",
    "MCPDataInst",
    "MCPOutput",
    "MCPTrajectory",
    # RAG Adapter (optional, requires vector store dependencies)
    "GenericRAGAdapter",
    "RAGDataInst",
    "RAGOutput",
    "RAGTrajectory",
    "RAGPipeline",
    "VectorStoreInterface",
    "ChromaVectorStore",
    "WeaviateVectorStore",
    "RAGEvaluationMetrics",
]
