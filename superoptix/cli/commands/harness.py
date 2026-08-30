"""CLI commands for the SuperOptiX-native harness runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from superoptix.harness import (
    FileSessionStore,
    HarnessAgent,
    HarnessContext,
    create_harness_app,
    discover_context,
)


console = Console()


async def run_harness_agent(args) -> None:
    """Run a stateful harness session for one SuperOptiX agent."""
    prompt = str(getattr(args, "prompt", "") or "").strip()
    if not prompt and not getattr(args, "skill", None):
        console.print(
            "[bold red]❌ Provide --prompt/--goal or --skill for harness run.[/]"
        )
        return

    agent = _create_harness_agent(args)
    if agent is None:
        return

    session = await agent.session(
        str(getattr(args, "session", "default") or "default"),
        role=getattr(args, "role", None),
    )
    skill_name = getattr(args, "skill", None)
    if skill_name:
        result = await session.skill(
            str(skill_name),
            args=_parse_key_value_args(getattr(args, "arg", None)),
            role=getattr(args, "role", None),
        )
    else:
        result = await session.prompt(prompt, role=getattr(args, "role", None))

    payload = {
        "agent": args.name,
        "session": getattr(args, "session", "default"),
        "backend": agent.backend.name,
        "text": result.text,
        "metadata": result.metadata,
    }
    if getattr(args, "json", False):
        console.print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        console.print(result.text)


def serve_harness_agent(args) -> None:
    """Serve a stateful harness agent over HTTP."""
    agent = _create_harness_agent(args)
    if agent is None:
        return

    try:
        import uvicorn
    except Exception as exc:
        raise ImportError(
            "Harness serve requires uvicorn. Install with: pip install 'superoptix[web]'."
        ) from exc

    app = create_harness_app(agent)
    public_host = args.host
    if public_host in {"0.0.0.0", "::"}:
        public_host = "127.0.0.1"
    url = f"http://{public_host}:{args.port}"
    console.print(
        f"🚀 [bold cyan]Serving harness agent '[yellow]{args.name}[/]' "
        f"with backend [yellow]{agent.backend.name}[/]"
    )
    console.print(f"[dim]Endpoint:[/] {url}/agents/{args.name}/<session_id>")
    console.print()
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)


def _create_harness_agent(args) -> HarnessAgent | None:
    project_root = Path.cwd()
    project_name = _load_project_name(project_root)
    if not project_name:
        return None

    agent_name = str(args.name).strip().lower().replace("-", "_")
    playbook = _load_harness_playbook(project_root, project_name, agent_name)
    if playbook is None:
        return None

    cwd = _resolve_cwd(project_root, getattr(args, "cwd", None))
    discovered = discover_context(cwd)
    system_prompt = _merge_prompts(
        discovered.system_prompt,
        _build_playbook_system_prompt(playbook),
    )
    context = HarnessContext(
        cwd=discovered.cwd,
        system_prompt=system_prompt,
        skills=discovered.skills,
        roles=discovered.roles,
    )
    state_dir = _resolve_state_dir(
        project_root, agent_name, getattr(args, "state_dir", None)
    )
    spec_data = _build_spec_data(playbook)

    return HarnessAgent(
        name=agent_name,
        cwd=cwd,
        backend=getattr(args, "backend", "openai"),
        model=None,
        model_config=_build_model_config(args),
        spec_data=spec_data,
        context=context,
        store=FileSessionStore(state_dir),
        enable_tools=(
            not bool(getattr(args, "no_tools", False))
            and str(getattr(args, "backend", "")).strip().lower() != "codex"
        ),
        allow_write=bool(getattr(args, "allow_write", False)),
        allow_shell=bool(getattr(args, "allow_shell", False)),
    )


def _load_project_name(project_root: Path) -> str | None:
    super_file = project_root / ".super"
    if not super_file.exists():
        console.print(
            "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
        )
        return None
    with super_file.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    project_name = config.get("project")
    if not project_name:
        console.print("[bold red]❌ .super is missing a project name.[/]")
        return None
    return str(project_name)


def _load_harness_playbook(
    project_root: Path,
    project_name: str,
    agent_name: str,
) -> dict[str, Any] | None:
    playbook_path = _find_harness_playbook(project_root, project_name, agent_name)
    if playbook_path is None:
        console.print(
            f"[bold red]❌ Playbook for agent '{agent_name}' not found.[/]\n"
            f"[cyan]Try:[/] super agent pull {agent_name}"
        )
        return None
    with playbook_path.open("r", encoding="utf-8") as handle:
        playbook = yaml.safe_load(handle) or {}
    if not isinstance(playbook, dict):
        console.print(f"[bold red]❌ Invalid playbook: {playbook_path}[/]")
        return None
    return playbook


def _find_harness_playbook(
    project_root: Path,
    project_name: str,
    agent_name: str,
) -> Path | None:
    agents_dir = project_root / project_name / "agents"
    if not agents_dir.exists():
        return None
    return next(agents_dir.rglob(f"**/{agent_name}_playbook.yaml"), None)


def _build_spec_data(playbook: dict[str, Any]) -> dict[str, Any]:
    spec = dict(playbook.get("spec", {}) or {})
    metadata = playbook.get("metadata", {}) or {}
    if isinstance(metadata, dict):
        spec["metadata"] = dict(metadata)
    return spec


def _build_playbook_system_prompt(playbook: dict[str, Any]) -> str:
    metadata = playbook.get("metadata", {}) or {}
    spec = playbook.get("spec", {}) or {}
    persona = spec.get("persona", {}) if isinstance(spec, dict) else {}
    if isinstance(persona, str):
        persona = {"instructions": persona}
    elif not isinstance(persona, dict):
        persona = {}

    parts: list[str] = []
    description = str(metadata.get("description", "") or "").strip()
    if description:
        parts.append(f"Agent description: {description}")

    for label, key in [
        ("Role", "role"),
        ("Goal", "goal"),
        ("Backstory", "backstory"),
        ("Instructions", "instructions"),
    ]:
        value = str(persona.get(key, "") or "").strip()
        if value:
            parts.append(f"{label}:\n{value}")

    tasks = spec.get("tasks", []) if isinstance(spec, dict) else []
    if isinstance(tasks, list) and tasks:
        task_parts = []
        for index, task in enumerate(tasks, start=1):
            if isinstance(task, dict):
                instruction = str(task.get("instruction", "") or "").strip()
                if instruction:
                    task_parts.append(f"{index}. {instruction}")
        if task_parts:
            parts.append("Tasks:\n" + "\n".join(task_parts))

    constraints = spec.get("constraints", []) if isinstance(spec, dict) else []
    if isinstance(constraints, list) and constraints:
        parts.append("Constraints:\n" + "\n".join(f"- {item}" for item in constraints))

    return "\n\n".join(parts).strip() or "You are a helpful AI assistant."


def _merge_prompts(*parts: str) -> str:
    return "\n\n".join(str(part).strip() for part in parts if str(part).strip())


def _resolve_cwd(project_root: Path, cwd: str | None) -> Path:
    if not cwd:
        return project_root
    path = Path(cwd).expanduser()
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def _resolve_state_dir(
    project_root: Path,
    agent_name: str,
    state_dir: str | None,
) -> Path:
    if state_dir:
        path = Path(state_dir).expanduser()
        if not path.is_absolute():
            path = project_root / path
        return path.resolve()
    return project_root / ".superoptix" / "harness" / "sessions" / agent_name


def _build_model_config(args) -> dict[str, Any]:
    config: dict[str, Any] = {}
    if getattr(args, "provider", None):
        config["provider"] = args.provider
    if getattr(args, "model", None):
        config["model"] = args.model
    if getattr(args, "codex_bin", None):
        config["codex_bin"] = args.codex_bin
    pydantic_usage_limits = {
        "request_limit": getattr(args, "pydantic_request_limit", None),
        "tool_calls_limit": getattr(args, "pydantic_tool_calls_limit", None),
        "input_tokens_limit": getattr(args, "pydantic_input_tokens_limit", None),
        "output_tokens_limit": getattr(args, "pydantic_output_tokens_limit", None),
        "total_tokens_limit": getattr(args, "pydantic_total_tokens_limit", None),
    }
    if getattr(args, "pydantic_count_tokens_before_request", False):
        pydantic_usage_limits["count_tokens_before_request"] = True
    pydantic_usage_limits = {
        key: value for key, value in pydantic_usage_limits.items() if value is not None
    }
    if pydantic_usage_limits:
        config["pydantic_usage_limits"] = pydantic_usage_limits
    if getattr(args, "pydantic_code_mode", False):
        config["pydantic_code_mode"] = True
    deepagents_config: dict[str, Any] = {}
    if getattr(args, "deepagents_skill_source", None):
        deepagents_config["skills"] = list(args.deepagents_skill_source)
    if getattr(args, "deepagents_memory", None):
        deepagents_config["memory"] = list(args.deepagents_memory)
    if getattr(args, "deepagents_checkpointer", None):
        deepagents_config["checkpointer"] = args.deepagents_checkpointer
    if getattr(args, "deepagents_debug", False):
        deepagents_config["debug"] = True
    if deepagents_config:
        config["deepagents"] = deepagents_config
    if getattr(args, "local", False):
        config.setdefault("provider", "ollama")
        config.setdefault("model", "qwen3.5:9b")
    return config


def _parse_key_value_args(raw_args: list[str] | None) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in raw_args or []:
        if "=" not in item:
            raise ValueError(f"Skill arguments must use key=value format: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Skill argument has an empty key: {item}")
        parsed[key] = _parse_scalar(value.strip())
    return parsed


def _parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value
