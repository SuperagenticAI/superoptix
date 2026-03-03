"""Tests for the enhanced memory system."""

import os
import tempfile
from datetime import datetime

import pytest

import superoptix.memory.memory_backends as memory_backends
from superoptix.memory import (
    AgentMemory,
    ContextManager,
    EpisodicMemory,
    FileBackend,
    LongTermMemory,
    ShortTermMemory,
    SQLiteBackend,
    SurrealDBBackend,
)


class TestMemoryBackends:
    """Test memory backend implementations."""

    def test_file_backend_basic_operations(self):
        """Test basic file backend operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)

            # Test store and retrieve
            assert backend.store("test_key", {"data": "test_value"})
            retrieved = backend.retrieve("test_key")
            assert retrieved == {"data": "test_value"}

            # Test exists
            assert backend.exists("test_key")
            assert not backend.exists("nonexistent_key")

            # Test delete
            assert backend.delete("test_key")
            assert not backend.exists("test_key")

    def test_file_backend_ttl(self):
        """Test TTL functionality in file backend."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)

            # Store with short TTL
            backend.store("ttl_key", "ttl_value", ttl=1)
            assert backend.retrieve("ttl_key") == "ttl_value"

            # Wait for expiration
            import time

            time.sleep(2)
            assert backend.retrieve("ttl_key") is None

    def test_sqlite_backend_basic_operations(self):
        """Test basic SQLite backend operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            backend = SQLiteBackend(db_path)

            # Test store and retrieve
            assert backend.store("test_key", {"data": "test_value"})
            retrieved = backend.retrieve("test_key")
            assert retrieved == {"data": "test_value"}

            # Test keys and size
            assert "test_key" in backend.keys()
            assert backend.size() == 1

            # Test clear
            backend.clear()
            assert backend.size() == 0

    def test_surrealdb_backend_basic_operations(self, monkeypatch):
        """Test basic SurrealDB backend operations via fake client."""

        class _FakeSurrealSession:
            def __init__(self):
                self.rows: list[dict] = []

            def signin(self, _payload):
                return None

            def use(self, _namespace, _database):
                return None

            def query(self, query: str, params: dict | None = None):
                params = params or {}
                sql = " ".join(query.split()).lower()
                now = datetime.now().isoformat()

                if "where expires_at != none and expires_at < time::now()" in sql:
                    self.rows = [
                        row
                        for row in self.rows
                        if not row.get("expires_at") or row["expires_at"] >= now
                    ]
                    return [{"result": []}]

                if sql.startswith("delete") and "where memory_key = $memory_key" in sql:
                    memory_key = params.get("memory_key")
                    self.rows = [
                        row for row in self.rows if row.get("memory_key") != memory_key
                    ]
                    return [{"result": []}]

                if sql.startswith("create"):
                    payload = dict(params.get("payload", {}))
                    self.rows.append(payload)
                    return [{"result": [payload]}]

                if sql.startswith("select *"):
                    memory_key = params.get("memory_key")
                    result = [
                        row for row in self.rows if row.get("memory_key") == memory_key
                    ]
                    return [{"result": result[:1]}]

                if sql.startswith("select memory_key"):
                    return [{"result": [{"memory_key": row["memory_key"]} for row in self.rows]}]

                if sql.startswith("select count()"):
                    return [{"result": [{"count": len(self.rows)}]}]

                if sql.startswith("delete") and "where" not in sql:
                    self.rows = []
                    return [{"result": []}]

                return [{"result": []}]

        fake_session = _FakeSurrealSession()

        class _FakeSurreal:
            def __init__(self, _url):
                pass

            def __enter__(self):
                return fake_session

            def __exit__(self, exc_type, exc, tb):
                return False

        monkeypatch.setattr(memory_backends, "SURREALDB_AVAILABLE", True)
        monkeypatch.setattr(memory_backends, "Surreal", _FakeSurreal)

        backend = SurrealDBBackend(url="memory", skip_signin=True, table_name="memory")

        assert backend.store("user:1", {"name": "alice"})
        assert backend.retrieve("user:1") == {"name": "alice"}
        assert backend.exists("user:1")
        assert "user:1" in backend.keys()
        assert backend.size() == 1

        assert backend.store("bad:json", {"tags": {"a", "b"}})
        restored = backend.retrieve("bad:json")
        assert isinstance(restored, dict)
        assert isinstance(restored["tags"], set)

        assert backend.delete("user:1")
        assert backend.retrieve("user:1") is None
        assert backend.size() == 1
        assert backend.clear()
        assert backend.size() == 0

    def test_surrealdb_backend_expiry_and_pattern_keys(self, monkeypatch):
        """Test TTL expiry and key pattern filtering."""

        class _FakeSurrealSession:
            def __init__(self):
                self.rows: list[dict] = []

            def signin(self, _payload):
                return None

            def use(self, _namespace, _database):
                return None

            def query(self, query: str, params: dict | None = None):
                params = params or {}
                sql = " ".join(query.split()).lower()
                now = datetime.now().isoformat()

                if "where expires_at != none and expires_at < time::now()" in sql:
                    self.rows = [
                        row
                        for row in self.rows
                        if not row.get("expires_at") or row["expires_at"] >= now
                    ]
                    return [{"result": []}]

                if sql.startswith("delete") and "where memory_key = $memory_key" in sql:
                    memory_key = params.get("memory_key")
                    self.rows = [
                        row for row in self.rows if row.get("memory_key") != memory_key
                    ]
                    return [{"result": []}]

                if sql.startswith("create"):
                    payload = dict(params.get("payload", {}))
                    self.rows.append(payload)
                    return [{"result": [payload]}]

                if sql.startswith("select *"):
                    memory_key = params.get("memory_key")
                    result = [
                        row for row in self.rows if row.get("memory_key") == memory_key
                    ]
                    return [{"result": result[:1]}]

                if sql.startswith("select memory_key"):
                    return [{"result": [{"memory_key": row["memory_key"]} for row in self.rows]}]

                if sql.startswith("select count()"):
                    return [{"result": [{"count": len(self.rows)}]}]

                return [{"result": []}]

        fake_session = _FakeSurrealSession()

        class _FakeSurreal:
            def __init__(self, _url):
                pass

            def __enter__(self):
                return fake_session

            def __exit__(self, exc_type, exc, tb):
                return False

        monkeypatch.setattr(memory_backends, "SURREALDB_AVAILABLE", True)
        monkeypatch.setattr(memory_backends, "Surreal", _FakeSurreal)

        backend = SurrealDBBackend(url="memory", skip_signin=True, table_name="memory")
        assert backend.store("tenant:a:1", {"v": 1})
        assert backend.store("tenant:a:2", {"v": 2})
        assert backend.store("tenant:b:1", {"v": 3}, ttl=-1)  # already expired

        keys = backend.keys("tenant:a:*")
        assert sorted(keys) == ["tenant:a:1", "tenant:a:2"]
        assert backend.retrieve("tenant:b:1") is None

    def test_surrealdb_backend_invalid_table_name_raises(self, monkeypatch):
        """Ensure table name validation prevents unsafe SQL identifier use."""
        monkeypatch.setattr(memory_backends, "SURREALDB_AVAILABLE", True)
        with pytest.raises(ValueError):
            SurrealDBBackend(table_name="bad-table")


class TestShortTermMemory:
    """Test short-term memory functionality."""

    def test_basic_operations(self):
        """Test basic short-term memory operations."""
        memory = ShortTermMemory(capacity=3)

        # Test store and retrieve
        assert memory.store("key1", "value1")
        assert memory.retrieve("key1") == "value1"

        # Test capacity and eviction
        memory.store("key2", "value2")
        memory.store("key3", "value3")
        memory.store("key4", "value4")  # Should evict key1

        assert memory.retrieve("key1") is None
        assert memory.retrieve("key4") == "value4"

    def test_conversation_history(self):
        """Test conversation history functionality."""
        memory = ShortTermMemory()

        # Add conversation messages
        memory.add_to_conversation("user", "Hello")
        memory.add_to_conversation("assistant", "Hi there!")
        memory.add_to_conversation("user", "How are you?")

        # Get conversation history
        history = memory.get_conversation_history()
        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"

    def test_working_memory(self):
        """Test working memory functionality."""
        memory = ShortTermMemory()

        # Set and get working memory
        memory.set_working_memory("current_task", "testing")
        assert memory.get_working_memory("current_task") == "testing"

        # Clear working memory
        memory.clear_working_memory()
        assert memory.get_working_memory("current_task") is None


class TestLongTermMemory:
    """Test long-term memory functionality."""

    def test_knowledge_storage_and_retrieval(self):
        """Test knowledge storage and retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            memory = LongTermMemory(backend=backend, enable_embeddings=False)

            # Store knowledge
            knowledge_id = memory.store_knowledge(
                content="Python is a programming language",
                category="programming",
                tags=["python", "programming"],
            )
            assert knowledge_id is not None

            # Retrieve knowledge
            knowledge = memory.retrieve_knowledge(knowledge_id)
            assert knowledge is not None
            assert knowledge["content"] == "Python is a programming language"
            assert "python" in knowledge["tags"]

    def test_knowledge_search(self):
        """Test knowledge search functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            memory = LongTermMemory(backend=backend, enable_embeddings=False)

            # Store multiple knowledge items
            memory.store_knowledge(
                "Python is great for data science", "programming", tags=["python"]
            )
            memory.store_knowledge(
                "JavaScript runs in browsers", "programming", tags=["javascript"]
            )
            memory.store_knowledge(
                "Machine learning uses algorithms", "ai", tags=["ml", "algorithms"]
            )

            # Search for Python-related content
            results = memory.search_knowledge("Python programming")
            assert len(results) > 0
            assert any("Python" in result["content"] for result in results)

    def test_knowledge_categories_and_tags(self):
        """Test knowledge organization by categories and tags."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            memory = LongTermMemory(backend=backend, enable_embeddings=False)

            # Store knowledge with categories and tags
            memory.store_knowledge("DSPy framework", "frameworks", tags=["dspy", "llm"])
            memory.store_knowledge(
                "React library", "frameworks", tags=["react", "javascript"]
            )

            # Get by category
            frameworks = memory.get_knowledge_by_category("frameworks")
            assert len(frameworks) == 2

            # Get by tags
            dspy_items = memory.get_knowledge_by_tags(["dspy"])
            assert len(dspy_items) == 1
            assert "DSPy" in dspy_items[0]["content"]


