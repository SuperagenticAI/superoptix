"""Base agent classes for SuperOptiX.

This module provides base agent implementations for different paradigms:
- Protocol-first agents (using Agenspy approach)
- Tool-first agents (using DSPy approach)

Vendored from Agenspy project and adapted for SuperOptiX.
"""

from superoptix.agent_bases.protocol_agent import ProtocolAgent

__all__ = [
    "ProtocolAgent",
]
