"""Helpers for building A2A Agent Card payloads from SuperSpec playbooks."""

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
    protocol_version: str = "0.3.0",
) -> Dict[str, Any]:
    """Create a minimal A2A Agent Card payload from SuperSpec metadata."""
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
                "input_modes": ["text"],
                "output_modes": ["text", "task-status"],
            }
        )

    return {
        "name": str(metadata.get("name") or metadata.get("id") or "SuperOptiX Agent"),
        "description": description,
        "url": f"{agent_url.rstrip('/')}{rpc_url}",
        "version": str(metadata.get("version") or "1.0.0"),
        "protocol_version": protocol_version,
        "default_input_modes": ["text"],
        "default_output_modes": ["text", "task-status"],
        "capabilities": {
            "streaming": True,
            "push_notifications": False,
            "state_transition_history": True,
        },
        "skills": skills,
        "preferred_transport": "JSONRPC",
        "additional_interfaces": [
            {
                "url": f"{agent_url.rstrip('/')}{rpc_url}",
                "transport": "JSONRPC",
            }
        ],
        "provider": {
            "organization": "SuperOptiX",
            "url": "https://super-agentic.ai",
        },
        "supports_authenticated_extended_card": False,
    }