class TestEpisodicMemory:
    """Test episodic memory functionality."""

    def test_episode_lifecycle(self):
        """Test complete episode lifecycle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            memory = EpisodicMemory(backend=backend)

            # Start episode
            episode_id = memory.start_episode(
                title="Test Episode",
                description="Testing episode functionality",
                tags=["test"],
            )
            assert episode_id is not None

            # Add events
            assert memory.add_event(episode_id, "start", "Episode started")
            assert memory.add_event(episode_id, "action", "Performed action")

            # Get episode
            episode = memory.get_episode(episode_id)
            assert episode is not None
            assert episode.title == "Test Episode"
            assert len(episode.events) == 2

            # End episode
            outcome = {"success": True, "result": "completed"}
            assert memory.end_episode(episode_id, outcome, "completed")

            # Verify episode is no longer active
            active_episodes = memory.get_active_episodes()
            assert len(active_episodes) == 0

    def test_episode_search(self):
        """Test episode search functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            memory = EpisodicMemory(backend=backend)

            # Create multiple episodes
            ep1 = memory.start_episode("Python Tutorial", tags=["python", "tutorial"])
            ep2 = memory.start_episode("JavaScript Guide", tags=["javascript", "guide"])

            memory.end_episode(ep1, {"success": True}, "completed")
            memory.end_episode(ep2, {"success": True}, "completed")

            # Search episodes
            python_episodes = memory.search_episodes(query="Python")
            assert len(python_episodes) >= 1
            assert any("Python" in ep.title for ep in python_episodes)

            # Search by tags
            tutorial_episodes = memory.search_episodes(tags=["tutorial"])
            assert len(tutorial_episodes) >= 1


