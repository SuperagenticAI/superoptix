"""Memory backend implementations for different storage systems."""

import base64
import fnmatch
import json
import pickle
import re
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

try:
    from surrealdb import Surreal

    SURREALDB_AVAILABLE = True
except ImportError:
    Surreal = None
    SURREALDB_AVAILABLE = False


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
            raise ImportError(
                "Redis is not available. Install with: uv pip install redis"
            )

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


class SurrealDBBackend(MemoryBackend):
    """SurrealDB-based memory backend."""

    def __init__(
        self,
        url: str = "ws://localhost:8000",
        namespace: str = "test",
        database: str = "test",
        username: str = "root",
        password: str = "root",
        table_name: str = "superoptix_memory",
        skip_signin: Optional[bool] = None,
        temporal_enabled: bool = False,
        max_versions_per_key: int = 50,
    ):
        if not SURREALDB_AVAILABLE:
            raise ImportError(
                "SurrealDB backend requires surrealdb package. Install with: uv pip install surrealdb"
            )
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            raise ValueError(
                "Invalid SurrealDB table name. Use letters, numbers, and underscores only."
            )

        self.url = self._normalize_surrealdb_url(url)
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.skip_signin = (
            self._default_skip_signin(self.url)
            if skip_signin is None
            else bool(skip_signin)
        )
        self.table_name = table_name
        self.temporal_enabled = bool(temporal_enabled)
        self.max_versions_per_key = max(5, int(max_versions_per_key))
        self.versions_table = f"{table_name}_versions"
        self._lock = threading.RLock()
        self._sticky_ctx = None
        self._sticky_db = None

    def _with_connection(self):
        """Context manager-like helper that returns a configured SurrealDB client."""
        db = Surreal(self.url)
        return db

    def _should_use_sticky_connection(self) -> bool:
        from urllib.parse import urlparse

        parsed = urlparse(self.url)
        scheme = parsed.scheme.lower()
        return scheme in {"memory", "mem", "file", "surrealkv"} or self.url == "memory"

    def _get_sticky_db(self):
        if self._sticky_db is not None:
            return self._sticky_db
        self._sticky_ctx = self._with_connection()
        self._sticky_db = self._sticky_ctx.__enter__()
        if not self.skip_signin:
            self._sticky_db.signin(
                {"username": self.username, "password": self.password}
            )
        self._sticky_db.use(self.namespace, self.database)
        return self._sticky_db

    def _run_query(self, query: str, params: Optional[dict[str, Any]] = None) -> Any:
        params = params or {}
        if self._should_use_sticky_connection():
            db = self._get_sticky_db()
            return db.query(query, params)

        with self._with_connection() as db:
            if not self.skip_signin:
                db.signin({"username": self.username, "password": self.password})
            db.use(self.namespace, self.database)
            return db.query(query, params)

    def __del__(self):
        """Best-effort cleanup for sticky SurrealDB sessions."""
        try:
            if self._sticky_ctx is not None:
                self._sticky_ctx.__exit__(None, None, None)
        except Exception:
            pass

    def _extract_rows(self, raw: Any) -> list[dict[str, Any]]:
        """Normalize query outputs from SurrealDB SDK variants."""
        if isinstance(raw, list):
            if (
                raw
                and isinstance(raw[0], dict)
                and "result" in raw[0]
                and isinstance(raw[0]["result"], list)
            ):
                return [row for row in raw[0]["result"] if isinstance(row, dict)]
            return [row for row in raw if isinstance(row, dict)]

        if isinstance(raw, dict):
            result = raw.get("result")
            if isinstance(result, list):
                if (
                    result
                    and isinstance(result[0], dict)
                    and "result" in result[0]
                    and isinstance(result[0]["result"], list)
                ):
                    return [row for row in result[0]["result"] if isinstance(row, dict)]
                return [row for row in result if isinstance(row, dict)]
            return [raw]

        return []

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value:
            return None
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except Exception:
            return None

    def _is_expired(self, row: dict[str, Any]) -> bool:
        expires_at = self._parse_datetime(row.get("expires_at"))
        if expires_at is None:
            return False
        return datetime.now(expires_at.tzinfo) > expires_at

    def _cleanup_expired(self) -> None:
        try:
            self._run_query(
                f"DELETE {self.table_name} WHERE expires_at != NONE AND expires_at < time::now();"
            )
        except Exception:
            # Best-effort cleanup only.
            pass

    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in SurrealDB with optional TTL.

        When ``temporal_enabled=True``, also appends a version record to the
        ``{table_name}_versions`` table so full history is preserved.
        The primary table always holds only the latest value — existing
        ``retrieve``, ``delete``, ``size``, and ``keys`` semantics are unchanged.
        """
        try:
            with self._lock:
                self._cleanup_expired()
                try:
                    encoded_value = json.dumps(value)
                    is_pickle = False
                except (TypeError, ValueError):
                    encoded_value = base64.b64encode(pickle.dumps(value)).decode(
                        "ascii"
                    )
                    is_pickle = True

                now_iso = datetime.now().isoformat()
                expires_at = None
                if ttl is not None:
                    expires_at = (
                        datetime.now() + timedelta(seconds=int(ttl))
                    ).isoformat()

                payload = {
                    "memory_key": key,
                    "stored_value": encoded_value,
                    "is_pickle": is_pickle,
                    "created_at": now_iso,
                    "updated_at": now_iso,
                    "expires_at": expires_at,
                }

                # Primary table: replace with latest value (unchanged semantics)
                self._run_query(
                    f"DELETE {self.table_name} WHERE memory_key = $memory_key;",
                    {"memory_key": key},
                )
                self._run_query(
                    f"CREATE {self.table_name} CONTENT $payload;",
                    {"payload": payload},
                )

                # Versions table: append-only log (temporal mode only)
                if self.temporal_enabled:
                    version_payload = {
                        "memory_key": key,
                        "stored_value": encoded_value,
                        "is_pickle": is_pickle,
                        "version_ts": now_iso,
                    }
                    self._run_query(
                        f"CREATE {self.versions_table} CONTENT $payload;",
                        {"payload": version_payload},
                    )
                    self._prune_versions(key)

                return True
        except Exception as e:
            print(f"Error storing key {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from SurrealDB by key."""
        try:
            with self._lock:
                self._cleanup_expired()
                raw = self._run_query(
                    f"SELECT * FROM {self.table_name} WHERE memory_key = $memory_key LIMIT 1;",
                    {"memory_key": key},
                )
                rows = self._extract_rows(raw)
                if not rows:
                    return None
                row = rows[0]
                if self._is_expired(row):
                    self.delete(key)
                    return None
                stored_value = row.get("stored_value")
                if stored_value is None:
                    return None
                if bool(row.get("is_pickle", False)):
                    return pickle.loads(
                        base64.b64decode(str(stored_value).encode("ascii"))
                    )
                return json.loads(str(stored_value))
        except Exception as e:
            print(f"Error retrieving key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete key from SurrealDB."""
        try:
            with self._lock:
                self._run_query(
                    f"DELETE {self.table_name} WHERE memory_key = $memory_key;",
                    {"memory_key": key},
                )
                return True
        except Exception as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in SurrealDB."""
        return self.retrieve(key) is not None

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching glob pattern."""
        try:
            with self._lock:
                self._cleanup_expired()
                raw = self._run_query(f"SELECT memory_key FROM {self.table_name};")
                rows = self._extract_rows(raw)
                all_keys: list[str] = []
                for row in rows:
                    key = row.get("memory_key")
                    if isinstance(key, str):
                        all_keys.append(key)
                if pattern == "*":
                    return all_keys
                return [key for key in all_keys if fnmatch.fnmatch(key, pattern)]
        except Exception as e:
            print(f"Error getting keys: {e}")
            return []

    def clear(self) -> bool:
        """Clear all keys in table."""
        try:
            with self._lock:
                self._run_query(f"DELETE {self.table_name};")
                return True
        except Exception as e:
            print(f"Error clearing SurrealDB: {e}")
            return False

    def size(self) -> int:
        """Get number of non-expired memory records."""
        try:
            with self._lock:
                self._cleanup_expired()
                raw = self._run_query(
                    f"SELECT count() AS count FROM {self.table_name} GROUP ALL;"
                )
                rows = self._extract_rows(raw)
                if not rows:
                    return 0
                count = rows[0].get("count", 0)
                return int(count) if isinstance(count, (int, float)) else 0
        except Exception as e:
            print(f"Error getting size: {e}")
            return 0

    def retrieve_at(self, key: str, as_of: datetime) -> Optional[Any]:
        """Retrieve the value for *key* as it was at *as_of* (point-in-time).

        Requires ``temporal_enabled=True``.  Falls back to the current value
        when temporal is disabled so callers don't need to branch.

        Args:
            key: Memory key to look up.
            as_of: Datetime at which to retrieve the value.

        Returns:
            The decoded value that was stored at or before *as_of*, or ``None``
            if no matching version is found.
        """
        if not self.temporal_enabled:
            return self.retrieve(key)

        try:
            with self._lock:
                as_of_iso = as_of.isoformat()
                raw = self._run_query(
                    f"SELECT * FROM {self.versions_table} "
                    f"WHERE memory_key = $key AND version_ts <= $as_of "
                    f"ORDER BY version_ts DESC LIMIT 1;",
                    {"key": key, "as_of": as_of_iso},
                )
                rows = self._extract_rows(raw)
                if not rows:
                    return None
                row = rows[0]
                stored_value = row.get("stored_value")
                if stored_value is None:
                    return None
                if bool(row.get("is_pickle", False)):
                    return pickle.loads(
                        base64.b64decode(str(stored_value).encode("ascii"))
                    )
                return json.loads(str(stored_value))
        except Exception as e:
            print(f"Error in retrieve_at for key {key}: {e}")
            return None

    def history(self, key: str, limit: int = 10) -> list[dict[str, Any]]:
        """Return version history for *key* in reverse chronological order.

        Requires ``temporal_enabled=True``.  Returns an empty list when
        temporal is disabled.

        Args:
            key: Memory key to look up.
            limit: Maximum number of versions to return.

        Returns:
            List of dicts with ``value``, ``version_ts``, and ``is_pickle`` keys.
        """
        if not self.temporal_enabled:
            return []

        try:
            with self._lock:
                raw = self._run_query(
                    f"SELECT memory_key, stored_value, is_pickle, version_ts "
                    f"FROM {self.versions_table} "
                    f"WHERE memory_key = $key "
                    f"ORDER BY version_ts DESC LIMIT $limit;",
                    {"key": key, "limit": int(limit)},
                )
                rows = self._extract_rows(raw)
                results: list[dict[str, Any]] = []
                for row in rows:
                    stored_value = row.get("stored_value")
                    if stored_value is None:
                        continue
                    try:
                        if bool(row.get("is_pickle", False)):
                            decoded = pickle.loads(
                                base64.b64decode(str(stored_value).encode("ascii"))
                            )
                        else:
                            decoded = json.loads(str(stored_value))
                    except Exception:
                        decoded = stored_value
                    results.append(
                        {
                            "value": decoded,
                            "version_ts": row.get("version_ts"),
                            "is_pickle": bool(row.get("is_pickle", False)),
                        }
                    )
                return results
        except Exception as e:
            print(f"Error in history for key {key}: {e}")
            return []

    def _prune_versions(self, key: str) -> None:
        """Keep only the most recent ``max_versions_per_key`` versions."""
        try:
            # Count existing versions for this key
            raw = self._run_query(
                f"SELECT count() AS count FROM {self.versions_table} "
                f"WHERE memory_key = $key GROUP ALL;",
                {"key": key},
            )
            rows = self._extract_rows(raw)
            if not rows:
                return
            count = int(rows[0].get("count", 0))
            if count <= self.max_versions_per_key:
                return

            # Delete oldest versions beyond the limit
            excess = count - self.max_versions_per_key
            self._run_query(
                f"DELETE FROM (SELECT id FROM {self.versions_table} "
                f"WHERE memory_key = $key "
                f"ORDER BY version_ts ASC LIMIT $excess);",
                {"key": key, "excess": excess},
            )
        except Exception:
            # Pruning is best-effort; never fail the calling store()
            pass

    def _normalize_surrealdb_url(self, url: str) -> str:
        """Normalize URL so SDK does not append duplicate /rpc."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        if (
            scheme in {"ws", "wss", "http", "https"}
            and parsed.path.rstrip("/") == "/rpc"
        ):
            return f"{scheme}://{parsed.netloc}"
        return url

    def _default_skip_signin(self, url: str) -> bool:
        """Embedded transports generally don't require explicit signin."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        return scheme in {"memory", "mem", "file", "surrealkv"} or url == "memory"
