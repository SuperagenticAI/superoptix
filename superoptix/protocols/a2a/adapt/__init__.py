"""Adapt an agent someone already built into an A2A 1.0 endpoint.

The path is: introspect the agent -> generate the SuperSpec IR -> emit an Agent
Card and a server. The user never writes a SuperSpec, and their agent is not
modified.
"""

from superoptix.protocols.a2a.adapt import crewai as _crewai  # noqa: F401
from superoptix.protocols.a2a.adapt import dspy as _dspy  # noqa: F401
from superoptix.protocols.a2a.adapt.base import (
    AdaptError,
    AgentSpec,
    Skill,
    available,
    detect,
    get,
    load_entrypoint,
)
from superoptix.protocols.a2a.adapt.emit import build_card, emit

__all__ = [
    "AdaptError",
    "AgentSpec",
    "Skill",
    "available",
    "build_card",
    "detect",
    "emit",
    "get",
    "load_entrypoint",
]