class TestContextManager:
    """Test context manager functionality."""

    def test_context_stack_operations(self):
        """Test context stack operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            context_mgr = ContextManager("test_agent", backend=backend)

            # Push context
            context_id = context_mgr.push_context(
                name="task_context",
                scope="task",
                data={"task_name": "testing", "priority": "high"},
            )
            assert context_id is not None

            # Get context
            task_data = context_mgr.get_context("task")
            assert task_data is not None
            assert task_data["task_name"] == "testing"

            # Set context value
            assert context_mgr.set_context("task", "status", "in_progress")
            assert context_mgr.get_context("task", "status") == "in_progress"

    def test_context_scopes(self):
        """Test different context scopes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(temp_dir)
            context_mgr = ContextManager("test_agent", backend=backend)

            # Should have default global and session contexts
            assert context_mgr.get_context("global") is not None
            assert context_mgr.get_context("session") is not None

            # Add local context
            context_mgr.push_context("local", "local", {"temp": "data"})

            # Get full context (merged from all scopes)
            full_context = context_mgr.get_full_context()
            assert "agent_id" in full_context  # From global
            assert "session_id" in full_context  # From session
            assert "temp" in full_context  # From local


class TestAgentMemory:
    """Test integrated agent memory system."""

    def test_memory_integration(self):
        """Test integrated memory functionality."""
        memory = AgentMemory("test_agent", enable_embeddings=False)

        # Test different memory types
        assert memory.remember("Short term info", memory_type="short")
        assert memory.remember(
            "Long term knowledge", memory_type="long", category="knowledge"
        )
        assert memory.remember("Task context", memory_type="context", category="task")

        # Test recall
        results = memory.recall("knowledge", memory_type="all")
        assert len(results) > 0

    def test_interaction_tracking(self):
        """Test interaction tracking."""
        memory = AgentMemory("test_agent", enable_embeddings=False)

        # Start interaction
        episode_id = memory.start_interaction({"user": "test_user"})
        assert episode_id is not None

        # Add events
        assert memory.add_interaction_event("user_input", "User asked question")
        assert memory.add_interaction_event("agent_response", "Agent provided answer")

        # Get conversation context
        context = memory.get_conversation_context()
        assert context is not None
        assert context["current_episode"] == episode_id

        # End interaction
        assert memory.end_interaction({"success": True})

    def test_learning_from_interaction(self):
        """Test learning from interactions."""
        memory = AgentMemory("test_agent", enable_embeddings=False)

        # Learn insights
        insights = ["Users prefer detailed explanations", "Code examples are helpful"]
        patterns = {
            "preferred_style": "detailed",
            "helpful_features": ["code", "examples"],
        }

        assert memory.learn_from_interaction(insights, patterns)

        # Verify learning was stored
        summary = memory.get_memory_summary()
        assert summary["long_term_memory"]["total_items"] >= len(insights)

    def test_memory_cleanup(self):
        """Test memory cleanup functionality."""
        memory = AgentMemory("test_agent", enable_embeddings=False)

        # Add some temporary data
        memory.remember("Temp data", memory_type="short", ttl=1)

        # Perform cleanup
        cleanup_stats = memory.cleanup_memory()
        assert isinstance(cleanup_stats, dict)
        assert "expired_short_term" in cleanup_stats

    def test_memory_statistics(self):
        """Test memory statistics."""
        memory = AgentMemory("test_agent", enable_embeddings=False)

        # Add some data
        memory.remember("Test data 1", memory_type="short")
        memory.remember("Test knowledge", memory_type="long")

        # Get statistics
        stats = memory.get_memory_summary()
        assert stats["agent_id"] == "test_agent"
        assert stats["short_term_memory"]["size"] >= 1
        assert stats["long_term_memory"]["total_items"] >= 1


