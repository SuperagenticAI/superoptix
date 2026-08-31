from __future__ import annotations

import importlib.util

import pytest

from superoptix.optimizers.gepa_rag_adapter.vector_stores.surrealdb_store import (
    SurrealDBVectorStore,
)


class FakeClient:
    def __init__(self, query_raw_response=None, query_response=None):
        self.query_raw_response = query_raw_response
        self.query_response = query_response
        self.query_raw_calls: list[tuple[str, dict]] = []
        self.query_calls: list[tuple[str, dict]] = []

    def query_raw(self, query: str, params: dict):
        self.query_raw_calls.append((query, params))
        return self.query_raw_response

    def query(self, query: str, params: dict):
        self.query_calls.append((query, params))
        return self.query_response


@pytest.fixture(autouse=True)
def mock_surrealdb_installed(monkeypatch):
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())


def test_init_rejects_invalid_table_name():
    client = FakeClient()
    with pytest.raises(ValueError):
        SurrealDBVectorStore(client=client, table_name="bad-table")


def test_build_where_clause_filters_invalid_keys_and_maps_operators():
    store = SurrealDBVectorStore(client=FakeClient(), table_name="docs")
    where, params = store._build_where_clause(
        {
            "tenant_id": "acme",
            "created_at": {"$gte": 100, "$lt": 200},
            "bad-key": "ignored",
        }
    )

    assert "tenant_id = $f_0" in where
    assert "created_at >= $f_1_gte" in where
    assert "created_at < $f_1_lt" in where
    assert "bad-key" not in where
    assert params["f_0"] == "acme"
    assert params["f_1_gte"] == 100
    assert params["f_1_lt"] == 200


def test_vector_search_uses_query_raw_and_formats_results():
    raw_response = {
        "result": [
            {
                "result": [
                    {
                        "id": "docs:1",
                        "content": "SurrealDB supports vector search",
                        "metadata": {"source": "kb"},
                        "score": 0.93,
                    }
                ]
            }
        ]
    }
    client = FakeClient(query_raw_response=raw_response)
    store = SurrealDBVectorStore(client=client, table_name="docs")

    results = store.vector_search([0.1, 0.2, 0.3], k=3, filters={"tenant_id": "acme"})

    assert len(results) == 1
    assert results[0]["content"] == "SurrealDB supports vector search"
    assert results[0]["metadata"]["source"] == "kb"
    assert results[0]["metadata"]["doc_id"] == "docs:1"
    assert results[0]["score"] == 0.93

    sent_query, sent_params = client.query_raw_calls[0]
    assert "vector::similarity::cosine" in sent_query
    assert "WHERE embedding != NONE" in sent_query
    assert sent_params["limit"] == 3
    assert sent_params["query_vector"] == [0.1, 0.2, 0.3]
    assert sent_params["f_0"] == "acme"


def test_vector_search_falls_back_to_query_when_query_raw_not_shaped():
    client = FakeClient(
        query_raw_response={"unexpected": True},
        query_response=[{"id": "docs:2", "content": "fallback"}],
    )
    store = SurrealDBVectorStore(client=client, table_name="docs")

    results = store.vector_search([0.2, 0.3], k=1)

    assert len(results) == 1
    assert results[0]["content"] == "fallback"
    assert len(client.query_raw_calls) == 1
    assert len(client.query_calls) == 1


def test_similarity_search_uses_embedding_function():
    client = FakeClient(
        query_raw_response={
            "result": [
                {"result": [{"id": "docs:3", "content": "embedded", "score": 0.5}]}
            ]
        }
    )
    embed_calls: list[str] = []

    def embed_fn(text: str):
        embed_calls.append(text)
        return [0.7, 0.8]

    store = SurrealDBVectorStore(
        client=client, table_name="docs", embedding_function=embed_fn
    )
    results = store.similarity_search("hello", k=2)

    assert embed_calls == ["hello"]
    assert len(results) == 1
    assert results[0]["content"] == "embedded"


def test_hybrid_search_emits_hybrid_query_and_scores():
    client = FakeClient(
        query_raw_response={
            "result": [
                {"result": [{"id": "docs:9", "content": "hybrid", "score": 0.77}]}
            ]
        }
    )

    store = SurrealDBVectorStore(
        client=client, table_name="docs", embedding_function=lambda _: [0.11, 0.22]
    )
    results = store.hybrid_search("vector db", k=4, alpha=0.8)

    assert len(results) == 1
    assert results[0]["score"] == 0.77

    sent_query, sent_params = client.query_raw_calls[0]
    assert "search::score()" in sent_query
    assert "@0@ $query" in sent_query
    assert sent_params["alpha"] == pytest.approx(0.8)
    assert sent_params["beta"] == pytest.approx(0.2)
    assert sent_params["limit"] == 4
    assert sent_params["query"] == "vector db"


def test_get_collection_info_parses_count_and_dimension():
    client = FakeClient(query_raw_response={"result": [{"result": [{"count": 12}]}]})
    store = SurrealDBVectorStore(client=client, table_name="docs")

    # First call returns count, second call returns dimension.
    responses = [
        {"result": [{"result": [{"count": 12}]}]},
        {"result": [{"result": [{"dimension": 384}]}]},
    ]
    idx = {"i": 0}

    def dynamic_query_raw(_query: str, _params: dict):
        value = responses[idx["i"]]
        idx["i"] += 1
        return value

    client.query_raw = dynamic_query_raw
    info = store.get_collection_info()

    assert info["name"] == "docs"
    assert info["document_count"] == 12
    assert info["dimension"] == 384
    assert info["vector_store_type"] == "surrealdb"
