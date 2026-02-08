"""Runtime helpers for Pydantic AI generated pipelines."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

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
    model = str(cfg.get("model") or language_model.get("model") or "llama3.1:8b").strip()
    provider = _normalize_provider(
        cfg.get("provider") or language_model.get("provider") or "ollama"
    )
    api_base = cfg.get("api_base") or language_model.get("api_base")
    runtime_mode = str(
        cfg.get("runtime_mode")
        or language_model.get("runtime_mode")
        or (
            "gateway"
            if isinstance(language_model.get("gateway"), dict)
            and language_model.get("gateway", {}).get("enabled")
            else "direct"
        )
    ).strip().lower()

    gateway_cfg: Dict[str, Any] = {}
    lm_gateway_cfg = language_model.get("gateway")
    cfg_gateway = cfg.get("gateway")
    if isinstance(lm_gateway_cfg, dict):
        gateway_cfg.update(lm_gateway_cfg)
    if isinstance(cfg_gateway, dict):
        gateway_cfg.update(cfg_gateway)

    if runtime_mode == "gateway":
        provider = _normalize_provider(str(cfg.get("provider") or provider or "gateway"))
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

    return "\n\n".join([p for p in parts if p]).strip() or "You are a helpful AI assistant."


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
        raise ImportError("pydantic-ai is required. Install with: pip install pydantic-ai")

    language_model = (spec_data or {}).get("language_model", {}) or {}
    resolved_model = model_name or resolve_model(language_model, model_config=model_config)
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


def resolve_stackone_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Resolve StackOne config from a framework-agnostic SuperSpec shape.

    Supported locations (in precedence order):
      1) spec.stackone
      2) spec.tools.stackone
      3) spec.dspy.tools.stackone (back-compat for existing playbooks)
    """
    spec = dict(spec_data or {})

    stackone_cfg = spec.get("stackone")
    if not isinstance(stackone_cfg, dict):
        tools_cfg = spec.get("tools", {})
        if isinstance(tools_cfg, dict):
            stackone_cfg = tools_cfg.get("stackone")
        if not isinstance(stackone_cfg, dict):
            dspy_cfg = spec.get("dspy", {})
            dspy_tools = dspy_cfg.get("tools", {}) if isinstance(dspy_cfg, dict) else {}
            stackone_cfg = dspy_tools.get("stackone") if isinstance(dspy_tools, dict) else {}
            mode = dspy_tools.get("mode") if isinstance(dspy_tools, dict) else None
        else:
            mode = tools_cfg.get("mode")
    else:
        mode = spec.get("stackone_mode") or "stackone"

    if not isinstance(stackone_cfg, dict):
        stackone_cfg = {}

    if not mode:
        tools_cfg = spec.get("tools", {})
        mode = tools_cfg.get("mode") if isinstance(tools_cfg, dict) else None

    merged = dict(stackone_cfg)
    merged["mode"] = str(mode or merged.get("mode") or "stackone").strip().lower()
    return merged


def build_stackone_tools(spec_data: Dict[str, Any] | None, framework: str = "pydantic_ai") -> list[Any]:
    """Build framework-native StackOne tools via the StackOne SDK bridge."""
    stackone_cfg = resolve_stackone_config(spec_data)
    if not isinstance(stackone_cfg, dict):
        return []

    mode = str(stackone_cfg.get("mode", "stackone")).strip().lower()
    enabled = bool(stackone_cfg.get("enabled", mode in {"stackone", "stackone_discovery"}))
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
    except Exception:
        msg = "⚠️ StackOne tools requested but dependencies are unavailable. Install: pip install 'stackone-ai[mcp]'"
        print(msg)
        if strict_mode:
            raise RuntimeError(msg)
        return []

    api_key_env = str(stackone_cfg.get("api_key_env", "STACKONE_API_KEY")).strip()
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        msg = f"⚠️ StackOne tools requested but {api_key_env} is not set."
        print(msg)
        if strict_mode:
            raise RuntimeError(msg)
        return []

    account_ids = _to_str_list(stackone_cfg.get("account_ids", []))
    providers = _to_str_list(stackone_cfg.get("providers", []))
    actions = _to_str_list(stackone_cfg.get("actions", []))
    fallback_unfiltered = bool(stackone_cfg.get("fallback_unfiltered", True))
    account_ids_env = str(stackone_cfg.get("account_ids_env", "")).strip()
    if account_ids_env:
        env_accounts = [part.strip() for part in os.getenv(account_ids_env, "").split(",") if part.strip()]
        account_ids.extend(env_accounts)
        account_ids = list(dict.fromkeys(account_ids))

    init_kwargs: Dict[str, Any] = {"api_key": api_key}
    base_url = stackone_cfg.get("base_url")
    if base_url:
        init_kwargs["base_url"] = str(base_url).strip()

    discovery_mode = bool(stackone_cfg.get("discovery_mode", False)) or mode == "stackone_discovery"

    try:
        toolset = StackOneToolSet(**init_kwargs)
        fetched_tools = toolset.fetch_tools(
            account_ids=account_ids or None,
            providers=providers or None,
            actions=actions or None,
        )
        fetched_count = len(fetched_tools or [])
        if fetched_count == 0 and fallback_unfiltered and (providers or actions):
            print("⚠️ StackOne returned 0 tools with current providers/actions filters; retrying unfiltered.")
            fetched_tools = toolset.fetch_tools(
                account_ids=account_ids or None,
                providers=None,
                actions=None,
            )
            fetched_count = len(fetched_tools or [])

        if fetched_count == 0:
            msg = (
                "⚠️ StackOne fetched 0 tools. Check STACKONE_ACCOUNT_IDS, provider/action filters, "
                "and connector account status."
            )
            print(msg)
            if strict_mode:
                raise RuntimeError(msg)
            return []

        bridge = StackOneBridge(fetched_tools)
        if discovery_mode:
            tools = bridge.to_discovery_tools(framework=framework)
        elif framework == "pydantic_ai":
            tools = bridge.to_pydantic_ai()
        else:
            raise ValueError(f"Unsupported framework for StackOne tools: {framework}")

        names = [getattr(t, "name", "") for t in (tools or [])]
        preview = ", ".join([n for n in names if n][:5])
        print(
            f"[StackOne] Loaded {len(tools or [])} {framework} tool(s)"
            + (f": {preview}" if preview else "")
        )
        return tools or []
    except Exception as exc:
        print(f"⚠️ StackOne tool loading failed: {exc}")
        if strict_mode:
            raise
        return []