@pytest.fixture
def sample_memory():
    """Fixture providing a sample memory system for testing."""
    return AgentMemory("test_agent", enable_embeddings=False)


def test_memory_persistence(sample_memory):
    """Test memory persistence across sessions."""
    # Store long-term knowledge
    sample_memory.remember(
        "Persistent knowledge", memory_type="long", category="test", tags=["persistent"]
    )

    # Save state
    assert sample_memory.save_memory_state()

    # Create new memory instance (simulating restart)
    new_memory = AgentMemory("test_agent", enable_embeddings=False)

    # Should be able to recall persistent knowledge
    results = new_memory.recall("Persistent knowledge", memory_type="long")
    assert len(results) > 0


def test_memory_search_relevance(sample_memory):
    """Test memory search relevance and ranking."""
    # Store knowledge with different relevance
    sample_memory.remember(
        "Python programming language", memory_type="long", tags=["python"]
    )
    sample_memory.remember(
        "Java programming language", memory_type="long", tags=["java"]
    )
    sample_memory.remember("Python snake animal", memory_type="long", tags=["animal"])

    # Search for Python programming
    results = sample_memory.recall("Python programming", memory_type="long")

    # Should prioritize programming-related results
    assert len(results) > 0
    top_result = results[0]
    assert "programming" in top_result["content"]


# ---------------------------------------------------------------------------
# Temporal memory tests (SurrealDBBackend with temporal_enabled=True)
# ---------------------------------------------------------------------------


