"""OpenAI Agents SDK backend for SuperOptiX harness sessions."""

from __future__ import annotations

from typing import Any

from superoptix.harness.tools import HarnessTool, to_openai_tools
from superoptix.harness.types import HarnessRunResult
from superoptix.runners.openai_runtime_helpers import (
    build_openai_agent,
    build_openai_run_config,
    resolve_model,
)


class OpenAIHarnessBackend:
    """Run harness turns through OpenAI Agents SDK."""

    name = "openai"

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
        try:
            from agents import Runner
        except Exception as exc:
            raise ImportError(
                "OpenAI harness backend requires openai-agents. "
                "Install with: pip install 'superoptix[frameworks-openai]'."
            ) from exc

        spec = _with_system_prompt(spec_data, system_prompt)
        resolved_model = model or resolve_model(
            spec.get("language_model", {}) or {},
            model_config=model_config,
        )
        agent = build_openai_agent(
            name=agent_name,
            instructions=system_prompt,
            model=resolved_model,
            tools=to_openai_tools(tools or []),
            spec_data=spec,
        )
        run_config = build_openai_run_config(
            spec,
            default_workflow_name=f"SuperOptiX harness run ({agent_name})",
        )
        kwargs: dict[str, Any] = {}
        if run_config is not None:
            kwargs["run_config"] = run_config

        result = await Runner.run(agent, input=prompt, **kwargs)
        text = str(getattr(result, "final_output", result) or "").strip()
        return HarnessRunResult(
            text=text,
            raw=result,
            metadata={"framework": self.name, "model": resolved_model},
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
