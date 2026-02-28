from io import StringIO

from rich.console import Console

from superoptix.cli.commands.slash_commands import SlashCommandHandler
from superoptix.cli.connection_state import ConnectionStateStore


def _make_handler(config: dict) -> SlashCommandHandler:
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=120)
    return SlashCommandHandler(console=console, config=config, chat_agent=None)


def test_slash_connect_commands_registered():
    handler = _make_handler(config={})
    assert "/connect" in handler.commands
    assert "/c" in handler.commands


def test_slash_connect_no_args_does_not_crash():
    handler = _make_handler(config={})
    handler.cmd_connect()


def test_slash_connect_byok_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    handler = _make_handler(config={})
    handler.cmd_connect("byok", "openai/gpt-4o")

    store = ConnectionStateStore()
    profile = store.profile(store.load())
    assert profile["active_connection"]["type"] == "byok"
    assert profile["byok"]["provider"] == "openai"
    assert profile["byok"]["model"] == "gpt-4o"


def test_slash_connect_local_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    handler = _make_handler(config={})
    handler.cmd_connect("local", "ollama/llama3.2:3b")

    store = ConnectionStateStore()
    profile = store.profile(store.load())
    assert profile["active_connection"]["type"] == "local"
    assert profile["local"]["provider"] == "ollama"
    assert profile["local"]["model"] == "llama3.2:3b"
