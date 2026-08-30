"""FastAPI service adapter for SuperOptiX harness agents."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from superoptix.harness.session import HarnessAgent


def create_harness_app(
    agent_factory: HarnessAgent | Callable[[str], HarnessAgent],
) -> Any:
    """Create a small HTTP app for stateful harness invocation."""
    try:
        from fastapi import FastAPI, HTTPException, Request
    except Exception as exc:
        raise ImportError(
            "Harness service requires FastAPI. Install with: pip install "
            "'superoptix[web]'."
        ) from exc

    app = FastAPI(title="SuperOptiX Harness")

    def resolve_agent(agent_name: str) -> HarnessAgent:
        if isinstance(agent_factory, HarnessAgent):
            if agent_factory.name != agent_name:
                raise HTTPException(
                    status_code=404,
                    detail=f"Unknown agent '{agent_name}'",
                )
            return agent_factory
        return agent_factory(agent_name)

    @app.post("/agents/{agent_name}/{session_id}")
    async def invoke_agent(
        agent_name: str,
        session_id: str,
        request: Request,
    ) -> dict[str, Any]:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="JSON object payload required")

        prompt = payload.get("prompt") or payload.get("message") or payload.get("text")
        if not isinstance(prompt, str) or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="Payload must include a non-empty prompt, message, or text",
            )

        agent = resolve_agent(agent_name)
        session = await agent.session(
            session_id,
            role=payload.get("role") if isinstance(payload.get("role"), str) else None,
        )
        result = await session.prompt(prompt)
        return {
            "agent": agent_name,
            "session": session_id,
            "text": result.text,
            "metadata": result.metadata,
        }

    return app
