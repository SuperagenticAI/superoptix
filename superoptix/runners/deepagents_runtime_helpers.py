"""Runtime helpers for DeepAgents generated pipelines."""

from __future__ import annotations

import os
from typing import Any, Dict, List


def _normalize_provider(provider: str) -> str:
    value = str(provider or "").strip().lower()
    if value in {"google-genai", "google-gla"}:
        return "google_genai"
    if value in {"google"}:
        return "google_genai"
    if value in {"local"}:
        return "ollama"
    return value or "ollama"


def resolve_model(
    language_model: Dict[str, Any] | None,
    model_config: Dict[str, Any] | None = None,
) -> str:
    """Resolve DeepAgents model string in provider:model format."""
    lm_cfg = dict(language_model or {})
    runtime_cfg = dict(model_config or {})
    provider = _normalize_provider(
        runtime_cfg.get("provider") or lm_cfg.get("provider") or "ollama"
    )
    model = str(runtime_cfg.get("model") or lm_cfg.get("model") or "qwen3.5:9b").strip()
    api_base = runtime_cfg.get("api_base") or lm_cfg.get("api_base")

    # normalize prefix model forms
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


def _to_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _extract_output_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        messages = result.get("messages")
        if isinstance(messages, list) and messages:
            last = messages[-1]
            content = getattr(last, "content", None)
            if content is None and isinstance(last, dict):
                content = last.get("content")
            if isinstance(content, list):
                # Some message objects store chunks
                parts = []
                for chunk in content:
                    if isinstance(chunk, dict):
                        if chunk.get("type") == "text":
                            parts.append(str(chunk.get("text", "")))
                    else:
                        parts.append(str(chunk))
                return "".join(parts).strip()
            if content is not None:
                return str(content).strip()
        for key in ("output", "response", "content", "text"):
            if key in result and result.get(key) is not None:
                return str(result.get(key)).strip()
    return str(result).strip()
