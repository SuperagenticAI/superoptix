"""Runtime helpers for CrewAI generated pipelines."""

from __future__ import annotations

import os
from typing import Any, Dict, List


def _normalize_provider(provider: str) -> str:
    value = str(provider or "").strip().lower()
    if value in {"google-genai", "google-gla"}:
        return "google_genai"
    if value == "google":
        return "google_genai"
    if value == "local":
        return "ollama"
    return value or "ollama"


def resolve_model(
    language_model: Dict[str, Any] | None,
    model_config: Dict[str, Any] | None = None,
) -> str:
    """Resolve model string to provider:model format."""
    lm_cfg = dict(language_model or {})
    runtime_cfg = dict(model_config or {})

    provider = _normalize_provider(
        runtime_cfg.get("provider") or lm_cfg.get("provider") or "ollama"
    )
    model = str(runtime_cfg.get("model") or lm_cfg.get("model") or "qwen3.5:9b").strip()
    api_base = runtime_cfg.get("api_base") or lm_cfg.get("api_base")

    if ":" in model:
        prefix, suffix = model.split(":", 1)
        prefix_norm = _normalize_provider(prefix)
        if suffix.strip() and prefix_norm in {
            "ollama",
            "openai",
            "anthropic",
            "google_genai",
            "azure_openai",
            "bedrock",
            "groq",
            "mistralai",
            "cohere",
            "deepseek",
            "together",
            "fireworks",
        }:
            provider = prefix_norm
            model = suffix.strip()

    if api_base and provider == "ollama":
        os.environ.setdefault("OLLAMA_BASE_URL", str(api_base).rstrip("/"))
        os.environ.setdefault("OLLAMA_API_KEY", "ollama")

    return f"{provider}:{model}"


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


def build_task_description(spec_data: Dict[str, Any] | None) -> str:
    spec = dict(spec_data or {})
    tasks = list(spec.get("tasks", []) or [])
    if tasks and isinstance(tasks[0], dict):
        text = str(tasks[0].get("instruction", "")).strip()
        if text:
            return f"{text}\n\nUser query:\n{{query}}"
    persona = dict(spec.get("persona", {}) or {})
    role = str(persona.get("role", "AI assistant")).strip() or "AI assistant"
    return f"Complete the user request using your expertise as {role}.\n\nUser query:\n{{query}}"


def _to_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def create_crewai_llm(
    model_name: str, language_model_cfg: Dict[str, Any] | None = None
) -> Any:
    """Create CrewAI LLM object (or model string fallback)."""
    lm_cfg = dict(language_model_cfg or {})
    provider, model = (
        (model_name.split(":", 1) + [""])[:2] if ":" in model_name else ("", model_name)
    )
    provider = _normalize_provider(provider)

    try:
        from crewai import LLM as CrewAILLM  # type: ignore
    except Exception:
        try:
            from crewai.llm import LLM as CrewAILLM  # type: ignore
        except Exception:
            CrewAILLM = None

    if provider == "ollama":
        api_base = str(
            lm_cfg.get("api_base")
            or os.getenv("OLLAMA_BASE_URL")
            or "http://localhost:11434"
        ).rstrip("/")
        model_for_crewai = f"ollama/{model}"
        if CrewAILLM is None:
            return model_for_crewai
        kwargs: Dict[str, Any] = {"model": model_for_crewai}
        if api_base:
            kwargs["base_url"] = api_base
        return CrewAILLM(**kwargs)

    # Use LiteLLM/CrewAI provider-prefixed model forms so CrewAI doesn't
    # silently fall back to OpenAI default provider.
    def _provider_model(p: str, m: str) -> str:
        raw = str(m or "").strip()
        if "/" in raw:
            return raw
        mapping = {
            "google_genai": "gemini",
            "openai": "openai",
            "anthropic": "anthropic",
            "groq": "groq",
            "cohere": "cohere",
            "mistralai": "mistral",
            "deepseek": "deepseek",
            "together": "together_ai",
            "fireworks": "fireworks_ai",
            "bedrock": "bedrock",
            "azure_openai": "azure",
        }
        prefix = mapping.get(p, p or "openai")
        return f"{prefix}/{raw}"

    model_for_crewai = _provider_model(provider, model)

    # Return model string by default; CrewAI resolves provider at runtime.
    # This avoids eager provider construction errors (like OpenAI fallback).
    return model_for_crewai


def extract_crewai_output(result: Any) -> str:
    if result is None:
        return ""
    raw = getattr(result, "raw", None)
    if raw is not None:
        return str(raw).strip()
    output = getattr(result, "output", None)
    if output is not None:
        return str(output).strip()
    to_dict = getattr(result, "to_dict", None)
    if callable(to_dict):
        try:
            return str(to_dict()).strip()
        except Exception:
            pass
    return str(result).strip()
