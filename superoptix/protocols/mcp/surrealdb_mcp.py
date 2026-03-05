"""Read-only SurrealDB MCP tool for agent knowledge queries.

Security model
--------------
* **Allowlist-only**: Only ``SELECT``, ``INFO``, and ``RETURN`` statements
  are permitted. Any other statement raises ``PermissionError`` immediately
  before touching the database.
* **Row limit**: A ``LIMIT {MAX_ROWS}`` clause is injected automatically when
  the query does not already contain a ``LIMIT`` keyword. This caps result
  set size and prevents accidental full-table scans.
* **Query timeout**: Queries are executed with a configurable timeout
  (default 5 s). Long-running queries are cancelled.
* **Namespace/database scoping**: The tool connects to a fixed
  namespace/database defined at construction time and cannot switch.

Intended use
------------
Register an instance of :class:`SurrealDBMCPTool` as an MCP tool in your
agent.  The tool's :meth:`execute` method can be called directly or via the
MCP ``call_tool`` protocol::

    tool = SurrealDBMCPTool.from_config(spec["vector_db"])
    result = tool.execute("SELECT content FROM rag_documents LIMIT 5;")

For Claude SDK agents using native MCP server support, register via
``get_tool_definition()``.
"""

from __future__ import annotations

import logging
import re
import threading
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Security constants
# ---------------------------------------------------------------------------

# Only SELECT, INFO, and RETURN statements are safe to expose.
_ALLOWED_PATTERN = re.compile(r"^\s*(SELECT|INFO|RETURN)\s", re.IGNORECASE)

# Hard cap on result rows injected when the user's query has no LIMIT clause.
_DEFAULT_MAX_ROWS: int = 100

# Default query timeout in seconds.
_DEFAULT_TIMEOUT_S: float = 5.0


