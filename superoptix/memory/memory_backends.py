"""Memory backend implementations for different storage systems."""

import json
import pickle
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional, Union

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class MemoryBackend(ABC):
    """Abstract base class for memory backends."""

    @abstractmethod
    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value with optional time-to-live."""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all stored data."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get number of stored items."""
        pass


class FileBackend(MemoryBackend):
    """File-based memory backend using JSON and pickle."""

    def __init__(self, storage_path: Union[str, Path] = None):
        self.storage_path = Path(storage_path or ".superoptix/memory")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _get_file_path(self, key: str) -> Path:
        """Get file path for a key."""
        # Replace invalid filename characters
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.storage_path / f"{safe_key}.json"

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for a key."""
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.storage_path / f"{safe_key}.meta"

    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value to file with optional TTL."""
        try:
            with self._lock:
                file_path = self._get_file_path(key)
                meta_path = self._get_metadata_path(key)

                # Store the actual data
                with open(file_path, "w", encoding="utf-8") as f:
                    if isinstance(value, (dict, list, str, int, float, bool)):
                        json.dump(value, f, indent=2, default=str)
                    else:
                        # Use pickle for complex objects
                        pickle_path = file_path.with_suffix(".pkl")
                        with open(pickle_path, "wb") as pf:
                            pickle.dump(value, pf)
                        file_path.unlink(missing_ok=True)  # Remove JSON file
                        file_path = pickle_path

                # Store metadata
                metadata = {
                    "original_key": key,  # Store the original key
                    "created_at": datetime.now().isoformat(),
                    "ttl": ttl,
                    "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
                    if ttl
                    else None,
                    "is_pickle": file_path.suffix == ".pkl",
                }

                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)

                return True

        except Exception as e:
            print(f"Error storing key {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from file."""
        try:
            with self._lock:
                file_path = self._get_file_path(key)
                meta_path = self._get_metadata_path(key)
                pickle_path = file_path.with_suffix(".pkl")

                # Check if metadata exists
                if not meta_path.exists():
                    return None

                # Load metadata
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # Check TTL
                if metadata.get("expires_at"):
                    expires_at = datetime.fromisoformat(metadata["expires_at"])
                    if datetime.now() > expires_at:
                        self.delete(key)
                        return None

                # Load data
                if metadata.get("is_pickle", False) and pickle_path.exists():
                    with open(pickle_path, "rb") as f:
                        return pickle.load(f)
                elif file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)

                return None

        except Exception as e:
            print(f"Error retrieving key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete files for a key."""
        try:
            with self._lock:
                file_path = self._get_file_path(key)
                meta_path = self._get_metadata_path(key)
                pickle_path = file_path.with_suffix(".pkl")

                deleted = False
                for path in [file_path, meta_path, pickle_path]:
                    if path.exists():
                        path.unlink()
                        deleted = True

                return deleted

        except Exception as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.retrieve(key) is not None

    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        try:
            with self._lock:
                import fnmatch
                import json
                from datetime import datetime

                keys = []
                for meta_file in self.storage_path.glob("*.meta"):
                    try:
                        # Load metadata to get original key
                        with open(meta_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)

                        original_key = metadata.get("original_key", meta_file.stem)

                        # Use fnmatch for glob-style pattern matching
                        if fnmatch.fnmatch(original_key, pattern):
                            # Check if not expired
                            if metadata.get("expires_at"):
                                expires_at = datetime.fromisoformat(
                                    metadata["expires_at"]
                                )
                                if datetime.now() > expires_at:
                                    continue
                            keys.append(original_key)
                    except Exception:
                        # If we can't read metadata, skip this file
                        continue
                return keys
        except Exception as e:
            print(f"Error getting keys: {e}")
            return []

    def clear(self) -> bool:
        """Clear all stored data."""
        try:
            with self._lock:
                for file_path in self.storage_path.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                return True
        except Exception as e:
            print(f"Error clearing storage: {e}")
            return False

    def size(self) -> int:
        """Get number of stored items."""
        return len(self.keys())


class SQLiteBackend(MemoryBackend):
    """SQLite-based memory backend."""

    def __init__(self, db_path: Union[str, Path] = None):
        self.db_path = Path(db_path or ".superoptix/memory/memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self):
        """Get a database connection with proper context management."""
        conn = sqlite3.connect(str(self.db_path))
        # Enable row factory for better results
        conn.row_factory = sqlite3.Row
        # Set pragmas for better performance and safety
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self):
        """Initialize the database schema."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        key TEXT PRIMARY KEY,
                        value BLOB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_json BOOLEAN DEFAULT 1
                    )
                """)
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_expires_at ON memory(expires_at)"
                )
                conn.commit()

    def __del__(self):
        """Cleanup method to ensure proper resource cleanup."""
        try:
            # Explicit cleanup - though context managers should handle this
            pass
        except:
            pass

    def _cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM memory WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (datetime.now().isoformat(),),
                )
                conn.commit()

    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in SQLite database."""
        try:
            with self._lock:
                self._cleanup_expired()

                with self._get_connection() as conn:
                    expires_at = None
                    if ttl:
                        expires_at = (
                            datetime.now() + timedelta(seconds=ttl)
                        ).isoformat()

                    # Try to serialize as JSON first
                    try:
                        serialized_value = json.dumps(value, default=str).encode(
                            "utf-8"
                        )
                        is_json = True
                    except (TypeError, ValueError):
                        # Fall back to pickle
                        serialized_value = pickle.dumps(value)
                        is_json = False

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO memory (key, value, expires_at, is_json)
                        VALUES (?, ?, ?, ?)
                    """,
                        (key, serialized_value, expires_at, is_json),
                    )
                    conn.commit()
                    return True

        except Exception as e:
            print(f"Error storing key {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from SQLite database."""
        try:
            with self._lock:
                self._cleanup_expired()

                with self._get_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT value, is_json FROM memory
                        WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
                    """,
                        (key, datetime.now().isoformat()),
                    )

                    row = cursor.fetchone()
                    if row:
                        value_bytes, is_json = row
                        if is_json:
                            return json.loads(value_bytes.decode("utf-8"))
                        else:
                            return pickle.loads(value_bytes)
                    return None

        except Exception as e:
            print(f"Error retrieving key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete value from SQLite database."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.execute("DELETE FROM memory WHERE key = ?", (key,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in database."""
        return self.retrieve(key) is not None

    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        try:
            with self._lock:
                import fnmatch

                self._cleanup_expired()

                with self._get_connection() as conn:
                    # Get all keys first, then filter with fnmatch for glob patterns
                    cursor = conn.execute(
                        """
                        SELECT key FROM memory
                        WHERE expires_at IS NULL OR expires_at > ?
                    """,
                        (datetime.now().isoformat(),),
                    )

                    all_keys = [row[0] for row in cursor.fetchall()]

                    # Filter using fnmatch for glob-style pattern matching
                    if pattern == "*":
                        return all_keys
                    else:
                        return [
                            key for key in all_keys if fnmatch.fnmatch(key, pattern)
                        ]

        except Exception as e:
            print(f"Error getting keys: {e}")
            return []

    def clear(self) -> bool:
        """Clear all data from database."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    conn.execute("DELETE FROM memory")
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

    def size(self) -> int:
        """Get number of stored items."""
        try:
            with self._lock:
                self._cleanup_expired()

                with self._get_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT COUNT(*) FROM memory
                        WHERE expires_at IS NULL OR expires_at > ?
                    """,
                        (datetime.now().isoformat(),),
                    )
                    return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting size: {e}")
            return 0


