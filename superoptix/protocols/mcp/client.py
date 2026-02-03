"""MCP Client implementation for SuperOptiX.

This module provides Model Context Protocol (MCP) client for protocol-first agents.
Implements both mock and real MCP clients:
- MCPClient: Mock MCP for testing and demonstration
- RealMCPClient: Real MCP with background server management

Vendored from Agenspy project and adapted for SuperOptiX architecture.
"""

import logging
from typing import Any, Dict, List

import dspy

from superoptix.protocols.base import BaseProtocol, ProtocolType

logger = logging.getLogger(__name__)


class MCPClient(BaseProtocol):
    """Model Context Protocol client implementation.

    Implements MCP protocol for automatic tool discovery and execution.
    Currently uses mock MCP session for demonstration without requiring
    actual MCP server infrastructure.

    The MCP protocol enables:
    - Automatic tool discovery from protocol servers
    - Context sharing between agents and tools
    - Session management for stateful interactions
    - Native protocol-level optimization

    This is a core component of SuperOptiX's protocol-first approach,
    which differentiates it from pure DSPy implementations.

    Attributes:
        server_url: MCP server URL
        timeout: Connection timeout in seconds
        session: MCP session instance
        available_tools: Dictionary of discovered tools

    Example:
        ```python
        from superoptix.protocols.mcp.client import MCPClient

        # Create and connect client
        client = MCPClient(server_url="mcp://localhost:8080/math")

        if client.connect():
            # Discover tools automatically
            caps = client.get_capabilities()
            print(f"Tools: {caps['tools']}")

            # Execute tool via protocol
            result = client._handle_request(
                context_request="Calculate 5 * 10",
                tool_name="calculator",
                tool_args={"expression": "5 * 10"}
            )
            print(f"Result: {result.tool_result}")
        ```
    """

    def __init__(self, server_url: str, timeout: int = 30, **kwargs):
        """Initialize MCP client.

        Args:
            server_url: MCP server URL (e.g., "mcp://localhost:8080/math")
            timeout: Connection timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseProtocol
        """
        protocol_config = {
            "type": ProtocolType.MCP,
            "server_url": server_url,
            "timeout": timeout,
        }
        super().__init__(protocol_config, **kwargs)
        self.server_url = server_url
        self.timeout = timeout
        self.session = None
        self.available_tools = {}

    def connect(self) -> bool:
        """Establish MCP connection.

        Creates mock MCP session and discovers available tools.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MCP server: {self.server_url}")

            # For now, using mock session
            # Future: Add RealMCPClient for production use
            from superoptix.protocols.mcp.session import MockMCPSession

            self.session = MockMCPSession(self.server_url)
            self._discover_tools()
            self._connected = True

            logger.info(
                f"MCP Connected! Available tools: {list(self.available_tools.keys())}"
            )
            return True

        except Exception as e:
            logger.error(f"MCP connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Close MCP connection.

        Closes the session and cleans up resources.
        """
        if self.session:
            self.session.close()
            self._connected = False
            logger.info("Disconnected from MCP server")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP server capabilities.

        Returns:
            Dictionary containing:
            - protocol: Protocol type ("mcp")
            - version: MCP protocol version
            - tools: List of available tool names
            - context_sharing: Whether context sharing is supported
            - session_management: Whether sessions are supported
            - server_url: MCP server URL
        """
        self._capabilities = {
            "protocol": "mcp",
            "version": "1.0",
            "tools": list(self.available_tools.keys()),
            "context_sharing": True,
            "session_management": True,
            "server_url": self.server_url,
        }
        return self._capabilities

    def discover_peers(self) -> List[str]:
        """Discover available MCP servers.

        In production, this would discover MCP servers on network.
        Currently returns configured server URL.

        Returns:
            List of MCP server URLs
        """
        return [self.server_url]

    def _discover_tools(self):
        """Discover available MCP tools.

        Queries the MCP server for available tools and caches them.
        """
        if self.session:
            self.available_tools = self.session.list_tools()
            logger.debug(f"Discovered {len(self.available_tools)} MCP tools")

    def _handle_request(self, **kwargs) -> dspy.Prediction:
        """Handle MCP-specific requests.

        Processes context requests and tool execution via MCP protocol.

        Args:
            context_request: Optional context request string
            tool_name: Optional tool name to execute
            tool_args: Optional tool arguments dictionary

        Returns:
            dspy.Prediction containing:
            - context_data: Context retrieved from MCP server
            - tool_result: Tool execution result (if tool was called)
            - capabilities: Server capabilities
            - protocol_info: Protocol status information
        """
        context_request = kwargs.get("context_request", "")
        tool_name = kwargs.get("tool_name", "")
        tool_args = kwargs.get("tool_args", {})

        logger.debug(f"MCP Request - Context: {context_request[:50]}...")

        # Get context from MCP server
        context_data = self._get_context(context_request)

        # Execute tool if specified
        tool_result = ""
        if tool_name and tool_name in self.available_tools:
            logger.debug(f"Executing MCP tool: {tool_name}")
            tool_result = self._execute_tool(tool_name, tool_args)

        return dspy.Prediction(
            context_data=context_data,
            tool_result=tool_result,
            capabilities=self.get_capabilities(),
            protocol_info=f"MCP session active with {len(self.available_tools)} tools",
        )

    def _get_context(self, request: str) -> str:
        """Get context from MCP server.

        Args:
            request: Context request string

        Returns:
            Context data string from MCP server
        """
        if self.session:
            return self.session.get_context(request)
        return ""

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute MCP tool.

        Args:
            tool_name: Name of tool to execute
            args: Tool arguments dictionary

        Returns:
            Tool execution result string
        """
        if self.session and tool_name in self.available_tools:
            return self.session.execute_tool(tool_name, args)
        return ""


