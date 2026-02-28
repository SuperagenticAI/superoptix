"""Conversational mode for SuperOptiX CLI.

This module provides the interactive conversational interface where users
can interact with SuperOptiX through natural language and slash commands.
"""

import os
import time
import warnings
import io
import logging
from contextlib import redirect_stderr
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# ULTRA-AGGRESSIVE: Suppress ALL warnings first (immediate suppression)
import os

warnings.simplefilter("ignore")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

# Comprehensive Pydantic warning suppression (for clarity/documentation)
warnings.filterwarnings("ignore", message=r".*[Pp]ydantic.*", category=UserWarning)
warnings.filterwarnings(
    "ignore", message=r".*[Pp]ydantic.*", category=DeprecationWarning
)
warnings.filterwarnings("ignore", module="pydantic.*", category=UserWarning)
warnings.filterwarnings("ignore", module="pydantic_ai.*", category=UserWarning)
# warnings.filterwarnings("ignore", module="storage3.*", category=UserWarning)  # Supabase removed

# Suppress specific litellm and other warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

# Silence noisy DSPy cache fallback warning in interactive startup.
logging.getLogger("dspy.clients").setLevel(logging.ERROR)
logging.getLogger("dspy").setLevel(logging.ERROR)

console = Console()
_STARTUP_NOISE_PATTERNS = [
    "Failed to initialize disk cache, falling back to memory-only cache",
]


def _filter_startup_stderr(text: str) -> str:
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        if any(p in line for p in _STARTUP_NOISE_PATTERNS):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def show_animated_welcome():
    """Show animated welcome screen."""
    console.clear()

    # Create gradient "Super CLI" title
    title = Text()
    title.append("S", style="bold bright_magenta")
    title.append("u", style="bold magenta")
    title.append("p", style="bold bright_red")
    title.append("e", style="bold red")
    title.append("r", style="bold bright_yellow")
    title.append(" ", style="")
    title.append("C", style="bold bright_green")
    title.append("L", style="bold green")
    title.append("I", style="bold bright_cyan")

    # Subtitle with SuperOptiX branding
    subtitle_text = Text.assemble(
        ("The Official ", "dim white"),
        ("SuperOptiX", "bold bright_yellow"),
        (" CLI", "dim white"),
    )

    # Welcome panel with animation
    welcome_panel = Panel(
        Align.center(title),
        border_style="bold bright_cyan",
        padding=(2, 4),
        title="✨ Welcome to Super CLI [yellow][BETA][/yellow] ✨",
        subtitle=subtitle_text,
    )

    console.print()
    console.print(welcome_panel)
    console.print()

    # Animated tagline
    taglines = [
        "💬 Conversational AI for Building AI Agents",
        "🎯 Full-Stack Agent Optimization Framework",
        "🚀 Build. Optimize. Deploy.",
    ]

    for tagline in taglines:
        console.print(Align.center(Text(tagline, style="bold cyan")))
        time.sleep(0.3)

    console.print()
    time.sleep(0.5)


def show_loading_animation(message: str, duration: float = 1.5):
    """Show a loading animation."""
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold cyan]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(message, total=None)
        time.sleep(duration)


def show_feature_showcase():
    """Show key features with animation."""
    console.print("[bold yellow]🎯 Key Features:[/bold yellow]\n")

    features = [
        ("💬", "Conversational Interface", "Talk to SuperOptiX naturally"),
        ("🎮", "Slash Commands", "Quick access to all features"),
        ("🤖", "Model Choice", "Ollama, OpenAI, or Anthropic"),
        ("🔒", "Privacy First", "Local models, your data stays yours"),
        ("⚡", "Fast & Easy", "Build agents in seconds"),
    ]

    for emoji, feature, desc in features:
        console.print(f"   {emoji} [bold cyan]{feature}[/bold cyan]")
        console.print(f"      [dim]{desc}[/dim]")
        time.sleep(0.2)

    console.print()
    time.sleep(0.5)


