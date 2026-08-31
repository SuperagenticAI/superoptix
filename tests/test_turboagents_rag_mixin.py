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


class _FakeTurboChroma:
    def __init__(
        self,
        *,
        path: str | None,
        collection_name: str | None,
        dim: int,
        bits: float,
        seed: int,
        metric: str,
    ):
        self.path = path
        self.collection_name = collection_name
        self.dim = dim
        self.bits = bits
        self.seed = seed
        self.metric = metric
        self.opened = None
        self.add_calls = []

    def open_collection(self, name: str):
        self.opened = name

    def create_collection(self, name: str, data=None, metadata=None):
        self.collection_name = name

    def add(self, vectors, metadata=None):
        self.add_calls.append((vectors, metadata))

    def search(self, query, k=10, rerank_top=None):
        return [
            {
                "index": 0,
                "score": 0.97,
                "metadata": {
                    "content": "TurboAgents chroma content",
                    "source": "turbo-chroma",
                },
            }
        ]


class _FakeTurboLanceDB:
    def __init__(self, uri: str, *, dim: int, bits: float, seed: int):
        self.uri = uri
        self.dim = dim
        self.bits = bits
        self.seed = seed
        self.opened = None

    def open_table(self, name: str):
        self.opened = name


class _FakeTurboSurrealDB:
    def __init__(
        self,
        *,
        url: str,
        namespace: str,
        database: str,
        dim: int,
        bits: float,
        seed: int,
        metric: str,
        auth=None,
    ):
        self.url = url
        self.namespace = namespace
        self.database = database
        self.dim = dim
        self.bits = bits
        self.seed = seed
        self.metric = metric
        self.auth = auth
        self.collection = None


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
    fake_rag.TurboChroma = _FakeTurboChroma
    fake_rag.TurboFAISS = _FakeTurboFAISS
    fake_rag.TurboLanceDB = _FakeTurboLanceDB
    fake_rag.TurboSurrealDB = _FakeTurboSurrealDB
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
                "retriever_type": "turboagents-chroma",
                "config": {"top_k": 3},
                "vector_store": {"embedding_dimension": 64},
            }
        )
        is True
    )
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


def test_setup_rag_and_retrieve_context_with_turboagents_chroma():
    harness = _Harness()
    spec = {
        "rag": {
            "enabled": True,
            "retriever_type": "turboagents-chroma",
            "config": {"top_k": 2},
            "vector_store": {
                "embedding_dimension": 64,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "bits": 3.5,
                "seed": 0,
                "collection_name": "demo_collection",
                "persist_directory": "/tmp/demo-chroma",
            },
        }
    }

    assert harness.setup_rag(spec) is True
    assert harness.vector_db["type"] == "turboagents-chroma"
    assert harness.add_documents(
        [{"content": "TurboAgents source doc", "metadata": {"source": "kb"}}]
    )

    docs = asyncio.run(harness.retrieve_context("Where does TurboAgents fit?", top_k=2))

    assert docs == ["TurboAgents chroma content"]
    assert harness.vector_db["collection_created"] is True
    assert len(harness.vector_db["store"].add_calls) == 1


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


def test_setup_rag_reopens_existing_turboagents_lancedb_table():
    harness = _Harness()
    spec = {
        "rag": {
            "enabled": True,
            "retriever_type": "turboagents-lancedb",
            "vector_store": {
                "embedding_dimension": 64,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "bits": 3.5,
                "seed": 0,
                "table_name": "demo_table",
                "uri": "/tmp/demo-lancedb",
            },
        }
    }

    assert harness.setup_rag(spec) is True
    assert harness.vector_db["type"] == "turboagents-lancedb"
    assert harness.vector_db["table_created"] is True
    assert harness.vector_db["store"].opened == "demo_table"


def test_setup_rag_restores_turboagents_surrealdb_collection_name():
    harness = _Harness()
    spec = {
        "rag": {
            "enabled": True,
            "retriever_type": "turboagents-surrealdb",
            "vector_store": {
                "embedding_dimension": 64,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "bits": 3.5,
                "seed": 0,
                "table_name": "rag_documents",
                "url": "surrealkv:///tmp/demo-surreal.kv",
                "namespace": "superoptix",
                "database": "knowledge",
            },
        }
    }

    assert harness.setup_rag(spec) is True
    assert harness.vector_db["type"] == "turboagents-surrealdb"
    assert harness.vector_db["collection_created"] is True
    assert harness.vector_db["store"].collection == "rag_documents"
