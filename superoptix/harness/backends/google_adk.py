"""Google ADK backend for SuperOptiX harness sessions."""

from __future__ import annotations

from typing import Any

from superoptix.harness.tools import HarnessTool, to_google_adk_tools
from superoptix.harness.types import HarnessRunResult
from superoptix.runners.google_adk_runtime_helpers import (
    create_agent_runner,
    run_agent_with_optional_rlm,
)


class GoogleADKHarnessBackend:
    """Run harness turns through Google ADK."""

    name = "google_adk"

    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        agent_name: str,
        cwd: Any | None = None,
        sandbox: Any | None = None,
        model: str | None = None,
        model_config: dict[str, Any] | None = None,
        spec_data: dict[str, Any] | None = None,
        tools: list[HarnessTool] | None = None,
    ) -> HarnessRunResult:
        _ = cwd, sandbox
        spec = _with_system_prompt(spec_data, system_prompt)
        effective_model_config = dict(model_config or {})
        if model:
            effective_model_config["model"] = model

        agent, runner, runtime = create_agent_runner(
            spec_data=spec,
            agent_name=agent_name,
            model_config=effective_model_config or None,
            extra_tools=to_google_adk_tools(tools or []),
        )
        text = await run_agent_with_optional_rlm(
            agent=agent,
            runner=runner,
            prompt=prompt,
            spec_data=spec,
            model_name=str(runtime.get("model", "")),
            app_name=str(runtime.get("app_name", "superoptix_agent")),
            logfire_enabled=bool((spec.get("logfire", {}) or {}).get("enabled", True)),
        )
        return HarnessRunResult(
            text=str(text or "").strip(),
            raw=text,
            metadata={
                "framework": self.name,
                "model": runtime.get("model"),
                "app_name": runtime.get("app_name"),
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
