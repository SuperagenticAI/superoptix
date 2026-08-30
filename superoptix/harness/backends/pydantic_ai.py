"""Pydantic AI backend for SuperOptiX harness sessions."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from superoptix.harness.tools import HarnessTool, to_pydantic_ai_tools
from superoptix.harness.types import HarnessRunResult
from superoptix.runners.pydantic_runtime_helpers import (
    build_stackone_tools,
    resolve_model,
    run_agent_with_optional_rlm,
)


class PydanticAIHarnessBackend:
    """Run harness turns through Pydantic AI."""

    name = "pydantic_ai"

    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        agent_name: str,
        cwd: Path | None = None,
        sandbox: Any | None = None,
        model: str | None = None,
        model_config: dict[str, Any] | None = None,
        spec_data: dict[str, Any] | None = None,
        tools: list[HarnessTool] | None = None,
    ) -> HarnessRunResult:
        _ = cwd, sandbox
        try:
            from pydantic_ai import Agent
        except Exception as exc:
            raise ImportError(
                "Pydantic AI harness backend requires pydantic-ai. "
                "Install with: pip install 'superoptix[frameworks-pydantic-ai]'."
            ) from exc

        spec = _with_system_prompt(spec_data, system_prompt)
        language_model = spec.get("language_model", {}) or {}
        resolved_model = model or resolve_model(
            language_model,
            model_config=model_config,
        )

        pydantic_tools = [
            *to_pydantic_ai_tools(tools or []),
            *build_stackone_tools(spec, framework="pydantic_ai"),
        ]
        agent_kwargs = _build_agent_capability_kwargs(
            model_config=model_config,
            agent_cls=Agent,
        )
        agent = Agent(
            resolved_model,
            instructions=system_prompt or None,
            name=agent_name,
            tools=pydantic_tools,
            **agent_kwargs,
        )
        run_kwargs = _build_run_kwargs(model_config)
        result = await run_agent_with_optional_rlm(
            agent=agent,
            prompt=prompt,
            spec_data=spec,
            model_name=resolved_model,
            logfire_enabled=bool((spec.get("logfire", {}) or {}).get("enabled", True)),
            run_kwargs=run_kwargs,
        )
        return HarnessRunResult(
            text=_extract_text(result),
            raw=result,
            metadata={
                "framework": self.name,
                "model": resolved_model,
                "tool_count": len(pydantic_tools),
                "usage_limits": bool(run_kwargs.get("usage_limits")),
                "capability_count": len(agent_kwargs.get("capabilities", [])),
            },
        )


def _with_system_prompt(
    spec_data: dict[str, Any] | None,
    system_prompt: str,
) -> dict[str, Any]:
    spec = dict(spec_data or {})
    persona = dict(spec.get("persona", {}) or {})
    persona["instructions"] = system_prompt
    spec["persona"] = persona
    return spec


def _extract_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result.strip()
    for attr in ("output", "data", "final_output", "content", "text"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            if value is not None:
                return str(value).strip()
    if isinstance(result, dict):
        for key in ("output", "data", "final_output", "content", "text"):
            if key in result and result[key] is not None:
                return str(result[key]).strip()
    return str(result).strip()


def _build_run_kwargs(model_config: dict[str, Any] | None) -> dict[str, Any]:
    usage_limits = _build_usage_limits(model_config)
    if usage_limits is None:
        return {}
    return {"usage_limits": usage_limits}


def _build_usage_limits(model_config: dict[str, Any] | None) -> Any | None:
    cfg = dict(model_config or {})
    raw_limits = cfg.get("pydantic_usage_limits")
    if not isinstance(raw_limits, dict):
        raw_limits = {}

    limit_keys = {
        "request_limit",
        "tool_calls_limit",
        "input_tokens_limit",
        "output_tokens_limit",
        "total_tokens_limit",
        "count_tokens_before_request",
        "request_tokens_limit",
        "response_tokens_limit",
    }
    limits = {
        key: raw_limits[key] for key in limit_keys if raw_limits.get(key) is not None
    }
    if not limits:
        return None

    try:
        from pydantic_ai.usage import UsageLimits
    except Exception as exc:
        raise ImportError(
            "Pydantic AI usage limits require pydantic_ai.usage. "
            "Upgrade pydantic-ai or remove the Pydantic limit flags."
        ) from exc

    return UsageLimits(**limits)


def _build_agent_capability_kwargs(
    *,
    model_config: dict[str, Any] | None,
    agent_cls: Any,
) -> dict[str, Any]:
    cfg = dict(model_config or {})
    if not bool(cfg.get("pydantic_code_mode", False)):
        return {}

    if "capabilities" not in inspect.signature(agent_cls).parameters:
        raise ImportError(
            "Pydantic AI CodeMode was requested, but the installed pydantic-ai "
            "Agent API does not expose capabilities. Upgrade to a compatible "
            "Pydantic AI release once capability support is available, or remove "
            "--pydantic-code-mode."
        )

    try:
        from pydantic_ai_harness import CodeMode
    except Exception as exc:
        raise ImportError(
            "Pydantic AI CodeMode requires the optional pydantic-ai-harness "
            "package. Install a compatible release or remove --pydantic-code-mode."
        ) from exc

    return {"capabilities": [CodeMode()]}
