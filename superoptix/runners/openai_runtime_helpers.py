"""Runtime helpers for OpenAI Agents SDK generated pipelines."""

from __future__ import annotations

import asyncio
import inspect
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List


def _normalize_provider(provider: str) -> str:
    value = str(provider or "").strip().lower()
    if value in {"google-genai", "google-gla", "google"}:
        return "gemini"
    if value in {"local"}:
        return "ollama"
    if value in {"lm_studio", "lmstudio"}:
        return "openai"
    return value or "ollama"


def resolve_model(
    language_model: Dict[str, Any] | None,
    model_config: Dict[str, Any] | None = None,
) -> str:
    """Resolve model string for OpenAI Agents SDK."""
    lm_cfg = dict(language_model or {})
    runtime_cfg = dict(model_config or {})

    provider = _normalize_provider(
        runtime_cfg.get("provider") or lm_cfg.get("provider") or "ollama"
    )
    model = str(
        runtime_cfg.get("model") or lm_cfg.get("model") or "llama3.1:8b"
    ).strip()
    api_base = runtime_cfg.get("api_base") or lm_cfg.get("api_base")

    # Allow pre-resolved model strings from callers.
    if model.startswith("litellm/"):
        return model

    # Accept provider-prefixed model formats like "openai:gpt-4o-mini".
    if ":" in model:
        prefix, suffix = model.split(":", 1)
        prefix_norm = _normalize_provider(prefix)
        if suffix.strip() and prefix_norm in {
            "openai",
            "anthropic",
            "gemini",
            "ollama",
            "groq",
            "cohere",
            "mistral",
            "azure",
            "bedrock",
            "deepseek",
            "together",
            "fireworks",
            "vllm",
        }:
            provider = prefix_norm
            model = suffix.strip()

    if api_base:
        base = str(api_base).rstrip("/")
        os.environ.setdefault("OPENAI_BASE_URL", base)
        os.environ.setdefault("LITELLM_BASE_URL", base)
        if provider == "ollama":
            os.environ.setdefault("OLLAMA_BASE_URL", base)
            os.environ.setdefault("OLLAMA_API_KEY", "ollama")

    # Native OpenAI path can remain plain model name.
    if provider == "openai" and re.match(r"^(gpt|o\d|o\d-mini|o\d-pro)", model):
        return model

    # Provider-agnostic path via LiteLLM adapter in OpenAI Agents.
    return f"litellm/{provider}/{model}"


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


def _safe_identifier(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", str(name or "arg"))
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "arg"
    if cleaned[0].isdigit():
        cleaned = f"arg_{cleaned}"
    return cleaned


def _build_signature_from_schema(
    schema: Dict[str, Any] | None,
) -> tuple[inspect.Signature, Dict[str, str]]:
    schema = dict(schema or {})
    props = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])

    params = []
    alias_map: Dict[str, str] = {}
    used: set[str] = set()
    for original_name, info in props.items():
        info = info or {}
        py_name = _safe_identifier(str(original_name))
        if py_name in used:
            idx = 2
            while f"{py_name}_{idx}" in used:
                idx += 1
            py_name = f"{py_name}_{idx}"
        used.add(py_name)
        alias_map[py_name] = str(original_name)
        ann = _json_schema_type_to_python(info.get("type"))
        default = inspect.Parameter.empty if original_name in required else None
        params.append(
            inspect.Parameter(
                name=py_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=ann,
            )
        )
    signature = inspect.Signature(parameters=params, return_annotation=str)
    return signature, alias_map


def _tool_schema(tool: Any) -> Dict[str, Any]:
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