def config_exists() -> bool:
    """Check if configuration exists."""
    config_path = Path.home() / ".superoptix" / "config.yaml"
    return config_path.exists()


def load_config() -> dict:
    """Load configuration."""
    config_path = Path.home() / ".superoptix" / "config.yaml"

    if not config_path.exists():
        return {}

    import yaml

    with open(config_path) as f:
        return yaml.safe_load(f)


def save_config(config: dict):
    """Save configuration."""
    import yaml
    config_path = Path.home() / ".superoptix" / "config.yaml"
    fallback_path = Path.cwd() / ".superoptix" / "config.yaml"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return
    except OSError:
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fallback_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)


def run_setup_wizard(console: Console) -> dict:
    """Run first-time setup wizard."""

    # Show animated welcome
    show_animated_welcome()

    # Show features
    show_feature_showcase()

    console.print("[bold cyan]🎉 Let's Get You Set Up![/bold cyan]\n")
    console.print("[dim]This will take about 30 seconds.[/dim]\n")
    time.sleep(0.5)

    # Step 1: Choose model provider
    console.print("[bold yellow]Step 1/2: Choose AI Model Provider[/bold yellow]\n")

    console.print("[bold]1. 🏠 Ollama (Local)[/bold]")
    console.print("   • FREE, Private, Offline")
    console.print("   • Recommended for: Privacy, no API costs")
    console.print("   • Requires: Ollama installed\n")

    console.print("[bold]2. ☁️  OpenAI (Cloud)[/bold]")
    console.print("   • Paid (requires API key)")
    console.print("   • Models: gpt-4o, gpt-4o-mini")
    console.print("   • Recommended for: Advanced reasoning\n")

    console.print("[bold]3. ☁️  Anthropic (Cloud)[/bold]")
    console.print("   • Paid (requires API key)")
    console.print("   • Models: claude-3.5-sonnet")
    console.print("   • Recommended for: Coding assistance\n")

    choice = Prompt.ask("Choose provider", choices=["1", "2", "3"], default="1")

    config = {}

    if choice == "1":
        # Ollama setup
        console.print(
            "\n[bold green]Setting up Ollama (local, free, private)[/bold green]\n"
        )

        # Check if Ollama is running
        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                console.print("✅ Ollama is running!")

                # List available models
                tags = response.json().get("models", [])
                if tags:
                    console.print(
                        f"\n[bold green]✅ Found {len(tags)} installed models:[/bold green]\n"
                    )

                    # Show models in a nice table
                    model_table = Table(show_header=False, box=None, padding=(0, 2))
                    model_table.add_column(style="cyan")
                    model_table.add_column(style="dim")

                    for i, tag in enumerate(tags[:5], 1):
                        model_table.add_row(f"{i}. {tag['name']}", "✅ Installed")

                    console.print(model_table)
                    console.print()

                    # Use first model as default
                    default_model = tags[0]["name"]
                    model = Prompt.ask(f"Choose model", default=default_model)
                else:
                    console.print("\n[yellow]No models installed yet.[/yellow]")
                    console.print(
                        "Install llama3.1:8b (recommended)? This will take a few minutes."
                    )

                    if Confirm.ask("Install now?", default=True):
                        console.print()

                        # Show loading animation
                        show_loading_animation(
                            "🚀 Installing llama3.1:8b...", duration=0.5
                        )

                        console.print(
                            "[cyan]Downloading model (this may take a few minutes)...[/cyan]"
                        )
                        console.print("[dim]Run: ollama pull llama3.1:8b[/dim]\n")

                        import subprocess

                        result = subprocess.run(
                            ["ollama", "pull", "llama3.1:8b"], capture_output=False
                        )

                        if result.returncode == 0:
                            console.print()
                            console.print(
                                Panel(
                                    "[bold green]✅ Model installed successfully![/bold green]\n\n"
                                    "[cyan]llama3.1:8b[/cyan] is ready to use!",
                                    border_style="green",
                                    title="[bold]🎉 Success[/bold]",
                                )
                            )
                            console.print()
                            model = "llama3.1:8b"
                        else:
                            console.print("\n[red]Failed to install model.[/red]")
                            console.print(
                                "Please run: [cyan]ollama pull llama3.1:8b[/cyan]"
                            )
                            model = "llama3.1:8b"
                    else:
                        model = "llama3.1:8b"

                config = {
                    "provider": "ollama",
                    "model": model,
                    "api_base": "http://localhost:11434",
                }
            else:
                raise Exception("Ollama not responding")
        except Exception as e:
            console.print(f"[yellow]⚠️  Ollama not running ({e})[/yellow]\n")
            console.print("To use Ollama:")
            console.print("1. Install: https://ollama.com")
            console.print("2. Run: ollama serve")
            console.print("3. Install model: ollama pull llama3.1:8b\n")

            console.print("For now, using mock mode (limited functionality)")
            config = {"provider": "mock", "model": "mock", "api_base": "mock"}

    elif choice == "2":
        # OpenAI setup
        console.print("\n[bold green]Setting up OpenAI (cloud)[/bold green]\n")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("[yellow]OPENAI_API_KEY not set in environment[/yellow]")
            api_key = Prompt.ask("Enter your OpenAI API key", password=True)
        else:
            console.print("✅ Found OPENAI_API_KEY in environment")

        model = Prompt.ask(
            "Choose model",
            choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            default="gpt-4o-mini",
        )

        config = {"provider": "openai", "model": model, "api_key": api_key}

    elif choice == "3":
        # Anthropic setup
        console.print("\n[bold green]Setting up Anthropic (cloud)[/bold green]\n")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("[yellow]ANTHROPIC_API_KEY not set in environment[/yellow]")
            api_key = Prompt.ask("Enter your Anthropic API key", password=True)
        else:
            console.print("✅ Found ANTHROPIC_API_KEY in environment")

        model = Prompt.ask(
            "Choose model",
            choices=["claude-3.5-sonnet", "claude-3.5-haiku"],
            default="claude-3.5-sonnet",
        )

        config = {"provider": "anthropic", "model": model, "api_key": api_key}

    # Save configuration
    save_config(config)

    # Show success animation
    console.print()
    show_loading_animation("✨ Saving configuration...", duration=0.8)

    console.print()

    # Create success panel with sparkles
    success_message = Text.assemble(
        ("🎉 ", "yellow"),
        ("Setup Complete!", "bold green"),
        (" 🎉\n\n", "yellow"),
        ("Configuration Saved:\n", "bold cyan"),
        ("━" * 40, "cyan"),
        ("\n"),
        ("Provider: ", "dim"),
        (f"{config['provider']}\n", "bold green"),
        ("Model: ", "dim"),
        (f"{config['model']}\n", "bold yellow"),
        ("Status: ", "dim"),
        ("✅ Ready\n\n", "bold green"),
        ("━" * 40, "cyan"),
        ("\n\n"),
        ("💡 Change anytime with: ", "dim"),
        ("/config", "cyan"),
        (" or ", "dim"),
        ("/model set", "cyan"),
    )

    console.print(
        Panel(Align.center(success_message), border_style="bold green", padding=(1, 2))
    )

    console.print()
    time.sleep(0.5)

    # Show quick start tips
    console.print("[bold cyan]🚀 Quick Start Tips:[/bold cyan]\n")

    tips = [
        # ("🔐", "/login", "Login with GitHub OAuth"),  # Disabled for OSS
        ("💬", "/help", "Show all commands"),
        ("❓", "/ask <question>", "Ask about SuperOptiX"),
        ("🤖", "/model list", "See all models"),
        ("📋", "/playbooks", "Browse templates"),
    ]

    tips_table = Table(show_header=False, box=None, padding=(0, 2))
    tips_table.add_column(style="yellow", width=3)
    tips_table.add_column(style="bold cyan", width=20)
    tips_table.add_column(style="dim")

    for emoji, cmd, desc in tips:
        tips_table.add_row(emoji, cmd, desc)

    console.print(tips_table)
    console.print()
    time.sleep(0.5)

    return config


