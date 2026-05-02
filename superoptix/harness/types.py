"""Shared types for the SuperOptiX harness runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class Skill:
    """Markdown-defined reusable workflow."""

    name: str
    description: str = ""
    instructions: str = ""
    path: Path | None = None


@dataclass(frozen=True)
class Role:
    """Markdown-defined role overlay."""

    name: str
    description: str = ""
    instructions: str = ""
    model: str | None = None
    path: Path | None = None


@dataclass(frozen=True)
class HarnessContext:
    """Discovered project context for one harness working directory."""

    cwd: Path
    system_prompt: str = ""
    skills: dict[str, Skill] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)


@dataclass
class HarnessRunResult:
    """Normalized response from a framework backend."""

    text: str
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class HarnessBackend(Protocol):
    """Minimal backend contract used by harness sessions."""

    name: str

    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        agent_name: str,
        cwd: Path | None = None,
        sandbox: Any | None = None,
        model: str | None = None,
        model_config: dict[str, Any] | None = None,
        spec_data: dict[str, Any] | None = None,
        tools: list[Any] | None = None,
    ) -> HarnessRunResult:
        """Run one prompt turn and return normalized text."""
