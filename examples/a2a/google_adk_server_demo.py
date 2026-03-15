"""Serve a lightweight Google ADK SuperOptiX pipeline over A2A."""

from __future__ import annotations

import argparse
import os

from common import serve_pipeline

try:
    from superoptix.runners.google_adk_runtime_helpers import (
        create_agent_runner,
        run_agent_with_optional_rlm,
    )
except ImportError as exc:  # pragma: no cover - optional dependency guard
    raise ImportError(
        "Google ADK demo requires the google-adk package. Install superoptix[frameworks-google]."
    ) from exc


class DemoGoogleADKPipeline:
    """Small async pipeline using the same Google ADK runtime helper path as generated agents."""

    metadata = {
        "name": "Google ADK Integration Planner",
        "id": "a2a-adk-demo",
        "version": "1.0.0",
        "description": "A Google ADK agent exposed over A2A via SuperOptiX.",
    }

    spec = {
        "metadata": metadata,
        "language_model": {
            "location": "cloud",
            "provider": "google",
            "model": "gemini-2.5-flash",
        },
        "persona": {
            "role": "Integration Architect",
            "goal": "Return concise rollout plans for interoperability work.",
            "instructions": (
                "Answer in a concise planning format. "
                "Give one recommendation, two implementation notes, and one operational caution."
            ),
        },
        "tasks": [
            {
                "name": "integration_plan",
                "instruction": "Create a short integration plan for the user query.",
            }
        ],
    }

    def __init__(self):
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError(
                "GOOGLE_API_KEY is required for the Google ADK A2A demo. "
                "Export it before starting this server."
            )
        self.agent, self.runner, self.runtime = create_agent_runner(
            spec_data=self.spec,
            agent_name="a2a_adk_demo",
        )

    async def run(self, query: str, **_: str):
        response = await run_agent_with_optional_rlm(
            agent=self.agent,
            runner=self.runner,
            prompt=query,
            spec_data=self.spec,
            model_name=str(self.runtime.get("model", "gemini-2.5-flash")),
            app_name=str(self.runtime.get("app_name", "superoptix_a2a_adk_demo")),
            logfire_enabled=False,
        )
        return {
            "response": response,
            "framework": "google_adk",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8103)
    args = parser.parse_args()

    agent_url = f"http://{args.host}:{args.port}"
    print(f"Serving Google ADK A2A demo at {agent_url}/a2a/jsonrpc")
    serve_pipeline(
        pipeline=DemoGoogleADKPipeline(),
        agent_url=agent_url,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
