from __future__ import annotations

import asyncio
import importlib.util
import sys
from types import ModuleType

import pytest

from superoptix.core.rag_mixin import RAGMixin
from superoptix.core.validation import validate_rag_config


class _Harness(RAGMixin):
    pass


class _FakeVector:
    def __init__(self, values):
        self._values = list(values)

    def tolist(self):
        return list(self._values)


class _FakeSentenceTransformer:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def encode(self, text: str):
        base = [float((len(text) + i) % 7) for i in range(64)]
        return _FakeVector(base)


class _FakeTurboFAISS:
    def __init__(self, *, dim: int, bits: float, seed: int):
        self.dim = dim
        self.bits = bits
        self.seed = seed
        self.add_calls = []

    def add(self, vectors, metadata=None):
        self.add_calls.append((vectors, metadata))

    def search(self, query, k=10, rerank_top=None):
        return [
            {
                "index": 0,
                "score": 0.95,
                "metadata": {"content": "TurboAgents content", "source": "turbo"},
            }
        ]


@pytest.fixture(autouse=True)
def _install_fake_modules(monkeypatch):
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "turboagents":
            return object()
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    fake_turboagents = ModuleType("turboagents")
    fake_rag = ModuleType("turboagents.rag")
    fake_rag.TurboFAISS = _FakeTurboFAISS
    fake_turboagents.rag = fake_rag
    monkeypatch.setitem(sys.modules, "turboagents", fake_turboagents)
    monkeypatch.setitem(sys.modules, "turboagents.rag", fake_rag)

    fake_st = ModuleType("sentence_transformers")
    fake_st.SentenceTransformer = _FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st)


def test_validate_rag_config_accepts_turboagents_retrievers():
    assert (
        validate_rag_config(
            {
                "enabled": True,
                "retriever_type": "turboagents-faiss",
                "config": {"top_k": 3},
                "vector_store": {"embedding_dimension": 64},
            }
        )
        is True
    )


def test_setup_rag_and_retrieve_context_with_turboagents_faiss():
    harness = _Harness()
    spec = {
        "rag": {
            "enabled": True,
            "retriever_type": "turboagents-faiss",
            "config": {"top_k": 2},
            "vector_store": {
                "embedding_dimension": 64,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "bits": 3.5,
                "seed": 0,
            },
        }
    }

    assert harness.setup_rag(spec) is True
    assert harness.vector_db["type"] == "turboagents-faiss"
    assert harness.add_documents(
        [{"content": "TurboAgents source doc", "metadata": {"source": "kb"}}]
    )

    docs = asyncio.run(harness.retrieve_context("Where does TurboAgents fit?", top_k=2))

    assert docs == ["TurboAgents content"]
    assert len(harness.vector_db["store"].add_calls) == 1
