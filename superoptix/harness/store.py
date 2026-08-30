"""Session persistence for the SuperOptiX harness runtime."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StoredMessage:
    """One stored session message."""

    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_now)


@dataclass
class SessionState:
    """Persisted harness session state."""

    session_id: str
    messages: list[StoredMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def append(self, role: str, content: str, **metadata: Any) -> None:
        self.messages.append(
            StoredMessage(role=role, content=content, metadata=dict(metadata))
        )
        self.updated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "messages": [asdict(message) for message in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SessionState":
        messages = [
            StoredMessage(
                role=str(item.get("role") or ""),
                content=str(item.get("content") or ""),
                metadata=dict(item.get("metadata") or {}),
                timestamp=str(item.get("timestamp") or _now()),
            )
            for item in payload.get("messages", []) or []
            if isinstance(item, dict)
        ]
        return cls(
            session_id=str(payload.get("session_id") or "default"),
            messages=messages,
            metadata=dict(payload.get("metadata") or {}),
            created_at=str(payload.get("created_at") or _now()),
            updated_at=str(payload.get("updated_at") or _now()),
        )


class SessionStore(Protocol):
    """Storage contract for harness sessions."""

    async def load(self, session_id: str) -> SessionState | None:
        """Load a session state by id."""

    async def save(self, state: SessionState) -> None:
        """Persist session state."""

    async def delete(self, session_id: str) -> None:
        """Delete a session state."""


class InMemorySessionStore:
    """Process-local session store."""

    def __init__(self):
        self._states: dict[str, SessionState] = {}

    async def load(self, session_id: str) -> SessionState | None:
        return self._states.get(session_id)

    async def save(self, state: SessionState) -> None:
        self._states[state.session_id] = state

    async def delete(self, session_id: str) -> None:
        self._states.pop(session_id, None)


class FileSessionStore:
    """JSON session store backed by a directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def load(self, session_id: str) -> SessionState | None:
        path = self._path_for(session_id)
        if not path.exists():
            return None
        return await asyncio.to_thread(self._load_sync, path)

    async def save(self, state: SessionState) -> None:
        path = self._path_for(state.session_id)
        await asyncio.to_thread(self._save_sync, path, state)

    async def delete(self, session_id: str) -> None:
        path = self._path_for(session_id)
        if path.exists():
            await asyncio.to_thread(path.unlink)

    def _path_for(self, session_id: str) -> Path:
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.json"

    @staticmethod
    def _load_sync(path: Path) -> SessionState:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid harness session file: {path}")
        return SessionState.from_dict(payload)

    @staticmethod
    def _save_sync(path: Path, state: SessionState) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, indent=2, sort_keys=True)
            handle.write("\n")
