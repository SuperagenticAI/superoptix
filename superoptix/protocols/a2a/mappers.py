"""Mapping helpers between A2A transport objects and SuperOptiX runtime payloads."""

from __future__ import annotations

import json
from typing import Any, Dict


def _to_camel_case(name: str) -> str:
    if "_" not in name:
        return name
    head, *tail = name.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in tail if part)


def normalize_a2a_payload(value: Any) -> Any:
    """Best-effort conversion to JSON-serializable camelCase dicts."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [normalize_a2a_payload(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_a2a_payload(item) for item in value]
    if isinstance(value, dict):
        return {
            _to_camel_case(str(key)): normalize_a2a_payload(item)
            for key, item in value.items()
            if item is not None
        }
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return normalize_a2a_payload(value.model_dump(exclude_none=True))
    if hasattr(value, "__dict__"):
        return normalize_a2a_payload(
            {
                key: item
                for key, item in vars(value).items()
                if not key.startswith("_") and item is not None
            }
        )
    return value


def normalize_agent_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize old and new Agent Card shapes into the v1-style form."""
    payload = normalize_a2a_payload(card or {})
    if not isinstance(payload, dict):
        return {}

    supported_interfaces = list(payload.get("supportedInterfaces") or [])
    if not supported_interfaces and payload.get("url"):
        preferred_binding = (
            payload.get("preferredTransport")
            or payload.get("preferred_transport")
            or "JSONRPC"
        )
        supported_interfaces.append(
            {
                "url": payload["url"],
                "protocolBinding": preferred_binding,
                "protocolVersion": payload.get("protocolVersion")
                or payload.get("protocol_version")
                or "0.3.0",
            }
        )
        for interface in (
            payload.get("additionalInterfaces")
            or payload.get("additional_interfaces")
            or []
        ):
            normalized = normalize_a2a_payload(interface)
            if isinstance(normalized, dict):
                supported_interfaces.append(
                    {
                        "url": normalized.get("url"),
                        "protocolBinding": normalized.get("protocolBinding")
                        or normalized.get("transport")
                        or "JSONRPC",
                        "protocolVersion": normalized.get("protocolVersion")
                        or payload.get("protocolVersion")
                        or payload.get("protocol_version")
                        or "0.3.0",
                    }
                )

    capabilities = dict(payload.get("capabilities") or {})
    if "pushNotifications" not in capabilities and "push_notifications" in capabilities:
        capabilities["pushNotifications"] = bool(capabilities.get("push_notifications"))
    if (
        "stateTransitionHistory" not in capabilities
        and "state_transition_history" in capabilities
    ):
        capabilities["stateTransitionHistory"] = bool(
            capabilities.get("state_transition_history")
        )
    if "extendedAgentCard" not in capabilities:
        capabilities["extendedAgentCard"] = bool(
            payload.get("supportsAuthenticatedExtendedCard")
            or payload.get("supports_authenticated_extended_card")
            or capabilities.get("extended_agent_card")
        )

    payload["supportedInterfaces"] = supported_interfaces
    payload["capabilities"] = capabilities
    payload.pop("url", None)
    payload.pop("protocolVersion", None)
    payload.pop("protocol_version", None)
    payload.pop("preferredTransport", None)
    payload.pop("preferred_transport", None)
    payload.pop("additionalInterfaces", None)
    payload.pop("additional_interfaces", None)
    payload.pop("supportsAuthenticatedExtendedCard", None)
    payload.pop("supports_authenticated_extended_card", None)
    return payload


def extract_text_from_message(message: Any) -> str:
    """Best-effort extraction of user text from an A2A message."""
    if isinstance(message, dict):
        parts = list(message.get("parts", []) or [])
    else:
        parts = list(getattr(message, "parts", []) or [])
    texts = []
    for part in parts:
        if isinstance(part, dict):
            text = part.get("text")
        else:
            text = getattr(part, "text", None)
        if text:
            texts.append(str(text))
    return "\n".join(texts).strip()


def runtime_result_to_text(result: Dict[str, Any]) -> str:
    """Render a runtime result as agent-visible text for A2A responses."""
    if "response" in result:
        return str(result["response"])
    if len(result) == 1:
        return str(next(iter(result.values())))
    return json.dumps(result, sort_keys=True)


def extract_text_from_payload(payload: Dict[str, Any]) -> str:
    """Extract the first meaningful text from a v1 task, message, or event payload."""
    if not isinstance(payload, dict):
        return str(payload)

    message = payload.get("message")
    if isinstance(message, dict):
        text = extract_text_from_message(message)
        if text:
            return text

    task = payload.get("task")
    if isinstance(task, dict):
        status = task.get("status") or {}
        status_message = status.get("message")
        if isinstance(status_message, dict):
            text = extract_text_from_message(status_message)
            if text:
                return text
        artifacts = list(task.get("artifacts") or [])
        for artifact in artifacts:
            parts = list((artifact or {}).get("parts") or [])
            text = extract_text_from_message({"parts": parts})
            if text:
                return text

    status_update = payload.get("statusUpdate")
    if isinstance(status_update, dict):
        status = status_update.get("status") or {}
        status_message = status.get("message")
        if isinstance(status_message, dict):
            text = extract_text_from_message(status_message)
            if text:
                return text

    artifact_update = payload.get("artifactUpdate")
    if isinstance(artifact_update, dict):
        artifact = artifact_update.get("artifact")
        if isinstance(artifact, dict):
            text = extract_text_from_message({"parts": artifact.get("parts") or []})
            if text:
                return text

    return json.dumps(payload, sort_keys=True)
