import os
import warnings
import json

"""Slash command handler for conversational mode.

Handles all slash commands like /model, /help, /config, etc.
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt

from superoptix.cli.connection_state import ConnectionStateStore
from superoptix.cli.provider_catalog import load_provider_catalog

try:
    from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
except Exception:
    input_dialog = None
    radiolist_dialog = None

# Suppress warnings for clean CLI experience
warnings.filterwarnings("ignore")


class SlashCommandHandler:
    """Handle slash commands in conversational mode."""

    def __init__(
        self,
        console: Console,
        config: dict,
        chat_agent=None,
        status_bar=None,
        progress_tracker=None,
    ):
        self.console = console
        self.config = config
        self.chat_agent = chat_agent  # Reference to chat agent for reloading
        self.status_bar = status_bar  # Status bar instance
        self.progress_tracker = progress_tracker  # Progress tracker instance
        self.connection_store = ConnectionStateStore()
        self.provider_catalog = load_provider_catalog()

        # Initialize playbook registry
        try:
            from .playbook_registry import PlaybookRegistry

            self.playbook_registry = PlaybookRegistry()
        except Exception:
            self.playbook_registry = None

        # Initialize knowledge access
        try:
            from .embedded_knowledge_access import EmbeddedKnowledgeAccess

            self.knowledge = EmbeddedKnowledgeAccess()
        except Exception:
            self.knowledge = None

        # Initialize MCP client
        try:
            from .mcp_client import get_mcp_client

            self.mcp_client = get_mcp_client()
        except Exception:
            self.mcp_client = None

        # Initialize ACP client
        try:
            from .acp_client import ACPClient

            self.acp_client = ACPClient(project_root=Path.cwd())
        except Exception:
            self.acp_client = None

        self.commands = self._register_commands()

    def _register_commands(self) -> dict:
        """Register all slash commands."""
        return {
            "/help": self.cmd_help,
            "/ask": self.cmd_ask,
            "/model": self.cmd_model,
            "/config": self.cmd_config,
            "/agents": self.cmd_agents,
            "/playbooks": self.cmd_playbooks,
            "/templates": self.cmd_templates,
            "/docs": self.cmd_docs,
            "/examples": self.cmd_examples,
            "/status": self.cmd_status,
            "/clear": self.cmd_clear,
            "/history": self.cmd_history,
            "/mcp": self.cmd_mcp,
            "/acp": self.cmd_acp,
            "/connect": self.cmd_connect,
            "/c": self.cmd_connect,
            "/session": self.cmd_session,
            "/tasks": self.cmd_tasks,
            "/build": self.cmd_build,
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/telemetry": self.cmd_telemetry,
        }

    def handle(self, command: str) -> Optional[str]:
        """Handle a slash command."""
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd in self.commands:
            self.commands[cmd](*args)
            return None
        else:
            self.console.print(f"\n[bold red]Unknown command:[/bold red] {cmd}")
            self.console.print(
                "[dim]Type [bold]/help[/bold] for available commands[/dim]\n"
            )
            return None

    def cmd_ask(self, *args):
        """Ask a question about SuperOptiX."""
        if not args:
            self.console.print("\n[yellow]Usage: /ask <question>[/yellow]")
            self.console.print("[dim]Example: /ask How do I add memory?[/dim]\n")
            return

        question = " ".join(args)

        if not self.knowledge:
            self.console.print("\n[yellow]Knowledge base not available[/yellow]\n")
            return

        # Search knowledge base
        results = self.knowledge.search(question, top_k=1)

        if results:
            answer = results[0]

            # Show answer in a nice panel
            answer_panel = Panel(
                f"[bold cyan]💡 {answer['question']}[/bold cyan]\n\n"
                f"{answer['answer']}\n\n"
                f"[dim]📖 Learn more: {answer.get('docs_link', 'https://superoptix.ai')}[/dim]",
                border_style="cyan",
                padding=(1, 2),
                title="[bold green]✨ Answer[/bold green]",
            )

            self.console.print()
            self.console.print(answer_panel)
            self.console.print()
        else:
            self.console.print()
            self.console.print(
                Panel(
                    "[yellow]❓ No answer found.[/yellow]\n\n"
                    "[dim]Try:[/dim]\n"
                    "• [cyan]/help[/cyan] - Show all commands\n"
                    "• [cyan]/examples[/cyan] - See workflows\n"
                    "• Visit [link=https://superoptix.ai]https://superoptix.ai[/link]",
                    border_style="yellow",
                    title="[bold yellow]⚠️  Not Found[/bold yellow]",
                )
            )
            self.console.print()

    def cmd_help(self, *args):
        """Show help message."""
        if args and args[0]:
            topic = args[0]
            self._show_topic_help(topic)
        else:
            self._show_general_help()

    def _show_general_help(self):
        """Show general help."""
        self.console.print()

        # Create title with animation effect
        title_panel = Panel(
            Align.center(Text("SuperOptiX Slash Commands", style="bold bright_cyan")),
            border_style="bright_magenta",
            padding=(1, 4),
            subtitle="[dim]Quick reference for all available commands[/dim]",
        )

        self.console.print(title_panel)
        self.console.print()

        table = Table(
            show_header=True, header_style="bold magenta", border_style="cyan"
        )
        table.add_column("Command", style="bold cyan", width=25)
        table.add_column("Description", style="white")

        # Configuration commands
        table.add_row("[bold yellow]📋 Configuration[/bold yellow]", "")
        table.add_row("/model", "Manage AI models")
        table.add_row("/model list", "List all available models")
        table.add_row("/model set <model>", "Switch model")
        table.add_row("/connect or /c", "SuperQode-style connection command")
        table.add_row("/connect byok <provider>/<model>", "Direct BYOK connect")
        table.add_row("/connect local <provider>/<model>", "Direct local connect")
        table.add_row("/connect acp [agent] [model]", "Direct ACP connect")
        table.add_row("/config", "Show configuration")
        table.add_row("/config show", "Show all settings")
        table.add_row("/config set <k> <v>", "Set configuration")
        table.add_row("", "")

        # Help & Documentation
        table.add_row("[bold yellow]📚 Help & Docs[/bold yellow]", "")
        table.add_row("/help", "Show this help")
        table.add_row("/ask <question>", "Ask about SuperOptiX")
        table.add_row("/help <topic>", "Topic-specific help")
        table.add_row("/docs <topic>", "Open documentation")
        table.add_row("/examples", "Show example workflows")
        table.add_row("", "")

        # Project Management
        table.add_row("[bold yellow]🤖 Agents & Project[/bold yellow]", "")
        table.add_row("/build", "🎨 Interactive agent builder")
        table.add_row("/build from-template <name>", "Build from template")
        table.add_row("/build resume", "Resume build session")
        table.add_row("/agents", "List all agents")
        table.add_row("/playbooks", "List all playbooks")
        table.add_row("/templates", "Show available templates")
        table.add_row("/status", "Show project status")
        table.add_row("", "")

        # MCP Integration
        table.add_row("[bold yellow]🔌 MCP Integration[/bold yellow]", "")
        table.add_row("/mcp", "Show MCP status")
        table.add_row("/mcp list", "List MCP servers")
        table.add_row("/mcp add <name> <cmd>", "Add MCP server")
        table.add_row("/mcp enable <name>", "Enable MCP server")
        table.add_row("/mcp connect <name>", "Connect MCP server now")
        table.add_row("/mcp disconnect <name>", "Disconnect MCP server")
        table.add_row("/mcp tools <name>", "List server tools")
        table.add_row("", "")

        table.add_row("[bold yellow]🔌 ACP Connection[/bold yellow]", "")
        table.add_row("/acp", "Show ACP status")
        table.add_row("/acp connect [agent] [model]", "Connect ACP agent")
        table.add_row("/acp send <prompt>", "Send a prompt to ACP agent")
        table.add_row("/acp disconnect", "Disconnect ACP agent")
        table.add_row("", "")

        # Session & Tasks
        table.add_row("[bold yellow]📊 Session & Tasks[/bold yellow]", "")
        table.add_row("/session", "Show session info")
        table.add_row("/session context", "Show context files")
        table.add_row("/session toggle", "Toggle status bar")
        table.add_row("/tasks", "List background tasks")
        table.add_row("/tasks running", "Show running tasks")
        table.add_row("", "")

        # Conversation
        table.add_row("[bold yellow]💬 Conversation[/bold yellow]", "")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/history", "Show history")
        table.add_row("/exit, /quit", "Exit SuperOptiX")

        self.console.print(table)

        self.console.print("\n[bold cyan]💡 Tips:[/bold cyan]")
        self.console.print("• Natural language mode [yellow][BETA][/yellow]!")
        self.console.print(
            "• Use traditional CLI: [cyan]super agent compile <name>[/cyan]"
        )
        self.console.print(
            "• Type [bold]/help <topic>[/bold] for detailed help on a topic\n"
        )

    def _show_topic_help(self, topic: str):
        """Show help for specific topic."""
        topic = topic.lower()

        if topic in ["agents", "agent"]:
            self.console.print("\n[bold cyan]Agent Management Help[/bold cyan]\n")
            self.console.print("Traditional CLI commands:")
            self.console.print(
                "  [cyan]super agent compile <name>[/cyan]  - Compile agent"
            )
            self.console.print(
                "  [cyan]super agent optimize <name>[/cyan] - Optimize agent"
            )
            self.console.print(
                "  [cyan]super agent evaluate <name>[/cyan] - Evaluate agent"
            )
            self.console.print(
                '  [cyan]super agent run <name> --goal "..."[/cyan] - Run agent\n'
            )
            self.console.print("Slash commands:")
            self.console.print("  [cyan]/agents[/cyan] - List all agents\n")

        elif topic in ["model", "models"]:
            self.console.print("\n[bold cyan]Model Management Help[/bold cyan]\n")
            self.console.print("Slash commands:")
            self.console.print("  [cyan]/model[/cyan] - Show current model")
            self.console.print("  [cyan]/model list[/cyan] - List all available models")
            self.console.print("  [cyan]/model set <model>[/cyan] - Switch model\n")
            self.console.print("Traditional CLI:")
            self.console.print("  [cyan]super model list[/cyan]")
            self.console.print("  [cyan]super model install llama3.1:8b[/cyan]\n")

        else:
            self.console.print(f"\n[yellow]No help available for:[/yellow] {topic}")
            self.console.print("[dim]Type [bold]/help[/bold] for all commands[/dim]\n")

    def cmd_model(self, *args):
        """Handle /model commands."""
        if not args:
            self._show_current_model()
        elif args[0] == "list":
            self._list_models()
        elif args[0] == "set" and len(args) > 1:
            self._set_model(args[1])
        else:
            self.console.print(
                f"\n[red]Unknown /model subcommand:[/red] {args[0] if args else 'none'}"
            )
            self.console.print("[dim]Usage: /model [list|set <model>][/dim]\n")

    def _show_current_model(self):
        """Show current model configuration."""
        self.console.print("\n[bold cyan]Current Model Configuration[/bold cyan]\n")
        self.console.print(
            f"• Provider: [green]{self.config.get('provider', 'not set')}[/green]"
        )
        self.console.print(
            f"• Model: [yellow]{self.config.get('model', 'not set')}[/yellow]"
        )

        if self.config.get("provider") == "ollama":
            self.console.print(
                f"• API Base: [dim]{self.config.get('api_base', 'http://localhost:11434')}[/dim]"
            )

            # Check status
            try:
                import requests

                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    self.console.print("• Status: [green]✅ Connected[/green]")
                else:
                    self.console.print("• Status: [red]❌ Not responding[/red]")
            except:
                self.console.print("• Status: [red]❌ Not running[/red]")

        self.console.print("\n[dim]Commands:[/dim]")
        self.console.print("[dim]  /model list - List available models[/dim]")
        self.console.print("[dim]  /model set <model> - Switch model[/dim]\n")

    def _list_models(self):
        """List all available models."""
        self.console.print()

        # Title panel
        title_panel = Panel(
            Align.center(Text("Available AI Models", style="bold bright_cyan")),
            border_style="bright_magenta",
            padding=(1, 3),
            subtitle="[dim]Choose your AI provider[/dim]",
        )

        self.console.print(title_panel)
        self.console.print()
        local_catalog = self.provider_catalog.get("local", {})
        byok_catalog = self.provider_catalog.get("byok", {})

        self.console.print("[bold green]🏠 LOCAL PROVIDERS[/bold green]\n")
        for provider_id, entry in list(local_catalog.items())[:12]:
            examples = ", ".join(entry.example_models[:3]) if entry.example_models else "no examples"
            self.console.print(f"  • [cyan]{provider_id}[/cyan] ({entry.name})")
            self.console.print(f"    [dim]{examples}[/dim]")

        self.console.print("\n" + "─" * 60 + "\n")
        self.console.print("[bold cyan]☁️  BYOK PROVIDERS[/bold cyan]\n")
        for provider_id, entry in list(byok_catalog.items())[:20]:
            env_hint = entry.env_vars[0] if entry.env_vars else "no-key"
            examples = ", ".join(entry.example_models[:2]) if entry.example_models else "no examples"
            self.console.print(f"  • [cyan]{provider_id}[/cyan] ({entry.name}) [dim]{env_hint}[/dim]")
            self.console.print(f"    [dim]{examples}[/dim]")

        self.console.print()
        self.console.print("[dim]Connect examples:[/dim]")
        self.console.print("[dim]  /connect local ollama/llama3.2:3b[/dim]")
        self.console.print("[dim]  /connect byok openai/gpt-4o[/dim]")
        self.console.print("[dim]  /connect byok anthropic/claude-sonnet-4[/dim]\n")

    def _set_model(self, model_name: str):
        """Set/switch model."""
        # Update config
        from superoptix.cli.commands.conversational import save_config

        # Support provider/model format.
        provider_prefix = None
        bare_model = model_name
        if "/" in model_name:
            provider_prefix, bare_model = model_name.split("/", 1)
            provider_prefix = provider_prefix.strip().lower()
            bare_model = bare_model.strip()

        # Determine provider from model name
        if provider_prefix == "openai" or bare_model.startswith("gpt-4") or bare_model.startswith("gpt-3"):
            # OpenAI cloud models
            self.config["provider"] = "openai"
            self.config["model"] = bare_model

            # Check for API key
            if "api_key" not in self.config and not os.getenv("OPENAI_API_KEY"):
                self.console.print("\n[yellow]⚠️  OPENAI_API_KEY not set[/yellow]")
                self.console.print(
                    "Set it with: [cyan]/config set OPENAI_API_KEY sk-...[/cyan]\n"
                )
                return

        elif provider_prefix == "anthropic" or bare_model.startswith("claude"):
            # Anthropic cloud models
            self.config["provider"] = "anthropic"
            self.config["model"] = bare_model

            if "api_key" not in self.config and not os.getenv("ANTHROPIC_API_KEY"):
                self.console.print("\n[yellow]⚠️  ANTHROPIC_API_KEY not set[/yellow]")
                self.console.print(
                    "Set it with: [cyan]/config set ANTHROPIC_API_KEY sk-...[/cyan]\n"
                )
                return

        elif provider_prefix in {"google", "gemini"}:
            self.config["provider"] = "google"
            self.config["model"] = bare_model

        else:
            # Other local models via Ollama
            self.config["provider"] = "ollama"
            self.config["model"] = bare_model
            self.config["api_base"] = "http://localhost:11434"

        save_config(self.config)

        # Reload chat agent to pick up new model (for conversation only)
        if self.chat_agent:
            try:
                self.chat_agent.reload_config()
                self.console.print(
                    f"[dim]Chat agent reloaded with new model (for conversation only)[/dim]"
                )
            except Exception as e:
                self.console.print(f"[dim]Chat agent reload: {e}[/dim]")

        self.console.print(f"\n[green]✅ Switched to:[/green] {self.config['model']}")
        self.console.print(f"[dim]Provider: {self.config['provider']}[/dim]\n")

    def cmd_config(self, *args):
        """Handle /config commands."""
        if not args:
            self._show_config()
        elif args[0] == "show":
            self._show_config_detailed()
        elif args[0] == "set" and len(args) > 2:
            self._set_config(args[1], " ".join(args[2:]))
        elif args[0] == "reset":
            self._reset_config()
        else:
            self.console.print(f"\n[red]Unknown /config subcommand[/red]")
            self.console.print(
                "[dim]Usage: /config [show|set <key> <value>|reset][/dim]\n"
            )

    def _show_config(self):
        """Show current configuration."""
        self.console.print("\n[bold cyan]Current Configuration[/bold cyan]\n")

        self.console.print("[bold]Model:[/bold]")
        self.console.print(
            f"  • Provider: [green]{self.config.get('provider', 'not set')}[/green]"
        )
        self.console.print(
            f"  • Model: [yellow]{self.config.get('model', 'not set')}[/yellow]"
        )

        self.console.print("\n[bold]Project:[/bold]")
        self.console.print(f"  • Path: [dim]{Path.cwd()}[/dim]")

        # Check for agents
        agents_dir = Path.cwd() / "agents"
        if agents_dir.exists():
            agent_count = len(list(agents_dir.glob("*_playbook.yaml")))
            self.console.print(f"  • Agents: {agent_count}")
        else:
            self.console.print("  • Agents: [dim]Not in a SuperOptiX project[/dim]")

        self.console.print("\n[dim]Commands:[/dim]")
        self.console.print("[dim]  /config show - Show detailed settings[/dim]")
        self.console.print("[dim]  /config set <key> <value> - Update setting[/dim]\n")

    def _show_config_detailed(self):
        """Show detailed configuration."""
        self.console.print("\n")

        # Model settings panel
        model_panel = Panel(
            f"[bold]Provider:[/bold] {self.config.get('provider', 'not set')}\n"
            f"[bold]Model:[/bold] {self.config.get('model', 'not set')}\n"
            f"[bold]API Base:[/bold] {self.config.get('api_base', 'N/A')}",
            title="[bold cyan]📋 Model Settings[/bold cyan]",
            border_style="cyan",
        )
        self.console.print(model_panel)

        # Project settings panel
        agents_dir = Path.cwd() / "agents"
        agent_count = (
            len(list(agents_dir.glob("*_playbook.yaml"))) if agents_dir.exists() else 0
        )

        project_panel = Panel(
            f"[bold]Path:[/bold] {Path.cwd()}\n[bold]Agents:[/bold] {agent_count}",
            title="[bold green]📁 Project Settings[/bold green]",
            border_style="green",
        )
        self.console.print(project_panel)

        self.console.print()

    def _set_config(self, key: str, value: str):
        """Set configuration value."""
        from superoptix.cli.commands.conversational import save_config

        self.config[key] = value
        save_config(self.config)

        self.console.print(
            f"\n[green]✅ Configuration updated:[/green] {key} = {value}\n"
        )

    def _reset_config(self):
        """Reset configuration."""
        from rich.prompt import Confirm

        if Confirm.ask("\n[yellow]Reset all configuration to defaults?[/yellow]"):
            config_path = Path.home() / ".superoptix" / "config.yaml"
            if config_path.exists():
                config_path.unlink()

            self.console.print("\n[green]✅ Configuration reset![/green]")
            self.console.print(
                "[dim]Restart SuperOptiX to run setup wizard again.[/dim]\n"
            )

    def cmd_agents(self, *args):
        """List all agents (uses super agent list command)."""
        import subprocess

        self.console.print("\n[bold cyan]📦 Available Agents[/bold cyan]\n")

        # Run super agent list command
        try:
            result = subprocess.run(
                ["super", "agent", "list"],
                capture_output=True,
                text=True,
                cwd=str(Path.cwd()),
            )

            if result.returncode == 0 and result.stdout:
                # Display the output from super agent list
                self.console.print(result.stdout)
            else:
                # Fallback - show basic message
                self.console.print("[yellow]⚠️  Could not list agents[/yellow]")
                self.console.print("[dim]Try: [cyan]super agent list[/cyan][/dim]\n")

        except Exception as e:
            self.console.print(f"[yellow]⚠️  Error listing agents: {e}[/yellow]")
            self.console.print("[dim]Try: [cyan]super agent list[/cyan][/dim]\n")

    def cmd_playbooks(self, *args):
        """List all playbooks."""
        self.console.print("\n[bold cyan]Available Playbooks[/bold cyan]\n")

        if not self.playbook_registry:
            self.console.print("[yellow]Playbook registry not available[/yellow]\n")
            return

        # Get counts
        counts = self.playbook_registry.get_count()

        # Library playbooks
        library_playbooks = self.playbook_registry.list_by_source("library")
        if library_playbooks:
            self.console.print(
                f"[bold green]📦 Library Templates ({counts['library']}):[/bold green]"
            )
            for pb in library_playbooks[:10]:
                features_str = (
                    f" [{', '.join(pb['features'])}]" if pb["features"] else ""
                )
                self.console.print(f"  • [cyan]{pb['name']}[/cyan]{features_str}")
                self.console.print(
                    f"    [dim]{pb['description'][:60]}...[/dim]"
                    if len(pb["description"]) > 60
                    else f"    [dim]{pb['description']}[/dim]"
                )

            if len(library_playbooks) > 10:
                self.console.print(
                    f"  [dim]... and {len(library_playbooks) - 10} more[/dim]"
                )
            self.console.print()

        # User playbooks
        user_playbooks = self.playbook_registry.list_by_source("user_project")
        if user_playbooks:
            self.console.print(
                f"[bold yellow]📁 Your Project ({counts['user_project']}):[/bold yellow]"
            )
            for pb in user_playbooks:
                features_str = (
                    f" [{', '.join(pb['features'])}]" if pb["features"] else ""
                )
                self.console.print(f"  • [cyan]{pb['name']}[/cyan]{features_str}")
            self.console.print()

        self.console.print(
            "[dim]Create new: [cyan]super spec generate genie <name>[/cyan][/dim]\n"
        )

    def cmd_templates(self, *args):
        """Show available templates."""
        self.console.print("\n[bold cyan]Available Templates[/bold cyan]\n")
        self.console.print("[bold green]SuperSpec Tiers:[/bold green]")
        self.console.print(
            "  • [cyan]oracles[/cyan] - Basic agent with chain-of-thought"
        )
        self.console.print(
            "  • [cyan]genies[/cyan] - Advanced agent with memory, tools, RAG\n"
        )
        self.console.print(
            "[dim]Generate: [cyan]super spec generate genie my_agent[/cyan][/dim]\n"
        )

    def cmd_docs(self, *args):
        """Open documentation."""
        if args:
            topic = args[0]
            self.console.print(f"\n[cyan]📖 Documentation for:[/cyan] {topic}")
            self.console.print(
                f"[dim]Visit: https://superoptix.ai/guides/{topic}/[/dim]\n"
            )
        else:
            self.console.print("\n[cyan]📖 Documentation[/cyan]")
            self.console.print("[dim]Visit: https://superoptix.ai[/dim]")
            self.console.print(
                "\n[dim]Or run: [cyan]super docs[/cyan] for comprehensive guide[/dim]\n"
            )

    def cmd_examples(self, *args):
        """Show example workflows."""
        self.console.print("\n[bold cyan]Example Workflows[/bold cyan]\n")

        self.console.print("[bold yellow]1. Build and Optimize Agent:[/bold yellow]")
        self.console.print("   [cyan]super spec generate genie code_reviewer[/cyan]")
        self.console.print("   [cyan]super agent compile code_reviewer[/cyan]")
        self.console.print(
            "   [cyan]super agent optimize code_reviewer --auto medium[/cyan]"
        )
        self.console.print("   [cyan]super agent evaluate code_reviewer[/cyan]\n")

        self.console.print("[bold yellow]2. Quick Agent from Template:[/bold yellow]")
        self.console.print("   [cyan]super agent pull developer[/cyan]")
        self.console.print("   [cyan]super agent compile developer[/cyan]")
        self.console.print(
            '   [cyan]super agent run developer --goal "Build a CLI tool"[/cyan]\n'
        )

        self.console.print("[bold yellow]3. Multi-Agent Orchestra:[/bold yellow]")
        self.console.print("   [cyan]super orchestra create my_workflow[/cyan]")
        self.console.print(
            '   [cyan]super orchestra run my_workflow --goal "Complex task"[/cyan]\n'
        )

    def cmd_status(self, *args):
        """Show project status."""
        self.console.print("\n[bold cyan]Project Status[/bold cyan]\n")

        # Check if in SuperOptiX project
        if not (Path.cwd() / ".super").exists():
            self.console.print("[yellow]⚠️  Not in a SuperOptiX project[/yellow]")
            self.console.print(
                "[dim]Initialize: [cyan]super init my_project[/cyan][/dim]\n"
            )
            return

        self.console.print(f"[green]✅ SuperOptiX Project[/green]\n")
        self.console.print(f"• Path: [dim]{Path.cwd()}[/dim]")

        # Count agents
        agents_dir = Path.cwd() / "agents"
        if agents_dir.exists():
            agent_count = len(list(agents_dir.glob("*_playbook.yaml")))
            self.console.print(f"• Agents: {agent_count}")

        # Count pipelines
        pipelines_dir = Path.cwd() / "pipelines"
        if pipelines_dir.exists():
            pipeline_count = len(list(pipelines_dir.glob("*_pipeline.py")))
            self.console.print(f"• Compiled: {pipeline_count}")

        # Count orchestras
        orchestras_dir = Path.cwd() / "orchestras"
        if orchestras_dir.exists():
            orchestra_count = len(list(orchestras_dir.glob("*.yaml")))
            self.console.print(f"• Orchestras: {orchestra_count}")

        self.console.print()

    def cmd_clear(self, *args):
        """Clear conversation history."""
        # Clear screen
        os.system("clear" if os.name == "posix" else "cls")
        self.console.print("\n[green]✅ Conversation history cleared[/green]\n")

    def cmd_history(self, *args):
        """Show conversation history."""
        self.console.print(
            "\n[yellow]💬 Conversation history feature coming soon![/yellow]\n"
        )

    def cmd_connect(self, *args):
        """Handle /connect (SuperQode-style ACP/BYOK/LOCAL connections)."""
        if not args:
            self._connect_interactive_root()
            return

        sub = args[0].lower()
        if sub in {"status"}:
            self._connect_show_status()
            return
        if sub in {"byok", "local"}:
            self._connect_mode(sub, list(args[1:]))
            return
        if sub == "acp":
            agent = args[1] if len(args) > 1 else None
            model = args[2] if len(args) > 2 else None
            self._connect_acp(agent=agent, model=model)
            return

        # Shortcut: /connect <provider>/<model> => BYOK
        provider, model = self._split_provider_model(sub, args[1] if len(args) > 1 else None)
        if provider and model:
            self._connect_byok(provider=provider, model=model, api_key_env=None)
            return

        self._connect_show_help()

    def _connect_mode(self, mode: str, args: list[str]):
        if not args:
            self._connect_interactive_mode(mode)
            return

        token = args[0].strip().lower()
        if token in {"!", "history"}:
            self._connect_show_history(mode)
            return
        if token in {"-", "last"}:
            self._connect_previous(mode)
            return

        provider, model = self._split_provider_model(args[0], args[1] if len(args) > 1 else None)
        if mode == "byok":
            api_key_env = args[2] if len(args) > 2 else None
            self._connect_byok(provider=provider, model=model, api_key_env=api_key_env)
            return
        endpoint = args[2] if len(args) > 2 else None
        self._connect_local(provider=provider, model=model, endpoint=endpoint)

    def _supports_interactive_picker(self) -> bool:
        return bool(radiolist_dialog and input_dialog and hasattr(self.console.file, "isatty") and self.console.file.isatty())

    def _connect_interactive_root(self):
        if not self._supports_interactive_picker():
            self._connect_show_help()
            return
        choice = radiolist_dialog(
            title="Connect Runtime",
            text="Select a runtime mode:",
            values=[
                ("acp", "ACP Agent (coding agent protocol)"),
                ("byok", "BYOK Provider (cloud API key)"),
                ("local", "Local Provider (self-hosted model)"),
                ("status", "Show current connection status"),
            ],
        ).run()
        if not choice:
            return
        if choice == "status":
            self._connect_show_status()
            return
        if choice == "acp":
            self._connect_interactive_acp()
            return
        self._connect_interactive_mode(choice)

    def _connect_interactive_mode(self, mode: str):
        catalog = self.provider_catalog.get(mode, {})
        if not catalog:
            self.console.print(f"\n[yellow]No providers available for {mode}.[/yellow]\n")
            return
        if not self._supports_interactive_picker():
            self._connect_show_mode_catalog(mode)
            return

        provider_values = []
        for provider_id, entry in sorted(catalog.items(), key=lambda x: x[0]):
            label = f"{provider_id} - {entry.name}"
            if mode == "byok" and entry.env_vars:
                label += f" ({entry.env_vars[0]})"
            provider_values.append((provider_id, label))
        provider = radiolist_dialog(
            title=f"{mode.upper()} Provider",
            text="Select provider:",
            values=provider_values,
        ).run()
        if not provider:
            return
        entry = catalog.get(provider)
        models = list((entry.example_models if entry else [])[:20])
        if not models:
            model = input_dialog(
                title=f"{mode.upper()} Model",
                text=f"Enter model for provider '{provider}':",
            ).run()
        else:
            values = [(m, m) for m in models] + [("__custom__", "Custom model...")]
            selected = radiolist_dialog(
                title=f"{mode.upper()} Model",
                text=f"Select model for {provider}:",
                values=values,
            ).run()
            if not selected:
                return
            if selected == "__custom__":
                model = input_dialog(
                    title=f"{mode.upper()} Model",
                    text=f"Enter custom model for '{provider}':",
                ).run()
            else:
                model = selected
        if not model:
            return

        if mode == "byok":
            default_env = entry.env_vars[0] if entry and entry.env_vars else ""
            api_env = input_dialog(
                title="BYOK API Key Env",
                text=f"API key env var for {provider} (optional):",
                default=default_env,
            ).run()
            self._connect_byok(provider=provider, model=model, api_key_env=(api_env or default_env or None))
            return

        default_endpoint = entry.default_base_url if entry else ""
        endpoint = input_dialog(
            title="Local Endpoint",
            text=f"Endpoint for {provider} (optional):",
            default=default_endpoint or "",
        ).run()
        self._connect_local(provider=provider, model=model, endpoint=(endpoint or default_endpoint or None))

    def _connect_interactive_acp(self):
        if self._supports_interactive_picker():
            agent = radiolist_dialog(
                title="ACP Agent",
                text="Select ACP agent:",
                values=[
                    ("opencode", "opencode"),
                    ("claude-code", "claude-code"),
                    ("custom", "Custom agent id..."),
                ],
            ).run()
            if not agent:
                return
            if agent == "custom":
                agent = input_dialog(title="ACP Agent", text="Enter ACP agent id:").run()
                if not agent:
                    return
            model = input_dialog(
                title="ACP Model (optional)",
                text="Model override (leave blank for saved/default):",
            ).run()
            self._connect_acp(agent=agent, model=(model or None))
            return

        agent = Prompt.ask("ACP agent", default="opencode")
        model = Prompt.ask("ACP model (optional)", default="")
        self._connect_acp(agent=agent, model=(model or None))

    def _connect_show_help(self):
        panel = Panel(
            Text.from_markup(
                "[bold cyan]Super Connection Commands[/bold cyan]\n\n"
                "[green]/connect status[/green]                        Show active profile/runtime\n"
                "[green]/connect[/green]                               Interactive keyboard picker\n"
                "[green]/connect acp[/green] [agent] [model]          Connect ACP agent\n"
                "[green]/connect byok[/green] <provider>/<model> [env] Connect BYOK provider/model\n"
                "[green]/connect local[/green] <provider>/<model>      Connect local provider/model\n"
                "[green]/connect byok ![/green] or [green]/connect local ![/green]     Show history\n"
                "[green]/connect byok -[/green] or [green]/connect local -[/green]     Switch previous\n\n"
                "[dim]Examples:[/dim]\n"
                "[dim]/connect acp opencode gpt-4o-mini[/dim]\n"
                "[dim]/connect byok openai/gpt-4o OPENAI_API_KEY[/dim]\n"
                "[dim]/connect local ollama/llama3.2:3b[/dim]"
            ),
            border_style="bright_cyan",
            title="[bold]🔌 Connect[/bold]",
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()

    def _connect_show_status(self):
        profile = self.connection_store.profile(self.connection_store.load())
        active = profile.get("active_connection") or {}
        self.console.print()
        self.console.print("[bold cyan]Connection Status[/bold cyan]")
        self.console.print(f"  • Active: [green]{active.get('type', '-')}/{active.get('name') or '-'}[/green]")
        self.console.print(f"  • BYOK: [dim]{profile.get('byok', {}) or '-'}[/dim]")
        self.console.print(f"  • LOCAL: [dim]{profile.get('local', {}) or '-'}[/dim]")
        self.console.print(f"  • ACP: [dim]{profile.get('acp', {}) or '-'}[/dim]")
        self.console.print()

    def _connect_show_mode_catalog(self, mode: str):
        catalog = self.provider_catalog.get(mode, {})
        if not catalog:
            self.console.print(f"\n[yellow]No providers available for {mode}.[/yellow]\n")
            return
        self.console.print()
        title = "BYOK Providers" if mode == "byok" else "Local Providers"
        table = Table(title=title, header_style="bold cyan")
        table.add_column("Provider", style="bold")
        table.add_column("API Key Env" if mode == "byok" else "Endpoint")
        table.add_column("Example Models")
        for entry in catalog.values():
            key_or_endpoint = (
                (entry.env_vars[0] if entry.env_vars else "-")
                if mode == "byok"
                else (entry.default_base_url or "-")
            )
            examples = ", ".join(entry.example_models[:3]) if entry.example_models else "-"
            table.add_row(entry.provider_id, key_or_endpoint, examples)
        self.console.print(table)
        self.console.print()

    def _connect_show_history(self, mode: str):
        items = [h for h in self.connection_store.connection_history(limit=20) if h.get("type") == mode]
        self.console.print()
        if not items:
            self.console.print(f"[yellow]No {mode.upper()} connection history yet.[/yellow]\n")
            return
        self.console.print(f"[bold cyan]{mode.upper()} History[/bold cyan]")
        for idx, item in enumerate(items[:10], start=1):
            self.console.print(f"  {idx}. [green]{item.get('type')}/{item.get('name') or '-'}[/green] [dim]{item.get('updated_at', '')}[/dim]")
        self.console.print()

    def _connect_previous(self, mode: str):
        items = [h for h in self.connection_store.connection_history(limit=20) if h.get("type") == mode]
        if len(items) < 2:
            self.console.print(f"\n[yellow]No previous {mode.upper()} connection found.[/yellow]\n")
            return
        previous = items[1]
        name = previous.get("name")
        profile = self.connection_store.profile(self.connection_store.load())
        if mode == "byok":
            cfg = profile.get("byok", {}) or {}
            self._connect_byok(cfg.get("provider") or name, cfg.get("model"), cfg.get("api_key_env"))
        else:
            cfg = profile.get("local", {}) or {}
            self._connect_local(cfg.get("provider") or name, cfg.get("model"), cfg.get("endpoint"))

    def _split_provider_model(self, first: str | None, second: str | None) -> tuple[str | None, str | None]:
        if not first:
            return None, None
        raw = first.strip()
        if "/" in raw:
            provider, model = raw.split("/", 1)
            return provider.strip().lower() or None, model.strip() or None
        provider = raw.lower()
        return provider, (second.strip() if second else None)

    def _connect_byok(self, provider: str | None, model: str | None, api_key_env: str | None):
        if not provider:
            self.console.print("\n[yellow]Usage: /connect byok <provider>/<model> [API_KEY_ENV][/yellow]\n")
            return
        catalog = self.provider_catalog.get("byok", {})
        entry = catalog.get(provider)
        if not model and entry and entry.example_models:
            model = entry.example_models[0]
        if not model:
            self.console.print("\n[yellow]Missing model. Example: /connect byok openai/gpt-4o[/yellow]\n")
            return

        resolved_env = api_key_env or (entry.env_vars[0] if entry and entry.env_vars else None)
        base_url = entry.default_base_url if entry else None
        try:
            self.connection_store.set_byok(provider=provider, model=model, api_key_env=resolved_env, base_url=base_url)
            self.connection_store.set_active("byok", provider)
        except Exception as exc:
            self.console.print(f"\n[red]❌ Failed to save BYOK connection:[/red] {exc}\n")
            return

        self.config["provider"] = provider
        self.config["model"] = model
        if resolved_env:
            self.config["api_key_env"] = resolved_env
            if os.getenv(resolved_env):
                self.config["api_key"] = os.getenv(resolved_env)
        if base_url:
            self.config["base_url"] = base_url
        self._persist_and_reload_config()

        env_state = "set" if (resolved_env and os.getenv(resolved_env)) else "missing"
        self.console.print()
        self.console.print(f"[green]✅ BYOK connected:[/green] {provider}/{model}")
        self.console.print(f"[dim]API key env: {resolved_env or '-'} ({env_state})[/dim]")
        self.console.print()

    def _connect_local(self, provider: str | None, model: str | None, endpoint: str | None):
        if not provider:
            self.console.print("\n[yellow]Usage: /connect local <provider>/<model> [endpoint][/yellow]\n")
            return
        catalog = self.provider_catalog.get("local", {})
        entry = catalog.get(provider)
        if not model and entry and entry.example_models:
            model = entry.example_models[0]
        if not model:
            self.console.print("\n[yellow]Missing model. Example: /connect local ollama/llama3.2:3b[/yellow]\n")
            return
        resolved_endpoint = endpoint or (entry.default_base_url if entry else None)
        try:
            self.connection_store.set_local(provider=provider, model=model, endpoint=resolved_endpoint)
            self.connection_store.set_active("local", provider)
        except Exception as exc:
            self.console.print(f"\n[red]❌ Failed to save LOCAL connection:[/red] {exc}\n")
            return

        self.config["provider"] = provider
        self.config["model"] = model
        if resolved_endpoint:
            self.config["api_base"] = resolved_endpoint
        self._persist_and_reload_config()

        self.console.print()
        self.console.print(f"[green]✅ LOCAL connected:[/green] {provider}/{model}")
        if resolved_endpoint:
            self.console.print(f"[dim]Endpoint: {resolved_endpoint}[/dim]")
        self.console.print()

    def _persist_and_reload_config(self):
        from superoptix.cli.commands.conversational import save_config

        try:
            save_config(self.config)
        except Exception as exc:
            self.console.print(f"[yellow]⚠️  Config save warning:[/yellow] {exc}")
        if self.chat_agent:
            try:
                self.chat_agent.reload_config()
            except Exception:
                pass

    def cmd_mcp(self, *args):
        """Handle /mcp commands for MCP server management."""
        if not self.mcp_client:
            self.console.print("\n[yellow]⚠️  MCP client not available[/yellow]")
            self.console.print("[dim]Install with: pip install superoptix[mcp][/dim]\n")
            return

        if not args:
            self._show_mcp_status()
        elif args[0] == "list":
            self._list_mcp_servers()
        elif args[0] == "add" and len(args) >= 3:
            self._add_mcp_server(args[1], args[2], args[3:])
        elif args[0] == "enable" and len(args) > 1:
            self._enable_mcp_server(args[1])
        elif args[0] == "disable" and len(args) > 1:
            self._disable_mcp_server(args[1])
        elif args[0] == "connect" and len(args) > 1:
            self._connect_mcp_server(args[1])
        elif args[0] == "disconnect" and len(args) > 1:
            self._disconnect_mcp_server(args[1])
        elif args[0] == "reload":
            self._reload_mcp_servers()
        elif args[0] == "tools" and len(args) > 1:
            self._list_mcp_tools(args[1])
        else:
            self.console.print(f"\n[red]Unknown /mcp subcommand[/red]")
            self.console.print("[dim]Usage:[/dim]")
            self.console.print("  [cyan]/mcp[/cyan] - Show MCP status")
            self.console.print("  [cyan]/mcp list[/cyan] - List MCP servers")
            self.console.print(
                "  [cyan]/mcp add <name> <command> [args...][/cyan] - Add server"
            )
            self.console.print("  [cyan]/mcp enable <name>[/cyan] - Enable server")
            self.console.print("  [cyan]/mcp disable <name>[/cyan] - Disable server")
            self.console.print("  [cyan]/mcp connect <name>[/cyan] - Connect server")
            self.console.print(
                "  [cyan]/mcp disconnect <name>[/cyan] - Disconnect server"
            )
            self.console.print("  [cyan]/mcp reload[/cyan] - Reload MCP config")
            self.console.print("  [cyan]/mcp tools <name>[/cyan] - List server tools\n")

    def _show_mcp_status(self):
        """Show MCP client status."""
        self.console.print()

        status_panel = Panel(
            f"[bold cyan]MCP Client Status[/bold cyan]\n\n"
            f"• Available: [{'green]✅' if self.mcp_client.available else 'red]❌'}\n"
            f"• Configured servers: {len(self.mcp_client.servers)}\n"
            f"• Active connections: {len(self.mcp_client.sessions)}\n\n"
            f"[dim]Use [cyan]/mcp list[/cyan] to see all servers[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )

        self.console.print(status_panel)
        self.console.print()

    def _list_mcp_servers(self):
        """List all MCP servers."""
        servers = self.mcp_client.list_servers()

        if not servers:
            self.console.print("\n[yellow]No MCP servers configured[/yellow]\n")
            return

        self.console.print()

        # Title panel
        title_panel = Panel(
            Align.center(Text("Configured MCP Servers", style="bold bright_cyan")),
            border_style="bright_magenta",
            padding=(1, 3),
        )

        self.console.print(title_panel)
        self.console.print()

        # Servers table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Name", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Connection", style="magenta")
        table.add_column("Command", style="dim")
        table.add_column("Description", style="cyan")

        status_map = {s.name: s for s in self.mcp_client.list_server_status()}
        for server in servers:
            status = "✅ Enabled" if server.enabled else "❌ Disabled"
            conn = status_map.get(server.name)
            conn_status = conn.state.value if conn else "disconnected"
            if conn_status == "connected":
                conn_status = "🟢 connected"
            elif conn_status == "connecting":
                conn_status = "🟡 connecting"
            elif conn_status == "error":
                conn_status = "🔴 error"
            else:
                conn_status = "⚪ disconnected"
            command = f"{server.command} {' '.join(server.args[:2])}"
            if len(server.args) > 2:
                command += "..."

            table.add_row(
                server.name, status, conn_status, command, server.description or "-"
            )

        self.console.print(table)
        self.console.print()

        self.console.print("[dim]Commands:[/dim]")
        self.console.print("  [cyan]/mcp enable <name>[/cyan] - Enable a server")
        self.console.print("  [cyan]/mcp connect <name>[/cyan] - Connect a server")
        self.console.print("  [cyan]/mcp disconnect <name>[/cyan] - Disconnect a server")
        self.console.print("  [cyan]/mcp tools <name>[/cyan] - List server's tools")
        self.console.print(
            "  [cyan]/mcp add <name> <cmd> [args][/cyan] - Add new server\n"
        )

    def _add_mcp_server(self, name: str, command: str, args: list):
        """Add a new MCP server."""
        self.mcp_client.add_server(name, command, list(args))
        self.console.print(f"\n[green]✅ Added MCP server:[/green] {name}")
        self.console.print(f"[dim]Command:[/dim] {command} {' '.join(args)}\n")

    def _enable_mcp_server(self, name: str):
        """Enable an MCP server."""
        self.mcp_client.enable_server(name)
        self.console.print(f"\n[green]✅ Enabled MCP server:[/green] {name}\n")

    def _disable_mcp_server(self, name: str):
        """Disable an MCP server."""
        self.mcp_client.disable_server(name)
        self.console.print(f"\n[yellow]⚠️  Disabled MCP server:[/yellow] {name}\n")

    def _connect_mcp_server(self, name: str):
        """Connect an MCP server."""
        ok = self.mcp_client.connect_server_sync(name)
        if ok:
            self.console.print(f"\n[green]✅ Connected MCP server:[/green] {name}\n")
        else:
            self.console.print(
                f"\n[yellow]⚠️  Failed to connect MCP server:[/yellow] {name}\n"
            )

    def _disconnect_mcp_server(self, name: str):
        """Disconnect an MCP server."""
        ok = self.mcp_client.disconnect_server_sync(name)
        if ok:
            self.console.print(
                f"\n[green]✅ Disconnected MCP server:[/green] {name}\n"
            )
        else:
            self.console.print(
                f"\n[yellow]⚠️  Failed to disconnect MCP server:[/yellow] {name}\n"
            )

    def _reload_mcp_servers(self):
        """Reload MCP server config from disk."""
        self.mcp_client.reload_config()
        self.console.print("\n[green]✅ Reloaded MCP configuration[/green]\n")

    def _list_mcp_tools(self, server_name: str):
        """List tools available on an MCP server."""
        self.console.print(
            f"\n[bold cyan]Fetching tools from:[/bold cyan] {server_name}\n"
        )

        tools = self.mcp_client.list_tools_sync(server_name)

        if not tools:
            self.console.print(
                "[yellow]No tools available or server not connected[/yellow]\n"
            )
            return

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Tool Name", style="yellow")
        table.add_column("Description", style="cyan")

        for tool in tools:
            table.add_row(tool.get("name", "unknown"), tool.get("description", "-"))

        self.console.print(table)
        self.console.print()

    def cmd_acp(self, *args):
        """Handle /acp commands for ACP session lifecycle."""
        if not self.acp_client:
            self.console.print("\n[yellow]⚠️  ACP client not available[/yellow]\n")
            return

        if not args:
            self._show_acp_status()
            return

        sub = args[0]
        if sub == "status":
            self._show_acp_status()
        elif sub == "connect":
            agent = args[1] if len(args) > 1 else None
            model = args[2] if len(args) > 2 else None
            self._connect_acp(agent=agent, model=model)
        elif sub == "disconnect":
            self._disconnect_acp()
        elif sub == "send" and len(args) > 1:
            self._send_acp_prompt(" ".join(args[1:]))
        else:
            self.console.print(f"\n[red]Unknown /acp subcommand[/red]")
            self.console.print("[dim]Usage:[/dim]")
            self.console.print("  [cyan]/acp[/cyan] - Show ACP status")
            self.console.print(
                "  [cyan]/acp connect [agent] [model][/cyan] - Connect ACP agent"
            )
            self.console.print("  [cyan]/acp send <prompt>[/cyan] - Send ACP prompt")
            self.console.print(
                "  [cyan]/acp disconnect[/cyan] - Disconnect ACP session\n"
            )

    def _show_acp_status(self):
        connected = self.acp_client.is_connected()
        agent = self.acp_client.connected_agent() or "-"
        panel = Panel(
            f"[bold cyan]ACP Session[/bold cyan]\n\n"
            f"• Connected: {'[green]✅ yes[/green]' if connected else '[yellow]no[/yellow]'}\n"
            f"• Agent: {agent}\n\n"
            f"[dim]Use /acp connect [agent] [model] to start[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()

    def _connect_acp(self, agent: Optional[str], model: Optional[str]):
        from .acp_client import ACPSessionConfig
        from superoptix.cli.connection_state import ConnectionStateStore

        store = ConnectionStateStore()
        profile = store.profile(store.load())
        saved = profile.get("acp", {}) or {}

        resolved_agent = agent or saved.get("agent") or "opencode"
        command = saved.get("command") or _default_acp_command(resolved_agent)
        resolved_model = model or saved.get("model")

        if not command:
            self.console.print(
                "\n[yellow]No ACP command configured.[/yellow] Use `super connect acp --agent <id> --command \"...\"` first.\n"
            )
            return

        cfg = ACPSessionConfig(
            agent=resolved_agent,
            command=command,
            model=resolved_model,
            cwd=str(Path.cwd()),
        )
        ok = self.acp_client.connect_sync(cfg)
        if ok:
            self.console.print(
                f"\n[green]✅ ACP connected:[/green] agent={resolved_agent}"
                + (f", model={resolved_model}" if resolved_model else "")
            )
            store.set_acp(agent=resolved_agent, model=resolved_model, command=command)
            store.set_active("acp", resolved_agent)
            self.console.print()
        else:
            self.console.print(
                "\n[yellow]⚠️  ACP connection failed.[/yellow] Check your command and agent installation.\n"
            )

    def _disconnect_acp(self):
        self.acp_client.disconnect_sync()
        self.console.print("\n[green]✅ ACP disconnected[/green]\n")

    def _send_acp_prompt(self, prompt: str):
        if not self.acp_client.is_connected():
            self.console.print(
                "\n[yellow]ACP is not connected.[/yellow] Run `/acp connect` first.\n"
            )
            return

        with self.console.status("🧠 ACP agent thinking...", spinner="dots"):
            result = self.acp_client.send_prompt_sync(prompt)
        self.console.print()
        if not result.get("ok"):
            self.console.print(
                f"[red]ACP request failed:[/red] {result.get('error', 'unknown error')}\n"
            )
            return

        payload = result.get("result") or {}
        pretty = json.dumps(payload, indent=2, default=str)
        panel = Panel(
            pretty,
            title="[bold bright_cyan]ACP Response[/bold bright_cyan]",
            border_style="cyan",
            padding=(1, 1),
        )
        self.console.print(panel)
        self.console.print()

    def cmd_session(self, *args):
        """Handle /session commands for session management."""
        if not self.status_bar:
            self.console.print("\n[yellow]⚠️  Status bar not available[/yellow]\n")
            return

        if not args:
            # Show session summary
            self._show_session_summary()
        elif args[0] == "info":
            self._show_session_summary()
        elif args[0] == "context":
            self._show_session_context()
        elif args[0] == "reset":
            self._reset_session()
        elif args[0] == "toggle":
            self._toggle_status_bar()
        else:
            self.console.print(f"\n[red]Unknown /session subcommand[/red]")
            self.console.print("[dim]Usage:[/dim]")
            self.console.print("  [cyan]/session[/cyan] - Show session info")
            self.console.print(
                "  [cyan]/session info[/cyan] - Show detailed session info"
            )
            self.console.print("  [cyan]/session context[/cyan] - Show session context")
            self.console.print("  [cyan]/session reset[/cyan] - Reset session")
            self.console.print("  [cyan]/session toggle[/cyan] - Toggle status bar\n")

    def _show_session_summary(self):
        """Show session summary."""
        summary = self.status_bar.get_session_summary()

        self.console.print()

        panel_content = Text()
        panel_content.append("Session ID: ", style="dim")
        panel_content.append(f"{summary['session_id']}\n", style="bright_cyan")

        # Duration
        duration_mins = int(summary["duration_seconds"] / 60)
        duration_secs = int(summary["duration_seconds"] % 60)
        panel_content.append("Duration: ", style="dim")
        panel_content.append(f"{duration_mins}m {duration_secs}s\n", style="cyan")

        # Operations
        panel_content.append("Operations: ", style="dim")
        panel_content.append(f"{summary['operations_count']}\n", style="yellow")

        # Agent
        if summary["current_agent"]:
            panel_content.append("Current Agent: ", style="dim")
            panel_content.append(f"{summary['current_agent']}\n", style="bright_yellow")

        # Context files
        panel_content.append("Context Files: ", style="dim")
        panel_content.append(f"{summary['context_files']}\n", style="cyan")

        # Tasks
        tasks = summary["background_tasks"]
        panel_content.append("\nBackground Tasks:\n", style="bold cyan")
        panel_content.append(f"  Total: {tasks['total']}\n", style="white")
        if tasks["running"] > 0:
            panel_content.append(
                f"  Running: {tasks['running']}\n", style="bright_magenta"
            )
        if tasks["completed"] > 0:
            panel_content.append(f"  Completed: {tasks['completed']}\n", style="green")
        if tasks["failed"] > 0:
            panel_content.append(f"  Failed: {tasks['failed']}\n", style="red")

        panel = Panel(
            panel_content,
            title="[bold bright_cyan]📊 Session Summary[/bold bright_cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def _show_session_context(self):
        """Show session context files."""
        self.console.print("\n[bold cyan]Session Context[/bold cyan]\n")

        if not self.status_bar.session.context_files:
            self.console.print("[yellow]No files in context[/yellow]\n")
            return

        self.console.print(
            f"[green]{len(self.status_bar.session.context_files)} files tracked:[/green]\n"
        )

        for filepath in self.status_bar.session.context_files:
            self.console.print(f"  • [cyan]{filepath}[/cyan]")

        self.console.print()

    def _reset_session(self):
        """Reset current session."""
        from rich.prompt import Confirm

        if Confirm.ask("\n[yellow]Reset current session?[/yellow]"):
            self.status_bar.session = self.status_bar._init_session()
            self.console.print("\n[green]✅ Session reset![/green]\n")

    def _toggle_status_bar(self):
        """Toggle status bar visibility."""
        self.status_bar.toggle()
        status = "enabled" if self.status_bar.enabled else "disabled"
        self.console.print(f"\n[cyan]Status bar {status}[/cyan]\n")

    def cmd_tasks(self, *args):
        """Handle /tasks commands for background task management."""
        if not self.status_bar:
            self.console.print("\n[yellow]⚠️  Status bar not available[/yellow]\n")
            return

        if not args:
            # List all tasks
            self._list_background_tasks()
        elif args[0] == "list":
            self._list_background_tasks()
        elif args[0] == "running":
            self._list_running_tasks()
        elif args[0] == "clear":
            self._clear_completed_tasks()
        else:
            self.console.print(f"\n[red]Unknown /tasks subcommand[/red]")
            self.console.print("[dim]Usage:[/dim]")
            self.console.print("  [cyan]/tasks[/cyan] - List all tasks")
            self.console.print("  [cyan]/tasks list[/cyan] - List all tasks")
            self.console.print("  [cyan]/tasks running[/cyan] - List running tasks")
            self.console.print("  [cyan]/tasks clear[/cyan] - Clear completed tasks\n")

    def _list_background_tasks(self):
        """List all background tasks."""
        tasks = self.status_bar.session.background_tasks

        if not tasks:
            self.console.print("\n[yellow]No background tasks[/yellow]\n")
            return

        self.console.print()

        # Create table
        table = Table(show_header=True, header_style="bold cyan", border_style="cyan")

        table.add_column("ID", style="dim", width=15)
        table.add_column("Name", style="yellow")
        table.add_column("Status", width=12)
        table.add_column("Progress", width=20)

        for task in tasks:
            # Status with icon
            status_icons = {"running": "⚡", "completed": "✓", "failed": "✗"}
            status_colors = {
                "running": "bright_cyan",
                "completed": "green",
                "failed": "red",
            }

            status_icon = status_icons.get(task.get("status", "unknown"), "•")
            status_color = status_colors.get(task.get("status", "unknown"), "white")
            status_text = Text(
                f"{status_icon} {task.get('status', 'unknown')}", style=status_color
            )

            # Progress bar
            progress = task.get("progress", 0)
            bar_length = 10
            filled = int((progress / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            progress_text = Text(f"{bar} {progress}%", style=status_color)

            table.add_row(
                task.get("task_id", "unknown")[-12:],
                task.get("name", "unknown"),
                status_text,
                progress_text,
            )

        panel = Panel(
            table,
            title="[bold bright_cyan]⚡ Background Tasks[/bold bright_cyan]",
            border_style="cyan",
        )

        self.console.print(panel)
        self.console.print()

    def _list_running_tasks(self):
        """List only running tasks."""
        running_tasks = self.status_bar.get_running_tasks()

        if not running_tasks:
            self.console.print("\n[green]No tasks currently running[/green]\n")
            return

        self.console.print()
        self.console.print(
            f"[bold cyan]Running Tasks ({len(running_tasks)}):[/bold cyan]\n"
        )

        for task in running_tasks:
            progress = task.get("progress", 0)
            bar_length = 20
            filled = int((progress / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            self.console.print(f"  ⚡ [yellow]{task.get('name', 'unknown')}[/yellow]")
            self.console.print(f"     {bar} {progress}%")
            self.console.print()

    def _clear_completed_tasks(self):
        """Clear completed tasks from list."""
        before_count = len(self.status_bar.session.background_tasks)
        self.status_bar.session.background_tasks = [
            t
            for t in self.status_bar.session.background_tasks
            if t.get("status") == "running"
        ]
        after_count = len(self.status_bar.session.background_tasks)
        cleared = before_count - after_count

        self.console.print(f"\n[green]✅ Cleared {cleared} completed task(s)[/green]\n")

    def cmd_build(self, *args):
        """Handle /build command for interactive agent builder."""
        from .build_wizard import BuildWizard

        wizard = BuildWizard(self.console, self.config)

        if args and args[0] == "from-template":
            template = args[1] if len(args) > 1 else None
            if not template:
                self.console.print(
                    "\n[yellow]Usage: /build from-template <template_name>[/yellow]\n"
                )
                return
            wizard.start(template=template)
        elif args and args[0] == "resume":
            session_id = args[1] if len(args) > 1 else None
            wizard.resume(session_id=session_id)
        elif args and args[0] == "list":
            # List saved sessions
            from .build_session import BuildSession

            sessions = BuildSession.list_sessions()

            if not sessions:
                self.console.print(
                    "\n[yellow]No saved build sessions found.[/yellow]\n"
                )
                return

            self.console.print("\n[bold cyan]Saved Build Sessions:[/bold cyan]\n")

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Agent", style="yellow")
            table.add_column("Progress", width=12)
            table.add_column("Step", width=20)
            table.add_column("Last Updated", style="dim")

            for sess in sessions[:10]:
                progress_pct = (sess["current_step"] / 6) * 100
                step_names = [
                    "Discovery",
                    "Goals",
                    "Evaluation",
                    "Prompts",
                    "Actions",
                    "Preview",
                ]
                current_step_name = (
                    step_names[sess["current_step"] - 1]
                    if sess["current_step"] <= 6
                    else "Complete"
                )

                table.add_row(
                    sess["agent_name"] or "Unnamed",
                    f"{int(progress_pct)}%",
                    current_step_name,
                    sess["updated_at"][:19],
                )

            self.console.print(table)
            self.console.print()
        elif args and args[0] == "help":
            self._show_build_help()
        else:
            # Start new build
            wizard.start()

    def _show_build_help(self):
        """Show help for /build command."""
        self.console.print()

        help_panel = Panel(
            "[bold cyan]/build[/bold cyan] - Interactive Agent Builder\n\n"
            "[bold yellow]Usage:[/bold yellow]\n"
            "  [cyan]/build[/cyan]                      - Start new agent build\n"
            "  [cyan]/build from-template <name>[/cyan] - Start from template\n"
            "  [cyan]/build resume[/cyan]               - Resume last session\n"
            "  [cyan]/build resume <id>[/cyan]          - Resume specific session\n"
            "  [cyan]/build list[/cyan]                 - List saved sessions\n"
            "  [cyan]/build help[/cyan]                 - Show this help\n\n"
            "[bold yellow]Examples:[/bold yellow]\n"
            "  [dim]/build[/dim]\n"
            "  [dim]/build from-template code_reviewer[/dim]\n"
            "  [dim]/build resume[/dim]\n\n"
            "[bold yellow]Natural Language:[/bold yellow]\n"
            "  You can also say:\n"
            '  [dim]"Build a code review agent"[/dim]\n'
            '  [dim]"Create an agent that analyzes data"[/dim]',
            title="[bold bright_cyan]Interactive Agent Builder[/bold bright_cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        self.console.print(help_panel)
        self.console.print()

    def cmd_telemetry(self, *args):
        """Manage anonymous telemetry settings."""
        from superoptix.cli.telemetry import get_telemetry

        telemetry = get_telemetry()

        if not args:
            # Show current status
            self.console.print()

            status_text = "Enabled ✅" if telemetry.enabled else "Disabled ❌"
            status_color = "green" if telemetry.enabled else "yellow"

            panel = Panel(
                Text.assemble(
                    ("📊 Anonymous Telemetry: ", "bold cyan"),
                    (status_text, f"bold {status_color}"),
                    ("\n\n", ""),
                    ("Anonymous ID: ", "dim"),
                    (telemetry.anonymous_id, "cyan"),
                    ("\n\n", ""),
                    ("What we track:\n", "bold"),
                    ("  • ", "dim"),
                    ("Commands used (e.g., 'spec.generate')\n", "white"),
                    ("  • ", "dim"),
                    ("Success/failure rates\n", "white"),
                    ("  • ", "dim"),
                    ("SuperOptiX version\n", "white"),
                    ("  • ", "dim"),
                    ("Platform (Mac/Linux/Windows)\n", "white"),
                    ("\n", ""),
                    ("What we DON'T track:\n", "bold"),
                    ("  • ", "dim"),
                    ("Your agent content or code\n", "white"),
                    ("  • ", "dim"),
                    ("Personal information\n", "white"),
                    ("  • ", "dim"),
                    ("File paths or data\n", "white"),
                    ("\n\n", ""),
                    ("Manage:\n", "bold cyan"),
                    ("  • ", "dim"),
                    ("/telemetry disable", "cyan"),
                    (" - Opt out\n", "dim"),
                    ("  • ", "dim"),
                    ("/telemetry enable", "cyan"),
                    (" - Opt back in\n", "dim"),
                ),
                border_style="bright_cyan",
                padding=(1, 2),
                title="[bold cyan]📊 Telemetry Settings[/bold cyan]",
            )

            self.console.print(panel)
            self.console.print()
            return

        # Handle subcommands
        subcommand = args[0].lower() if args else ""

        if subcommand == "disable":
            telemetry.disable()
            self.console.print()
            self.console.print("[green]✅ Telemetry disabled[/green]")
            self.console.print(
                "[dim]Your usage data will no longer be collected.[/dim]"
            )
            self.console.print()

        elif subcommand == "enable":
            telemetry.enable()
            self.console.print()
            self.console.print("[green]✅ Telemetry enabled[/green]")
            self.console.print(
                "[dim]Thank you for helping us improve SuperOptiX![/dim]"
            )
            self.console.print()

        else:
            self.console.print()
            self.console.print("[yellow]Unknown telemetry command[/yellow]")
            self.console.print(
                "[dim]Use: /telemetry, /telemetry disable, or /telemetry enable[/dim]"
            )
            self.console.print()

    def cmd_exit(self, *args):
        """Exit conversational mode."""
        pass  # Handled in main loop


def _default_acp_command(agent: str) -> Optional[str]:
    defaults = {
        "opencode": "opencode acp",
        "claude-code": "claude-code acp",
    }
    return defaults.get(agent)
