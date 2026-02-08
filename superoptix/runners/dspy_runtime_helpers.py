"""Shared DSPy runtime helpers used by generated SuperOptiX pipelines.

Keeps generated pipeline code minimal by centralizing:
- Structured output coercion
- Assertion checks
- Built-in tool loading
- Optional StackOne tool loading
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

_TOOL_TRACE_EMITTER = None


def set_tool_trace_emitter(emitter):
    """Set process-local tool trace emitter callable(event: dict) or None."""
    global _TOOL_TRACE_EMITTER
    _TOOL_TRACE_EMITTER = emitter


def _emit_tool_trace(stage: str, detail: str, **extra) -> None:
    emitter = _TOOL_TRACE_EMITTER
    if emitter is None:
        return
    payload = {"stage": stage, "detail": detail, **extra}
    try:
        emitter(payload)
    except Exception:
        return


def _run_with_timeout(callable_obj, timeout_sec: float, *args, **kwargs):
    """Run callable in daemon thread and raise TimeoutError without blocking shutdown."""
    if timeout_sec <= 0:
        return callable_obj(*args, **kwargs)

    state: dict[str, Any] = {"done": False, "result": None, "error": None}

    def _target():
        try:
            state["result"] = callable_obj(*args, **kwargs)
        except Exception as exc:
            state["error"] = exc
        finally:
            state["done"] = True

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_sec)
    if not state["done"]:
        raise TimeoutError(f"timed out after {timeout_sec}s")
    if state["error"] is not None:
        raise state["error"]
    return state["result"]


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if "\n" in cleaned:
            cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def _coerce_bool(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    return value


def _coerce_value(value: Any, type_hint: str) -> Any:
    if value is None:
        return None

    hint = (type_hint or "str").strip()
    if not hint or hint == "str":
        return value

    if hint.startswith("Optional[") and hint.endswith("]"):
        inner = hint[len("Optional[") : -1]
        return _coerce_value(value, inner)

    if "|" in hint:
        for candidate in [part.strip() for part in hint.split("|")]:
            converted = _coerce_value(value, candidate)
            if converted is not value:
                return converted
        return value

    try:
        if hint == "int":
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return int(value)
            if isinstance(value, str):
                return int(value.strip())
        elif hint == "float":
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            if isinstance(value, str):
                return float(value.strip())
        elif hint == "bool":
            return _coerce_bool(value)
        elif hint.startswith("list[") or hint == "list":
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                parsed = json.loads(_strip_code_fences(value))
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict):
                    return [parsed]
        elif hint.startswith("dict[") or hint == "dict":
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                parsed = json.loads(_strip_code_fences(value))
                if isinstance(parsed, dict):
                    return parsed
        elif hint == "Any":
            return value
    except Exception:
        return value

    return value


def postprocess_prediction(
    prediction: Any,
    result: dict[str, Any] | None,
    output_fields: list[str] | None,
    signature_config: dict[str, Any] | None = None,
    output_field_types: dict[str, str] | None = None,
) -> dict[str, Any]:
    del prediction  # retained for hook compatibility
    cfg = signature_config or {}
    if str(cfg.get("output_mode", "simple")).strip().lower() != "structured":
        return result or {}

    processed = dict(result or {})
    field_types = output_field_types or {}
    for field in output_fields or []:
        if field not in processed:
            continue
        processed[field] = _coerce_value(processed[field], field_types.get(field, "str"))
    return processed


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def validate_prediction_result(
    result: dict[str, Any] | None,
    assertions_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = result or {}
    cfg = assertions_config or {}

    try:
        metric_weight = float(cfg.get("metric_weight", 0.3))
    except (TypeError, ValueError):
        metric_weight = 0.3

    if not cfg.get("enabled", False):
        return {
            "result": data,
            "assertions_passed": True,
            "assertion_errors": [],
            "assertion_mode": "fail_fast",
            "assertion_score": 1.0,
            "checks_total": 0,
            "checks_failed": 0,
            "metric_weight": metric_weight,
        }

    errors: list[str] = []
    checks_total = 0
    checks_failed = 0
    mode = str(cfg.get("mode", "fail_fast")).strip().lower() or "fail_fast"
    if mode not in {"fail_fast", "warn_only"}:
        mode = "fail_fast"

    for field in cfg.get("required_fields", []) or []:
        checks_total += 1
        if field not in data or data.get(field) is None:
            errors.append(f"Missing required field: {field}")
            checks_failed += 1

    for field in cfg.get("non_empty", []) or []:
        checks_total += 1
        if field in data and not _is_non_empty(data.get(field)):
            errors.append(f"Field must be non-empty: {field}")
            checks_failed += 1

    enum_rules = cfg.get("enum", {}) or {}
    for field, allowed in enum_rules.items():
        if field not in data:
            continue
        checks_total += 1
        allowed_set = {str(item) for item in (allowed or [])}
        if str(data.get(field)) not in allowed_set:
            errors.append(
                f"Field '{field}' value '{data.get(field)}' not in allowed set {sorted(list(allowed_set))}"
            )
            checks_failed += 1

    max_length_rules = cfg.get("max_length", {}) or {}
    for field, limit in max_length_rules.items():
        if field not in data:
            continue
        checks_total += 1
        value = data.get(field)
        if isinstance(value, str) and isinstance(limit, int) and len(value) > limit:
            errors.append(f"Field '{field}' exceeds max_length={limit} (got {len(value)})")
            checks_failed += 1
        elif (
            isinstance(value, (list, tuple, dict, set))
            and isinstance(limit, int)
            and len(value) > limit
        ):
            errors.append(f"Field '{field}' exceeds max_length={limit} (got {len(value)})")
            checks_failed += 1

    regex_rules = cfg.get("custom_regex", {}) or {}
    for field, pattern in regex_rules.items():
        if field not in data:
            continue
        checks_total += 1
        value = data.get(field)
        if isinstance(value, str):
            try:
                if re.search(pattern, value) is None:
                    errors.append(f"Field '{field}' did not match required regex pattern")
                    checks_failed += 1
            except re.error:
                errors.append(f"Invalid regex for field '{field}'")
                checks_failed += 1

    score = 1.0 if checks_total == 0 else max(0.0, 1.0 - (checks_failed / checks_total))
    return {
        "result": data,
        "assertions_passed": len(errors) == 0,
        "assertion_errors": errors,
        "assertion_mode": mode,
        "assertion_score": score,
        "checks_total": checks_total,
        "checks_failed": checks_failed,
        "metric_weight": metric_weight,
    }


def build_builtin_tools(tool_names: list[str] | None) -> list[Any]:
    if not tool_names:
        return []
    try:
        from superoptix.tools.builtin_tools import create_tool as superoptix_create_tool
    except Exception:
        return []

    tools: list[Any] = []
    for name in tool_names:
        try:
            tools.append(superoptix_create_tool(name))
        except Exception:
            continue
    return tools


def build_stackone_tools(dspy_tool_config: dict[str, Any] | None) -> list[Any]:
    if not isinstance(dspy_tool_config, dict):
        return []

    mode = str(dspy_tool_config.get("mode", "builtin")).strip().lower()
    stackone_cfg = dspy_tool_config.get("stackone", {})
    if not isinstance(stackone_cfg, dict):
        stackone_cfg = {}

    enabled = bool(stackone_cfg.get("enabled", mode in {"stackone", "stackone_discovery"}))
    if not enabled:
        return []
    if mode not in {"stackone", "stackone_discovery"} and not stackone_cfg:
        return []

    strict_mode = str(os.getenv("SUPEROPTIX_STACKONE_STRICT", "1")).strip().lower() not in {
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
        _emit_tool_trace("stackone", "dependencies unavailable")
        if strict_mode:
            raise RuntimeError(msg)
        return []

    api_key_env = str(stackone_cfg.get("api_key_env", "STACKONE_API_KEY")).strip()
    api_key = os.getenv(api_key_env)
    if not api_key:
        msg = f"⚠️ StackOne tools requested but {api_key_env} is not set."
        print(msg)
        _emit_tool_trace("stackone", f"missing env: {api_key_env}")
        if strict_mode:
            raise RuntimeError(msg)
        return []

    def _to_str_list(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
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

    base_url = stackone_cfg.get("base_url")
    discovery_mode = bool(stackone_cfg.get("discovery_mode", False)) or mode == "stackone_discovery"
    init_kwargs = {"api_key": api_key}
    if base_url:
        init_kwargs["base_url"] = str(base_url).strip()

    _emit_tool_trace(
        "stackone",
        "initializing connection",
        providers=providers or [],
        actions=actions or [],
        account_ids_count=len(account_ids or []),
        discovery_mode=bool(discovery_mode),
    )

    try:
        toolset = StackOneToolSet(**init_kwargs)
        _emit_tool_trace("stackone", "fetching tools")
        fetched_tools = toolset.fetch_tools(
            account_ids=account_ids or None,
            providers=providers or None,
            actions=actions or None,
        )
        fetched_count = len(fetched_tools or [])
        _emit_tool_trace("stackone", f"fetched {fetched_count} tools")

        if fetched_count == 0 and fallback_unfiltered and (providers or actions):
            _emit_tool_trace(
                "stackone",
                "no tools from filters; retrying without provider/action filters",
            )
            print("⚠️ StackOne returned 0 tools with current providers/actions filters; retrying unfiltered.")
            fetched_tools = toolset.fetch_tools(
                account_ids=account_ids or None,
                providers=None,
                actions=None,
            )
            fetched_count = len(fetched_tools or [])
            _emit_tool_trace("stackone", f"fallback fetched {fetched_count} tools")

        if fetched_count == 0:
            msg = (
                "⚠️ StackOne fetched 0 tools. Check STACKONE_ACCOUNT_IDS, provider/action filters, "
                "and whether the connector account is active."
            )
            print(msg)
            _emit_tool_trace("stackone", "fetched 0 tools")
            if strict_mode:
                raise RuntimeError(msg)

        # Build schema map from original StackOne tool objects (best effort).
        schema_keys_by_tool: dict[str, set[str]] = {}
        for st in fetched_tools or []:
            try:
                name = str(getattr(st, "name", "")).strip()
                props = (
                    ((st.parameters.model_dump() or {}).get("properties", {}))
                    if hasattr(st, "parameters")
                    else {}
                )
                if name:
                    schema_keys_by_tool[name] = set(props.keys()) if isinstance(props, dict) else set()
            except Exception:
                continue

        bridge = StackOneBridge(fetched_tools)
        tools = bridge.to_discovery_tools(framework="dspy") if discovery_mode else bridge.to_dspy()

        try:
            names = [getattr(t, "name", "") for t in (tools or [])]
            preview = ", ".join([n for n in names if n][:5])
            print(f"[StackOne] Loaded {len(tools or [])} DSPy tool(s)" + (f": {preview}" if preview else ""))
        except Exception:
            pass

        raw_func_by_name: dict[str, Any] = {}
        for t in tools or []:
            fn = getattr(t, "func", None)
            nm = getattr(t, "name", "")
            if callable(fn) and nm:
                raw_func_by_name[str(nm)] = fn
        current_user_cache: dict[str, Any] = {}

        def _extract_user_ctx(value: Any) -> dict[str, str]:
            out: dict[str, str] = {}
            if isinstance(value, dict):
                for key in ["uri", "user_uri", "id", "username", "timezone"]:
                    if key in value and isinstance(value[key], str):
                        out[key] = value[key]
                for nested_key in ["data", "user", "current_user", "response"]:
                    nested = value.get(nested_key)
                    if isinstance(nested, dict):
                        out.update(_extract_user_ctx(nested))
            return out

        def _calendly_retry_kwargs(name: str, kwargs: dict[str, Any]) -> tuple[dict[str, Any], str]:
            retry_kwargs = dict(kwargs or {})
            schema_keys = schema_keys_by_tool.get(name, set())
            now = datetime.now(timezone.utc)
            start = (now - timedelta(days=30)).isoformat().replace("+00:00", "Z")
            end = now.isoformat().replace("+00:00", "Z")

            # Add date windows if likely supported.
            key_pairs = [
                ("start_time", "end_time"),
                ("min_start_time", "max_start_time"),
                ("start", "end"),
                ("from", "to"),
                ("start_date", "end_date"),
            ]
            for a, b in key_pairs:
                if (a in schema_keys or b in schema_keys) and (a not in retry_kwargs and b not in retry_kwargs):
                    if a in schema_keys:
                        retry_kwargs[a] = start
                    if b in schema_keys:
                        retry_kwargs[b] = end
                    break

            for tz_key in ["timezone", "tz", "time_zone"]:
                if tz_key in schema_keys and tz_key not in retry_kwargs:
                    retry_kwargs[tz_key] = "UTC"

            for limit_key in ["count", "limit", "page_size", "per_page"]:
                if limit_key in schema_keys and limit_key not in retry_kwargs:
                    retry_kwargs[limit_key] = 3

            # Try user context if supported.
            if not current_user_cache:
                get_user_fn = raw_func_by_name.get("calendly_get_current_user")
                if callable(get_user_fn):
                    try:
                        current_user_cache.update(_extract_user_ctx(_run_with_timeout(get_user_fn, 10.0)))
                    except Exception:
                        pass
            user_uri = current_user_cache.get("uri") or current_user_cache.get("user_uri")
            for user_key in ["user", "user_uri", "uri"]:
                if user_key in schema_keys and user_key not in retry_kwargs and user_uri:
                    retry_kwargs[user_key] = user_uri
                    break

            return retry_kwargs, ",".join(sorted(retry_kwargs.keys()))

        instrumented: list[Any] = []
        for tool in tools or []:
            func = getattr(tool, "func", None)
            name = getattr(tool, "name", "stackone_tool")
            if not callable(func):
                instrumented.append(tool)
                continue

            def _wrapped(*args, __func=func, __name=name, **kwargs):
                arg_keys = sorted(list(kwargs.keys()))
                arg_preview = ",".join(arg_keys) if arg_keys else "-"
                _emit_tool_trace("tool:start", f"{__name} kwargs=[{arg_preview}]", args=len(args), kwargs=arg_keys)
                t0 = time.time()
                try:
                    timeout_sec = float(os.getenv("SUPEROPTIX_DSPY_TOOL_TIMEOUT_SEC", "20"))
                except (TypeError, ValueError):
                    timeout_sec = 20.0
                try:
                    out = _run_with_timeout(__func, timeout_sec, *args, **kwargs)
                    _emit_tool_trace("tool:ok", __name, latency_ms=int((time.time() - t0) * 1000))
                    return out
                except TimeoutError:
                    _emit_tool_trace(
                        "tool:error",
                        f"{__name} timeout>{timeout_sec}s",
                        latency_ms=int((time.time() - t0) * 1000),
                        error=f"timeout>{timeout_sec}s",
                    )
                    raise TimeoutError(f"Tool {__name} timed out after {timeout_sec}s")
                except Exception as exc:
                    err = str(exc).replace("\n", " ").strip()
                    if __name == "calendly_list_scheduled_events" and "400" in err:
                        retry_kwargs, key_preview = _calendly_retry_kwargs(__name, kwargs)
                        _emit_tool_trace("tool:retry", f"{__name} retry kwargs=[{key_preview}]")
                        try:
                            out = _run_with_timeout(__func, timeout_sec, *args, **retry_kwargs)
                            _emit_tool_trace("tool:ok", f"{__name} retry", latency_ms=int((time.time() - t0) * 1000))
                            return out
                        except Exception as retry_exc:
                            err = str(retry_exc).replace("\n", " ").strip()
                    if len(err) > 180:
                        err = err[:177] + "..."
                    _emit_tool_trace(
                        "tool:error",
                        f"{__name} error={err}",
                        latency_ms=int((time.time() - t0) * 1000),
                        error=str(exc),
                    )
                    raise

            try:
                setattr(tool, "func", _wrapped)
            except Exception:
                pass
            instrumented.append(tool)
        return instrumented
    except Exception as exc:
        print(f"⚠️ StackOne tool loading failed: {exc}")
        _emit_tool_trace("stackone", f"tool loading failed: {exc}")
        return []