class RedisBackend(MemoryBackend):
    """Redis-based memory backend."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "superoptix:",
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not available. Install with: pip install redis")

        self.prefix = prefix
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We'll handle encoding ourselves
        )

        # Test connection
        try:
            self.redis_client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Could not connect to Redis: {e}") from e

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"

    def _strip_prefix(self, key: str) -> str:
        """Remove prefix from key."""
        if key.startswith(self.prefix):
            return key[len(self.prefix) :]
        return key

    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis."""
        try:
            redis_key = self._make_key(key)

            # Try to serialize as JSON first
            try:
                serialized_value = json.dumps(value, default=str)
                self.redis_client.hset(
                    redis_key, mapping={"value": serialized_value, "is_json": "true"}
                )
            except (TypeError, ValueError):
                # Fall back to pickle
                serialized_value = pickle.dumps(value)
                self.redis_client.hset(
                    redis_key, mapping={"value": serialized_value, "is_json": "false"}
                )

            if ttl:
                self.redis_client.expire(redis_key, ttl)

            return True

        except Exception as e:
            print(f"Error storing key {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis."""
        try:
            redis_key = self._make_key(key)
            data = self.redis_client.hmget(redis_key, "value", "is_json")

            if data[0] is None:
                return None

            value_bytes = data[0]
            is_json = data[1] == b"true" if data[1] else True

            if is_json:
                return json.loads(value_bytes.decode("utf-8"))
            else:
                return pickle.loads(value_bytes)

        except Exception as e:
            print(f"Error retrieving key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        try:
            redis_key = self._make_key(key)
            return self.redis_client.delete(redis_key) > 0
        except Exception as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            redis_key = self._make_key(key)
            return self.redis_client.exists(redis_key) > 0
        except Exception as e:
            print(f"Error checking existence of key {key}: {e}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        try:
            redis_pattern = self._make_key(pattern)
            redis_keys = self.redis_client.keys(redis_pattern)
            return [self._strip_prefix(key.decode("utf-8")) for key in redis_keys]
        except Exception as e:
            print(f"Error getting keys: {e}")
            return []

    def clear(self) -> bool:
        """Clear all data with prefix."""
        try:
            keys = self.redis_client.keys(self._make_key("*"))
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error clearing Redis: {e}")
            return False

    def size(self) -> int:
        """Get number of stored items."""
        try:
            return len(self.redis_client.keys(self._make_key("*")))
        except Exception as e:
            print(f"Error getting size: {e}")
            return 0
