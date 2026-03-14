"""Registry for framework-neutral runtime adapters."""

from __future__ import annotations

from typing import Any, Callable, Dict

from superoptix.runtime.base import AgentRuntime


RuntimeFactory = Callable[[Any], AgentRuntime]


class RuntimeRegistry:
    """Store factories that wrap framework pipelines as AgentRuntime objects."""

    def __init__(self):
        self._factories: Dict[str, RuntimeFactory] = {}

    def register(self, name: str, factory: RuntimeFactory) -> None:
        self._factories[str(name).strip().lower()] = factory

    def create(self, name: str, target: Any) -> AgentRuntime:
        key = str(name).strip().lower()
        if key not in self._factories:
            available = ", ".join(sorted(self._factories.keys()))
            raise ValueError(
                f"Runtime adapter '{name}' is not registered. Available: {available}"
            )
        return self._factories[key](target)

    def registered(self) -> list[str]:
        return sorted(self._factories.keys())


runtime_registry = RuntimeRegistry()

