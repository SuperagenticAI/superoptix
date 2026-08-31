"""System Under Test harness for the official A2A TCK.

The TCK drives an agent into specific protocol states by prefixing the request's
``messageId`` — ``tck-input-required`` must leave the task non-terminal,
``tck-complete-task`` must complete it, ``tck-artifact-text`` must return an
artifact, and so on. Reference SUTs in the A2A project implement the same hooks.

This lives in its own app on purpose. The published SuperOptiX endpoint must not
change behaviour because of a magic ``messageId``: that would be a production
agent honouring untrusted client input. Run this one only for conformance:

    uvicorn superoptix.protocols.a2a.tck_sut:app
    run_tck.py --sut-host http://127.0.0.1:8000
"""

from __future__ import annotations

import os
from typing import Any, AsyncIterator, Dict, List

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.server import create_a2a_fastapi_app
from superoptix.runtime.base import RuntimeContext
from superoptix.runtime.registry import runtime_registry

RPC_URL = "/a2a/jsonrpc"
DEFAULT_URL = "http://127.0.0.1:8000"


def _text_artifact(text: str, name: str = "result") -> Dict[str, Any]:
    return {
        "artifactId": f"{name}-1",
        "name": name,
        "parts": [{"text": text}],
    }


def _file_artifact(name: str, *, url: str | None = None) -> Dict[str, Any]:
    """A2A 1.0 unifies Part: content fields sit flat on the part itself.

    The pre-1.0 nested ``{"file": {...}}`` wrapper is gone; a file part carries
    ``raw`` or ``url`` alongside ``filename`` and ``mediaType``.
    """
    part: Dict[str, Any] = {"filename": "output.txt", "mediaType": "text/plain"}
    if url:
        part["url"] = url
    else:
        part["raw"] = "VENLIGZmlsZQ=="
    return {"artifactId": f"{name}-1", "name": name, "parts": [part]}


def _data_artifact(name: str) -> Dict[str, Any]:
    return {
        "artifactId": f"{name}-1",
        "name": name,
        "parts": [{"data": {"key": "value", "count": 42}}],
    }


class TckSutRuntime:
    """Maps TCK messageId prefixes onto declared task outcomes."""

    def __init__(self, target: Any = None):
        self._target = target

    @staticmethod
    def _scenario(inputs: Dict[str, Any]) -> str:
        return str(inputs.get("message_id") or "")

    async def invoke(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> Dict[str, Any]:
        message_id = ""
        if context is not None:
            message_id = str((context.metadata or {}).get("message_id") or "")

        if message_id.startswith("tck-input-required"):
            return {
                "response": "More input is required to continue.",
                "a2a_state": "TASK_STATE_INPUT_REQUIRED",
            }
        if message_id.startswith("tck-message-response"):
            return {"response": "Direct message response", "a2a_message_only": True}
        if message_id.startswith("tck-artifact-file-url"):
            return {
                "response": "Artifact produced.",
                "a2a_artifacts": [
                    _file_artifact("file-url", url="https://example.com/f.txt")
                ],
            }
        if message_id.startswith("tck-artifact-file"):
            return {
                "response": "Artifact produced.",
                "a2a_artifacts": [_file_artifact("file")],
            }
        if message_id.startswith("tck-artifact-data"):
            return {
                "response": "Artifact produced.",
                "a2a_artifacts": [_data_artifact("data")],
            }
        if message_id.startswith("tck-artifact-text") or message_id.startswith(
            "tck-stream-artifact"
        ):
            return {
                "response": "Artifact produced.",
                "a2a_artifacts": [_text_artifact("Generated text content", "text")],
            }

        query = str(inputs.get("query") or "")
        return {"response": f"Echo: {query}" if query else "Acknowledged."}

    async def stream(
        self, inputs: Dict[str, Any], context: RuntimeContext | None = None
    ) -> AsyncIterator[Dict[str, Any]]:
        yield await self.invoke(inputs, context=context)

    async def cancel(self, task_id: str, context: RuntimeContext | None = None) -> bool:
        return True

    async def metadata(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "name": "SuperOptiX TCK SUT",
                "description": "Conformance harness for the A2A TCK",
                "version": "1.0",
            },
            "spec": {"tasks": []},
        }

    async def capabilities(self) -> Dict[str, Any]:
        return {"streaming": True, "cancel": True, "task_context": True}


runtime_registry.register("superoptix_tck_sut", TckSutRuntime)


def _sut_skills() -> List[Dict[str, Any]]:
    return [
        {
            "id": "echo",
            "name": "Echo",
            "description": "Echoes the submitted text back, and honours the TCK "
            "scenario prefixes used to drive protocol states",
            "tags": ["tck", "conformance"],
            "examples": ["hello"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ]


def create_sut_app(service_url: str | None = None) -> Any:
    url = (
        service_url
        or os.environ.get("SUPEROPTIX_A2A_SUT_URL", "").strip()
        or DEFAULT_URL
    ).rstrip("/")
    return create_a2a_fastapi_app(
        pipeline=None,
        agent_url=url,
        rpc_url=RPC_URL,
        runtime_adapter="superoptix_tck_sut",
        agent_card=build_a2a_agent_card_payload(
            metadata={
                "name": "SuperOptiX TCK SUT",
                "description": "Conformance harness for the official A2A TCK",
                "version": "1.0",
            },
            spec={},
            agent_url=url,
            rpc_url=RPC_URL,
            protocol_version="1.0",
            legacy_protocol_version="0.3",
            skills_override=_sut_skills(),
        ),
    )


app = create_sut_app()
