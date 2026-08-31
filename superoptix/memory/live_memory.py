"""Live memory subscriber using SurrealDB LIVE SELECT.

Provides real-time change notification for agent memory keys, enabling
multi-agent coordination and reactive workflows.

Requirements:
- WebSocket connection (ws:// or wss://)
- SurrealDB Python SDK with live query support
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Reconnect policy constants
_MAX_RECONNECT_ATTEMPTS = 3
_RECONNECT_BASE_DELAY_S = 2.0


class LiveMemorySubscriber:
    """Subscribe to real-time SurrealDB memory changes via LIVE SELECT.

    Only works with WebSocket connections (ws:// or wss://). Will raise
    ``ValueError`` at construction time for non-WebSocket URLs.

    Reconnect behaviour
    -------------------
    When the underlying connection drops, the subscriber attempts to
    re-establish up to ``reconnect_attempts`` times using exponential
    back-off (base delay doubles each attempt).  If all attempts fail the
    connection error is re-raised.

    Callback isolation
    ------------------
    Exceptions raised inside a callback are caught, logged at ERROR level,
    and swallowed.  A single bad callback will never kill the subscription.

    Example
    -------
    ::

        backend = SurrealDBBackend(url="ws://localhost:8000", ...)
        subscriber = LiveMemorySubscriber(backend)

        def on_change(event: dict):
            print("memory changed:", event)

        sub_id = await subscriber.subscribe("superoptix_memory", on_change)
        # ... later ...
        await subscriber.unsubscribe(sub_id)
        await subscriber.close()
    """

    def __init__(
        self,
        backend: Any,
        *,
        reconnect_attempts: int = _MAX_RECONNECT_ATTEMPTS,
        reconnect_delay_s: float = _RECONNECT_BASE_DELAY_S,
    ) -> None:
        url: str = getattr(backend, "url", "") or ""
        if not self._is_websocket_url(url):
            raise ValueError(
                "Live queries require a WebSocket connection (ws:// or wss://). "
                f"Current backend URL: '{url!r}'. "
                "Use ws://localhost:8000 or wss://... instead."
            )

        self._backend = backend
        self._url = url
        self._reconnect_attempts = max(1, int(reconnect_attempts))
        self._reconnect_delay_s = max(0.1, float(reconnect_delay_s))

        # subscription_id -> (live_query_id, table, callback)
        self._subscriptions: Dict[str, tuple] = {}
        self._next_sub_id: int = 1
        self._db: Any = None  # async SurrealDB connection
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Establish the persistent WebSocket connection."""
        async with self._lock:
            if self._db is not None:
                return
            self._db = await self._open_connection()
            logger.debug("LiveMemorySubscriber: connected to %s", self._url)

    async def subscribe(
        self, table: str, callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """Register a LIVE SELECT on *table*.

        Parameters
        ----------
        table:
            SurrealDB table name to watch (e.g. ``"superoptix_memory"``).
        callback:
            Called with the raw SurrealDB live-event dict on each change.
            Must not raise — exceptions are caught and logged.

        Returns
        -------
        str
            A subscription ID that can be passed to :meth:`unsubscribe`.
        """
        await self._ensure_connected()

        sub_id = f"sub_{self._next_sub_id}"
        self._next_sub_id += 1

        def _safe_callback(event: Dict[str, Any]) -> None:
            try:
                callback(event)
            except Exception as exc:
                logger.error(
                    "LiveMemorySubscriber: callback raised for sub %s: %s",
                    sub_id,
                    exc,
                    exc_info=True,
                )

        live_query_id = await self._live_select(table, _safe_callback)
        self._subscriptions[sub_id] = (live_query_id, table, _safe_callback)
        logger.info(
            "LiveMemorySubscriber: subscribed to '%s' (sub_id=%s, live_id=%s)",
            table,
            sub_id,
            live_query_id,
        )
        return sub_id

    async def unsubscribe(self, sub_id: str) -> None:
        """Stop receiving events for *sub_id*.

        Sends ``KILL`` to SurrealDB and removes the local subscription.
        Non-fatal if the subscription ID is unknown.
        """
        entry = self._subscriptions.pop(sub_id, None)
        if entry is None:
            logger.warning("LiveMemorySubscriber: unknown sub_id '%s'", sub_id)
            return

        live_query_id, table, _ = entry
        try:
            if self._db is not None:
                await self._db.kill(live_query_id)
            logger.info(
                "LiveMemorySubscriber: unsubscribed from '%s' (sub_id=%s)",
                table,
                sub_id,
            )
        except Exception as exc:
            logger.warning(
                "LiveMemorySubscriber: KILL failed for sub_id=%s: %s", sub_id, exc
            )

    async def close(self) -> None:
        """Kill all active subscriptions and close the connection."""
        for sub_id in list(self._subscriptions.keys()):
            await self.unsubscribe(sub_id)

        async with self._lock:
            if self._db is not None:
                try:
                    await self._db.close()
                except Exception:
                    pass
                self._db = None
        logger.debug("LiveMemorySubscriber: closed")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_websocket_url(url: str) -> bool:
        """Return True iff the URL uses ws or wss scheme."""
        parsed = urlparse(url)
        return parsed.scheme.lower() in {"ws", "wss"}

    async def _ensure_connected(self) -> None:
        """Connect (or reconnect) if not already connected."""
        if self._db is None:
            await self.connect()

    async def _open_connection(self) -> Any:
        """Open an async SurrealDB connection with exponential-backoff reconnect."""
        try:
            from surrealdb import AsyncSurreal  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "LiveMemorySubscriber requires the 'surrealdb' package (>=1.0.0) "
                "with async support. Install with: uv pip install surrealdb"
            ) from exc

        last_exc: Exception | None = None
        for attempt in range(self._reconnect_attempts):
            try:
                db = AsyncSurreal(self._url)
                await db.connect()

                if not self._backend.skip_signin:
                    await db.signin(
                        {
                            "username": self._backend.username,
                            "password": self._backend.password,
                        }
                    )
                await db.use(self._backend.namespace, self._backend.database)
                return db

            except Exception as exc:
                last_exc = exc
                delay = self._reconnect_delay_s * (2**attempt)
                logger.warning(
                    "LiveMemorySubscriber: connection attempt %d/%d failed (%s). "
                    "Retrying in %.1fs...",
                    attempt + 1,
                    self._reconnect_attempts,
                    exc,
                    delay,
                )
                if attempt < self._reconnect_attempts - 1:
                    await asyncio.sleep(delay)

        raise RuntimeError(
            f"LiveMemorySubscriber: failed to connect after {self._reconnect_attempts} "
            f"attempts. Last error: {last_exc}"
        )

    async def _live_select(self, table: str, callback: Callable) -> str:
        """Issue a LIVE SELECT on *table* and register *callback*.

        Returns the live query UUID issued by SurrealDB.
        """
        try:
            # SDK >=1.0 async API
            live_id = await self._db.live(table, callback=callback)
            return str(live_id)
        except AttributeError:
            # Fallback: issue raw SQL
            result = await self._db.query(f"LIVE SELECT * FROM {table};")
            # Extract UUID from result
            rows = result[0].get("result") if result else None
            if rows:
                return str(rows)
            raise RuntimeError(f"Could not obtain live query ID for table '{table}'")

    async def _reconnect_all(self) -> None:
        """Re-open connection and re-register all active subscriptions."""
        async with self._lock:
            self._db = None
            self._db = await self._open_connection()

        logger.info(
            "LiveMemorySubscriber: reconnected; re-registering %d subscription(s)",
            len(self._subscriptions),
        )

        # Re-register subscriptions with new live query IDs
        new_subs: Dict[str, tuple] = {}
        for sub_id, (_, table, cb) in list(self._subscriptions.items()):
            try:
                new_live_id = await self._live_select(table, cb)
                new_subs[sub_id] = (new_live_id, table, cb)
                logger.debug(
                    "LiveMemorySubscriber: re-registered sub_id=%s table=%s",
                    sub_id,
                    table,
                )
            except Exception as exc:
                logger.error(
                    "LiveMemorySubscriber: failed to re-register sub_id=%s: %s",
                    sub_id,
                    exc,
                )

        self._subscriptions = new_subs
