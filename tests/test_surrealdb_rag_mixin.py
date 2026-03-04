"""Tests for SurrealDB retrieval hardening in RAGMixin."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from superoptix.core.rag_mixin import RAGMixin


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

    def encode(self, _text: str):
        return _FakeVector([0.1, 0.2, 0.3])


class _FakeSurrealSession:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def signin(self, _payload):
        return None

    def use(self, _namespace, _database):
        return None

    def query(self, sql: str, params: dict | None = None):
        params = params or {}
        self.calls.append((sql, params))
        normalized = " ".join(sql.split()).lower()

        if normalized.startswith("info for table"):
            return [{"result": [{"indexes": {}}]}]

        return [
            {
                "result": [
                    {"content": "NEON-FOX-742 is present", "score": 0.91},
                    {"content": "Second hit", "score": 0.77},
                ]
            }
        ]


class _FakeSurreal:
    def __init__(self, _url: str, session: _FakeSurrealSession):
        self._session = session

    def __enter__(self):
        return self._session

    def __exit__(self, exc_type, exc, tb):
        return False


def _install_fake_surreal_modules(monkeypatch: pytest.MonkeyPatch, session: _FakeSurrealSession):
    fake_surreal_mod = ModuleType("surrealdb")
    fake_surreal_mod.Surreal = lambda url: _FakeSurreal(url, session)
    monkeypatch.setitem(sys.modules, "surrealdb", fake_surreal_mod)

    fake_st_mod = ModuleType("sentence_transformers")
    fake_st_mod.SentenceTransformer = _FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st_mod)


def _build_harness(mode: str = "vector", *, index_check: bool = False) -> _Harness:
    h = _Harness()
    h.vector_db = {
        "type": "surrealdb",
        "url": "memory",
        "namespace": "test",
        "database": "test",
        "username": "root",
        "password": "root",
        "skip_signin": True,
        "table_name": "rag_documents",
        "vector_field": "embedding",
        "content_field": "content",
        "retrieval_mode": mode,
        "hybrid_alpha": 0.8,
        "telemetry_enabled": True,
        "index_check": index_check,
        "config": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2"},
    }
    return h


@pytest.mark.asyncio
async def test_surrealdb_query_vector_mode_sets_telemetry(monkeypatch):
    session = _FakeSurrealSession()
    _install_fake_surreal_modules(monkeypatch, session)

    harness = _build_harness(mode="vector", index_check=False)
    docs = await harness._query_surrealdb("What is NEON-FOX-742?", top_k=3)

    assert docs == ["NEON-FOX-742 is present", "Second hit"]
    assert len(session.calls) == 1
    sql, params = session.calls[0]
    assert "vector::similarity::cosine" in sql
    assert "search::score()" not in sql
    assert params["top_k"] == 3
    telemetry = harness._last_retrieval_telemetry
    assert telemetry["provider"] == "surrealdb"
    assert telemetry["mode"] == "vector"
    assert telemetry["hit_count"] == 2
    assert telemetry["score_max"] == pytest.approx(0.91)


@pytest.mark.asyncio
async def test_surrealdb_query_hybrid_mode_uses_weighted_search(monkeypatch):
    session = _FakeSurrealSession()
    _install_fake_surreal_modules(monkeypatch, session)

    harness = _build_harness(mode="hybrid", index_check=False)
    docs = await harness._query_surrealdb("What is NEON-FOX-742?", top_k=5)

    assert docs[0] == "NEON-FOX-742 is present"
    assert len(session.calls) == 1
    sql, params = session.calls[0]
    assert "search::score()" in sql
    assert "@0@ $query" in sql
    assert params["query"] == "What is NEON-FOX-742?"
    assert params["alpha"] == pytest.approx(0.8)
    assert params["beta"] == pytest.approx(0.2)
    telemetry = harness._last_retrieval_telemetry
    assert telemetry["mode"] == "hybrid"
    assert telemetry["hit_count"] == 2


@pytest.mark.asyncio
async def test_surrealdb_index_check_is_warning_only_and_cached(monkeypatch):
    session = _FakeSurrealSession()
    _install_fake_surreal_modules(monkeypatch, session)

    harness = _build_harness(mode="hybrid", index_check=True)
    await harness._query_surrealdb("query one", top_k=2)
    await harness._query_surrealdb("query two", top_k=2)

    info_calls = [sql for sql, _ in session.calls if sql.strip().lower().startswith("info for table")]
    assert len(info_calls) == 1
    assert harness.vector_db["_index_check_done"] is True
    assert isinstance(harness.vector_db["_index_warnings"], list)
    assert len(harness.vector_db["_index_warnings"]) >= 1


# ---------------------------------------------------------------------------
# GraphRAG and multi-mode tests
# ---------------------------------------------------------------------------


class _FakeSurrealSessionGraph(_FakeSurrealSession):
    """Fake SurrealDB session that simulates graph expansion queries."""

    def __init__(self, graph_results: list[str] | None = None):
        super().__init__()
        self.graph_results = graph_results or ["Graph-expanded entity content"]

    def query(self, sql: str, params: dict | None = None):
        params = params or {}
        self.calls.append((sql, params))
        normalized = " ".join(sql.split()).lower()

        # Feature detector probe
        if "info for table" in normalized or "return type::is::float" in normalized:
            return [{"result": [{"indexes": {}}]}]

        # Graph expansion query (contains -> arrow)
        if "->" in sql:
            return [
                {"result": [{"content": c} for c in self.graph_results]}
            ]

        # Seed vector query
        return [
            {
                "result": [
                    {"id": "rag_documents:superoptix", "content": "NEON-FOX-742 is present", "score": 0.91},
                    {"id": "rag_documents:surrealdb", "content": "Second hit", "score": 0.77},
                ]
            }
        ]


def _build_graph_harness(
    mode: str = "graph",
    graph_depth: int = 1,
    graph_relations: list[str] | None = None,
    embedding_mode: str = "client",
) -> _Harness:
    h = _Harness()
    h.vector_db = {
        "type": "surrealdb",
        "url": "memory",
        "namespace": "test",
        "database": "test",
        "username": "root",
        "password": "root",
        "skip_signin": True,
        "table_name": "rag_documents",
        "vector_field": "embedding",
        "content_field": "content",
        "retrieval_mode": mode,
        "hybrid_alpha": 0.7,
        "telemetry_enabled": False,
        "index_check": False,
        "graph_depth": graph_depth,
        "graph_relations": graph_relations if graph_relations is not None else ["integrates_with", "provides"],
        "embedding_mode": embedding_mode,
        "config": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2"},
    }
    return h


def _install_fake_graph_modules(
    monkeypatch: pytest.MonkeyPatch,
    session: _FakeSurrealSessionGraph,
    relate_supported: bool = True,
):
    """Install fake surrealdb + sentence_transformers + SurrealDBFeatureDetector."""
    fake_surreal_mod = ModuleType("surrealdb")
    fake_surreal_mod.Surreal = lambda url: _FakeSurreal(url, session)
    monkeypatch.setitem(sys.modules, "surrealdb", fake_surreal_mod)

    fake_st_mod = ModuleType("sentence_transformers")
    fake_st_mod.SentenceTransformer = _FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st_mod)

    # Patch SurrealDBFeatureDetector.has to control capability gate
    import superoptix.utils.surrealdb_features as _feat_mod
    monkeypatch.setattr(
        _feat_mod.SurrealDBFeatureDetector,
        "has",
        lambda self, feature: relate_supported if feature == "relate" else False,
    )


@pytest.mark.asyncio
async def test_graph_mode_performs_vector_seed_then_graph_expansion(monkeypatch):
    """graph mode: vector seed search + graph expansion calls are both made."""
    session = _FakeSurrealSessionGraph(graph_results=["Graph entity: SurrealDB capabilities"])
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="graph", graph_depth=1)
    docs = await harness._query_surrealdb("What does SurrealDB provide?", top_k=2)

    # Should have seed results + graph-expanded results
    assert "NEON-FOX-742 is present" in docs
    assert "Second hit" in docs
    assert "Graph entity: SurrealDB capabilities" in docs

    # Verify both seed query and graph expansion queries were issued
    all_sql = [sql for sql, _ in session.calls]
    seed_queries = [s for s in all_sql if "vector::similarity::cosine" in s]
    graph_queries = [s for s in all_sql if "->" in s]
    assert len(seed_queries) >= 1, "Expected at least one vector seed query"
    assert len(graph_queries) >= 1, "Expected at least one graph expansion query"


@pytest.mark.asyncio
async def test_graph_mode_fallback_to_vector_when_relate_unsupported(monkeypatch):
    """graph mode: falls back to vector-only when RELATE is not supported."""
    session = _FakeSurrealSessionGraph()
    _install_fake_graph_modules(monkeypatch, session, relate_supported=False)

    harness = _build_graph_harness(mode="graph")
    docs = await harness._query_surrealdb("What does SurrealDB provide?", top_k=2)

    # Should still return seed vector results
    assert len(docs) >= 1
    # Should NOT have issued any graph expansion queries
    graph_queries = [sql for sql, _ in session.calls if "->" in sql]
    assert len(graph_queries) == 0, "Should not issue graph queries when RELATE unsupported"


@pytest.mark.asyncio
async def test_graph_mode_no_relations_returns_vector_only(monkeypatch):
    """graph mode with empty graph_relations returns vector results only."""
    session = _FakeSurrealSessionGraph()
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="graph", graph_relations=[])
    docs = await harness._query_surrealdb("Query", top_k=2)

    assert "NEON-FOX-742 is present" in docs
    # No graph expansion expected (empty relations list)
    graph_queries = [sql for sql, _ in session.calls if "->" in sql]
    assert len(graph_queries) == 0


@pytest.mark.asyncio
async def test_graph_mode_expansion_failure_is_nonfatal(monkeypatch):
    """graph mode: if graph expansion fails, seed results are still returned."""

    class _FailingGraphSession(_FakeSurrealSessionGraph):
        def query(self, sql: str, params: dict | None = None):
            params = params or {}
            self.calls.append((sql, params))
            normalized = " ".join(sql.split()).lower()
            if "info for table" in normalized or "return type::is::float" in normalized:
                return [{"result": [{"indexes": {}}]}]
            if "->" in sql:
                raise RuntimeError("Simulated graph traversal failure")
            return [{"result": [{"id": "rag_documents:x", "content": "Seed result", "score": 0.9}]}]

    session = _FailingGraphSession()
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="graph")
    docs = await harness._query_surrealdb("Query", top_k=2)

    # Seed results should still be returned despite graph failure
    assert "Seed result" in docs


@pytest.mark.asyncio
async def test_multi_mode_issues_hybrid_then_graph_expansion(monkeypatch):
    """multi mode: runs hybrid query first, then graph-expands the results."""
    session = _FakeSurrealSessionGraph(graph_results=["Multi-mode graph content"])
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="multi")
    docs = await harness._query_surrealdb("What does SurrealDB provide?", top_k=2)

    # Should include seed results and graph-expanded content
    assert len(docs) >= 1

    all_sql = [sql for sql, _ in session.calls]
    hybrid_queries = [s for s in all_sql if "search::score()" in s]
    assert len(hybrid_queries) >= 1, "multi mode should issue a hybrid query"


@pytest.mark.asyncio
async def test_multi_mode_fallback_to_hybrid_when_relate_unsupported(monkeypatch):
    """multi mode falls back to hybrid (not vector) when RELATE not supported."""
    session = _FakeSurrealSessionGraph()
    _install_fake_graph_modules(monkeypatch, session, relate_supported=False)

    harness = _build_graph_harness(mode="multi")
    docs = await harness._query_surrealdb("Query", top_k=2)

    assert len(docs) >= 1
    # Should have issued a hybrid query (search::score)
    hybrid_queries = [sql for sql, _ in session.calls if "search::score()" in sql]
    assert len(hybrid_queries) >= 1


def test_setup_surrealdb_accepts_graph_mode():
    """_setup_surrealdb correctly parses graph mode and graph config."""
    h = _Harness()
    config = {
        "url": "ws://localhost:8000",
        "namespace": "superoptix",
        "database": "knowledge",
        "username": "root",
        "password": "secret",
        "table_name": "rag_documents",
        "vector_field": "embedding",
        "content_field": "content",
        "_rag_runtime_config": {
            "retrieval_mode": "graph",
            "graph_depth": 2,
            "graph_relations": ["integrates_with", "provides", "supports"],
        },
    }
    result = h._setup_surrealdb(config)
    assert result is not None
    assert result["retrieval_mode"] == "graph"
    assert result["graph_depth"] == 2
    assert result["graph_relations"] == ["integrates_with", "provides", "supports"]


def test_setup_surrealdb_clamps_graph_depth():
    """_setup_surrealdb clamps graph_depth to [1, 3]."""
    h = _Harness()
    config = {
        "url": "memory",
        "namespace": "t", "database": "t", "username": "r", "password": "r",
        "table_name": "docs", "vector_field": "emb", "content_field": "c",
        "_rag_runtime_config": {"retrieval_mode": "graph", "graph_depth": 99},
    }
    result = h._setup_surrealdb(config)
    assert result["graph_depth"] == 3  # clamped to max


def test_setup_surrealdb_rejects_unknown_mode_falls_back_to_vector():
    """_setup_surrealdb falls back to vector for unknown retrieval modes."""
    h = _Harness()
    config = {
        "url": "memory",
        "namespace": "t", "database": "t", "username": "r", "password": "r",
        "table_name": "docs", "vector_field": "emb", "content_field": "c",
        "_rag_runtime_config": {"retrieval_mode": "unknown_mode"},
    }
    result = h._setup_surrealdb(config)
    assert result["retrieval_mode"] == "vector"


# ---------------------------------------------------------------------------
# Increment 3: Server-side embedding mode tests
# ---------------------------------------------------------------------------


def _build_server_embed_harness(embedding_mode: str = "server") -> _Harness:
    h = _Harness()
    h.vector_db = {
        "type": "surrealdb",
        "url": "memory",
        "namespace": "test",
        "database": "test",
        "username": "root",
        "password": "root",
        "skip_signin": True,
        "table_name": "rag_documents",
        "vector_field": "embedding",
        "content_field": "content",
        "retrieval_mode": "vector",
        "hybrid_alpha": 0.7,
        "telemetry_enabled": False,
        "index_check": False,
        "graph_depth": 1,
        "graph_relations": [],
        "embedding_mode": embedding_mode,
        "config": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2"},
    }
    return h


class _FakeSurrealSessionServerEmbed(_FakeSurrealSession):
    """Fake SurrealDB session where fn::embed is available."""

    def __init__(self, fn_embed_supported: bool = True):
        super().__init__()
        self.fn_embed_supported = fn_embed_supported

    def query(self, sql: str, params: dict | None = None):
        params = params or {}
        self.calls.append((sql, params))
        normalized = " ".join(sql.split()).lower()

        if "fn::embed" in normalized:
            if not self.fn_embed_supported:
                raise RuntimeError("No such function: fn::embed")
            # Server-side embedding probe or actual query
            if "return fn::embed" in normalized:
                return [{"result": [[0.1, 0.2, 0.3]]}]
            # Actual SELECT using fn::embed
            return [{"result": [{"content": "Server-embedded result", "score": 0.88}]}]

        if normalized.startswith("info for table"):
            return [{"result": [{"indexes": {}}]}]

        # Fallback vector query (client-side)
        return [{"result": [{"content": "Client-embedded result", "score": 0.75}]}]


def _install_server_embed_modules(
    monkeypatch: pytest.MonkeyPatch,
    session: _FakeSurrealSession,
    fn_embed_supported: bool = True,
):
    fake_surreal_mod = ModuleType("surrealdb")
    fake_surreal_mod.Surreal = lambda url: _FakeSurreal(url, session)
    monkeypatch.setitem(sys.modules, "surrealdb", fake_surreal_mod)

    fake_st_mod = ModuleType("sentence_transformers")
    fake_st_mod.SentenceTransformer = _FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st_mod)


@pytest.mark.asyncio
async def test_server_embedding_mode_uses_fn_embed_in_sql(monkeypatch):
    """embedding_mode=server: fn::embed() used in SQL, SentenceTransformer not called."""
    session = _FakeSurrealSessionServerEmbed(fn_embed_supported=True)
    _install_server_embed_modules(monkeypatch, session)

    harness = _build_server_embed_harness(embedding_mode="server")
    docs = await harness._query_surrealdb("What is SurrealDB?", top_k=3)

    assert docs == ["Server-embedded result"]
    # Verify fn::embed appears in SQL (not $query_vector)
    all_sql = " ".join(sql for sql, _ in session.calls)
    assert "fn::embed" in all_sql
    # Verify $query_vector NOT in params (server mode skips client embedding)
    for _, params in session.calls:
        assert "query_vector" not in params


@pytest.mark.asyncio
async def test_server_embedding_fallback_to_client_when_fn_embed_unavailable(monkeypatch):
    """embedding_mode=server: falls back to client-side when fn::embed unavailable."""
    session = _FakeSurrealSessionServerEmbed(fn_embed_supported=False)
    _install_server_embed_modules(monkeypatch, session)

    harness = _build_server_embed_harness(embedding_mode="server")
    docs = await harness._query_surrealdb("What is SurrealDB?", top_k=3)

    # Should fall back to client-side and still return results
    assert len(docs) >= 1
    # Verify fallback: $query_vector used in subsequent SQL
    vector_params = [params for _, params in session.calls if "query_vector" in params]
    assert len(vector_params) >= 1, "Fallback should issue a client-side vector query"


@pytest.mark.asyncio
async def test_client_embedding_mode_uses_sentence_transformer(monkeypatch):
    """embedding_mode=client (default): SentenceTransformer is used, fn::embed is not."""
    session = _FakeSurrealSession()
    _install_fake_surreal_modules(monkeypatch, session)

    harness = _build_server_embed_harness(embedding_mode="client")
    docs = await harness._query_surrealdb("Query text", top_k=2)

    assert len(docs) >= 1
    # Verify fn::embed NOT in any issued SQL
    all_sql = " ".join(sql for sql, _ in session.calls)
    assert "fn::embed" not in all_sql
    # Verify $query_vector was sent
    vector_params = [params for _, params in session.calls if "query_vector" in params]
    assert len(vector_params) >= 1


@pytest.mark.asyncio
async def test_server_embedding_mode_hybrid_uses_fn_embed_without_query_vector(monkeypatch):
    """embedding_mode=server + mode=hybrid uses fn::embed and query_text params."""
    session = _FakeSurrealSessionServerEmbed(fn_embed_supported=True)
    _install_server_embed_modules(monkeypatch, session)

    harness = _build_server_embed_harness(embedding_mode="server")
    harness.vector_db["retrieval_mode"] = "hybrid"
    docs = await harness._query_surrealdb("Hybrid query", top_k=2)

    assert len(docs) >= 1
    sql_calls = [sql for sql, _ in session.calls]
    assert any("search::score()" in sql for sql in sql_calls)
    assert any("fn::embed" in sql for sql in sql_calls)
    assert all("query_vector" not in params for _, params in session.calls)
    assert any("query_text" in params for _, params in session.calls)


@pytest.mark.asyncio
async def test_server_embedding_mode_graph_uses_fn_embed_seed(monkeypatch):
    """embedding_mode=server + mode=graph uses fn::embed for graph seed query."""
    session = _FakeSurrealSessionGraph(graph_results=["Graph expanded"])
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="graph", embedding_mode="server")
    docs = await harness._query_surrealdb("Graph query", top_k=2)

    assert len(docs) >= 1
    assert "Graph expanded" in docs
    sql_calls = [sql for sql, _ in session.calls]
    assert any("fn::embed" in sql for sql in sql_calls)
    assert all("query_vector" not in params for _, params in session.calls)
    assert any("query_text" in params for _, params in session.calls)


@pytest.mark.asyncio
async def test_server_embedding_mode_multi_uses_fn_embed_without_query_vector(monkeypatch):
    """embedding_mode=server + mode=multi keeps server-side embeddings through hybrid+graph."""
    session = _FakeSurrealSessionGraph(graph_results=["Multi graph"])
    _install_fake_graph_modules(monkeypatch, session, relate_supported=True)

    harness = _build_graph_harness(mode="multi", embedding_mode="server")
    docs = await harness._query_surrealdb("Multi query", top_k=2)

    assert len(docs) >= 1
    assert "Multi graph" in docs
    sql_calls = [sql for sql, _ in session.calls]
    assert any("search::score()" in sql for sql in sql_calls)
    assert any("fn::embed" in sql for sql in sql_calls)
    assert all("query_vector" not in params for _, params in session.calls)


def test_setup_surrealdb_parses_embedding_mode():
    """_setup_surrealdb correctly parses embedding_mode config."""
    h = _Harness()
    config = {
        "url": "memory",
        "namespace": "t", "database": "t", "username": "r", "password": "r",
        "table_name": "docs", "vector_field": "emb", "content_field": "c",
        "_rag_runtime_config": {"embedding_mode": "server"},
    }
    result = h._setup_surrealdb(config)
    assert result["embedding_mode"] == "server"


def test_setup_surrealdb_defaults_embedding_mode_to_client():
    """_setup_surrealdb defaults embedding_mode to 'client' when not specified."""
    h = _Harness()
    config = {
        "url": "memory",
        "namespace": "t", "database": "t", "username": "r", "password": "r",
        "table_name": "docs", "vector_field": "emb", "content_field": "c",
    }
    result = h._setup_surrealdb(config)
    assert result["embedding_mode"] == "client"


def test_setup_surrealdb_rejects_invalid_embedding_mode():
    """_setup_surrealdb falls back to 'client' for unknown embedding_mode values."""
    h = _Harness()
    config = {
        "url": "memory",
        "namespace": "t", "database": "t", "username": "r", "password": "r",
        "table_name": "docs", "vector_field": "emb", "content_field": "c",
        "_rag_runtime_config": {"embedding_mode": "gpu_turbo_mode"},
    }
    result = h._setup_surrealdb(config)
    assert result["embedding_mode"] == "client"