def start_conversation():
    """Start conversational mode."""

    # Ensure warnings are suppressed
    warnings.filterwarnings("ignore")

    # Check if first time
    if not config_exists():
        config = run_setup_wizard(console)
    else:
        # Returning user - show quick welcome
        config = load_config()
        console.clear()

        # Create colorful title - "Super CLI"
        title = Text()
        title.append("Super", style="bold bright_magenta")
        title.append(" ", style="")
        title.append("CLI", style="bold bright_cyan")

        # Subtitle
        subtitle = Text.assemble(
            ("The Official ", "dim"),
            ("SuperOptiX", "bold bright_yellow"),
            (" CLI", "dim"),
        )

        # Status panel
        status_panel = Panel(
            Align.center(
                Text.assemble(
                    ("✨ ", "yellow"),
                    title,
                    (" ✨\n", "yellow"),
                    subtitle,
                    ("\n\n", ""),
                    ("Using: ", "dim"),
                    (f"{config.get('provider', 'mock')}", "bold green"),
                    (" (", "dim"),
                    (f"{config.get('model', 'mock')}", "bold yellow"),
                    (")", "dim"),
                )
            ),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold green]🎉 Welcome Back to Super CLI![/bold green]",
        )

        console.print()
        console.print(status_panel)
        console.print()

    # Show auth status
    # Auth disabled for OSS version
    # from superoptix.cli.auth import is_authenticated, get_current_user
    # ... code removed ...

    console.print()

    # Show essential slash commands menu
    commands_panel = Panel(
        Text.from_markup(
            "[bold cyan]💡 Quick Start[/bold cyan]\n\n"
            "[dim]Essential Commands:[/dim]\n"
            # "  [green]/login[/green]             Login with GitHub OAuth\n"  # Disabled
            "  [green]/help[/green]              Full command reference\n"
            "  [green]/ask[/green] <question>    Ask about SuperOptiX\n"
            "  [green]/model[/green] list         List available models\n"
            "  [green]/connect[/green]           Connect ACP/BYOK/LOCAL runtime\n"
            "  [green]/mcp[/green] status         Check MCP server status\n"
            "  [green]/acp[/green] status         Check ACP session status\n"
            "  [green]/exit[/green]              Exit Super CLI\n\n"
            "[dim]Natural Language (Just type what you want!):[/dim]\n"
            '  [cyan]"Build a developer agent"[/cyan]\n'
            '  [cyan]"Evaluate my customer support agent"[/cyan]\n'
            '  [cyan]"Optimize the code review agent with GEPA"[/cyan]\n\n'
            "[dim italic]💬 Type naturally or use slash commands • Type [green]/help[/green] for all commands[/dim italic]\n"
        ),
        border_style="bright_magenta",
        padding=(1, 2),
        title="[bold yellow]✨ Welcome to Super CLI ✨[/bold yellow]",
    )

    console.print(commands_panel)
    console.print()

    # Import slash command handler and chat agent
    from superoptix.cli.commands.slash_commands import SlashCommandHandler
    from superoptix.cli.commands.chat_agent import ConversationalAgent

    # Initialize conversational agent + slash handler while filtering known noisy stderr.
    startup_stderr = io.StringIO()
    with redirect_stderr(startup_stderr):
        try:
            chat_agent = ConversationalAgent(console, config)
            natural_language_enabled = True
        except Exception:
            chat_agent = None
            natural_language_enabled = False
        slash_handler = SlashCommandHandler(console, config, chat_agent=chat_agent)
    remaining_startup_stderr = _filter_startup_stderr(startup_stderr.getvalue())
    if remaining_startup_stderr:
        print(remaining_startup_stderr)

    # Main conversation loop
    while True:
        try:
            # Import enhanced textbox
            from superoptix.cli.commands.multiline_input import InlineTextBox

            # Display with spacing
            console.print()

            # Create and use enhanced inline textbox
            textbox = InlineTextBox(
                console,
                placeholder="Type your message or /help for commands...",
                show_char_count=False,  # Keep it clean
                emoji_support=True,
            )

            # Get user input with beautiful textbox UX
            user_input = textbox.get_input()

            console.print()

            if not user_input.strip():
                continue

            # Handle slash commands
            if user_input.startswith("/"):
                response = slash_handler.handle(user_input)

                # Check for exit
                if user_input.strip() in ["/exit", "/quit"]:
                    console.print()

                    # Animated goodbye
                    goodbye_panel = Panel(
                        Align.center(
                            Text.assemble(
                                ("👋 ", "yellow"),
                                ("Goodbye!", "bold bright_cyan"),
                                ("\n\n", ""),
                                ("Thanks for using ", "cyan"),
                                ("Super CLI", "bold bright_magenta"),
                                ("!", "cyan"),
                                ("\n", ""),
                                ("The Official ", "dim"),
                                ("SuperOptiX", "bold bright_yellow"),
                                (" CLI", "dim"),
                                ("\n\n", ""),
                                ("Happy building! 🚀", "bold green"),
                            )
                        ),
                        border_style="bright_magenta",
                        padding=(1, 4),
                        title="[bold yellow]✨ See You Soon! ✨[/bold yellow]",
                    )

                    console.print(goodbye_panel)
                    console.print()
                    break

                if response:
                    console.print(response)

            # Handle natural language
            else:
                if natural_language_enabled and chat_agent:
                    # Process with conversational agent
                    try:
                        chat_agent.process(user_input)
                    except Exception as e:
                        console.print(f"\n[red]Error processing request:[/red] {e}")
                        console.print(
                            "[dim]Try using slash commands or traditional CLI[/dim]\n"
                        )
                else:
                    # Fallback message if chat agent not available
                    console.print()

                    coming_soon_panel = Panel(
                        "[bold yellow]💬 Natural Language Mode[/bold yellow]\n\n"
                        "[cyan]Natural language processing requires a configured model.[/cyan]\n\n"
                        "[dim]For now, use slash commands:[/dim]\n"
                        "  [bold cyan]•[/bold cyan] /help - Show all commands\n"
                        "  [bold cyan]•[/bold cyan] /ask <question> - Ask about SuperOptiX\n"
                        "  [bold cyan]•[/bold cyan] /model list - List models\n"
                        "  [bold cyan]•[/bold cyan] /agents - List agents\n\n"
                        "[dim]Or use traditional CLI:[/dim] [cyan]super agent compile <name>[/cyan]",
                        border_style="yellow",
                        padding=(1, 2),
                        title="[bold bright_yellow]ℹ️  Info[/bold bright_yellow]",
                    )

                    console.print(coming_soon_panel)
                    console.print()

        except KeyboardInterrupt:
            console.print("\n")

            # Animated goodbye for Ctrl+C
            goodbye_panel = Panel(
                Align.center(
                    Text.assemble(
                        ("👋 ", "yellow"),
                        ("Goodbye!", "bold bright_cyan"),
                        ("\n\n", ""),
                        ("Thanks for using ", "cyan"),
                        ("Super CLI", "bold bright_magenta"),
                        ("!", "cyan"),
                        ("\n", ""),
                        ("The Official ", "dim"),
                        ("SuperOptiX", "bold bright_yellow"),
                        (" CLI", "dim"),
                        ("\n\n", ""),
                        ("Happy building! 🚀", "bold green"),
                    )
                ),
                border_style="bright_magenta",
                padding=(1, 4),
                title="[bold yellow]✨ See You Soon! ✨[/bold yellow]",
            )

            console.print(goodbye_panel)
            console.print()
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