class _TemporalSurrealSession:
    """Fake SurrealDB session that tracks both primary and versions table writes."""

    def __init__(self):
        self.primary: list[dict] = []    # primary table rows
        self.versions: list[dict] = []   # versions table rows (append-only)

    def signin(self, _payload):
        return None

    def use(self, _ns, _db):
        return None

    def query(self, sql: str, params: dict | None = None):
        params = params or {}
        normalized = " ".join(sql.split()).lower()

        # Expired cleanup (primary only)
        if "expires_at != none and expires_at < time::now()" in normalized:
            return [{"result": []}]

        # DELETE primary by memory_key
        if normalized.startswith("delete") and "where memory_key = $memory_key" in normalized:
            mk = params.get("memory_key")
            self.primary = [r for r in self.primary if r.get("memory_key") != mk]
            return [{"result": []}]

        # DELETE full table (clear)
        if normalized.startswith("delete") and "where" not in normalized:
            if "versions" in sql.lower():
                self.versions = []
            else:
                self.primary = []
            return [{"result": []}]

        # CREATE — route to correct table
        if normalized.startswith("create"):
            payload = dict(params.get("payload", {}))
            if "versions" in sql.lower():
                self.versions.append(payload)
            else:
                self.primary.append(payload)
            return [{"result": [payload]}]

        # SELECT * (retrieve by key — primary only)
        if normalized.startswith("select *") and "version_ts" not in normalized:
            mk = params.get("memory_key") or params.get("key")
            matches = [r for r in self.primary if r.get("memory_key") == mk]
            return [{"result": matches[:1]}]

        # SELECT from versions table — retrieve_at
        if "version_ts <=" in normalized and "limit 1" in normalized:
            mk = params.get("key")
            as_of = params.get("as_of", "")
            matches = [
                r for r in self.versions
                if r.get("memory_key") == mk and str(r.get("version_ts", "")) <= as_of
            ]
            matches.sort(key=lambda r: r.get("version_ts", ""), reverse=True)
            return [{"result": matches[:1]}]

        # SELECT from versions table — history()
        if "version_ts desc limit" in normalized and "version_ts <=" not in normalized:
            mk = params.get("key")
            limit = params.get("limit", 10)
            matches = [r for r in self.versions if r.get("memory_key") == mk]
            matches.sort(key=lambda r: r.get("version_ts", ""), reverse=True)
            return [{"result": matches[:limit]}]

        # COUNT — route by table
        if "select count()" in normalized:
            if "versions" in sql.lower():
                mk = params.get("key")
                count = sum(1 for r in self.versions if r.get("memory_key") == mk)
            else:
                count = len(self.primary)
            return [{"result": [{"count": count}]}]

        # SELECT memory_key (keys())
        if normalized.startswith("select memory_key"):
            return [{"result": [{"memory_key": r["memory_key"]} for r in self.primary]}]

        # Prune: DELETE FROM (SELECT ... LIMIT $excess) — best-effort, ignore in tests
        if "order by version_ts asc limit" in normalized:
            return [{"result": []}]

        return [{"result": []}]


def _make_temporal_backend(monkeypatch, temporal_enabled=True, max_versions=50):
    """Build a SurrealDBBackend wired to a TemporalSurrealSession."""
    session = _TemporalSurrealSession()

    class _FakeSurreal:
        def __init__(self, _url):
            pass

        def __enter__(self):
            return session

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(memory_backends, "SURREALDB_AVAILABLE", True)
    monkeypatch.setattr(memory_backends, "Surreal", _FakeSurreal)

    backend = SurrealDBBackend(
        url="memory",
        skip_signin=True,
        table_name="mem",
        temporal_enabled=temporal_enabled,
        max_versions_per_key=max_versions,
    )
    return backend, session


