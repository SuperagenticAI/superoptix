"""MCP (Model Context Protocol) support for SuperOptiX.

This module provides MCP client and session implementations for protocol-first agents.
"""

from superoptix.protocols.mcp.client import MCPClient, RealMCPClient
from superoptix.protocols.mcp.session import MockMCPSession, BackgroundMCPServer

__all__ = [
    "MCPClient",
    "RealMCPClient",
    "MockMCPSession",
    "BackgroundMCPServer",
]
