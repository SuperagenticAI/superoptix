#!/usr/bin/env python3
"""Main CLI entry point for SuperOptiX."""

# CRITICAL: Apply warning filters BEFORE any imports
# This ensures warnings from dependencies (storage3, supabase, pydantic) are suppressed
import warnings
import os

# ============================================================================
# ULTRA-AGGRESSIVE WARNING SUPPRESSION FOR PYPI INSTALLATIONS
# ============================================================================
# For PyPI installations, warnings can be triggered during dependency imports
# BEFORE our filters are applied. We use a multi-layered approach:

# STEP 1: Suppress ALL warnings first (catches everything immediately)
# This prevents warnings from showing during import
warnings.simplefilter("ignore")

# STEP 2: Set PYTHONWARNINGS environment variable as fallback
# This ensures warnings are suppressed even if they trigger before Python code runs
os.environ.setdefault("PYTHONWARNINGS", "ignore")

# STEP 3: Now apply specific filters for Pydantic-related warnings
# (Even though simplefilter("ignore") catches everything, these are for clarity
# and in case someone wants to selectively allow non-Pydantic warnings later)

# ============================================================================
# COMPREHENSIVE PYDANTIC WARNING SUPPRESSION
# ============================================================================
# Suppress ALL Pydantic-related warnings to ensure clean CLI experience

# 1. Suppress ALL Pydantic-related warnings by message pattern
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=FutureWarning,
)

# 2. Suppress specific Pydantic warning types
warnings.filterwarnings(
    "ignore",
    message=r".*PydanticDeprecatedSince20.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*pydantic\.config\.Extra.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*Pydantic serializer warnings.*",
    category=UserWarning,
)

# 3. Suppress ALL warnings from pydantic module
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=FutureWarning,
)

# 4. Suppress ALL warnings from pydantic_ai module
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=FutureWarning,
)

# 5. Suppress warnings from storage3 module (Supabase dependency)
# CRITICAL: storage3 uses deprecated Pydantic V2 APIs that trigger warnings
warnings.filterwarnings(
    "ignore",
    module="storage3.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="storage3.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*storage3.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*storage3.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*pydantic\.config\.Extra.*is deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*PydanticDeprecatedSince20.*",
    category=DeprecationWarning,
)

# 6. Suppress warnings from supabase module
warnings.filterwarnings(
    "ignore",
    module="supabase.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*supabase.*[Pp]ydantic.*",
    category=UserWarning,
)

import asyncio
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from superoptix import __version__ as superoptix_version

# Additional warning suppressions for runtime warnings
# SQLite resource warnings from DSPy evaluation
warnings.filterwarnings("ignore", message="unclosed database", category=ResourceWarning)
# LiteLLM async event loop warnings
warnings.filterwarnings(
    "ignore", message="There is no current event loop", category=DeprecationWarning
)
warnings.filterwarnings("ignore", module="litellm", category=DeprecationWarning)
# Final catch-all for storage3 Pydantic warnings (defense in depth)
warnings.filterwarnings("ignore", module="storage3.*", category=DeprecationWarning)
warnings.filterwarnings(
    "ignore", message=r".*pydantic\.config\.Extra.*", category=DeprecationWarning
)

from superoptix.cli.commands.agent import (
    add_agent,
    compile_agent,
    design_agent,
    inspect_agent,
    lint_agent,
    list_agents,
    optimize_agent,
    remove_agent,
    run_agent,
    show_tier_status,
    test_agent_bdd,
)
from superoptix.cli.commands.dataset import (
    preview_dataset,
    validate_dataset,
    dataset_info,
)
from superoptix.cli.commands.dataset_marketplace import (
    list_example_datasets,
    pull_example_dataset,
    show_dataset_details,
)
from superoptix.cli.commands.init import init_project
from superoptix.cli.commands.marketplace import (
    browse_marketplace,
    install_component,
    marketplace_dashboard,
    search_marketplace,
    show_component,
    show_featured,
)
from superoptix.cli.commands.observability import (
    analyze,
    dashboard,
    debug,
    list_agents_with_traces,
    traces,
    check_traces,
)
from superoptix.cli.commands.orchestra import (
    create_orchestra,
    list_orchestras,
    run_orchestra,
)
from superoptix.cli.commands.superspec import (
    analyze_agents,
    bootstrap_namespace,
    generate_agent,
    show_info,
    show_schema,
    validate_agents,
)
# from superoptix.cli.commands.auth_commands import login, logout, whoami


console = Console()


