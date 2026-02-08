"""Runtime helpers for CrewAI generated pipelines."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


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
    model = str(runtime_cfg.get("model") or lm_cfg.get("model") or "llama3.1:8b").strip()
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
            return text
    persona = dict(spec.get("persona", {}) or {})
    role = str(persona.get("role", "AI assistant")).strip() or "AI assistant"
    return f"Complete the user request using your expertise as {role}."


def _to_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def resolve_stackone_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Resolve StackOne config from framework-agnostic SuperSpec paths."""
    spec = dict(spec_data or {})
    stackone_cfg = spec.get("stackone")
    mode = spec.get("stackone_mode")

    if not isinstance(stackone_cfg, dict):
        tools_cfg = spec.get("tools", {})
        if isinstance(tools_cfg, dict):
            stackone_cfg = tools_cfg.get("stackone")
            mode = mode or tools_cfg.get("mode")

    if not isinstance(stackone_cfg, dict):
        dspy_cfg = spec.get("dspy", {})
        dspy_tools = dspy_cfg.get("tools", {}) if isinstance(dspy_cfg, dict) else {}
        if isinstance(dspy_tools, dict):
            stackone_cfg = dspy_tools.get("stackone")
            mode = mode or dspy_tools.get("mode")

    if not isinstance(stackone_cfg, dict):
        stackone_cfg = {}

    merged = dict(stackone_cfg)
    merged["mode"] = str(mode or merged.get("mode") or "none").strip().lower()
    return merged


def build_stackone_tools(spec_data: Dict[str, Any] | None) -> List[Any]:
    """Build CrewAI-compatible StackOne tools when configured."""
    cfg = resolve_stackone_config(spec_data)
    mode = str(cfg.get("mode", "none")).strip().lower()
    enabled = bool(cfg.get("enabled", mode in {"stackone", "stackone_discovery"}))
    if not enabled:
        return []

    strict_mode = str(os.getenv("SUPEROPTIX_STACKONE_STRICT", "0")).strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    try:
        from stackone_ai import StackOneToolSet
        from superoptix.adapters import StackOneBridge
    except Exception as exc:
        msg = (
            "StackOne requested but dependencies are unavailable. "
            "Install: pip install 'stackone-ai[mcp]'"
        )
        if strict_mode:
            raise RuntimeError(msg) from exc
        print(f"⚠️ {msg}")
        return []

    api_key_env = str(cfg.get("api_key_env", "STACKONE_API_KEY")).strip()
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        msg = f"StackOne requested but {api_key_env} is not set."
        if strict_mode:
            raise RuntimeError(msg)
        print(f"⚠️ {msg}")
        return []

    account_ids = _to_str_list(cfg.get("account_ids"))
    account_ids_env = str(cfg.get("account_ids_env", "")).strip()
    if account_ids_env:
        account_ids.extend(
            [part.strip() for part in os.getenv(account_ids_env, "").split(",") if part.strip()]
        )
    account_ids = list(dict.fromkeys(account_ids))

    providers = _to_str_list(cfg.get("providers"))
    actions = _to_str_list(cfg.get("actions"))
    fallback_unfiltered = bool(cfg.get("fallback_unfiltered", True))

    init_kwargs: Dict[str, Any] = {"api_key": api_key}
    base_url = cfg.get("base_url")
    if base_url:
        init_kwargs["base_url"] = str(base_url).strip()

    try:
        toolset = StackOneToolSet(**init_kwargs)
        fetched_tools = toolset.fetch_tools(
            account_ids=account_ids or None,
            providers=providers or None,
            actions=actions or None,
        )
        if not fetched_tools and fallback_unfiltered and (providers or actions):
            fetched_tools = toolset.fetch_tools(
                account_ids=account_ids or None,
                providers=None,
                actions=None,
            )

        bridge = StackOneBridge(fetched_tools or [])
        tools = bridge.to_crewai()
        names = [getattr(t, "name", "") for t in tools[:5]]
        if tools:
            print(
                f"[StackOne] Loaded {len(tools)} CrewAI tool(s)"
                + (f": {', '.join(n for n in names if n)}" if names else "")
            )
        return tools or []
    except Exception as exc:
        msg = f"Failed to initialize StackOne tools: {exc}"
        if strict_mode:
            raise RuntimeError(msg) from exc
        print(f"⚠️ {msg}")
        return []


