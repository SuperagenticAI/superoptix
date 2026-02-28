"""Phase 2 CLI tests for MCP/ACP helpers."""
from pathlib import Path

from superoptix.cli.commands.acp_client import ACPClient
from superoptix.cli.commands.mcp_client import MCPClient


def test_mcp_client_server_config_roundtrip(tmp_path):
    """MCP client should persist and reload custom server configuration."""
    config_path = tmp_path / "mcp_config.json"
    client = MCPClient(config_path=config_path)
    client.add_server(
        name="demo",
        command="npx",
        args=["-y", "server-demo"],
        description="demo server",
    )

    reloaded = MCPClient(config_path=config_path)
    servers = {s.name: s for s in reloaded.list_servers()}
    assert "demo" in servers
    assert servers["demo"].command == "npx"
    assert servers["demo"].args == ["-y", "server-demo"]


def test_mcp_client_disable_sets_state(tmp_path):
    """Disabling a server should persist enabled=False."""
    config_path = tmp_path / "mcp_config.json"
    client = MCPClient(config_path=config_path)
    client.add_server("demo", "npx", ["-y", "server-demo"])
    client.disable_server("demo")

    reloaded = MCPClient(config_path=config_path)
    servers = {s.name: s for s in reloaded.list_servers()}
    assert "demo" in servers
    assert servers["demo"].enabled is False


def test_acp_client_disconnected_send_prompt(tmp_path):
    """ACP send_prompt should return a stable error when disconnected."""
    client = ACPClient(project_root=Path(tmp_path))
    result = client.send_prompt("hello")
    assert result["ok"] is False
    assert "not connected" in result["error"].lower()
