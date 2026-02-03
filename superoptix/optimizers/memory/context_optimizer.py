"""
Context Window Optimizer - GEPA-based optimization of which memories to include in context.

This optimizer learns:
- Which memories are most relevant for a given query
- How to balance recency vs relevance vs importance
- When to use full content vs summaries
- How to maximize context quality within token budget
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import dspy

from .memory_ranker import MemoryRanker
from .memory_summarizer import MemorySummarizer


class ContextWindowOptimizer:
    """
    GEPA-based optimizer for selecting memories to include in context window.

    Optimizes:
    - Which memories to include (relevance, importance, recency)
    - How much of each memory (full, summary, keywords)
    - Order of memories (chronological, relevance-based, hybrid)
    - Token budget allocation across memory types

    Example:
            optimizer = ContextWindowOptimizer(max_tokens=4096)

            # Optimize context for query
            optimized_context = optimizer.optimize_context(
                    query="What did the customer order last time?",
                    available_memories=all_memories,
                    task_type="customer_support"
            )
    """

    def __init__(
        self,
        max_tokens: int = 4096,
        enable_gepa: bool = True,
        min_relevance_score: float = 0.3,
        preserve_recency: bool = True,
    ):
        """
        Initialize context window optimizer.

        Args:
                max_tokens: Maximum tokens for context window
                enable_gepa: Use GEPA optimization (vs simple heuristics)
                min_relevance_score: Minimum relevance to include memory
                preserve_recency: Always include most recent memories
        """
        self.max_tokens = max_tokens
        self.enable_gepa = enable_gepa
        self.min_relevance_score = min_relevance_score
        self.preserve_recency = preserve_recency

        # Initialize components
        self.ranker = MemoryRanker()
        self.summarizer = MemorySummarizer()

        # GEPA components (if enabled)
        self.gepa_scorer = None
        if enable_gepa:
            self._init_gepa_scorer()

        # Statistics
        self.stats = {
            "total_optimizations": 0,
            "avg_tokens_used": 0,
            "avg_memories_selected": 0,
            "avg_relevance_score": 0,
        }

    def _init_gepa_scorer(self):
        """Initialize GEPA-based memory scoring."""
        try:
            # Define GEPA signature for memory relevance scoring
            class MemoryRelevanceScorer(dspy.Signature):
                """Score how relevant a memory is for answering a query."""

                query = dspy.InputField(desc="User query or current task")
                memory_content = dspy.InputField(desc="Memory content to evaluate")
                memory_metadata = dspy.InputField(
                    desc="Memory metadata (type, age, importance)"
                )
                task_context = dspy.InputField(
                    desc="Additional task context", prefix="Task:"
                )

                relevance_score = dspy.OutputField(
                    desc="Relevance score 0.0-1.0", prefix="Score:"
                )
                reasoning = dspy.OutputField(
                    desc="Brief explanation of score", prefix="Reasoning:"
                )

            self.gepa_scorer = dspy.ChainOfThought(MemoryRelevanceScorer)
        except Exception as e:
            print(f"Warning: Could not initialize GEPA scorer: {e}")
            self.gepa_scorer = None

    def optimize_context(
        self,
        query: str,
        available_memories: List[Dict[str, Any]],
        task_type: str = "general",
        preserve_n_recent: int = 3,
    ) -> Dict[str, Any]:
        """
        Optimize which memories to include in context window.

        Args:
                query: Current query or task
                available_memories: All memories that could be included
                task_type: Type of task (affects weighting)
                preserve_n_recent: Always include N most recent memories

        Returns:
                Dict with:
                        - selected_memories: List of memories to include
                        - total_tokens: Estimated tokens used
                        - strategy: Description of optimization strategy
                        - scores: Relevance scores for transparency
        """
        start_time = time.time()

        if not available_memories:
            return {
                "selected_memories": [],
                "total_tokens": 0,
                "strategy": "no_memories_available",
                "scores": {},
            }

        # Step 1: Score all memories
        scored_memories = self._score_memories(
            query=query,
            memories=available_memories,
            task_type=task_type,
        )

        # Step 2: Preserve most recent memories (if enabled)
        must_include = []
        if self.preserve_recency and preserve_n_recent > 0:
            must_include = self._get_most_recent(available_memories, preserve_n_recent)

        # Step 3: Select memories within token budget
        selected = self._select_within_budget(
            scored_memories=scored_memories,
            must_include=must_include,
            max_tokens=self.max_tokens,
        )

        # Step 4: Order selected memories
        ordered = self._order_memories(selected, strategy="recency_first")

        # Update statistics
        self._update_stats(ordered)

        optimization_time = time.time() - start_time

        return {
            "selected_memories": ordered,
            "total_tokens": sum(m.get("tokens", 0) for m in ordered),
            "strategy": f"gepa_optimized_{task_type}"
            if self.enable_gepa
            else "heuristic",
            "scores": {
                m.get("id", i): m.get("score", 0.0) for i, m in enumerate(ordered)
            },
            "optimization_time": optimization_time,
            "total_available": len(available_memories),
            "selected_count": len(ordered),
        }

    def _score_memories(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        task_type: str = "general",
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Score all memories for relevance.

        Returns:
                List of (score, memory) tuples sorted by score descending
        """
        scored = []

        for memory in memories:
            # Extract memory properties
            content = memory.get("content", "")
            importance = memory.get("importance", 0.5)
            timestamp = memory.get("timestamp", datetime.now())
            memory_type = memory.get("type", "unknown")

            # Calculate component scores
            relevance = self._calculate_relevance(query, content, task_type)
            recency = self._calculate_recency_score(timestamp)

            # Combine scores (GEPA learns these weights)
            if self.enable_gepa and self.gepa_scorer:
                try:
                    # Use GEPA to score
                    result = self.gepa_scorer(
                        query=query,
                        memory_content=content[:500],  # Truncate for efficiency
                        memory_metadata=f"Type:{memory_type}, Importance:{importance:.2f}",
                        task_context=task_type,
                    )
                    final_score = float(result.relevance_score)
                except Exception:
                    # Fallback to heuristic
                    final_score = self._heuristic_score(
                        relevance, importance, recency, task_type
                    )
            else:
                final_score = self._heuristic_score(
                    relevance, importance, recency, task_type
                )

            # Add score to memory
            memory_with_score = memory.copy()
            memory_with_score["score"] = final_score
            memory_with_score["relevance"] = relevance
            memory_with_score["recency"] = recency

            scored.append((final_score, memory_with_score))

        # Sort by score descending
        scored.sort(reverse=True, key=lambda x: x[0])

        return scored

    def _calculate_relevance(self, query: str, content: str, task_type: str) -> float:
        """Calculate semantic relevance between query and memory content."""
        # Simple keyword-based relevance (can be enhanced with embeddings)
        query_lower = query.lower()
        content_lower = content.lower()

        # Keyword overlap
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())

        if not query_words:
            return 0.0

        overlap = len(query_words & content_words)
        relevance = overlap / len(query_words)

        # Boost for exact phrase matches
        if query_lower in content_lower:
            relevance = min(1.0, relevance + 0.3)

        return relevance

    def _calculate_recency_score(self, timestamp: datetime) -> float:
        """Calculate recency score (1.0 = most recent, decays over time)."""
        now = datetime.now()
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                return 0.5  # Unknown age

        age_seconds = (now - timestamp).total_seconds()

        # Exponential decay: 1.0 at 0 seconds, 0.5 at 1 hour, 0.1 at 1 day
        decay_rate = 1 / 3600  # 1 hour half-life
        recency = max(0.0, 1.0 - (age_seconds * decay_rate))

        return recency

    def _heuristic_score(
        self,
        relevance: float,
        importance: float,
        recency: float,
        task_type: str,
    ) -> float:
        """
        Combine scores using heuristic weights.

        Task-specific weights:
        - Q&A: relevance >> recency
        - Conversation: recency >> relevance
        - Knowledge: importance >> recency
        """
        if task_type == "qa" or task_type == "question_answering":
            weights = {"relevance": 0.6, "importance": 0.3, "recency": 0.1}
        elif task_type == "conversation" or task_type == "customer_support":
            weights = {"relevance": 0.3, "importance": 0.2, "recency": 0.5}
        elif task_type == "knowledge" or task_type == "research":
            weights = {"relevance": 0.4, "importance": 0.5, "recency": 0.1}
        else:
            # General/balanced
            weights = {"relevance": 0.4, "importance": 0.3, "recency": 0.3}

        score = (
            relevance * weights["relevance"]
            + importance * weights["importance"]
            + recency * weights["recency"]
        )

        return score

    def _get_most_recent(
        self,
        memories: List[Dict[str, Any]],
        n: int,
    ) -> List[Dict[str, Any]]:
        """Get N most recent memories."""
        sorted_by_time = sorted(
            memories,
            key=lambda m: m.get("timestamp", datetime.min),
            reverse=True,
        )
        return sorted_by_time[:n]

    def _select_within_budget(
        self,
        scored_memories: List[Tuple[float, Dict[str, Any]]],
        must_include: List[Dict[str, Any]],
        max_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        Select memories to fit within token budget.

        Strategy:
        1. Always include must_include memories
        2. Add highest scoring memories until budget exhausted
        3. Use summaries if full content doesn't fit
        """
        selected = []
        total_tokens = 0
        must_include_ids = {id(m) for m in must_include}

        # First, add must_include memories
        for memory in must_include:
            memory_tokens = self._estimate_tokens(memory)

            if total_tokens + memory_tokens <= max_tokens:
                selected.append(memory)
                total_tokens += memory_tokens
            elif self.summarizer.can_summarize(memory):
                # Try summary instead
                summary = self.summarizer.summarize(
                    memory, target_tokens=memory_tokens // 2
                )
                summary_tokens = self._estimate_tokens(summary)
                if total_tokens + summary_tokens <= max_tokens:
                    selected.append(summary)
                    total_tokens += summary_tokens

        # Then, add highest scoring memories
        for score, memory in scored_memories:
            # Skip if already included
            if id(memory) in must_include_ids:
                continue

            # Skip if score too low
            if score < self.min_relevance_score:
                continue

            memory_tokens = self._estimate_tokens(memory)

            if total_tokens + memory_tokens <= max_tokens:
                selected.append(memory)
                total_tokens += memory_tokens
            elif self.summarizer.can_summarize(memory) and total_tokens < max_tokens:
                # Try summary if we have room
                remaining_tokens = max_tokens - total_tokens
                summary = self.summarizer.summarize(
                    memory, target_tokens=remaining_tokens
                )
                summary_tokens = self._estimate_tokens(summary)
                if summary_tokens <= remaining_tokens:
                    selected.append(summary)
                    total_tokens += summary_tokens

            # Stop if budget exhausted
            if total_tokens >= max_tokens:
                break

        return selected

    def _order_memories(
        self,
        memories: List[Dict[str, Any]],
        strategy: str = "recency_first",
    ) -> List[Dict[str, Any]]:
        """
        Order memories for context inclusion.

        Strategies:
        - recency_first: Most recent first (good for conversation)
        - relevance_first: Most relevant first (good for Q&A)
        - chronological: Oldest first (good for narratives)
        """
        if strategy == "recency_first":
            return sorted(
                memories,
                key=lambda m: m.get("timestamp", datetime.min),
                reverse=True,
            )
        elif strategy == "relevance_first":
            return sorted(
                memories,
                key=lambda m: m.get("score", 0.0),
                reverse=True,
            )
        elif strategy == "chronological":
            return sorted(
                memories,
                key=lambda m: m.get("timestamp", datetime.min),
            )
        else:
            return memories

    def _estimate_tokens(self, memory: Dict[str, Any]) -> int:
        """Estimate token count for memory content."""
        if "tokens" in memory:
            return memory["tokens"]

        content = memory.get("content", "")
        # Rough estimate: 1 token ≈ 4 characters
        estimated = len(content) // 4
        return max(1, estimated)

    def _update_stats(self, selected_memories: List[Dict[str, Any]]):
        """Update optimization statistics."""
        self.stats["total_optimizations"] += 1

        total_tokens = sum(self._estimate_tokens(m) for m in selected_memories)
        avg_score = (
            sum(m.get("score", 0.0) for m in selected_memories) / len(selected_memories)
            if selected_memories
            else 0.0
        )

        # Running average
        n = self.stats["total_optimizations"]
        self.stats["avg_tokens_used"] = (
            self.stats["avg_tokens_used"] * (n - 1) + total_tokens
        ) / n
        self.stats["avg_memories_selected"] = (
            self.stats["avg_memories_selected"] * (n - 1) + len(selected_memories)
        ) / n
        self.stats["avg_relevance_score"] = (
            self.stats["avg_relevance_score"] * (n - 1) + avg_score
        ) / n

    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_optimizations": 0,
            "avg_tokens_used": 0,
            "avg_memories_selected": 0,
            "avg_relevance_score": 0,
        }