def create_crewai_llm(model_name: str, language_model_cfg: Dict[str, Any] | None = None) -> Any:
    """Create CrewAI LLM object (or model string fallback)."""
    lm_cfg = dict(language_model_cfg or {})
    provider, model = (model_name.split(":", 1) + [""])[:2] if ":" in model_name else ("", model_name)
    provider = _normalize_provider(provider)

    try:
        from crewai import LLM as CrewAILLM  # type: ignore
    except Exception:
        try:
            from crewai.llm import LLM as CrewAILLM  # type: ignore
        except Exception:
            CrewAILLM = None

    if provider == "ollama":
        api_base = str(lm_cfg.get("api_base") or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
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


def get_crewai_rlm_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Resolve CrewAI RLM config from spec.crewai.rlm with legacy fallback."""
    spec = dict(spec_data or {})
    crew_cfg = spec.get("crewai")
    rlm_cfg: Dict[str, Any] = {}
    if isinstance(crew_cfg, dict) and isinstance(crew_cfg.get("rlm"), dict):
        rlm_cfg = dict(crew_cfg.get("rlm") or {})
    else:
        legacy_rlm = spec.get("rlm")
        if isinstance(legacy_rlm, dict) and (
            "backend" in legacy_rlm or "task_model" in legacy_rlm or "mode" in legacy_rlm
        ):
            rlm_cfg = dict(legacy_rlm)

    logger_cfg = rlm_cfg.get("logger")
    if not isinstance(logger_cfg, dict):
        logger_cfg = {}

    return {
        "enabled": bool(rlm_cfg.get("enabled", False)),
        "mode": str(rlm_cfg.get("mode", "assist")).strip().lower() or "assist",
        "backend": str(rlm_cfg.get("backend", "litellm")).strip() or "litellm",
        "environment": str(rlm_cfg.get("environment", "python")).strip() or "python",
        "max_iterations": int(rlm_cfg.get("max_iterations", 8) or 8),
        "max_depth": int(rlm_cfg.get("max_depth", 1) or 1),
        "verbose": bool(rlm_cfg.get("verbose", False)),
        "persistent": bool(rlm_cfg.get("persistent", False)),
        "task_model": str(rlm_cfg.get("task_model", "") or "").strip(),
        "api_key_env": str(rlm_cfg.get("api_key_env", "") or "").strip(),
        "api_base": str(rlm_cfg.get("api_base", "") or "").strip(),
        "logger_enabled": bool(logger_cfg.get("enabled", False)),
        "logger_dir": str(
            logger_cfg.get("log_dir", ".superoptix/logs/rlm") or ".superoptix/logs/rlm"
        ),
        "logger_file_name": str(logger_cfg.get("file_name", "crewai_rlm") or "crewai_rlm"),
    }


def run_with_optional_rlm(
    *,
    crew: Any,
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
    task_description: str,
) -> str:
    """Execute CrewAI with optional RLM orchestration."""
    cfg = get_crewai_rlm_config(spec_data)
    if not cfg.get("enabled", False):
        result = crew.kickoff(inputs={"query": prompt})
        return extract_crewai_output(result)

    try:
        from rlm import RLM  # type: ignore
    except Exception:
        print("⚠️ RLM enabled but package not installed. Install with: pip install rlms")
        result = crew.kickoff(inputs={"query": prompt})
        return extract_crewai_output(result)

    logger_obj = None
    if cfg.get("logger_enabled", False):
        try:
            from rlm.logger.rlm_logger import RLMLogger  # type: ignore

            logger_obj = RLMLogger(
                log_dir=Path(str(cfg.get("logger_dir"))).as_posix(),
                file_name=str(cfg.get("logger_file_name")),
            )
        except Exception as exc:
            print(f"⚠️ Unable to initialize RLM logger: {exc}")

    backend_kwargs: Dict[str, Any] = {"model_name": cfg.get("task_model") or model_name}
    api_key_env = str(cfg.get("api_key_env", "")).strip()
    if api_key_env:
        api_key = os.getenv(api_key_env, "").strip()
        if api_key:
            backend_kwargs["api_key"] = api_key
    api_base = str(cfg.get("api_base", "")).strip()
    if api_base:
        backend_kwargs["api_base"] = api_base

    rlm = RLM(
        backend=cfg.get("backend") or "litellm",
        environment=cfg.get("environment") or "python",
        logger=logger_obj,
        **backend_kwargs,
    )

    task_prompt = (
        f"Task Description:\n{task_description}\n\n"
        f"User Request:\n{prompt}\n\n"
        "Provide a concise, actionable answer."
    )

    mode = cfg.get("mode", "assist")
    if mode == "replace":
        print("🧠 CrewAI RLM mode=replace (RLM-only)")
        try:
            return str(rlm(task_prompt)).strip()
        except Exception as exc:
            print(f"⚠️ RLM execution failed, falling back to CrewAI: {exc}")
            result = crew.kickoff(inputs={"query": prompt})
            return extract_crewai_output(result)

    print("🧠 CrewAI RLM mode=assist (RLM draft + CrewAI execution)")
    try:
        draft = str(rlm(task_prompt)).strip()
    except Exception as exc:
        print(f"⚠️ RLM draft failed, continuing without draft: {exc}")
        draft = ""

    augmented = prompt
    if draft:
        augmented = (
            f"User Request:\n{prompt}\n\n"
            f"RLM Draft (consider and refine):\n{draft}\n\n"
            "Produce the final answer."
        )

    result = crew.kickoff(inputs={"query": augmented})
    return extract_crewai_output(result)
