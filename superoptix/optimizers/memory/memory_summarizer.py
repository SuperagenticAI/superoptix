"""Memory summarization for context compression."""

from typing import Any, Dict


class MemorySummarizer:
    """
    Summarizes memories to fit within token budgets.

    Strategies:
    - Extract keywords (fast)
    - Generate summary (LLM-based)
    - Compress to key facts (structured)
    """

    def __init__(self):
        """Initialize memory summarizer."""
        pass

    def can_summarize(self, memory: Dict[str, Any]) -> bool:
        """
        Check if memory can be summarized.

        Args:
                memory: Memory to check

        Returns:
                True if summarizable (has sufficient content)
        """
        content = memory.get("content", "")

        # Need at least 50 characters to be worth summarizing
        if len(content) < 50:
            return False

        # Check memory type
        memory_type = memory.get("type", "")

        # Some types shouldn't be summarized (e.g., code, data)
        non_summarizable_types = ["code", "data", "json", "binary"]
        if memory_type in non_summarizable_types:
            return False

        return True

    def summarize(
        self,
        memory: Dict[str, Any],
        target_tokens: int = 100,
        strategy: str = "keywords",
    ) -> Dict[str, Any]:
        """
        Summarize memory to target token count.

        Args:
                memory: Memory to summarize
                target_tokens: Target token count
                strategy: Summarization strategy ("keywords", "summary", "facts")

        Returns:
                Summarized memory
        """
        content = memory.get("content", "")

        if strategy == "keywords":
            summarized_content = self._extract_keywords(content, target_tokens)
        elif strategy == "summary":
            summarized_content = self._generate_summary(content, target_tokens)
        elif strategy == "facts":
            summarized_content = self._extract_key_facts(content, target_tokens)
        else:
            # Default: truncate
            summarized_content = self._truncate(content, target_tokens)

        # Create summarized memory
        summarized = memory.copy()
        summarized["content"] = summarized_content
        summarized["is_summary"] = True
        summarized["original_length"] = len(content)
        summarized["summary_length"] = len(summarized_content)

        # Update token estimate
        summarized["tokens"] = self._estimate_tokens(summarized_content)

        return summarized

    def _extract_keywords(self, content: str, target_tokens: int) -> str:
        """
        Extract keywords from content.

        Fast strategy: Select important words/phrases.
        """
        # Simple keyword extraction (can be enhanced with TF-IDF, etc.)
        words = content.split()

        # Target approximately target_tokens * 4 characters
        target_chars = target_tokens * 4

        # Take first N words
        selected_words = []
        current_chars = 0

        for word in words:
            if current_chars + len(word) + 1 <= target_chars:
                selected_words.append(word)
                current_chars += len(word) + 1
            else:
                break

        keywords = " ".join(selected_words)

        # Add ellipsis if truncated
        if len(keywords) < len(content):
            keywords += "..."

        return keywords

    def _generate_summary(self, content: str, target_tokens: int) -> str:
        """
        Generate natural language summary.

        Would use LLM here in production, but using simple extraction for now.
        """
        # TODO: Implement LLM-based summarization
        # For now, use keyword extraction
        return self._extract_keywords(content, target_tokens)

    def _extract_key_facts(self, content: str, target_tokens: int) -> str:
        """
        Extract key facts in structured format.

        Example: "User: John | Order: #12345 | Issue: Shipping delay"
        """
        # Simple fact extraction (can be enhanced with NER, etc.)
        sentences = content.split(". ")

        # Take first sentence as primary fact
        if sentences:
            key_fact = sentences[0]
            target_chars = target_tokens * 4
            if len(key_fact) > target_chars:
                key_fact = key_fact[:target_chars] + "..."
            return key_fact

        return self._truncate(content, target_tokens)

    def _truncate(self, content: str, target_tokens: int) -> str:
        """Simple truncation to target tokens."""
        target_chars = target_tokens * 4

        if len(content) <= target_chars:
            return content

        return content[:target_chars] + "..."

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text."""
        # Rough estimate: 1 token ≈ 4 characters
        return max(1, len(text) // 4)
