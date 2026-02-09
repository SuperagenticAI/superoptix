"""Runtime helpers for Google ADK generated pipelines."""

from __future__ import annotations

import asyncio
import os
import time
import inspect
from pathlib import Path
from typing import Any, Dict, List, Tuple


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
        runtime_cfg.get("model") or lm_cfg.get("model") or "gemini-2.5-flash"
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

    return model or "gemini-2.5-flash"


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
    """Build Google ADK-compatible StackOne tools when configured."""
    cfg = resolve_stackone_config(spec_data)
    mode = str(cfg.get("mode", "none")).strip().lower()
    enabled = bool(cfg.get("enabled", mode in {"stackone", "stackone_discovery"}))
    if not enabled:
        return []

    strict_mode = str(
        os.getenv("SUPEROPTIX_STACKONE_STRICT", "0")
    ).strip().lower() not in {
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
            [
                part.strip()
                for part in os.getenv(account_ids_env, "").split(",")
                if part.strip()
            ]
        )
    account_ids = list(dict.fromkeys(account_ids))

    providers = _to_str_list(cfg.get("providers"))
    actions = _to_str_list(cfg.get("actions"))
    fallback_unfiltered = bool(cfg.get("fallback_unfiltered", True))

    init_kwargs: Dict[str, Any] = {"api_key": api_key}
    if account_ids:
        init_kwargs["account_ids"] = account_ids
    if providers:
        init_kwargs["providers"] = providers
    if actions:
        init_kwargs["actions"] = actions

    try:
        toolset = StackOneToolSet(**init_kwargs)
        tools = toolset.get_tools()
        bridge = StackOneBridge(tools)
        if mode == "stackone_discovery":
            source_tools = bridge.to_discovery_tools(framework="dspy")
        else:
            source_tools = bridge.to_dspy()
        converted = _to_adk_stackone_callables(source_tools)
        if not converted and fallback_unfiltered and (providers or actions):
            toolset = StackOneToolSet(api_key=api_key)
            tools = toolset.get_tools()
            bridge = StackOneBridge(tools)
            if mode == "stackone_discovery":
                source_tools = bridge.to_discovery_tools(framework="dspy")
            else:
                source_tools = bridge.to_dspy()
            converted = _to_adk_stackone_callables(source_tools)
        names = [getattr(t, "__name__", "") for t in converted[:5]]
        if converted:
            print(
                f"[StackOne] Loaded {len(converted)} ADK tool(s): "
                + ", ".join(name for name in names if name)
            )
        return converted
    except Exception as exc:
        msg = f"Failed to initialize StackOne tools: {exc}"
        if strict_mode:
            raise RuntimeError(msg) from exc
        print(f"⚠️ {msg}")
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


def _to_adk_stackone_callables(source_tools: List[Any]) -> List[Any]:
    wrapped = []
    for tool in source_tools or []:
        name = str(getattr(tool, "name", "stackone_tool"))
        description = str(getattr(tool, "description", "") or "").strip()
        schema = _tool_to_schema(tool)
        signature = _build_signature_from_schema(schema)

        def _make_callable(bound_tool: Any, bound_name: str):
            class _ToolCallable:
                def __call__(self, **kwargs):
                    started = time.time()
                    keys = ", ".join(sorted(list(kwargs.keys()))[:6]) or "-"
                    print(f"tool:start: {bound_name} kwargs=[{keys}]")
                    try:
                        result = bound_tool.execute(kwargs or {})
                        elapsed = int((time.time() - started) * 1000)
                        print(f"tool:ok: {bound_name} ({elapsed}ms)")
                        return result
                    except Exception as exc:
                        elapsed = int((time.time() - started) * 1000)
                        print(f"tool:error: {bound_name} ({elapsed}ms) {exc}")
                        return {"error": str(exc)}

            return _ToolCallable()

        instance = _make_callable(tool, name)
        instance.__name__ = str(name)
        instance.__doc__ = description or f"StackOne tool: {name}"
        instance.__signature__ = signature
        wrapped.append(instance)
    return wrapped


def create_agent_runner(
    *,
    spec_data: Dict[str, Any],
    agent_name: str,
    model_config: Dict[str, Any] | None = None,
) -> Tuple[Any, Any, Dict[str, Any]]:
    """Create Google ADK Agent and runner from SuperSpec."""
    try:
        from google.adk import Agent
        from google.adk.runners import InMemoryRunner
    except Exception as exc:
        raise ImportError(
            "google-adk is required. Install with: pip install google-adk"
        ) from exc

    model = resolve_model(
        spec_data.get("language_model", {}) or {}, model_config=model_config
    )
    instruction = build_instructions(spec_data)
    description = str(
        (spec_data.get("metadata", {}) or {}).get("description", "")
    ).strip()
    if not description:
        description = f"{agent_name} agent"
    tools = build_stackone_tools(spec_data)

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


def get_google_adk_rlm_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Resolve Google ADK RLM config from SuperSpec.

    Preferred location:
      spec.google_adk.rlm
    Optional fallback:
      spec.rlm (legacy compatibility if it includes backend/task_model/mode fields)
    """
    spec = dict(spec_data or {})
    adk_cfg = spec.get("google_adk")
    rlm_cfg: Dict[str, Any] = {}

    if isinstance(adk_cfg, dict) and isinstance(adk_cfg.get("rlm"), dict):
        rlm_cfg = dict(adk_cfg.get("rlm") or {})
    else:
        legacy_rlm = spec.get("rlm")
        if isinstance(legacy_rlm, dict) and (
            "backend" in legacy_rlm
            or "task_model" in legacy_rlm
            or "mode" in legacy_rlm
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
        "logger_file_name": str(logger_cfg.get("file_name", "adk_rlm") or "adk_rlm"),
    }


def _build_logfire_span(logfire_enabled: bool, config: Dict[str, Any]):
    """Best-effort Logfire span context manager for ADK RLM calls."""
    if not logfire_enabled:
        return None
    try:
        import logfire  # type: ignore

        return logfire.span(
            "superoptix.google_adk.rlm",
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
    runner: Any,
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
    app_name: str,
    user_id: str = "superoptix_user",
    logfire_enabled: bool = False,
) -> str:
    """
    Execute ADK run with optional RLM routing.

    Modes:
    - disabled: direct ADK run
    - assist: RLM draft -> ADK run(augmented_prompt)
    - replace: RLM only
    """
    cfg = get_google_adk_rlm_config(spec_data)
    if not cfg.get("enabled", False):
        return await run_agent_query(
            agent=agent,
            runner=runner,
            prompt=prompt,
            app_name=app_name,
            user_id=user_id,
        )

    try:
        from rlm import RLM  # type: ignore
    except Exception:
        print("⚠️ RLM enabled but package not installed. Install with: pip install rlms")
        return await run_agent_query(
            agent=agent,
            runner=runner,
            prompt=prompt,
            app_name=app_name,
            user_id=user_id,
        )

    logger_obj = None
    if cfg.get("logger_enabled", False):
        try:
            from rlm.logger.rlm_logger import RLMLogger  # type: ignore

            log_dir = Path(
                str(cfg.get("logger_dir", ".superoptix/logs/rlm"))
            ).as_posix()
            logger_obj = RLMLogger(
                log_dir=log_dir,
                file_name=str(cfg.get("logger_file_name", "adk_rlm")),
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
        return await run_agent_query(
            agent=agent,
            runner=runner,
            prompt=augmented_prompt,
            app_name=app_name,
            user_id=user_id,
        )
    finally:
        if span is not None:
            span.__exit__(None, None, None)


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
