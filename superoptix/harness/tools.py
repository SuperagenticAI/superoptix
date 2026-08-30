"""Built-in model-callable tools for the SuperOptiX harness."""

from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from superoptix.harness.sandbox import LocalSandbox


ToolExecute = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class HarnessTool:
    """Framework-neutral tool definition."""

    name: str
    description: str
    parameters: dict[str, Any]
    execute: ToolExecute


def create_builtin_tools(sandbox: LocalSandbox) -> list[HarnessTool]:
    """Create built-in file/search/shell tools from a sandbox policy."""
    tools = [
        HarnessTool(
            name="read",
            description="Read a file or list a directory inside the sandbox workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path.",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Optional 1-indexed starting line for files.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional maximum number of lines.",
                    },
                },
                "required": ["path"],
            },
            execute=lambda args: sandbox.read(
                str(args.get("path", "")),
                offset=args.get("offset"),
                limit=args.get("limit"),
            ),
        ),
        HarnessTool(
            name="grep",
            description="Search files inside the sandbox workspace with a regex pattern.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern."},
                    "path": {
                        "type": "string",
                        "description": "File or directory to search. Defaults to '.'.",
                    },
                    "include": {
                        "type": "string",
                        "description": "Optional glob filter such as '*.py'.",
                    },
                },
                "required": ["pattern"],
            },
            execute=lambda args: sandbox.grep(
                str(args.get("pattern", "")),
                path=str(args.get("path") or "."),
                include=args.get("include"),
            ),
        ),
        HarnessTool(
            name="glob",
            description="List files matching a glob pattern inside the sandbox workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern, for example '**/*.py'.",
                    }
                },
                "required": ["pattern"],
            },
            execute=lambda args: sandbox.glob(str(args.get("pattern", ""))),
        ),
    ]

    if sandbox.policy.allow_write:
        tools.extend(
            [
                HarnessTool(
                    name="write",
                    description="Write a file inside the sandbox workspace.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                    },
                    execute=lambda args: sandbox.write(
                        str(args.get("path", "")),
                        str(args.get("content", "")),
                    ),
                ),
                HarnessTool(
                    name="edit",
                    description=(
                        "Edit a file by exact text replacement. old_text must match "
                        "a unique region unless replace_all is true."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "old_text": {"type": "string"},
                            "new_text": {"type": "string"},
                            "replace_all": {"type": "boolean"},
                        },
                        "required": ["path", "old_text", "new_text"],
                    },
                    execute=lambda args: sandbox.edit(
                        str(args.get("path", "")),
                        str(args.get("old_text", "")),
                        str(args.get("new_text", "")),
                        replace_all=bool(args.get("replace_all", False)),
                    ),
                ),
            ]
        )

    if sandbox.policy.allow_shell:
        tools.append(
            HarnessTool(
                name="bash",
                description="Run a shell command inside the sandbox workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds.",
                        },
                    },
                    "required": ["command"],
                },
                execute=lambda args: json.dumps(
                    sandbox.bash(
                        str(args.get("command", "")),
                        timeout=args.get("timeout"),
                    ),
                    sort_keys=True,
                ),
            )
        )

    return tools


def to_openai_tools(tools: list[HarnessTool]) -> list[Any]:
    """Convert harness tools to OpenAI Agents SDK tools."""
    if not tools:
        return []
    try:
        from agents import function_tool
    except Exception as exc:
        raise ImportError(
            "OpenAI tool conversion requires openai-agents. Install with: "
            "pip install 'superoptix[frameworks-openai]'."
        ) from exc

    converted = []
    for tool in tools:
        func = _make_callable(tool, async_callable=True)
        try:
            converted.append(
                function_tool(
                    name_override=tool.name,
                    description_override=tool.description,
                )(func)
            )
        except TypeError:
            converted.append(function_tool(func))
    return converted


def to_google_adk_tools(tools: list[HarnessTool]) -> list[Any]:
    """Convert harness tools to Google ADK function tools."""
    return [_make_callable(tool, async_callable=False) for tool in tools]


def to_pydantic_ai_tools(tools: list[HarnessTool]) -> list[Any]:
    """Convert harness tools to Pydantic AI tools."""
    if not tools:
        return []
    try:
        from pydantic_ai import Tool
    except Exception as exc:
        raise ImportError(
            "Pydantic AI tool conversion requires pydantic-ai. Install with: "
            "pip install 'superoptix[frameworks-pydantic-ai]'."
        ) from exc

    return [
        Tool(
            _make_callable(tool, async_callable=True),
            name=tool.name,
            description=tool.description,
        )
        for tool in tools
    ]


def to_deepagents_tools(tools: list[HarnessTool]) -> list[Any]:
    """Convert custom harness tools to DeepAgents/LangChain callables.

    DeepAgents already ships native filesystem, shell, planning, and task tools.
    Skip SuperOptiX's built-in tool names so those native tools stay in charge.
    """
    native_tool_names = {"read", "write", "edit", "bash", "grep", "glob"}
    return [
        _make_callable(tool, async_callable=False)
        for tool in tools
        if tool.name not in native_tool_names
    ]


def _make_callable(tool: HarnessTool, *, async_callable: bool) -> Callable[..., Any]:
    signature = _signature_from_schema(tool.parameters)

    if async_callable:

        async def _tool_callable(**kwargs: Any) -> str:
            return tool.execute(dict(kwargs or {}))

    else:

        def _tool_callable(**kwargs: Any) -> str:
            return tool.execute(dict(kwargs or {}))

    _tool_callable.__name__ = _safe_identifier(tool.name)
    _tool_callable.__doc__ = tool.description
    _tool_callable.__signature__ = signature  # type: ignore[attr-defined]
    return _tool_callable


def _signature_from_schema(schema: dict[str, Any]) -> inspect.Signature:
    props = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])
    parameters = []
    for raw_name, info in props.items():
        info = info or {}
        name = _safe_identifier(str(raw_name))
        default = inspect.Parameter.empty if raw_name in required else None
        parameters.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=_json_schema_type_to_python(info.get("type")),
            )
        )
    return inspect.Signature(parameters=parameters, return_annotation=str)


def _json_schema_type_to_python(raw_type: Any) -> Any:
    value = str(raw_type or "string").strip().lower()
    return {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }.get(value, str)


def _safe_identifier(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", str(name or "tool"))
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "tool"
    if cleaned[0].isdigit():
        cleaned = f"tool_{cleaned}"
    return cleaned
