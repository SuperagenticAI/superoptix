"""Protocol-first agent support for SuperOptiX.

This module provides the foundation for building protocol-first agents
that treat communication protocols (like MCP) as first-class primitives.

Vendored from Agenspy project and adapted for SuperOptiX.
"""

from superoptix.protocols.base import BaseProtocol, ProtocolType
from superoptix.protocols.registry import ProtocolRegistry, registry

__all__ = [
    "BaseProtocol",
    "ProtocolType",
    "ProtocolRegistry",
    "registry",
]
