"""Base agent classes for SuperOptiX.

This module provides base agent implementations for different paradigms:
- Protocol-first agents (using native protocol runtime)
- Tool-first agents (using DSPy approach)
"""

from superoptix.agent_bases.protocol_agent import ProtocolAgent

__all__ = [
    "ProtocolAgent",
]
