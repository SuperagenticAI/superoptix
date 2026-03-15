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
) -> Dict[str, Any]:
    """Create a minimal A2A v1 Agent Card payload from SuperSpec metadata."""
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

    return {
        "name": str(metadata.get("name") or metadata.get("id") or "SuperOptiX Agent"),
        "description": description,
        "version": str(metadata.get("version") or "1.0.0"),
        "supportedInterfaces": [
            {
                "url": base_url,
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": protocol_version,
            },
            {
                "url": f"{base_url}{rpc_url}",
                "protocolBinding": "JSONRPC",
                "protocolVersion": protocol_version,
            },
        ],
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True,
            "extendedAgentCard": False,
        },
        "skills": skills,
        "provider": {
            "organization": "SuperOptiX",
            "url": "https://super-agentic.ai",
        },
    }
