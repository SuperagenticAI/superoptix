"""A2A v1 client protocol implementation for SuperOptiX."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List
from urllib.parse import urlparse

import dspy
import requests

from superoptix.protocols.a2a.mappers import (
    extract_text_from_payload,
    normalize_a2a_payload,
    normalize_agent_card,
)
from superoptix.protocols.base import BaseProtocol, ProtocolType

logger = logging.getLogger(__name__)

_WELL_KNOWN_CARD_PATH = "/.well-known/agent-card.json"
_SUPPORTED_BINDINGS = ("HTTP+JSON", "JSONRPC")


def _trim_trailing_slash(value: str) -> str:
    return value[:-1] if value.endswith("/") else value


def _base_url_candidates(agent_url: str) -> List[str]:
    raw = _trim_trailing_slash(agent_url.strip())
    if not raw:
        return []

    parsed = urlparse(raw)
    if parsed.path.endswith(_WELL_KNOWN_CARD_PATH):
        path = parsed.path[: -len(_WELL_KNOWN_CARD_PATH)] or "/"
        rebuilt = parsed._replace(path=path, query="", fragment="").geturl()
        return [_trim_trailing_slash(rebuilt)]

    suffixes = (
        "/a2a/jsonrpc",
        "/message:send",
        "/message:stream",
    )
    for suffix in suffixes:
        if parsed.path.endswith(suffix):
            path = parsed.path[: -len(suffix)] or "/"
            rebuilt = parsed._replace(path=path, query="", fragment="").geturl()
            return [_trim_trailing_slash(rebuilt), raw]

    return [raw]


def _task_state_terminal(state: str | None) -> bool:
    return state in {
        "TASK_STATE_COMPLETED",
        "TASK_STATE_CANCELED",
        "TASK_STATE_FAILED",
        "TASK_STATE_REJECTED",
    }


class A2AClient(BaseProtocol):
    """Native A2A client for protocol-level agent delegation."""

    def __init__(
        self,
        agent_url: str,
        timeout: int = 30,
        mock_agent_card: Dict[str, Any] | None = None,
        **kwargs,
    ):
        protocol_config = {
            "type": ProtocolType.AGENT2AGENT,
            "agent_url": agent_url,
            "timeout": timeout,
        }
        super().__init__(protocol_config, **kwargs)
        self.agent_url = agent_url
        self.timeout = timeout
        self.mock_agent_card = mock_agent_card
        self.agent_card: Dict[str, Any] = {}
        self.available_skills: List[Dict[str, Any]] = []
        self.selected_interface: Dict[str, Any] = {}
        self.task_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _json_headers() -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "A2A-Version": "1.0",
        }

    def _http(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        headers = dict(self._json_headers())
        headers.update(kwargs.pop("headers", {}) or {})
        headers = {key: value for key, value in headers.items() if value}
        response = requests.request(
            method,
            url,
            timeout=self.timeout,
            headers=headers,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def _fetch_agent_card(self) -> Dict[str, Any]:
        last_error: Exception | None = None
        for base_url in _base_url_candidates(self.agent_url):
            if base_url.endswith(_WELL_KNOWN_CARD_PATH):
                card_url = base_url
            else:
                card_url = f"{base_url}{_WELL_KNOWN_CARD_PATH}"
            try:
                response = self._http("GET", card_url, headers={"Content-Type": ""})
                return normalize_agent_card(response.json())
            except Exception as exc:  # pragma: no cover - exercised in live use
                last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError("Unable to resolve A2A agent card URL")

    @staticmethod
    def _select_interface(card: Dict[str, Any]) -> Dict[str, Any]:
        interfaces = list(card.get("supportedInterfaces") or [])
        for binding in _SUPPORTED_BINDINGS:
            for interface in interfaces:
                if str(interface.get("protocolBinding") or "").upper() == binding:
                    return dict(interface)
        return dict(interfaces[0]) if interfaces else {}

    def _make_message(
        self, message_text: str, *, task_id: str | None = None
    ) -> Dict[str, Any]:
        return {
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "role": "ROLE_USER",
            "parts": [{"text": message_text}],
        }

    @staticmethod
    def _task_payload_to_response(payload: Dict[str, Any]) -> Dict[str, Any]:
        task = payload.get("task")
        message = payload.get("message")
        text = extract_text_from_payload(payload)
        task_id = None
        if isinstance(task, dict):
            task_id = task.get("id")
        elif isinstance(message, dict):
            task_id = message.get("taskId")
        return {
            "response": text,
            "task_id": str(task_id) if task_id else None,
            "agent_url": "",
            "result": payload,
        }

    def _jsonrpc_request(
        self,
        method: str,
        params: Dict[str, Any],
        *,
        stream: bool = False,
    ) -> Any:
        rpc_url = self.selected_interface.get("url")
        if not rpc_url:
            raise RuntimeError("A2A JSON-RPC interface is not available")
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        response = self._http(
            "POST",
            rpc_url,
            data=json.dumps(payload),
            stream=stream,
        )
        if stream:
            return self._iter_sse_json(response, expect_jsonrpc=True)
        parsed = response.json()
        if "error" in parsed:
            raise RuntimeError(str(parsed["error"]))
        return normalize_a2a_payload(parsed.get("result") or {})

    def _rest_request(
        self,
        method: str,
        path: str,
        *,
        json_body: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        stream: bool = False,
    ) -> Any:
        base_url = self.selected_interface.get("url")
        if not base_url:
            raise RuntimeError("A2A HTTP+JSON interface is not available")
        response = self._http(
            method,
            f"{_trim_trailing_slash(base_url)}{path}",
            json=json_body,
            params=params,
            stream=stream,
        )
        if stream:
            return self._iter_sse_json(response, expect_jsonrpc=False)
        return normalize_a2a_payload(response.json())

    @staticmethod
    def _iter_sse_json(
        response: requests.Response, *, expect_jsonrpc: bool
    ) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data:"):
                continue
            data = raw_line[len("data:") :].strip()
            if not data:
                continue
            payload = normalize_a2a_payload(json.loads(data))
            if expect_jsonrpc:
                payload = normalize_a2a_payload(payload.get("result") or {})
            events.append(payload)
        return events

    def _binding(self) -> str:
        return str(self.selected_interface.get("protocolBinding") or "").upper()

    def connect(self) -> bool:
        try:
            if self.mock_agent_card is not None:
                self.agent_card = normalize_agent_card(dict(self.mock_agent_card))
            else:
                self.agent_card = self._fetch_agent_card()
            self.available_skills = list(self.agent_card.get("skills", []) or [])
            self.selected_interface = self._select_interface(self.agent_card)
            self._connected = bool(self.selected_interface)
            return self._connected
        except Exception as exc:
            logger.error("A2A connection failed: %s", exc)
            self._connected = False
            return False

    def disconnect(self) -> None:
        self.selected_interface = {}
        self._connected = False

    def get_capabilities(self) -> Dict[str, Any]:
        card = self.agent_card or {}
        interface = self.selected_interface or {}
        capabilities = card.get("capabilities") or {}
        self._capabilities = {
            "protocol": "a2a",
            "version": str(interface.get("protocolVersion") or "1.0"),
            "binding": interface.get("protocolBinding"),
            "agent_url": self.agent_url,
            "skills": [skill.get("id") for skill in self.available_skills],
            "streaming": bool(capabilities.get("streaming")),
            "push_notifications": bool(capabilities.get("pushNotifications")),
            "state_transition_history": bool(
                capabilities.get("stateTransitionHistory")
            ),
        }
        return self._capabilities

    def discover_peers(self) -> List[str]:
        return [self.agent_url]

    def _send_message_http(self, message_text: str) -> Dict[str, Any]:
        response_payload = self._rest_request(
            "POST",
            "/message:send",
            json_body={
                "message": self._make_message(message_text),
                "configuration": {
                    "acceptedOutputModes": ["text/plain"],
                    "returnImmediately": False,
                },
            },
        )
        result = self._task_payload_to_response(response_payload)
        task_id = result.get("task_id")
        if task_id and isinstance(response_payload.get("task"), dict):
            self.task_cache[task_id] = dict(response_payload["task"])
        result["agent_url"] = self.agent_url
        return result

    def _send_message_jsonrpc(self, message_text: str) -> Dict[str, Any]:
        response_payload = self._jsonrpc_request(
            "SendMessage",
            {
                "message": self._make_message(message_text),
                "configuration": {
                    "acceptedOutputModes": ["text/plain"],
                    "returnImmediately": False,
                },
            },
        )
        result = self._task_payload_to_response(response_payload)
        task_id = result.get("task_id")
        if task_id and isinstance(response_payload.get("task"), dict):
            self.task_cache[task_id] = dict(response_payload["task"])
        result["agent_url"] = self.agent_url
        return result

    def send_message(self, message_text: str) -> Dict[str, Any]:
        if self.mock_agent_card is not None:
            task_id = f"mock-task-{len(self.task_cache) + 1}"
            task_payload = {
                "id": task_id,
                "contextId": f"context-{task_id}",
                "status": {"state": "TASK_STATE_COMPLETED"},
            }
            self.task_cache[task_id] = task_payload
            return {
                "response": f"Mock A2A response from {self.agent_url}: {message_text}",
                "agent_url": self.agent_url,
                "task_id": task_id,
                "result": {"task": task_payload},
            }

        if not self._connected and not self.connect():
            raise RuntimeError("A2A client is not connected")
        if self._binding() == "JSONRPC":
            return self._send_message_jsonrpc(message_text)
        return self._send_message_http(message_text)

    def _cache_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = payload.get("id")
        if task_id:
            self.task_cache[str(task_id)] = payload
        return payload

    def get_task(
        self, task_id: str, history_length: int | None = None
    ) -> Dict[str, Any]:
        if self.mock_agent_card is not None:
            payload = dict(self.task_cache.get(task_id, {}))
            if not payload:
                raise KeyError(f"Unknown mock task: {task_id}")
            return payload

        if not self._connected and not self.connect():
            raise RuntimeError("A2A client is not connected")
        if self._binding() == "JSONRPC":
            payload = self._jsonrpc_request(
                "GetTask",
                {"id": task_id, "historyLength": history_length},
            )
        else:
            params = (
                {"historyLength": history_length}
                if history_length is not None
                else None
            )
            payload = self._rest_request("GET", f"/tasks/{task_id}", params=params)
        return self._cache_task(payload)

    def list_tasks(
        self,
        *,
        context_id: str | None = None,
        status: str | None = None,
        page_size: int | None = None,
    ) -> Dict[str, Any]:
        if not self._connected and not self.connect():
            raise RuntimeError("A2A client is not connected")

        params = {
            "contextId": context_id,
            "status": status,
            "pageSize": page_size,
        }
        params = {key: value for key, value in params.items() if value is not None}
        if self._binding() == "JSONRPC":
            return self._jsonrpc_request("ListTasks", params)
        return self._rest_request("GET", "/tasks", params=params or None)

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        if self.mock_agent_card is not None:
            payload = dict(self.task_cache.get(task_id, {}))
            if not payload:
                raise KeyError(f"Unknown mock task: {task_id}")
            payload["status"] = {"state": "TASK_STATE_CANCELED"}
            self.task_cache[task_id] = payload
            return payload

        if not self._connected and not self.connect():
            raise RuntimeError("A2A client is not connected")
        if self._binding() == "JSONRPC":
            payload = self._jsonrpc_request("CancelTask", {"id": task_id})
        else:
            payload = self._rest_request("POST", f"/tasks/{task_id}:cancel")
        return self._cache_task(payload)

    def resubscribe(self, task_id: str) -> Dict[str, Any]:
        if self.mock_agent_card is not None:
            payload = dict(self.task_cache.get(task_id, {}))
            if not payload:
                raise KeyError(f"Unknown mock task: {task_id}")
            return {"task_id": task_id, "events": [{"task": payload}]}

        if not self._connected and not self.connect():
            raise RuntimeError("A2A client is not connected")

        cached = self.task_cache.get(task_id, {})
        if _task_state_terminal(str((cached.get("status") or {}).get("state"))):
            return {"task_id": task_id, "events": [{"task": cached}]}

        if self._binding() == "JSONRPC":
            events = self._jsonrpc_request(
                "SubscribeToTask",
                {"id": task_id},
                stream=True,
            )
        else:
            events = self._rest_request(
                "POST",
                f"/tasks/{task_id}:subscribe",
                stream=True,
            )
        normalized_events = list(events or [])
        if normalized_events:
            last = normalized_events[-1]
            task = last.get("task")
            if isinstance(task, dict) and task.get("id"):
                self.task_cache[str(task["id"])] = task
        return {"task_id": task_id, "events": normalized_events}

    def _handle_request(self, **kwargs) -> dspy.Prediction:
        message_text = str(
            kwargs.get("message") or kwargs.get("query") or kwargs.get("task") or ""
        ).strip()
        if not message_text:
            message_text = "No message provided"

        result = self.send_message(message_text)
        return dspy.Prediction(
            response=result.get("response", ""),
            capabilities=self.get_capabilities(),
            agent_card=json.dumps(self.agent_card, sort_keys=True),
        )
