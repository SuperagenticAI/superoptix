"""Negotiate between the A2A 0.3 and 1.0 spec lines.

The installed base is on 0.3. Of the eight frameworks SuperOptiX adapts, five
declare no A2A support at all and the three that do — CrewAI, Google ADK and
Pydantic AI — are pinned to the pre-1.0 line. A brownfield promise that only
speaks 1.0 therefore reaches almost none of the agents already deployed.

Bridging is table stakes rather than differentiation, but omitting it makes the
claim false for most of the market.
"""

from __future__ import annotations

from typing import Any, Dict, List

V1 = "1.0"
V03 = "0.3"

# 1.0 standardised every enum to SCREAMING_SNAKE_CASE and prefixed task states.
_STATE_TO_V03 = {
    "TASK_STATE_SUBMITTED": "submitted",
    "TASK_STATE_WORKING": "working",
    "TASK_STATE_INPUT_REQUIRED": "input-required",
    "TASK_STATE_COMPLETED": "completed",
    "TASK_STATE_CANCELED": "canceled",
    "TASK_STATE_FAILED": "failed",
    "TASK_STATE_REJECTED": "rejected",
    "TASK_STATE_AUTH_REQUIRED": "auth-required",
    "TASK_STATE_UNKNOWN": "unknown",
}
_STATE_TO_V1 = {v: k for k, v in _STATE_TO_V03.items()}

_ROLE_TO_V03 = {"ROLE_USER": "user", "ROLE_AGENT": "agent"}
_ROLE_TO_V1 = {v: k for k, v in _ROLE_TO_V03.items()}


def normalize_version(value: Any) -> str | None:
    """Reduce a spec-version spelling to the line it belongs to.

    Returns None for a version we do not serve. Mapping every unrecognised
    string onto 0.3 would silently accept "99.0", which the spec requires us to
    reject with VersionNotSupportedError.
    """
    text = str(value or "").strip()
    if not text:
        return V1
    parts = text.split(".")
    if parts[0] == "1":
        return V1
    if parts[0] == "0" and len(parts) > 1 and parts[1] == "3":
        return V03
    return None


def _part_to_v03(part: Dict[str, Any]) -> Dict[str, Any]:
    """1.0 unified Part; 0.3 wrapped each content type in its own object."""
    if "text" in part:
        return {"kind": "text", "text": part["text"]}
    if "data" in part:
        return {"kind": "data", "data": part["data"]}
    if "raw" in part or "url" in part:
        file_payload: Dict[str, Any] = {}
        if part.get("filename"):
            file_payload["name"] = part["filename"]
        if part.get("mediaType"):
            file_payload["mimeType"] = part["mediaType"]
        if part.get("raw"):
            file_payload["bytes"] = part["raw"]
        if part.get("url"):
            file_payload["uri"] = part["url"]
        return {"kind": "file", "file": file_payload}
    return dict(part)


def _part_to_v1(part: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a 0.3 wrapped part onto the unified 1.0 Part."""
    if "text" in part:
        return {"text": part["text"]}
    if "data" in part:
        return {"data": part["data"]}
    file_payload = part.get("file")
    if isinstance(file_payload, dict):
        flat: Dict[str, Any] = {}
        if file_payload.get("name"):
            flat["filename"] = file_payload["name"]
        if file_payload.get("mimeType"):
            flat["mediaType"] = file_payload["mimeType"]
        if file_payload.get("bytes"):
            flat["raw"] = file_payload["bytes"]
        if file_payload.get("uri"):
            flat["url"] = file_payload["uri"]
        return flat
    return {k: v for k, v in part.items() if k != "kind"}


def _message_to_v03(message: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(message)
    out["role"] = _ROLE_TO_V03.get(str(message.get("role")), message.get("role"))
    out["parts"] = [
        _part_to_v03(p) for p in message.get("parts") or [] if isinstance(p, dict)
    ]
    return out


def _message_to_v1(message: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(message)
    out["role"] = _ROLE_TO_V1.get(str(message.get("role")), message.get("role"))
    out["parts"] = [
        _part_to_v1(p) for p in message.get("parts") or [] if isinstance(p, dict)
    ]
    return out


def task_to_v03(task: Dict[str, Any]) -> Dict[str, Any]:
    """Render a 1.0 Task as a 0.3 client expects to read it."""
    out = dict(task or {})
    status = dict(out.get("status") or {})
    if status.get("state"):
        status["state"] = _STATE_TO_V03.get(str(status["state"]), status["state"])
    if isinstance(status.get("message"), dict):
        status["message"] = _message_to_v03(status["message"])
    if status:
        out["status"] = status
    if out.get("history"):
        out["history"] = [
            _message_to_v03(m) for m in out["history"] if isinstance(m, dict)
        ]
    if out.get("artifacts"):
        out["artifacts"] = [
            {**a, "parts": [_part_to_v03(p) for p in a.get("parts") or []]}
            for a in out["artifacts"]
            if isinstance(a, dict)
        ]
    return out


def task_to_v1(task: Dict[str, Any]) -> Dict[str, Any]:
    """Read a 0.3 Task into the 1.0 shape."""
    out = dict(task or {})
    status = dict(out.get("status") or {})
    if status.get("state"):
        status["state"] = _STATE_TO_V1.get(str(status["state"]), status["state"])
    if isinstance(status.get("message"), dict):
        status["message"] = _message_to_v1(status["message"])
    if status:
        out["status"] = status
    if out.get("history"):
        out["history"] = [
            _message_to_v1(m) for m in out["history"] if isinstance(m, dict)
        ]
    if out.get("artifacts"):
        out["artifacts"] = [
            {**a, "parts": [_part_to_v1(p) for p in a.get("parts") or []]}
            for a in out["artifacts"]
            if isinstance(a, dict)
        ]
    return out


def message_to_v1(message: Dict[str, Any]) -> Dict[str, Any]:
    """Read an inbound 0.3 message into the 1.0 shape."""
    return _message_to_v1(dict(message or {}))


def card_to_v03(card: Dict[str, Any]) -> Dict[str, Any]:
    """Present a 1.0 card to a 0.3 client.

    A 0.3 reader expects a single top-level ``url`` and its own protocol
    version; advertising only ``supportedInterfaces`` leaves it with nothing
    to call.
    """
    out = dict(card or {})
    interfaces: List[Dict[str, Any]] = list(out.get("supportedInterfaces") or [])
    legacy = [
        i for i in interfaces if normalize_version(i.get("protocolVersion")) == V03
    ]
    chosen = (legacy or interfaces or [{}])[0]
    if chosen.get("url"):
        out["url"] = chosen["url"]
    out["protocolVersion"] = V03
    if chosen.get("protocolBinding"):
        out["preferredTransport"] = chosen["protocolBinding"]
    return out


def requested_version(headers: Any) -> str | None:
    """Spec line the caller asked for, or None if we do not serve it."""
    try:
        raw = headers.get("A2A-Version") or headers.get("a2a-version")
    except AttributeError:
        raw = None
    return normalize_version(raw)
