"""Runtime helpers for Google ADK generated pipelines."""

from __future__ import annotations

import os
import time
import inspect
from typing import Any, Dict, List, Tuple

from superoptix.observability.phoenix import (
    instrument_framework_with_phoenix,
    phoenix_session_span,
    setup_phoenix_for_spec,
)


def _normalize_provider(provider: str) -> str:
    value = str(provider or "").strip().lower()
    if value in {"google-genai", "google-gla"}:
        return "google"
    if value in {"local"}:
        return "ollama"
    return value or "google"


def resolve_model(
    language_model: Dict[str, Any] | None,
    model_config: Dict[str, Any] | None = None,
) -> str:
    lm_cfg = dict(language_model or {})
    runtime_cfg = dict(model_config or {})
    provider = _normalize_provider(
        runtime_cfg.get("provider") or lm_cfg.get("provider") or "google"
    )
    model = str(
        runtime_cfg.get("model") or lm_cfg.get("model") or "gemini-3.7-flash"
    ).strip()

    # ADK examples expect bare Gemini model names. Normalize provider-prefixed aliases.
    if ":" in model:
        prefix, suffix = model.split(":", 1)
        if _normalize_provider(prefix) == "google" and suffix.strip():
            model = suffix.strip()

    # Local provider hints can still be passed via env if desired.
    api_base = runtime_cfg.get("api_base") or lm_cfg.get("api_base")
    if provider == "ollama" and api_base:
        os.environ.setdefault("OLLAMA_BASE_URL", str(api_base).rstrip("/"))
        os.environ.setdefault("OLLAMA_API_KEY", "ollama")

    return model or "gemini-3.7-flash"


def build_instructions(spec_data: Dict[str, Any] | None) -> str:
    spec = dict(spec_data or {})
    persona = dict(spec.get("persona", {}) or {})
    tasks = list(spec.get("tasks", []) or [])
    parts: List[str] = []

    role = str(persona.get("role", "")).strip()
    goal = str(persona.get("goal", "")).strip()
    backstory = str(persona.get("backstory", "")).strip()
    instructions = str(persona.get("instructions", "")).strip()
    traits = persona.get("traits", []) or []
    if isinstance(traits, str):
        traits = [part.strip() for part in traits.split(",") if part.strip()]

    if role:
        parts.append(f"Role: {role}")
    if goal:
        parts.append(f"Goal: {goal}")
    if backstory:
        parts.append(f"Backstory: {backstory}")
    if traits:
        parts.append(f"Traits: {', '.join(str(t) for t in traits)}")
    if instructions:
        parts.append(f"Instructions:\n{instructions}")

    if tasks and isinstance(tasks[0], dict):
        task_instruction = str(tasks[0].get("instruction", "")).strip()
        if task_instruction:
            parts.append(f"Task:\n{task_instruction}")

    return (
        "\n\n".join([part for part in parts if part]).strip()
        or "You are a helpful AI assistant."
    )


def _to_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _json_schema_type_to_python(t: str | None) -> Any:
    raw = str(t or "string").strip().lower()
    mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return mapping.get(raw, str)


def _build_signature_from_schema(schema: Dict[str, Any] | None) -> inspect.Signature:
    schema = dict(schema or {})
    props = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])
    params = []
    for name, info in props.items():
        info = info or {}
        ann = _json_schema_type_to_python(info.get("type"))
        default = inspect.Parameter.empty if name in required else None
        params.append(
            inspect.Parameter(
                name=str(name),
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=ann,
            )
        )
    return inspect.Signature(parameters=params, return_annotation=dict)


def _tool_to_schema(tool: Any) -> Dict[str, Any]:
    try:
        params = getattr(tool, "parameters", None)
        if params is None:
            return {}
        if hasattr(params, "model_dump"):
            return params.model_dump() or {}
        if isinstance(params, dict):
            return params
    except Exception:
        return {}
    return {}


