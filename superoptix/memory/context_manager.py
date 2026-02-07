"""Context manager for managing agent context and state across interactions."""

import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .episodic_memory import EpisodicMemory
from .long_term_memory import LongTermMemory
from .memory_backends import MemoryBackend, SQLiteBackend
from .short_term_memory import ShortTermMemory


@dataclass
class ContextFrame:
    """Represents a context frame with scope and data."""

    id: str
    name: str
    scope: str  # 'global', 'session', 'task', 'local'
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    expires_at: Optional[str]
    priority: int


class ContextManager:
    """Manages agent context and state across different scopes and interactions."""

    def __init__(
        self,
        agent_id: str,
        short_term_memory: Optional[ShortTermMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        episodic_memory: Optional[EpisodicMemory] = None,
        backend: Optional[MemoryBackend] = None,
    ):
        """Initialize context manager."""
        self.agent_id = agent_id
        resolved_backend = backend or SQLiteBackend()
        self.short_term_memory = short_term_memory or ShortTermMemory()
        # Disable embeddings by default in context manager to avoid network/model
        # loads during lightweight context operations and tests.
        self.long_term_memory = long_term_memory or LongTermMemory(
            backend=resolved_backend,
            enable_embeddings=False,
        )
        self.episodic_memory = episodic_memory or EpisodicMemory(
            backend=resolved_backend
        )
        self.backend = resolved_backend

        self._lock = threading.RLock()
        self._context_stack = []
        self._active_contexts = {}
        self._context_history = []

        self._initialize_default_contexts()

    def _initialize_default_contexts(self):
        """Initialize default context frames."""
        try:
            with self._lock:
                global_context = self._create_context_frame(
                    name="global",
                    scope="global",
                    data={
                        "agent_id": self.agent_id,
                        "created_at": datetime.now().isoformat(),
                        "preferences": {},
                        "capabilities": [],
                        "learned_patterns": {},
                    },
                    priority=10,
                )

                session_context = self._create_context_frame(
                    name="session",
                    scope="session",
                    data={
                        "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "start_time": datetime.now().isoformat(),
                        "interaction_count": 0,
                        "current_goals": [],
                        "active_tasks": [],
                    },
                    priority=8,
                )

                self._active_contexts["global"] = global_context
                self._active_contexts["session"] = session_context

        except Exception as e:
            print(f"Error initializing default contexts: {e}")

    def _create_context_frame(
        self,
        name: str,
        scope: str,
        data: Dict[str, Any],
        priority: int = 5,
        ttl: Optional[int] = None,
    ) -> ContextFrame:
        """Create a new context frame."""
        current_time = datetime.now().isoformat()
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

        return ContextFrame(
            id=f"{scope}_{name}_{datetime.now().timestamp()}",
            name=name,
            scope=scope,
            data=data,
            created_at=current_time,
            updated_at=current_time,
            expires_at=expires_at,
            priority=priority,
        )

    def push_context(
        self,
        name: str,
        scope: str,
        data: Dict[str, Any],
        priority: int = 5,
        ttl: Optional[int] = None,
    ) -> str:
        """Push a new context frame onto the stack."""
        try:
            with self._lock:
                context_frame = self._create_context_frame(
                    name, scope, data, priority, ttl
                )

                self._context_stack.append(context_frame)

                if (
                    scope not in self._active_contexts
                    or self._active_contexts[scope].priority <= priority
                ):
                    self._active_contexts[scope] = context_frame

                key = f"context:{self.agent_id}:{context_frame.id}"
                self.backend.store(key, asdict(context_frame), ttl=ttl)

                self._record_context_change("push", context_frame)

                return context_frame.id

        except Exception as e:
            print(f"Error pushing context: {e}")
            return None

    def get_context(self, scope: str, key: Optional[str] = None) -> Any:
        """Get context data by scope and optional key."""
        try:
            with self._lock:
                if scope not in self._active_contexts:
                    return None

                context_frame = self._active_contexts[scope]

                if context_frame.expires_at:
                    if datetime.now().isoformat() > context_frame.expires_at:
                        self._expire_context(context_frame)
                        return None

                if key:
                    return context_frame.data.get(key)
                else:
                    return context_frame.data

        except Exception as e:
            print(f"Error getting context: {e}")
            return None

    def set_context(self, scope: str, key: str, value: Any) -> bool:
        """Set a value in the specified context scope."""
        try:
            with self._lock:
                if scope not in self._active_contexts:
                    self.push_context(
                        name=f"auto_{scope}", scope=scope, data={key: value}
                    )
                    return True

                context_frame = self._active_contexts[scope]
                context_frame.data[key] = value
                context_frame.updated_at = datetime.now().isoformat()

                storage_key = f"context:{self.agent_id}:{context_frame.id}"
                self.backend.store(storage_key, asdict(context_frame))

                self._record_context_change("update", context_frame, key)

                return True

        except Exception as e:
            print(f"Error setting context: {e}")
            return False

    def get_full_context(self) -> Dict[str, Any]:
        """Get consolidated context from all active scopes."""
        try:
            with self._lock:
                full_context = {}

                sorted_contexts = sorted(
                    self._active_contexts.values(), key=lambda x: x.priority
                )

                for context_frame in sorted_contexts:
                    if context_frame.expires_at:
                        if datetime.now().isoformat() > context_frame.expires_at:
                            self._expire_context(context_frame)
                            continue

                    scoped_data = {
                        f"{context_frame.scope}_{key}": value
                        for key, value in context_frame.data.items()
                    }
                    full_context.update(scoped_data)
                    full_context.update(context_frame.data)

                return full_context

        except Exception as e:
            print(f"Error getting full context: {e}")
            return {}

    def _expire_context(self, context_frame: ContextFrame):
        """Handle context expiration."""
        try:
            if context_frame.scope in self._active_contexts:
                if self._active_contexts[context_frame.scope].id == context_frame.id:
                    self._active_contexts.pop(context_frame.scope, None)

            key = f"context:{self.agent_id}:{context_frame.id}"
            self.backend.delete(key)

            self._record_context_change("expire", context_frame)

        except Exception as e:
            print(f"Error expiring context: {e}")

    def _record_context_change(
        self, action: str, context_frame: ContextFrame, key: str = None
    ):
        """Record context change in history."""
        try:
            change_record = {
                "action": action,
                "context_id": context_frame.id,
                "scope": context_frame.scope,
                "name": context_frame.name,
                "timestamp": datetime.now().isoformat(),
                "key": key,
            }

            self._context_history.append(change_record)

            if len(self._context_history) > 1000:
                self._context_history = self._context_history[-500:]

        except Exception as e:
            print(f"Error recording context change: {e}")

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context state."""
        try:
            with self._lock:
                summary = {
                    "agent_id": self.agent_id,
                    "active_scopes": list(self._active_contexts.keys()),
                    "context_stack_size": len(self._context_stack),
                    "contexts": {},
                }

                for scope, context_frame in self._active_contexts.items():
                    summary["contexts"][scope] = {
                        "name": context_frame.name,
                        "priority": context_frame.priority,
                        "created_at": context_frame.created_at,
                        "updated_at": context_frame.updated_at,
                        "expires_at": context_frame.expires_at,
                        "data_keys": list(context_frame.data.keys()),
                    }

                return summary

        except Exception as e:
            print(f"Error getting context summary: {e}")
            return {}

    def clear_context(self, scope: Optional[str] = None):
        """Clear context data."""
        try:
            with self._lock:
                if scope:
                    if scope in self._active_contexts:
                        context_frame = self._active_contexts.pop(scope)
                        key = f"context:{self.agent_id}:{context_frame.id}"
                        self.backend.delete(key)

                    self._context_stack = [
                        frame for frame in self._context_stack if frame.scope != scope
                    ]
                else:
                    for scope_name, context_frame in self._active_contexts.items():
                        if scope_name != "global":
                            key = f"context:{self.agent_id}:{context_frame.id}"
                            self.backend.delete(key)

                    global_context = self._active_contexts.get("global")
                    self._active_contexts = {}
                    if global_context:
                        self._active_contexts["global"] = global_context

                    self._context_stack = []

        except Exception as e:
            print(f"Error clearing context: {e}")
