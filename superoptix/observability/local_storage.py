"""Local-first storage for SuperOptiX observability.

Provides lightweight SQLite-based storage for agent metrics, optimization
history, and protocol usage without requiring external services.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LocalObservabilityStorage:
    """Local SQLite storage for observability data.

    Stores agent runs, optimization history, and protocol usage locally.
    Can export to external platforms (MLFlow, W&B, etc.) when needed.

    Examples:
        >>> storage = LocalObservabilityStorage()
        >>> storage.store_agent_run({
        ...     "agent_name": "my_agent",
        ...     "framework": "dspy",
        ...     "accuracy": 0.85,
        ...     "cost_usd": 0.05
        ... })
        >>>
        >>> # Query recent runs
        >>> runs = storage.get_agent_runs("my_agent", limit=10)
    """

    def __init__(self, db_path: str = ".superoptix/observability.db"):
        """Initialize local storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows

        self._create_tables()
        logger.info(f"Initialized local storage at {self.db_path}")

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Agent runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                framework TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                accuracy REAL,
                cost_usd REAL,
                tokens_used INTEGER,
                latency_ms REAL,
                success_rate REAL,
                status TEXT DEFAULT 'success',
                extra_data TEXT  -- JSON string for additional metrics
            )
        """)

        # Optimization runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                optimizer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                initial_score REAL NOT NULL,
                final_score REAL NOT NULL,
                improvement REAL NOT NULL,
                iterations INTEGER NOT NULL,
                population_size INTEGER,
                generations INTEGER,
                duration_seconds REAL,
                best_prompt TEXT,
                evolution_history TEXT  -- JSON string
            )
        """)

        # Protocol usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protocol_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                protocol_type TEXT NOT NULL,
                server_uri TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tools_discovered INTEGER NOT NULL,
                tools_used TEXT NOT NULL,  -- JSON array
                tool_success_rate REAL,
                avg_latency_ms REAL,
                total_calls INTEGER
            )
        """)

        # Cost tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens_input INTEGER NOT NULL,
                tokens_output INTEGER NOT NULL,
                tokens_total INTEGER NOT NULL,
                cost_usd REAL NOT NULL
            )
        """)

        # Framework comparison table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS framework_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frameworks_data TEXT NOT NULL,  -- JSON string
                best_framework TEXT NOT NULL,
                best_accuracy REAL
            )
        """)

        self.conn.commit()
        logger.debug("Database tables created/verified")

    def store_agent_run(self, metrics: Dict[str, Any]):
        """Store agent run metrics.

        Args:
            metrics: Dictionary with agent run metrics
        """
        import json

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO agent_runs (
                agent_name, framework, accuracy, cost_usd,
                tokens_used, latency_ms, success_rate, status, extra_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.get("agent_name"),
                metrics.get("framework"),
                metrics.get("accuracy"),
                metrics.get("cost_usd"),
                metrics.get("tokens_used"),
                metrics.get("latency_ms"),
                metrics.get("success_rate"),
                metrics.get("status", "success"),
                json.dumps(
                    {
                        k: v
                        for k, v in metrics.items()
                        if k
                        not in [
                            "agent_name",
                            "framework",
                            "accuracy",
                            "cost_usd",
                            "tokens_used",
                            "latency_ms",
                            "success_rate",
                            "status",
                        ]
                    }
                ),
            ),
        )
        self.conn.commit()
        logger.debug(f"Stored agent run for {metrics.get('agent_name')}")

    def store_optimization(self, metrics: Dict[str, Any]):
        """Store optimization run metrics.

        Args:
            metrics: Dictionary with optimization metrics
        """
        import json

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO optimization_runs (
                agent_name, optimizer, initial_score, final_score,
                improvement, iterations, population_size, generations,
                duration_seconds, best_prompt, evolution_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.get("agent_name"),
                metrics.get("optimizer", "GEPA"),
                metrics.get("initial_score"),
                metrics.get("final_score"),
                metrics.get("improvement"),
                metrics.get("iterations"),
                metrics.get("population_size"),
                metrics.get("generations"),
                metrics.get("duration_seconds"),
                metrics.get("best_prompt"),
                json.dumps(metrics.get("evolution_history"))
                if metrics.get("evolution_history")
                else None,
            ),
        )
        self.conn.commit()
        logger.debug(f"Stored optimization run for {metrics.get('agent_name')}")

    def store_protocol_usage(self, metrics: Dict[str, Any]):
        """Store protocol usage metrics.

        Args:
            metrics: Dictionary with protocol metrics
        """
        import json

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO protocol_usage (
                agent_name, protocol_type, server_uri, tools_discovered,
                tools_used, tool_success_rate, avg_latency_ms, total_calls
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.get("agent_name"),
                metrics.get("protocol_type"),
                metrics.get("server_uri"),
                metrics.get("tools_discovered"),
                json.dumps(metrics.get("tools_used", [])),
                metrics.get("tool_success_rate"),
                metrics.get("avg_latency_ms"),
                metrics.get("total_calls"),
            ),
        )
        self.conn.commit()
        logger.debug(f"Stored protocol usage for {metrics.get('agent_name')}")

    def store_cost(self, cost_data: Dict[str, Any]):
        """Store cost tracking data.

        Args:
            cost_data: Dictionary with cost information
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO cost_tracking (
                agent_name, provider, model, tokens_input,
                tokens_output, tokens_total, cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                cost_data.get("agent_name"),
                cost_data.get("provider"),
                cost_data.get("model"),
                cost_data.get("tokens_input"),
                cost_data.get("tokens_output"),
                cost_data.get("tokens_total"),
                cost_data.get("cost_usd"),
            ),
        )
        self.conn.commit()
        logger.debug(f"Stored cost data for {cost_data.get('agent_name')}")

    def store_framework_comparison(self, comparison: Dict[str, Any]):
        """Store framework comparison data.

        Args:
            comparison: Dictionary with framework comparison
        """
        import json

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO framework_comparisons (
                agent_name, frameworks_data, best_framework, best_accuracy
            ) VALUES (?, ?, ?, ?)
        """,
            (
                comparison.get("agent_name"),
                json.dumps(comparison.get("frameworks")),
                comparison.get("best_framework"),
                comparison.get("best_accuracy"),
            ),
        )
        self.conn.commit()
        logger.debug(f"Stored framework comparison for {comparison.get('agent_name')}")

    def get_agent_runs(
        self, agent_name: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get agent runs from storage.

        Args:
            agent_name: Optional agent name filter
            limit: Maximum number of runs to return
            offset: Offset for pagination

        Returns:
            List of agent run dictionaries
        """
        cursor = self.conn.cursor()

        if agent_name:
            cursor.execute(
                """
                SELECT * FROM agent_runs
                WHERE agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """,
                (agent_name, limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM agent_runs
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

        return [dict(row) for row in cursor.fetchall()]

    def get_optimizations(
        self,
        agent_name: Optional[str] = None,
        optimizer: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get optimization runs from storage.

        Args:
            agent_name: Optional agent name filter
            optimizer: Optional optimizer name filter
            limit: Maximum number to return

        Returns:
            List of optimization run dictionaries
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM optimization_runs"
        conditions = []
        params = []

        if agent_name:
            conditions.append("agent_name = ?")
            params.append(agent_name)
        if optimizer:
            conditions.append("optimizer = ?")
            params.append(optimizer)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_protocol_usage(
        self,
        agent_name: Optional[str] = None,
        protocol_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get protocol usage from storage.

        Args:
            agent_name: Optional agent name filter
            protocol_type: Optional protocol type filter
            limit: Maximum number to return

        Returns:
            List of protocol usage dictionaries
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM protocol_usage"
        conditions = []
        params = []

        if agent_name:
            conditions.append("agent_name = ?")
            params.append(agent_name)
        if protocol_type:
            conditions.append("protocol_type = ?")
            params.append(protocol_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_cost_summary(
        self, agent_name: Optional[str] = None, days: int = 30
    ) -> Dict[str, Any]:
        """Get cost summary for an agent or all agents.

        Args:
            agent_name: Optional agent name filter
            days: Number of days to include (default: 30)

        Returns:
            Dictionary with cost summary
        """
        cursor = self.conn.cursor()

        if agent_name:
            cursor.execute(
                """
                SELECT 
                    SUM(cost_usd) as total_cost,
                    SUM(tokens_total) as total_tokens,
                    COUNT(*) as total_calls,
                    AVG(cost_usd) as avg_cost_per_call
                FROM cost_tracking
                WHERE agent_name = ?
                AND timestamp >= datetime('now', '-' || ? || ' days')
            """,
                (agent_name, days),
            )
        else:
            cursor.execute(
                """
                SELECT 
                    SUM(cost_usd) as total_cost,
                    SUM(tokens_total) as total_tokens,
                    COUNT(*) as total_calls,
                    AVG(cost_usd) as avg_cost_per_call
                FROM cost_tracking
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """,
                (days,),
            )

        row = cursor.fetchone()

        return {
            "total_cost_usd": row["total_cost"] or 0,
            "total_tokens": row["total_tokens"] or 0,
            "total_calls": row["total_calls"] or 0,
            "avg_cost_per_call": row["avg_cost_per_call"] or 0,
            "days": days,
            "agent_name": agent_name or "all",
        }

    def get_optimization_summary(
        self, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get optimization summary.

        Args:
            agent_name: Optional agent name filter

        Returns:
            Dictionary with optimization summary
        """
        cursor = self.conn.cursor()

        if agent_name:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_optimizations,
                    AVG(improvement) as avg_improvement,
                    MAX(improvement) as max_improvement,
                    SUM(iterations) as total_iterations,
                    AVG(duration_seconds) as avg_duration
                FROM optimization_runs
                WHERE agent_name = ?
            """,
                (agent_name,),
            )
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_optimizations,
                    AVG(improvement) as avg_improvement,
                    MAX(improvement) as max_improvement,
                    SUM(iterations) as total_iterations,
                    AVG(duration_seconds) as avg_duration
                FROM optimization_runs
            """)

        row = cursor.fetchone()

        return {
            "total_optimizations": row["total_optimizations"] or 0,
            "avg_improvement": row["avg_improvement"] or 0,
            "max_improvement": row["max_improvement"] or 0,
            "total_iterations": row["total_iterations"] or 0,
            "avg_duration_seconds": row["avg_duration"] or 0,
            "agent_name": agent_name or "all",
        }

    def get_protocol_summary(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get protocol usage summary.

        Args:
            agent_name: Optional agent name filter

        Returns:
            Dictionary with protocol summary
        """
        cursor = self.conn.cursor()

        if agent_name:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(tools_discovered) as total_tools_discovered,
                    AVG(tool_success_rate) as avg_success_rate,
                    AVG(avg_latency_ms) as avg_latency,
                    SUM(total_calls) as total_tool_calls
                FROM protocol_usage
                WHERE agent_name = ?
            """,
                (agent_name,),
            )
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(tools_discovered) as total_tools_discovered,
                    AVG(tool_success_rate) as avg_success_rate,
                    AVG(avg_latency_ms) as avg_latency,
                    SUM(total_calls) as total_tool_calls
                FROM protocol_usage
            """)

        row = cursor.fetchone()

        return {
            "total_sessions": row["total_sessions"] or 0,
            "total_tools_discovered": row["total_tools_discovered"] or 0,
            "avg_success_rate": row["avg_success_rate"] or 0,
            "avg_latency_ms": row["avg_latency"] or 0,
            "total_tool_calls": row["total_tool_calls"] or 0,
            "agent_name": agent_name or "all",
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for dashboard.

        Returns:
            Dictionary with all summary data
        """
        return {
            "cost_summary": self.get_cost_summary(),
            "optimization_summary": self.get_optimization_summary(),
            "protocol_summary": self.get_protocol_summary(),
            "recent_runs": self.get_agent_runs(limit=10),
            "recent_optimizations": self.get_optimizations(limit=10),
            "recent_protocol_usage": self.get_protocol_usage(limit=10),
        }

    def export_to_mlflow(self, agent_name: Optional[str] = None):
        """Export data to MLFlow.

        Args:
            agent_name: Optional agent name filter
        """
        try:
            import mlflow

            runs = self.get_agent_runs(agent_name=agent_name)

            for run in runs:
                with mlflow.start_run(run_name=f"{run['agent_name']}_export"):
                    mlflow.log_params(
                        {
                            "agent_name": run["agent_name"],
                            "framework": run["framework"],
                        }
                    )

                    if run["accuracy"]:
                        mlflow.log_metric("accuracy", run["accuracy"])
                    if run["cost_usd"]:
                        mlflow.log_metric("cost_usd", run["cost_usd"])
                    if run["tokens_used"]:
                        mlflow.log_metric("tokens_used", run["tokens_used"])

            logger.info(f"Exported {len(runs)} runs to MLFlow")

        except ImportError:
            logger.error("MLFlow not available - install with: pip install mlflow")
        except Exception as e:
            logger.error(f"Failed to export to MLFlow: {e}")

    def export_to_wandb(self, agent_name: Optional[str] = None):
        """Export data to Weights & Biases.

        Args:
            agent_name: Optional agent name filter
        """
        try:
            import wandb

            wandb.init(project="superoptix", name=f"{agent_name}_export")

            runs = self.get_agent_runs(agent_name=agent_name)

            for run in runs:
                wandb.log(
                    {
                        f"agent/{run['agent_name']}/accuracy": run["accuracy"],
                        f"agent/{run['agent_name']}/cost": run["cost_usd"],
                        f"agent/{run['agent_name']}/tokens": run["tokens_used"],
                    }
                )

            wandb.finish()
            logger.info(f"Exported {len(runs)} runs to W&B")

        except ImportError:
            logger.error("W&B not available - install with: pip install wandb")
        except Exception as e:
            logger.error(f"Failed to export to W&B: {e}")

    def cleanup_old_data(self, days: int = 90):
        """Clean up data older than specified days.

        Args:
            days: Number of days to keep (default: 90)
        """
        cursor = self.conn.cursor()

        # Clean up agent runs
        cursor.execute(
            """
            DELETE FROM agent_runs
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """,
            (days,),
        )

        # Clean up optimization runs
        cursor.execute(
            """
            DELETE FROM optimization_runs
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """,
            (days,),
        )

        # Clean up protocol usage
        cursor.execute(
            """
            DELETE FROM protocol_usage
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """,
            (days,),
        )

        # Clean up cost tracking
        cursor.execute(
            """
            DELETE FROM cost_tracking
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """,
            (days,),
        )

        self.conn.commit()
        logger.info(f"Cleaned up data older than {days} days")

    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.debug("Database connection closed")
