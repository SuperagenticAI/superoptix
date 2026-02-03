"""Long-term memory implementation with semantic search and knowledge storage."""

import hashlib
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .memory_backends import MemoryBackend, SQLiteBackend

try:
    import numpy as np

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class LongTermMemory:
    """Long-term memory with semantic search and knowledge storage."""

    def __init__(
        self,
        backend: Optional[MemoryBackend] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        enable_embeddings: bool = True,
    ):
        """
        Initialize long-term memory.

        Args:
            backend: Storage backend (defaults to SQLite)
            embedding_model: Model for generating embeddings
            enable_embeddings: Whether to enable semantic search
        """
        self.backend = backend or SQLiteBackend()
        self.enable_embeddings = enable_embeddings and EMBEDDINGS_AVAILABLE
        self._lock = threading.RLock()
        self.embedding_model_name = embedding_model

        # Initialize embedding model if available (lazy loading)
        self.embedding_model = None
        if self.enable_embeddings:
            self._load_embedding_model()

        # Knowledge categories
        self.categories = {
            "facts": "Factual information and data",
            "procedures": "Step-by-step procedures and workflows",
            "experiences": "Past experiences and outcomes",
            "preferences": "User preferences and settings",
            "relationships": "Entity relationships and connections",
            "patterns": "Identified patterns and insights",
        }

    def _load_embedding_model(self):
        """Lazy load the embedding model only when needed."""
        if self.embedding_model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        except ImportError:
            print(
                "Warning: sentence_transformers not available. Semantic search disabled."
            )
            self.enable_embeddings = False
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            self.enable_embeddings = False

    def store_knowledge(
        self,
        content: str,
        category: str = "facts",
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store knowledge in long-term memory.

        Args:
            content: The knowledge content
            category: Knowledge category
            metadata: Additional metadata
            tags: Tags for categorization

        Returns:
            Knowledge ID
        """
        try:
            with self._lock:
                # Generate unique ID
                knowledge_id = self._generate_id(content)

                # Prepare knowledge item
                knowledge_item = {
                    "id": knowledge_id,
                    "content": content,
                    "category": category,
                    "metadata": metadata or {},
                    "tags": tags or [],
                    "created_at": datetime.now().isoformat(),
                    "access_count": 0,
                    "last_accessed": None,
                    "importance_score": metadata.get("importance", 1.0)
                    if metadata
                    else 1.0,
                }

                # Generate embedding if enabled
                if self.enable_embeddings:
                    # Ensure embedding model is loaded
                    self._load_embedding_model()
                    if self.embedding_model:
                        try:
                            embedding = self.embedding_model.encode(content).tolist()
                            knowledge_item["embedding"] = embedding
                        except Exception as e:
                            print(f"Warning: Could not generate embedding: {e}")

                # Store in backend
                key = f"knowledge:{knowledge_id}"
                success = self.backend.store(key, knowledge_item)

                if success:
                    # Update category index
                    self._update_category_index(category, knowledge_id)
                    # Update tag index
                    for tag in tags or []:
                        self._update_tag_index(tag, knowledge_id)

                return knowledge_id if success else None

        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return None

    def retrieve_knowledge(self, knowledge_id: str) -> Optional[Dict]:
        """Retrieve knowledge by ID."""
        try:
            with self._lock:
                key = f"knowledge:{knowledge_id}"
                knowledge_item = self.backend.retrieve(key)

                if knowledge_item:
                    # Update access information
                    knowledge_item["access_count"] += 1
                    knowledge_item["last_accessed"] = datetime.now().isoformat()
                    self.backend.store(key, knowledge_item)

                return knowledge_item

        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return None

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.3,
    ) -> List[Dict]:
        """
        Search knowledge using semantic similarity or keyword matching.

        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of matching knowledge items with scores
        """
        try:
            with self._lock:
                results = []

                # Get all knowledge items
                all_keys = self.backend.keys("knowledge:*")

                for key in all_keys:
                    knowledge_item = self.backend.retrieve(key)
                    if not knowledge_item:
                        continue

                    # Apply filters
                    if category and knowledge_item.get("category") != category:
                        continue

                    if tags:
                        item_tags = set(knowledge_item.get("tags", []))
                        if not item_tags.intersection(set(tags)):
                            continue

                    # Calculate similarity
                    if self.enable_embeddings and "embedding" in knowledge_item:
                        similarity = self._calculate_semantic_similarity(
                            query, knowledge_item
                        )
                    else:
                        similarity = self._calculate_keyword_similarity(
                            query, knowledge_item
                        )

                    if similarity >= min_similarity:
                        result_item = knowledge_item.copy()
                        result_item["similarity_score"] = similarity
                        results.append(result_item)

                # Sort by similarity and importance
                results.sort(
                    key=lambda x: (x["similarity_score"], x["importance_score"]),
                    reverse=True,
                )

                return results[:limit]

        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []

    def get_knowledge_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Get knowledge items by category."""
        try:
            with self._lock:
                category_key = f"category_index:{category}"
                knowledge_ids = self.backend.retrieve(category_key) or []

                results = []
                for knowledge_id in knowledge_ids[:limit]:
                    knowledge_item = self.retrieve_knowledge(knowledge_id)
                    if knowledge_item:
                        results.append(knowledge_item)

                return results

        except Exception as e:
            print(f"Error getting knowledge by category: {e}")
            return []

    def get_knowledge_by_tags(self, tags: List[str], limit: int = 20) -> List[Dict]:
        """Get knowledge items by tags."""
        try:
            with self._lock:
                matching_ids = set()

                for tag in tags:
                    tag_key = f"tag_index:{tag}"
                    tag_ids = self.backend.retrieve(tag_key) or []
                    if not matching_ids:
                        matching_ids = set(tag_ids)
                    else:
                        matching_ids = matching_ids.intersection(set(tag_ids))

                results = []
                for knowledge_id in list(matching_ids)[:limit]:
                    knowledge_item = self.retrieve_knowledge(knowledge_id)
                    if knowledge_item:
                        results.append(knowledge_item)

                return results

        except Exception as e:
            print(f"Error getting knowledge by tags: {e}")
            return []

    def update_knowledge(self, knowledge_id: str, updates: Dict) -> bool:
        """Update knowledge item."""
        try:
            with self._lock:
                knowledge_item = self.retrieve_knowledge(knowledge_id)
                if not knowledge_item:
                    return False

                # Update fields
                for key, value in updates.items():
                    if key not in ["id", "created_at"]:  # Protect immutable fields
                        knowledge_item[key] = value

                knowledge_item["updated_at"] = datetime.now().isoformat()

                # Regenerate embedding if content changed
                if (
                    "content" in updates
                    and self.enable_embeddings
                    and self.embedding_model
                ):
                    try:
                        embedding = self.embedding_model.encode(
                            updates["content"]
                        ).tolist()
                        knowledge_item["embedding"] = embedding
                    except Exception as e:
                        print(f"Warning: Could not regenerate embedding: {e}")

                # Store updated item
                key = f"knowledge:{knowledge_id}"
                return self.backend.store(key, knowledge_item)

        except Exception as e:
            print(f"Error updating knowledge: {e}")
            return False

    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete knowledge item."""
        try:
            with self._lock:
                knowledge_item = self.retrieve_knowledge(knowledge_id)
                if not knowledge_item:
                    return False

                # Remove from indices
                category = knowledge_item.get("category")
                if category:
                    self._remove_from_category_index(category, knowledge_id)

                tags = knowledge_item.get("tags", [])
                for tag in tags:
                    self._remove_from_tag_index(tag, knowledge_id)

                # Delete main item
                key = f"knowledge:{knowledge_id}"
                return self.backend.delete(key)

        except Exception as e:
            print(f"Error deleting knowledge: {e}")
            return False

    def get_related_knowledge(self, knowledge_id: str, limit: int = 5) -> List[Dict]:
        """Get knowledge items related to the given item."""
        try:
            knowledge_item = self.retrieve_knowledge(knowledge_id)
            if not knowledge_item:
                return []

            # Search for similar content
            content = knowledge_item.get("content", "")
            category = knowledge_item.get("category")
            tags = knowledge_item.get("tags", [])

            results = self.search_knowledge(
                query=content,
                category=category,
                tags=tags,
                limit=limit + 1,  # +1 because we'll filter out the original
            )

            # Filter out the original item
            related = [item for item in results if item["id"] != knowledge_id]
            return related[:limit]

        except Exception as e:
            print(f"Error getting related knowledge: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            with self._lock:
                all_keys = self.backend.keys("knowledge:*")
                total_items = len(all_keys)

                if total_items == 0:
                    return {
                        "total_items": 0,
                        "categories": {},
                        "total_tags": 0,
                        "avg_importance": 0,
                        "embeddings_enabled": self.enable_embeddings,
                    }

                # Collect statistics
                categories = {}
                all_tags = set()
                importance_scores = []

                for key in all_keys:
                    item = self.backend.retrieve(key)
                    if item:
                        category = item.get("category", "unknown")
                        categories[category] = categories.get(category, 0) + 1

                        tags = item.get("tags", [])
                        all_tags.update(tags)

                        importance = item.get("importance_score", 1.0)
                        importance_scores.append(importance)

                avg_importance = (
                    sum(importance_scores) / len(importance_scores)
                    if importance_scores
                    else 0
                )

                return {
                    "total_items": total_items,
                    "categories": categories,
                    "total_tags": len(all_tags),
                    "avg_importance": avg_importance,
                    "embeddings_enabled": self.enable_embeddings,
                }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content."""
        timestamp = datetime.now().isoformat()
        combined = f"{content}:{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _calculate_semantic_similarity(self, query: str, knowledge_item: Dict) -> float:
        """Calculate semantic similarity using embeddings."""
        try:
            # Ensure embedding model is loaded
            self._load_embedding_model()

            if not self.embedding_model or "embedding" not in knowledge_item:
                return 0.0

            query_embedding = self.embedding_model.encode(query)
            item_embedding = np.array(knowledge_item["embedding"])

            # Cosine similarity
            similarity = np.dot(query_embedding, item_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding)
            )

            return float(similarity)

        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0

    def _calculate_keyword_similarity(self, query: str, knowledge_item: Dict) -> float:
        """Calculate keyword-based similarity."""
        try:
            content = knowledge_item.get("content", "").lower()
            query_lower = query.lower()

            # Simple keyword matching
            query_words = set(query_lower.split())
            content_words = set(content.split())

            if not query_words:
                return 0.0

            intersection = query_words.intersection(content_words)
            similarity = len(intersection) / len(query_words)

            return similarity

        except Exception as e:
            print(f"Error calculating keyword similarity: {e}")
            return 0.0

    def _update_category_index(self, category: str, knowledge_id: str):
        """Update category index."""
        try:
            key = f"category_index:{category}"
            current_ids = self.backend.retrieve(key) or []
            if knowledge_id not in current_ids:
                current_ids.append(knowledge_id)
                self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error updating category index: {e}")

    def _update_tag_index(self, tag: str, knowledge_id: str):
        """Update tag index."""
        try:
            key = f"tag_index:{tag}"
            current_ids = self.backend.retrieve(key) or []
            if knowledge_id not in current_ids:
                current_ids.append(knowledge_id)
                self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error updating tag index: {e}")

    def _remove_from_category_index(self, category: str, knowledge_id: str):
        """Remove from category index."""
        try:
            key = f"category_index:{category}"
            current_ids = self.backend.retrieve(key) or []
            if knowledge_id in current_ids:
                current_ids.remove(knowledge_id)
                self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error removing from category index: {e}")

    def _remove_from_tag_index(self, tag: str, knowledge_id: str):
        """Remove from tag index."""
        try:
            key = f"tag_index:{tag}"
            current_ids = self.backend.retrieve(key) or []
            if knowledge_id in current_ids:
                current_ids.remove(knowledge_id)
                self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error removing from tag index: {e}")

    def clear(self):
        """Clear all long-term memory."""
        try:
            with self._lock:
                # Clear all knowledge items
                knowledge_keys = self.backend.keys("knowledge:*")
                for key in knowledge_keys:
                    self.backend.delete(key)

                # Clear indices
                category_keys = self.backend.keys("category_index:*")
                for key in category_keys:
                    self.backend.delete(key)

                tag_keys = self.backend.keys("tag_index:*")
                for key in tag_keys:
                    self.backend.delete(key)

        except Exception as e:
            print(f"Error clearing long-term memory: {e}")