def create_agent_runner(
    *,
    spec_data: Dict[str, Any],
    agent_name: str,
    model_config: Dict[str, Any] | None = None,
    extra_tools: List[Any] | None = None,
) -> Tuple[Any, Any, Dict[str, Any]]:
    """Create Google ADK Agent and runner from SuperSpec."""
    try:
        from google.adk import Agent
        from google.adk.runners import InMemoryRunner
    except Exception as exc:
        raise ImportError(
            "google-adk is required. Install with: uv pip install google-adk"
        ) from exc

    model = resolve_model(
        spec_data.get("language_model", {}) or {}, model_config=model_config
    )
    setup_phoenix_for_spec(
        agent_id=agent_name,
        spec_data=spec_data,
        default_project_name=f"SuperOptiX-{agent_name}",
    )
    instruction = build_instructions(spec_data)
    description = str(
        (spec_data.get("metadata", {}) or {}).get("description", "")
    ).strip()
    if not description:
        description = f"{agent_name} agent"
    tools = list(extra_tools or [])

    agent_kwargs: Dict[str, Any] = {
        "name": agent_name.replace("-", "_"),
        "model": model,
        "description": description,
        "instruction": instruction,
        "tools": tools or [],
    }
    try:
        agent = Agent(**agent_kwargs)
    except Exception:
        # Some ADK runtimes can reject non-native tool objects; keep run-path functional.
        if tools:
            print("⚠️ Failed to attach tools to ADK Agent. Retrying without tools.")
            agent_kwargs["tools"] = []
            agent = Agent(**agent_kwargs)
        else:
            raise

    app_name = f"superoptix_{agent_name.replace('-', '_')}"
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    runtime = {
        "model": model,
        "app_name": app_name,
        "tool_count": len(tools or []),
    }
    return agent, runner, runtime


def _build_logfire_span(logfire_enabled: bool, config: Dict[str, Any]):
    """Best-effort Logfire span context manager for ADK agent runs."""
    if not logfire_enabled:
        return None
    try:
        import logfire  # type: ignore

        return logfire.span(
            "superoptix.google_adk.run",
            backend=config.get("backend"),
            mode=config.get("mode"),
            max_iterations=config.get("max_iterations"),
            environment=config.get("environment"),
        )
    except Exception:
        return None


async def run_agent(
    *,
    agent: Any,
    runner: Any,
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
    app_name: str,
    user_id: str = "superoptix_user",
    logfire_enabled: bool = False,
) -> str:
    """Execute a Google ADK agent run with Phoenix instrumentation."""
    phoenix_handle = setup_phoenix_for_spec(
        agent_id=str(getattr(agent, "name", "google_adk_agent") or "google_adk_agent"),
        spec_data=spec_data,
        default_project_name=f"SuperOptiX-{str(getattr(agent, 'name', 'google_adk_agent') or 'google_adk_agent')}",
    )
    instrument_framework_with_phoenix(phoenix_handle, "google_adk")
    session_id = f"{user_id}:{int(time.time() * 1000)}"
    span_attributes = {
        "superoptix.framework": "google_adk",
        "superoptix.agent_name": str(
            getattr(agent, "name", "google_adk_agent") or "google_adk_agent"
        ),
        "superoptix.model_name": model_name,
        "superoptix.app_name": app_name,
    }
    with phoenix_session_span(
        phoenix_handle,
        span_name="superoptix.google_adk.run",
        session_id=session_id,
        attributes=span_attributes,
        input_data=prompt,
    ) as span:
        result = await run_agent_query(
            agent=agent,
            runner=runner,
            prompt=prompt,
            app_name=app_name,
            user_id=user_id,
        )
        if span is not None and hasattr(span, "set_output"):
            span.set_output({"status": "success"})
        return result


async def run_agent_query(
    *,
    agent: Any,
    runner: Any,
    prompt: str,
    app_name: str,
    user_id: str = "superoptix_user",
) -> str:
    """Execute an ADK run and return a concatenated text response."""
    from google.genai import types

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
    )
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=str(prompt or ""))],
    )
    response_parts: List[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if not getattr(event, "content", None):
            continue
        parts = getattr(event.content, "parts", None) or []
        for part in parts:
            text = getattr(part, "text", "")
            if text:
                response_parts.append(str(text))
    return "\n".join(response_parts).strip() or "No response generated."
