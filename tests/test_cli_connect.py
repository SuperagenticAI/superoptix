"""Tests for Super CLI connection commands/state."""

from argparse import Namespace

from superoptix.cli.commands.connect import (
    connect_acp,
    connect_byok,
    connect_local,
    connect_mcp,
)
from superoptix.cli.connection_state import ConnectionStateStore


def test_connection_store_defaults(tmp_path):
    """Store should create sane defaults when file does not exist."""
    store = ConnectionStateStore(state_path=tmp_path / "super_cli.yaml")
    data = store.load()
    assert data["version"] == 1
    assert data["active_profile"] == "default"
    assert "default" in data["profiles"]


def test_connect_byok_persists(tmp_path, monkeypatch):
    """BYOK command should persist provider/model and active connection."""
    monkeypatch.setenv("HOME", str(tmp_path))
    args = Namespace(
        provider="openai",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        activate=True,
    )
    connect_byok(args)

    store = ConnectionStateStore()
    data = store.load()
    profile = store.profile(data)
    assert profile["byok"]["provider"] == "openai"
    assert profile["byok"]["model"] == "gpt-4o"
    assert profile["active_connection"]["type"] == "byok"
    assert profile["connection_history"][0]["type"] == "byok"


def test_connect_local_persists(tmp_path, monkeypatch):
    """LOCAL command should persist local provider/model config."""
    monkeypatch.setenv("HOME", str(tmp_path))
    args = Namespace(
        provider="ollama",
        model="llama3.2:3b",
        endpoint="http://localhost:11434/api/tags",
        test=False,
        activate=True,
    )
    connect_local(args)

    store = ConnectionStateStore()
    profile = store.profile(store.load())
    assert profile["local"]["provider"] == "ollama"
    assert profile["local"]["model"] == "llama3.2:3b"
    assert profile["active_connection"]["type"] == "local"


def test_connect_acp_persists(tmp_path, monkeypatch):
    """ACP command should persist agent/model/command config."""
    monkeypatch.setenv("HOME", str(tmp_path))
    args = Namespace(
        agent="opencode",
        model="gpt-4o-mini",
        command="opencode acp",
        test=False,
        activate=True,
    )
    connect_acp(args)

    store = ConnectionStateStore()
    profile = store.profile(store.load())
    assert profile["acp"]["agent"] == "opencode"
    assert profile["acp"]["command"] == "opencode acp"
    assert profile["active_connection"]["type"] == "acp"


def test_connect_mcp_stdio_persists(tmp_path, monkeypatch):
    """MCP command should save stdio server config with parsed args."""
    monkeypatch.setenv("HOME", str(tmp_path))
    args = Namespace(
        name="filesystem",
        transport="stdio",
        command="npx",
        args="-y @modelcontextprotocol/server-filesystem .",
        url=None,
        disable=False,
        test=False,
        activate=True,
    )
    connect_mcp(args)

    store = ConnectionStateStore()
    profile = store.profile(store.load())
    servers = profile["mcp"]["servers"]
    assert "filesystem" in servers
    assert servers["filesystem"]["command"] == "npx"
    assert servers["filesystem"]["args"] == [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        ".",
    ]
    assert profile["active_connection"]["type"] == "mcp"
    assert profile["active_connection"]["name"] == "filesystem"


def test_connection_history_tracks_recent_unique(tmp_path):
    """set_active should maintain a recent unique history list."""
    store = ConnectionStateStore(state_path=tmp_path / "super_cli.yaml")
    store.set_active("byok", "openai")
    store.set_active("local", "ollama")
    store.set_active("byok", "openai")

    history = store.connection_history(limit=5)
    assert len(history) == 2
    assert history[0]["type"] == "byok"
    assert history[1]["type"] == "local"