class TestTemporalSurrealDBBackend:
    """Tests for temporal versioning in SurrealDBBackend."""

    def test_temporal_store_preserves_history(self, monkeypatch):
        """Storing the same key twice produces two version records."""
        backend, session = _make_temporal_backend(monkeypatch)

        backend.store("config", "v1")
        backend.store("config", "v2")

        # Primary table: only latest value
        assert len(session.primary) == 1
        assert session.primary[0]["stored_value"] == '"v2"'

        # Versions table: both versions recorded
        config_versions = [r for r in session.versions if r.get("memory_key") == "config"]
        assert len(config_versions) == 2

    def test_temporal_retrieve_at_returns_version_at_timestamp(self, monkeypatch):
        """retrieve_at returns the value stored at or before the given timestamp."""
        backend, session = _make_temporal_backend(monkeypatch)

        # Inject two versions manually with distinct timestamps
        import json as _json
        t1 = "2025-01-01T10:00:00"
        t2 = "2025-01-01T11:00:00"
        session.versions = [
            {"memory_key": "cfg", "stored_value": '"v1"', "is_pickle": False, "version_ts": t1},
            {"memory_key": "cfg", "stored_value": '"v2"', "is_pickle": False, "version_ts": t2},
        ]

        # Ask for value at a point between t1 and t2
        as_of_between = datetime.fromisoformat("2025-01-01T10:30:00")
        result = backend.retrieve_at("cfg", as_of=as_of_between)
        assert result == "v1"

        # Ask for value at or after t2
        as_of_after = datetime.fromisoformat("2025-01-01T12:00:00")
        result2 = backend.retrieve_at("cfg", as_of=as_of_after)
        assert result2 == "v2"

    def test_temporal_off_by_default(self, monkeypatch):
        """Default SurrealDBBackend does NOT write to versions table."""
        backend, session = _make_temporal_backend(monkeypatch, temporal_enabled=False)

        backend.store("key", "value")
        backend.store("key", "updated")

        assert session.versions == []  # No versions table writes

    def test_history_returns_versions_in_reverse_order(self, monkeypatch):
        """history() returns versions newest-first."""
        backend, session = _make_temporal_backend(monkeypatch)

        t1 = "2025-01-01T09:00:00"
        t2 = "2025-01-01T10:00:00"
        t3 = "2025-01-01T11:00:00"
        session.versions = [
            {"memory_key": "k", "stored_value": '"a"', "is_pickle": False, "version_ts": t1},
            {"memory_key": "k", "stored_value": '"b"', "is_pickle": False, "version_ts": t2},
            {"memory_key": "k", "stored_value": '"c"', "is_pickle": False, "version_ts": t3},
        ]

        hist = backend.history("k", limit=10)
        assert len(hist) == 3
        assert hist[0]["value"] == "c"  # newest first
        assert hist[1]["value"] == "b"
        assert hist[2]["value"] == "a"

    def test_history_returns_empty_when_temporal_disabled(self, monkeypatch):
        """history() returns [] when temporal_enabled=False."""
        backend, session = _make_temporal_backend(monkeypatch, temporal_enabled=False)
        backend.store("key", "value")
        assert backend.history("key") == []

    def test_existing_retrieve_unchanged_by_temporal(self, monkeypatch):
        """Primary retrieve() always returns the latest value regardless of versions."""
        backend, session = _make_temporal_backend(monkeypatch)

        backend.store("x", "first")
        backend.store("x", "second")
        backend.store("x", "third")

        # Primary table should have been overwritten to latest only
        assert len(session.primary) == 1
        result = backend.retrieve("x")
        assert result == "third"

    def test_delete_does_not_affect_versions_table(self, monkeypatch):
        """delete() removes from primary table; versions table is preserved."""
        backend, session = _make_temporal_backend(monkeypatch)

        backend.store("item", "value_a")
        backend.store("item", "value_b")

        assert len(session.versions) == 2
        backend.delete("item")

        # Primary should be empty
        assert len(session.primary) == 0
        # Versions should still have both records
        assert len(session.versions) == 2

    def test_retrieve_at_falls_back_to_retrieve_when_temporal_disabled(self, monkeypatch):
        """retrieve_at() delegates to retrieve() when temporal is off."""
        backend, session = _make_temporal_backend(monkeypatch, temporal_enabled=False)
        session.primary = [{
            "memory_key": "k",
            "stored_value": '"current"',
            "is_pickle": False,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "expires_at": None,
        }]
        result = backend.retrieve_at("k", as_of=datetime(2024, 1, 1))
        assert result == "current"


# ---------------------------------------------------------------------------
# Increment 3: LiveMemorySubscriber tests
# ---------------------------------------------------------------------------


