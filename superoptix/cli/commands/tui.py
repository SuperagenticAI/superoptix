"""Super CLI TUI - SuperQode-style interface for SuperOptiX."""

from __future__ import annotations

import os
import random
import re
import shlex
import shutil
import textwrap
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style as PTStyle
from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.status import Status
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from superoptix.cli.commands.acp_client import ACPClient, ACPSessionConfig
from superoptix.cli.commands.mcp_client import MCPClient
from superoptix.cli.connection_state import ConnectionStateStore
from superoptix.cli.provider_catalog import load_provider_catalog


console = Console()


EMOJI = {
    "brain": "🧠",
    "rocket": "🚀",
    "sparkles": "✨",
    "laptop": "💻",
    "test_tube": "🧪",
    "gear": "⚙️",
    "house": "🏠",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "robot": "🤖",
    "link": "🔌",
    "key": "🔑",
}

THINKING_MESSAGES = [
    "Analyzing your request",
    "Understanding context",
    "Thinking deeply",
    "Formulating response",
    "Connecting MCP/ACP runtime",
]

SUPERCLI_ASCII = """
[bold bright_cyan] ███████╗██╗   ██╗██████╗ ███████╗██████╗      ██████╗██╗     ██╗[/bold bright_cyan]
[bold bright_cyan] ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║     ██║[/bold bright_cyan]
[bold bright_cyan] ███████╗██║   ██║██████╔╝█████╗  ██████╔╝    ██║     ██║     ██║[/bold bright_cyan]
[bold bright_cyan] ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗    ██║     ██║     ██║[/bold bright_cyan]
[bold bright_cyan] ███████║╚██████╔╝██║     ███████╗██║  ██║    ╚██████╗███████╗██║[/bold bright_cyan]
[bold bright_cyan] ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝[/bold bright_cyan]
"""

SUPERCLI_ASCII_COMPACT = """[bold bright_cyan]SUPER CLI[/bold bright_cyan]"""


@dataclass
class TeamRole:
    mode: str
    role: str
    description: str
    model: str
    provider: str
    execution_mode: str = "acp"
    enabled: bool = True
    agent: str = ""

    @property
    def command(self) -> str:
        return f":{self.mode} {self.role}"


@dataclass
class TeamConfig:
    team_name: str
    description: str
    roles: List[TeamRole]

    @property
    def enabled_roles(self) -> List[TeamRole]:
        return [r for r in self.roles if r.enabled]


def _fmt_kvs(data: Dict[str, object], keys: List[str]) -> str:
    parts = []
    for key in keys:
        value = data.get(key)
        if value:
            parts.append(f"{key}={value}")
    return ", ".join(parts) if parts else "-"


def _default_acp_command(agent: str) -> str | None:
    defaults = {
        "opencode": "opencode acp",
        "claude-code": "claude-code acp",
    }
    return defaults.get(agent)


def _safe_text(value: object, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _extract_openai_text(payload: Mapping[str, object]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, Mapping):
            message = first.get("message")
            if isinstance(message, Mapping):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content
    return ""


def _default_local_endpoint(provider: str, endpoint: str | None) -> str:
    if endpoint:
        return _normalize_local_endpoint(provider, endpoint)
    defaults = {
        "ollama": "http://localhost:11434/api/chat",
        "lmstudio": "http://localhost:1234/v1/chat/completions",
        "vllm": "http://localhost:8000/v1/chat/completions",
        "sglang": "http://localhost:30000/v1/chat/completions",
        "mlx": "http://localhost:8080/v1/chat/completions",
    }
    return defaults.get(provider.lower(), "http://localhost:8000/v1/chat/completions")


def _normalize_local_endpoint(provider: str, endpoint: str) -> str:
    value = endpoint.strip()
    if not value:
        return _default_local_endpoint(provider, None)
    provider_key = provider.lower()
    if provider_key == "ollama":
        if value.endswith("/api/chat"):
            return value
        if value.endswith("/api/tags"):
            return value[:-9] + "/api/chat"
        if value.endswith("/"):
            value = value[:-1]
        if "/api/" not in value:
            return value + "/api/chat"
        return value
    if value.endswith("/v1/chat/completions"):
        return value
    if value.endswith("/v1/models"):
        return value[:-9] + "/chat/completions"
    if value.endswith("/v1"):
        return value + "/chat/completions"
    if value.endswith("/"):
        value = value[:-1]
    if "/v1/" not in value:
        return value + "/v1/chat/completions"
    return value


def _default_byok_base_url(provider: str, base_url: str | None) -> str:
    if base_url:
        return base_url
    defaults = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "deepseek": "https://api.deepseek.com/chat/completions",
        "groq": "https://api.groq.com/openai/v1/chat/completions",
        "anthropic": "https://api.anthropic.com/v1/messages",
    }
    return defaults.get(provider.lower(), "https://api.openai.com/v1/chat/completions")


def _split_provider_model_token(
    first: str | None,
    second: str | None = None,
) -> tuple[str | None, str | None]:
    if not first:
        return None, None
    value = first.strip()
    if "/" in value:
        provider, model = value.split("/", 1)
        provider = provider.strip().lower()
        model = model.strip()
        return (provider or None, model or None)
    provider = value.lower()
    model = second.strip() if second else None
    return (provider or None, model or None)


