"""Runtime helpers for Pydantic AI generated pipelines."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from superoptix.observability.phoenix import (
    instrument_framework_with_phoenix,
    phoenix_session_span,
    setup_phoenix_for_spec,
)

try:
    from pydantic_ai import Agent
except Exception:  # pragma: no cover - handled by generated pipeline import checks
    Agent = None  # type: ignore


def _normalize_provider(provider: str) -> str:
    p = str(provider or "").strip().lower()
    if p in {"google-genai", "google"}:
        return "google-gla"
    if p in {"local"}:
        return "ollama"
    return p or "ollama"


def _known_prefix(model: str) -> bool:
    known = (
        "ollama",
        "openai",
        "anthropic",
        "google",
        "google-gla",
        "bedrock",
        "azure",
        "cohere",
        "mistral",
        "deepseek",
        "groq",
        "together",
        "fireworks",
    )
    return any(model.startswith(f"{x}:") for x in known)


def resolve_model(
    language_model: Dict[str, Any],
    model_config: Optional[Dict[str, Any]] = None,
) -> str:
    cfg = dict(model_config or {})
    model = str(cfg.get("model") or language_model.get("model") or "qwen3.5:9b").strip()
    provider = _normalize_provider(
        cfg.get("provider") or language_model.get("provider") or "ollama"
    )
    api_base = cfg.get("api_base") or language_model.get("api_base")
    runtime_mode = (
        str(
            cfg.get("runtime_mode")
            or language_model.get("runtime_mode")
            or (
                "gateway"
                if isinstance(language_model.get("gateway"), dict)
                and language_model.get("gateway", {}).get("enabled")
                else "direct"
            )
        )
        .strip()
        .lower()
    )

    gateway_cfg: Dict[str, Any] = {}
    lm_gateway_cfg = language_model.get("gateway")
    cfg_gateway = cfg.get("gateway")
    if isinstance(lm_gateway_cfg, dict):
        gateway_cfg.update(lm_gateway_cfg)
    if isinstance(cfg_gateway, dict):
        gateway_cfg.update(cfg_gateway)

    if runtime_mode == "gateway":
        provider = _normalize_provider(
            str(cfg.get("provider") or provider or "gateway")
        )
        if provider in {"ollama", "local"}:
            provider = "gateway"

        gateway_base = gateway_cfg.get("base_url")
        if gateway_base:
            os.environ["LITELLM_BASE_URL"] = str(gateway_base).rstrip("/")

        api_key_env = str(
            gateway_cfg.get("api_key_env")
            or cfg.get("gateway_key_env")
            or "PYDANTIC_AI_GATEWAY_API_KEY"
        ).strip()
        if api_key_env:
            gateway_key = os.getenv(api_key_env, "").strip()
            if not gateway_key:
                raise ValueError(
                    f"Gateway runtime selected but env var '{api_key_env}' is not set."
                )
            os.environ.setdefault("LITELLM_API_KEY", gateway_key)
            # Many gateway endpoints are OpenAI-compatible.
            os.environ.setdefault("OPENAI_API_KEY", gateway_key)

    if not _known_prefix(model):
        model = f"{provider}:{model}"

    # Pydantic AI relies on env for Ollama endpoint configuration.
    if model.startswith("ollama:") and api_base:
        base = str(api_base).rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        os.environ["OLLAMA_BASE_URL"] = base
        os.environ.setdefault("OLLAMA_API_KEY", "ollama")

    return model


def build_instructions(spec_data: Dict[str, Any]) -> str:
    persona = (spec_data or {}).get("persona", {}) or {}
    tasks = (spec_data or {}).get("tasks", []) or []
    parts: list[str] = []

    role = str(persona.get("role", "")).strip()
    goal = str(persona.get("goal", "")).strip()
    backstory = str(persona.get("backstory", "")).strip()
    instructions = str(persona.get("instructions", "")).strip()
    traits = persona.get("traits", []) or []
    if isinstance(traits, str):
        traits = [x.strip() for x in traits.split(",") if x.strip()]

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
        "\n\n".join([p for p in parts if p]).strip()
        or "You are a helpful AI assistant."
    )


def create_agent(
    *,
    spec_data: Dict[str, Any],
    agent_name: str,
    model_name: Optional[str] = None,
    instructions: Optional[str] = None,
    output_model: Any = None,
    model_config: Optional[Dict[str, Any]] = None,
):
    if Agent is None:
        raise ImportError(
            "pydantic-ai is required. Install with: uv pip install pydantic-ai"
        )

    language_model = (spec_data or {}).get("language_model", {}) or {}
    resolved_model = model_name or resolve_model(
        language_model, model_config=model_config
    )
    resolved_instructions = instructions or build_instructions(spec_data)

    kwargs: Dict[str, Any] = {
        "model": resolved_model,
        "instructions": resolved_instructions,
        "name": agent_name,
    }
    if output_model is not None:
        kwargs["output_type"] = output_model
    return Agent(**kwargs)


def _to_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _build_logfire_span(logfire_enabled: bool, config: Dict[str, Any]):
    """Best-effort Logfire span context manager for agent runs."""
    if not logfire_enabled:
        return None
    try:
        import logfire  # type: ignore

        return logfire.span(
            "superoptix.pydantic_ai.run",
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
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
    logfire_enabled: bool = False,
    run_kwargs: Dict[str, Any] | None = None,
) -> Any:
    """Execute a Pydantic AI agent run with Phoenix instrumentation."""
    agent_name = str(getattr(agent, "name", "pydantic_ai_agent") or "pydantic_ai_agent")
    effective_run_kwargs = dict(run_kwargs or {})
    phoenix_handle = setup_phoenix_for_spec(
        agent_id=agent_name,
        spec_data=spec_data,
        default_project_name=f"SuperOptiX-{agent_name}",
    )
    instrument_framework_with_phoenix(phoenix_handle, "pydantic_ai")
    session_id = f"{agent_name}:{int(time.time() * 1000)}"
    span_attributes = {
        "superoptix.framework": "pydantic_ai",
        "superoptix.agent_name": agent_name,
        "superoptix.model_name": model_name,
    }
    with phoenix_session_span(
        phoenix_handle,
        span_name="superoptix.pydantic_ai.run",
        session_id=session_id,
        attributes=span_attributes,
        input_data=prompt,
    ) as span:
        result = await agent.run(prompt, **effective_run_kwargs)
        if span is not None and hasattr(span, "set_output"):
            span.set_output({"status": "success"})
        return result
