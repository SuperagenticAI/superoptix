"""A2A v1 server bridge for exposing SuperOptiX pipelines."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

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
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse, StreamingResponse

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in live use
    FASTAPI_AVAILABLE = False
    FastAPI = None
    HTTPException = Exception
    Request = object
    JSONResponse = None
    StreamingResponse = None


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
        self.lock = asyncio.Lock()

    async def _publish(self, task_id: str, event: Dict[str, Any]) -> None:
        queues = list(self.subscribers.get(task_id, set()))
        for queue in queues:
            await queue.put(event)

    async def _set_task(self, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        task["lastModified"] = _iso8601_now()
        async with self.lock:
            self.tasks[task_id] = task
        return task

    async def get(self, task_id: str) -> Dict[str, Any] | None:
        async with self.lock:
            task = self.tasks.get(task_id)
            return dict(task) if task else None

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
        if publish:
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
    ) -> Dict[str, Any]:
        response_message = _agent_message(
            response_text,
            task_id=task["id"],
            context_id=task["contextId"],
        )
        history = list(task.get("history") or [])
        history.append(response_message)
        task["history"] = history
        task["status"] = {
            "state": state,
            "timestamp": _iso8601_now(),
            "message": response_message,
        }
        await self._set_task(task["id"], task)
        if publish:
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
            "createdAt": created_at,
            "lastModified": created_at,
        }
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
            message=task["history"][0],
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
            if _terminal_state(str((current.get("status") or {}).get("state"))):
                return current
            return await self._finalize_task(
                current,
                state="TASK_STATE_COMPLETED",
                response_text=runtime_result_to_text(result),
                publish=publish,
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

    async def send_message(
        self,
        *,
        message: Dict[str, Any],
        configuration: Dict[str, Any] | None = None,
        request: Any | None = None,
    ) -> Dict[str, Any]:
        user_message = _user_message(message)
        task = await self._create_task(user_message)
        user_input = extract_text_from_message(user_message)
        config = configuration or {}
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
            return await self.get(task["id"]) or task

        return await self._execute_task(
            task,
            user_input=user_input,
            request=request,
            publish=False,
        )

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
            return task

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


def _jsonrpc_error(request_id: Any, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        },
    )


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
) -> Any:
    """Create an A2A v1 FastAPI app exposing a compiled SuperOptiX pipeline."""
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "A2A server dependencies are not installed. Install superoptix[a2a]."
        )

    runtime = runtime_registry.create(runtime_adapter, pipeline)
    metadata = asyncio.run(runtime.metadata())
    agent_card = build_a2a_agent_card_payload(
        metadata=metadata.get("metadata", {}),
        spec=metadata.get("spec", {}),
        agent_url=agent_url,
        rpc_url=rpc_url,
    )
    tasks = _A2ATaskStore(runtime)
    app = FastAPI(title="SuperOptiX A2A", version="1.0")

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> Dict[str, Any]:
        return agent_card

    @app.get("/extendedAgentCard")
    async def get_extended_agent_card() -> JSONResponse:
        raise HTTPException(status_code=400, detail="Extended agent card not supported")

    @app.post("/message:send")
    async def send_message(payload: Dict[str, Any], request: Request) -> Dict[str, Any]:
        task = await tasks.send_message(
            message=payload.get("message") or {},
            configuration=payload.get("configuration") or {},
            request=request,
        )
        return {"task": task}

    @app.post("/message:stream")
    async def stream_message(
        payload: Dict[str, Any], request: Request
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
    async def get_task(task_id: str) -> Dict[str, Any]:
        task = await tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @app.post("/tasks/{task_id}:cancel")
    async def cancel_task(task_id: str, request: Request) -> Dict[str, Any]:
        try:
            return await tasks.cancel(task_id, request=request)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Task not found") from exc

    @app.post("/tasks/{task_id}:subscribe")
    async def subscribe_task(task_id: str) -> StreamingResponse:
        current = await tasks.get(task_id)
        if not current:
            raise HTTPException(status_code=404, detail="Task not found")
        state = str((current.get("status") or {}).get("state"))
        if _terminal_state(state):
            raise HTTPException(
                status_code=409, detail=f"Task {task_id} is already terminal"
            )
        return _sse_stream(tasks.subscribe(task_id))

    @app.post(rpc_url)
    async def jsonrpc(payload: Dict[str, Any], request: Request) -> Any:
        method = str(payload.get("method") or "")
        request_id = payload.get("id")
        params = normalize_a2a_payload(payload.get("params") or {})

        if method == "SendMessage":
            task = await tasks.send_message(
                message=params.get("message") or {},
                configuration=params.get("configuration") or {},
                request=request,
            )
            return {"jsonrpc": "2.0", "id": request_id, "result": {"task": task}}

        if method == "SendStreamingMessage":
            iterator = tasks.stream_message(
                message=params.get("message") or {},
                request=request,
            )
            return _sse_stream(iterator, request_id=request_id)

        if method == "GetTask":
            task_id = params.get("id")
            task = await tasks.get(str(task_id))
            if not task:
                return _jsonrpc_error(request_id, -32001, "Task not found")
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
                return _jsonrpc_error(request_id, -32001, "Task not found")
            return {"jsonrpc": "2.0", "id": request_id, "result": task}

        if method == "SubscribeToTask":
            task_id = str(params.get("id") or "")
            current = await tasks.get(task_id)
            if not current:
                return _jsonrpc_error(request_id, -32001, "Task not found")
            state = str((current.get("status") or {}).get("state"))
            if _terminal_state(state):
                return _jsonrpc_error(
                    request_id,
                    -32004,
                    f"Task {task_id} is already terminal",
                )
            return _sse_stream(tasks.subscribe(task_id), request_id=request_id)

        if method == "GetExtendedAgentCard":
            return _jsonrpc_error(
                request_id,
                -32004,
                "Extended agent card is not supported",
            )

        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")

    return app