def load_team_config() -> TeamConfig:
    """Load pseudo-team roles from Super CLI profile."""
    store = ConnectionStateStore()
    profile = store.profile(store.load())
    byok = profile.get("byok", {}) or {}
    local = profile.get("local", {}) or {}
    acp = profile.get("acp", {}) or {}

    roles = [
        TeamRole(
            mode="dev",
            role="fullstack",
            description="ACP coding role",
            model=_safe_text(acp.get("model"), "default"),
            provider=_safe_text(acp.get("agent"), "opencode"),
            execution_mode="acp",
            enabled=bool(acp),
            agent=_safe_text(acp.get("agent"), "opencode"),
        ),
        TeamRole(
            mode="qe",
            role="review",
            description="BYOK review role",
            model=_safe_text(byok.get("model"), "gpt-4o"),
            provider=_safe_text(byok.get("provider"), "openai"),
            execution_mode="byok",
            enabled=bool(byok),
        ),
        TeamRole(
            mode="devops",
            role="local",
            description="Local runtime role",
            model=_safe_text(local.get("model"), "llama3.2:3b"),
            provider=_safe_text(local.get("provider"), "ollama"),
            execution_mode="local",
            enabled=bool(local),
        ),
    ]
    return TeamConfig(
        team_name="Super CLI Team",
        description="ACP + MCP + BYOK + Local unified runtime",
        roles=roles,
    )


class OutputFilter:
    TOOL_OPERATIONS = ["Read", "Write", "Edit", "Bash", "Grep", "Search", "List"]

    def __init__(self):
        self.ansi_pattern = re.compile(r"\x1b\[[0-9;]*m|\[\d+(?:;\d+)*m")

    def filter(self, text: str) -> str:
        if not text:
            return text
        lines = text.split("\n")
        filtered = []
        for line in lines:
            clean = self.ansi_pattern.sub("", line).strip()
            if clean.startswith("|"):
                after = clean[1:].strip()
                if any(after.startswith(op) for op in self.TOOL_OPERATIONS):
                    continue
            filtered.append(line)
        return re.sub(r"\n{3,}", "\n\n", "\n".join(filtered)).strip()