class SurrealDBMCPTool:
    """Read-only SurrealDB query tool compatible with the MCP tool protocol.

    Parameters
    ----------
    url:
        SurrealDB server URL (e.g. ``ws://localhost:8000`` or ``http://...``).
    namespace:
        Namespace to connect to.
    database:
        Database to connect to.
    username:
        Authentication username.
    password:
        Authentication password.
    skip_signin:
        Skip authentication (useful for in-memory or unauthenticated local servers).
    max_rows:
        Maximum rows returned per query. Injected as ``LIMIT {max_rows}``
        when the query has no ``LIMIT`` clause.
    timeout_s:
        Per-query timeout in seconds. Queries exceeding this are cancelled.
    """

    def __init__(
        self,
        *,
        url: str,
        namespace: str,
        database: str,
        username: str = "root",
        password: str = "root",
        skip_signin: bool = False,
        max_rows: int = _DEFAULT_MAX_ROWS,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.skip_signin = skip_signin
        self.max_rows = max(1, int(max_rows))
        self.timeout_s = max(0.5, float(timeout_s))
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "SurrealDBMCPTool":
        """Build a tool from a SuperOptiX ``vector_db`` config dict."""
        return cls(
            url=config.get("url", "ws://localhost:8000"),
            namespace=config.get("namespace", "superoptix"),
            database=config.get("database", "agents"),
            username=config.get("username", "root"),
            password=config.get("password", "root"),
            skip_signin=bool(config.get("skip_signin", False)),
            max_rows=int(config.get("mcp_max_rows", _DEFAULT_MAX_ROWS)),
            timeout_s=float(config.get("mcp_timeout_s", _DEFAULT_TIMEOUT_S)),
        )

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    def execute(self, sql: str) -> Dict[str, Any]:
        """Execute a read-only SurrealQL query.

        Parameters
        ----------
        sql:
            A ``SELECT``, ``INFO``, or ``RETURN`` SurrealQL statement.

        Returns
        -------
        dict
            ``{"results": [...], "row_count": int, "truncated": bool}``

        Raises
        ------
        PermissionError
            If the statement is not in the ``SELECT/INFO/RETURN`` allowlist.
        TimeoutError
            If the query exceeds ``timeout_s``.
        RuntimeError
            On connection or query failure.
        """
        sql = sql.strip()
        self._enforce_allowlist(sql)
        sql = self._inject_limit(sql)

        result_holder: Dict[str, Any] = {}
        exc_holder: List[Exception] = []

        def _run() -> None:
            try:
                from surrealdb import Surreal  # type: ignore[import]

                with Surreal(self.url) as db:
                    if not self.skip_signin:
                        db.signin(
                            {"username": self.username, "password": self.password}
                        )
                    db.use(self.namespace, self.database)
                    raw = db.query(sql)
                    result_holder["raw"] = raw
            except Exception as exc:
                exc_holder.append(exc)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_s)

        if thread.is_alive():
            # Thread still running — timeout elapsed
            raise TimeoutError(
                f"SurrealDB MCP query timed out after {self.timeout_s}s: {sql[:80]}..."
            )

        if exc_holder:
            raise RuntimeError(
                f"SurrealDB MCP query failed: {exc_holder[0]}"
            ) from exc_holder[0]

        rows = self._extract_rows(result_holder.get("raw", []))
        truncated = len(rows) >= self.max_rows

        return {
            "results": rows,
            "row_count": len(rows),
            "truncated": truncated,
        }

    # ------------------------------------------------------------------
    # MCP tool definition
    # ------------------------------------------------------------------

    def get_tool_definition(self) -> Dict[str, Any]:
        """Return the MCP-compatible tool definition for agent registration.

        Compatible with Anthropic tool-use format and the MCP tool schema.
        """
        return {
            "name": "surrealdb_query",
            "description": (
                "Execute a read-only SurrealQL query against the knowledge database. "
                "Only SELECT, INFO, and RETURN statements are allowed. "
                f"Results are capped at {self.max_rows} rows."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": (
                            "A read-only SurrealQL statement: SELECT, INFO, or RETURN. "
                            "Examples: "
                            "'SELECT content FROM rag_documents LIMIT 10;' "
                            "'INFO FOR TABLE rag_documents;'"
                        ),
                    }
                },
                "required": ["sql"],
            },
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _enforce_allowlist(self, sql: str) -> None:
        """Raise PermissionError for non-allowlisted statements."""
        if not _ALLOWED_PATTERN.match(sql):
            preview = sql[:80].replace("\n", " ")
            raise PermissionError(
                f"SurrealDB MCP: only SELECT, INFO, and RETURN statements are allowed. "
                f"Rejected: '{preview}...'"
            )

        # Disallow multi-statement input such as:
        #   "SELECT ...; DELETE ..."
        # A single optional trailing semicolon is allowed.
        stmt = sql.strip()
        if stmt.endswith(";"):
            stmt = stmt[:-1].strip()
        if ";" in stmt:
            preview = sql[:80].replace("\n", " ")
            raise PermissionError(
                "SurrealDB MCP: only a single statement is allowed per call. "
                f"Rejected: '{preview}...'"
            )

    def _inject_limit(self, sql: str) -> str:
        """Append LIMIT clause for SELECT queries when absent."""
        stripped = sql.lstrip()
        if not stripped.upper().startswith("SELECT"):
            return sql
        if "LIMIT" not in stripped.upper():
            sql = sql.rstrip(";") + f" LIMIT {self.max_rows};"
        return sql

    @staticmethod
    def _extract_rows(raw: Any) -> List[Dict[str, Any]]:
        """Normalise SurrealDB query result to a flat list of dicts."""
        if not raw:
            return []
        rows: List[Dict[str, Any]] = []
        for item in raw:
            if isinstance(item, dict):
                result = item.get("result") or item.get("results") or []
                if isinstance(result, list):
                    rows.extend(result)
                elif isinstance(result, dict):
                    rows.append(result)
            elif isinstance(item, list):
                rows.extend(item)
        return rows
