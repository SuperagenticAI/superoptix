"""Short-term memory implementation for agents."""

import threading
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class ShortTermMemory:
    """Short-term memory with LRU eviction and conversation history."""

    def __init__(self, capacity: int = 100, retention_policy: str = "lru"):
        """
        Initialize short-term memory.

        Args:
            capacity: Maximum number of items to store
            retention_policy: "lru", "fifo", or "priority"
        """
        self.capacity = capacity
        self.retention_policy = retention_policy
        self._data = OrderedDict()
        self._priorities = {}  # For priority-based retention
        self._access_times = {}
        self._lock = threading.RLock()

        # Conversation history
        self._conversation_history = []
        self._max_conversation_length = 50

        # Working memory for current context
        self._working_memory = {}

    def store(
        self, key: str, value: Any, priority: int = 1, ttl: Optional[int] = None
    ) -> bool:
        """
        Store a value in short-term memory.

        Args:
            key: Storage key
            value: Value to store
            priority: Priority for retention (higher = more important)
            ttl: Time to live in seconds
        """
        try:
            with self._lock:
                current_time = time.time()

                # Calculate expiry time if TTL is set
                expires_at = current_time + ttl if ttl else None

                # Store the item
                item = {
                    "value": value,
                    "created_at": current_time,
                    "expires_at": expires_at,
                    "access_count": 1,
                    "last_accessed": current_time,
                }

                # If key exists, update it
                if key in self._data:
                    self._data[key] = item
                    self._data.move_to_end(key)  # Move to end for LRU
                else:
                    # Check capacity and evict if necessary
                    if len(self._data) >= self.capacity:
                        self._evict()

                    self._data[key] = item

                self._priorities[key] = priority
                self._access_times[key] = current_time

                return True

        except Exception as e:
            print(f"Error storing in short-term memory: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from short-term memory."""
        try:
            with self._lock:
                if key not in self._data:
                    return None

                item = self._data[key]
                current_time = time.time()

                # Check if item has expired
                if item.get("expires_at") and current_time > item["expires_at"]:
                    self.delete(key)
                    return None

                # Update access information
                item["access_count"] += 1
                item["last_accessed"] = current_time
                self._access_times[key] = current_time

                # Move to end for LRU
                self._data.move_to_end(key)

                return item["value"]

        except Exception as e:
            print(f"Error retrieving from short-term memory: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a value from short-term memory."""
        try:
            with self._lock:
                if key in self._data:
                    del self._data[key]
                    self._priorities.pop(key, None)
                    self._access_times.pop(key, None)
                    return True
                return False
        except Exception as e:
            print(f"Error deleting from short-term memory: {e}")
            return False

    def _evict(self):
        """Evict items based on retention policy."""
        if not self._data:
            return

        if self.retention_policy == "lru":
            # Remove least recently used (first item in OrderedDict)
            oldest_key = next(iter(self._data))
            self.delete(oldest_key)

        elif self.retention_policy == "fifo":
            # Remove first in, first out
            oldest_key = min(
                self._data.keys(), key=lambda k: self._data[k]["created_at"]
            )
            self.delete(oldest_key)

        elif self.retention_policy == "priority":
            # Remove lowest priority item, then oldest if tied
            lowest_priority_key = min(
                self._data.keys(),
                key=lambda k: (self._priorities.get(k, 1), self._data[k]["created_at"]),
            )
            self.delete(lowest_priority_key)

    def add_to_conversation(
        self, role: str, content: str, metadata: Optional[Dict] = None
    ):
        """Add a message to conversation history."""
        try:
            with self._lock:
                message = {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {},
                }

                self._conversation_history.append(message)

                # Trim conversation history if too long
                if len(self._conversation_history) > self._max_conversation_length:
                    # Keep recent messages and system messages
                    system_messages = [
                        msg
                        for msg in self._conversation_history
                        if msg["role"] == "system"
                    ]
                    recent_messages = self._conversation_history[
                        -(self._max_conversation_length - len(system_messages)) :
                    ]
                    self._conversation_history = system_messages + recent_messages

        except Exception as e:
            print(f"Error adding to conversation: {e}")

    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict]:
        """Get conversation history."""
        try:
            with self._lock:
                if last_n:
                    return self._conversation_history[-last_n:]
                return self._conversation_history.copy()
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    def clear_conversation(self):
        """Clear conversation history."""
        try:
            with self._lock:
                self._conversation_history.clear()
        except Exception as e:
            print(f"Error clearing conversation: {e}")

    def set_working_memory(self, key: str, value: Any):
        """Set a value in working memory (temporary context)."""
        try:
            with self._lock:
                self._working_memory[key] = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            print(f"Error setting working memory: {e}")

    def get_working_memory(self, key: str) -> Optional[Any]:
        """Get a value from working memory."""
        try:
            with self._lock:
                item = self._working_memory.get(key)
                return item["value"] if item else None
        except Exception as e:
            print(f"Error getting working memory: {e}")
            return None

    def clear_working_memory(self):
        """Clear working memory."""
        try:
            with self._lock:
                self._working_memory.clear()
        except Exception as e:
            print(f"Error clearing working memory: {e}")

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context."""
        try:
            with self._lock:
                recent_conversation = self.get_conversation_history(last_n=10)

                return {
                    "recent_conversation": recent_conversation,
                    "working_memory": dict(self._working_memory),
                    "memory_items": len(self._data),
                    "memory_capacity": self.capacity,
                    "memory_usage": len(self._data) / self.capacity,
                }
        except Exception as e:
            print(f"Error getting context summary: {e}")
            return {}

    def cleanup_expired(self):
        """Remove expired items."""
        try:
            with self._lock:
                current_time = time.time()
                expired_keys = []

                for key, item in self._data.items():
                    if item.get("expires_at") and current_time > item["expires_at"]:
                        expired_keys.append(key)

                for key in expired_keys:
                    self.delete(key)

                return len(expired_keys)

        except Exception as e:
            print(f"Error cleaning up expired items: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            with self._lock:
                if not self._data:
                    return {
                        "size": 0,
                        "capacity": self.capacity,
                        "usage_percentage": 0,
                        "retention_policy": self.retention_policy,
                    }

                access_counts = [item["access_count"] for item in self._data.values()]
                ages = [
                    time.time() - item["created_at"] for item in self._data.values()
                ]

                return {
                    "size": len(self._data),
                    "capacity": self.capacity,
                    "usage_percentage": (len(self._data) / self.capacity) * 100,
                    "retention_policy": self.retention_policy,
                    "avg_access_count": sum(access_counts) / len(access_counts),
                    "avg_age_seconds": sum(ages) / len(ages),
                    "conversation_length": len(self._conversation_history),
                    "working_memory_items": len(self._working_memory),
                }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def clear(self):
        """Clear all memory."""
        try:
            with self._lock:
                self._data.clear()
                self._priorities.clear()
                self._access_times.clear()
                self._conversation_history.clear()
                self._working_memory.clear()
        except Exception as e:
            print(f"Error clearing memory: {e}")

    def keys(self) -> List[str]:
        """Get all keys in memory."""
        try:
            with self._lock:
                return list(self._data.keys())
        except Exception as e:
            print(f"Error getting keys: {e}")
            return []

    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs."""
        try:
            with self._lock:
                return [(key, item["value"]) for key, item in self._data.items()]
        except Exception as e:
            print(f"Error getting items: {e}")
            return []
