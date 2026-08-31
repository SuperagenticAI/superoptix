"""Runtime helpers for OpenAI Agents SDK generated pipelines."""

from __future__ import annotations

import inspect
import os
import re
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
    model = str(runtime_cfg.get("model") or lm_cfg.get("model") or "qwen3.5:9b").strip()
    api_base = runtime_cfg.get("api_base") or lm_cfg.get("api_base")

    # Allow pre-resolved model strings from callers.
    if model.startswith("litellm/"):
        return model

    # Accept provider-prefixed model formats like "openai:gpt-5.6-luna".
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


def _normalize_openai_sandbox_client(client: Any) -> str:
    value = str(client or "").strip().lower()
    if value in {"unix-local", "unixlocal"}:
        return "unix_local"
    if value in {"docker"}:
        return value
    return "unix_local"


def _normalize_manifest_entries(
    entries: Any, *, required_fields: tuple[str, ...]
) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    if not isinstance(entries, list):
        return normalized
    for item in entries:
        if not isinstance(item, dict):
            continue
        payload: Dict[str, str] = {}
        valid = True
        for field in required_fields:
            value = str(item.get(field, "") or "").strip()
            if not value:
                valid = False
                break
            payload[field] = value
        if not valid:
            continue
        optional_ref = str(item.get("ref", "") or "").strip()
        if optional_ref:
            payload["ref"] = optional_ref
        normalized.append(payload)
    return normalized


