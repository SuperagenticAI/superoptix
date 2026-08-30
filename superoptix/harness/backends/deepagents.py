"""DeepAgents backend for SuperOptiX harness sessions."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from superoptix.harness.sandbox import LocalSandbox
from superoptix.harness.tools import HarnessTool, to_deepagents_tools
from superoptix.harness.types import HarnessRunResult


class DeepAgentsHarnessBackend:
    """Run harness turns through DeepAgents."""

    name = "deepagents"

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
        _ = cwd
        try:
            from deepagents import create_deep_agent
        except Exception as exc:
            raise ImportError(
                "DeepAgents harness backend requires deepagents>=0.5.6. "
                "Install with: pip install 'superoptix[frameworks-deepagents]'."
            ) from exc

        resolved_model = _resolve_model(model, model_config, spec_data)
        backend = (
            _create_deepagents_backend(sandbox)
            if isinstance(sandbox, LocalSandbox)
            else None
        )
        config = _resolve_deepagents_config(
            model_config=model_config,
            spec_data=spec_data,
            cwd=cwd,
            sandbox=sandbox,
        )

        agent = create_deep_agent(
            model=resolved_model,
            tools=to_deepagents_tools(tools or []),
            system_prompt=system_prompt or None,
            backend=backend,
            name=agent_name,
            skills=config["skills"],
            memory=config["memory"],
            permissions=config["permissions"],
            subagents=config["subagents"],
            interrupt_on=config["interrupt_on"],
            response_format=config["response_format"],
            checkpointer=config["checkpointer"],
            debug=config["debug"],
        )

        inputs = {"messages": [{"role": "user", "content": prompt}]}
        runnable_config = _build_runnable_config(agent_name=agent_name, config=config)
        if hasattr(agent, "ainvoke"):
            result = await agent.ainvoke(inputs, config=runnable_config)
        else:
            result = await asyncio.to_thread(
                agent.invoke, inputs, config=runnable_config
            )

        text = _extract_text(result)
        return HarnessRunResult(
            text=text,
            raw=result,
            metadata={
                "framework": self.name,
                "model": resolved_model,
                "sandbox": "local" if backend is not None else "state",
                "skill_sources": config["skills"],
                "memory_sources": config["memory"],
                "subagent_count": len(config["subagents"] or []),
                "checkpointer": config["checkpointer_name"],
                "debug": config["debug"],
            },
        )


def _resolve_model(
    model: str | None,
    model_config: dict[str, Any] | None,
    spec_data: dict[str, Any] | None,
) -> str | None:
    if model:
        return model
    config = dict(model_config or {})
    configured_model = config.get("model")
    provider = config.get("provider")
    if provider and configured_model and ":" not in str(configured_model):
        return f"{provider}:{configured_model}"
    if configured_model:
        return str(configured_model)

    language_model = (spec_data or {}).get("language_model", {}) or {}
    if isinstance(language_model, dict):
        provider = language_model.get("provider")
        name = language_model.get("model") or language_model.get("name")
        if provider and name:
            return f"{provider}:{name}" if ":" not in str(name) else str(name)
        if name:
            return str(name)
    return None


def _create_deepagents_backend(sandbox: LocalSandbox) -> Any:
    from deepagents.backends.protocol import (
        EditResult,
        ExecuteResponse,
        FileDownloadResponse,
        FileUploadResponse,
        GlobResult,
        GrepResult,
        LsResult,
        ReadResult,
        SandboxBackendProtocol,
        WriteResult,
    )

    class SuperOptiXDeepAgentsBackend(SandboxBackendProtocol):
        @property
        def id(self) -> str:
            return f"superoptix-local:{sandbox.root}"

        def ls(self, path: str) -> Any:
            try:
                target = sandbox.resolve(_from_backend_path(path))
                if target.is_file():
                    entries = [_file_info(target)]
                else:
                    entries = [_file_info(child) for child in sorted(target.iterdir())]
                return LsResult(entries=entries)
            except Exception as exc:
                return LsResult(error=str(exc))

        def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> Any:
            try:
                content = sandbox.read(
                    _from_backend_path(file_path),
                    offset=offset + 1,
                    limit=limit,
                )
                return ReadResult(file_data={"content": content, "encoding": "utf-8"})
            except Exception as exc:
                return ReadResult(error=str(exc))

        def write(self, file_path: str, content: str) -> Any:
            try:
                target = sandbox.resolve(
                    _from_backend_path(file_path), must_exist=False
                )
                if target.exists():
                    return WriteResult(error=f"File already exists: {file_path}")
                sandbox.write(_from_backend_path(file_path), content)
                return WriteResult(path=_to_backend_path(target))
            except Exception as exc:
                return WriteResult(error=str(exc))

        def edit(
            self,
            file_path: str,
            old_string: str,
            new_string: str,
            replace_all: bool = False,
        ) -> Any:
            try:
                target = sandbox.resolve(_from_backend_path(file_path))
                occurrences = target.read_text(
                    encoding="utf-8", errors="replace"
                ).count(old_string)
                sandbox.edit(
                    _from_backend_path(file_path),
                    old_string,
                    new_string,
                    replace_all=replace_all,
                )
                return EditResult(
                    path=_to_backend_path(target),
                    occurrences=occurrences if replace_all else min(occurrences, 1),
                )
            except Exception as exc:
                return EditResult(error=str(exc))

        def grep(
            self,
            pattern: str,
            path: str | None = None,
            glob: str | None = None,
        ) -> Any:
            try:
                output = sandbox.grep(
                    pattern,
                    path=_from_backend_path(path or "/"),
                    include=glob,
                )
                return GrepResult(matches=_parse_grep_matches(output))
            except Exception as exc:
                return GrepResult(error=str(exc))

        def glob(self, pattern: str, path: str = "/") -> Any:
            try:
                search = _join_backend_glob(path, pattern)
                output = sandbox.glob(search)
                matches = []
                for line in output.splitlines():
                    if not line or line.startswith("("):
                        continue
                    target = sandbox.resolve(line)
                    matches.append(_file_info(target))
                return GlobResult(matches=matches)
            except Exception as exc:
                return GlobResult(error=str(exc))

        def execute(self, command: str, *, timeout: int | None = None) -> Any:
            try:
                result = sandbox.bash(command, timeout=timeout)
                output = "\n".join(
                    part
                    for part in [result.get("stdout", ""), result.get("stderr", "")]
                    if part
                )
                return ExecuteResponse(
                    output=output.strip(),
                    exit_code=result.get("exit_code"),
                    truncated=False,
                )
            except Exception as exc:
                return ExecuteResponse(output=str(exc), exit_code=-1, truncated=False)

        def upload_files(self, files: list[tuple[str, bytes]]) -> Any:
            responses = []
            for path, content in files:
                try:
                    sandbox.write(
                        _from_backend_path(path),
                        content.decode("utf-8", errors="replace"),
                    )
                    responses.append(FileUploadResponse(path=path))
                except Exception as exc:
                    responses.append(FileUploadResponse(path=path, error=str(exc)))
            return responses

        def download_files(self, paths: list[str]) -> Any:
            responses = []
            for path in paths:
                try:
                    target = sandbox.resolve(_from_backend_path(path))
                    responses.append(
                        FileDownloadResponse(path=path, content=target.read_bytes())
                    )
                except Exception as exc:
                    responses.append(FileDownloadResponse(path=path, error=str(exc)))
            return responses

    def _file_info(path: Path) -> dict[str, Any]:
        return {
            "path": _to_backend_path(path),
            "is_dir": path.is_dir(),
            "size": 0 if path.is_dir() else path.stat().st_size,
        }

    def _to_backend_path(path: Path) -> str:
        rel = sandbox.relative(path)
        return "/" if rel in {"", "."} else "/" + rel

    return SuperOptiXDeepAgentsBackend()


def _resolve_deepagents_config(
    *,
    model_config: dict[str, Any] | None,
    spec_data: dict[str, Any] | None,
    cwd: Path | None,
    sandbox: Any | None,
) -> dict[str, Any]:
    merged = _deepagents_section(spec_data)
    merged.update(dict((model_config or {}).get("deepagents", {}) or {}))

    skill_sources = _as_str_list(merged.get("skills"))
    if not skill_sources:
        skill_sources = _default_skill_sources(cwd)

    memory_sources = _as_str_list(merged.get("memory"))
    if not memory_sources:
        memory_sources = _default_memory_sources(cwd)

    permissions = _build_permissions(
        raw_permissions=merged.get("permissions"),
        sandbox=sandbox,
    )
    checkpointer, checkpointer_name = _build_checkpointer(merged.get("checkpointer"))

    return {
        "skills": skill_sources or None,
        "memory": memory_sources or None,
        "permissions": permissions,
        "subagents": _as_subagents(merged.get("subagents")),
        "interrupt_on": _as_interrupt_on(merged.get("interrupt_on")),
        "response_format": merged.get("response_format"),
        "checkpointer": checkpointer,
        "checkpointer_name": checkpointer_name,
        "debug": bool(merged.get("debug", False)),
        "thread_id": str(merged.get("thread_id", "") or "").strip(),
    }


def _deepagents_section(spec_data: dict[str, Any] | None) -> dict[str, Any]:
    spec = dict(spec_data or {})
    section = spec.get("deepagents")
    if isinstance(section, dict):
        return dict(section)
    section = spec.get("deep_agents")
    if isinstance(section, dict):
        return dict(section)
    return {}


def _default_skill_sources(cwd: Path | None) -> list[str]:
    if cwd is None:
        return []
    sources: list[str] = []
    for candidate in [cwd / ".agents" / "skills", cwd / "skills"]:
        if candidate.exists():
            sources.append(_workspace_path(cwd, candidate))
    return sources


def _default_memory_sources(cwd: Path | None) -> list[str]:
    if cwd is None:
        return []
    sources: list[str] = []
    for candidate in [cwd / "AGENTS.md", cwd / "CLAUDE.md"]:
        if candidate.exists():
            sources.append(_workspace_path(cwd, candidate))
    return sources


def _workspace_path(root: Path, path: Path) -> str:
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    return "/" + rel if rel else "/"


def _build_permissions(
    *,
    raw_permissions: Any,
    sandbox: Any | None,
) -> Any:
    try:
        from deepagents import FilesystemPermission
    except Exception:
        return None

    if isinstance(raw_permissions, list):
        rules = []
        for item in raw_permissions:
            if not isinstance(item, dict):
                continue
            operations = _as_str_list(item.get("operations"))
            paths = _as_str_list(item.get("paths"))
            mode = str(item.get("mode", "allow") or "allow")
            if operations and paths:
                rules.append(
                    FilesystemPermission(
                        operations=operations,
                        paths=paths,
                        mode=mode,
                    )
                )
        if rules:
            return rules

    if not isinstance(sandbox, LocalSandbox):
        return None

    if sandbox.policy.allow_write:
        return [
            FilesystemPermission(operations=["read", "write"], paths=["/**"]),
        ]
    return [
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        FilesystemPermission(operations=["read"], paths=["/**"]),
    ]


def _build_checkpointer(raw: Any) -> tuple[Any, str | None]:
    if raw in {None, False, "none", "false", "off"}:
        return None, None
    if raw in {True, "memory", "inmemory", "in_memory"}:
        # Let DeepAgents own the concrete checkpoint implementation. SuperOptiX
        # only asks for DeepAgents-managed in-memory session state here.
        return True, "deepagents-memory"
    return raw, type(raw).__name__


def _as_subagents(raw: Any) -> list[dict[str, Any]] | None:
    if not isinstance(raw, list):
        return None
    subagents = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "") or "").strip()
        description = str(item.get("description", "") or "").strip()
        system_prompt = str(item.get("system_prompt", "") or "").strip()
        if name and description and system_prompt:
            subagent = dict(item)
            subagent["name"] = name
            subagent["description"] = description
            subagent["system_prompt"] = system_prompt
            subagents.append(subagent)
    return subagents or None


def _as_interrupt_on(raw: Any) -> dict[str, Any] | None:
    return dict(raw) if isinstance(raw, dict) and raw else None


def _as_str_list(raw: Any) -> list[str]:
    if isinstance(raw, str):
        value = raw.strip()
        return [value] if value else []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def _build_runnable_config(
    *, agent_name: str, config: dict[str, Any]
) -> dict[str, Any]:
    thread_id = config.get("thread_id") or agent_name
    return {"configurable": {"thread_id": thread_id}}


def _from_backend_path(path: str | None) -> str:
    raw = str(path or "/").strip() or "/"
    if raw in {"/", "/workspace"}:
        return "."
    if raw.startswith("/workspace/"):
        return raw.removeprefix("/workspace/")
    if raw.startswith("/"):
        return raw[1:]
    return raw


def _join_backend_glob(path: str, pattern: str) -> str:
    base = _from_backend_path(path)
    if base == ".":
        return pattern.lstrip("/")
    return f"{base.rstrip('/')}/{pattern.lstrip('/')}"


def _parse_grep_matches(output: str) -> list[dict[str, Any]]:
    matches = []
    for line in output.splitlines():
        if not line or line.startswith("(") or line.startswith("["):
            continue
        path, sep, rest = line.partition(":")
        line_no, sep2, text = rest.partition(":")
        if not sep or not sep2:
            continue
        try:
            number = int(line_no)
        except ValueError:
            continue
        matches.append({"path": "/" + path.lstrip("/"), "line": number, "text": text})
    return matches


def _extract_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result.strip()
    if isinstance(result, dict):
        messages = result.get("messages")
        if isinstance(messages, list) and messages:
            return _message_text(messages[-1]).strip()
        for key in ("output", "final_output", "content", "text"):
            if key in result:
                return _extract_text(result[key])
    return _message_text(result).strip()


def _message_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)
    return str(content or "")
