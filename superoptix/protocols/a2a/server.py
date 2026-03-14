"""A2A server bridge for exposing SuperOptiX pipelines."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.mappers import (
    extract_text_from_message,
    runtime_result_to_text,
)
from superoptix.runtime.base import AgentRuntime
from superoptix.runtime.registry import runtime_registry

logger = logging.getLogger(__name__)

try:
    from a2a.server.agent_execution.agent_executor import AgentExecutor
    from a2a.server.agent_execution.context import RequestContext
    from a2a.server.apps import A2AFastAPIApplication
    from a2a.server.events.event_queue import EventQueue
    from a2a.server.request_handlers.default_request_handler import (
        DefaultRequestHandler,
    )
    from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
    from a2a.types import (
        AgentCard,
        Message,
        TaskState,
        TaskStatus,
        TaskStatusUpdateEvent,
        TextPart,
    )

    A2A_SERVER_AVAILABLE = True
except ImportError:
    A2A_SERVER_AVAILABLE = False
    AgentExecutor = object

class SuperOptiXA2AExecutor(AgentExecutor):
    """Bridge a SuperOptiX runtime into the A2A AgentExecutor interface."""

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.running_tasks: set[str] = set()

    async def cancel(self, context: Any, event_queue: Any) -> None:
        task_id = context.task_id
        self.running_tasks.discard(task_id)
        status_update = TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context.context_id or str(uuid.uuid4()),
            status=TaskStatus(
                state=TaskState.canceled,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            final=True,
        )
        await event_queue.enqueue_event(status_update)

    async def execute(self, context: Any, event_queue: Any) -> None:
        task_id = context.task_id
        context_id = context.context_id
        self.running_tasks.add(task_id)

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(
                    state=TaskState.working,
                    message=Message(
                        role="agent",
                        message_id=str(uuid.uuid4()),
                        parts=[TextPart(text="Processing request")],
                        task_id=task_id,
                        context_id=context_id,
                    ),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ),
                final=False,
            )
        )

        try:
            user_input = extract_text_from_message(context.message)
            result = await self.runtime.invoke({"query": user_input})
            if task_id not in self.running_tasks:
                return
            result_text = runtime_result_to_text(result)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id,
                    context_id=context_id,
                    status=TaskStatus(
                        state=TaskState.completed,
                        message=Message(
                            role="agent",
                            message_id=str(uuid.uuid4()),
                            parts=[TextPart(text=result_text)],
                            task_id=task_id,
                            context_id=context_id,
                        ),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ),
                    final=True,
                )
            )
        except Exception as exc:
            logger.exception("A2A runtime execution failed")
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id,
                    context_id=context_id,
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=Message(
                            role="agent",
                            message_id=str(uuid.uuid4()),
                            parts=[TextPart(text=str(exc))],
                            task_id=task_id,
                            context_id=context_id,
                        ),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ),
                    final=True,
                )
            )
        finally:
            self.running_tasks.discard(task_id)


def create_a2a_fastapi_app(
    *,
    pipeline: Any,
    agent_url: str,
    rpc_url: str = "/a2a/jsonrpc",
    runtime_adapter: str = "compiled_pipeline",
) -> Any:
    """Create an A2A FastAPI app exposing a compiled SuperOptiX pipeline."""
    if not A2A_SERVER_AVAILABLE:
        raise ImportError(
            "A2A server dependencies are not installed. Install superoptix[a2a]."
        )

    runtime = runtime_registry.create(runtime_adapter, pipeline)

    async def _runtime_metadata():
        return await runtime.metadata()

    metadata = asyncio.run(_runtime_metadata())
    agent_card_payload = build_a2a_agent_card_payload(
        metadata=metadata.get("metadata", {}),
        spec=metadata.get("spec", {}),
        agent_url=agent_url,
        rpc_url=rpc_url,
    )
    agent_card = AgentCard(**agent_card_payload)
    request_handler = DefaultRequestHandler(
        agent_executor=SuperOptiXA2AExecutor(runtime),
        task_store=InMemoryTaskStore(),
    )
    application = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    return application.build(rpc_url=rpc_url)