def get_openai_sandbox_config(spec_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Resolve OpenAI sandbox config from spec.openai_agent.sandbox."""
    spec = dict(spec_data or {})
    openai_cfg = spec.get("openai_agent")
    sandbox_cfg: Dict[str, Any] = {}
    if isinstance(openai_cfg, dict) and isinstance(openai_cfg.get("sandbox"), dict):
        sandbox_cfg = dict(openai_cfg.get("sandbox") or {})

    manifest_cfg = sandbox_cfg.get("manifest")
    if not isinstance(manifest_cfg, dict):
        manifest_cfg = {}

    return {
        "enabled": bool(sandbox_cfg.get("enabled", False)),
        "client": _normalize_openai_sandbox_client(
            sandbox_cfg.get("client", "unix_local")
        ),
        "docker_image": str(
            sandbox_cfg.get("docker_image", "python:3.14-slim") or "python:3.14-slim"
        ).strip(),
        "workflow_name": str(sandbox_cfg.get("workflow_name", "") or "").strip(),
        "manifest_root": str(manifest_cfg.get("root", "") or "").strip(),
        "manifest_local_dirs": _normalize_manifest_entries(
            manifest_cfg.get("local_dirs"), required_fields=("path", "src")
        ),
        "manifest_local_files": _normalize_manifest_entries(
            manifest_cfg.get("local_files"), required_fields=("path", "src")
        ),
        "manifest_git_repos": _normalize_manifest_entries(
            manifest_cfg.get("git_repos"), required_fields=("path", "url")
        ),
    }


def _parse_git_repo_url(url: str) -> tuple[str, str] | None:
    cleaned = str(url or "").strip()
    if not cleaned:
        return None

    # Accept https://host/owner/repo(.git), ssh://git@host/owner/repo(.git), git@host:owner/repo(.git)
    match = re.match(
        r"^(?:https?://|ssh://(?:[^@]+@)?|(?:[^@]+@))(?P<host>[^/:]+)[:/](?P<repo>.+?)(?:\.git)?/?$",
        cleaned,
    )
    if match:
        return match.group("host"), match.group("repo")

    # Accept host/owner/repo(.git)
    match = re.match(r"^(?P<host>[^/]+)/(?P<repo>.+?)(?:\.git)?/?$", cleaned)
    if match:
        return match.group("host"), match.group("repo")
    return None


def _build_openai_manifest_from_config(config: Dict[str, Any]) -> Any:
    try:
        from agents.sandbox import Manifest
        from agents.sandbox.entries import GitRepo, LocalDir, LocalFile
    except Exception:
        return None

    entries: Dict[str, Any] = {}
    for item in config.get("manifest_local_dirs", []):
        try:
            entries[str(item["path"])] = LocalDir(src=Path(item["src"]))
        except Exception as exc:
            print(f"⚠️ Skipping sandbox local_dir entry {item}: {exc}")
    for item in config.get("manifest_local_files", []):
        try:
            entries[str(item["path"])] = LocalFile(src=Path(item["src"]))
        except Exception as exc:
            print(f"⚠️ Skipping sandbox local_file entry {item}: {exc}")
    for item in config.get("manifest_git_repos", []):
        try:
            parsed = _parse_git_repo_url(item["url"])
            if parsed is None:
                raise ValueError(
                    "git_repos.url must be parseable as host/repo or a full git URL"
                )
            host, repo = parsed
            ref = str(item.get("ref", "main") or "main").strip() or "main"
            entries[str(item["path"])] = GitRepo(host=host, repo=repo, ref=ref)
        except Exception as exc:
            print(f"⚠️ Skipping sandbox git_repo entry {item}: {exc}")

    manifest_kwargs: Dict[str, Any] = {"entries": entries}
    root = str(config.get("manifest_root", "") or "").strip()
    if root:
        manifest_kwargs["root"] = root

    try:
        return Manifest(**manifest_kwargs)
    except Exception as exc:
        print(f"⚠️ Failed to build sandbox manifest; using SDK defaults. ({exc})")
        return None


def build_openai_agent(
    *,
    name: str,
    instructions: str,
    model: Any,
    tools: List[Any] | None,
    spec_data: Dict[str, Any] | None,
) -> Any:
    """Build Agent or SandboxAgent from OpenAI + sandbox config."""
    from agents import Agent

    sandbox_cfg = get_openai_sandbox_config(spec_data)
    if not sandbox_cfg.get("enabled", False):
        return Agent(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or [],
        )

    try:
        from agents.sandbox import SandboxAgent
    except Exception:
        print(
            "⚠️ openai_agent.sandbox.enabled=true but sandbox classes are unavailable. "
            "Install a newer openai-agents package (>=0.14.0). Falling back to Agent."
        )
        return Agent(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or [],
        )

    manifest = _build_openai_manifest_from_config(sandbox_cfg)
    return SandboxAgent(
        name=name,
        instructions=instructions,
        model=model,
        tools=tools or [],
        default_manifest=manifest,
    )


def build_openai_run_config(
    spec_data: Dict[str, Any] | None,
    *,
    default_workflow_name: str = "",
) -> Any | None:
    """Build RunConfig with SandboxRunConfig when sandbox mode is enabled."""
    sandbox_cfg = get_openai_sandbox_config(spec_data)
    if not sandbox_cfg.get("enabled", False):
        return None

    try:
        from agents.run import RunConfig
        from agents.sandbox import SandboxRunConfig
        from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient
    except Exception:
        print(
            "⚠️ openai_agent.sandbox.enabled=true but sandbox runtime imports failed. "
            "Install a newer openai-agents package (>=0.14.0)."
        )
        return None

    workflow_name = str(
        sandbox_cfg.get("workflow_name")
        or default_workflow_name
        or "SuperOptiX OpenAI run"
    ).strip()
    client_name = str(sandbox_cfg.get("client") or "unix_local").strip().lower()

    client: Any = None
    sandbox_options: Any = None
    if client_name == "docker":
        try:
            from docker import from_env as docker_from_env
            from agents.sandbox.sandboxes.docker import (
                DockerSandboxClient,
                DockerSandboxClientOptions,
            )

            client = DockerSandboxClient(docker_from_env())
            image = str(sandbox_cfg.get("docker_image") or "python:3.14-slim").strip()
            sandbox_options = DockerSandboxClientOptions(image=image)
        except Exception as exc:
            print(
                "⚠️ docker sandbox requested but Docker runtime is unavailable; "
                f"falling back to unix_local. ({exc})"
            )
            client = UnixLocalSandboxClient()
    else:
        client = UnixLocalSandboxClient()

    sandbox_kwargs: Dict[str, Any] = {"client": client}
    if sandbox_options is not None:
        sandbox_kwargs["options"] = sandbox_options

    return RunConfig(
        sandbox=SandboxRunConfig(**sandbox_kwargs),
        workflow_name=workflow_name,
    )
