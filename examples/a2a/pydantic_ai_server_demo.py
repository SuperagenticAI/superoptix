"""Serve a lightweight Pydantic AI-style SuperOptiX pipeline over A2A."""

from __future__ import annotations

import argparse

from common import serve_pipeline

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.test import TestModel
except ImportError as exc:  # pragma: no cover - import guard for optional dep
    raise ImportError(
        "Pydantic AI demo requires the pydantic-ai package. Install superoptix[frameworks-pydantic-ai]."
    ) from exc


class DemoPydanticAIPipeline:
    """Small async pipeline using Pydantic AI's local TestModel."""

    metadata = {
        "name": "Pydantic AI FAQ Agent",
        "id": "pydantic_ai_faq",
        "version": "1.0.0",
        "description": "A Pydantic AI agent exposed over A2A via SuperOptiX.",
    }
    spec = {
        "persona": {
            "role": "FAQ Assistant",
            "goal": "Answer concise platform questions.",
        },
        "tasks": [
            {
                "name": "faq_answer",
                "instruction": "Answer the user question in one short paragraph.",
            }
        ],
    }

    def __init__(self):
        self.agent = Agent(
            TestModel(),
            system_prompt=(
                "You are a concise FAQ assistant for SuperOptiX demos. "
                "Answer clearly and briefly."
            ),
        )

    async def run(self, query: str, **_: str):
        result = await self.agent.run(query)
        return {
            "response": str(result.output),
            "framework": "pydantic_ai",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8102)
    args = parser.parse_args()

    agent_url = f"http://{args.host}:{args.port}"
    print(f"Serving Pydantic AI A2A demo at {agent_url}/a2a/jsonrpc")
    serve_pipeline(
        pipeline=DemoPydanticAIPipeline(),
        agent_url=agent_url,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