def _stackone_to_openai_function_tools(source_tools: List[Any]) -> List[Any]:
    try:
        from agents import function_tool
    except Exception:
        return []

    wrapped_tools: List[Any] = []
    for tool in source_tools or []:
        name = str(getattr(tool, "name", "stackone_tool"))
        description = str(getattr(tool, "description", "") or "").strip()
        signature, alias_map = _build_signature_from_schema(_tool_schema(tool))
        safe_name = _safe_identifier(name)

        def _make_callable(
            bound_tool: Any, bound_name: str, bound_alias: Dict[str, str]
        ):
            def _tool_callable(**kwargs):
                payload = {
                    bound_alias.get(k, k): v
                    for k, v in (kwargs or {}).items()
                    if v is not None
                }
                keys = ",".join(sorted(payload.keys())) if payload else "-"
                print(f"tool:start: {bound_name} kwargs=[{keys}]")
                started = time.time()
                try:
                    out = bound_tool.execute(payload)
                    latency_ms = int((time.time() - started) * 1000)
                    print(f"tool:ok: {bound_name} ({latency_ms}ms)")
                    return str(out)
                except Exception as exc:
                    latency_ms = int((time.time() - started) * 1000)
                    print(f"tool:error: {bound_name} ({latency_ms}ms) error={exc}")
                    raise

            _tool_callable.__name__ = bound_name
            _tool_callable.__doc__ = description or f"StackOne tool: {bound_name}"
            _tool_callable.__signature__ = signature
            return _tool_callable

        wrapped = _make_callable(tool, safe_name, alias_map)
        try:
            wrapped_tools.append(function_tool(wrapped))
        except Exception:
            continue
    return wrapped_tools


def build_stackone_tools(spec_data: Dict[str, Any] | None) -> List[Any]:
    """Build OpenAI Agents-compatible StackOne tools when configured."""
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
        if mode == "stackone_discovery":
            source_tools = bridge.to_discovery_tools(framework="dspy")
        else:
            source_tools = bridge.tools

        tools = _stackone_to_openai_function_tools(source_tools)
        names = [getattr(t, "name", "") for t in tools[:5]]
        if tools:
            print(
                f"[StackOne] Loaded {len(tools)} OpenAI tool(s)"
                + (f": {', '.join(n for n in names if n)}" if names else "")
            )
        return tools
    except Exception as exc:
        msg = f"Failed to initialize StackOne tools: {exc}"
        if strict_mode:
            raise RuntimeError(msg) from exc
        print(f"⚠️ {msg}")
        return []


def get_openai_rlm_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Resolve OpenAI Agents RLM config from SuperSpec.

    Preferred location:
      spec.openai_agent.rlm
    Optional fallback:
      spec.rlm
    """
    spec = dict(spec_data or {})
    openai_cfg = spec.get("openai_agent")
    rlm_cfg: Dict[str, Any] = {}
    if isinstance(openai_cfg, dict) and isinstance(openai_cfg.get("rlm"), dict):
        rlm_cfg = dict(openai_cfg.get("rlm") or {})
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
        "logger_file_name": str(
            logger_cfg.get("file_name", "openai_rlm") or "openai_rlm"
        ),
    }


async def run_with_optional_rlm(
    *,
    agent: Any,
    prompt: str,
    spec_data: Dict[str, Any] | None,
    model_name: str,
) -> Any:
    """
    Execute OpenAI Agents run with optional RLM orchestration.

    Modes:
    - disabled: direct Runner.run(agent, input=prompt)
    - assist: RLM draft -> Runner.run(augmented_prompt)
    - replace: RLM-only response
    """
    from agents import Runner

    cfg = get_openai_rlm_config(spec_data)
    if not cfg.get("enabled", False):
        return await Runner.run(agent, input=prompt)

    try:
        from rlm import RLM  # type: ignore
    except Exception:
        print("⚠️ RLM enabled but package not installed. Install with: pip install rlms")
        return await Runner.run(agent, input=prompt)

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
        backend=str(cfg.get("backend") or "litellm"),
        backend_kwargs=backend_kwargs,
        environment=str(cfg.get("environment") or "python"),
        max_depth=int(cfg.get("max_depth") or 1),
        max_iterations=int(cfg.get("max_iterations") or 8),
        logger=logger_obj,
        verbose=bool(cfg.get("verbose", False)),
        persistent=bool(cfg.get("persistent", False)),
    )

    mode = str(cfg.get("mode", "assist")).strip().lower()
    if mode not in {"assist", "replace"}:
        mode = "assist"

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
    return await Runner.run(agent, input=augmented_prompt)
