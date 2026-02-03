"""
Model registry for tracking model metadata and usage statistics.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .utils import (
    SuperOptiXModelSize,
    SuperOptiXModelTask,
    SuperOptiXModelStatus,
    SuperOptiXBackendType,
    SuperOptiXModelInfo,
)
from .config import get_superoptix_config_dir


class SuperOptiXModelRegistry:
    """SuperOptiX Registry for tracking model metadata and usage statistics."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            cache_dir = get_superoptix_config_dir() / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / "models.db"

        self.db_path = db_path
        self._initialized = False

    def _initialize_db(self):
        """Initialize the database schema."""
        if self._initialized:
            return

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    status TEXT NOT NULL,
                    size_category TEXT,
                    task_type TEXT,
                    parameters TEXT,
                    description TEXT,
                    tags TEXT,  -- JSON array
                    disk_size INTEGER,
                    context_length INTEGER,
                    local_path TEXT,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, backend)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_type TEXT,  -- 'inference', 'test', 'training'
                    tokens_generated INTEGER,
                    response_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    metadata TEXT  -- JSON object
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_models_name_backend 
                ON models(name, backend)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_model_time 
                ON model_usage(model_name, backend, used_at)
            """)

            conn.commit()

        self._initialized = True

    async def register_model(self, model_info: SuperOptiXModelInfo):
        """Register or update a model in the registry."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            # Check if model exists
            cursor = conn.execute(
                "SELECT id FROM models WHERE name = ? AND backend = ?",
                (model_info.name, model_info.backend.value),
            )

            if cursor.fetchone():
                # Update existing model
                conn.execute(
                    """
                    UPDATE models SET
                        status = ?, size_category = ?, task_type = ?, parameters = ?,
                        description = ?, tags = ?, disk_size = ?, context_length = ?,
                        local_path = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ? AND backend = ?
                """,
                    (
                        model_info.status.value,
                        model_info.size.value if model_info.size else None,
                        model_info.task.value if model_info.task else None,
                        model_info.parameters,
                        model_info.description,
                        json.dumps(model_info.tags),
                        model_info.disk_size,
                        model_info.context_length,
                        str(model_info.local_path) if model_info.local_path else None,
                        json.dumps(model_info.metadata),
                        model_info.name,
                        model_info.backend.value,
                    ),
                )
            else:
                # Insert new model
                conn.execute(
                    """
                    INSERT INTO models (
                        name, backend, status, size_category, task_type, parameters,
                        description, tags, disk_size, context_length, local_path, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        model_info.name,
                        model_info.backend.value,
                        model_info.status.value,
                        model_info.size.value if model_info.size else None,
                        model_info.task.value if model_info.task else None,
                        model_info.parameters,
                        model_info.description,
                        json.dumps(model_info.tags),
                        model_info.disk_size,
                        model_info.context_length,
                        str(model_info.local_path) if model_info.local_path else None,
                        json.dumps(model_info.metadata),
                    ),
                )

            conn.commit()

    async def get_model(
        self, name: str, backend: SuperOptiXBackendType
    ) -> Optional[SuperOptiXModelInfo]:
        """Get a model from the registry."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM models WHERE name = ? AND backend = ?
            """,
                (name, backend.value),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return self._row_to_model_info(row)

    async def list_models(
        self,
        backend: Optional[SuperOptiXBackendType] = None,
        status: Optional[SuperOptiXModelStatus] = None,
    ) -> List[SuperOptiXModelInfo]:
        """List models from the registry."""
        self._initialize_db()

        query = "SELECT * FROM models WHERE 1=1"
        params = []

        if backend:
            query += " AND backend = ?"
            params.append(backend.value)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        query += " ORDER BY name"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            models = []
            for row in cursor.fetchall():
                models.append(self._row_to_model_info(row))

            return models

    async def search_models(
        self, query: str, limit: int = 10
    ) -> List[SuperOptiXModelInfo]:
        """Search models in the registry."""
        self._initialize_db()

        search_query = """
            SELECT * FROM models 
            WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY 
                CASE 
                    WHEN name LIKE ? THEN 1
                    WHEN description LIKE ? THEN 2
                    ELSE 3
                END,
                name
            LIMIT ?
        """

        search_term = f"%{query}%"
        exact_term = f"%{query}%"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                search_query,
                (search_term, search_term, search_term, exact_term, exact_term, limit),
            )

            models = []
            for row in cursor.fetchall():
                models.append(self._row_to_model_info(row))

            return models

    async def record_usage(
        self,
        model_name: str,
        backend: SuperOptiXBackendType,
        usage_type: str = "inference",
        **kwargs,
    ):
        """Record model usage statistics."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO model_usage (
                    model_name, backend, usage_type, tokens_generated, 
                    response_time, success, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    model_name,
                    backend.value,
                    usage_type,
                    kwargs.get("tokens_generated"),
                    kwargs.get("response_time"),
                    kwargs.get("success", True),
                    kwargs.get("error_message"),
                    json.dumps(kwargs.get("metadata", {})),
                ),
            )

            conn.commit()

    async def get_usage_stats(
        self, model_name: str, backend: SuperOptiXBackendType, days: int = 30
    ) -> Dict[str, Any]:
        """Get usage statistics for a model."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
                    AVG(response_time) as avg_response_time,
                    SUM(tokens_generated) as total_tokens,
                    MAX(used_at) as last_used
                FROM model_usage 
                WHERE model_name = ? AND backend = ? 
                AND used_at >= datetime('now', '-' || ? || ' days')
            """,
                (model_name, backend.value, days),
            )

            stats = dict(cursor.fetchone())

            # Get usage by day
            cursor = conn.execute(
                """
                SELECT 
                    DATE(used_at) as date,
                    COUNT(*) as uses,
                    AVG(response_time) as avg_response_time
                FROM model_usage 
                WHERE model_name = ? AND backend = ? 
                AND used_at >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(used_at)
                ORDER BY date
            """,
                (model_name, backend.value, days),
            )

            daily_stats = [dict(row) for row in cursor.fetchall()]
            stats["daily_usage"] = daily_stats

            return stats

    async def get_popular_models(
        self, limit: int = 10, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get most popular models by usage."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    u.model_name,
                    u.backend,
                    COUNT(*) as usage_count,
                    AVG(u.response_time) as avg_response_time,
                    m.description,
                    m.parameters
                FROM model_usage u
                LEFT JOIN models m ON u.model_name = m.name AND u.backend = m.backend
                WHERE u.used_at >= datetime('now', '-' || ? || ' days')
                GROUP BY u.model_name, u.backend
                ORDER BY usage_count DESC
                LIMIT ?
            """,
                (days, limit),
            )

            return [dict(row) for row in cursor.fetchall()]

    async def cleanup_old_usage(self, days: int = 90):
        """Clean up old usage records."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM model_usage 
                WHERE used_at < datetime('now', '-' || ? || ' days')
            """,
                (days,),
            )

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

    async def export_data(self, output_path: Path):
        """Export registry data to JSON."""
        self._initialize_db()

        data = {
            "models": [],
            "usage_stats": [],
            "exported_at": datetime.now().isoformat(),
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Export models
            cursor = conn.execute("SELECT * FROM models")
            for row in cursor.fetchall():
                data["models"].append(dict(row))

            # Export recent usage
            cursor = conn.execute("""
                SELECT * FROM model_usage 
                WHERE used_at >= datetime('now', '-30 days')
                ORDER BY used_at DESC
            """)
            for row in cursor.fetchall():
                data["usage_stats"].append(dict(row))

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _row_to_model_info(self, row) -> SuperOptiXModelInfo:
        """Convert database row to SuperOptiXModelInfo object."""
        from .utils import (
            SuperOptiXModelStatus,
            SuperOptiXBackendType,
            SuperOptiXModelInfo,
        )

        # Parse enums safely
        size = None
        if row["size_category"]:
            try:
                size = SuperOptiXModelSize(row["size_category"])
            except ValueError:
                pass

        task = None
        if row["task_type"]:
            try:
                task = SuperOptiXModelTask(row["task_type"])
            except ValueError:
                pass

        status = SuperOptiXModelStatus(row["status"])
        backend = SuperOptiXBackendType(row["backend"])

        # Parse JSON fields
        tags = json.loads(row["tags"]) if row["tags"] else []
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        # Parse datetime
        last_used = None
        if row["updated_at"]:
            try:
                last_used = datetime.fromisoformat(row["updated_at"])
            except ValueError:
                pass

        return SuperOptiXModelInfo(
            name=row["name"],
            backend=backend,
            status=status,
            size=size,
            task=task,
            description=row["description"],
            tags=tags,
            parameters=row["parameters"],
            context_length=row["context_length"],
            local_path=Path(row["local_path"]) if row["local_path"] else None,
            disk_size=row["disk_size"],
            last_used=last_used,
            metadata=metadata,
        )

    def add_model(self, model_info: SuperOptiXModelInfo):
        """Add or update a model in the registry (sync wrapper)."""
        import asyncio

        try:
            asyncio.run(self.register_model(model_info))
        except RuntimeError:
            # If there's already a running event loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.register_model(model_info))
            finally:
                loop.close()

    def remove_model(self, model_name: str):
        """Remove a model from the registry (sync wrapper)."""
        # For now, just mark as uninstalled
        # In a full implementation, this would delete the record
        pass

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics (sync wrapper)."""
        import asyncio

        try:
            return asyncio.run(self._get_usage_stats_sync())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_usage_stats_sync())
            finally:
                loop.close()

    async def _get_usage_stats_sync(self) -> Dict[str, Any]:
        """Get usage statistics."""
        self._initialize_db()

        with sqlite3.connect(self.db_path) as conn:
            # Get total models
            cursor = conn.execute("SELECT COUNT(*) as count FROM models")
            total_models = cursor.fetchone()[0]

            # Get total usage
            cursor = conn.execute("SELECT COUNT(*) as count FROM model_usage")
            total_usage = cursor.fetchone()[0]

            # Get popular models
            cursor = conn.execute("""
                SELECT model_name, backend, COUNT(*) as usage_count
                FROM model_usage
                GROUP BY model_name, backend
                ORDER BY usage_count DESC
                LIMIT 5
            """)
            popular_models = [dict(row) for row in cursor.fetchall()]

            return {
                "total_models": total_models,
                "total_usage": total_usage,
                "popular_models": popular_models,
            }

    def close(self):
        """Close the registry (cleanup)."""
        # For now, just a placeholder
        # In a full implementation, this would close database connections
        pass
