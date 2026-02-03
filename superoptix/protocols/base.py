"""Base protocol interface for SuperOptiX.

This module provides the foundation for protocol-first agent development in SuperOptiX.
Vendored from Agenspy project and adapted for SuperOptiX architecture.

Protocol-first agents use communication protocols (like MCP) as first-class primitives,
enabling automatic tool discovery, session management, and protocol-level optimization.
"""

from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, List

import dspy


class ProtocolType(Enum):
    """Supported protocol types in SuperOptiX.

    Attributes:
        MCP: Model Context Protocol - for tool and context sharing
        AGENT2AGENT: Direct agent-to-agent communication (future)
        CUSTOM: User-defined custom protocols
    """

    MCP = "mcp"
    AGENT2AGENT = "agent2agent"
    CUSTOM = "custom"


class BaseProtocol(dspy.Module):
    """Base class for all agent communication protocols.

    This class provides a standardized interface for integrating various
    agent communication protocols with DSPy's module system, enabling
    protocol-first agent development.

    The protocol-first approach treats protocols as primitives rather than
    tools, enabling:
    - Automatic tool discovery from protocol servers
    - Native session and context management
    - Protocol-level optimization and reasoning
    - Seamless multi-protocol agent composition

    Attributes:
        protocol_config: Configuration dictionary for the protocol
        protocol_type: Type of protocol (MCP, Agent2Agent, Custom)
        connection_manager: Optional connection manager instance
        _connected: Connection status flag
        _capabilities: Protocol capabilities dictionary

    Example:
        ```python
        from superoptix.protocols.mcp.client import MCPClient

        # Create MCP client
        client = MCPClient(server_url="mcp://localhost:8080/math")

        # Connect and discover tools
        if client.connect():
            capabilities = client.get_capabilities()
            print(f"Available tools: {capabilities['tools']}")
        ```
    """

    def __init__(self, protocol_config: Dict[str, Any], **kwargs):
        """Initialize protocol with configuration.

        Args:
            protocol_config: Protocol configuration dictionary
                Must contain 'type' key with ProtocolType value
            **kwargs: Additional arguments passed to dspy.Module
        """
        super().__init__(**kwargs)
        self.protocol_config = protocol_config
        self.protocol_type = protocol_config.get("type", ProtocolType.CUSTOM)
        self.connection_manager = None
        self._connected = False
        self._capabilities = {}

    @abstractmethod
    def connect(self) -> bool:
        """Establish protocol connection.

        Implementations should:
        1. Establish connection to protocol server/endpoint
        2. Perform handshake and authentication
        3. Discover available capabilities (tools, resources, etc.)
        4. Set self._connected = True on success

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close protocol connection.

        Implementations should:
        1. Clean up any active sessions
        2. Close network connections
        3. Release resources
        4. Set self._connected = False
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get protocol capabilities and available tools.

        Returns:
            Dictionary containing:
            - protocol: Protocol name/type
            - version: Protocol version
            - tools: List of available tool names
            - Additional protocol-specific capabilities
        """
        pass

    @abstractmethod
    def discover_peers(self) -> List[str]:
        """Discover available peers/servers for this protocol.

        Returns:
            List of peer identifiers (URLs, addresses, etc.)
        """
        pass

    def forward(self, **kwargs):
        """DSPy module forward method.

        Automatically connects if not already connected,
        then delegates to protocol-specific handler.

        Args:
            **kwargs: Protocol-specific request parameters

        Returns:
            dspy.Prediction with protocol response
        """
        if not self._connected:
            self.connect()
        return self._handle_request(**kwargs)

    @abstractmethod
    def _handle_request(self, **kwargs) -> dspy.Prediction:
        """Handle protocol-specific requests.

        Implementations should:
        1. Parse request parameters
        2. Execute protocol operations (tool calls, context requests, etc.)
        3. Return results as dspy.Prediction

        Args:
            **kwargs: Protocol-specific request parameters

        Returns:
            dspy.Prediction containing response data
        """
        pass

    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol metadata and status.

        Returns:
            Dictionary containing:
            - type: Protocol type string
            - connected: Connection status
            - capabilities: Protocol capabilities
            - config: Protocol configuration
        """
        return {
            "type": self.protocol_type.value,
            "connected": self._connected,
            "capabilities": self._capabilities,
            "config": self.protocol_config,
        }
