"""Tests for the enhanced memory system."""

import os
import tempfile

import pytest

from superoptix.memory import (
    AgentMemory,
    ContextManager,
    EpisodicMemory,
    FileBackend,
    LongTermMemory,
    ShortTermMemory,
    SQLiteBackend,
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


if __name__ == "__main__":
    pytest.main([__file__])
