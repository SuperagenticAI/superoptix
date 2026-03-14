"""A2A client protocol implementation for SuperOptiX."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

import dspy

from superoptix.protocols.base import BaseProtocol, ProtocolType

logger = logging.getLogger(__name__)

try:
    from a2a.client import ClientConfig, ClientFactory
    from a2a.types import Message, TextPart

    A2A_SDK_AVAILABLE = True
except ImportError:
    A2A_SDK_AVAILABLE = False
    ClientConfig = None
    ClientFactory = None
    Message = None
    TextPart = None


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
        self.client = None
        self.agent_card: Dict[str, Any] = {}
        self.available_skills: List[Dict[str, Any]] = []

    def _run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            raise RuntimeError(
                "A2AClient synchronous methods cannot be used from an active event loop"
            )
        return asyncio.run(coro)

    async def _connect_async(self) -> bool:
        if self.mock_agent_card is not None:
            self.agent_card = dict(self.mock_agent_card)
            self.available_skills = list(self.agent_card.get("skills", []) or [])
            self._connected = True
            return True

        if not A2A_SDK_AVAILABLE:
            logger.warning(
                "A2A SDK is not installed. Install superoptix[a2a] to enable A2A connectivity."
            )
            return False

        config = ClientConfig()
        self.client = await ClientFactory.connect(
            self.agent_url,
            client_config=config,
        )
        card = await self.client.get_card()
        self.agent_card = (
            card.model_dump()
            if hasattr(card, "model_dump")
            else dict(card)
        )
        self.available_skills = list(self.agent_card.get("skills", []) or [])
        self._connected = True
        return True

    def connect(self) -> bool:
        try:
            return bool(self._run_async(self._connect_async()))
        except Exception as exc:
            logger.error("A2A connection failed: %s", exc)
            return False

    def disconnect(self) -> None:
        self.client = None
        self._connected = False

    def get_capabilities(self) -> Dict[str, Any]:
        card = self.agent_card or {}
        self._capabilities = {
            "protocol": "a2a",
            "version": str(card.get("protocol_version") or "0.3.0"),
            "agent_url": self.agent_url,
            "skills": [skill.get("id") for skill in self.available_skills],
            "streaming": bool((card.get("capabilities") or {}).get("streaming")),
            "push_notifications": bool(
                (card.get("capabilities") or {}).get("push_notifications")
            ),
        }
        return self._capabilities

    def discover_peers(self) -> List[str]:
        return [self.agent_url]

    async def _send_message_async(self, message_text: str) -> Dict[str, Any]:
        if self.mock_agent_card is not None:
            return {
                "response": f"Mock A2A response from {self.agent_url}: {message_text}",
                "agent_url": self.agent_url,
            }

        if not self.client or not A2A_SDK_AVAILABLE:
            raise RuntimeError("A2A client is not connected")

        message = Message(
            role="user",
            message_id="superoptix-a2a",
            parts=[TextPart(text=message_text)],
        )
        events = []
        async for event in self.client.send_message(message):
            events.append(event)

        rendered = []
        for event in events:
            rendered.append(str(event))
        return {
            "response": "\n".join(rendered),
            "events": rendered,
            "agent_url": self.agent_url,
        }

    def _handle_request(self, **kwargs) -> dspy.Prediction:
        message_text = str(
            kwargs.get("message")
            or kwargs.get("query")
            or kwargs.get("task")
            or ""
        ).strip()
        if not message_text:
            message_text = "No message provided"

        result = self._run_async(self._send_message_async(message_text))
        return dspy.Prediction(
            response=result.get("response", ""),
            capabilities=self.get_capabilities(),
            agent_card=json.dumps(self.agent_card, sort_keys=True),
        )
