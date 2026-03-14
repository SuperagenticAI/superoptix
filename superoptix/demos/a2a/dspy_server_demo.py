"""Serve a lightweight DSPy-style SuperOptiX pipeline over A2A."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import dspy

from superoptix.demos.a2a.common import serve_pipeline


class ResearchSignature(dspy.Signature):
    """Create a concise research brief from a user query."""

    query: str = dspy.InputField(desc="Research question")
    response: str = dspy.OutputField(desc="Short research brief")


class ResearchModule(dspy.Module):
    """Deterministic DSPy module for the packaged A2A demo."""

    def forward(self, query: str):
        summary = (
            f"Research brief: '{query}' should be answered with a concise summary, "
            "2 key facts, and one recommended next step."
        )
        return dspy.Prediction(response=summary)


@dataclass
class DemoDSPyPipeline:
    """Small compiled-pipeline-shaped object for the A2A demo."""

    metadata = {
        "name": "DSPy Research Brief Agent",
        "id": "a2a-dspy-demo",
        "version": "1.0.0",
        "description": "A DSPy-style agent exposed over A2A via SuperOptiX.",
    }
    spec = {
        "persona": {
            "role": "Research Analyst",
            "goal": "Return compact research briefs.",
        },
        "tasks": [
            {
                "name": "research_brief",
                "instruction": "Produce a short research brief for the query.",
            }
        ],
    }

    def __post_init__(self):
        self.program = ResearchModule()

    def run(self, query: str, **_: str):
        result = self.program(query=query)
        return {
            "response": getattr(result, "response", str(result)),
            "framework": "dspy",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8101)
    args = parser.parse_args()

    agent_url = f"http://{args.host}:{args.port}"
    print(f"Serving DSPy A2A demo at {agent_url}/a2a/jsonrpc")
    serve_pipeline(
        pipeline=DemoDSPyPipeline(),
        agent_url=agent_url,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()

