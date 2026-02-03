"""Memory ranking utilities for context optimization."""

from datetime import datetime
from typing import Any, Dict, List, Tuple


class MemoryRanker:
    """
    Ranks memories by relevance, importance, and recency.

    Used by ContextWindowOptimizer to score memories for inclusion.
    """

    def __init__(self):
        """Initialize memory ranker."""
        self.ranking_history = []

    def rank_by_relevance(
        self,
        query: str,
        memories: List[Dict[str, Any]],
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Rank memories by relevance to query.

        Args:
                query: Search query
                memories: List of memories to rank

        Returns:
                List of (relevance_score, memory) tuples sorted by score
        """
        ranked = []

        for memory in memories:
            content = memory.get("content", "")
            score = self._calculate_text_relevance(query, content)
            ranked.append((score, memory))

        # Sort by score descending
        ranked.sort(reverse=True, key=lambda x: x[0])

        return ranked

    def rank_by_importance(
        self,
        memories: List[Dict[str, Any]],
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Rank memories by importance score."""
        ranked = []

        for memory in memories:
            importance = memory.get("importance", 0.5)
            ranked.append((importance, memory))

        ranked.sort(reverse=True, key=lambda x: x[0])

        return ranked

    def rank_by_recency(
        self,
        memories: List[Dict[str, Any]],
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Rank memories by recency (most recent = highest score)."""
        ranked = []
        now = datetime.now()

        for memory in memories:
            timestamp = memory.get("timestamp", datetime.min)
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = datetime.min

            age_seconds = (now - timestamp).total_seconds()
            # Convert to 0-1 score (1 = most recent)
            recency_score = 1.0 / (1.0 + age_seconds / 3600)  # Half-life of 1 hour

            ranked.append((recency_score, memory))

        ranked.sort(reverse=True, key=lambda x: x[0])

        return ranked

    def rank_hybrid(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        weights: Dict[str, float] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Rank memories using hybrid scoring (relevance + importance + recency).

        Args:
                query: Search query
                memories: List of memories
                weights: Custom weights for scoring components

        Returns:
                List of (hybrid_score, memory) tuples
        """
        if weights is None:
            weights = {"relevance": 0.4, "importance": 0.3, "recency": 0.3}

        ranked = []
        now = datetime.now()

        for memory in memories:
            # Get components
            content = memory.get("content", "")
            importance = memory.get("importance", 0.5)
            timestamp = memory.get("timestamp", datetime.min)

            # Calculate scores
            relevance = self._calculate_text_relevance(query, content)

            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = datetime.min

            age_seconds = (now - timestamp).total_seconds()
            recency = 1.0 / (1.0 + age_seconds / 3600)

            # Combine
            hybrid_score = (
                relevance * weights.get("relevance", 0.4)
                + importance * weights.get("importance", 0.3)
                + recency * weights.get("recency", 0.3)
            )

            ranked.append((hybrid_score, memory))

        ranked.sort(reverse=True, key=lambda x: x[0])

        return ranked

    def _calculate_text_relevance(self, query: str, content: str) -> float:
        """
        Calculate text relevance using simple keyword matching.

        Can be enhanced with:
        - TF-IDF scoring
        - Embeddings + cosine similarity
        - BM25 scoring
        """
        query_lower = query.lower()
        content_lower = content.lower()

        # Split into words
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())

        if not query_words:
            return 0.0

        # Jaccard similarity
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)

        if union == 0:
            return 0.0

        similarity = intersection / union

        # Boost for exact phrase match
        if query_lower in content_lower:
            similarity = min(1.0, similarity + 0.3)

        return similarity
