"""Shared DSPy runtime helpers used by generated SuperOptiX pipelines.

Keeps generated pipeline code minimal by centralizing:
- Structured output coercion
- Assertion checks
- Built-in tool loading
"""

from __future__ import annotations

import json
import re
import threading
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
        processed[field] = _coerce_value(
            processed[field], field_types.get(field, "str")
        )
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
            errors.append(
                f"Field '{field}' exceeds max_length={limit} (got {len(value)})"
            )
            checks_failed += 1
        elif (
            isinstance(value, (list, tuple, dict, set))
            and isinstance(limit, int)
            and len(value) > limit
        ):
            errors.append(
                f"Field '{field}' exceeds max_length={limit} (got {len(value)})"
            )
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
                    errors.append(
                        f"Field '{field}' did not match required regex pattern"
                    )
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