def show_comprehensive_docs(args):
    """Display comprehensive SuperOptiX documentation."""
    # Show the banner first
    show_superoptix_banner()

    console.print("🚀 COMPREHENSIVE GETTING STARTED GUIDE", style="bold bright_yellow")
    console.print("═" * 90, style="bright_cyan")
    console.print(
        "   [dim]Follow this step-by-step guide to master SuperOptiX in minutes![/]"
    )
    console.print()

    # Prerequisites
    console.print("📋 [bold bright_green]PREREQUISITES[/]")
    console.print("   ✅ Python 3.8+ installed ([cyan]python --version[/] to check)")
    console.print("   ✅ Basic familiarity with command line")
    console.print("   ✅ Text editor or IDE of your choice")
    console.print("   ✅ Internet connection for API setup (optional)")
    console.print()

    # Step 1: Environment Setup
    console.print("🏗️ [bold bright_green]STEP 1: SET UP YOUR DEVELOPMENT ENVIRONMENT[/]")
    console.print("   [yellow]Choose your preferred Python environment manager:[/]")
    console.print()
    console.print(
        "   🔹 [bold]Option A - Standard venv (Recommended for beginners):[/]"
    )
    console.print("     [cyan]python -m venv .venv[/]")
    console.print(
        "     [cyan]source .venv/bin/activate[/]  [dim]# Windows: .venv\\Scripts\\activate[/]"
    )
    console.print()
    console.print("   🔹 [bold]Option B - Conda (If you use Anaconda/Miniconda):[/]")
    console.print("     [cyan]conda create -n superoptix python=3.12[/]")
    console.print("     [cyan]conda activate superoptix[/]")
    console.print()
    console.print("   🔹 [bold]Option C - uv (Fast & Modern, for advanced users):[/]")
    console.print("     [cyan]pip install uv[/]")
    console.print("     [cyan]uv venv[/]")
    console.print(
        "     [cyan]source .venv/bin/activate[/]  [dim]# Windows: .venv\\Scripts\\activate[/]"
    )
    console.print()
    console.print(
        "   [green]💡 Why virtual environments? They keep your project dependencies isolated![/]"
    )
    console.print()

    # Step 2: Project Creation
    console.print("🎯 [bold bright_green]STEP 2: CREATE YOUR FIRST AGENTIC SYSTEM[/]")
    console.print("   [cyan]super init my_awesome_project[/]")
    console.print("   [cyan]cd my_awesome_project[/]")
    console.print()
    console.print("   [yellow]📁 This creates a complete project structure:[/]")
    console.print("     • 📋 [cyan]agents/[/] - Where your AI agents live")
    console.print("     • 🎼 [cyan]orchestras/[/] - Multi-agent workflows")
    console.print("     • 📊 [cyan]observability/[/] - Monitoring and debugging")
    console.print("     • ⚙️  [cyan].env[/] - API keys and configuration")
    console.print("     • 🔧 [cyan].super[/] - Project marker file")
    console.print()

    # Step 3: Verify and Install
    console.print(
        "🔍 [bold bright_green]STEP 3: VERIFY PROJECT & INSTALL DEPENDENCIES[/]"
    )
    console.print("   [yellow]First, make sure you're in the right place:[/]")
    console.print("   [cyan]ls -la | grep .super[/]")
    console.print(
        "   [dim]👀 You should see the .super file - this confirms you're in a SuperOptiX project![/]"
    )
    console.print()
    console.print("   [yellow]Install the project in development mode:[/]")
    console.print("   [cyan]pip install -e .[/]")
    console.print(
        "   [dim]🔧 This installs SuperOptiX and all dependencies for development[/]"
    )
    console.print()

    # Step 4: API Configuration
    console.print("🔐 [bold bright_green]STEP 4: CONFIGURE AI MODEL ACCESS[/]")
    console.print("   [yellow]You have two great options for AI models:[/]")
    console.print()
    console.print(
        "   🏠 [bold]Option A - Local Models (Recommended for Development):[/]"
    )
    console.print(
        "     • Install Ollama: Visit [cyan]https://ollama.com[/cyan] or run [cyan]curl -fsSL https://ollama.com/install.sh | sh[/]"
    )
    console.print("     • Download a model: [cyan]ollama pull llama3.2[/]")
    console.print("     • No API keys needed! Free and private!")
    console.print()
    console.print("   🌐 [bold]Option B - Cloud Models (For Production):[/]")
    console.print("     • Edit the [cyan].env[/] file in your project:")
    console.print("     [cyan]OPENAI_API_KEY=your_openai_key_here[/]")
    console.print("     [cyan]ANTHROPIC_API_KEY=your_anthropic_key_here[/]")
    console.print()
    console.print("   [red]🚨 SECURITY REMINDER:[/]")
    console.print("   [green]✅ Never commit .env file to version control[/]")
    console.print("   [green]✅ Keep API keys private and secure[/]")
    console.print("   [green]✅ .env is automatically ignored by git[/]")
    console.print()

    # Step 4.5: Model Management System
    console.print(
        "🤖 [bold bright_green]STEP 4.5: MASTER THE MODEL INTELLIGENCE SYSTEM[/]"
    )
    console.print(
        "   [yellow]SuperOptiX provides comprehensive model management across multiple backends:[/]"
    )
    console.print()
    console.print("   🔍 [bold]Discover and List Models:[/]")
    console.print("     [cyan]super model list[/] - Show installed models")
    console.print("     [cyan]super model list --help[/] - Browse discovery guides")
    console.print("     [cyan]super model backends[/] - List supported backends")
    console.print()
    console.print("   📦 [bold]Install Models Across Backends:[/]")
    console.print(
        "     [cyan]super model install llama3.2:3b[/] - Install Ollama model (default)"
    )
    console.print(
        "     [cyan]super model install -b huggingface microsoft/Phi-4[/] - Install HuggingFace model"
    )
    console.print(
        "     [cyan]super model install -b mlx mlx-community/phi-2[/] - Install MLX model"
    )
    console.print()
    console.print("   🖥️ [bold]Manage Local Servers:[/]")
    console.print(
        "     [cyan]super model server mlx phi-2 --port 8000[/] - Start MLX server"
    )
    console.print(
        "     [cyan]super model server huggingface microsoft/Phi-4 --port 8001[/] - Start HF server"
    )
    console.print(
        "     [cyan]super model server lmstudio llama3.2:3b --port 1234[/] - Start LM Studio server"
    )
    console.print()
    console.print("   🔗 [bold]Create DSPy Clients:[/]")
    console.print(
        "     [cyan]super model dspy ollama/llama3.2:3b[/] - Create Ollama DSPy client"
    )
    console.print("     [cyan]super model dspy mlx/phi-2[/] - Create MLX DSPy client")
    console.print(
        "     [cyan]super model dspy huggingface/microsoft/Phi-4[/] - Create HF DSPy client"
    )
    console.print()
    # Removed Smart Model Recommendations block
    console.print(
        "   [green]🎯 Pro Tip: Use local models for development, cloud models for production![/]"
    )
    console.print()

    # Step 5: Your First Agent (DSL Approach)
    console.print(
        "🤖 [bold bright_green]STEP 5: CREATE YOUR FIRST AI AGENT WITH DSL[/]"
    )
    console.print("   [yellow]Generate a sophisticated Genie-tier agent:[/]")
    console.print(
        "   [cyan]super spec generate genie developer --namespace software[/]"
    )
    console.print(
        "   [dim]🎯 This creates a tier-compliant agent with memory, tools, and RAG![/]"
    )
    console.print()
    console.print("   [yellow]Or start with a basic Oracles-tier agent:[/]")
    console.print(
        "   [cyan]super spec generate oracles code-reviewer --namespace software[/]"
    )
    console.print("   [dim]📋 This creates a simple agent for basic reasoning tasks[/]")
    console.print()
    console.print("   [yellow]Validate your agent playbook:[/]")
    console.print("   [cyan]super spec validate agents/developer_playbook.yaml[/]")
    console.print(
        "   [dim]✅ Comprehensive validation with tier compliance checking[/]"
    )
    console.print()
    console.print("   [yellow]Alternative: Use pre-built agents:[/]")
    console.print("   [cyan]super agent pull developer[/]")
    console.print("   [dim]📚 Browse 50+ pre-built agents if you prefer[/]")
    console.print()

    # Step 6: Compile Agent
    console.print(
        "⚡ [bold bright_green]STEP 6: COMPILE YOUR AGENT (MAGIC HAPPENS HERE!)[/]"
    )
    console.print("   [cyan]super agent compile developer[/]")
    console.print(
        "   [dim]🔮 This transforms your YAML playbook into executable Python code![/]"
    )
    console.print()
    console.print(
        "   [yellow]Advanced: Use the fully abstracted template when you need maximum code reduction:[/]"
    )
    console.print("   [cyan]super agent compile developer --abstracted[/]")
    console.print()

    # Step 7: Evaluate Baseline Performance
    console.print("🧪 [bold bright_green]STEP 7: ESTABLISH BASELINE PERFORMANCE[/]")
    console.print("   [cyan]super agent evaluate developer[/]")
    console.print(
        "   [dim]🎭 Runs BDD test suite to establish baseline performance![/]"
    )
    console.print()
    console.print("   [yellow]Why evaluate first:[/]")
    console.print("     • 📊 Measure current performance baseline")
    console.print("     • 🎯 Identify areas needing improvement")
    console.print("     • 💡 Plan optimization strategy")
    console.print("     • ✅ Validate scenarios are well-written")
    console.print()

    # Step 8: Optimize Agent
    console.print(
        "🎯 [bold bright_green]STEP 8: OPTIMIZE YOUR AGENT FOR PEAK PERFORMANCE[/]"
    )
    console.print("   [cyan]super agent optimize developer[/]")
    console.print(
        "   [dim]🚀 Uses DSPy's BootstrapFewShot to enhance agent capabilities![/]"
    )
    console.print()
    console.print("   [yellow]What optimization does:[/]")
    console.print("     • 📈 Learns from your BDD scenarios")
    console.print("     • 🎯 Improves response accuracy and quality")
    console.print("     • 💾 Creates optimized pipeline weights")
    console.print("     • ⚡ Speeds up future executions")
    console.print()

    # Step 9: Re-evaluate for Improvement
    console.print("📊 [bold bright_green]STEP 9: MEASURE OPTIMIZATION IMPROVEMENT[/]")
    console.print("   [cyan]super agent evaluate developer[/]")
    console.print("   [dim]📈 Compare before/after performance to see the magic![/]")
    console.print()
    console.print("   [yellow]What to look for:[/]")
    console.print("     • 📊 Improved accuracy scores")
    console.print("     • 🎯 Better response quality")
    console.print("     • ⚡ Faster execution times")
    console.print("     • 💡 More consistent behavior")
    console.print()

    # Step 10: Run Your Agent
    console.print("🚀 [bold bright_green]STEP 10: RUN YOUR OPTIMIZED AGENT[/]")
    console.print("   [cyan]super agent run developer[/]")
    console.print("   [dim]🎉 Your agent is now ready for production use![/]")
    console.print()
    console.print("   [yellow]Interactive mode:[/]")
    console.print("   [cyan]super agent run developer --interactive[/]")
    console.print("   [dim]💬 Chat with your agent in real-time![/]")
    console.print()

    # Step 11: Advanced Features
    console.print("🔧 [bold bright_green]STEP 11: EXPLORE ADVANCED FEATURES[/]")
    console.print("   [yellow]Multi-Agent Orchestration:[/]")
    console.print("   [cyan]super orchestra create my_workflow[/]")
    console.print("   [dim]🎼 Coordinate multiple agents in complex workflows[/]")
    console.print()
    console.print("   [yellow]Observability & Monitoring:[/]")
    console.print("   [cyan]super observe[/]")
    console.print("   [dim]📊 Monitor agent performance and debug issues[/]")
    console.print()
    console.print("   [yellow]Marketplace Integration:[/]")
    console.print("   [cyan]super market browse agents[/]")
    console.print("   [dim]🏪 Discover and install pre-built agents and tools[/]")
    console.print()

    # Best Practices
    console.print("💡 [bold bright_green]BEST PRACTICES[/]")
    console.print("   • 🎯 Start with simple agents and gradually add complexity")
    console.print("   • 📝 Write clear, specific BDD scenarios for better optimization")
    console.print("   • 🔄 Iterate: evaluate → optimize → evaluate")
    console.print("   • 🧪 Test thoroughly before deploying to production")
    console.print("   • 📚 Use the marketplace for common use cases")
    console.print("   • 🔍 Monitor performance with observability tools")
    console.print()

    # Troubleshooting
    console.print("🔧 [bold bright_green]TROUBLESHOOTING[/]")
    console.print("   [yellow]Common Issues:[/]")
    console.print(
        "     • [red]Import errors:[/] Make sure you're in a SuperOptiX project directory"
    )
    console.print(
        "     • [red]Model not found:[/] Use [cyan]super model list[/] to check installed models"
    )
    console.print(
        "     • [red]Compilation errors:[/] Validate your playbook with [cyan]super spec validate[/]"
    )
    console.print(
        "     • [red]Performance issues:[/] Run [cyan]super agent optimize[/] to improve"
    )
    console.print()
    console.print("   [yellow]Getting Help:[/]")
    console.print("     • 📖 [cyan]super docs[/] - This comprehensive guide")
    console.print("     • 💬 [cyan]super --help[/] - Command-specific help")
    console.print("     • 🌐 [cyan]https://superoptix.ai[/] - Full documentation")
    console.print(
        "     • 🐛 [cyan]https://github.com/superoptix/superoptix[/] - Report issues"
    )
    console.print()

    # Support and Community
    console.print("🤝 [bold bright_green]SUPPORT & COMMUNITY[/]")
    console.print("   [yellow]Get Help & Connect:[/]")
    console.print("     • 📧 Support: [blue]support@super-agentic.ai[/]")
    console.print()
    console.print(
        "   [green]🌟 Happy Building with SuperOptiX! Transform ideas into intelligent systems![/]"
    )
    console.print("=" * 90)


def show_superoptix_banner():
    """Display a beautiful static SuperOptiX banner."""

    # Create rainbow gradient text
    title = Text("SuperOptiX", style="bold")
    title.stylize("rgb(255,0,128)", 0, 2)  # Su - Hot Pink
    title.stylize("rgb(255,128,0)", 2, 4)  # pe - Orange
    title.stylize("rgb(255,255,0)", 4, 5)  # r - Yellow
    title.stylize("rgb(128,255,0)", 5, 6)  # N - Light Green
    title.stylize("rgb(0,255,128)", 6, 7)  # e - Green
    title.stylize("rgb(0,128,255)", 7, 8)  # t - Light Blue
    title.stylize("rgb(128,0,255)", 8, 9)  # i - Purple
    title.stylize("rgb(255,0,255)", 9, 10)  # X - Magenta

    console.print()  # Add spacing

    # Simple static banner
    try:
        # Create the main title with sparkles
        decorated_title = Text.assemble(("✨ ", "yellow"), title, (" ✨", "yellow"))

        # Beautiful static panel
        title_panel = Panel(
            Align.center(decorated_title),
            border_style="bright_cyan",
            padding=(1, 4),
            title="🌟 SuperOptiX CLI 🌟",
            title_align="center",
        )
        console.print(title_panel)

        # Add subtitle
        console.print()
        subtitle = Text(
            "🌟 Next-Generation Agentic System Framework 🌟", style="bold cyan"
        )
        console.print(Align.center(subtitle))

        # Add welcome message
        console.print()
        welcome_msg = Text(
            "🚀 Welcome to the future of AI agent development! 🚀", style="bold yellow"
        )
        console.print(Align.center(welcome_msg))

        console.print()
        console.print("═" * 80, style="bright_cyan")

    except Exception:
        # Fallback for any display issues
        console.print()
        console.print(
            "🌟 [bold bright_cyan]SuperOptiX - Next-Generation Agentic System Framework[/] 🌟"
        )
        console.print(
            "🚀 [bold yellow]Welcome to the future of AI agent development![/] 🚀"
        )
        console.print()

    console.print()  # Add spacing after banner