class TestLiveMemorySubscriber:
    """Tests for LiveMemorySubscriber — non-WebSocket rejection and subscription lifecycle."""

    def _make_fake_backend(self, url: str) -> object:
        """Return a minimal object that looks like SurrealDBBackend."""
        class _FakeBackend:
            pass

        fb = _FakeBackend()
        fb.url = url
        fb.namespace = "test"
        fb.database = "test"
        fb.username = "root"
        fb.password = "root"
        fb.skip_signin = True
        return fb

    def test_non_websocket_url_raises_value_error(self):
        """LiveMemorySubscriber raises ValueError for http:// URLs."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        backend = self._make_fake_backend("http://localhost:8000")
        with pytest.raises(ValueError, match="WebSocket"):
            LiveMemorySubscriber(backend)

    def test_websocket_url_is_accepted(self):
        """LiveMemorySubscriber accepts ws:// URLs without error at construction time."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        backend = self._make_fake_backend("ws://localhost:8000")
        subscriber = LiveMemorySubscriber(backend)
        assert subscriber._url == "ws://localhost:8000"
        assert subscriber._db is None  # not connected yet

    def test_wss_url_is_accepted(self):
        """LiveMemorySubscriber accepts wss:// (secure WebSocket) URLs."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        backend = self._make_fake_backend("wss://cloud.surrealdb.com")
        subscriber = LiveMemorySubscriber(backend)
        assert subscriber._url == "wss://cloud.surrealdb.com"

    def test_non_websocket_schemes_rejected(self):
        """LiveMemorySubscriber rejects memory://, file://, and plain URLs."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        for bad_url in ["memory", "file:///tmp/db", "surrealkv://local", ""]:
            backend = self._make_fake_backend(bad_url)
            with pytest.raises(ValueError, match="WebSocket"):
                LiveMemorySubscriber(backend)

    def test_default_reconnect_policy(self):
        """Default reconnect_attempts=3 and reconnect_delay_s=2.0."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        backend = self._make_fake_backend("ws://localhost:8000")
        subscriber = LiveMemorySubscriber(backend)
        assert subscriber._reconnect_attempts == 3
        assert subscriber._reconnect_delay_s == 2.0

    def test_custom_reconnect_policy(self):
        """Custom reconnect_attempts and reconnect_delay_s are applied."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        backend = self._make_fake_backend("ws://localhost:8000")
        subscriber = LiveMemorySubscriber(backend, reconnect_attempts=5, reconnect_delay_s=1.0)
        assert subscriber._reconnect_attempts == 5
        assert subscriber._reconnect_delay_s == 1.0

    def test_is_websocket_url_helper(self):
        """_is_websocket_url correctly identifies WebSocket schemes."""
        from superoptix.memory.live_memory import LiveMemorySubscriber

        assert LiveMemorySubscriber._is_websocket_url("ws://localhost:8000") is True
        assert LiveMemorySubscriber._is_websocket_url("wss://cloud.example.com") is True
        assert LiveMemorySubscriber._is_websocket_url("http://localhost:8000") is False
        assert LiveMemorySubscriber._is_websocket_url("memory") is False
        assert LiveMemorySubscriber._is_websocket_url("") is False


# ---------------------------------------------------------------------------
# Increment 3: SurrealDB MCP tool tests
# ---------------------------------------------------------------------------


