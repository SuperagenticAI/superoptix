"""MCP client manager for SuperOptiX conversational CLI."""

from __future__ import annotations

import asyncio
import json
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

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


class MCPConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    description: str = ""
    enabled: bool = True
    transport: str = "stdio"
    url: Optional[str] = None


@dataclass
class MCPServerStatus:
    """Runtime status of an MCP server connection."""

    name: str
    state: MCPConnectionState = MCPConnectionState.DISCONNECTED
    error: Optional[str] = None


class MCPClient:
    """MCP manager with multi-server lifecycle support."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".superoptix_mcp_config.json"
        self.servers: Dict[str, MCPServerConfig] = {}
        self.server_status: Dict[str, MCPServerStatus] = {}
        self.sessions: Dict[str, Any] = {}
        self.available = MCP_AVAILABLE

        self._stdio_contexts: Dict[str, Any] = {}
        self._session_contexts: Dict[str, Any] = {}

        self._load_config()

    def _load_config(self):
        """Load MCP server configurations."""
        self.servers = {
            "filesystem": MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", str(Path.cwd())],
                description="MCP filesystem server for local file access",
                enabled=False,
                transport="stdio",
            )
        }
        self.server_status = {
            name: MCPServerStatus(name=name) for name in self.servers.keys()
        }

        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            return

        for server_name, server_config in config_data.get("servers", {}).items():
            cfg = MCPServerConfig(
                name=server_name,
                command=server_config.get("command", ""),
                args=server_config.get("args", []),
                env=server_config.get("env"),
                description=server_config.get("description", ""),
                enabled=server_config.get("enabled", True),
                transport=server_config.get("transport", "stdio"),
                url=server_config.get("url"),
            )
            self.servers[server_name] = cfg
            self.server_status[server_name] = MCPServerStatus(name=server_name)

    def reload_config(self) -> None:
        self._load_config()

    def save_config(self):
        """Save MCP server configurations."""
        config_data = {"servers": {}}
        for name, server in self.servers.items():
            if name == "filesystem":
                continue
            config_data["servers"][name] = {
                "command": server.command,
                "args": server.args,
                "env": server.env,
                "description": server.description,
                "enabled": server.enabled,
                "transport": server.transport,
                "url": server.url,
            }

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
        except Exception:
            pass

    def add_server(
        self,
        name: str,
        command: str,
        args: List[str],
        description: str = "",
        env: Optional[Dict] = None,
    ):
        """Add or update stdio server config."""
        self.servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args,
            env=env,
            description=description,
            enabled=True,
            transport="stdio",
        )
        self.server_status[name] = MCPServerStatus(name=name)
        self.save_config()

    def add_url_server(
        self,
        name: str,
        url: str,
        transport: str = "http",
        description: str = "",
        enabled: bool = True,
    ):
        """Add or update URL-based server config (future transport support)."""
        self.servers[name] = MCPServerConfig(
            name=name,
            command="",
            args=[],
            description=description,
            enabled=enabled,
            transport=transport,
            url=url,
        )
        self.server_status[name] = MCPServerStatus(name=name)
        self.save_config()

    def list_servers(self) -> List[MCPServerConfig]:
        return list(self.servers.values())

    def list_server_status(self) -> List[MCPServerStatus]:
        return [self.server_status.get(name, MCPServerStatus(name=name)) for name in self.servers.keys()]

    def enable_server(self, name: str):
        if name in self.servers:
            self.servers[name].enabled = True
            self.save_config()

    def disable_server(self, name: str):
        if name in self.servers:
            self.servers[name].enabled = False
            self.save_config()
            self.disconnect_server_sync(name)

    async def connect_server(self, server_name: str) -> bool:
        if not self.available:
            return False
        if server_name not in self.servers:
            return False
        if server_name in self.sessions:
            return True

        server = self.servers[server_name]
        status = self.server_status.setdefault(server_name, MCPServerStatus(name=server_name))
        status.state = MCPConnectionState.CONNECTING
        status.error = None

        if not server.enabled:
            status.state = MCPConnectionState.DISCONNECTED
            return False

        if server.transport != "stdio":
            status.state = MCPConnectionState.ERROR
            status.error = f"Transport '{server.transport}' not implemented yet (stdio only)"
            return False

        try:
            server_params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=server.env,
            )
            stdio_cm = stdio_client(server_params)
            read, write = await stdio_cm.__aenter__()

            session_cm = ClientSession(read, write)
            session = await session_cm.__aenter__()
            await session.initialize()

            self._stdio_contexts[server_name] = stdio_cm
            self._session_contexts[server_name] = session_cm
            self.sessions[server_name] = session

            status.state = MCPConnectionState.CONNECTED
            return True
        except Exception as e:
            status.state = MCPConnectionState.ERROR
            status.error = str(e)
            return False

    async def connect_all(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for name, cfg in self.servers.items():
            if not cfg.enabled:
                continue
            results[name] = await self.connect_server(name)
        return results

    async def disconnect_server(self, server_name: str) -> bool:
        if server_name not in self.sessions:
            status = self.server_status.get(server_name)
            if status:
                status.state = MCPConnectionState.DISCONNECTED
                status.error = None
            return True

        ok = True
        session_cm = self._session_contexts.pop(server_name, None)
        stdio_cm = self._stdio_contexts.pop(server_name, None)

        try:
            if session_cm:
                await session_cm.__aexit__(None, None, None)
        except Exception:
            ok = False
        try:
            if stdio_cm:
                await stdio_cm.__aexit__(None, None, None)
        except Exception:
            ok = False

        self.sessions.pop(server_name, None)
        status = self.server_status.setdefault(server_name, MCPServerStatus(name=server_name))
        status.state = MCPConnectionState.DISCONNECTED if ok else MCPConnectionState.ERROR
        if ok:
            status.error = None
        return ok

    async def disconnect_all(self):
        for server_name in list(self.sessions.keys()):
            await self.disconnect_server(server_name)

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[Any]:
        if server_name not in self.sessions:
            if not await self.connect_server(server_name):
                return None
        session = self.sessions[server_name]
        try:
            return await session.call_tool(tool_name, arguments=arguments)
        except Exception as e:
            status = self.server_status.setdefault(server_name, MCPServerStatus(name=server_name))
            status.state = MCPConnectionState.ERROR
            status.error = str(e)
            return None

    async def list_tools(self, server_name: str) -> List[Dict]:
        if server_name not in self.sessions:
            if not await self.connect_server(server_name):
                return []
        session = self.sessions[server_name]
        try:
            raw = await session.list_tools()
            if isinstance(raw, dict):
                return raw.get("tools", [])
            if hasattr(raw, "tools"):
                tools = getattr(raw, "tools")
                normalized = []
                for t in tools:
                    name = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
                    description = getattr(t, "description", None) or (t.get("description") if isinstance(t, dict) else "")
                    normalized.append({"name": name or "unknown", "description": description or ""})
                return normalized
            if isinstance(raw, list):
                return raw
            return []
        except Exception as e:
            status = self.server_status.setdefault(server_name, MCPServerStatus(name=server_name))
            status.state = MCPConnectionState.ERROR
            status.error = str(e)
            return []

    def connect_server_sync(self, server_name: str) -> bool:
        return asyncio.run(self.connect_server(server_name))

    def connect_all_sync(self) -> Dict[str, bool]:
        return asyncio.run(self.connect_all())

    def disconnect_server_sync(self, server_name: str) -> bool:
        return asyncio.run(self.disconnect_server(server_name))

    def disconnect_all_sync(self) -> None:
        asyncio.run(self.disconnect_all())

    def call_tool_sync(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[Any]:
        return asyncio.run(self.call_tool(server_name, tool_name, arguments))

    def list_tools_sync(self, server_name: str) -> List[Dict]:
        return asyncio.run(self.list_tools(server_name))

    def read_file(
        self, file_path: str, server_name: str = "filesystem"
    ) -> Optional[str]:
        if not self.available:
            try:
                return Path(file_path).read_text()
            except Exception:
                return None
        result = self.call_tool_sync(server_name, "read_file", {"path": file_path})
        if not result:
            return None
        content = getattr(result, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            try:
                return "\n".join(str(x) for x in content)
            except Exception:
                return str(content)
        return str(content) if content is not None else None

    def list_directory(
        self, dir_path: str, server_name: str = "filesystem"
    ) -> Optional[List]:
        result = self.call_tool_sync(server_name, "list_directory", {"path": dir_path})
        if not result:
            return None
        return getattr(result, "content", None)


_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
