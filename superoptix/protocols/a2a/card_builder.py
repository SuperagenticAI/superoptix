"""Helpers for building A2A v1 Agent Card payloads from SuperSpec playbooks."""

from __future__ import annotations

from typing import Any, Dict, List


def _skill_examples(task: Dict[str, Any]) -> List[str] | None:
    instruction = str(task.get("instruction", "")).strip()
    if not instruction:
        return None
    return [instruction]


def build_a2a_agent_card_payload(
    *,
    metadata: Dict[str, Any],
    spec: Dict[str, Any],
    agent_url: str,
    rpc_url: str = "/a2a/jsonrpc",
    protocol_version: str = "1.0",
    legacy_protocol_version: str | None = None,
    skills_override: List[Dict[str, Any]] | None = None,
    security_schemes: Dict[str, Any] | None = None,
    icon_url: str | None = None,
    documentation_url: str | None = None,
    preferred_transport: str = "JSONRPC",
    push_notifications: bool = False,
) -> Dict[str, Any]:
    """Create an A2A Agent Card payload from SuperSpec metadata.

    Args:
        legacy_protocol_version: when set (e.g. "0.3"), the card additionally
            advertises that spec line so pre-1.0 clients can still negotiate.
            This mirrors how SuperQode publishes one card for both lines.
        skills_override: use these skill objects instead of deriving them from
            ``spec["tasks"]``. Used by the public catalogue endpoint.
        security_schemes: A2A ``securitySchemes`` map declaring how callers
            authenticate.
    """
    tasks = list(spec.get("tasks", []) or [])
    persona = spec.get("persona", {}) or {}

    description = str(
        metadata.get("description")
        or persona.get("goal")
        or persona.get("instructions")
        or f"A2A exposure for {metadata.get('name', metadata.get('id', 'agent'))}"
    ).strip()

    skills = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        skill_id = str(task.get("name") or task.get("id") or "task").strip()
        if not skill_id:
            continue
        skills.append(
            {
                "id": skill_id,
                "name": str(task.get("name") or skill_id).strip(),
                "description": str(
                    task.get("description")
                    or task.get("instruction")
                    or "Execute an agent task"
                ).strip(),
                "tags": ["superoptix", "task"],
                "examples": _skill_examples(task),
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"],
            }
        )

    base_url = agent_url.rstrip("/")
    if skills_override is not None:
        skills = list(skills_override)

    interfaces: List[Dict[str, Any]] = [
        {
            "url": f"{base_url}{rpc_url}",
            "protocolBinding": "JSONRPC",
            "protocolVersion": protocol_version,
        },
        {
            "url": base_url,
            "protocolBinding": "HTTP+JSON",
            "protocolVersion": protocol_version,
        },
    ]
    if legacy_protocol_version:
        # Advertised so pre-1.0 clients can negotiate rather than skip the agent.
        interfaces.append(
            {
                "url": f"{base_url}{rpc_url}",
                "protocolBinding": "JSONRPC",
                "protocolVersion": legacy_protocol_version,
            }
        )

    card: Dict[str, Any] = {
        "name": str(metadata.get("name") or metadata.get("id") or "SuperOptiX Agent"),
        "description": description,
        "version": str(metadata.get("version") or "1.0.0"),
        "protocolVersion": protocol_version,
        "url": base_url,
        "preferredTransport": preferred_transport,
        "supportedInterfaces": interfaces,
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "capabilities": {
            "streaming": True,
            "pushNotifications": push_notifications,
            "stateTransitionHistory": True,
            "extendedAgentCard": False,
        },
        "skills": skills,
        "provider": {
            "organization": "Superagentic AI",
            "url": "https://super-agentic.ai",
        },
    }
    if security_schemes:
        card["securitySchemes"] = security_schemes
    if icon_url:
        card["iconUrl"] = icon_url
    if documentation_url:
        card["documentationUrl"] = documentation_url
    return card
