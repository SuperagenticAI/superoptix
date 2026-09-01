"""A2A v1 server bridge for exposing SuperOptiX pipelines."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import uuid
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import suppress
from datetime import datetime, timezone
from email.utils import format_datetime
from typing import Any, Dict

from superoptix.protocols.a2a import bridge as a2a_bridge
from superoptix.protocols.a2a import errors as a2a_errors
from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.mappers import (
    extract_text_from_message,
    normalize_a2a_payload,
    runtime_result_to_text,
)
from superoptix.runtime.base import AgentRuntime, RuntimeContext
from superoptix.runtime.registry import runtime_registry

logger = logging.getLogger(__name__)

try:
    from fastapi import Body, FastAPI, HTTPException, Request
    from fastapi.responses import (
        HTMLResponse,
        JSONResponse,
        Response,
        StreamingResponse,
    )

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in live use
    FASTAPI_AVAILABLE = False
    FastAPI = None
    HTTPException = Exception
    Request = object
    HTMLResponse = None
    JSONResponse = None
    Response = None
    StreamingResponse = None


class A2AProtocolError(Exception):
    """A request that the A2A spec requires the server to reject.

    Carries the binding so each transport can render it with the right code.
    """

    def __init__(self, error: "a2a_errors.A2AError", message: str):
        super().__init__(message)
        self.error = error


class TaskNotCancelable(A2AProtocolError):
    """CancelTask targeted a task already in a terminal state."""

    def __init__(self, task_id: str):
        super().__init__(
            a2a_errors.TASK_NOT_CANCELABLE, f"Task {task_id} is already terminal"
        )
        self.task_id = task_id


def _iso8601_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _agent_message(
    text: str,
    *,
    task_id: str | None = None,
    context_id: str | None = None,
) -> Dict[str, Any]:
    return {
        "messageId": str(uuid.uuid4()),
        "taskId": task_id,
        "contextId": context_id,
        "role": "ROLE_AGENT",
        "parts": [{"text": text}],
    }


def _user_message(message: Dict[str, Any]) -> Dict[str, Any]:
    payload = normalize_a2a_payload(message)
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("messageId", str(uuid.uuid4()))
    payload.setdefault("role", "ROLE_USER")
    payload.setdefault("parts", [])
    return payload


def _task_status(
    state: str,
    *,
    message_text: str | None = None,
    task_id: str,
    context_id: str,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "state": state,
        "timestamp": _iso8601_now(),
    }
    if message_text:
        payload["message"] = _agent_message(
            message_text,
            task_id=task_id,
            context_id=context_id,
        )
    return payload


# States a runtime may ask for instead of the default completion. Anything else
# is ignored so a runtime cannot invent protocol states.
_RUNTIME_SELECTABLE_STATES = {
    "TASK_STATE_COMPLETED",
    "TASK_STATE_INPUT_REQUIRED",
    "TASK_STATE_FAILED",
    "TASK_STATE_REJECTED",
    "TASK_STATE_AUTH_REQUIRED",
}


def _int_or_none(value: Any) -> int | None:
    """Coerce a query/param value to int, ignoring anything unparseable."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _declared_state(result: Any) -> str:
    """Task state requested by the runtime, defaulting to completion."""
    if isinstance(result, dict):
        state = str(result.get("a2a_state") or "")
        if state in _RUNTIME_SELECTABLE_STATES:
            return state
    return "TASK_STATE_COMPLETED"


def _terminal_state(state: str | None) -> bool:
    return state in {
        "TASK_STATE_COMPLETED",
        "TASK_STATE_FAILED",
        "TASK_STATE_CANCELED",
        "TASK_STATE_REJECTED",
    }


