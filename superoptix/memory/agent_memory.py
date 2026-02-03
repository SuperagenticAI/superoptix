"""Main agent memory class that integrates all memory components."""

import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .context_manager import ContextManager
from .episodic_memory import EpisodicMemory
from .long_term_memory import LongTermMemory
from .memory_backends import MemoryBackend, SQLiteBackend
from .short_term_memory import ShortTermMemory

# Import context window optimizer (if available)
try:
    from ..optimizers.memory import ContextWindowOptimizer

    MEMORY_OPTIMIZATION_AVAILABLE = True
except ImportError:
    MEMORY_OPTIMIZATION_AVAILABLE = False
    ContextWindowOptimizer = None


class AgentMemory:
    """
    Unified memory system for agents that integrates short-term, long-term,
    episodic memory, and context management.
    """

    def __init__(
        self,
        agent_id: str,
        backend: Optional[MemoryBackend] = None,
        short_term_capacity: int = 100,
        enable_embeddings: bool = True,
        enable_context_optimization: bool = True,
        max_context_tokens: int = 4096,
    ):
        """
        Initialize agent memory system.

        Args:
            agent_id: Unique agent identifier
            backend: Storage backend (defaults to SQLite)
            short_term_capacity: Short-term memory capacity
            enable_embeddings: Enable semantic search in long-term memory
            enable_context_optimization: Enable GEPA-based context window optimization
            max_context_tokens: Maximum tokens for context window
        """
        self.agent_id = agent_id
        self.backend = backend or SQLiteBackend()
        self._lock = threading.RLock()

        # Initialize memory components
        self.short_term = ShortTermMemory(capacity=short_term_capacity)
        self.long_term = LongTermMemory(
            backend=self.backend, enable_embeddings=enable_embeddings
        )
        self.episodic = EpisodicMemory(backend=self.backend)
        self.context = ContextManager(
            agent_id=agent_id,
            short_term_memory=self.short_term,
            long_term_memory=self.long_term,
            episodic_memory=self.episodic,
            backend=self.backend,
        )

        # Memory statistics
        self._interaction_count = 0
        self._last_cleanup = datetime.now()

        # Context window optimization (NEW!)
        self.enable_context_optimization = enable_context_optimization
        self.max_context_tokens = max_context_tokens
        self.context_optimizer = None

        if enable_context_optimization and MEMORY_OPTIMIZATION_AVAILABLE:
            try:
                self.context_optimizer = ContextWindowOptimizer(
                    max_tokens=max_context_tokens,
                    enable_gepa=True,
                )
                print(
                    f"✅ Memory context optimization enabled (max: {max_context_tokens} tokens)"
                )
            except Exception as e:
                print(f"⚠️  Context optimization unavailable: {e}")
                self.context_optimizer = None

    def remember(
        self,
        content: str,
        memory_type: str = "short",
        category: str = "general",
        importance: float = 1.0,
        tags: Optional[List[str]] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store information in memory.

        Args:
            content: Content to remember
            memory_type: "short", "long", or "context"
            category: Memory category
            importance: Importance score (0.0-1.0)
            tags: Tags for categorization
            ttl: Time to live in seconds (for short-term memory)

        Returns:
            Success status
        """
        try:
            with self._lock:
                if memory_type == "short":
                    key = f"memory_{datetime.now().timestamp()}"
                    return self.short_term.store(
                        key=key, value=content, priority=int(importance * 10), ttl=ttl
                    )

                elif memory_type == "long":
                    knowledge_id = self.long_term.store_knowledge(
                        content=content,
                        category=category,
                        metadata={"importance": importance},
                        tags=tags or [],
                    )
                    return knowledge_id is not None

                elif memory_type == "context":
                    return self.context.set_context(
                        scope=category, key="content", value=content
                    )

                return False

        except Exception as e:
            print(f"Error storing memory: {e}")
            return False

    def recall(
        self,
        query: str,
        memory_type: str = "all",
        limit: int = 10,
        min_similarity: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Recall information from memory.

        Args:
            query: Search query
            memory_type: "short", "long", "episodic", or "all"
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of memory items
        """
        try:
            with self._lock:
                results = []

                if memory_type in ["short", "all"]:
                    # Search short-term memory
                    for key, value in self.short_term.items():
                        if isinstance(value, str) and query.lower() in value.lower():
                            results.append(
                                {
                                    "type": "short_term",
                                    "content": value,
                                    "key": key,
                                    "similarity": self._calculate_simple_similarity(
                                        query, value
                                    ),
                                }
                            )

                if memory_type in ["long", "all"]:
                    # Search long-term memory
                    knowledge_results = self.long_term.search_knowledge(
                        query=query, limit=limit, min_similarity=min_similarity
                    )

                    for item in knowledge_results:
                        results.append(
                            {
                                "type": "long_term",
                                "content": item["content"],
                                "id": item["id"],
                                "category": item.get("category"),
                                "tags": item.get("tags", []),
                                "similarity": item.get("similarity_score", 0),
                            }
                        )

                if memory_type in ["episodic", "all"]:
                    # Search episodic memory
                    episodes = self.episodic.search_episodes(query=query, limit=limit)

                    for episode in episodes:
                        results.append(
                            {
                                "type": "episodic",
                                "content": f"{episode.title}: {episode.description}",
                                "id": episode.id,
                                "status": episode.status,
                                "tags": episode.tags,
                                "similarity": self._calculate_simple_similarity(
                                    query, episode.title + " " + episode.description
                                ),
                            }
                        )

                # Sort by similarity
                results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                return results[:limit]

        except Exception as e:
            print(f"Error recalling memory: {e}")
            return []

    def get_optimized_context(
        self,
        query: str,
        task_type: str = "general",
        preserve_n_recent: int = 3,
    ) -> Dict[str, Any]:
        """
        Get optimized context for query using GEPA-based selection.

        This method uses the ContextWindowOptimizer to select which memories
        to include in the context window based on relevance, importance, and
        recency, while staying within token budget.

        Args:
            query: Current query or task
            task_type: Type of task (affects scoring weights)
            preserve_n_recent: Always include N most recent memories

        Returns:
            Dict with:
                - context_string: Formatted context string
                - selected_memories: List of selected memories
                - optimization_info: Stats about optimization

        Example:
            context_info = memory.get_optimized_context(
                query="What did the customer order?",
                task_type="customer_support"
            )
            context_string = context_info["context_string"]
            # Use context_string in your prompt
        """
        try:
            # Get all available memories
            all_memories = self.recall(query="", memory_type="all", limit=100)

            # Add timestamps and importance if missing
            for memory in all_memories:
                if "timestamp" not in memory:
                    memory["timestamp"] = datetime.now()
                if "importance" not in memory:
                    memory["importance"] = 0.5

            # Use context optimizer if available
            if self.context_optimizer:
                optimization_result = self.context_optimizer.optimize_context(
                    query=query,
                    available_memories=all_memories,
                    task_type=task_type,
                    preserve_n_recent=preserve_n_recent,
                )

                selected_memories = optimization_result["selected_memories"]
                optimization_info = {
                    "method": "gepa_optimized",
                    "total_available": optimization_result["total_available"],
                    "selected_count": optimization_result["selected_count"],
                    "total_tokens": optimization_result["total_tokens"],
                    "strategy": optimization_result["strategy"],
                    "scores": optimization_result.get("scores", {}),
                }
            else:
                # Fallback: Simple selection (most relevant)
                selected_memories = all_memories[: min(10, len(all_memories))]
                optimization_info = {
                    "method": "simple_selection",
                    "selected_count": len(selected_memories),
                }

            # Format as context string
            context_string = self._format_memories_as_context(selected_memories)

            return {
                "context_string": context_string,
                "selected_memories": selected_memories,
                "optimization_info": optimization_info,
            }

        except Exception as e:
            print(f"Error getting optimized context: {e}")
            return {
                "context_string": "",
                "selected_memories": [],
                "optimization_info": {"method": "error", "error": str(e)},
            }

    def _format_memories_as_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories as a context string for prompts."""
        if not memories:
            return ""

        context_parts = ["## Relevant Memories\n"]

        for i, memory in enumerate(memories, 1):
            memory_type = memory.get("type", "unknown")
            content = memory.get("content", "")

            # Add memory with type indicator
            context_parts.append(f"\n### Memory {i} ({memory_type})")
            context_parts.append(f"{content}\n")

        return "\n".join(context_parts)

    def start_interaction(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new interaction episode.

        Args:
            context: Initial context for the interaction

        Returns:
            Episode ID
        """
        try:
            with self._lock:
                self._interaction_count += 1

                episode_id = self.episodic.start_episode(
                    title=f"Interaction {self._interaction_count}",
                    description=f"User interaction session {self._interaction_count}",
                    context=context or {},
                    tags=["interaction", "user_session"],
                    importance_score=0.7,
                )

                # Update context
                self.context.set_context("session", "current_episode", episode_id)
                self.context.set_context(
                    "session", "interaction_count", self._interaction_count
                )

                return episode_id

        except Exception as e:
            print(f"Error starting interaction: {e}")
            return None

    def end_interaction(self, outcome: Optional[Dict[str, Any]] = None) -> bool:
        """
        End the current interaction episode.

        Args:
            outcome: Interaction outcome

        Returns:
            Success status
        """
        try:
            with self._lock:
                episode_id = self.context.get_context("session", "current_episode")
                if not episode_id:
                    return False

                success = self.episodic.end_episode(
                    episode_id=episode_id,
                    outcome=outcome,
                    status="completed"
                    if outcome and outcome.get("success")
                    else "ended",
                )

                # Clear current episode from context
                self.context.set_context("session", "current_episode", None)

                return success

        except Exception as e:
            print(f"Error ending interaction: {e}")
            return False

    def add_interaction_event(
        self, event_type: str, description: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an event to the current interaction episode.

        Args:
            event_type: Type of event
            description: Event description
            data: Event data

        Returns:
            Success status
        """
        try:
            episode_id = self.context.get_context("session", "current_episode")
            if not episode_id:
                return False

            return self.episodic.add_event(
                episode_id=episode_id,
                event_type=event_type,
                description=description,
                data=data,
            )

        except Exception as e:
            print(f"Error adding interaction event: {e}")
            return False

    def get_conversation_context(self, last_n: int = 10) -> Dict[str, Any]:
        """
        Get current conversation context.

        Args:
            last_n: Number of recent messages to include

        Returns:
            Conversation context
        """
        try:
            context = {
                "recent_conversation": self.short_term.get_conversation_history(last_n),
                "working_memory": self.short_term.get_context_summary(),
                "session_context": self.context.get_context("session"),
                "global_context": self.context.get_context("global"),
                "current_episode": self.context.get_context(
                    "session", "current_episode"
                ),
            }

            return context

        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return {}

    def learn_from_interaction(
        self, insights: List[str], patterns: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Learn from the current interaction and store insights.

        Args:
            insights: List of insights learned
            patterns: Identified patterns

        Returns:
            Success status
        """
        try:
            with self._lock:
                success_count = 0

                # Store insights in long-term memory
                for insight in insights:
                    knowledge_id = self.long_term.store_knowledge(
                        content=insight,
                        category="insights",
                        metadata={"source": "interaction", "agent_id": self.agent_id},
                        tags=["insight", "learned", self.agent_id],
                    )
                    if knowledge_id:
                        success_count += 1

                # Store patterns in global context
                if patterns:
                    current_patterns = (
                        self.context.get_context("global", "learned_patterns") or {}
                    )
                    current_patterns.update(patterns)
                    self.context.set_context(
                        "global", "learned_patterns", current_patterns
                    )

                return success_count > 0

        except Exception as e:
            print(f"Error learning from interaction: {e}")
            return False

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of memory state."""
        try:
            with self._lock:
                return {
                    "agent_id": self.agent_id,
                    "interaction_count": self._interaction_count,
                    "short_term_memory": self.short_term.get_stats(),
                    "long_term_memory": self.long_term.get_statistics(),
                    "episodic_memory": self.episodic.get_statistics(),
                    "context_summary": self.context.get_context_summary(),
                    "last_cleanup": self._last_cleanup.isoformat(),
                }

        except Exception as e:
            print(f"Error getting memory summary: {e}")
            return {}

    def cleanup_memory(self) -> Dict[str, int]:
        """
        Perform memory cleanup operations.

        Returns:
            Cleanup statistics
        """
        try:
            with self._lock:
                stats = {"expired_short_term": 0, "expired_contexts": 0}

                # Cleanup short-term memory
                stats["expired_short_term"] = self.short_term.cleanup_expired()

                # Cleanup contexts (if context manager has cleanup method)
                if hasattr(self.context, "cleanup_expired_contexts"):
                    stats["expired_contexts"] = self.context.cleanup_expired_contexts()

                self._last_cleanup = datetime.now()

                return stats

        except Exception as e:
            print(f"Error cleaning up memory: {e}")
            return {}

    def save_memory_state(self) -> bool:
        """Save current memory state to persistent storage."""
        try:
            with self._lock:
                # Save context to long-term memory
                context_summary = self.context.get_context_summary()

                knowledge_id = self.long_term.store_knowledge(
                    content=f"Memory state snapshot: {context_summary}",
                    category="memory_state",
                    metadata={
                        "agent_id": self.agent_id,
                        "timestamp": datetime.now().isoformat(),
                        "interaction_count": self._interaction_count,
                    },
                    tags=["memory_state", "snapshot", self.agent_id],
                )

                return knowledge_id is not None

        except Exception as e:
            print(f"Error saving memory state: {e}")
            return False

    def _calculate_simple_similarity(self, query: str, text: str) -> float:
        """Calculate simple keyword-based similarity."""
        try:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())

            if not query_words:
                return 0.0

            intersection = query_words.intersection(text_words)
            return len(intersection) / len(query_words)

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def clear_all_memory(self):
        """Clear all memory components (use with caution)."""
        try:
            with self._lock:
                self.short_term.clear()
                self.long_term.clear()
                self.episodic.clear()
                self.context.clear_context()
                self._interaction_count = 0

        except Exception as e:
            print(f"Error clearing all memory: {e}")

    def get_related_memories(
        self, content: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get memories related to the given content."""
        try:
            # Get related from long-term memory
            related_knowledge = self.long_term.search_knowledge(
                query=content, limit=limit, min_similarity=0.2
            )

            results = []
            for item in related_knowledge:
                results.append(
                    {
                        "type": "knowledge",
                        "content": item["content"],
                        "category": item.get("category"),
                        "similarity": item.get("similarity_score", 0),
                    }
                )

            return results

        except Exception as e:
            print(f"Error getting related memories: {e}")
            return []
