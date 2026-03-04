"""
Runtime feature detection for SurrealDB capabilities.

Different SurrealDB server versions support different features.
This module probes the connected server to determine what's available,
enabling graceful fallbacks when newer features aren't supported.

Usage:
    from superoptix.utils.surrealdb_features import SurrealDBFeatureDetector

    with Surreal(url) as db:
        db.use(ns, database)
        detector = SurrealDBFeatureDetector(db)
        if detector.has("relate"):
            # use graph features
        else:
            # fall back to vector-only
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SurrealDBFeatureDetector:
    """Detect SurrealDB server capabilities via lightweight runtime probes.

    Each probe is a minimal SurrealQL query that exercises a specific feature.
    Results are cached per instance so a feature is probed at most once per
    connection session.
    """

    # Probe queries designed to be safe (no side effects, no real tables).
    # A probe returning successfully means the feature is available.
    # A syntax/unsupported error means it's not.
    _PROBES: dict[str, Optional[str]] = {
        # Graph traversal parser support (used by GraphRAG expansion).
        # This is a read-only probe with no side effects.
        "relate": (
            "SELECT * FROM ONLY __superoptix_feature_probe__:a"
            "->__superoptix_feature_probe_edge__->* LIMIT 1;"
        ),
        # Live queries require WebSocket — checked by connection scheme, not query.
        "live_select": None,
        # Vector similarity functions (available in recent SurrealDB versions).
        "vector_cosine": "RETURN vector::similarity::cosine([1.0, 2.0], [3.0, 4.0]);",
        # Full-text search helper function (context-free probe).
        "search_score": "RETURN search::rrf([0.1, 0.2], [0.2, 0.1]);",
        # Server-side embedding function (SurrealDB 3.0 Surrealism plugin).
        "fn_embed": None,  # Probed dynamically with the actual function name.
    }

    # Errors that indicate a feature is unavailable (vs connection/auth errors).
    _FEATURE_ABSENT_TOKENS = (
        "syntax",
        "not found",
        "undefined",
        "unsupported",
        "unknown function",
        "not yet implemented",
        "parse error",
        "invalid function",
        "invalid arguments",
        "incorrect arguments",
    )

    def __init__(self, db: Any) -> None:
        """Initialize with an already-connected SurrealDB client.

        Args:
            db: A connected ``surrealdb.Surreal`` instance (already signed in
                and ``use()``'d on the target namespace/database).
        """
        self.db = db
        self._cache: dict[str, bool] = {}

    def has(self, feature: str) -> bool:
        """Check whether *feature* is available on the connected server.

        Returns ``True`` if the feature is available, ``False`` if it's not
        supported by this server version.  Connection-level errors (timeout,
        auth failure, etc.) are **not** caught — they propagate normally.

        Results are cached for the lifetime of this detector instance.
        """
        if feature in self._cache:
            return self._cache[feature]

        # Special cases that don't use a query probe.
        if feature == "live_select":
            result = self._check_live_select_support()
            self._cache[feature] = result
            return result

        if feature == "fn_embed":
            # Cannot probe without knowing the function name.
            # Caller should use probe_function() instead.
            self._cache[feature] = False
            return False

        probe = self._PROBES.get(feature)
        if probe is None:
            logger.debug("No probe defined for feature '%s'; assuming unavailable", feature)
            self._cache[feature] = False
            return False

        available = self._run_probe(feature, probe)
        self._cache[feature] = available
        return available

    def probe_function(self, function_name: str) -> bool:
        """Check whether a specific SurrealQL function exists.

        Useful for testing ``fn::embed``, ``ml::embed``, or custom functions.

        Args:
            function_name: The function call to test, e.g. ``"fn::embed('test')"``
                           or ``"ml::embed('all-MiniLM-L6-v2', 'hello')"``
        """
        cache_key = f"function:{function_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        probe_sql = f"RETURN {function_name};"
        available = self._run_probe(cache_key, probe_sql)
        self._cache[cache_key] = available
        return available

    def check_all(self) -> dict[str, bool]:
        """Run all built-in probes and return a feature availability map."""
        results: dict[str, bool] = {}
        for feature in self._PROBES:
            results[feature] = self.has(feature)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_probe(self, feature: str, sql: str) -> bool:
        """Execute a probe query and interpret the result."""
        try:
            self.db.query(sql)
            logger.debug("Feature '%s' is available", feature)
            return True
        except Exception as e:
            err = str(e).lower()
            if any(token in err for token in self._FEATURE_ABSENT_TOKENS):
                logger.debug("Feature '%s' is not available: %s", feature, e)
                return False
            # Connection errors, auth errors, etc. should propagate.
            raise

    def _check_live_select_support(self) -> bool:
        """Live queries require a WebSocket transport."""
        try:
            url = getattr(self.db, "url", None) or getattr(self.db, "_url", None)
            if url is None:
                return False
            parsed = urlparse(str(url))
            return parsed.scheme.lower() in {"ws", "wss"}
        except Exception:
            return False
