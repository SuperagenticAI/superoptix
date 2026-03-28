"""Lean SurrealDB coverage checks for SuperOptiX framework parity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEMO_DIR = Path("superoptix/agents/demo")

# Lean scope: keep one canonical SurrealDB playbook per major framework.
FRAMEWORK_PLAYBOOKS: dict[str, str] = {
    "dspy": "rag_surrealdb_dspy_demo_playbook.yaml",
    "openai": "rag_surrealdb_openai_demo_playbook.yaml",
    "claude-sdk": "rag_surrealdb_claude_sdk_demo_playbook.yaml",
    "microsoft": "rag_surrealdb_microsoft_demo_playbook.yaml",
    "pydantic-ai": "rag_surrealdb_pydanticai_demo_playbook.yaml",
    "crewai": "rag_surrealdb_crewai_demo_playbook.yaml",
    "google-adk": "rag_surrealdb_adk_demo_playbook.yaml",
    "deepagents": "rag_surrealdb_deepagents_demo_playbook.yaml",
}

GRAPH_FRAMEWORK_PLAYBOOKS: dict[str, str] = {
    "dspy": "graphrag_surrealdb_dspy_demo_playbook.yaml",
    "openai": "graphrag_surrealdb_openai_demo_playbook.yaml",
    "claude-sdk": "graphrag_surrealdb_claude_sdk_demo_playbook.yaml",
    "microsoft": "graphrag_surrealdb_microsoft_demo_playbook.yaml",
    "pydantic-ai": "graphrag_surrealdb_pydanticai_demo_playbook.yaml",
    "crewai": "graphrag_surrealdb_crewai_demo_playbook.yaml",
    "google-adk": "graphrag_surrealdb_adk_demo_playbook.yaml",
    "deepagents": "graphrag_surrealdb_deepagents_demo_playbook.yaml",
}


def _load_playbook(filename: str) -> dict[str, Any]:
    path = DEMO_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def test_surrealdb_framework_playbook_matrix_exists():
    """All canonical framework playbooks for SurrealDB must exist."""
    for framework, filename in FRAMEWORK_PLAYBOOKS.items():
        path = DEMO_DIR / filename
        assert path.exists(), f"Missing SurrealDB playbook for {framework}: {path}"


def test_surrealdb_graphrag_framework_playbook_matrix_exists():
    """All framework GraphRAG playbooks for SurrealDB must exist."""
    for framework, filename in GRAPH_FRAMEWORK_PLAYBOOKS.items():
        path = DEMO_DIR / filename
        assert path.exists(), f"Missing GraphRAG SurrealDB playbook for {framework}: {path}"


def test_surrealdb_framework_playbooks_are_wired_for_rag():
    """Canonical playbooks must use the supported SurrealDB RAG retriever path."""
    for framework, filename in FRAMEWORK_PLAYBOOKS.items():
        playbook = _load_playbook(filename)
        spec = playbook.get("spec", {})

        rag = spec.get("rag", {})
        assert rag.get("enabled") is True, f"{framework}: rag.enabled should be true"
        assert (
            str(rag.get("retriever_type", "")).strip().lower()
            in {"surrealdb", "turboagents-surrealdb"}
        ), f"{framework}: rag.retriever_type must be surrealdb or turboagents-surrealdb"

        config = rag.get("config", {})
        assert isinstance(config.get("top_k", 0), int) and config.get("top_k", 0) > 0

        vector_store = rag.get("vector_store", {})
        for key in ("url", "namespace", "database", "table_name", "vector_field", "content_field"):
            assert key in vector_store, f"{framework}: rag.vector_store missing '{key}'"


def test_surrealdb_graphrag_framework_playbooks_use_graph_mode():
    """GraphRAG playbooks must keep explicit graph retrieval mode."""
    for framework, filename in GRAPH_FRAMEWORK_PLAYBOOKS.items():
        playbook = _load_playbook(filename)
        graph_cfg = playbook.get("spec", {}).get("rag", {}).get("config", {})
        assert (
            str(graph_cfg.get("retrieval_mode", "")).strip().lower() == "graph"
        ), f"{framework}: expected rag.config.retrieval_mode=graph"


def test_surrealdb_advanced_playbooks_keep_expected_mode_boundaries():
    """Graph and temporal demos keep explicit advanced-mode configuration."""
    graph_openai = _load_playbook("graphrag_surrealdb_openai_demo_playbook.yaml")
    graph_cfg = graph_openai.get("spec", {}).get("rag", {}).get("config", {})
    assert str(graph_cfg.get("retrieval_mode", "")).strip().lower() == "graph"

    temporal = _load_playbook("temporal_memory_surrealdb_demo_playbook.yaml")
    mem = temporal.get("spec", {}).get("memory", {})
    backend = mem.get("backend", {})
    assert str(backend.get("type", "")).strip().lower() == "surrealdb"
    assert bool(mem.get("temporal", {}).get("enabled", False)) is True
