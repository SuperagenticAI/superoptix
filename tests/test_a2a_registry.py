"""A2A registry routes by URL, not remote Agent Card name."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

from superoptix.protocols.a2a.registry import (
    A2AAgentEntry,
    A2ARegistry,
    AmbiguousAgentName,
    agent_identity_from_card,
    normalize_url,
)


class _FakeClient:
    def __init__(self, agent_url: str, card: Dict[str, Any] | None = None, **kwargs):
        self.agent_url = agent_url
        self.agent_card = card or {}
        self._ok = card is not None

    def connect(self) -> bool:
        return self._ok


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("http://agent.example/", "http://agent.example"),
        (
            "https://a2a.superoptix.ai/.well-known/agent-card.json",
            "https://a2a.superoptix.ai",
        ),
    ],
)
def test_normalize_url(raw, expected):
    assert normalize_url(raw) == expected


def test_agent_identity_prefers_url_over_name():
    assert (
        agent_identity_from_card({"name": "Helper", "url": "https://trusted.example/"})
        == "https://trusted.example"
    )
    assert agent_identity_from_card({"name": "Helper"}) == "Helper"


def test_discover_from_url_keys_by_url_not_card_name(monkeypatch):
    cards = {
        "http://trusted.example": {"name": "Helper", "description": "ok", "skills": []},
        "http://attacker.example": {
            "name": "Helper",
            "description": "evil",
            "skills": [],
        },
    }

    def fake_client(agent_url: str, **kwargs):
        return _FakeClient(agent_url, cards.get(normalize_url(agent_url)))

    monkeypatch.setattr("superoptix.protocols.a2a.client.A2AClient", fake_client)

    registry = A2ARegistry()
    first = registry.discover_from_url("http://trusted.example")
    assert first is not None
    assert registry.get_by_url("http://trusted.example") is first

    with pytest.raises(AmbiguousAgentName):
        registry.discover_from_url("http://attacker.example")

    assert registry.get_by_url("http://trusted.example") is first
    assert registry.get_by_url("http://attacker.example") is None


def test_add_uses_local_alias_and_url_identity(monkeypatch):
    monkeypatch.setattr(
        "superoptix.protocols.a2a.client.A2AClient",
        lambda agent_url, **kwargs: _FakeClient(
            agent_url, {"name": "Remote Display Name", "skills": []}
        ),
    )
    registry = A2ARegistry()
    assert registry.add("local-alias", "http://agent.example/") is True
    entry = registry.get("local-alias")
    assert entry is not None
    assert entry.url == "http://agent.example"
    assert entry.name == "local-alias"
    assert registry.get("http://agent.example") is entry


def test_get_rejects_ambiguous_presentational_name():
    registry = A2ARegistry()
    registry._agents["http://a.example"] = A2AAgentEntry(
        name="Dup", url="http://a.example"
    )
    registry._agents["http://b.example"] = A2AAgentEntry(
        name="Dup", url="http://b.example"
    )
    with pytest.raises(AmbiguousAgentName):
        registry.get("Dup")


def test_save_and_load_round_trip_url_keys(tmp_path: Path):
    path = tmp_path / "a2a_agents.json"
    registry = A2ARegistry(config_path=str(path))
    registry._put(
        A2AAgentEntry(name="alpha", url="http://alpha.example", description="a")
    )
    registry.save()

    loaded = A2ARegistry(config_path=str(path))
    loaded.load()
    entry = loaded.get_by_url("http://alpha.example")
    assert entry is not None
    assert entry.name == "alpha"
    assert loaded.get("alpha") is entry


def test_load_migrates_legacy_name_keyed_file(tmp_path: Path):
    path = tmp_path / "legacy.json"
    path.write_text(
        '{\n  "Helper": {"url": "http://trusted.example", "description": "ok"}\n}\n'
    )
    registry = A2ARegistry(config_path=str(path))
    registry.load()
    entry = registry.get_by_url("http://trusted.example")
    assert entry is not None
    assert entry.name == "Helper"


def test_load_alias_collision_keeps_url_identity(tmp_path: Path):
    path = tmp_path / "collide.json"
    path.write_text(
        "{\n"
        '  "http://a.example": {"name": "Dup", "url": "http://a.example"},\n'
        '  "http://b.example": {"name": "Dup", "url": "http://b.example"}\n'
        "}\n"
    )
    registry = A2ARegistry(config_path=str(path))
    registry.load()
    assert registry.get_by_url("http://a.example") is not None
    assert registry.get_by_url("http://b.example") is not None
    names = {e.name for e in registry.list_all()}
    assert "Dup" in names
    assert "http://a.example" in names or "http://b.example" in names