def show_welcome_screen(args):
    """Display a more graphical welcome screen with warmup message."""
    show_superoptix_banner()
    console.print(
        Align.center(
            "Your one-stop shop for building, testing, and deploying autonomous agentic systems."
        )
    )
    console.print()

    # Show warmup message for first-time users
    console.print(
        Panel(
            "[bold green]🎉 Welcome to SuperOptiX![/bold green]\n\n"
            "[yellow]💡 Pro Tip:[/yellow] The first time you run any SuperOptiX command, "
            "Python may take a few seconds to prepare the environment. "
            "This is normal and only happens once—subsequent runs will be much faster!\n\n"
            "[cyan]🚀 Ready to get started?[/cyan]",
            title="[bold bright_cyan]🌟 First Time Setup[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )
    console.print()

    text = Text.from_markup(
        """
[bold bright_yellow]Common Commands:[/bold bright_yellow]

      [bold cyan]super init[/bold cyan]         [grey50]Initialize a new project[/grey50]
    [bold cyan]super marketplace[/bold cyan]  [grey50]🏪 Discover agents and tools[/grey50]
    [bold cyan]super agent[/bold cyan]        [grey50]Manage agents (add, compile, test, run)[/grey50]
    [bold cyan]super model[/bold cyan]        [grey50]🤖 Model intelligence system[/grey50]
    [bold cyan]super spec[/bold cyan]   [grey50]🤖 Agent DSL (generate, validate, analyze)[/grey50]
    [bold cyan]super orchestra[/bold cyan]         [grey50]Manage multi-agent workflows[/grey50]
    [bold cyan]super docs[/bold cyan]         [grey50]Show comprehensive getting started guide[/grey50]

Use '[bold]super <command> --help[/]' for more information.
"""
    )
    panel = Panel(
        text,
        title="[bold]Quickstart[/bold]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def show_version_screen(args=None):
    """Display a visually attractive SuperOptiX version banner."""
    version = superoptix_version

    # Clean, modern SuperOptiX branding
    console.print("\n")
    console.print(
        Panel(
            f"[bold bright_yellow]SuperOptiX[/bold bright_yellow] [bold cyan]v{version}[/bold cyan]\n\n"
            "[green]The Full Stack Agentic AI Framework[/green]\n"
            "[bright_magenta]✨ Fast. Modular. Beautiful. ✨[/bright_magenta]",
            title="[bold bright_cyan]🚀 SuperOptiX Version[/bold bright_cyan]",
            border_style="bold magenta",
            padding=(1, 2),
        )
    )
    console.print("\n")


def execute_with_loader(func, args, command_name="SuperOptiX"):
    """Execute a function with clean, simple progress feedback."""
    from superoptix.cli.utils import suppress_warnings

    # Determine if this is a long-running operation that needs progress feedback
    needs_progress = False
    progress_message = "Working..."

    if hasattr(args, "command") and args.command:
        if args.command == "model":
            if hasattr(args, "model_command") and args.model_command:
                # DISABLE PROGRESS SPINNER FOR MODEL INSTALL - LET NATIVE OUTPUT SHOW
                if args.model_command == "install":
                    needs_progress = False  # Force native output
                elif args.model_command in ["backends", "refresh"]:
                    needs_progress = True
                    progress_map = {
                        "backends": "Checking backends...",
                        "refresh": "Refreshing cache...",
                    }
                    progress_message = progress_map.get(
                        args.model_command, "Working..."
                    )

        elif args.command == "agent":
            if hasattr(args, "agent_command") and args.agent_command in [
                "compile",
                "evaluate",
                "optimize",
                "pull",
            ]:
                needs_progress = True
                progress_message = f"Agent {args.agent_command}..."

        elif args.command == "spec":
            if hasattr(args, "spec_command") and args.spec_command in [
                "generate",
                "analyze",
            ]:
                needs_progress = True
                progress_message = f"Spec {args.spec_command}..."

    try:
        with suppress_warnings():
            if needs_progress:
                # Use simple, clean progress indicator for long-running tasks
                with console.status(f"[cyan]{progress_message}[/cyan]", spinner="dots"):
                    # Run async functions in an event loop
                    if asyncio.iscoroutinefunction(func):
                        try:
                            return asyncio.run(func(args))
                        except KeyboardInterrupt:
                            console.print(
                                "\n[bold red]⚠️ Operation cancelled by user.[/bold red]"
                            )
                            sys.exit(1)
                    else:
                        return func(args)
            else:
                # No progress indicator for quick operations OR model install (native output)
                if asyncio.iscoroutinefunction(func):
                    try:
                        return asyncio.run(func(args))
                    except KeyboardInterrupt:
                        console.print(
                            "\n[bold red]⚠️ Operation cancelled by user.[/bold red]"
                        )
                        sys.exit(1)
                else:
                    return func(args)

    except Exception as e:
        console.print(f"\n[bold red]❌ An error occurred:[/bold red] {e}")
        sys.exit(1)


def check_conversational_mode():
    """Check if should enter conversational mode."""
    # Enter conversational mode if just 'super' with no arguments
    if len(sys.argv) == 1:
        return True
    return False


def main():
    """Main CLI entry point."""

    # FINAL SAFETY: Ensure all warnings are suppressed (defense in depth)
    # This is a redundant check in case anything bypasses the top-level filters
    import warnings
    import os

    # Suppress all warnings (immediate)
    warnings.simplefilter("ignore")

    # Set environment variable as fallback
    os.environ.setdefault("PYTHONWARNINGS", "ignore")

    # Re-apply specific Pydantic filters for clarity
    warnings.filterwarnings("ignore", message=r".*[Pp]ydantic.*", category=UserWarning)
    warnings.filterwarnings(
        "ignore", message=r".*[Pp]ydantic.*", category=DeprecationWarning
    )
    warnings.filterwarnings("ignore", module="pydantic.*", category=UserWarning)
    warnings.filterwarnings("ignore", module="pydantic_ai.*", category=UserWarning)
    # warnings.filterwarnings("ignore", module="storage3.*", category=UserWarning)
    # warnings.filterwarnings("ignore", module="storage3.*", category=DeprecationWarning)
    # warnings.filterwarnings("ignore", message=r".*storage3.*", category=DeprecationWarning)
    warnings.filterwarnings(
        "ignore", message=r".*pydantic\.config\.Extra.*", category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore", message=r".*PydanticDeprecatedSince20.*", category=DeprecationWarning
    )
    # warnings.filterwarnings("ignore", module="supabase.*", category=UserWarning)

    # Track CLI usage (anonymous)
    try:
        from superoptix.cli.telemetry import track

        command_name = sys.argv[1] if len(sys.argv) > 1 else "conversational"
        track(f"cli.{command_name}", success=True)
    except:
        pass  # Never let telemetry break CLI

    # Check if conversational mode
    if check_conversational_mode():
        from superoptix.cli.commands.conversational import start_conversation

        start_conversation()
        return

    # Minimal help description
    description = """\
Welcome to SuperOptiX! 🌟

SuperOptiX is a revolutionary AI agent framework that brings enterprise-grade orchestration 
to agentic AI development. Built on DSPy 3.0, it features intelligent BDD evaluation, 
multi-layered memory systems, comprehensive observability, and a progressive tier system 
that scales from simple automation to enterprise complexity.

🚀 COMPLETE WORKFLOW:
super init → super spec generate → super spec validate → super agent compile → super agent evaluate → super agent optimize → super agent evaluate → super agent run → super orchestra

Start your journey: super init my_project && cd my_project && super spec generate genie developer --namespace software

✨ MIXIN-DEFAULT COMPILATION:
• Default: Mixin templates (60% code reduction, enhanced modularity)
• Legacy: Basic templates available via --basic flag for full control

🧪 ENHANCED BDD EVALUATION:
• Intelligent model analysis with capability scoring
• Auto-tuning evaluation criteria based on model performance  
• Smart recommendations for model upgrades and scenario optimization
• Professional test runner UI with comprehensive quality gates
• Progressive difficulty assessment with actionable guidance

🚀 MODEL INTELLIGENCE SYSTEM:
• Multi-backend model management (Ollama, MLX, HuggingFace, LM Studio)
• Smart model recommendations by use case and task
• Local server management for all backends
• Seamless DSPy integration with model-agnostic design
• Model discovery guides and installation assistance

COMPLETE MARKETPLACE:
• Unified discovery hub for agents and tools across all industries
• Universal search, category browsing, and intelligent recommendations
• Project-aware installation and seamless workflow integration

🛠️ MODULAR TOOLS ARCHITECTURE:
• Clean separation across 17 industry categories
• 29+ fully implemented tools with factory functions
• Easy extension points for custom tool development
• Seamless DSPy integration with backward compatibility

Key Features:
• 🎭 Progressive tier system (Oracles → Genies → Protocols)
• 🧪 BDD-driven agent validation with auto-tuning
• 🧠 Multi-layered memory systems (short-term, long-term, episodic)
• 📊 Comprehensive observability and tracing
• 🏪 Unified marketplace for agents and tools
• 🔧 Modular tools architecture across industries
• 🤖 Model-agnostic with intelligent recommendations
• 🚀 Production-ready with enterprise features

Core Commands:
• `super init <name>`           - Initialize a new SuperOptiX project
• `super agent <command>`       - Manage AI agents (pull, compile, evaluate, run)
• `super model <command>`       - Model intelligence system (list, install, serve)
• `super spec <command>`        - Agent DSL (generate, validate, analyze)
• `super orchestra <command>`        - Multi-agent orchestration
• `super observe <command>`     - Observability and monitoring
• `super marketplace <command>` - Discover agents and tools
• `super docs`                  - Comprehensive getting started guide

Model Management Examples:
• `super model list`                           - List installed models
• `super model install llama3.2:3b -b ollama` - Install Ollama model
• `super model install mlx-community/phi-2 -b mlx` - Install MLX model
• `super model server mlx phi-2 --port 8000`  - Start MLX server
• `super model dspy ollama/llama3.2:3b`       - Create DSPy client

Use `super <command> --help` for more information on a specific command.

📖 Learn more: https://github.com/SuperagenticAI/superoptix
"""

    # Main command parser
    parser = ArgumentParser(
        description=description, formatter_class=RawDescriptionHelpFormatter
    )

    # Add global version arguments
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Show the current SuperOptiX version",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=False
    )
    parser.set_defaults(func=show_welcome_screen)

    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show the current SuperOptiX version",
    )
    version_parser.set_defaults(func=show_version_screen)

    # Docs command
    docs_parser = subparsers.add_parser(
        "docs",
        help="📚 Comprehensive guide with examples and getting started information",
    )
    docs_parser.set_defaults(func=show_comprehensive_docs)

    # Auth commands - DISABLED FOR OSS VERSION
    # login_parser = subparsers.add_parser(
    #     "login",
    #     help="🔐 Login to SuperOptiX with GitHub",
    # )
    # login_parser.add_argument("--token", help="Login with access token directly")
    # login_parser.set_defaults(func=login)

    # logout_parser = subparsers.add_parser(
    #     "logout",
    #     help="🚪 Logout from SuperOptiX",
    # )
    # logout_parser.set_defaults(func=logout)

    # whoami_parser = subparsers.add_parser(
    #     "whoami",
    #     help="👤 Show current logged in user",
    # )
    # whoami_parser.set_defaults(func=whoami)

    # === DATASET Command (NEW! Dataset Marketplace) ===
    dataset_parser = subparsers.add_parser(
        "dataset",
        aliases=["data", "ds"],
        help="Browse and pull example datasets",
        description="Manage example datasets for agent training and evaluation.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    dataset_main_subparsers = dataset_parser.add_subparsers(
        dest="dataset_command", help="Dataset commands", required=True
    )

    # super dataset list
    list_datasets_main_parser = dataset_main_subparsers.add_parser(
        "list",
        aliases=["ls"],
        help="List available example datasets",
        formatter_class=RawDescriptionHelpFormatter,
    )
    list_datasets_main_parser.set_defaults(func=list_example_datasets)

    # super dataset pull
    pull_dataset_main_parser = dataset_main_subparsers.add_parser(
        "pull",
        help="Pull an example dataset to your project",
        formatter_class=RawDescriptionHelpFormatter,
    )
    pull_dataset_main_parser.add_argument("name", help="Name of the dataset to pull")
    pull_dataset_main_parser.set_defaults(func=pull_example_dataset)

    # super dataset show
    show_dataset_main_parser = dataset_main_subparsers.add_parser(
        "show",
        help="Show details about an example dataset",
        formatter_class=RawDescriptionHelpFormatter,
    )
    show_dataset_main_parser.add_argument("name", help="Name of the dataset")
    show_dataset_main_parser.set_defaults(func=show_dataset_details)

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="🚀 Initialize a new agentic system - Your journey starts here!"
    )
    init_parser.add_argument("name", help="Name of the agent system")
    init_parser.set_defaults(func=init_project)

    # Agent commands
    agent_parser = subparsers.add_parser(
        "agent",
        aliases=["ag"],
        help="Manage AI agents",
        formatter_class=RawDescriptionHelpFormatter,
        description="""
Manage the lifecycle of AI agents in your SuperOptiX project.

This command suite provides a comprehensive workflow to handle everything
from adding and optimizing agents to testing and deploying them.

Recommended Workflow:
  1. `super agent pull <name>`       - Pull a pre-built agent into your project
  2. `super agent compile <name>`   - Compile the agent's playbook into runnable code
  3. `super agent optimize <name>`  - Enhance performance using DSPy optimization
  4. `super agent evaluate <name>`   - Evaluate an agent using its BDD specification tests
  5. `super agent run <name>`        - Execute the optimized agent with tasks
  6. `super agent inspect <name>`    - View detailed information about an agent
  7. `super agent rm <name>`         - Remove an agent from your project

Advanced Commands:
  • `super agent design`           - Interactively design custom agents
  • `super agent lint`             - Validate playbook syntax and best practices
  • `super agent list`             - Browse available agents and project status

Use `super agent <command> --help` for more information on a specific command.
        """,
    )
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_command", help="[AGENT]", required=False
    )

    # super agent pull (formerly 'add')
    add_parser = agent_subparsers.add_parser(
        "pull",
        aliases=["pl"],
        help="Pull a pre-built agent into your project.",
        description="Copies a pre-built agent playbook from the library to your project's agents directory.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    add_parser.add_argument("name", help="The name of the pre-built agent to add.")
    add_parser.add_argument(
        "--tier",
        choices=["oracles", "genies"],
        default="oracles",
        help="Agent tier level (default: oracles). Genies-tier includes ReAct agents, tools, and RAG support.",
    )
    add_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite if an agent with the same name already exists.",
    )
    add_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed guidance and customization options",
    )
    add_parser.set_defaults(func=add_agent)

    # super agent compile
    compile_parser = agent_subparsers.add_parser(
        "compile",
        aliases=["co"],
        help="Compile an agent playbook into a Python pipeline.",
        description="Transforms a YAML playbook into executable Python code. Uses explicit DSPy template by default (pure DSPy, no mixins, fully transparent code you can understand and modify).",
        formatter_class=RawDescriptionHelpFormatter,
    )
    compile_parser.add_argument(
        "name", nargs="?", help="The name of the agent to compile."
    )
    compile_parser.add_argument(
        "--framework",
        "-f",
        choices=[
            "dspy",
            "microsoft",
            "openai",
            "deepagents",
            "crewai",
            "google-adk",
            "pydantic-ai",
            "claude-sdk",
        ],
        default="dspy",
        help="Target agent framework (default: dspy). Compile the same agent to different frameworks.",
    )
    compile_parser.add_argument(
        "--target",
        choices=[
            "dspy",
            "optimas-dspy",
            "optimas-crewai",
            "optimas-autogen",
            "optimas-openai",
        ],
        default="dspy",
        help="Select compilation target backend (default: dspy)",
    )
    compile_parser.add_argument(
        "--tier",
        choices=["oracles", "genies"],
        help="Override playbook tier for compilation. Use 'genie' for ReAct agents with tools and RAG.",
    )
    compile_parser.add_argument(
        "--all", action="store_true", help="Compile all agents in the project."
    )
    compile_parser.add_argument(
        "--optimize",
        action="store_true",
        help="Generate the full optimization/evaluation pipeline (default compile generates a minimal PyTorch-like DSPy pipeline).",
    )
    compile_parser.add_argument(
        "--rlm",
        action="store_true",
        help="DSPy only: opt into dspy.RLM in minimal mode (default remains ChainOfThought/ReAct).",
    )
    compile_parser.add_argument(
        "--local-ollama",
        dest="local_ollama",
        action="store_true",
        help="Generate Ollama runtime code path (default behavior is already Ollama-first; this flag is kept for explicitness).",
    )
    compile_parser.add_argument(
        "--local-models",
        dest="local_ollama",
        action="store_true",
        help="Deprecated alias for --local-ollama.",
    )
    compile_mode_group = compile_parser.add_mutually_exclusive_group()
    compile_mode_group.add_argument(
        "--local",
        action="store_true",
        help="Compile for local runtime mode (default provider: ollama).",
    )
    compile_mode_group.add_argument(
        "--cloud",
        action="store_true",
        help="Compile for cloud runtime mode (provider/model required via playbook or flags).",
    )
    compile_runtime_group = compile_parser.add_mutually_exclusive_group()
    compile_runtime_group.add_argument(
        "--direct",
        action="store_true",
        help="Pydantic AI: use direct provider runtime mode.",
    )
    compile_runtime_group.add_argument(
        "--gateway",
        action="store_true",
        help="Pydantic AI: use gateway runtime mode.",
    )
    compile_parser.add_argument(
        "--provider",
        help="Override model provider at compile time (e.g. ollama, openai, google-genai, anthropic, vllm, mlx, lmstudio).",
    )
    compile_parser.add_argument(
        "--model",
        help="Override model id at compile time (e.g. llama3.1:8b, gpt-4o-mini, gemini-2.5-flash-lite).",
    )
    compile_parser.add_argument(
        "--gateway-url",
        help="Pydantic AI gateway base URL (used when --gateway is enabled).",
    )
    compile_parser.add_argument(
        "--gateway-key-env",
        default="PYDANTIC_AI_GATEWAY_API_KEY",
        help="Env var name containing gateway API key (default: PYDANTIC_AI_GATEWAY_API_KEY).",
    )
    compile_parser.add_argument(
        "--explicit",
        action="store_true",
        default=True,
        help="Use explicit DSPy template with no mixins (DEFAULT, pure DSPy code you can understand and modify).",
    )
    compile_parser.add_argument(
        "--no-explicit",
        dest="explicit",
        action="store_false",
        help="Disable explicit template (use legacy mixin-based template).",
    )
    compile_parser.add_argument(
        "--abstracted",
        action="store_true",
        help="Use abstracted pipeline with SuperOptixPipeline base class (85%% less code, overrides --explicit).",
    )
    compile_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed guidance and feature explanations",
    )
    compile_parser.set_defaults(func=compile_agent)

    # super agent design
    design_parser = agent_subparsers.add_parser(
        "design",
        aliases=["de"],
        help="Interactively design an agent.",
        description="Starts an interactive session to help you design an agent and its tier.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    design_parser.add_argument("agent", help="Name of the agent to design.")
    design_parser.add_argument(
        "--tier", help="Specify the agent tier for the designer."
    )
    design_parser.set_defaults(func=design_agent)

    # super agent inspect
    inspect_parser = agent_subparsers.add_parser(
        "inspect",
        aliases=["in"],
        help="Show detailed information and metadata about an agent.",
        description="Displays the configuration, capabilities, and dependencies of an agent from its playbook.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    inspect_parser.add_argument("name", help="The name of the agent to inspect.")
    inspect_parser.set_defaults(func=inspect_agent)

    # super agent lint
    lint_parser = agent_subparsers.add_parser(
        "lint",
        aliases=["li"],
        help="Validate agent playbooks for syntax and best practices.",
        description="Checks agent playbooks for correctness without compiling them.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    lint_parser.add_argument("name", nargs="?", help="The name of the agent to lint.")
    lint_parser.add_argument(
        "--all", action="store_true", help="Lint all agents in the project."
    )
    lint_parser.set_defaults(func=lint_agent)

    # super agent list (with ps alias)
    list_parser = agent_subparsers.add_parser(
        "list",
        aliases=["ps", "ls"],
        help="List all agents in the project or pre-built agents available.",
        description="Shows agents in your project, or lists all pre-built agents available to be added. Alias: 'ps' (like docker ps)",
        formatter_class=RawDescriptionHelpFormatter,
    )
    list_parser.add_argument(
        "-p",
        "--pre-built",
        action="store_true",
        help="List all available pre-built agents from the library.",
    )
    list_parser.add_argument("--industry", help="Filter pre-built agents by industry.")
    list_parser.set_defaults(func=list_agents)

    # super agent optimize
    optimize_parser = agent_subparsers.add_parser(
        "optimize",
        aliases=["op"],
        help="Optimize an agent pipeline using DSPy or Optimas.",
        description="Uses DSPy or Optimas optimization to improve the agent's performance.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    optimize_parser.add_argument("name", help="The name of the agent to optimize.")
    optimize_parser.add_argument(
        "--framework",
        "-f",
        choices=[
            "dspy",
            "microsoft",
            "openai",
            "deepagents",
            "crewai",
            "google-adk",
            "pydantic-ai",
            "claude-sdk",
        ],
        default="dspy",
        help="Agent framework to optimize (default: dspy). GEPA works with all frameworks.",
    )
    optimize_parser.add_argument(
        "--engine",
        choices=["dspy", "optimas"],
        default="dspy",
        help="Optimization engine (default: dspy)",
    )
    optimize_parser.add_argument(
        "--target",
        choices=[
            "optimas-dspy",
            "optimas-crewai",
            "optimas-openai",
            "optimas-autogen",
        ],
        help="Optimas pipeline target to use when --engine=optimas",
    )
    optimize_mode_group = optimize_parser.add_mutually_exclusive_group()
    optimize_mode_group.add_argument(
        "--local",
        action="store_true",
        help="Optimize in local mode (default provider: ollama unless overridden).",
    )
    optimize_mode_group.add_argument(
        "--cloud",
        action="store_true",
        help="Optimize in cloud mode (rejects local-only providers like ollama).",
    )
    optimize_parser.add_argument(
        "--provider",
        help="Provider override for optimization/runtime (e.g. ollama, openai, google-genai, anthropic).",
    )
    optimize_parser.add_argument(
        "--model",
        help="Model override for optimization task model (e.g. llama3.1:8b, gemini-2.5-flash-lite).",
    )
    optimize_parser.add_argument(
        "--optimizer",
        choices=["opro", "mipro", "copro"],
        default="opro",
        help="Prompt optimizer to use with --engine=optimas (default: opro). Note: mipro/copro currently require --target optimas-dspy.",
    )
    optimize_parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-optimization even if an optimized version exists",
    )
    # GEPA-specific parameters
    optimize_parser.add_argument(
        "--auto",
        choices=["light", "medium", "heavy"],
        help="GEPA auto budget: light (~6 candidates), medium (~12), heavy (~18)",
    )
    optimize_parser.add_argument(
        "--reflection-lm",
        help="Language model for GEPA reflection (e.g., 'gpt-4o', 'gpt-4o-mini'). Required for GEPA.",
    )
    optimize_parser.add_argument(
        "--max-full-evals",
        type=int,
        help="GEPA: Maximum number of full evaluations (alternative to --auto)",
    )
    optimize_parser.add_argument(
        "--max-metric-calls",
        type=int,
        help="GEPA: Maximum number of metric calls (alternative to --auto)",
    )
    optimize_parser.add_argument(
        "--reflection-minibatch-size",
        type=int,
        default=3,
        help="GEPA: Number of examples per reflection step (default: 3)",
    )
    optimize_parser.add_argument(
        "--skip-perfect-score",
        action="store_true",
        default=True,
        help="GEPA: Skip examples with perfect scores during reflection (default: True)",
    )
    optimize_parser.add_argument(
        "--use-merge",
        action="store_true",
        default=True,
        help="GEPA: Enable merge-based optimization (default: True)",
    )
    optimize_parser.add_argument(
        "--log-dir",
        help="GEPA: Directory to save optimization logs",
    )
    optimize_parser.add_argument(
        "--track-stats",
        action="store_true",
        help="GEPA: Track detailed optimization statistics",
    )
    optimize_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed guidance and optimization information",
    )
    optimize_parser.add_argument(
        "--fresh",
        action="store_true",
        help="Clear DSPy cache before optimization to see real GEPA iterations (recommended for demos)",
    )
    optimize_parser.set_defaults(func=optimize_agent)

    # super agent dataset (NEW! Dataset management commands)
    dataset_parser = agent_subparsers.add_parser(
        "dataset",
        aliases=["ds"],
        help="Manage external datasets for agents.",
        description="Preview, validate, and get info about external datasets configured in agent playbooks.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    dataset_subparsers = dataset_parser.add_subparsers(
        dest="dataset_command", help="Dataset management commands", required=True
    )

    # super agent dataset preview
    preview_parser = dataset_subparsers.add_parser(
        "preview",
        aliases=["pr"],
        help="Preview examples from configured datasets",
        formatter_class=RawDescriptionHelpFormatter,
    )
    preview_parser.add_argument("name", help="The name of the agent")
    preview_parser.add_argument(
        "--limit", type=int, default=5, help="Number of examples to show (default: 5)"
    )
    preview_parser.set_defaults(func=preview_dataset)

    # super agent dataset validate
    validate_ds_parser = dataset_subparsers.add_parser(
        "validate",
        aliases=["val"],
        help="Validate dataset configuration",
        formatter_class=RawDescriptionHelpFormatter,
    )
    validate_ds_parser.add_argument("name", help="The name of the agent")
    validate_ds_parser.set_defaults(func=validate_dataset)

    # super agent dataset info
    info_parser = dataset_subparsers.add_parser(
        "info",
        aliases=["in"],
        help="Show dataset statistics",
        formatter_class=RawDescriptionHelpFormatter,
    )
    info_parser.add_argument("name", help="The name of the agent")
    info_parser.set_defaults(func=dataset_info)

    # super agent rm
    remove_parser = agent_subparsers.add_parser(
        "rm",
        help="Remove an agent from the project.",
        description="Deletes an agent's playbook and its compiled pipeline from the project.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    remove_parser.add_argument("name", help="The name of the agent to remove.")
    remove_parser.set_defaults(func=remove_agent)

    # super agent run
    run_parser = agent_subparsers.add_parser(
        "run",
        aliases=["ru"],
        help="Run a compiled agent.",
        description="Executes a compiled agent with a given task.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    run_parser.add_argument("name", help="The name of the agent to run.")
    run_parser.add_argument(
        "--goal", required=True, help="Goal description for the agent."
    )
    run_parser.add_argument(
        "--observe",
        choices=["superoptix", "mlflow", "langfuse", "wandb", "all"],
        default="superoptix",
        help="Observability backend to use (default: superoptix - local storage)",
    )
    run_parser.add_argument(
        "--framework",
        "-f",
        choices=[
            "dspy",
            "microsoft",
            "openai",
            "deepagents",
            "crewai",
            "google-adk",
            "pydantic-ai",
            "claude-sdk",
        ],
        default="dspy",
        help="Agent framework to run (default: dspy). Must match the framework used during compilation.",
    )
    run_parser.add_argument(
        "--engine",
        choices=["dspy", "optimas"],
        default="dspy",
        help="Execution engine (default: dspy)",
    )
    run_parser.add_argument(
        "--target",
        choices=[
            "optimas-dspy",
            "optimas-crewai",
            "optimas-openai",
            "optimas-autogen",
        ],
        help="Optimas pipeline target to use when --engine=optimas",
    )
    run_mode_group = run_parser.add_mutually_exclusive_group()
    run_mode_group.add_argument(
        "--local",
        action="store_true",
        help="Run in local mode (no cloud fallback).",
    )
    run_mode_group.add_argument(
        "--cloud",
        action="store_true",
        help="Run in cloud mode (requires cloud-capable provider/model).",
    )
    run_runtime_group = run_parser.add_mutually_exclusive_group()
    run_runtime_group.add_argument(
        "--direct",
        action="store_true",
        help="Pydantic AI: use direct provider runtime mode.",
    )
    run_runtime_group.add_argument(
        "--gateway",
        action="store_true",
        help="Pydantic AI: use gateway runtime mode.",
    )
    run_parser.add_argument(
        "--provider",
        help="Runtime provider override for DSPy (e.g. ollama, openai, google-genai).",
    )
    run_parser.add_argument(
        "--model",
        help="Runtime model override for DSPy.",
    )
    run_parser.add_argument(
        "--gateway-url",
        help="Pydantic AI gateway base URL (used when --gateway is enabled).",
    )
    run_parser.add_argument(
        "--gateway-key-env",
        default="PYDANTIC_AI_GATEWAY_API_KEY",
        help="Env var name containing gateway API key (default: PYDANTIC_AI_GATEWAY_API_KEY).",
    )
    run_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed guidance and next steps",
    )
    run_parser.set_defaults(func=run_agent)

    # super agent evaluate
    test_parser = agent_subparsers.add_parser(
        "evaluate",
        aliases=["ev"],
        help="Evaluate an agent using its BDD specification tests.",
        description="Executes the BDD specification suite for a specified agent to validate its behavior.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    test_parser.add_argument("name", help="Name of the agent to test")
    test_parser.add_argument(
        "--engine",
        choices=["dspy", "optimas"],
        default="dspy",
        help="Evaluation engine (default: dspy)",
    )
    test_parser.add_argument(
        "--target",
        choices=[
            "optimas-dspy",
            "optimas-crewai",
            "optimas-openai",
            "optimas-autogen",
        ],
        help="Optimas pipeline target to use when --engine=optimas",
    )
    test_parser.add_argument(
        "--auto-tune",
        action="store_true",
        help="Enable auto-tuning for evaluation metrics",
    )
    test_parser.add_argument(
        "--ignore-checks",
        action="store_true",
        help="Ignore non-essential checks during testing",
    )
    test_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed results for each BDD specification",
    )
    test_parser.add_argument(
        "--format",
        choices=["table", "json", "junit"],
        default="table",
        help="Output format for test results (default: table)",
    )
    test_parser.add_argument(
        "--save-report",
        metavar="FILE",
        help="Save detailed test report to file",
    )
    test_parser.set_defaults(func=test_agent_bdd)

    # super agent tier-status
    tier_status_parser = agent_subparsers.add_parser(
        "tier-status",
        aliases=["ts"],
        help="Show tier status for agents.",
        description="Displays the tier status and capabilities of agents in the project.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    tier_status_parser.set_defaults(func=show_tier_status)

    # Set default function for agent command if no subcommand is provided
    agent_parser.set_defaults(
        func=lambda args: (
            agent_parser.print_help() if args.agent_command else show_tier_status({})
        )
    )

    # Orchestra commands
    orchestra_parser = subparsers.add_parser(
        "orchestra",
        aliases=["orch"],
        help="Manage multi-agent workflows",
        formatter_class=RawDescriptionHelpFormatter,
        description="""
Orchestrate multiple agents to perform complex, coordinated tasks.

SuperOptiX orchestras allow you to define workflows where agents collaborate
to achieve a common goal. This command suite helps you create, manage, and
run these powerful multi-agent systems.

Recommended Workflow:
  1. `super orchestra create <name>` - Create a new orchestra definition
2. `super orchestra run <name>`    - Execute an orchestra with a specific task
3. `super orchestra list`         - Browse all orchestras in your project

Use `super orchestra <command> --help` for more information.
        """,
    )
    orchestra_subparsers = orchestra_parser.add_subparsers(
        dest="orchestra_command", help="[ORCHESTRA]", required=False
    )

    # Set default func for orchestra
    orchestra_parser.set_defaults(func=lambda args: orchestra_parser.print_help())

    # super orchestra create
    create_orchestra_parser = orchestra_subparsers.add_parser(
        "create",
        aliases=["cr"],
        help="Create a new orchestra",
        formatter_class=RawDescriptionHelpFormatter,
    )
    create_orchestra_parser.add_argument("name", help="Name of the orchestra to create")
    create_orchestra_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed guidance and customization options",
    )
    create_orchestra_parser.set_defaults(func=create_orchestra)

    # super orchestra list
    list_orchestras_parser = orchestra_subparsers.add_parser(
        "list",
        aliases=["ls"],
        help="List all orchestras in the project",
        formatter_class=RawDescriptionHelpFormatter,
    )
    list_orchestras_parser.set_defaults(func=list_orchestras)

    # super orchestra run
    run_orchestra_parser = orchestra_subparsers.add_parser(
        "run",
        aliases=["ru"],
        help="Run an orchestra",
        formatter_class=RawDescriptionHelpFormatter,
    )
    run_orchestra_parser.add_argument("name", help="Name of the orchestra to run")
    run_orchestra_parser.add_argument(
        "--goal", required=True, help="Goal description for the orchestra"
    )
    run_orchestra_parser.set_defaults(func=run_orchestra)

    # Marketplace commands
    marketplace_parser = subparsers.add_parser(
        "marketplace",
        aliases=["market", "mk"],
        help="🏪 Discover and install agents and tools",
        formatter_class=RawDescriptionHelpFormatter,
        description="""
Unified discovery hub for AI agents and tools - your component marketplace.

Browse, search, and install agents and tools from SuperOptiX's comprehensive library.
Perfect for discovering new capabilities and finding the right components for your project.

Quick Start:
  super marketplace                    - Dashboard overview with stats
super marketplace browse agents      - Browse all available agents  
      super marketplace browse tools       - Browse all available tools
    super marketplace search "web"       - Universal search across components
      super marketplace featured          - See popular components

Advanced Discovery:
  super marketplace browse industries  - Explore agent industries
super marketplace browse categories  - Explore tool categories
super marketplace show <component>   - Detailed component information
super marketplace install agent <name> - Quick install (same as super agent pull)

Use `super marketplace <command> --help` for more information.
        """,
    )
    marketplace_subparsers = marketplace_parser.add_subparsers(
        dest="marketplace_command", help="[MARKETPLACE]", required=False
    )
    marketplace_parser.set_defaults(func=marketplace_dashboard)

    # super marketplace browse
    marketplace_browse_parser = marketplace_subparsers.add_parser(
        "browse",
        aliases=["br"],
        help="Browse components by category",
        description="Browse agents, tools, industries, or categories with filtering options.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    marketplace_browse_parser.add_argument(
        "type",
        choices=["agents", "tools", "industries", "categories"],
        help="What to browse: agents, tools, industries, or categories",
    )
    marketplace_browse_parser.add_argument(
        "--industry", help="Filter agents by industry (when browsing agents)"
    )
    marketplace_browse_parser.add_argument(
        "--category", help="Filter tools by category (when browsing tools)"
    )
    marketplace_browse_parser.add_argument(
        "--tier", choices=["oracles", "genies"], help="Filter by tier level"
    )
    marketplace_browse_parser.set_defaults(func=browse_marketplace)

    # super marketplace search
    marketplace_search_parser = marketplace_subparsers.add_parser(
        "search",
        aliases=["se"],
        help="Universal search across agents and tools",
        description="Search for components by name, description, industry, or category.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    marketplace_search_parser.add_argument("query", help="Search term or phrase")
    marketplace_search_parser.set_defaults(func=search_marketplace)

    # super marketplace show
    marketplace_show_parser = marketplace_subparsers.add_parser(
        "show",
        aliases=["sh"],
        help="Show detailed information about a component",
        description="Display comprehensive details about an agent or tool including usage examples.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    marketplace_show_parser.add_argument("name", help="Name of the component to show")
    marketplace_show_parser.set_defaults(func=show_component)

    # super marketplace featured
    marketplace_featured_parser = marketplace_subparsers.add_parser(
        "featured",
        aliases=["fe"],
        help="Show featured/popular components",
        description="Display curated list of popular and recommended agents and tools.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    marketplace_featured_parser.set_defaults(func=show_featured)

    # super marketplace install
    marketplace_install_parser = marketplace_subparsers.add_parser(
        "install",
        aliases=["in"],
        help="Install a component (convenience wrapper)",
        description="Quick install command for agents and tools. Same as 'super agent pull' but discoverable via marketplace.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    marketplace_install_parser.add_argument(
        "type", choices=["agent", "tool"], help="Type of component to install"
    )
    marketplace_install_parser.add_argument(
        "name", help="Name of the component to install"
    )
    marketplace_install_parser.set_defaults(func=install_component)

    # SuperSpec DSL commands
    superspec_parser = subparsers.add_parser(
        "spec",
        aliases=["sx-dsl"],
        help="🤖 Agent DSL for playbook management",
        formatter_class=RawDescriptionHelpFormatter,
        description="""
🎭 SuperSpec DSL - Agent Playbook Definition Language

🚀 Create, validate, and manage AI agent playbooks with SuperSpec DSL!

📚 Quick Start:
  super spec generate genies my-agent --namespace software
  super spec validate my-agent_playbook.yaml
  super spec analyze ./agents/

🎯 Available Commands:
  generate  - 🎨 Create new agent playbook templates
  validate  - ✅ Check playbook syntax and structure
  analyze   - 📊 Get insights about your playbooks
  info      - 📋 Show detailed playbook information
  schema    - 📚 Explore DSL schema and features
  bootstrap - 🚀 Generate multiple agents for a namespace

✨ Key Features:
  • 🎯 Tier-based agent templates (Oracles and Genies)
  • ✅ Comprehensive validation with detailed error reporting
  • 📊 Project-wide agent analysis and insights
  • 🚀 Namespace bootstrapping for rapid development
  • 📋 Rich schema documentation and guidance

💡 Common Workflow:
  1. super spec generate genies developer --namespace software
  2. super spec validate developer.yaml
  3. super agent compile developer
  4. super spec analyze ./agents

Use 'super spec <command> --help' for more information.
        """,
    )
    superspec_subparsers = superspec_parser.add_subparsers(
        dest="spec_command", help="[SPEC]", required=False
    )
    superspec_parser.set_defaults(func=lambda args: superspec_parser.print_help())

    # super spec generate
    generate_parser = superspec_subparsers.add_parser(
        "generate",
        aliases=["gen"],
        help="🎨 Generate agent playbook templates",
        description="""
🎨 Generate agent playbook templates with customizable features.

✨ Examples:
  super spec generate genies data-analyst --namespace finance
  super spec generate oracles chatbot --output ./my-agents/
  super spec generate genies assistant --no-rag --format json

🎯 Tiers:
  oracles - Basic agent with chain-of-thought reasoning
  genies  - Advanced agent with memory, tools, and optimization

🔧 Features (Genies only):
  • 💾 Memory system for context retention
  • 🔧 Tool integration for external actions
  • 🔍 RAG/retrieval for knowledge access
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    generate_parser.add_argument(
        "tier",
        choices=["oracles", "genies"],
        help="🎯 Agent tier: oracles (basic) or genies (advanced)",
    )
    generate_parser.add_argument(
        "name", help="🤖 Agent name (e.g., 'data-analyst', 'customer-support')"
    )
    generate_parser.add_argument(
        "--namespace",
        default="software",
        choices=[
            "software",
            "healthcare",
            "finance",
            "education",
            "legal",
            "marketing",
            "manufacturing",
            "retail",
            "transportation",
            "energy",
            "agriculture",
            "consulting",
            "government",
            "human_resources",
            "hospitality",
            "real_estate",
            "media",
            "gaming",
        ],
        help="🏷️ Agent namespace (software, finance, healthcare, etc.)",
    )
    generate_parser.add_argument(
        "--role", default="Assistant", help="👤 Agent role description"
    )
    generate_parser.add_argument("--description", help="📝 Detailed agent description")
    generate_parser.add_argument(
        "--output",
        help="📁 Output directory or file path (auto-creates filename if directory)",
    )
    generate_parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="📄 Output format (yaml or json)",
    )
    generate_parser.add_argument(
        "--memory",
        action="store_true",
        default=True,
        help="💾 Enable memory system (Genies only)",
    )
    generate_parser.add_argument(
        "--no-memory",
        dest="memory",
        action="store_false",
        help="💾 Disable memory system",
    )
    generate_parser.add_argument(
        "--tools",
        action="store_true",
        default=True,
        help="🔧 Enable tool integration (Genies only)",
    )
    generate_parser.add_argument(
        "--no-tools",
        dest="tools",
        action="store_false",
        help="🔧 Disable tool integration",
    )
    generate_parser.add_argument(
        "--rag",
        action="store_true",
        default=False,
        help="🔍 Enable RAG/retrieval (Genies only)",
    )
    generate_parser.set_defaults(func=generate_agent)

    # super spec validate
    validate_parser = superspec_subparsers.add_parser(
        "validate",
        aliases=["val"],
        help="✅ Validate agent playbooks",
        description="""
✅ Validate agent playbook files against SuperSpec schema.

🔍 Checks syntax, structure, and compliance with tier-specific constraints.

✨ Examples:
  super spec validate my-agent_playbook.yaml
  super spec validate *.yaml --verbose
  super spec validate agent1.yaml agent2.yaml --format json

📋 Validates:
  • YAML/JSON syntax and structure
  • Required fields and metadata
  • Tier-specific constraints and features
  • Namespace compatibility
  • Agent flow and task definitions
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    validate_parser.add_argument(
        "files", nargs="+", help="📄 Playbook files to validate"
    )
    validate_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="🔍 Show detailed validation output",
    )
    validate_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="📊 Output format (table or json)",
    )
    validate_parser.set_defaults(func=validate_agents)

    # super spec analyze
    analyze_parser = superspec_subparsers.add_parser(
        "analyze",
        aliases=["an"],
        help="📊 Analyze agent ecosystem",
        description="""
📊 Analyze agent playbooks to provide insights on your agent collection.

🔍 Get comprehensive insights about tier distribution, feature usage, and project structure.

✨ Examples:
  super spec analyze ./agents/
  super spec analyze my-playbook.yaml
  super spec analyze ./ --pattern "*.json" --format json

📈 Provides:
  • 🤖 Agent overview and statistics
  • 🎯 Tier and namespace distribution
  • ⚡ Feature usage analysis
  • 📋 Task count and complexity metrics
  • 📊 Project structure insights
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    analyze_parser.add_argument("path", help="📁 Directory or file path to analyze")
    analyze_parser.add_argument(
        "--pattern", default="*.yaml", help="🔍 File pattern to match (default: *.yaml)"
    )
    analyze_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="📊 Output format (table or json)",
    )
    analyze_parser.set_defaults(func=analyze_agents)

    # super spec info
    info_parser = superspec_subparsers.add_parser(
        "info",
        aliases=["inf"],
        help="📋 Show detailed agent information",
        description="""
📋 Show comprehensive information about a specific agent playbook.

🔍 Get detailed insights about metadata, features, tasks, and configuration.

✨ Examples:
  super spec info my-agent_playbook.yaml
  super spec info ./agents/developer/playbook/developer_playbook.yaml

📊 Shows:
  • 📋 Agent metadata and configuration
  • 🧠 Language model settings
  • 📋 Task definitions and flow
  • ⚡ Feature capabilities
  • ✅ Validation status
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    info_parser.add_argument("file", help="📄 Agent playbook file")
    info_parser.set_defaults(func=show_info)

    # super spec schema
    schema_parser = superspec_subparsers.add_parser(
        "schema",
        aliases=["sch"],
        help="📚 Show DSL schema information",
        description="""
📚 Show SuperSpec DSL schema information and tier capabilities.

🔍 Explore the DSL structure, supported features, and tier comparisons.

✨ Examples:
  super spec schema
  super spec schema --tier genie
  super spec schema --tier oracle

📖 Provides:
  • 📚 Schema overview and structure
  • 🎯 Tier feature comparison
  • ✅ Allowed and forbidden features
  • 🏷️ Namespace and component information
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    schema_parser.add_argument(
        "--tier",
        choices=["oracles", "genies"],
        help="🎯 Show features for specific tier",
    )
    schema_parser.set_defaults(func=show_schema)

    # super spec bootstrap
    bootstrap_parser = superspec_subparsers.add_parser(
        "bootstrap",
        aliases=["boot"],
        help="🚀 Bootstrap agents for a namespace",
        description="""
🚀 Bootstrap agents for a namespace with common roles and configurations.

⚡ Quickly generate multiple agent playbooks for a specific domain or namespace.

✨ Examples:
  super spec bootstrap --namespace software
  super spec bootstrap --namespace finance --tiers genie
  super spec bootstrap --namespace healthcare --output-dir ./healthcare-agents/

🎯 Creates:
  • Multiple agent playbooks for the namespace
  • Common roles and responsibilities
  • Proper directory structure
  • Ready-to-customize templates
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    bootstrap_parser.add_argument(
        "namespace",
        choices=[
            "software",
            "healthcare",
            "finance",
            "education",
            "legal",
            "marketing",
            "manufacturing",
            "retail",
            "transportation",
            "energy",
            "agriculture",
            "consulting",
            "government",
            "human_resources",
            "hospitality",
            "real_estate",
            "media",
            "gaming",
        ],
        help="🏷️ Target namespace (software, finance, healthcare, etc.)",
    )
    bootstrap_parser.add_argument(
        "--output-dir",
        default="./generated_agents",
        help="📁 Output directory for generated agents (default: ./generated_agents)",
    )
    bootstrap_parser.add_argument(
        "--tiers",
        nargs="*",
        choices=["oracles", "genies"],
        default=["oracles", "genies"],
        help="🎯 Tiers to generate (default: both oracle and genie)",
    )
    bootstrap_parser.set_defaults(func=bootstrap_namespace)

    # Model management commands - SuperOptiX Model Intelligence System
    def handle_model_list(args):
        """Handle model list command."""
        from superoptix.cli.commands.model import list_models

        list_models(
            backend=getattr(args, "backend", None),
            size=getattr(args, "size", None),
            task=getattr(args, "task", None),
            installed_only=getattr(args, "installed_only", True),
            all_models=getattr(args, "all_models", False),
            verbose=getattr(args, "verbose", False),
        )

    def handle_model_discover(args):
        """Handle model discover command."""
        from superoptix.cli.commands.model import discover_models

        discover_models()

    def handle_model_guide(args):
        """Handle model guide command."""
        from superoptix.cli.commands.model import model_guide

        model_guide()

    def handle_model_install(args):
        """Handle model install command."""
        from superoptix.cli.commands.model import install_model

        install_model(
            model_name=getattr(args, "model_name", None),
            backend=getattr(args, "backend", None),
        )

    def handle_model_info(args):
        """Handle model info command."""
        from superoptix.cli.commands.model import model_info

        model_info(model_name=getattr(args, "model_name", None))

    def handle_model_backends(args):
        """Handle model backends command."""
        from superoptix.cli.commands.model import list_backends

        list_backends()

    def handle_model_dspy(args):
        """Handle model dspy command."""
        from superoptix.cli.commands.model import create_dspy_client

        create_dspy_client(
            model_name=getattr(args, "model_name", None),
            temperature=getattr(args, "temperature", 0.7),
            max_tokens=getattr(args, "max_tokens", 2048),
        )

    def handle_model_server(args):
        """Handle model server command."""
        from superoptix.cli.commands.model import start_server

        start_server(
            backend=getattr(args, "backend", None),
            model_name=getattr(args, "model_name", None),
            port=getattr(args, "port", None),
        )

    def handle_model_refresh(args):
        """Handle model refresh command."""
        from superoptix.cli.commands.model import refresh_models

        refresh_models()

    def handle_model_remove(args):
        """Handle model remove command."""
        from superoptix.cli.commands.model import remove_model

        remove_model(
            model_name=getattr(args, "model_name", None),
            backend=getattr(args, "backend", None),
            all_backends=getattr(args, "all_backends", False),
        )

    def handle_model_run(args):
        """Handle model run command."""
        from superoptix.cli.commands.model import run_model

        run_model(
            model_name=getattr(args, "model_name", None),
            prompt=getattr(args, "prompt", None),
            backend=getattr(args, "backend", None),
            interactive=getattr(args, "interactive", False),
            max_tokens=getattr(args, "max_tokens", 2048),
            temperature=getattr(args, "temperature", 0.7),
        )

    def handle_model_convert(args):
        """Handle model convert command."""
        from superoptix.cli.commands.model import convert_model

        convert_model(
            hf_model=getattr(args, "hf_model", None),
            output_path=getattr(args, "output", None),
            quantize=getattr(args, "quantize", False),
            q_bits=getattr(args, "bits", 4),
            q_group_size=getattr(args, "group_size", 64),
            quant_recipe=getattr(args, "quant_recipe", None),
            dtype=getattr(args, "dtype", None),
            upload_repo=getattr(args, "upload", None),
            dequantize=getattr(args, "dequantize", False),
            trust_remote_code=getattr(args, "trust_remote_code", False),
        )

    def handle_model_quantize(args):
        """Handle model quantize command."""
        from superoptix.cli.commands.model import quantize_model

        quantize_model(
            model_name=getattr(args, "model_name", None),
            output_path=getattr(args, "output", None),
            q_bits=getattr(args, "bits", 4),
            q_group_size=getattr(args, "group_size", 64),
            quant_recipe=getattr(args, "recipe", None),
            dequantize=getattr(args, "dequantize", False),
        )

    model_parser = subparsers.add_parser(
        "model",
        aliases=["md"],
        help="🚀 SuperOptiX Model Intelligence System",
        formatter_class=RawDescriptionHelpFormatter,
        description="""
🚀 SuperOptiX Model Intelligence System - Advanced model management for agentic AI.

Manage installed models across different backends with SuperOptiX branding and philosophy.
Focus on models you actually have installed, with guidance on how to get more.

✨ Quick Examples:
  super model list                           # List installed models
  super model discover                       # Model discovery guide
  super model install llama3.2:3b           # Install Ollama model (default)
  super model info llama3.2:3b               # Get model details
  super model backends                       # Check backend status
  super model dspy ollama/llama3.2:3b        # Create DSPy client

🔧 Supported Backends & Examples:

🦙 Ollama (Local Models - Default):
  • Install: super model install llama3.2:3b (auto-pulls with ollama)
  • Serve: ollama serve (runs on localhost:11434)
  • Use: super model dspy ollama/llama3.2:3b

🍎 MLX (Apple Silicon):
  • Install: super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
  • Serve: super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000
  • Use: super model dspy mlx-community/Llama-3.2-3B-Instruct-4bit

🤗 HuggingFace (Transformers):
  • Install: super model install -b huggingface microsoft/Phi-4
  • Serve: super model server huggingface microsoft/Phi-4 --port 8001
  • Use: super model dspy microsoft/Phi-4

🎮 LM Studio (Desktop App):
  • Install: Download via LM Studio app
  • Serve: Start server in LM Studio app (localhost:1234)
  • Use: super model dspy lmstudio/your-model-name

🎯 SuperOptiX Features:
  • Shows only installed models by default
  • Provides discovery guides for model sources
  • Seamless DSPy integration
  • SuperOptiX-branded model intelligence
        """,
    )
    model_subparsers = model_parser.add_subparsers(
        dest="model_command",
        help="SuperOptiX Model Intelligence commands",
        required=False,
    )
    model_parser.set_defaults(func=lambda args: model_parser.print_help())

    # super model list (installed models by default)
    list_models_parser = model_subparsers.add_parser(
        "list", aliases=["ls"], help="📋 List SuperOptiX models (installed by default)"
    )
    list_models_parser.add_argument(
        "--backend",
        choices=["ollama", "mlx", "huggingface", "lmstudio"],
        help="Filter by backend",
    )
    list_models_parser.add_argument(
        "--size", choices=["tiny", "small", "medium", "large"], help="Filter by size"
    )
    list_models_parser.add_argument(
        "--task",
        choices=["chat", "code", "reasoning", "embedding"],
        help="Filter by task",
    )
    list_models_parser.add_argument(
        "--installed-only",
        action="store_true",
        default=True,
        help="Show only installed models (default)",
    )
    list_models_parser.add_argument(
        "--all", action="store_true", help="Show all available models"
    )
    list_models_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed information"
    )
    list_models_parser.set_defaults(func=handle_model_list)

    # super model discover
    discover_parser = model_subparsers.add_parser(
        "discover", aliases=["disc"], help="🔍 SuperOptiX Model Discovery Guide"
    )
    discover_parser.set_defaults(func=handle_model_discover)

    # super model guide
    guide_parser = model_subparsers.add_parser(
        "guide", aliases=["g"], help="📚 SuperOptiX Model Installation Guide"
    )
    guide_parser.set_defaults(func=handle_model_guide)

    # super model install
    install_model_parser = model_subparsers.add_parser(
        "install",
        aliases=["i"],
        help="📥 Install a SuperOptiX model",
        description="""
📥 Install SuperOptiX models across different backends.

Examples:
  • Ollama: super model install llama3.2:3b (default backend)
  • MLX: super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
  • HuggingFace: super model install -b huggingface microsoft/Phi-4
  • LM Studio: super model install -b lmstudio your-model-name

Ollama models are automatically pulled using 'ollama pull'.
Other backends may require additional setup steps.
        """,
    )
    install_model_parser.add_argument("model_name", help="Model name to install")
    install_model_parser.add_argument(
        "--backend",
        "-b",
        choices=["ollama", "mlx", "huggingface", "lmstudio"],
        help="Specify backend",
    )

    install_model_parser.set_defaults(func=handle_model_install)

    # super model info
    model_info_parser = model_subparsers.add_parser(
        "info", aliases=["inf"], help="ℹ️ Get detailed SuperOptiX model information"
    )
    model_info_parser.add_argument("model_name", help="Model name to inspect")
    model_info_parser.set_defaults(func=handle_model_info)

    # super model backends
    backends_parser = model_subparsers.add_parser(
        "backends", aliases=["b"], help="🔧 Show SuperOptiX backend status"
    )
    backends_parser.set_defaults(func=handle_model_backends)

    # super model refresh
    refresh_parser = model_subparsers.add_parser(
        "refresh", aliases=["rf"], help="🔄 Refresh SuperOptiX model cache"
    )
    refresh_parser.set_defaults(func=handle_model_refresh)

    # super model remove
    remove_parser = model_subparsers.add_parser(
        "remove", aliases=["rm"], help="🗑️ Remove a SuperOptiX model"
    )
    remove_parser.add_argument("model_name", help="Model name to remove")
    remove_parser.add_argument(
        "--backend",
        "-b",
        choices=["ollama", "mlx", "huggingface", "lmstudio"],
        help="Specify backend to remove",
    )

    remove_parser.add_argument(
        "--all-backends",
        action="store_true",
        help="Remove the model from all backends",
    )
    remove_parser.set_defaults(func=handle_model_remove)

    # super model dspy (EXPERIMENTAL)
    dspy_parser = model_subparsers.add_parser(
        "dspy",
        aliases=["d"],
        help="🧠 Create DSPy client for SuperOptiX model (EXPERIMENTAL)",
        description="""
🧠 Create DSPy-compatible clients for SuperOptiX models. EXPERIMENTAL FEATURE.

Examples:
  • Ollama: super model dspy ollama/llama3.2:3b
  • MLX: super model dspy mlx-community/Llama-3.2-3B-Instruct-4bit
  • HuggingFace: super model dspy microsoft/Phi-4
  • LM Studio: super model dspy lmstudio/your-model-name

The client will be configured with the model's backend and settings.
        """,
    )
    dspy_parser.add_argument("model_name", help="Model name for DSPy client")
    dspy_parser.add_argument(
        "--temperature",
        "-t",
        type=float,
        default=0.7,
        help="Temperature for generation",
    )
    dspy_parser.add_argument(
        "--max-tokens", "-m", type=int, default=2048, help="Maximum tokens"
    )
    dspy_parser.set_defaults(func=handle_model_dspy)

    # super model server
    server_parser = model_subparsers.add_parser(
        "server",
        aliases=["srv"],
        help="🚀 Start local server for SuperOptiX models",
        description="""
🚀 Start local model servers for MLX, HuggingFace, or LM Studio.

Examples:
  super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit
  super model server huggingface microsoft/DialoGPT-small --port 8001
  super model server lmstudio llama-3.2-1b-instruct

Backends:
  mlx          Apple Silicon optimized (default: port 8000)
  huggingface  Transformers models (default: port 8001)
  lmstudio     Desktop app models (default: port 1234)

Note:
  Ollama servers use 'ollama serve' command separately.
        """,
    )
    server_parser.add_argument(
        "backend", choices=["mlx", "huggingface", "lmstudio"], help="Backend type"
    )
    server_parser.add_argument("model_name", help="Model name to start server for")
    server_parser.add_argument("--port", "-p", type=int, help="Port to run server on")
    server_parser.set_defaults(func=handle_model_server)

    # Observability commands
    observability_parser = subparsers.add_parser(
        "observe",
        aliases=["ob"],
        help="Manage observability features",
        formatter_class=RawDescriptionHelpFormatter,
    )
    observability_subparsers = observability_parser.add_subparsers(
        dest="observability_command", required=False
    )
    observability_parser.set_defaults(
        func=lambda args: observability_parser.print_help()
    )

    # super observability dashboard
    dashboard_parser = observability_subparsers.add_parser(
        "dashboard", aliases=["db"], help="Launch the observability dashboard"
    )
    dashboard_parser.add_argument("--agent-id", help="Agent ID to monitor (optional)")
    dashboard_parser.add_argument(
        "--port", type=int, default=8501, help="Dashboard port (default: 8501)"
    )
    dashboard_parser.add_argument(
        "--host", default="localhost", help="Dashboard host (default: localhost)"
    )
    dashboard_parser.add_argument(
        "--auto-open", action="store_true", help="Auto-open browser"
    )
    dashboard_parser.set_defaults(func=dashboard)

    # super observability traces
    traces_parser = observability_subparsers.add_parser(
        "traces", aliases=["tr"], help="View traces for a specific agent"
    )
    traces_parser.add_argument("agent_id", help="The agent ID to view traces for")
    traces_parser.add_argument("--component", help="Filter by component")
    traces_parser.add_argument("--status", help="Filter by status")
    traces_parser.add_argument(
        "--limit", type=int, default=100, help="Limit number of traces (default: 100)"
    )
    traces_parser.add_argument(
        "--export", choices=["json", "csv"], help="Export format"
    )
    traces_parser.add_argument("--output", help="Output file path")
    traces_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed trace analysis"
    )
    traces_parser.add_argument(
        "--show-tools", action="store_true", help="Show tool execution details"
    )
    traces_parser.add_argument(
        "--show-llm", action="store_true", help="Show LLM call details"
    )
    traces_parser.set_defaults(func=traces)

    # super observability check
    check_parser = observability_subparsers.add_parser(
        "check", aliases=["ch"], help="Check pipeline tracing configuration"
    )
    check_parser.add_argument("--agent-id", help="Agent ID to test (optional)")
    check_parser.add_argument(
        "--run-test", action="store_true", help="Run a test agent execution"
    )
    check_parser.add_argument(
        "--check-dspy", action="store_true", help="Check DSPy configuration"
    )
    check_parser.set_defaults(func=check_traces)

    # super observability analyze
    analyze_parser = observability_subparsers.add_parser(
        "analyze", aliases=["an"], help="Analyze agent performance"
    )
    analyze_parser.add_argument("agent_id", help="The agent ID to analyze")
    analyze_parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    analyze_parser.set_defaults(func=analyze)

    # super observability list
    list_agents_parser = observability_subparsers.add_parser(
        "list", aliases=["ls"], help="List all agents with trace files"
    )
    list_agents_parser.set_defaults(func=list_agents_with_traces)

    # super observability debug
    debugger_parser = observability_subparsers.add_parser(
        "debug", help="Debug an agent or orchestra"
    )
    debugger_subparsers = debugger_parser.add_subparsers(
        dest="debugger_command", help="Debugger commands", required=True
    )

    # super debug agent
    debug_agent_parser = debugger_subparsers.add_parser("agent", help="Debug an agent")
    debug_agent_parser.add_argument("agent_id", help="Agent ID to debug")
    debug_agent_parser.add_argument(
        "--enable-step-mode", action="store_true", help="Enable step-by-step debugging"
    )
    debug_agent_parser.add_argument(
        "--break-on-error", action="store_true", help="Break on error"
    )
    debug_agent_parser.add_argument(
        "--break-on-memory", action="store_true", help="Break on memory operations"
    )
    debug_agent_parser.set_defaults(func=debug)

    run_parser = model_subparsers.add_parser(
        "run", help="🚀 Run a prompt against a SuperOptiX model"
    )
    run_parser.add_argument("model_name", help="Model name to run")
    run_parser.add_argument("prompt", help="Prompt to send to the model")
    run_parser.add_argument(
        "--backend",
        "-b",
        choices=["ollama", "mlx", "huggingface"],
        help="Specify backend to use",
    )
    run_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    run_parser.add_argument(
        "--max-tokens",
        "-m",
        type=int,
        default=2048,
        help="Maximum tokens to generate",
    )
    run_parser.add_argument(
        "--temperature",
        "-t",
        type=float,
        default=0.7,
        help="Temperature for generation (0.0-2.0)",
    )
    run_parser.set_defaults(func=handle_model_run)

    # super model convert (EXPERIMENTAL - Hidden from help)
    convert_parser = model_subparsers.add_parser(
        "convert",
        aliases=["c"],
        help="EXPERIMENTAL: WIP - NOT READY YET",
        description="EXPERIMENTAL: WIP - NOT READY YET",
    )
    convert_parser.add_argument("hf_model", help="HuggingFace model to convert")
    convert_parser.add_argument(
        "--output",
        "-o",
        help="Output path for converted model (default: model name)",
    )
    convert_parser.add_argument(
        "--quantize",
        "-q",
        action="store_true",
        help="Generate a quantized model",
    )
    convert_parser.add_argument(
        "--bits",
        type=int,
        default=4,
        help="Bits per weight for quantization (default: 4)",
    )
    convert_parser.add_argument(
        "--group-size",
        type=int,
        default=64,
        help="Group size for quantization (default: 64)",
    )
    convert_parser.add_argument(
        "--quant-recipe",
        choices=["mixed_2_6", "mixed_3_4", "mixed_3_6", "mixed_4_6"],
        help="Mixed quantization recipe",
    )
    convert_parser.add_argument(
        "--dtype",
        choices=["float16", "bfloat16", "float32"],
        help="Data type for conversion",
    )
    convert_parser.add_argument(
        "--upload",
        help="HuggingFace repo to upload converted model to",
    )
    convert_parser.add_argument(
        "--dequantize",
        action="store_true",
        help="Dequantize a quantized model",
    )
    convert_parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Trust remote code from HuggingFace",
    )
    convert_parser.set_defaults(func=handle_model_convert)

    # super model quantize (EXPERIMENTAL - Hidden from help)
    quantize_parser = model_subparsers.add_parser(
        "quantize",
        aliases=["q"],
        help="EXPERIMENTAL: WIP - NOT READY YET",
        description="EXPERIMENTAL: WIP - NOT READY YET",
    )
    quantize_parser.add_argument("model_name", help="MLX model to quantize")
    quantize_parser.add_argument(
        "--output",
        "-o",
        help="Output path for quantized model",
    )
    quantize_parser.add_argument(
        "--bits",
        type=int,
        default=4,
        help="Bits per weight for quantization (default: 4)",
    )
    quantize_parser.add_argument(
        "--group-size",
        type=int,
        default=64,
        help="Group size for quantization (default: 64)",
    )
    quantize_parser.add_argument(
        "--recipe",
        choices=["mixed_2_6", "mixed_3_4", "mixed_3_6", "mixed_4_6"],
        help="Mixed quantization recipe",
    )
    quantize_parser.add_argument(
        "--dequantize",
        action="store_true",
        help="Dequantize instead of quantize",
    )
    quantize_parser.set_defaults(func=handle_model_quantize)

    args = parser.parse_args()

    # Handle version flag first
    if args.version:
        show_version_screen(args)
        return

    # Only these commands require project context
    commands_requiring_project = [
        "agent",
        "ag",
        "spec",
        "orchestra",
        "orch",
        "observe",
        "ob",
    ]
    if (
        hasattr(args, "command")
        and args.command
        and args.command in commands_requiring_project
    ):
        from superoptix.cli.utils import validate_superoptix_project

        validate_superoptix_project()

    # Execute the function associated with the command with loader
    if hasattr(args, "func"):
        # For the welcome screen (no command), don't show loader
        if args.func == show_welcome_screen:
            args.func(args)
        # For version command, run directly without loader
        elif args.func == show_version_screen:
            args.func(args)
        # For model commands, use enhanced progress handling
        elif hasattr(args, "command") and args.command == "model":
            execute_with_loader(args.func, args)
        else:
            # Show loader for all other commands
            execute_with_loader(args.func, args)
    else:
        # If no function is set, default to showing help with loader
        execute_with_loader(lambda x: parser.print_help(), args)


if __name__ == "__main__":
    main()
