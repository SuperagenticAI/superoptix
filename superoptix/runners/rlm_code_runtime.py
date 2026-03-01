"""Shared runtime adapter for `provider: rlm_code`."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Tuple


_PROVIDER_ALIASES: dict[str, str] = {
    "google": "gemini",
    "google-genai": "gemini",
    "google_generative_ai": "gemini",
    "google-gla": "gemini",
    "lm_studio": "lmstudio",
    "local": "ollama",
}

_KNOWN_PROVIDERS: set[str] = {
    "anthropic",
    "azure",
    "deepseek",
    "fireworks",
    "gemini",
    "groq",
    "lmstudio",
    "ollama",
    "opencode",
    "openai",
    "openrouter",
    "together",
    "vllm",
}

_BACKEND_TO_PROVIDER: dict[str, str] = {
    "anthropic": "anthropic",
    "gemini": "gemini",
    "google": "gemini",
    "google-genai": "gemini",
    "litellm": "openai",
    "ollama": "ollama",
    "openai": "openai",
}

_PROVIDER_API_ENV: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "together": "TOGETHER_API_KEY",
}


def _normalize_provider(value: str) -> str:
    token = str(value or "").strip().lower()
    if not token:
        return ""
    return _PROVIDER_ALIASES.get(token, token)


def _parse_provider_and_model(raw: str) -> Tuple[str, str]:
    token = str(raw or "").strip()
    if not token:
        return "", ""

    if token.startswith("litellm/"):
        token = token.split("/", 1)[1]

    if "/" in token:
        prefix, suffix = token.split("/", 1)
        provider = _normalize_provider(prefix)
        if provider in _KNOWN_PROVIDERS and suffix.strip():
            return provider, suffix.strip()

    if ":" in token:
        prefix, suffix = token.split(":", 1)
        provider = _normalize_provider(prefix)
        if provider in _KNOWN_PROVIDERS and suffix.strip():
            return provider, suffix.strip()

    return "", token


def _resolve_provider_and_model(config: Dict[str, Any], model_name: str) -> Tuple[str, str]:
    backend = _normalize_provider(str(config.get("backend", "") or ""))
    backend_provider = _BACKEND_TO_PROVIDER.get(backend, "")

    candidates = [
        str(config.get("task_model", "") or "").strip(),
        str(model_name or "").strip(),
    ]
    for candidate in candidates:
        provider, resolved_model = _parse_provider_and_model(candidate)
        if provider and resolved_model:
            return provider, resolved_model
        if resolved_model and backend_provider:
            return backend_provider, resolved_model

    fallback_model = str(model_name or "").strip() or "gpt-4o-mini"
    return backend_provider or "openai", fallback_model


def _resolve_api_key(provider: str, config: Dict[str, Any]) -> str | None:
    explicit_env = str(config.get("api_key_env", "") or "").strip()
    if explicit_env:
        key = os.getenv(explicit_env, "").strip()
        if key:
            return key

    env_name = _PROVIDER_API_ENV.get(provider)
    if env_name:
        key = os.getenv(env_name, "").strip()
        if key:
            return key

    if provider == "gemini":
        key = os.getenv("GOOGLE_API_KEY", "").strip()
        if key:
            return key

    return None


def _normalize_environment(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if not value:
        return "generic"
    if value in {"python", "local"}:
        return "generic"
    return value


def _run_rlm_code_sync(prompt: str, config: Dict[str, Any], model_name: str) -> str:
    from rlm_code.core.config import ConfigManager
    from rlm_code.execution.engine import ExecutionEngine
    from rlm_code.models.llm_connector import LLMConnector
    from rlm_code.rlm import RLMRunner

    workdir = Path.cwd()
    config_manager = ConfigManager(project_root=workdir)

    # Avoid forcing Docker runtime in host projects.
    config_manager.config.sandbox.runtime = "local"

    llm_connector = LLMConnector(config_manager=config_manager)
    provider, resolved_model = _resolve_provider_and_model(config, model_name)
    api_key = _resolve_api_key(provider, config)
    api_base = str(config.get("api_base", "") or "").strip() or None

    llm_connector.connect_to_model(
        model_name=resolved_model,
        model_type=provider,
        api_key=api_key,
        base_url=api_base,
    )

    execution_engine = ExecutionEngine(config_manager=config_manager)
    try:
        execution_engine.set_runtime("local")
    except Exception:
        pass

    log_root = str(config.get("logger_dir", "") or "").strip() or ".superoptix/logs/rlm_code"
    run_dir = Path(log_root).expanduser().resolve() / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)

    runner = RLMRunner(
        llm_connector=llm_connector,
        execution_engine=execution_engine,
        run_dir=run_dir,
        workdir=workdir,
    )

    run_result = runner.run_task(
        task=str(prompt or ""),
        max_steps=max(1, int(config.get("max_iterations", 8) or 8)),
        exec_timeout=30,
        environment=_normalize_environment(str(config.get("environment", "") or "")),
        max_depth=max(1, int(config.get("max_depth", 1) or 1)),
    )
    return str(getattr(run_result, "final_response", "") or "").strip()


async def run_rlm_code_completion(
    *,
    prompt: str,
    config: Dict[str, Any],
    model_name: str,
) -> Tuple[str | None, str | None]:
    """
    Execute one RLM completion via installed `rlm-code`.

    Returns:
      (completion_text, error_message)
    """
    try:
        text = await asyncio.to_thread(_run_rlm_code_sync, prompt, config, model_name)
        return text, None
    except Exception as exc:  # pragma: no cover - exercised via caller fallbacks
        return None, str(exc)