# RealMCPClient addition to client.py
# Append this to the end of client.py


class RealMCPClient(BaseProtocol):
    """Real MCP Client with background server management.

    This client starts and manages actual MCP servers as background processes.
    Use this for production scenarios with real MCP servers like:
    - @modelcontextprotocol/server-github
    - @modelcontextprotocol/server-filesystem
    - Custom MCP servers

    Attributes:
            server_command: Command to start MCP server
            mcp_server: BackgroundMCPServer instance
            available_tools: Dictionary of discovered tools

    Example:
            ```python
            from superoptix.protocols.mcp.client import RealMCPClient

            # GitHub MCP server
            client = RealMCPClient(
                    server_command=["npx", "-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_TOKEN": "your_token"}
            )

            if client.connect():
                    caps = client.get_capabilities()
                    print(f"Tools: {caps['tools']}")

            client.disconnect()
            ```
    """

    def __init__(self, server_command: List[str], env: dict = None, **kwargs):
        """Initialize real MCP client.

        Args:
                server_command: Command to start MCP server (e.g., ["npx", "mcp-server"])
                env: Environment variables for server process
                **kwargs: Additional arguments passed to BaseProtocol
        """
        protocol_config = {
            "type": ProtocolType.MCP,
            "server_command": server_command,
            "real_server": True,
        }
        super().__init__(protocol_config, **kwargs)
        self.server_command = server_command
        self.env = env or {}
        self.mcp_server = None
        self.available_tools = {}
        logger.debug(f"Initialized RealMCPClient with command: {server_command}")

    def connect(self) -> bool:
        """Establish real MCP connection with background server.

        Returns:
                True if connection successful, False otherwise
        """
        try:
            logger.info(f"Starting real MCP server: {' '.join(self.server_command)}")

            from superoptix.protocols.mcp.session import BackgroundMCPServer

            self.mcp_server = BackgroundMCPServer(self.server_command)

            if not self.mcp_server.start_server():
                logger.error("Failed to start MCP server")
                return False

            if not self.mcp_server.connect_client():
                logger.error("Failed to connect to MCP server")
                self.mcp_server.stop_server()
                return False

            self.available_tools = self.mcp_server.tools
            self._connected = True

            logger.info(
                f"Real MCP Connected! Available tools: {list(self.available_tools.keys())}"
            )
            return True

        except Exception as e:
            logger.error(f"Real MCP connection failed: {e}")
            if self.mcp_server:
                self.mcp_server.stop_server()
            return False

    def disconnect(self) -> None:
        """Close MCP connection and stop background server."""
        if self.mcp_server:
            self.mcp_server.stop_server()
            self._connected = False
            logger.info("Disconnected from real MCP server")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get real MCP server capabilities."""
        self._capabilities = {
            "protocol": "real_mcp",
            "version": "1.0",
            "tools": list(self.available_tools.keys()),
            "context_sharing": True,
            "session_management": True,
            "background_server": True,
            "server_command": self.server_command,
        }
        return self._capabilities

    def discover_peers(self) -> List[str]:
        """Discover available MCP servers."""
        return ["background_server"]

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute tool via real MCP server."""
        if not self.mcp_server:
            return "Error: No active MCP server"

        if tool_name not in self.available_tools:
            return f"Error: Tool {tool_name} not available"

        logger.debug(f"Executing real MCP tool: {tool_name}")
        return self.mcp_server.execute_tool(tool_name, args)

    def get_context(self, request: str) -> str:
        """Get context from real MCP server."""
        if not self.mcp_server:
            return "Error: No active MCP server"

        return self.mcp_server.get_context(request)