class _A2ATaskStore:
    """Small in-memory task manager for the SuperOptiX A2A bridge."""

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running: Dict[str, asyncio.Task] = {}
        self.subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
        # Timestamps kept beside the task rather than on it: the A2A Task
        # schema is closed (additionalProperties: false).
        self.created_at: Dict[str, str] = {}
        # Populated when a runtime answers with a bare Message instead of a Task.
        self.message_replies: Dict[str, Dict[str, Any]] = {}
        self.last_modified: Dict[str, str] = {}
        self.lock = asyncio.Lock()

    async def _publish(self, task_id: str, event: Dict[str, Any]) -> None:
        queues = list(self.subscribers.get(task_id, set()))
        for queue in queues:
            await queue.put(event)

    async def _set_task(self, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        # No bookkeeping fields on the Task itself: the A2A 1.0 Task schema
        # declares additionalProperties: false, so anything beyond the six
        # spec'd fields fails conformance validation. Timestamps live on
        # status.timestamp, which the spec does define.
        self.last_modified[task_id] = _iso8601_now()
        async with self.lock:
            self.tasks[task_id] = task
        return task

    async def get(
        self, task_id: str, *, history_length: int | None = None
    ) -> Dict[str, Any] | None:
        async with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            task = dict(task)
        return _apply_history_length(task, history_length)

    async def list(
        self,
        *,
        context_id: str | None = None,
        status: str | None = None,
        page_size: int | None = None,
    ) -> Dict[str, Any]:
        async with self.lock:
            tasks = [dict(task) for task in self.tasks.values()]
        if context_id:
            tasks = [task for task in tasks if task.get("contextId") == context_id]
        if status:
            tasks = [
                task
                for task in tasks
                if (task.get("status") or {}).get("state") == status
            ]
        total_size = len(tasks)
        size = page_size or total_size
        return {
            "tasks": tasks[:size],
            "nextPageToken": "",
            "pageSize": min(size, total_size) if total_size else 0,
            "totalSize": total_size,
        }

    async def _runtime_context(
        self,
        *,
        task_id: str,
        context_id: str,
        request: Any | None,
        message: Dict[str, Any],
    ) -> RuntimeContext:
        return RuntimeContext(
            task_id=task_id,
            context_id=context_id,
            protocol="a2a",
            metadata={
                "message_id": message.get("messageId"),
                "role": message.get("role"),
            },
            request=request,
        )

    async def _update_status(
        self,
        task: Dict[str, Any],
        *,
        state: str,
        message_text: str | None = None,
        publish: bool = False,
    ) -> Dict[str, Any]:
        task["status"] = _task_status(
            state,
            message_text=message_text,
            task_id=task["id"],
            context_id=task["contextId"],
        )
        await self._set_task(task["id"], task)
        # `publish` controls the streaming caller's own SSE feed. Anyone
        # subscribed through SubscribeToTask must see the transition either
        # way, or their stream never observes the task finish and hangs open.
        if publish or self.subscribers.get(task["id"]):
            await self._publish(
                task["id"],
                {
                    "statusUpdate": {
                        "taskId": task["id"],
                        "contextId": task["contextId"],
                        "status": dict(task["status"]),
                    }
                },
            )
        return task

    async def _finalize_task(
        self,
        task: Dict[str, Any],
        *,
        state: str,
        response_text: str,
        publish: bool,
        artifacts: list[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        response_message = _agent_message(
            response_text,
            task_id=task["id"],
            context_id=task["contextId"],
        )
        history = list(task.get("history") or [])
        history.append(response_message)
        task["history"] = history
        if artifacts:
            task["artifacts"] = list(artifacts)
        task["status"] = {
            "state": state,
            "timestamp": _iso8601_now(),
            "message": response_message,
        }
        await self._set_task(task["id"], task)
        # `publish` controls the streaming caller's own SSE feed. Anyone
        # subscribed through SubscribeToTask must see the transition either
        # way, or their stream never observes the task finish and hangs open.
        if publish or self.subscribers.get(task["id"]):
            await self._publish(
                task["id"],
                {
                    "statusUpdate": {
                        "taskId": task["id"],
                        "contextId": task["contextId"],
                        "status": dict(task["status"]),
                    }
                },
            )
        return task

    async def _create_task(
        self,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Start a task, or continue the one the message references.

        A message carrying a taskId is a follow-up turn: it must extend that
        task's history rather than replacing it with a fresh task, or anything
        subscribed to the original never observes it finish.
        """
        existing_id = message.get("taskId")
        if existing_id:
            existing = await self.get(str(existing_id))
            if existing:
                history = list(existing.get("history") or [])
                history.append(message)
                existing["history"] = history
                await self._set_task(str(existing_id), existing)
                return existing

        task_id = str(message.get("taskId") or uuid.uuid4())
        context_id = str(message.get("contextId") or uuid.uuid4())
        created_at = _iso8601_now()
        task = {
            "id": task_id,
            "contextId": context_id,
            "status": _task_status(
                "TASK_STATE_SUBMITTED",
                task_id=task_id,
                context_id=context_id,
            ),
            "artifacts": [],
            "history": [message],
            "metadata": {},
        }
        self.created_at[task_id] = created_at
        await self._set_task(task_id, task)
        return task

    async def _execute_task(
        self,
        task: Dict[str, Any],
        *,
        user_input: str,
        request: Any | None,
        publish: bool,
    ) -> Dict[str, Any]:
        task_id = str(task["id"])
        context_id = str(task["contextId"])
        runtime_context = await self._runtime_context(
            task_id=task_id,
            context_id=context_id,
            request=request,
            # The current turn, not the first: on a follow-up the runtime must
            # see the message it is actually answering.
            message=(task.get("history") or [{}])[-1],
        )
        await self._update_status(
            task,
            state="TASK_STATE_WORKING",
            message_text="Processing request",
            publish=publish,
        )
        try:
            result = await self.runtime.invoke(
                {"query": user_input},
                context=runtime_context,
            )
            current = await self.get(task_id) or task
            if isinstance(result, dict) and result.get("a2a_message_only"):
                # The runtime answered directly; no Task envelope is produced.
                self.message_replies[task_id] = _agent_message(
                    runtime_result_to_text(result),
                    task_id=task_id,
                    context_id=context_id,
                )
            if _terminal_state(str((current.get("status") or {}).get("state"))):
                return current
            return await self._finalize_task(
                current,
                state=_declared_state(result),
                response_text=runtime_result_to_text(result),
                publish=publish,
                artifacts=result.get("a2a_artifacts")
                if isinstance(result, dict)
                else None,
            )
        except asyncio.CancelledError:  # pragma: no cover - async cancellation timing
            current = await self.get(task_id) or task
            if not _terminal_state(str((current.get("status") or {}).get("state"))):
                await self._update_status(
                    current,
                    state="TASK_STATE_CANCELED",
                    message_text="Task canceled",
                    publish=publish,
                )
            raise
        except Exception as exc:
            logger.exception("A2A runtime execution failed")
            current = await self.get(task_id) or task
            return await self._finalize_task(
                current,
                state="TASK_STATE_FAILED",
                response_text=str(exc),
                publish=publish,
            )
        finally:
            self.running.pop(task_id, None)

    async def _validate_message_references(self, message: Dict[str, Any]) -> None:
        """Reject a message whose taskId/contextId cannot be honoured.

        The spec requires TaskNotFoundError for an unknown task, and rejection
        of a follow-up aimed at a terminal task or carrying a contextId that
        disagrees with the task's own.
        """
        if not (message.get("parts") or message.get("content")):
            raise A2AProtocolError(
                a2a_errors.INVALID_PARAMS,
                "message.parts is required and must not be empty",
            )

        task_id = message.get("taskId")
        if not task_id:
            return

        task = await self.get(str(task_id))
        if not task:
            raise A2AProtocolError(
                a2a_errors.TASK_NOT_FOUND, f"Task {task_id} not found"
            )

        context_id = message.get("contextId")
        if context_id and str(context_id) != str(task.get("contextId")):
            raise A2AProtocolError(
                a2a_errors.INVALID_PARAMS,
                f"contextId does not match task {task_id}",
            )

        state = str((task.get("status") or {}).get("state"))
        if _terminal_state(state):
            raise A2AProtocolError(
                a2a_errors.UNSUPPORTED_OPERATION,
                f"Task {task_id} is terminal and cannot accept further messages",
            )

    async def send_message(
        self,
        *,
        message: Dict[str, Any],
        configuration: Dict[str, Any] | None = None,
        request: Any | None = None,
    ) -> Dict[str, Any]:
        """Run one turn.

        Returns a Task, or a bare Message when the runtime asks for one via
        ``a2a_message_only`` — the spec allows either as a SendMessage result.
        """
        user_message = _user_message(message)
        await self._validate_message_references(user_message)
        task = await self._create_task(user_message)
        user_input = extract_text_from_message(user_message)
        config = configuration or {}
        history_length = _int_or_none(config.get("historyLength"))
        if bool(config.get("returnImmediately")):
            worker = asyncio.create_task(
                self._execute_task(
                    task,
                    user_input=user_input,
                    request=request,
                    publish=True,
                )
            )
            self.running[task["id"]] = worker
            await self._update_status(
                task,
                state="TASK_STATE_WORKING",
                message_text="Processing request",
                publish=True,
            )
            return await self.get(task["id"], history_length=history_length) or task

        finished = await self._execute_task(
            task,
            user_input=user_input,
            request=request,
            publish=False,
        )
        message_reply = self.message_replies.pop(task["id"], None)
        if message_reply is not None:
            return {"__a2a_message__": message_reply}
        return _apply_history_length(dict(finished), history_length)

    async def stream_message(
        self,
        *,
        message: Dict[str, Any],
        request: Any | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        user_message = _user_message(message)
        task = await self._create_task(user_message)
        task_id = str(task["id"])
        context_id = str(task["contextId"])
        user_input = extract_text_from_message(user_message)
        runtime_context = await self._runtime_context(
            task_id=task_id,
            context_id=context_id,
            request=request,
            message=user_message,
        )
        await self._update_status(
            task,
            state="TASK_STATE_WORKING",
            message_text="Processing request",
            publish=False,
        )
        yield {"task": await self.get(task_id) or task}

        try:
            capabilities = await self.runtime.capabilities()
            if capabilities.get("streaming"):
                last_text = ""
                async for chunk in self.runtime.stream(
                    {"query": user_input},
                    context=runtime_context,
                ):
                    last_text = runtime_result_to_text(chunk)
                    yield {
                        "statusUpdate": {
                            "taskId": task_id,
                            "contextId": context_id,
                            "status": _task_status(
                                "TASK_STATE_WORKING",
                                message_text=last_text,
                                task_id=task_id,
                                context_id=context_id,
                            ),
                        }
                    }
                final_text = last_text or "Completed"
            else:
                result = await self.runtime.invoke(
                    {"query": user_input},
                    context=runtime_context,
                )
                final_text = runtime_result_to_text(result)

            current = await self.get(task_id) or task
            current = await self._finalize_task(
                current,
                state="TASK_STATE_COMPLETED",
                response_text=final_text,
                publish=False,
            )
            yield {
                "statusUpdate": {
                    "taskId": task_id,
                    "contextId": context_id,
                    "status": dict(current["status"]),
                }
            }
        except Exception as exc:
            logger.exception("A2A runtime stream failed")
            current = await self.get(task_id) or task
            current = await self._finalize_task(
                current,
                state="TASK_STATE_FAILED",
                response_text=str(exc),
                publish=False,
            )
            yield {
                "statusUpdate": {
                    "taskId": task_id,
                    "contextId": context_id,
                    "status": dict(current["status"]),
                }
            }

    async def cancel(
        self, task_id: str, *, request: Any | None = None
    ) -> Dict[str, Any]:
        task = await self.get(task_id)
        if not task:
            raise KeyError(task_id)
        state = str((task.get("status") or {}).get("state"))
        if _terminal_state(state):
            # The spec requires TaskNotCancelableError rather than a silent
            # success when the task has already reached a terminal state.
            raise TaskNotCancelable(task_id)

        runtime_context = RuntimeContext(
            task_id=task_id,
            context_id=task.get("contextId"),
            protocol="a2a",
            request=request,
        )
        with suppress(Exception):
            await self.runtime.cancel(task_id, context=runtime_context)

        worker = self.running.get(task_id)
        if worker:
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker

        return await self._update_status(
            task,
            state="TASK_STATE_CANCELED",
            message_text="Task canceled",
            publish=True,
        )

    async def subscribe(self, task_id: str) -> AsyncIterator[Dict[str, Any]]:
        current = await self.get(task_id)
        if not current:
            raise KeyError(task_id)
        state = str((current.get("status") or {}).get("state"))
        if _terminal_state(state):
            raise ValueError(f"Task {task_id} is already terminal")

        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers[task_id].add(queue)
        try:
            yield {"task": current}
            while True:
                event = await queue.get()
                yield event
                payload = event.get("task") or {}
                if not payload and isinstance(event.get("statusUpdate"), dict):
                    payload = {"status": event["statusUpdate"].get("status") or {}}
                if _terminal_state(str((payload.get("status") or {}).get("state"))):
                    return
        finally:
            self.subscribers[task_id].discard(queue)


def _jsonrpc_error(
    request_id: Any,
    error: a2a_errors.A2AError,
    message: str,
    *,
    metadata: Dict[str, str] | None = None,
) -> JSONResponse:
    """JSON-RPC error, returned with HTTP 200.

    The transport succeeded; the failure is inside the envelope. Returning 4xx
    makes conformant clients treat it as a transport error and never read the
    code, which is what the A2A TCK observed.
    """
    return JSONResponse(
        status_code=200,
        content=a2a_errors.jsonrpc_error_body(
            request_id, error, message, metadata=metadata
        ),
    )


def _http_error(
    error: a2a_errors.A2AError,
    message: str,
    *,
    metadata: Dict[str, str] | None = None,
) -> JSONResponse:
    """AIP-193 error response for the HTTP+JSON binding."""
    return JSONResponse(
        status_code=error.http_status,
        content=a2a_errors.http_error_body(error, message, metadata=metadata),
    )


# Clients declare the spec line they speak via this header; we serve 1.0 and 0.3.

def _apply_history_length(
    task: Dict[str, Any], history_length: int | None
) -> Dict[str, Any]:
    """Cap a task's history, keeping the most recent messages.

    Zero is a meaningful value here and asks for no history at all, so the
    check is against None rather than truthiness.
    """
    if history_length is None or history_length < 0:
        return task
    history = list(task.get("history") or [])
    task["history"] = history[-history_length:] if history_length else []
    return task


def _etag_matches(header: str | None, etag: str) -> bool:
    """True when an If-None-Match header covers this entity tag.

    RFC 9110 allows a comma separated list and the wildcard, and a weak
    validator compares equal to its strong form for this purpose.
    """
    if not header:
        return False
    candidates = [c.strip() for c in header.split(",")]
    if "*" in candidates:
        return True
    target = etag.removeprefix("W/")
    return any(c.removeprefix("W/") == target for c in candidates)

SUPPORTED_PROTOCOL_VERSIONS = {"1.0", "0.3"}

# The 0.3 spec line names its JSON-RPC methods with slashes; 1.0 renamed them to
# the RPC style. The card advertises a 0.3 JSON-RPC interface, so a 0.3 client
# calling the older names has to reach the same handlers.
LEGACY_JSONRPC_METHODS = {
    "message/send": "SendMessage",
    "message/stream": "SendStreamingMessage",
    "tasks/get": "GetTask",
    "tasks/list": "ListTasks",
    "tasks/cancel": "CancelTask",
    "tasks/resubscribe": "SubscribeToTask",
    "agent/authenticatedExtendedCard": "GetExtendedAgentCard",
    "agent/getAuthenticatedExtendedCard": "GetExtendedAgentCard",
    "tasks/pushNotificationConfig/set": "CreateTaskPushNotificationConfig",
    "tasks/pushNotificationConfig/get": "GetTaskPushNotificationConfig",
    "tasks/pushNotificationConfig/list": "ListTaskPushNotificationConfigs",
    "tasks/pushNotificationConfig/delete": "DeleteTaskPushNotificationConfig",
}


def _unsupported_version(request: Any) -> str | None:
    """Return the requested A2A version when we cannot serve it."""
    try:
        requested = (request.headers.get("A2A-Version") or "").strip()
    except AttributeError:
        return None
    if not requested:
        return None
    # Accept any spelling that reduces to a line we serve: a client asking for
    # "0.3.0" wants the same wire shape as one asking for "0.3".
    if a2a_bridge.normalize_version(requested) in SUPPORTED_PROTOCOL_VERSIONS:
        return None
    if requested in SUPPORTED_PROTOCOL_VERSIONS:
        return None
    return requested


def _maybe_legacy(request: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Render a response in the 0.3 wire shape when the caller asked for it."""
    if not _wants_legacy(request):
        return payload
    if isinstance(payload, dict) and "task" in payload:
        return {**payload, "task": a2a_bridge.task_to_v03(payload["task"])}
    return a2a_bridge.task_to_v03(payload)


def _wants_legacy(request: Any) -> bool:
    """Whether this caller asked for the pre-1.0 wire shape."""
    try:
        return a2a_bridge.requested_version(request.headers) == a2a_bridge.V03
    except AttributeError:
        return False


def _sse_stream(
    iterator: AsyncIterator[Dict[str, Any]],
    *,
    request_id: Any | None = None,
) -> StreamingResponse:
    async def _event_stream() -> AsyncIterator[str]:
        async for payload in iterator:
            envelope = normalize_a2a_payload(payload)
            if request_id is not None:
                envelope = {"jsonrpc": "2.0", "id": request_id, "result": envelope}
            yield f"data: {json.dumps(envelope, ensure_ascii=True)}\n\n"

    return StreamingResponse(_event_stream(), media_type="text/event-stream")


def create_a2a_fastapi_app(
    *,
    pipeline: Any,
    agent_url: str,
    rpc_url: str = "/a2a/jsonrpc",
    runtime_adapter: str = "compiled_pipeline",
    agent_card: Dict[str, Any] | None = None,
) -> Any:
    """Create an A2A v1 FastAPI app exposing a compiled SuperOptiX pipeline.

    Args:
        agent_card: serve this card verbatim instead of deriving one from the
            runtime's metadata. Used by the published public endpoint, which
            advertises hand-written skills rather than SuperSpec tasks.
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "A2A server dependencies are not installed. Install superoptix[a2a]."
        )

    runtime = runtime_registry.create(runtime_adapter, pipeline)
    if agent_card is None:
        metadata = asyncio.run(runtime.metadata())
        agent_card = build_a2a_agent_card_payload(
            metadata=metadata.get("metadata", {}),
            spec=metadata.get("spec", {}),
            agent_url=agent_url,
            rpc_url=rpc_url,
        )
    tasks = _A2ATaskStore(runtime)
    app = FastAPI(title="SuperOptiX A2A", version="1.0")

    @app.middleware("http")
    async def _a2a_protocol_middleware(request: Any, call_next: Any) -> Any:
        """Enforce the two request-level contracts the spec puts before routing.

        FastAPI would otherwise answer an unsupported media type with its own
        422 validation error, and would ignore version negotiation entirely.
        """
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = (request.headers.get("content-type") or "").split(";")[0]
            content_type = content_type.strip().lower()
            if content_type and content_type != "application/json":
                message = (
                    f"Content type '{content_type}' is not supported; "
                    "use application/json"
                )
                if request.url.path.rstrip("/") == rpc_url.rstrip("/"):
                    # JSON-RPC reports this in its envelope, not as an HTTP status.
                    return _jsonrpc_error(
                        None,
                        a2a_errors.CONTENT_TYPE_NOT_SUPPORTED,
                        message,
                        metadata={"received": content_type},
                    )
                return _http_error(
                    a2a_errors.CONTENT_TYPE_NOT_SUPPORTED,
                    message,
                    metadata={"received": content_type},
                )

        requested_version = _unsupported_version(request)
        if requested_version and not request.url.path.endswith(rpc_url):
            # The JSON-RPC binding reports this inside its own envelope.
            return _http_error(
                a2a_errors.VERSION_NOT_SUPPORTED,
                f"A2A version {requested_version} is not supported",
                metadata={
                    "requested": requested_version,
                    "supported": ", ".join(sorted(SUPPORTED_PROTOCOL_VERSIONS)),
                },
            )

        return await call_next(request)

    @app.get("/", include_in_schema=False)
    async def index() -> Any:
        """Explain the endpoint to a person who opened it in a browser.

        This address appears in the Agent Card, in registries and in anything
        published about the agent, so people will click it. A bare 404 reads as
        a broken service. The JSON-RPC binding lives at the RPC path, so the
        root is free to answer.
        """
        name = str(agent_card.get("name") or "SuperOptiX Agent")
        description = str(agent_card.get("description") or "")
        skills = agent_card.get("skills") or []
        bindings = sorted(
            {
                str(i.get("protocolBinding"))
                for i in agent_card.get("supportedInterfaces") or []
                if i.get("protocolBinding")
            }
        )
        versions = sorted(
            {
                str(i.get("protocolVersion"))
                for i in agent_card.get("supportedInterfaces") or []
                if i.get("protocolVersion")
            }
        )
        skill_rows = "".join(
            f"<tr><td><code>{s.get('id')}</code></td><td>{s.get('description', '')}</td></tr>"
            for s in skills
            if isinstance(s, dict)
        )
        html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — A2A interface</title>
<style>
 body{{font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
   max-width:44rem;margin:3rem auto;padding:0 1.5rem;color:#12161c;background:#fbfcfd}}
 h1{{font-size:1.5rem;margin:0 0 .25rem}}
 p.lede{{color:#566470;margin:0 0 2rem}}
 table{{border-collapse:collapse;width:100%;margin:.5rem 0 2rem;font-size:.94rem}}
 td,th{{text-align:left;padding:.45rem .6rem;border-bottom:1px solid #e5ebf0;vertical-align:top}}
 th{{color:#566470;font-weight:600;width:11rem}}
 code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em;
   background:#eef2f6;border-radius:3px;padding:.1em .35em}}
 a{{color:#16607c}}
 @media (prefers-color-scheme:dark){{
   body{{background:#0e1317;color:#e8eef3}} p.lede,th{{color:#8c9ba7}}
   td,th{{border-color:#27333c}} code{{background:#1d262e}} a{{color:#6fbdda}}}}
</style></head><body>
<h1>{name}</h1>
<p class="lede">This is an Agent-to-Agent (A2A) interface. Other agents call it.
If you were looking for the project, see the documentation link below.</p>
<table>
<tr><th>Agent Card</th><td><a href="/.well-known/agent-card.json">/.well-known/agent-card.json</a></td></tr>
<tr><th>Protocol versions</th><td>{", ".join(versions) or "1.0"}</td></tr>
<tr><th>Bindings</th><td>{", ".join(bindings) or "JSONRPC"}</td></tr>
<tr><th>JSON-RPC endpoint</th><td><code>{rpc_url}</code></td></tr>
<tr><th>Description</th><td>{description}</td></tr>
</table>
<h2 style="font-size:1.05rem">Skills</h2>
<table>{skill_rows or "<tr><td>None declared</td></tr>"}</table>
<p style="color:#566470;font-size:.9rem">The first request after a quiet period
may take a moment while the service starts.</p>
<p><a href="https://superagenticai.github.io/superoptix/guides/a2a-adapt/">Documentation</a>
 · <a href="https://github.com/SuperagenticAI/superoptix">Source</a></p>
</body></html>"""
        return HTMLResponse(content=html)

    # The card is fixed for the life of the process, so its validators are too.
    # A2A asks servers to make the card cacheable, and a conditional request that
    # matches should cost the caller nothing.
    _card_served_at = format_datetime(datetime.now(timezone.utc), usegmt=True)

    def _card_etag(payload: Dict[str, Any]) -> str:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return '"' + hashlib.sha256(body.encode("utf-8")).hexdigest()[:32] + '"'

    _card_etags = {
        "1.0": _card_etag(agent_card),
        "0.3": _card_etag(a2a_bridge.card_to_v03(agent_card)),
    }

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card(request: Request) -> Any:
        # A 0.3 reader expects a top-level `url` and its own protocolVersion;
        # handed only `supportedInterfaces` it has nothing to call.
        legacy = _wants_legacy(request)
        payload = a2a_bridge.card_to_v03(agent_card) if legacy else agent_card
        etag = _card_etags["0.3" if legacy else "1.0"]
        headers = {
            "Cache-Control": "public, max-age=3600",
            "ETag": etag,
            "Last-Modified": _card_served_at,
            "Vary": "A2A-Version",
        }
        if _etag_matches(request.headers.get("if-none-match"), etag):
            return Response(status_code=304, headers=headers)
        return JSONResponse(content=payload, headers=headers)

    @app.get("/extendedAgentCard")
    async def get_extended_agent_card() -> Any:
        return _http_error(
            a2a_errors.EXTENDED_AGENT_CARD_NOT_CONFIGURED,
            "Extended agent card is not configured",
        )

    @app.post("/message:send")
    async def send_message(request: Request, payload: Dict[str, Any] = Body()) -> Any:
        try:
            result = await _http_send_message(request, payload)
        except A2AProtocolError as exc:
            return _http_error(exc.error, str(exc))
        return _maybe_legacy(request, result)

    async def _http_send_message(
        request: Request, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        task = await tasks.send_message(
            message=payload.get("message") or {},
            configuration=payload.get("configuration") or {},
            request=request,
        )
        if "__a2a_message__" in task:
            return {"message": task["__a2a_message__"]}
        return {"task": task}

    @app.post("/message:stream")
    async def stream_message(
        request: Request, payload: Dict[str, Any] = Body()
    ) -> StreamingResponse:
        iterator = tasks.stream_message(
            message=payload.get("message") or {},
            request=request,
        )
        return _sse_stream(iterator)

    @app.get("/tasks")
    async def list_tasks(
        contextId: str | None = None,
        status: str | None = None,
        pageSize: int | None = None,
    ) -> Dict[str, Any]:
        return await tasks.list(context_id=contextId, status=status, page_size=pageSize)

    @app.get("/tasks/{task_id}")
    async def get_task(
        request: Request,
        task_id: str,
        historyLength: int | None = None,  # noqa: N803
    ) -> Any:
        task = await tasks.get(task_id, history_length=historyLength)
        if not task:
            return _http_error(a2a_errors.TASK_NOT_FOUND, "Task not found")
        return _maybe_legacy(request, task)

    @app.post("/tasks/{task_id}:cancel")
    async def cancel_task(task_id: str, request: Request) -> Any:
        try:
            return await tasks.cancel(task_id, request=request)
        except KeyError:
            return _http_error(a2a_errors.TASK_NOT_FOUND, "Task not found")
        except A2AProtocolError as exc:
            return _http_error(exc.error, str(exc))

    @app.post("/tasks/{task_id}:subscribe")
    async def subscribe_task(task_id: str) -> Any:
        current = await tasks.get(task_id)
        if not current:
            return _http_error(a2a_errors.TASK_NOT_FOUND, "Task not found")
        state = str((current.get("status") or {}).get("state"))
        if _terminal_state(state):
            return _http_error(
                a2a_errors.TASK_NOT_CANCELABLE,
                f"Task {task_id} is already terminal",
            )
        return _sse_stream(tasks.subscribe(task_id))

    # Both spellings are served. A client given the interface URL as an httpx
    # base_url and posting to "/" resolves to "<rpc_url>/", and Starlette's
    # default redirect for the missing trailing slash returns an empty 307 body
    # that JSON-RPC clients cannot parse.
    # Declared so callers get the spec'd PushNotificationNotSupportedError
    # rather than a 404, which reads as "wrong URL" instead of "not offered".
    @app.post("/tasks/{task_id}/pushNotificationConfigs")
    @app.get("/tasks/{task_id}/pushNotificationConfigs")
    @app.get("/tasks/{task_id}/pushNotificationConfigs/{config_id}")
    @app.delete("/tasks/{task_id}/pushNotificationConfigs/{config_id}")
    async def push_notification_configs(task_id: str, config_id: str = "") -> Any:
        return _http_error(
            a2a_errors.PUSH_NOTIFICATION_NOT_SUPPORTED,
            "Push notifications are not supported by this agent",
        )

    @app.post(rpc_url)
    @app.post(rpc_url.rstrip("/") + "/")
    async def jsonrpc(request: Request, payload: Dict[str, Any] = Body()) -> Any:
        request_id = payload.get("id") if isinstance(payload, dict) else None

        requested_version = _unsupported_version(request)
        if requested_version:
            return _jsonrpc_error(
                request_id,
                a2a_errors.VERSION_NOT_SUPPORTED,
                f"A2A version {requested_version} is not supported",
                metadata={
                    "requested": requested_version,
                    "supported": ", ".join(sorted(SUPPORTED_PROTOCOL_VERSIONS)),
                },
            )

        method = str(payload.get("method") or "") if isinstance(payload, dict) else ""
        if not isinstance(payload, dict) or not method:
            return _jsonrpc_error(
                request_id,
                a2a_errors.INVALID_REQUEST,
                "Request must be a JSON-RPC 2.0 object with a 'method' member",
            )

        method = LEGACY_JSONRPC_METHODS.get(method, method)

        params = normalize_a2a_payload(payload.get("params") or {})

        if method == "SendMessage":
            try:
                task = await tasks.send_message(
                    message=params.get("message") or {},
                    configuration=params.get("configuration") or {},
                    request=request,
                )
            except A2AProtocolError as exc:
                return _jsonrpc_error(request_id, exc.error, str(exc))
            if "__a2a_message__" in task:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"message": task["__a2a_message__"]},
                }
            return {"jsonrpc": "2.0", "id": request_id, "result": {"task": task}}

        if method == "SendStreamingMessage":
            iterator = tasks.stream_message(
                message=params.get("message") or {},
                request=request,
            )
            return _sse_stream(iterator, request_id=request_id)

        if method == "GetTask":
            task_id = params.get("id")
            task = await tasks.get(
                str(task_id), history_length=_int_or_none(params.get("historyLength"))
            )
            if not task:
                return _jsonrpc_error(
                    request_id, a2a_errors.TASK_NOT_FOUND, "Task not found"
                )
            return {"jsonrpc": "2.0", "id": request_id, "result": task}

        if method == "ListTasks":
            result = await tasks.list(
                context_id=params.get("contextId"),
                status=params.get("status"),
                page_size=params.get("pageSize"),
            )
            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        if method == "CancelTask":
            task_id = params.get("id")
            try:
                task = await tasks.cancel(str(task_id), request=request)
            except KeyError:
                return _jsonrpc_error(
                    request_id, a2a_errors.TASK_NOT_FOUND, "Task not found"
                )
            except A2AProtocolError as exc:
                return _jsonrpc_error(request_id, exc.error, str(exc))
            return {"jsonrpc": "2.0", "id": request_id, "result": task}

        if method == "SubscribeToTask":
            task_id = str(params.get("id") or "")
            current = await tasks.get(task_id)
            if not current:
                return _jsonrpc_error(
                    request_id, a2a_errors.TASK_NOT_FOUND, "Task not found"
                )
            state = str((current.get("status") or {}).get("state"))
            if _terminal_state(state):
                return _jsonrpc_error(
                    request_id,
                    a2a_errors.TASK_NOT_CANCELABLE,
                    f"Task {task_id} is already terminal",
                )
            return _sse_stream(tasks.subscribe(task_id), request_id=request_id)

        if method in (
            "CreateTaskPushNotificationConfig",
            "GetTaskPushNotificationConfig",
            "ListTaskPushNotificationConfigs",
            "DeleteTaskPushNotificationConfig",
            "SetTaskPushNotificationConfig",
        ):
            return _jsonrpc_error(
                request_id,
                a2a_errors.PUSH_NOTIFICATION_NOT_SUPPORTED,
                "Push notifications are not supported by this agent",
            )

        if method == "GetExtendedAgentCard":
            return _jsonrpc_error(
                request_id,
                a2a_errors.EXTENDED_AGENT_CARD_NOT_CONFIGURED,
                "Extended agent card is not configured",
            )

        return _jsonrpc_error(
            request_id, a2a_errors.METHOD_NOT_FOUND, f"Method not found: {method}"
        )

    return app