class ThinkingSpinner:
    def __init__(self, console: Console, message: str = "Thinking..."):
        self.console = console
        self.initial_message = message
        self._status: Optional[Status] = None
        self._start_time = 0.0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._msg_index = 0
        self._last_msg_change = 0.0

    def _status_text(self) -> str:
        elapsed = time.time() - self._start_time
        if time.time() - self._last_msg_change > 2.5:
            self._msg_index = (self._msg_index + 1) % len(THINKING_MESSAGES)
            self._last_msg_change = time.time()
        return f"  {EMOJI['brain']} [bold cyan]{THINKING_MESSAGES[self._msg_index]}[/bold cyan] [dim]({elapsed:.1f}s)[/dim]"

    def _loop(self):
        while self._running and self._status:
            try:
                self._status.update(self._status_text())
                time.sleep(0.12)
            except Exception:
                break

    def __enter__(self):
        self._running = True
        self._start_time = time.time()
        self._last_msg_change = self._start_time
        self._msg_index = random.randint(0, len(THINKING_MESSAGES) - 1)
        self._status = self.console.status(self._status_text(), spinner="dots")
        self._status.__enter__()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.4)
        if self._status:
            self._status.__exit__(*args)


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"`([^`]+?)`", r"\1", text)
    text = re.sub(r"\[([^\]]+?)\]\([^)]+?\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    return text


class ResponsePanel:
    def __init__(self, console: Console):
        self.console = console
        self.filter = OutputFilter()

    def display(self, content: str, title: str = "Response"):
        filtered = self.filter.filter(content)
        if not filtered:
            return
        rendered = self._render_content(filtered)
        panel = Panel(
            rendered,
            title=f"[bold bright_cyan]{title}[/bold bright_cyan]",
            border_style="bright_blue",
            box=ROUNDED,
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)

    def _render_content(self, content: str) -> Group:
        term_width = shutil.get_terminal_size().columns
        wrap_width = min(term_width - 10, 100)
        code_pattern = r"```(\w*)\n?(.*?)```"
        parts = []
        last_end = 0
        for match in re.finditer(code_pattern, content, re.DOTALL):
            if match.start() > last_end:
                text = content[last_end : match.start()].strip()
                if text:
                    clean = _strip_markdown(text)
                    parts.append(Text(textwrap.fill(clean, width=wrap_width)))
            lang = match.group(1) or "text"
            code = match.group(2).strip()
            if code:
                parts.append(Text())
                parts.append(Syntax(code, lang, theme="monokai", line_numbers=True, word_wrap=True))
                parts.append(Text())
            last_end = match.end()
        if last_end < len(content):
            remaining = content[last_end:].strip()
            if remaining:
                clean = _strip_markdown(remaining)
                parts.append(Text(textwrap.fill(clean, width=wrap_width)))
        return Group(*parts) if parts else Group(Text(_strip_markdown(content)))


def print_welcome(console: Console, team_config: Optional[TeamConfig] = None):
    console.clear()
    cfg = team_config or load_team_config()
    term_width = shutil.get_terminal_size().columns
    console.print()
    console.print(SUPERCLI_ASCII if term_width >= 90 else SUPERCLI_ASCII_COMPACT)
    console.print(Align.center(f"[bold white]{cfg.team_name}[/bold white] [dim]• {cfg.description}[/dim]"))
    console.print()
    console.print(Rule(style="bright_magenta"))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    table.add_column("Icon", width=3)
    table.add_column("Command", style="bold yellow", width=18)
    table.add_column("Mode", width=12)
    table.add_column("Description")
    table.add_column("Model", style="dim cyan", width=20)
    icons = {"dev": "💻", "qe": "🧪", "devops": "⚙️"}
    for role in cfg.roles:
        badge = (
            f"[blue]ACP[/blue]•{role.agent[:8]}"
            if role.execution_mode == "acp"
            else f"[green]{role.execution_mode.upper()}[/green]•{role.provider[:6]}"
        )
        table.add_row(
            icons.get(role.mode, "🔧"),
            role.command,
            badge,
            role.description,
            role.model[:18],
        )
    console.print(Align.center(table))
    console.print()
    console.print(Rule(style="dim cyan"))
    console.print(Align.center("Quick Start: [yellow]:help[/yellow] • [yellow]:acp connect[/yellow] • [yellow]:mcp list[/yellow] • [yellow]:exit[/yellow]"))
    console.print()


def print_roles(console: Console, team_config: Optional[TeamConfig] = None):
    cfg = team_config or load_team_config()
    console.print()
    console.print(Align.center(f"[bold cyan]{EMOJI['robot']} {cfg.team_name} - Roles[/bold cyan]"))
    console.print()
    for role in cfg.roles:
        status = "[green]●[/green]" if role.enabled else "[dim]○[/dim]"
        mode = role.execution_mode.upper()
        console.print(
            f"  {status} [yellow]{role.command:<18}[/yellow] "
            f"[bold]{mode:<6}[/bold] [dim cyan]{role.model:<20}[/dim cyan] "
            f"[dim]{role.description}[/dim]"
        )
    console.print()


class SuperCLICompleter(Completer):
    def __init__(self):
        self.base_commands = [
            (":help", "Show help"),
            (":roles", "List roles"),
            (":status", "Show runtime status"),
            (":profile", "Show saved profile summary"),
            (":connect", "Connection picker/help"),
            (":connect acp", "Connect ACP agent"),
            (":connect byok", "Activate BYOK provider"),
            (":connect local", "Activate local model"),
            (":c", "Alias for :connect"),
            (":acp connect", "Connect ACP agent"),
            (":acp disconnect", "Disconnect ACP"),
            (":acp send", "Send prompt via ACP"),
            (":mcp list", "List MCP servers"),
            (":mcp connect", "Connect MCP server"),
            (":mcp tools", "List MCP tools"),
            (":disconnect", "Disconnect current session"),
            (":clear", "Clear screen"),
            (":home", "Show welcome"),
            (":exit", "Exit TUI"),
        ]
        self._role_commands: Optional[List[tuple[str, str]]] = None

    @property
    def commands(self) -> List[tuple[str, str]]:
        if self._role_commands is None:
            self._load_role_commands()
        return self._role_commands + self.base_commands

    def _load_role_commands(self):
        self._role_commands = []
        cfg = load_team_config()
        for role in cfg.roles:
            self._role_commands.append((role.command, f"{role.execution_mode.upper()} {role.description} ({role.model})"))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        normalized = text.lower()
        if not (normalized.startswith(":") or normalized.startswith("/")):
            return
        pref = ":" if normalized.startswith(":") else "/"
        normalized = ":" + normalized[1:]
        for cmd, desc in self.commands:
            if cmd.startswith(normalized):
                out = pref + cmd[1:]
                yield Completion(out, start_position=-len(text), display=out, display_meta=desc)


class EnhancedPrompt:
    STYLE = PTStyle.from_dict(
        {
            "prompt": "bold ansicyan",
            "mode": "bold ansigreen",
            "arrow": "bold ansiwhite",
            "input": "ansiwhite",
            "completion-menu": "bg:ansiblack ansigreen",
            "completion-menu.completion": "bg:ansiblack ansiwhite",
            "completion-menu.completion.current": "bg:ansicyan ansiblack bold",
            "completion-menu.meta": "bg:ansiblack ansigray",
            "completion-menu.meta.current": "bg:ansicyan ansiblack",
        }
    )

    def __init__(self, history_file: Optional[Path] = None):
        if history_file:
            history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history = FileHistory(str(history_file))
        else:
            self.history = InMemoryHistory()

        bindings = KeyBindings()

        @bindings.add(Keys.ControlC)
        def _(event):
            event.app.exit(exception=KeyboardInterrupt())

        @bindings.add(Keys.ControlD)
        def _(event):
            event.app.exit(exception=EOFError())

        self.session = PromptSession(
            history=self.history,
            completer=SuperCLICompleter(),
            style=self.STYLE,
            key_bindings=bindings,
            complete_while_typing=True,
            enable_history_search=True,
        )
        self.console = Console()
        self.mode = "HOME"
        self.connected = False
        self.agent_name = ""
        self.execution_mode = ""

    def _mode_info(self) -> tuple[str, str, str]:
        if self.connected and self.agent_name:
            badge = "ACP" if self.execution_mode == "acp" else self.execution_mode.upper()
            return EMOJI["link"], f"{badge} • {self.agent_name.upper()}", "bright_blue"
        base = self.mode.upper()
        mapping = {
            "HOME": (EMOJI["house"], "HOME", "bright_cyan"),
            "DEV": (EMOJI["laptop"], "DEV", "bright_green"),
            "QE": (EMOJI["test_tube"], "QE", "bright_yellow"),
            "DEVOPS": (EMOJI["gear"], "DEVOPS", "bright_blue"),
        }
        return mapping.get(base, ("🔧", base, "white"))

    def prompt(self, clear_screen: bool = False) -> str:
        if clear_screen:
            self.console.clear()
        icon, mode_text, color = self._mode_info()
        self.console.print()
        self.console.print(f"[bold {color} reverse] {icon} {mode_text} [/]")
        self.console.print()
        result = self.session.prompt(HTML("<ansicyan>❯ </ansicyan>"))
        self.console.print()
        self.console.print("  [dim]Tab[/] complete  [dim]│[/]  [dim]↑↓[/] history  [dim]│[/]  [yellow]:help[/]  [dim]│[/]  [yellow]:exit[/]")
        self.console.print()
        return result

    def set_mode(self, mode: str):
        self.mode = mode

    def set_connected(self, agent_name: str, connected: bool = True, execution_mode: str = "acp"):
        self.agent_name = agent_name
        self.connected = connected
        self.execution_mode = execution_mode


class SuperCLIUI:
    def __init__(self):
        self.console = Console()
        self.prompt = EnhancedPrompt(history_file=Path.home() / ".superoptix" / "tui_history")
        self.response_panel = ResponsePanel(self.console)
        self.team_config = load_team_config()

    def print_welcome(self):
        print_welcome(self.console, self.team_config)

    def print_roles(self):
        print_roles(self.console, self.team_config)

    def get_input(self, clear_screen: bool = False) -> str:
        return self.prompt.prompt(clear_screen=clear_screen)

    def set_mode(self, mode: str):
        self.prompt.set_mode(mode)

    def set_agent(self, name: str, connected: bool, execution_mode: str):
        self.prompt.set_connected(name, connected, execution_mode)

    def show_thinking(self, message: str = "Thinking..."):
        return ThinkingSpinner(self.console, message)

    def display_response(self, content: str, title: str = "Response"):
        self.response_panel.display(content, title=title)


@dataclass
class TUIRunner:
    ui: SuperCLIUI = field(default_factory=SuperCLIUI)
    running: bool = True

    def __post_init__(self):
        self.store = ConnectionStateStore()
        self.provider_catalog = load_provider_catalog()
        self.mcp_client = MCPClient()
        self.acp_client = ACPClient(project_root=Path.cwd(), on_event=self._on_acp_event)
        self.messages: List[str] = []
        self._sync_prompt_from_profile()

    def run(self):
        self.ui.print_welcome()
        while self.running:
            try:
                user_input = self.ui.get_input()
            except (KeyboardInterrupt, EOFError):
                self._exit()
                break

            if not user_input.strip():
                continue
            self._handle_input(user_input.strip())

    def _handle_input(self, text: str):
        if text.startswith("/") or text.startswith(":"):
            self._handle_command(text)
            return

        if self.acp_client.is_connected():
            with self.ui.show_thinking("Sending prompt to ACP"):
                result = self.acp_client.send_prompt_sync(text)
            if result.get("ok"):
                self.ui.display_response(str(result.get("result")), title="ACP Response")
            else:
                self.ui.display_response(f"Error: {result.get('error')}", title="ACP Error")
            return

        profile = self.store.profile(self.store.load())
        active = profile.get("active_connection") or {}
        active_type = active.get("type")
        if active_type in {"byok", "local"}:
            cfg = profile.get(active_type, {}) or {}
            with self.ui.show_thinking(f"Sending prompt to {active_type.upper()} runtime"):
                if active_type == "byok":
                    result = self._invoke_byok_prompt(text, cfg)
                else:
                    result = self._invoke_local_prompt(text, cfg)
            if result.get("ok"):
                self.ui.display_response(str(result.get("result")), title=f"{active_type.upper()} Response")
            else:
                self.ui.display_response(str(result.get("error")), title=f"{active_type.upper()} Error")
            return

        self.ui.display_response(
            "No active interactive session. Use :connect or :acp connect [agent] [model].",
            title="Not Connected",
        )

    def _invoke_byok_prompt(self, prompt: str, cfg: Dict[str, object]) -> Dict[str, object]:
        provider = str(cfg.get("provider") or "").strip().lower()
        model = str(cfg.get("model") or "").strip()
        if not provider or not model:
            return {"ok": False, "error": "BYOK profile is missing provider/model. Use :connect byok <provider> <model>."}

        api_key_env = str(cfg.get("api_key_env") or "").strip()
        api_key = os.getenv(api_key_env) if api_key_env else None
        if provider in {"openai", "deepseek", "groq"} and not api_key:
            return {
                "ok": False,
                "error": f"Missing API key. Set {api_key_env or 'your provider key env'} and reconnect.",
            }

        base_url = _default_byok_base_url(provider, cfg.get("base_url") if isinstance(cfg.get("base_url"), str) else None)
        try:
            if provider == "anthropic":
                if not api_key:
                    return {"ok": False, "error": "Missing API key for Anthropic. Set ANTHROPIC_API_KEY or configure api_key_env."}
                return self._call_anthropic(base_url, model, prompt, api_key)
            if provider in {"google", "google-genai", "gemini"}:
                key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if not key:
                    return {"ok": False, "error": "Missing Google/Gemini API key (GEMINI_API_KEY or GOOGLE_API_KEY)."}
                return self._call_google(model, prompt, key)
            return self._call_openai_compatible(base_url, model, prompt, api_key)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _invoke_local_prompt(self, prompt: str, cfg: Dict[str, object]) -> Dict[str, object]:
        provider = str(cfg.get("provider") or "ollama").strip().lower()
        model = str(cfg.get("model") or "").strip()
        if not model:
            return {"ok": False, "error": "Local profile is missing model. Use :connect local <provider> <model>."}
        endpoint = _default_local_endpoint(provider, cfg.get("endpoint") if isinstance(cfg.get("endpoint"), str) else None)
        try:
            if provider == "ollama":
                response = requests.post(
                    endpoint,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                    timeout=90,
                )
                response.raise_for_status()
                payload = response.json()
                message = payload.get("message", {}) if isinstance(payload, dict) else {}
                content = message.get("content") if isinstance(message, Mapping) else None
                if isinstance(content, str) and content.strip():
                    return {"ok": True, "result": content}
                return {"ok": False, "error": "No content returned from Ollama response."}

            return self._call_openai_compatible(endpoint, model, prompt, api_key=None)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _call_openai_compatible(
        self,
        endpoint: str,
        model: str,
        prompt: str,
        api_key: str | None,
    ) -> Dict[str, object]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        text = _extract_openai_text(payload if isinstance(payload, Mapping) else {})
        if not text:
            return {"ok": False, "error": "No text content in response payload."}
        return {"ok": True, "result": text}

    def _call_anthropic(self, endpoint: str, model: str, prompt: str, api_key: str) -> Dict[str, object]:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "model": model,
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("content") if isinstance(payload, Mapping) else None
        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, Mapping) and item.get("type") == "text" and isinstance(item.get("text"), str):
                    chunks.append(str(item["text"]))
            text = "\n".join(chunks).strip()
            if text:
                return {"ok": True, "result": text}
        return {"ok": False, "error": "No text content in Anthropic response."}

    def _call_google(self, model: str, prompt: str, api_key: str) -> Dict[str, object]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates") if isinstance(payload, Mapping) else None
        if isinstance(candidates, list) and candidates:
            candidate = candidates[0]
            if isinstance(candidate, Mapping):
                content = candidate.get("content")
                if isinstance(content, Mapping):
                    parts = content.get("parts")
                    if isinstance(parts, list):
                        text = "\n".join(
                            str(p.get("text"))
                            for p in parts
                            if isinstance(p, Mapping) and isinstance(p.get("text"), str)
                        ).strip()
                        if text:
                            return {"ok": True, "result": text}
        return {"ok": False, "error": "No text content in Google response."}

    def _handle_command(self, raw: str):
        normalized = raw.replace("/", ":", 1) if raw.startswith("/") else raw
        parts = shlex.split(normalized)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in (":exit", ":quit"):
            self._exit()
            return
        if cmd == ":clear":
            self.ui.print_welcome()
            return
        if cmd == ":home":
            self.ui.print_welcome()
            return
        if cmd == ":help":
            self._help()
            return
        if cmd == ":roles":
            self.ui.print_roles()
            return
        if cmd in (":connect", ":c"):
            self._handle_connect(args)
            return
        if cmd == ":profile":
            profile = self.store.profile(self.store.load())
            self.ui.display_response(
                "Profile: "
                + _fmt_kvs(profile.get("byok", {}), ["provider", "model"])
                + " | "
                + _fmt_kvs(profile.get("local", {}), ["provider", "model"])
                + " | "
                + _fmt_kvs(profile.get("acp", {}), ["agent", "model"]),
                title="Profile",
            )
            return
        if cmd == ":status":
            self._status()
            return
        if cmd == ":disconnect":
            self.acp_client.disconnect_sync()
            self.ui.set_agent("", False, "acp")
            self.store.set_active("none", None)
            self.ui.display_response("Disconnected from ACP session.", title="Disconnected")
            return
        if cmd == ":mcp":
            self._handle_mcp(args)
            return
        if cmd == ":acp":
            self._handle_acp(args)
            return

        # Role shortcut commands like :dev fullstack
        if cmd.startswith(":dev") or cmd.startswith(":qe") or cmd.startswith(":devops"):
            role_mode = cmd[1:].split()[0].upper()
            self.ui.set_mode(role_mode)
            if role_mode == "DEV":
                # Super CLI native behavior: entering DEV role tries ACP profile connect.
                self._handle_acp(["connect"])
            else:
                self.ui.display_response(f"Switched mode to {cmd[1:]}", title="Mode")
            return

        self.ui.display_response(f"Unknown command: {raw}\nUse :help.", title="Command Error")

    def _help(self):
        table = Table(title="Super CLI Commands", header_style="bold cyan")
        table.add_column("Command", style="bold yellow")
        table.add_column("Description")
        rows = [
            (":help", "Show help"),
            (":roles", "Show role commands"),
            (":status", "Show ACP/MCP status"),
            (":profile", "Show saved profile summary"),
            (":connect or :c", "Connection picker/help and shortcuts"),
            (":connect !", "Show connection history"),
            (":connect -", "Switch to previous connection"),
            (":connect byok <provider> <model> [api_key_env]", "Activate BYOK profile"),
            (":connect local <provider> <model> [endpoint]", "Activate local profile"),
            (":connect acp [agent] [model]", "Connect ACP profile/agent"),
            (":acp connect [agent] [model]", "Connect ACP session"),
            (":acp send <prompt>", "Send prompt via ACP"),
            (":acp disconnect", "Disconnect ACP"),
            (":mcp list", "List MCP servers"),
            (":mcp connect <name>", "Connect MCP server"),
            (":mcp tools <name>", "List server tools"),
            (":disconnect", "Disconnect current agent"),
            (":home", "Back to home screen"),
            (":clear", "Clear and redraw"),
            (":exit", "Exit TUI"),
        ]
        for c, d in rows:
            table.add_row(c, d)
        self.ui.console.print()
        self.ui.console.print(table)
        self.ui.console.print()

    def _status(self):
        profile = self.store.profile(self.store.load())
        active = profile.get("active_connection") or {}
        active_desc = f"{active.get('type', '-')}/{active.get('name') or '-'}"
        statuses = self.mcp_client.list_server_status()
        mcp = ", ".join(f"{s.name}:{s.state.value}" for s in statuses) or "-"
        acp = f"connected={self.acp_client.is_connected()}, agent={self.acp_client.connected_agent() or '-'}"
        self.ui.display_response(f"ACTIVE: {active_desc}\nACP: {acp}\nMCP: {mcp}", title="Runtime Status")

    def _handle_connect(self, args: List[str]):
        if not args:
            self._interactive_connect_root()
            return

        sub = args[0].lower()
        if sub == "!":
            history = self.store.connection_history(limit=10)
            if not history:
                self.ui.display_response("No connection history yet.", title="Connection History")
                return
            lines = [
                f"{idx + 1}. {h.get('type', '-')}/{h.get('name') or '-'} ({h.get('updated_at', '-')})"
                for idx, h in enumerate(history)
            ]
            self.ui.display_response("\n".join(lines), title="Connection History")
            return

        if sub == "-":
            history = self.store.connection_history(limit=2)
            if len(history) < 2:
                self.ui.display_response("No previous connection to switch to.", title="Connect")
                return
            prev = history[1]
            prev_type = str(prev.get("type") or "").lower()
            prev_name = prev.get("name")
            if prev_type == "acp":
                self._handle_acp(["connect", str(prev_name or "")])
                return
            if prev_type == "byok":
                profile = self.store.profile(self.store.load())
                byok = profile.get("byok", {}) or {}
                self._activate_byok(byok.get("provider"), byok.get("model"), byok.get("api_key_env"))
                return
            if prev_type == "local":
                profile = self.store.profile(self.store.load())
                local = profile.get("local", {}) or {}
                self._activate_local(local.get("provider"), local.get("model"), local.get("endpoint"))
                return
            self.ui.display_response(f"Cannot switch to previous type: {prev_type}", title="Connect")
            return

        if sub == "acp":
            if len(args) == 1:
                self._interactive_connect_acp()
                return
            self._handle_acp(["connect", *args[1:]])
            return
        if sub == "byok":
            if len(args) == 1:
                self._interactive_connect_mode("byok")
                return
            provider, model = _split_provider_model_token(args[1], args[2] if len(args) > 2 else None)
            api_key_env = args[3] if len(args) > 3 else None
            self._activate_byok(provider, model, api_key_env)
            return
        if sub == "local":
            if len(args) == 1:
                self._interactive_connect_mode("local")
                return
            provider, model = _split_provider_model_token(args[1], args[2] if len(args) > 2 else None)
            endpoint = args[3] if len(args) > 3 else None
            self._activate_local(provider, model, endpoint)
            return

        self._show_connect_help()

    def _supports_interactive_picker(self) -> bool:
        return bool(hasattr(self.ui.console.file, "isatty") and self.ui.console.file.isatty())

    def _interactive_connect_root(self):
        self.ui.console.print()
        self.ui.console.print("[bold cyan]Connect[/bold cyan]")
        self.ui.console.print("  1. ACP Agent")
        self.ui.console.print("  2. BYOK Provider")
        self.ui.console.print("  3. Local Provider")
        self.ui.console.print("  4. Show Status")
        self.ui.console.print()
        choice_num = Prompt.ask("Choose option", choices=["1", "2", "3", "4"], default="2")
        choice = {"1": "acp", "2": "byok", "3": "local", "4": "status"}[choice_num]
        if choice == "status":
            self._status()
            return
        if choice == "acp":
            self._interactive_connect_acp()
            return
        self._interactive_connect_mode(choice)

    def _interactive_connect_mode(self, mode: str):
        catalog = self.provider_catalog.get(mode, {})
        if not catalog:
            self.ui.display_response(f"No {mode.upper()} providers available.", title="Connect")
            return
        entries = sorted(catalog.items(), key=lambda i: i[0])
        self.ui.console.print()
        self.ui.console.print(f"[bold cyan]{mode.upper()} Providers[/bold cyan]")
        for idx, (pid, entry) in enumerate(entries, start=1):
            self.ui.console.print(f"  {idx}. {pid} - {entry.name}")
        self.ui.console.print()
        provider_idx = Prompt.ask(
            "Choose provider number",
            choices=[str(i) for i in range(1, len(entries) + 1)],
            default="1",
        )
        provider, entry = entries[int(provider_idx) - 1]

        models = list((entry.example_models if entry else [])[:20])
        if mode == "local" and provider == "ollama":
            installed = self._discover_ollama_models()
            if installed:
                # Keep installed models first while preserving order and uniqueness.
                seen: set[str] = set()
                ordered = []
                for m in [*installed, *models]:
                    if m not in seen:
                        seen.add(m)
                        ordered.append(m)
                models = ordered[:40]
        if models:
            self.ui.console.print()
            self.ui.console.print(f"[bold cyan]{mode.upper()} Models ({provider})[/bold cyan]")
            for idx, model in enumerate(models, start=1):
                self.ui.console.print(f"  {idx}. {model}")
            self.ui.console.print(f"  {len(models) + 1}. custom...")
            self.ui.console.print()
            model_idx = Prompt.ask(
                "Choose model number",
                choices=[str(i) for i in range(1, len(models) + 2)],
                default="1",
            )
            if int(model_idx) == len(models) + 1:
                selected_model = Prompt.ask("Enter custom model").strip()
            else:
                selected_model = models[int(model_idx) - 1]
        else:
            selected_model = Prompt.ask("Enter model").strip()
        if not selected_model:
            return

        if mode == "byok":
            default_env = entry.env_vars[0] if entry and entry.env_vars else ""
            api_env = Prompt.ask("API key env var (optional)", default=default_env).strip()
            self._activate_byok(provider, selected_model, api_env or default_env or None)
            return

        default_endpoint = entry.default_base_url if entry else ""
        endpoint = Prompt.ask("Endpoint (optional)", default=default_endpoint or "").strip()
        self._activate_local(provider, selected_model, endpoint or default_endpoint or None)

    def _discover_ollama_models(self) -> List[str]:
        candidates = [
            "http://localhost:11434/api/tags",
        ]
        profile = self.store.profile(self.store.load())
        local = profile.get("local", {}) or {}
        endpoint = local.get("endpoint")
        if isinstance(endpoint, str) and endpoint.strip():
            normalized = _normalize_local_endpoint("ollama", endpoint)
            tags_url = normalized.replace("/api/chat", "/api/tags")
            if tags_url not in candidates:
                candidates.insert(0, tags_url)

        for url in candidates:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code >= 400:
                    continue
                payload = response.json()
                models = payload.get("models")
                if not isinstance(models, list):
                    continue
                names = []
                for item in models:
                    if isinstance(item, Mapping) and isinstance(item.get("name"), str):
                        names.append(item["name"])
                if names:
                    return names
            except Exception:
                continue
        return []

    def _interactive_connect_acp(self):
        self.ui.console.print()
        self.ui.console.print("[bold cyan]ACP Agent[/bold cyan]")
        self.ui.console.print("  1. opencode")
        self.ui.console.print("  2. claude-code")
        self.ui.console.print("  3. custom...")
        self.ui.console.print()
        agent_choice = Prompt.ask("Choose agent", choices=["1", "2", "3"], default="1")
        if agent_choice == "1":
            agent = "opencode"
        elif agent_choice == "2":
            agent = "claude-code"
        else:
            agent = Prompt.ask("Enter ACP agent id").strip()
            if not agent:
                return
        model = Prompt.ask("Model override (optional)", default="").strip()
        payload = ["connect", agent]
        if model:
            payload.append(model)
        self._handle_acp(payload)

    def _show_connect_help(self):
        profile = self.store.profile(self.store.load())
        byok = profile.get("byok", {}) or {}
        local = profile.get("local", {}) or {}
        acp = profile.get("acp", {}) or {}
        content = (
            "Connection shortcuts:\n"
            "- :connect (interactive picker)\n"
            "- :connect acp [agent] [model]\n"
            "- :connect byok <provider> <model> [api_key_env]\n"
            "- :connect byok <provider>/<model> [api_key_env]\n"
            "- :connect local <provider> <model> [endpoint]\n"
            "- :connect local <provider>/<model> [endpoint]\n"
            "- :connect -  (switch to previous)\n"
            "- :connect !  (history)\n\n"
            f"Saved ACP: {_fmt_kvs(acp, ['agent', 'model'])}\n"
            f"Saved BYOK: {_fmt_kvs(byok, ['provider', 'model', 'api_key_env'])}\n"
            f"Saved LOCAL: {_fmt_kvs(local, ['provider', 'model', 'endpoint'])}"
        )
        self.ui.display_response(content, title="Connect")

    def _activate_byok(self, provider: Optional[str], model: Optional[str], api_key_env: Optional[str]):
        profile = self.store.profile(self.store.load())
        saved = profile.get("byok", {}) or {}
        resolved_provider = provider or saved.get("provider")
        resolved_model = model or saved.get("model")
        resolved_env = api_key_env or saved.get("api_key_env")
        if not resolved_provider or not resolved_model:
            self.ui.display_response(
                "Missing BYOK settings. Use :connect byok <provider> <model> [api_key_env].",
                title="BYOK Setup Required",
            )
            return
        self.acp_client.disconnect_sync()
        self.store.set_byok(
            provider=resolved_provider,
            model=resolved_model,
            api_key_env=resolved_env,
            base_url=saved.get("base_url"),
        )
        self.store.set_active("byok", resolved_provider)
        self.ui.set_agent(f"{resolved_provider}/{resolved_model}", True, "byok")
        self.ui.display_response(
            f"BYOK active: provider={resolved_provider}, model={resolved_model}",
            title="BYOK Connected",
        )

    def _activate_local(self, provider: Optional[str], model: Optional[str], endpoint: Optional[str]):
        profile = self.store.profile(self.store.load())
        saved = profile.get("local", {}) or {}
        resolved_provider = provider or saved.get("provider")
        resolved_model = model or saved.get("model")
        resolved_endpoint = endpoint or saved.get("endpoint")
        if not resolved_provider or not resolved_model:
            self.ui.display_response(
                "Missing local settings. Use :connect local <provider> <model> [endpoint].",
                title="Local Setup Required",
            )
            return
        if isinstance(resolved_endpoint, str) and resolved_endpoint.strip():
            resolved_endpoint = _normalize_local_endpoint(resolved_provider, resolved_endpoint)
        self.acp_client.disconnect_sync()
        self.store.set_local(
            provider=resolved_provider,
            model=resolved_model,
            endpoint=resolved_endpoint,
        )
        self.store.set_active("local", resolved_provider)
        self.ui.set_agent(f"{resolved_provider}/{resolved_model}", True, "local")
        extra = f", endpoint={resolved_endpoint}" if resolved_endpoint else ""
        self.ui.display_response(
            f"Local runtime active: provider={resolved_provider}, model={resolved_model}{extra}",
            title="Local Connected",
        )

    def _handle_mcp(self, args: List[str]):
        if not args or args[0] == "status":
            self._status()
            return
        sub = args[0]
        if sub == "list":
            servers = self.mcp_client.list_servers()
            if not servers:
                self.ui.display_response("No MCP servers configured.", title="MCP")
                return
            lines = [f"- {s.name} ({'enabled' if s.enabled else 'disabled'})" for s in servers]
            self.ui.display_response("\n".join(lines), title="MCP Servers")
            return
        if sub == "connect" and len(args) > 1:
            with self.ui.show_thinking("Connecting MCP server"):
                ok = self.mcp_client.connect_server_sync(args[1])
            self.ui.display_response(
                f"{'Connected' if ok else 'Failed'}: {args[1]}",
                title="MCP Connect",
            )
            return
        if sub == "disconnect" and len(args) > 1:
            ok = self.mcp_client.disconnect_server_sync(args[1])
            self.ui.display_response(
                f"{'Disconnected' if ok else 'Failed'}: {args[1]}",
                title="MCP Disconnect",
            )
            return
        if sub == "tools" and len(args) > 1:
            with self.ui.show_thinking("Fetching MCP tools"):
                tools = self.mcp_client.list_tools_sync(args[1])
            if not tools:
                self.ui.display_response("No tools available.", title="MCP Tools")
                return
            names = "\n".join(f"- {t.get('name', 'unknown')}: {t.get('description', '')}" for t in tools[:30])
            self.ui.display_response(names, title=f"MCP Tools ({args[1]})")
            return
        self.ui.display_response("Usage: :mcp [list|connect <name>|disconnect <name>|tools <name>]", title="MCP Help")

    def _handle_acp(self, args: List[str]):
        sub = args[0] if args else "status"
        if sub == "status":
            self._status()
            return
        if sub == "connect":
            profile = self.store.profile(self.store.load())
            saved = profile.get("acp", {}) or {}
            agent = (args[1].strip() if len(args) > 1 else "") or saved.get("agent") or "opencode"
            model = args[2] if len(args) > 2 else saved.get("model")
            command = saved.get("command") or _default_acp_command(agent)
            if not command:
                self.ui.display_response(
                    "No ACP command configured. Use `super connect acp --agent <id> --command \"...\"`.",
                    title="ACP Setup Required",
                )
                return
            with self.ui.show_thinking("Connecting ACP session"):
                ok = self.acp_client.connect_sync(
                    ACPSessionConfig(
                        agent=agent,
                        command=command,
                        model=model,
                        cwd=str(Path.cwd()),
                    )
                )
            if ok:
                self.store.set_acp(agent=agent, model=model, command=command)
                self.store.set_active("acp", agent)
                self.ui.set_agent(agent, True, "acp")
                self.ui.display_response(f"Connected ACP agent: {agent}", title="ACP Connected")
            else:
                self.ui.display_response("Failed to connect ACP agent.", title="ACP Error")
            return
        if sub == "disconnect":
            self.acp_client.disconnect_sync()
            self.ui.set_agent("", False, "acp")
            self.ui.display_response("ACP disconnected.", title="ACP")
            return
        if sub == "send" and len(args) > 1:
            prompt = " ".join(args[1:])
            with self.ui.show_thinking("Sending ACP command"):
                result = self.acp_client.send_prompt_sync(prompt)
            if result.get("ok"):
                self.ui.display_response(str(result.get("result")), title="ACP Response")
            else:
                self.ui.display_response(str(result.get("error")), title="ACP Error")
            return
        self.ui.display_response("Usage: :acp [status|connect [agent] [model]|send <prompt>|disconnect]", title="ACP Help")

    def _on_acp_event(self, payload: Dict[str, object]):
        # Keep this minimal for now; response path is synchronous via send_prompt_sync.
        _ = payload

    def _sync_prompt_from_profile(self):
        profile = self.store.profile(self.store.load())
        active = profile.get("active_connection") or {}
        conn_type = str(active.get("type") or "").lower()
        if conn_type == "acp":
            acp = profile.get("acp", {}) or {}
            agent = acp.get("agent") or active.get("name") or "acp"
            self.ui.set_agent(str(agent), True, "acp")
            return
        if conn_type == "byok":
            byok = profile.get("byok", {}) or {}
            name = f"{byok.get('provider', '-')}/{byok.get('model', '-')}"
            self.ui.set_agent(name, True, "byok")
            return
        if conn_type == "local":
            local = profile.get("local", {}) or {}
            name = f"{local.get('provider', '-')}/{local.get('model', '-')}"
            self.ui.set_agent(name, True, "local")
            return

    def _exit(self):
        self.running = False
        self.acp_client.disconnect_sync()
        if hasattr(self.mcp_client, "disconnect_all_sync"):
            self.mcp_client.disconnect_all_sync()
        self.ui.console.print()
        self.ui.console.print(
            Panel(
                Text.assemble(
                    ("👋 ", "yellow"),
                    ("Thanks for using ", "white"),
                    ("Super CLI", "bold bright_cyan"),
                    ("!", "white"),
                ),
                border_style="bright_cyan",
                box=ROUNDED,
                padding=(0, 2),
            )
        )
        self.ui.console.print()


def start_tui(args=None) -> None:
    runner = TUIRunner()
    runner.run()
