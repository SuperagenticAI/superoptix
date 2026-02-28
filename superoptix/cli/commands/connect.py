"""Connection commands for Super CLI (BYOK/LOCAL/ACP/MCP)."""

from __future__ import annotations

import shlex
import shutil
from argparse import Namespace
from typing import Any

import requests
from rich.console import Console
from rich.table import Table

from superoptix.cli.connection_state import ConnectionStateStore


console = Console()


def connect_status(args: Namespace) -> None:
    """Show current connection state and configured endpoints."""
    store = ConnectionStateStore()
    data = store.load()
    profile = store.profile(data)

    table = Table(
        title="Super CLI Connections",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Type", style="bold")
    table.add_column("Configured", style="white")
    table.add_column("Details", style="dim")

    byok = profile.get("byok", {}) or {}
    local = profile.get("local", {}) or {}
    acp = profile.get("acp", {}) or {}
    mcp_servers = (profile.get("mcp", {}) or {}).get("servers", {}) or {}

    table.add_row(
        "BYOK",
        "yes" if byok else "no",
        _fmt_kvs(byok, ["provider", "model", "api_key_env", "base_url"]),
    )
    table.add_row(
        "LOCAL",
        "yes" if local else "no",
        _fmt_kvs(local, ["provider", "model", "endpoint"]),
    )
    table.add_row(
        "ACP",
        "yes" if acp else "no",
        _fmt_kvs(acp, ["agent", "model", "command"]),
    )
    table.add_row(
        "MCP",
        "yes" if mcp_servers else "no",
        f"{len(mcp_servers)} server(s)",
    )

    console.print(table)

    active = profile.get("active_connection")
    if active:
        console.print(
            f"\n[green]Active:[/green] {active.get('type')} ({active.get('name') or 'default'})"
        )
    else:
        console.print("\n[yellow]Active:[/yellow] none")

    if mcp_servers:
        mcp_table = Table(title="Configured MCP Servers", header_style="bold magenta")
        mcp_table.add_column("Name", style="bold")
        mcp_table.add_column("Transport")
        mcp_table.add_column("Enabled")
        mcp_table.add_column("Endpoint")
        for name, server in mcp_servers.items():
            endpoint = server.get("url") or _fmt_command(server)
            mcp_table.add_row(
                name,
                server.get("transport", "stdio"),
                "yes" if server.get("enabled", True) else "no",
                endpoint,
            )
        console.print()
        console.print(mcp_table)

    console.print(f"\n[dim]State file: {store.state_path}[/dim]")


def connect_byok(args: Namespace) -> None:
    """Configure BYOK provider/model and optionally set active connection."""
    store = ConnectionStateStore()
    store.set_byok(
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
    )
    if args.activate:
        store.set_active("byok", args.provider)

    env_status = "set" if args.api_key_env else "not set"
    console.print(
        f"[green]Saved BYOK connection:[/green] provider={args.provider}, model={args.model}, api_key_env={env_status}"
    )

    if args.api_key_env:
        import os

        has_env = bool(os.environ.get(args.api_key_env))
        if has_env:
            console.print(f"[green]Environment key present:[/green] {args.api_key_env}")
        else:
            console.print(
                f"[yellow]Environment key missing:[/yellow] {args.api_key_env} (set this before running cloud calls)"
            )


def connect_local(args: Namespace) -> None:
    """Configure local model provider/model and optionally test endpoint."""
    store = ConnectionStateStore()
    store.set_local(
        provider=args.provider,
        model=args.model,
        endpoint=args.endpoint,
    )
    if args.activate:
        store.set_active("local", args.provider)

    console.print(
        f"[green]Saved local connection:[/green] provider={args.provider}, model={args.model}"
    )
    if args.endpoint:
        console.print(f"[dim]Endpoint: {args.endpoint}[/dim]")
    if args.test:
        _run_local_health_check(args.provider, args.endpoint)


def connect_acp(args: Namespace) -> None:
    """Configure ACP agent command/model and optionally verify binary exists."""
    store = ConnectionStateStore()
    store.set_acp(
        agent=args.agent,
        model=args.model,
        command=args.command,
    )
    if args.activate:
        store.set_active("acp", args.agent)

    console.print(f"[green]Saved ACP connection:[/green] agent={args.agent}")
    if args.command:
        console.print(f"[dim]Command: {args.command}[/dim]")
    if args.test and args.command:
        binary = shlex.split(args.command)[0]
        if shutil.which(binary):
            console.print(f"[green]ACP command available:[/green] {binary}")
        else:
            console.print(
                f"[yellow]ACP command not found on PATH:[/yellow] {binary}"
            )


def connect_mcp(args: Namespace) -> None:
    """Add/update MCP server config and optionally set active connection."""
    store = ConnectionStateStore()
    parsed_args = _parse_mcp_args(args.args)

    store.set_mcp_server(
        name=args.name,
        transport=args.transport,
        command=args.command,
        args=parsed_args,
        url=args.url,
        enabled=not args.disable,
    )
    if args.activate:
        store.set_active("mcp", args.name)

    console.print(
        f"[green]Saved MCP server:[/green] name={args.name}, transport={args.transport}"
    )
    if args.transport == "stdio":
        console.print(f"[dim]{_fmt_command({'command': args.command, 'args': parsed_args})}[/dim]")
    else:
        console.print(f"[dim]URL: {args.url}[/dim]")

    if args.test:
        _run_mcp_health_check(args.transport, args.command, parsed_args, args.url)


def _fmt_kvs(data: dict[str, Any], keys: list[str]) -> str:
    parts = []
    for k in keys:
        v = data.get(k)
        if v:
            parts.append(f"{k}={v}")
    return ", ".join(parts) if parts else "-"


def _fmt_command(server: dict[str, Any]) -> str:
    command = server.get("command")
    args = server.get("args") or []
    if not command:
        return "-"
    return " ".join([command, *args])


def _parse_mcp_args(raw_args: str | None) -> list[str]:
    if not raw_args:
        return []
    return shlex.split(raw_args)


def _run_local_health_check(provider: str, endpoint: str | None) -> None:
    default_endpoint = {
        "ollama": "http://localhost:11434/api/tags",
        "lmstudio": "http://localhost:1234/v1/models",
        "vllm": "http://localhost:8000/v1/models",
        "sglang": "http://localhost:30000/v1/models",
        "mlx": "http://localhost:8080/v1/models",
    }.get(provider, "http://localhost:8000/v1/models")
    url = endpoint or default_endpoint
    try:
        response = requests.get(url, timeout=3)
        if response.status_code < 400:
            console.print(f"[green]Local endpoint reachable:[/green] {url}")
        else:
            console.print(
                f"[yellow]Local endpoint responded with status {response.status_code}:[/yellow] {url}"
            )
    except Exception as exc:
        console.print(f"[yellow]Local endpoint check failed:[/yellow] {exc}")


def _run_mcp_health_check(
    transport: str,
    command: str | None,
    args: list[str],
    url: str | None,
) -> None:
    if transport == "stdio":
        if not command:
            console.print("[yellow]Cannot test stdio MCP: missing --command[/yellow]")
            return
        binary = shlex.split(command)[0]
        if shutil.which(binary):
            console.print(f"[green]MCP stdio command available:[/green] {binary}")
            if args:
                console.print(f"[dim]Args: {' '.join(args)}[/dim]")
        else:
            console.print(f"[yellow]MCP stdio command not found:[/yellow] {binary}")
        return

    if not url:
        console.print("[yellow]Cannot test MCP URL transport: missing --url[/yellow]")
        return
    try:
        response = requests.get(url, timeout=3)
        console.print(f"[green]MCP endpoint reachable:[/green] {url} ({response.status_code})")
    except Exception as exc:
        console.print(f"[yellow]MCP endpoint check failed:[/yellow] {exc}")
