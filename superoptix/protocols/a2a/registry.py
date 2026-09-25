"""A2A peer registry — discover and manage A2A agents.

Routing identity is the normalized agent URL (origin-bound). The Agent Card
``name`` field is presentational metadata, not a stable routing key. Storing
or looking up peers by remote card name alone enables name-collision
wrong-peer dispatch (see arXiv:2609.27624).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

_CARD_SUFFIXES = (
    "/.well-known/agent-card.json",
    "/.well-known/agent.json",
)


def normalize_url(url: str) -> str:
    """Normalize an agent URL for use as a stable registry key.

    Strips trailing slashes and well-known card path suffixes so the same
    origin always maps to one key.
    """
    trimmed = (url or "").strip().rstrip("/")
    for suffix in _CARD_SUFFIXES:
        if trimmed.endswith(suffix):
            return trimmed[: -len(suffix)].rstrip("/") or trimmed
    return trimmed


@dataclass
class A2AAgentEntry:
    """One registered A2A peer."""

    name: str
    url: str
    description: str = ""
    version: str = "1.0"
    skills: List[Dict[str, Any]] = field(default_factory=list)
    verified: bool = False


class AmbiguousAgentName(ValueError):
    """More than one registered URL shares the same presentational name."""


class A2ARegistry:
    """Registry for managing A2A agent connections.

    Entries are keyed by normalized URL. ``name`` is a local presentational
    alias (user-chosen on :meth:`add`, or the card name on discover). Looking
    up by alias rejects collisions instead of silently picking one peer.
    """

    def __init__(self, config_path: Optional[str] = None):
        self._agents: Dict[str, A2AAgentEntry] = {}
        self._config_path = config_path or ".superoptix/a2a_agents.json"

    def _key(self, url: str) -> str:
        return normalize_url(url)

    def _entries_named(self, name: str) -> List[A2AAgentEntry]:
        return [entry for entry in self._agents.values() if entry.name == name]

    def _require_unique_alias(self, name: str, url: str) -> None:
        """Reject a presentational name already bound to a different URL."""
        key = self._key(url)
        clashes = [
            entry for entry in self._entries_named(name) if self._key(entry.url) != key
        ]
        if clashes:
            urls = ", ".join(sorted({self._key(e.url) for e in clashes} | {key}))
            raise AmbiguousAgentName(
                f"Agent name {name!r} is already bound to another URL; "
                f"route by URL instead. Conflicting URLs: {urls}"
            )

    def _put(self, entry: A2AAgentEntry) -> A2AAgentEntry:
        key = self._key(entry.url)
        entry.url = key
        self._require_unique_alias(entry.name, key)
        self._agents[key] = entry
        return entry

    def _skills_from_card(self, card: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for skill in card.get("skills") or []:
            if not isinstance(skill, dict):
                continue
            out.append(
                {
                    "id": skill.get("id") or skill.get("name") or "",
                    "name": skill.get("name") or "",
                }
            )
        return out

    def add(self, name: str, url: str, description: str = "") -> bool:
        """Add an agent to the registry.

        Args:
            name: Local presentational alias (not a remote identity).
            url: A2A server URL (stable routing key).
            description: Optional description used if the peer is unreachable.

        Returns:
            True if the agent is reachable, False otherwise.
        """
        from superoptix.protocols.a2a.client import A2AClient

        key = self._key(url)
        try:
            client = A2AClient(agent_url=url)
            if not client.connect():
                raise RuntimeError("connect failed")
            card = client.agent_card or {}
            entry = A2AAgentEntry(
                name=name,
                url=key,
                description=str(card.get("description") or description or ""),
                version=str(
                    card.get("version") or card.get("protocolVersion") or "1.0"
                ),
                skills=self._skills_from_card(card),
                verified=True,
            )
            self._put(entry)
            return True
        except AmbiguousAgentName:
            raise
        except Exception:
            entry = A2AAgentEntry(
                name=name,
                url=key,
                description=description or "Unverified agent",
                verified=False,
            )
            self._put(entry)
            return False

    def remove(self, name: str) -> bool:
        """Remove the unique agent with this presentational name."""
        matches = self._entries_named(name)
        if not matches:
            key = self._key(name)
            if key in self._agents:
                del self._agents[key]
                return True
            return False
        if len(matches) > 1:
            raise AmbiguousAgentName(
                f"Agent name {name!r} matches {len(matches)} URLs; "
                "remove by URL instead."
            )
        del self._agents[self._key(matches[0].url)]
        return True

    def remove_by_url(self, url: str) -> bool:
        """Remove an agent by its stable URL identity."""
        key = self._key(url)
        if key in self._agents:
            del self._agents[key]
            return True
        return False

    def discover_from_url(self, url: str) -> Optional[A2AAgentEntry]:
        """Discover an agent from a URL.

        The registry key is the URL. The card ``name`` is stored only as a
        presentational alias and must not collide with another URL's alias.
        """
        from superoptix.protocols.a2a.client import A2AClient

        key = self._key(url)
        try:
            client = A2AClient(agent_url=url)
            if not client.connect():
                return None
            card = client.agent_card or {}
            display = str(card.get("name") or "").strip() or key
            entry = A2AAgentEntry(
                name=display,
                url=key,
                description=str(card.get("description") or ""),
                version=str(
                    card.get("version") or card.get("protocolVersion") or "1.0"
                ),
                skills=self._skills_from_card(card),
                verified=True,
            )
            return self._put(entry)
        except AmbiguousAgentName:
            raise
        except Exception:
            return None

    def get(self, name: str) -> Optional[A2AAgentEntry]:
        """Get an agent by presentational name, or by URL.

        Raises:
            AmbiguousAgentName: if more than one URL shares the same name.
        """
        key = self._key(name)
        if key in self._agents:
            return self._agents[key]
        matches = self._entries_named(name)
        if not matches:
            return None
        if len(matches) > 1:
            urls = ", ".join(sorted(self._key(e.url) for e in matches))
            raise AmbiguousAgentName(
                f"Agent name {name!r} matches multiple URLs ({urls}); "
                "route by URL instead of card name."
            )
        return matches[0]

    def get_by_url(self, url: str) -> Optional[A2AAgentEntry]:
        """Get an agent by its stable URL identity."""
        return self._agents.get(self._key(url))

    def list_all(self) -> List[A2AAgentEntry]:
        """List all registered agents."""
        return list(self._agents.values())

    def save(self) -> None:
        """Save registry to file (URL-keyed; name is presentational)."""
        data = {
            self._key(entry.url): {
                "name": entry.name,
                "url": self._key(entry.url),
                "description": entry.description,
                "version": entry.version,
                "skills": entry.skills,
            }
            for entry in self._agents.values()
        }
        path = Path(self._config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    def load(self) -> None:
        """Load registry from file.

        Supports the current URL-keyed format and the older name-keyed format
        (top-level key was the alias, with ``url`` inside each object).
        """
        path = Path(self._config_path)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            self._agents.clear()
            for top_key, info in data.items():
                if not isinstance(info, dict):
                    continue
                url = str(info.get("url") or top_key)
                name = str(info.get("name") or top_key)
                entry = A2AAgentEntry(
                    name=name,
                    url=self._key(url),
                    description=info.get("description", ""),
                    version=info.get("version", "1.0"),
                    skills=info.get("skills", []),
                )
                try:
                    self._put(entry)
                except AmbiguousAgentName:
                    # Prefer URL identity; rewrite colliding presentational alias.
                    entry.name = self._key(url)
                    self._agents[self._key(url)] = entry
        except Exception:
            pass


def agent_identity_from_card(card: Dict[str, Any]) -> str:
    """Origin-bound identity for routing: prefer card URL, never name alone.

    Card ``name`` is presentational (arXiv:2609.27624). Callers that need a
    display label should read ``card["name"]`` separately.
    """
    url = str(card.get("url") or "").strip()
    if url:
        return normalize_url(url)
    interfaces = card.get("supportedInterfaces") or card.get("interfaces") or []
    for interface in interfaces:
        if isinstance(interface, dict):
            iface_url = str(interface.get("url") or "").strip()
            if iface_url:
                parsed = urlparse(iface_url)
                if parsed.scheme and parsed.netloc:
                    return normalize_url(f"{parsed.scheme}://{parsed.netloc}")
    return str(card.get("name") or "agent")
