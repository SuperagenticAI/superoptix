"""`super a2a` — adapt an existing agent into an A2A 1.0 endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

DEFAULT_PUBLIC_URL = "http://127.0.0.1:8000"


def _uvicorn_target(out_dir: Path, server_module: str) -> str:
    """Build the uvicorn target for the emitted server.

    uvicorn takes a dotted module path, so the output directory has to be
    converted rather than interpolated. A directory outside the working
    directory gets an --app-dir, since no dotted path from here reaches it.
    """
    resolved = out_dir.resolve()
    try:
        relative = resolved.relative_to(Path.cwd())
    except ValueError:
        return f"--app-dir {resolved} {server_module}:app"
    if not relative.parts:
        return f"{server_module}:app"
    return ".".join([*relative.parts, server_module]) + ":app"


def adapt_agent(args) -> None:
    """Introspect an existing agent and emit an A2A card plus server."""
    from superoptix.protocols.a2a.adapt import (
        AdaptError,
        available,
        detect,
        emit,
        get,
        load_entrypoint,
    )

    # The agent lives in the user's project, not ours.
    project_root = Path(getattr(args, "project_root", "") or Path.cwd()).resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    entrypoint = str(args.entrypoint)
    try:
        obj = load_entrypoint(entrypoint)
    except AdaptError as exc:
        console.print(f"[bold red]❌ {exc}[/]")
        raise SystemExit(1) from exc

    framework = str(getattr(args, "framework", "") or "").strip().lower()
    try:
        introspector = get(framework) if framework else detect(obj)
    except AdaptError as exc:
        console.print(f"[bold red]❌ {exc}[/]")
        raise SystemExit(1) from exc

    if introspector is None:
        console.print(
            f"[bold red]❌ Could not tell which framework {entrypoint} belongs to.[/]\n"
            f"   Pass --framework explicitly. Supported: {', '.join(available())}"
        )
        raise SystemExit(1)

    try:
        spec = introspector.introspect(obj, entrypoint=entrypoint)
    except AdaptError as exc:
        console.print(f"[bold red]❌ {exc}[/]")
        raise SystemExit(1) from exc

    public_url = str(getattr(args, "url", "") or DEFAULT_PUBLIC_URL).rstrip("/")
    out_dir = Path(getattr(args, "out", "") or "a2a").expanduser()

    written = emit(spec, out_dir, public_url=public_url)

    skill_lines = "\n".join(
        f"  • [cyan]{s.id}[/] — {s.description[:80]}" for s in spec.skills
    )
    console.print(
        Panel(
            f"[bold]{spec.name}[/] · {introspector.framework}\n"
            f"{spec.description}\n\n"
            f"[bold]Skills discovered:[/]\n{skill_lines}",
            title="🔌 Adapted to A2A 1.0",
            border_style="cyan",
        )
    )
    for path in written:
        console.print(f"  [green]✓[/] {path}")

    server_module = written[1].stem
    console.print(
        "\n[bold]Serve it:[/]\n"
        f"  [cyan]uvicorn {_uvicorn_target(out_dir, server_module)} --port 8000[/]\n"
        "\n[bold]Then check it:[/]\n"
        "  [cyan]curl localhost:8000/.well-known/agent-card.json[/]\n"
    )
    console.print(
        "[dim]Your agent was not modified. These files are yours to edit and deploy.[/]"
    )
