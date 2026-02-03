"""MCP (Model Context Protocol) Client for SuperOptiX.

Provides integration with MCP servers for tool calling and filesystem access.
Users can configure their own trusted MCP servers.
"""

import warnings
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

warnings.filterwarnings("ignore")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    description: str = ""
    enabled: bool = True


class MCPClient:
    """MCP client for SuperOptiX conversational CLI.

    Supports:
    - Filesystem access via @modelcontextprotocol/server-filesystem
    - User-defined trusted MCP servers
    - Tool calling through MCP protocol
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize MCP client.

        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = config_path or Path.home() / ".superoptix_mcp_config.json"
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.available = MCP_AVAILABLE
        self._load_config()

    def _load_config(self):
        """Load MCP server configurations."""
        # Default filesystem server
        self.servers["filesystem"] = MCPServerConfig(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", str(Path.cwd())],
            description="MCP filesystem server for local file access",
            enabled=False,  # Disabled by default, user can enable
        )

        # Load user-defined servers from config
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config_data = json.load(f)

                for server_name, server_config in config_data.get(
                    "servers", {}
                ).items():
                    self.servers[server_name] = MCPServerConfig(
                        name=server_name,
                        command=server_config["command"],
                        args=server_config.get("args", []),
                        env=server_config.get("env"),
                        description=server_config.get("description", ""),
                        enabled=server_config.get("enabled", True),
                    )
            except Exception as e:
                pass  # Silently ignore config load errors

    def save_config(self):
        """Save MCP server configurations."""
        config_data = {"servers": {}}

        for name, server in self.servers.items():
            if name != "filesystem":  # Don't save default filesystem server
                config_data["servers"][name] = {
                    "command": server.command,
                    "args": server.args,
                    "env": server.env,
                    "description": server.description,
                    "enabled": server.enabled,
                }

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            pass  # Silently ignore save errors

    def add_server(
        self,
        name: str,
        command: str,
        args: List[str],
        description: str = "",
        env: Optional[Dict] = None,
    ):
        """Add a new MCP server configuration.

        Args:
            name: Server identifier
            command: Command to run server
            args: Command arguments
            description: Server description
            env: Environment variables
        """
        self.servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args,
            env=env,
            description=description,
            enabled=True,
        )
        self.save_config()

    def list_servers(self) -> List[MCPServerConfig]:
        """List all configured MCP servers."""
        return list(self.servers.values())

    def enable_server(self, name: str):
        """Enable an MCP server."""
        if name in self.servers:
            self.servers[name].enabled = True
            self.save_config()

    def disable_server(self, name: str):
        """Disable an MCP server."""
        if name in self.servers:
            self.servers[name].enabled = False
            self.save_config()

    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server.

        Args:
            server_name: Name of server to connect to

        Returns:
            True if connection successful
        """
        if not self.available:
            return False

        if server_name not in self.servers:
            return False

        server = self.servers[server_name]
        if not server.enabled:
            return False

        try:
            server_params = StdioServerParameters(
                command=server.command, args=server.args, env=server.env
            )

            # Connect asynchronously
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()

            self.sessions[server_name] = session
            return True

        except Exception as e:
            return False

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[Any]:
        """Call a tool on an MCP server.

        Args:
            server_name: Server to call tool on
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool result or None
        """
        if server_name not in self.sessions:
            # Try to connect
            if not await self.connect_server(server_name):
                return None

        session = self.sessions[server_name]

        try:
            result = await session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            return None

    async def list_tools(self, server_name: str) -> List[Dict]:
        """List available tools on a server.

        Args:
            server_name: Server to query

        Returns:
            List of tool descriptions
        """
        if server_name not in self.sessions:
            if not await self.connect_server(server_name):
                return []

        session = self.sessions[server_name]

        try:
            tools = await session.list_tools()
            return tools
        except Exception as e:
            return []

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for server_name, session in self.sessions.items():
            try:
                await session.__aexit__(None, None, None)
            except:
                pass

        self.sessions.clear()

    # Synchronous wrappers for CLI use
    def connect_server_sync(self, server_name: str) -> bool:
        """Synchronous wrapper for connect_server."""
        return asyncio.run(self.connect_server(server_name))

    def call_tool_sync(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[Any]:
        """Synchronous wrapper for call_tool."""
        return asyncio.run(self.call_tool(server_name, tool_name, arguments))

    def list_tools_sync(self, server_name: str) -> List[Dict]:
        """Synchronous wrapper for list_tools."""
        return asyncio.run(self.list_tools(server_name))

    def read_file(
        self, file_path: str, server_name: str = "filesystem"
    ) -> Optional[str]:
        """Read a file via MCP filesystem server.

        Args:
            file_path: Path to file
            server_name: MCP server to use (default: filesystem)

        Returns:
            File content or None
        """
        if not self.available:
            # Fallback to direct file reading
            try:
                return Path(file_path).read_text()
            except:
                return None

        result = self.call_tool_sync(server_name, "read_file", {"path": file_path})

        return result.content if result else None

    def list_directory(
        self, dir_path: str, server_name: str = "filesystem"
    ) -> Optional[List]:
        """List directory contents via MCP.

        Args:
            dir_path: Path to directory
            server_name: MCP server to use

        Returns:
            Directory listing or None
        """
        result = self.call_tool_sync(server_name, "list_directory", {"path": dir_path})

        return result.content if result else None


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
