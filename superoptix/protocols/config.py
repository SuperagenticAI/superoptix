"""Protocol configuration helpers for SuperOptiX."""

from __future__ import annotations

from typing import Any, Dict, List


LEGACY_PROTOCOL_BACKENDS = {"agenspy", "protocols"}
SUPPORTED_PROTOCOL_TYPES = {"mcp", "a2a", "agent2agent"}


def normalize_protocol_type(value: Any) -> str:
    """Normalize protocol labels to stable internal names."""
    protocol_type = str(value or "").strip().lower()
    if protocol_type in {"a2a", "agent2agent"}:
        return "a2a"
    if protocol_type == "mcp":
        return "mcp"
    return protocol_type


def _protocol_type_from_url(url: str) -> str:
    lowered = str(url or "").strip().lower()
    if lowered.startswith("mcp://"):
        return "mcp"
    if lowered.startswith(("a2a://", "http://", "https://")):
        return "a2a"
    return "custom"


def normalize_protocol_entry(entry: Any) -> Dict[str, Any] | None:
    """Normalize a protocol entry from SuperSpec into a dict shape."""
    if isinstance(entry, str):
        url = entry.strip()
        if not url:
            return None
        return {
            "type": _protocol_type_from_url(url),
            "url": url,
        }

    if not isinstance(entry, dict):
        return None

    normalized = dict(entry)
    url = str(
        normalized.get("url")
        or normalized.get("server_url")
        or normalized.get("agent_url")
        or ""
    ).strip()
    if not url:
        return None

    protocol_type = normalize_protocol_type(
        normalized.get("type") or _protocol_type_from_url(url)
    )
    normalized["type"] = protocol_type
    normalized["url"] = url
    normalized.pop("server_url", None)
    normalized.pop("agent_url", None)
    return normalized


def extract_protocol_entries(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return normalized protocol config entries, merging legacy MCP config."""
    protocols: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for entry in list(spec.get("protocols", []) or []):
        normalized = normalize_protocol_entry(entry)
        if not normalized:
            continue
        key = (normalized["type"], normalized["url"])
        if key in seen:
            continue
        seen.add(key)
        protocols.append(normalized)

    for server_url in list(spec.get("mcp_servers", []) or []):
        normalized = normalize_protocol_entry({"type": "mcp", "url": server_url})
        if not normalized:
            continue
        key = (normalized["type"], normalized["url"])
        if key in seen:
            continue
        seen.add(key)
        protocols.append(normalized)

    return protocols


def uses_protocol_runtime(spec: Dict[str, Any]) -> bool:
    """Detect whether the spec should compile to the protocol-first path."""
    tool_backend = str(spec.get("tool_backend", "dspy")).strip().lower()
    return tool_backend in LEGACY_PROTOCOL_BACKENDS or bool(
        extract_protocol_entries(spec)
    )

