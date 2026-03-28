from __future__ import annotations

import importlib.util
import sys
import types

import pytest

from superoptix.optimizers.gepa_rag_adapter.vector_stores.turboagents_store import (
    TurboChromaVectorStore,
    TurboFAISSVectorStore,
    TurboLanceDBVectorStore,
    TurboSurrealDBVectorStore,
)


class FakeTurboChroma:
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
        self.init = {
            "path": path,
            "collection_name": collection_name,
            "dim": dim,
            "bits": bits,
            "seed": seed,
            "metric": metric,
        }
        self.created = None
        self.add_calls: list[tuple[object, list[dict[str, object]] | None]] = []

    def create_collection(self, name: str, data=None, metadata=None):
        self.created = {"name": name, "data": data, "metadata": metadata}

    def add(self, vectors, metadata=None):
        self.add_calls.append((vectors, metadata))

    def search(self, query, k=10, rerank_top=None):
        return [{"index": 0, "score": 0.91, "metadata": {"content": "chroma doc", "source": "kb"}}]


class FakeTurboFAISS:
    def __init__(self, *, dim: int, bits: float, seed: int):
        self.init = {"dim": dim, "bits": bits, "seed": seed}
        self.add_calls: list[tuple[object, list[dict[str, object]] | None]] = []
        self.search_calls: list[dict[str, object]] = []

    def add(self, vectors, metadata=None):
        self.add_calls.append((vectors, metadata))

    def search(self, query, k=10, rerank_top=None):
        self.search_calls.append({"query": query, "k": k, "rerank_top": rerank_top})
        return [{"index": 0, "score": 0.99, "metadata": {"content": "faiss doc", "source": "kb"}}]


class FakeTurboLanceDB:
    def __init__(self, uri: str, *, dim: int, bits: float, seed: int, metric: str):
        self.init = {"uri": uri, "dim": dim, "bits": bits, "seed": seed, "metric": metric}
        self.created = None
        self.add_calls: list[tuple[object, list[dict[str, object]] | None]] = []

    def create_table(self, name: str, data, metadata=None, mode: str = "overwrite"):
        self.created = {"name": name, "data": data, "metadata": metadata, "mode": mode}

    def add(self, vectors, metadata=None):
        self.add_calls.append((vectors, metadata))

    def search(self, query, k=10, rerank_top=None):
        return [{"index": 0, "score": 0.88, "metadata": {"content": "lance doc"}}]


class FakeTurboSurrealDB:
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
        self.init = {
            "url": url,
            "namespace": namespace,
            "database": database,
            "dim": dim,
            "bits": bits,
            "seed": seed,
            "metric": metric,
            "auth": auth,
        }
        self.created: list[str] = []
        self.added = []

    async def create_collection(self, name: str, dim=None):
        self.created.append(name)

    async def add(self, embeddings, metadata=None):
        self.added.append((embeddings, metadata))

    async def search(self, query_vec, *, k=10, rerank_top=None):
        return [{"index": 7, "score": 0.77, "metadata": {"content": "surreal doc"}}]


@pytest.fixture(autouse=True)
def fake_turboagents(monkeypatch):
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object() if name == "turboagents" else None)
    module = types.ModuleType("turboagents")
    rag = types.ModuleType("turboagents.rag")
    rag.TurboChroma = FakeTurboChroma
    rag.TurboFAISS = FakeTurboFAISS
    rag.TurboLanceDB = FakeTurboLanceDB
    rag.TurboSurrealDB = FakeTurboSurrealDB
    module.rag = rag
    monkeypatch.setitem(sys.modules, "turboagents", module)
    monkeypatch.setitem(sys.modules, "turboagents.rag", rag)


def test_turbo_faiss_vector_store_formats_results_and_tracks_count():
    store = TurboFAISSVectorStore(dim=3, bits=4.0, seed=11)
    ids = store.add_documents(
        [{"content": "faiss doc", "metadata": {"source": "kb"}}],
        [[0.1, 0.2, 0.3]],
    )

    results = store.vector_search([0.3, 0.2, 0.1], k=2)
    info = store.get_collection_info()

    assert ids == ["doc_0"]
    assert results[0]["content"] == "faiss doc"
    assert results[0]["metadata"]["source"] == "kb"
    assert results[0]["score"] == pytest.approx(0.99)
    assert info["document_count"] == 1
    assert info["vector_store_type"] == "turboagents-faiss"


def test_turbo_chroma_vector_store_creates_collection_and_queries():
    store = TurboChromaVectorStore(
        path="/tmp/superoptix-chroma",
        collection_name="docs",
        dim=64,
        rerank_top=8,
    )

    ids = store.add_documents(
        [{"content": "first", "metadata": {"source": "kb"}}],
        [[0.1] * 64],
    )
    results = store.vector_search([0.2] * 64, k=1)

    assert ids == ["doc_0"]
    assert store._store.created["name"] == "docs"
    assert len(store._store.add_calls) == 1
    assert results[0]["content"] == "chroma doc"
    assert results[0]["score"] == pytest.approx(0.91)
    assert store.get_collection_info()["vector_store_type"] == "turboagents-chroma"


def test_turbo_lancedb_vector_store_creates_table_then_adds():
    store = TurboLanceDBVectorStore(
        uri="/tmp/superoptix-lancedb",
        table_name="docs",
        dim=3,
        rerank_top=8,
    )

    store.add_documents([{"content": "first"}], [[0.1, 0.2, 0.3]])
    store.add_documents([{"content": "second"}], [[0.3, 0.2, 0.1]])
    results = store.vector_search([0.0, 0.1, 0.2], k=1)

    assert store._store.created["name"] == "docs"
    assert len(store._store.add_calls) == 1
    assert results[0]["content"] == "lance doc"
    assert results[0]["score"] == pytest.approx(0.88)


def test_turbo_surrealdb_vector_store_runs_async_adapter_synchronously(monkeypatch):
    store = TurboSurrealDBVectorStore(
        url="ws://localhost:8000/rpc",
        namespace="test",
        database="test",
        table_name="docs",
        dim=3,
    )

    run_calls = []

    def fake_run(coro):
        run_calls.append(coro.cr_code.co_name)
        return __import__("asyncio").run(coro)

    monkeypatch.setattr(TurboSurrealDBVectorStore, "_run", staticmethod(fake_run))

    store.add_documents([{"content": "surreal source"}], [[0.1, 0.2, 0.3]])
    results = store.vector_search([0.4, 0.5, 0.6], k=1)

    assert run_calls[:2] == ["create_collection", "add"]
    assert run_calls[-1] == "search"
    assert results[0]["content"] == "surreal doc"
    assert results[0]["score"] == pytest.approx(0.77)