class TestSurrealDBMCPTool:
    """Tests for SurrealDBMCPTool security model and row-limit enforcement."""

    def _make_tool(self, **kwargs) -> object:
        from superoptix.protocols.mcp.surrealdb_mcp import SurrealDBMCPTool

        defaults = dict(
            url="memory",
            namespace="test",
            database="test",
            username="root",
            password="root",
            skip_signin=True,
            max_rows=100,
            timeout_s=5.0,
        )
        defaults.update(kwargs)
        return SurrealDBMCPTool(**defaults)

    def test_select_statement_passes_allowlist(self):
        """SELECT is allowed by the allowlist without raising PermissionError."""
        from superoptix.protocols.mcp.surrealdb_mcp import SurrealDBMCPTool

        tool = self._make_tool()
        # Verify the allowlist check method directly (no DB needed)
        tool._enforce_allowlist("SELECT content FROM rag_documents;")  # must not raise

    def test_info_statement_passes_allowlist(self):
        """INFO statements are allowed."""
        tool = self._make_tool()
        tool._enforce_allowlist("INFO FOR TABLE rag_documents;")

    def test_return_statement_passes_allowlist(self):
        """RETURN statements are allowed."""
        tool = self._make_tool()
        tool._enforce_allowlist("RETURN 1 + 1;")

    def test_create_statement_raises_permission_error(self):
        """CREATE is rejected by the allowlist."""
        from superoptix.protocols.mcp.surrealdb_mcp import SurrealDBMCPTool

        tool = self._make_tool()
        with pytest.raises(PermissionError, match="SELECT|INFO|RETURN"):
            tool._enforce_allowlist("CREATE rag_documents SET content = 'hacked';")

    def test_delete_statement_raises_permission_error(self):
        """DELETE is rejected by the allowlist."""
        tool = self._make_tool()
        with pytest.raises(PermissionError):
            tool._enforce_allowlist("DELETE FROM rag_documents;")

    def test_define_statement_raises_permission_error(self):
        """DEFINE is rejected."""
        tool = self._make_tool()
        with pytest.raises(PermissionError):
            tool._enforce_allowlist("DEFINE TABLE secret;")

    def test_relate_statement_raises_permission_error(self):
        """RELATE is rejected."""
        tool = self._make_tool()
        with pytest.raises(PermissionError):
            tool._enforce_allowlist("RELATE node:a->edge->node:b;")

    def test_inject_limit_adds_limit_when_absent(self):
        """_inject_limit appends LIMIT clause when the query has none."""
        tool = self._make_tool(max_rows=50)
        result = tool._inject_limit("SELECT content FROM docs")
        assert "LIMIT 50" in result

    def test_inject_limit_respects_existing_limit(self):
        """_inject_limit does NOT add a second LIMIT when one is already present."""
        tool = self._make_tool(max_rows=100)
        sql = "SELECT content FROM docs LIMIT 5;"
        result = tool._inject_limit(sql)
        assert result.count("LIMIT") == 1  # only one LIMIT clause

    def test_inject_limit_does_not_modify_info_or_return(self):
        """_inject_limit only applies to SELECT statements."""
        tool = self._make_tool(max_rows=25)
        assert tool._inject_limit("INFO FOR TABLE rag_documents;") == "INFO FOR TABLE rag_documents;"
        assert tool._inject_limit("RETURN 1 + 1;") == "RETURN 1 + 1;"

    def test_allowlist_rejects_multi_statement_payload(self):
        """Allowlist blocks statement chaining (e.g. SELECT ...; DELETE ...)."""
        tool = self._make_tool()
        with pytest.raises(PermissionError, match="single statement"):
            tool._enforce_allowlist("SELECT * FROM docs; DELETE FROM docs;")

    def test_get_tool_definition_schema(self):
        """get_tool_definition returns a valid MCP tool schema."""
        tool = self._make_tool()
        defn = tool.get_tool_definition()
        assert defn["name"] == "surrealdb_query"
        assert "sql" in defn["input_schema"]["properties"]
        assert defn["input_schema"]["required"] == ["sql"]

    def test_from_config_factory(self):
        """from_config builds a tool from a config dict."""
        from superoptix.protocols.mcp.surrealdb_mcp import SurrealDBMCPTool

        config = {
            "url": "ws://localhost:8000",
            "namespace": "superoptix",
            "database": "agents",
            "username": "admin",
            "password": "secret",
            "skip_signin": False,
            "mcp_max_rows": 25,
            "mcp_timeout_s": 3.0,
        }
        tool = SurrealDBMCPTool.from_config(config)
        assert tool.url == "ws://localhost:8000"
        assert tool.namespace == "superoptix"
        assert tool.max_rows == 25
        assert tool.timeout_s == 3.0

    def test_allowlist_case_insensitive(self):
        """Allowlist check is case-insensitive."""
        tool = self._make_tool()
        # All caps
        tool._enforce_allowlist("SELECT * FROM docs;")
        # lowercase
        tool._enforce_allowlist("select * from docs;")
        # Mixed
        tool._enforce_allowlist("Select * From docs;")

    def test_surrealdb_query_in_valid_builtin_tools(self):
        """'surrealdb_query' is registered in SuperOptiX VALID_BUILTIN_TOOLS."""
        from superoptix.superspec.schema import SuperSpecXSchema

        assert "surrealdb_query" in SuperSpecXSchema.VALID_BUILTIN_TOOLS

    def test_surrealdb_query_builtin_tool_is_creatable(self):
        """Built-in tool registry can construct surrealdb_query."""
        from superoptix.tools.builtin_tools import create_tool

        tool = create_tool("surrealdb_query", url="memory", skip_signin=True)
        assert tool is not None


if __name__ == "__main__":
    pytest.main([__file__])
