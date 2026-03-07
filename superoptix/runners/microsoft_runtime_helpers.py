"""Runtime helpers for Microsoft Agent Framework generated pipelines."""

from __future__ import annotations

import os
from typing import Any, Dict


GOOGLE_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _normalize_provider(provider: Any) -> str:
    value = str(provider or "").strip().lower()
    if value in {"google-genai", "google-gla", "google"}:
        return "google-genai"
    if value in {"azure-openai", "azure_openai"}:
        return "azure"
    if value in {"local"}:
        return "ollama"
    if value in {"lm_studio", "lmstudio"}:
        return "openai"
    return value or "ollama"


def _strip_provider_prefix(model: str) -> tuple[str | None, str]:
    text = str(model or "").strip()
    if ":" not in text:
        return None, text
    prefix, suffix = text.split(":", 1)
    return prefix.strip(), suffix.strip()


def resolve_client_config(
    language_model: Dict[str, Any] | None,
    model_config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Resolve Microsoft client type and kwargs from playbook/runtime config."""
    lm_cfg = dict(language_model or {})
    runtime_cfg = dict(model_config or {})

    provider = _normalize_provider(
        runtime_cfg.get("provider") or lm_cfg.get("provider") or "ollama"
    )
    model = str(
        runtime_cfg.get("model") or lm_cfg.get("model") or "llama3.1:8b"
    ).strip()
    runtime_provider = _normalize_provider(runtime_cfg.get("provider") or "")
    lm_provider = _normalize_provider(lm_cfg.get("provider") or "")
    provider_switched = bool(runtime_provider and runtime_provider != lm_provider)
    api_base_source = runtime_cfg.get("api_base")
    if not api_base_source and not provider_switched:
        api_base_source = lm_cfg.get("api_base")
    api_base = str(api_base_source or "").strip()

    model_prefix, model_suffix = _strip_provider_prefix(model)
    if model_prefix:
        prefix_norm = _normalize_provider(model_prefix)
        if model_suffix:
            provider = prefix_norm
            model = model_suffix

    if provider == "azure":
        return {
            "client_type": "azure",
            "kwargs": {
                "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", api_base),
                "api_key": os.getenv(
                    "AZURE_OPENAI_API_KEY", str(lm_cfg.get("api_key") or "").strip()
                ),
                "deployment_name": model,
            },
        }

    if provider == "ollama":
        return {
            "client_type": "openai",
            "kwargs": {
                "api_key": "ollama",
                "base_url": api_base or "http://localhost:11434/v1",
                "model_id": model,
            },
        }

    if provider == "google-genai":
        api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or str(lm_cfg.get("api_key") or "").strip()
        )
        return {
            "client_type": "openai",
            "kwargs": {
                "api_key": api_key,
                "base_url": api_base or GOOGLE_OPENAI_BASE_URL,
                "model_id": model,
            },
        }

    api_key = os.getenv("OPENAI_API_KEY", str(lm_cfg.get("api_key") or "").strip())
    kwargs: Dict[str, Any] = {"model_id": model}
    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["base_url"] = api_base
    return {
        "client_type": "openai",
        "kwargs": kwargs,
    }