def get_pydantic_rlm_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Resolve Pydantic AI RLM config from SuperSpec.

    Preferred location:
      spec.pydantic_ai.rlm
    Optional fallback:
      spec.rlm (legacy compatibility if it includes backend/task_model fields)
    """
    spec = dict(spec_data or {})
    pydantic_cfg = spec.get("pydantic_ai")
    rlm_cfg: Dict[str, Any] = {}

    if isinstance(pydantic_cfg, dict) and isinstance(pydantic_cfg.get("rlm"), dict):
        rlm_cfg = dict(pydantic_cfg.get("rlm") or {})
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
        "logger_dir": str(logger_cfg.get("log_dir", ".superoptix/logs/rlm") or ".superoptix/logs/rlm"),
        "logger_file_name": str(logger_cfg.get("file_name", "pydantic_rlm") or "pydantic_rlm"),
    }


def _build_logfire_span(logfire_enabled: bool, config: Dict[str, Any]):
    """Best-effort Logfire span context manager for RLM calls."""
    if not logfire_enabled:
        return None
    try:
        import logfire  # type: ignore

        return logfire.span(
            "superoptix.pydantic_ai.rlm",
            backend=config.get("backend"),
            mode=config.get("mode"),
            max_iterations=config.get("max_iterations"),
            environment=config.get("environment"),
        )
    except Exception:
        return None


async def run_agent_with_optional_rlm(
    *,
    agent: Any,
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
    logfire_enabled: bool = False,
) -> Any:
    """
    Execute a Pydantic AI Agent run, optionally routing through RLM first.

    Modes:
    - disabled: direct Agent.run(prompt)
    - assist: RLM draft -> Agent.run(augmented_prompt)
    - replace: RLM only (returns string)
    """
    cfg = get_pydantic_rlm_config(spec_data)
    if not cfg.get("enabled", False):
        return await agent.run(prompt)

    try:
        from rlm import RLM  # type: ignore
    except Exception:
        print("⚠️ RLM enabled but package not installed. Install with: pip install rlms")
        return await agent.run(prompt)

    logger_obj = None
    if cfg.get("logger_enabled", False):
        try:
            from rlm.logger.rlm_logger import RLMLogger  # type: ignore

            log_dir = Path(str(cfg.get("logger_dir", ".superoptix/logs/rlm"))).as_posix()
            logger_obj = RLMLogger(
                log_dir=log_dir,
                file_name=str(cfg.get("logger_file_name", "pydantic_rlm")),
            )
        except Exception as exc:
            print(f"⚠️ Unable to initialize RLM logger: {exc}")

    backend_kwargs: Dict[str, Any] = {
        "model_name": cfg.get("task_model") or model_name,
    }
    api_key_env = str(cfg.get("api_key_env", "")).strip()
    if api_key_env:
        api_key = os.getenv(api_key_env, "").strip()
        if api_key:
            backend_kwargs["api_key"] = api_key

    api_base = str(cfg.get("api_base", "")).strip()
    if api_base:
        backend_kwargs["api_base"] = api_base

    rlm = RLM(
        backend=str(cfg.get("backend") or "litellm"),
        backend_kwargs=backend_kwargs,
        environment=str(cfg.get("environment") or "python"),
        max_depth=int(cfg.get("max_depth") or 1),
        max_iterations=int(cfg.get("max_iterations") or 8),
        logger=logger_obj,
        verbose=bool(cfg.get("verbose", False)),
        persistent=bool(cfg.get("persistent", False)),
    )

    span = _build_logfire_span(logfire_enabled=logfire_enabled, config=cfg)
    mode = str(cfg.get("mode", "assist")).strip().lower()
    if mode not in {"assist", "replace"}:
        mode = "assist"

    if span is not None:
        span.__enter__()
    try:
        print(
            "🧠 RLM enabled "
            f"(mode={mode}, backend={cfg.get('backend')}, max_iterations={cfg.get('max_iterations')})"
        )
        started = time.time()
        completion = await asyncio.to_thread(rlm.completion, prompt)
        rlm_text = str(getattr(completion, "response", completion) or "").strip()
        elapsed = int((time.time() - started) * 1000)
        print(f"✅ RLM completed ({elapsed}ms)")

        if mode == "replace":
            return rlm_text

        augmented_prompt = (
            "User request:\n"
            f"{prompt}\n\n"
            "RLM draft reasoning (use as guidance, verify with tools when needed):\n"
            f"{rlm_text}\n"
        )
        return await agent.run(augmented_prompt)
    finally:
        if span is not None:
            span.__exit__(None, None, None)
