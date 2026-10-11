"""Runtime helpers for Microsoft Agent Framework generated pipelines."""

from __future__ import annotations

import os
from typing import Any, Dict

from superoptix.core.local_lm import ollama_openai_base


GOOGLE_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


_KNOWN_PROVIDERS = {
    "ollama",
    "openai",
    "azure",
    "google-genai",
    "anthropic",
    "mistral",
    "groq",
    "deepseek",
    "openrouter",
}


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
    model = str(runtime_cfg.get("model") or lm_cfg.get("model") or "qwen3.5:9b").strip()
    runtime_provider = _normalize_provider(runtime_cfg.get("provider") or "")
    lm_provider = _normalize_provider(lm_cfg.get("provider") or "")
    provider_switched = bool(runtime_provider and runtime_provider != lm_provider)
    api_base_source = runtime_cfg.get("api_base")
    if not api_base_source and not provider_switched:
        api_base_source = lm_cfg.get("api_base")
    api_base = str(api_base_source or "").strip()

    model_prefix, model_suffix = _strip_provider_prefix(model)
    # Only a real provider counts as a prefix: "qwen2.5:1.5b" is an Ollama
    # name:tag, not provider "qwen2.5" with model "1.5b".
    if model_prefix and _normalize_provider(model_prefix) in _KNOWN_PROVIDERS:
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
                # Ollama's OpenAI-compatible API lives under /v1.
                "base_url": ollama_openai_base(api_base or None),
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


def create_chat_client(client_config: Dict[str, Any]) -> Any:
    """Build an Agent Framework chat client from :func:`resolve_client_config`.

    Copes with Agent Framework API drift: 1.19 dropped
    ``agent_framework.azure.AzureOpenAIChatClient`` (Azure moved onto
    ``OpenAIChatClient(azure_endpoint=...)``) and renamed ``model_id`` to
    ``model``. Servers reached through ``base_url`` (Ollama, Gemini's OpenAI
    endpoint) get the Chat Completions client, which every OpenAI-compatible
    server implements.
    """
    import inspect

    from agent_framework import openai as af_openai

    kwargs = dict(client_config.get("kwargs") or {})
    cls = af_openai.OpenAIChatClient
    if client_config.get("client_type") == "azure":
        try:
            from agent_framework.azure import AzureOpenAIChatClient as cls
        except ImportError:
            kwargs["azure_endpoint"] = kwargs.pop("endpoint", None)
            kwargs["model"] = kwargs.pop("deployment_name", None)
    elif kwargs.get("base_url"):
        cls = getattr(af_openai, "OpenAIChatCompletionClient", None) or cls

    params = inspect.signature(cls.__init__).parameters
    if "model_id" in kwargs and "model_id" not in params and "model" in params:
        kwargs["model"] = kwargs.pop("model_id")
    return cls(**kwargs)
