"""Call an adapted agent through its own framework's entry API.

Each framework has one idiomatic way to run an agent with a string. This maps
A2A's message text onto that call and normalises whatever comes back, so the
generated server stays a thin bridge rather than a reimplementation.
"""

from __future__ import annotations

import inspect
from typing import Any, Dict


async def _maybe_await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


# Intermediate scratchpads a caller did not ask for.
_INTERNAL_FIELDS = {"reasoning", "rationale"}


def _as_text(result: Any) -> str:
    """Render a framework result as the text an A2A caller receives."""
    for attr in ("raw", "output", "final_output", "answer", "text"):
        value = getattr(result, attr, None)
        if isinstance(value, str) and value.strip():
            return value

    # Structured multi-field results (a DSPy Prediction, say). One field is
    # returned bare; several are labelled, because the raw repr is unreadable.
    fields = None
    if hasattr(result, "items") and callable(result.items):
        try:
            fields = dict(result.items())
        except Exception:  # noqa: BLE001 - fall through to str()
            fields = None
    elif isinstance(result, dict):
        fields = dict(result)

    if fields:
        for key in ("response", "answer", "output", "text", "result"):
            value = fields.get(key)
            if isinstance(value, str) and value.strip():
                return value
        visible = {
            k: v
            for k, v in fields.items()
            if k not in _INTERNAL_FIELDS and v is not None
        }
        if len(visible) == 1:
            return str(next(iter(visible.values()))).strip()
        if visible:
            return "\n".join(f"{k}: {v}" for k, v in visible.items())

    return str(result)


async def _invoke_crewai(agent: Any, query: str) -> Any:
    if hasattr(agent, "kickoff"):
        return await _maybe_await(agent.kickoff(inputs={"query": query}))
    if hasattr(agent, "execute_task"):
        return await _maybe_await(agent.execute_task(task=query))
    raise TypeError("CrewAI object exposes neither kickoff() nor execute_task()")


async def _invoke_dspy(program: Any, query: str) -> Any:
    if not callable(program):
        raise TypeError("DSPy object is not callable")
    # Signatures name their own input field; feed the first one when it is not
    # the conventional `question`.
    field = None
    try:
        predictors = list(program.named_predictors())
        if predictors:
            signature = getattr(predictors[0][1], "signature", None)
            inputs = list(getattr(signature, "input_fields", {}) or {})
            field = inputs[0] if inputs else None
    except Exception:  # noqa: BLE001 - fall through to a positional call
        field = None

    if field:
        return await _maybe_await(program(**{field: query}))
    return await _maybe_await(program(query))


async def _invoke_openai(agent: Any, query: str) -> Any:
    from agents import Runner

    return await _maybe_await(Runner.run(agent, query))


async def _invoke_pydantic_ai(agent: Any, query: str) -> Any:
    return await _maybe_await(agent.run(query))


async def _invoke_google_adk(agent: Any, query: str) -> Any:
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=agent, app_name="superoptix-a2a")
    session = await _maybe_await(
        runner.session_service.create_session(app_name="superoptix-a2a", user_id="a2a")
    )
    message = types.Content(role="user", parts=[types.Part(text=query)])
    chunks = []
    async for event in runner.run_async(
        user_id="a2a", session_id=session.id, new_message=message
    ):
        content = getattr(event, "content", None)
        for part in getattr(content, "parts", None) or []:
            if getattr(part, "text", None):
                chunks.append(part.text)
    return "\n".join(chunks)


async def _invoke_microsoft(agent: Any, query: str) -> Any:
    return await _maybe_await(agent.run(query))


async def _invoke_claude_sdk(options: Any, query: str) -> Any:
    from claude_agent_sdk import AssistantMessage, TextBlock, query as claude_query

    chunks = []
    async for message in claude_query(prompt=query, options=options):
        if isinstance(message, AssistantMessage):
            for block in getattr(message, "content", None) or []:
                if isinstance(block, TextBlock):
                    chunks.append(block.text)
    return "\n".join(chunks)


async def _invoke_deepagents(graph: Any, query: str) -> Any:
    result = await _maybe_await(
        graph.invoke({"messages": [{"role": "user", "content": query}]})
    )
    messages = (result or {}).get("messages") if isinstance(result, dict) else None
    if messages:
        last = messages[-1]
        return getattr(last, "content", None) or (
            last.get("content") if isinstance(last, dict) else last
        )
    return result


_INVOKERS = {
    "crewai": _invoke_crewai,
    "dspy": _invoke_dspy,
    "openai": _invoke_openai,
    "pydantic-ai": _invoke_pydantic_ai,
    "google-adk": _invoke_google_adk,
    "microsoft": _invoke_microsoft,
    "claude-sdk": _invoke_claude_sdk,
    "deepagents": _invoke_deepagents,
}


async def invoke_agent(agent: Any, framework: str, query: str) -> Dict[str, Any]:
    """Run the agent and return an A2A-shaped result."""
    invoker = _INVOKERS.get(str(framework or "").strip().lower())
    if invoker is None:
        raise ValueError(
            f"No invoker for framework {framework!r}. "
            f"Available: {', '.join(sorted(_INVOKERS))}"
        )
    result = await invoker(agent, query)
    return {"response": _as_text(result)}
