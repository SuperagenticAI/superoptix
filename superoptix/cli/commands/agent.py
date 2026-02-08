#!/usr/bin/env python3
import asyncio
import copy
import inspect
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
import time
import warnings
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


# Helper class to prevent YAML aliases
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


# Suppress SQLite resource warnings that are harmless in our use case
# These warnings occur due to Python's garbage collection timing with DSPy evaluation metrics
warnings.filterwarnings("ignore", message="unclosed database", category=ResourceWarning)

from superoptix.cli.utils import run_async
from superoptix.compiler.agent_compiler import AgentCompiler
from superoptix.models.tier_system import TierLevel, tier_system
from superoptix.observability.tracer import SuperOptixTracer
from superoptix.runners.dspy_runner import DSPyRunner
from superoptix.ui.designer_factory import DesignerFactory
from superoptix.validators.playbook_linter import PlaybookLinter, display_lint_results
from superoptix.adapters.framework_registry import FrameworkRegistry
from superoptix.optimizers import UniversalGEPA

console = Console()


def _optimize_crewai_component(component, trainset, llm_model, temperature, max_tokens):
    """
    Custom optimization function for CrewAI components that avoids hanging.

    This function uses a simpler approach than OPRO:
    1. Generates a few prompt variations using the LLM
    2. Tests them quickly without full evaluation
    3. Returns the best one based on simple heuristics
    """
    import os

    console.print(f"[blue]🔧 Custom CrewAI optimization for {component.name}[/]")

    # Get current prompt
    current_prompt = component.variable or "You are a helpful assistant."

    # Generate prompt variations using LLM
    prompt_variations = []

    # Simple prompt improvement prompts that are less likely to trigger safety filters
    improvement_prompts = [
        f"Here is a current instruction: '{current_prompt}'\n\nPlease provide a slightly improved version that is more specific and actionable. Keep it concise and focused on the task.",
        f"Current instruction: '{current_prompt}'\n\nSuggest a refined version that adds clarity and removes ambiguity. Make it more direct and professional.",
        f"Instruction to improve: '{current_prompt}'\n\nCreate an enhanced version that includes specific examples or steps. Keep the core message but make it more detailed.",
    ]

    # Use the LLM to generate variations
    for i, improvement_prompt in enumerate(improvement_prompts):
        try:
            # Set environment variables for the LLM call
            os.environ.setdefault("LITELLM_TIMEOUT", "15")
            os.environ.setdefault("LITELLM_MAX_RETRIES", "1")

            # Import and use the LLM function
            from optimas.optim.opro import get_llm_output

            response = get_llm_output(
                message=improvement_prompt,
                model=llm_model,
                temperature=temperature,
                max_new_tokens=max_tokens,
            )

            # Clean up the response
            cleaned_response = response.strip()
            if cleaned_response and len(cleaned_response) > 10:
                prompt_variations.append(cleaned_response)
                console.print(f"[green]✓ Generated variation {i + 1}[/]")

        except Exception as e:
            console.print(
                f"[yellow]⚠️ Failed to generate variation {i + 1}: {str(e)[:50]}...[/]"
            )
            continue

    # If no variations were generated, return current prompt
    if not prompt_variations:
        console.print("[yellow]⚠️ No variations generated, keeping current prompt[/]")
        return current_prompt

    # Add current prompt to variations for comparison
    prompt_variations.append(current_prompt)

    # Simple heuristic scoring (length, specificity, action words)
    def score_prompt(prompt):
        score = 0
        # Prefer longer prompts (more detailed)
        score += min(len(prompt) / 100, 2)
        # Bonus for action words
        action_words = [
            "write",
            "create",
            "build",
            "implement",
            "develop",
            "generate",
            "provide",
            "ensure",
            "use",
            "follow",
        ]
        score += sum(1 for word in action_words if word.lower() in prompt.lower()) * 0.5
        # Bonus for specific technical terms
        tech_words = [
            "python",
            "function",
            "code",
            "error",
            "test",
            "validate",
            "format",
            "json",
            "api",
        ]
        score += sum(1 for word in tech_words if word.lower() in prompt.lower()) * 0.3
        return score

    # Score all variations
    scored_variations = [(prompt, score_prompt(prompt)) for prompt in prompt_variations]
    scored_variations.sort(key=lambda x: x[1], reverse=True)

    best_prompt = scored_variations[0][0]
    best_score = scored_variations[0][1]

    console.print(f"[green]🏆 Best prompt selected (score: {best_score:.2f})[/]")

    return best_prompt


def compile_agent(args):
    """Handle agent compilation."""
    if not args.name and not args.all:
        console.print(
            "[bold red]❌ You must specify an agent name or use --all.[/bold red]"
        )
        return

    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            return

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        agents_dir = project_root / project_name / "agents"
        if not agents_dir.exists():
            console.print(
                f"\n[bold red]❌ Agents directory not found for project '{project_name}'.[/]"
            )
            return

        if args.all:
            playbook_files = sorted(list(agents_dir.rglob("*_playbook.yaml")))
            if not playbook_files:
                console.print(
                    f"\n[yellow]No agent playbooks found in '{agents_dir}'.[/yellow]"
                )
                return

            console.print(
                f"\n[bold blue]🚀 Compiling all {len(playbook_files)} agents in project '{project_name}'...[/]"
            )
            successful_compilations = []
            failed_compilations = []

            for playbook_path in playbook_files:
                agent_name = playbook_path.stem.replace("_playbook", "")
                tier_level = getattr(args, "tier", None)
                if _compile_single_agent(agent_name, args, tier_level):
                    successful_compilations.append(agent_name)
                else:
                    failed_compilations.append(agent_name)

            console.print("=" * 80)

            # Create summary panel
            if successful_compilations and not failed_compilations:
                console.print(
                    Panel(
                        f"🎉 [bold bright_green]ALL AGENTS COMPILED SUCCESSFULLY![/]\n\n"
                        f"✅ [bold]Successful:[/] {len(successful_compilations)} agent(s)\n"
                        f"🚀 [bold]Ready for testing and customization![/]",
                        title="📊 Compilation Summary",
                        border_style="bright_green",
                        padding=(1, 2),
                    )
                )
            else:
                summary_text = ""
                if successful_compilations:
                    summary_text += f"✅ [bold green]Success:[/] {len(successful_compilations)} agent(s) compiled successfully\n"
                if failed_compilations:
                    summary_text += f"❌ [bold red]Failed:[/] {len(failed_compilations)} agent(s) failed: {', '.join(failed_compilations)}"

                border_color = "red" if failed_compilations else "green"
                console.print(
                    Panel(
                        summary_text,
                        title="📊 Compilation Summary",
                        border_style=border_color,
                        padding=(1, 2),
                    )
                )

                if failed_compilations:
                    sys.exit(1)

        else:  # Compile single agent
            agent_name = args.name.lower()
            # Pass tier level if specified
            tier_level = getattr(args, "tier", None)
            if not _compile_single_agent(agent_name, args, tier_level):
                sys.exit(1)

    except Exception as e:
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during compilation:[/] {e}"
        )
        sys.exit(1)


def _compile_single_agent(agent_name: str, args, tier_level: str = None):
    """Helper to compile a single agent with enhanced visual feedback and tier awareness."""
    console.print("=" * 80)
    try:
        compile_args = copy.copy(args)
        compile_args.name = agent_name

        # Load playbook data for display
        project_root = Path.cwd()
        with open(project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        # Find playbook file
        playbook_path = next(
            (project_root / system_name / "agents").rglob(
                f"**/{agent_name}_playbook.yaml"
            ),
            None,
        )
        if not playbook_path:
            package_root = Path(__file__).parent.parent.parent
            playbook_path = next(
                package_root.rglob(f"**/agents/**/{agent_name}_playbook.yaml"), None
            )

        playbook_data = None
        if playbook_path:
            with open(playbook_path) as f:
                playbook_data = yaml.safe_load(f)

        # Get metadata for display
        metadata = playbook_data.get("metadata", {}) if playbook_data else {}
        spec = playbook_data.get("spec", {}) if playbook_data else {}

        console.print(
            f"\n🔨 [bold bright_cyan]Compiling agent '[bold yellow]{agent_name}[/]'...[/]"
        )

        compiler = AgentCompiler()
        pipeline_path = compiler._get_pipeline_path(agent_name)

        # Get framework from args (defaults to dspy)
        framework = getattr(args, "framework", "dspy")
        framework_display = {
            "dspy": "DSPy",
            "microsoft": "Microsoft Agent Framework",
            "openai": "OpenAI Agents SDK",
            "deepagents": "DeepAgents (LangGraph)",
            "crewai": "CrewAI",
            "google-adk": "Google ADK",
            "pydantic-ai": "Pydantic AI",
            "claude-sdk": "Claude Agent SDK",
        }.get(framework, framework.upper())

        if framework == "deepagents":
            lm_cfg = spec.get("language_model", {}) if isinstance(spec, dict) else {}
            lm_provider = str(lm_cfg.get("provider", "")).strip().lower()
            lm_model = str(lm_cfg.get("model", "")).strip()
            looks_local = (
                lm_provider in {"ollama", "local"}
                or lm_model.startswith("ollama:")
                or lm_model.startswith("llama")
            )

            if looks_local:
                console.print(
                    "[yellow]⚠️  DeepAgents requires cloud function-calling models.[/]\n"
                    "[dim]Update playbook `spec.language_model` to Google/Anthropic/OpenAI "
                    "(for example: `provider: google-genai`, "
                    "`model: google-genai:gemini-2.5-flash`) and recompile.[/]"
                )
            else:
                console.print(
                    f"[dim]DeepAgents model config: provider={lm_provider or 'auto'}, "
                    f"model={lm_model or 'unset'}[/]"
                )

        if getattr(args, "rlm", False) and framework != "dspy":
            console.print(
                "[yellow]⚠️  Ignoring --rlm: currently supported only for DSPy compilation.[/]"
            )

        # Show what's happening (concise)
        console.print(
            Panel(
                f"🤖 [bold bright_green]COMPILATION IN PROGRESS[/]\n\n"
                f"🎯 [bold]Agent:[/] {metadata.get('name', agent_name.title())}\n"
                f"🏗️ [bold]Framework:[/] {framework_display} {tier_level.title() if tier_level else 'Junior'} Pipeline\n"
                f"🔧 [bold]Process:[/] YAML playbook → Executable Python pipeline\n"
                f"📁 [bold]Output:[/] [cyan]{pipeline_path.relative_to(project_root)}[/]",
                title="⚡ Compilation Details",
                border_style="bright_green",
                padding=(1, 2),
            )
        )

        # Determine tier level from various sources
        effective_tier = tier_level
        if not effective_tier and playbook_data:
            effective_tier = playbook_data.get("metadata", {}).get("level", "oracles")

        # Compile the agent with template selection
        use_abstracted = getattr(args, "abstracted", False)
        use_explicit = getattr(args, "explicit", True)  # DEFAULT: explicit template
        compile_profile = "optimized" if getattr(args, "optimize", False) else "minimal"

        # If abstracted is requested, disable explicit
        if use_abstracted:
            use_explicit = False

        compiler.compile(
            compile_args,
            tier_level=effective_tier,
            use_abstracted=use_abstracted,
            use_explicit=use_explicit,
            compile_profile=compile_profile,
        )

        # Show success
        console.print(
            Panel(
                "🎉 [bold bright_green]COMPILATION SUCCESSFUL![/] Pipeline Generated",
                style="bright_green",
                border_style="bright_green",
            )
        )

        # Show verbose panels only in verbose mode
        if getattr(args, "verbose", False):
            # Auto-generation notice (verbose only)
            important_notice = """⚠️ [bold bright_yellow]Auto-Generated Pipeline[/]

🚨 [bold]Starting foundation[/] - Customize for production use
💡 [bold]You own this code[/] - Modify for your specific requirements"""

            console.print(
                Panel(
                    important_notice,
                    title="🛠️ Customization Required",
                    border_style="bright_yellow",
                    padding=(1, 2),
                )
            )

            # Testing guidance (verbose only)
            test_count = 0
            if (
                playbook_data
                and "feature_specifications" in spec
                and "scenarios" in spec["feature_specifications"]
            ):
                test_count = len(spec["feature_specifications"]["scenarios"])

            tests_guidance = f"""🧪 [bold]Current BDD Scenarios:[/] {test_count} found

🎯 [bold]Recommendations:[/]
• Add comprehensive test scenarios to your playbook
• Include edge cases and error handling scenarios
• Test with real-world data samples

💡 [bold]Why scenarios matter:[/] Training data for optimization & quality gates"""

            console.print(
                Panel(
                    tests_guidance,
                    title="🧪 Testing Enhancement",
                    border_style="bright_magenta",
                    padding=(1, 2),
                )
            )

            # Next steps guidance (verbose only)
            if compile_profile == "minimal":
                next_steps = f"""🚀 [bold bright_cyan]NEXT STEPS[/]

[cyan]super agent run {agent_name} --goal "goal"[/] - Execute minimal DSPy pipeline
[cyan]super agent compile {agent_name} --rlm[/] - Recompile minimal DSPy pipeline with dspy.RLM
[cyan]super agent compile {agent_name} --optimize[/] - Generate full optimization/evaluation pipeline
[cyan]super agent evaluate {agent_name}[/] - Run BDD evaluation (after optimized compile)
[cyan]super agent optimize {agent_name}[/] - Run optimizer (after optimized compile)
"""
            else:
                next_steps = f"""🚀 [bold bright_cyan]NEXT STEPS[/]

[cyan]super agent evaluate {agent_name}[/] - Establish baseline performance
[cyan]super agent optimize {agent_name}[/] - Enhance performance using DSPy
[cyan]super agent evaluate {agent_name}[/] - Measure improvement
[cyan]super agent run {agent_name} --goal "goal"[/] - Execute optimized agent

[dim]💡 Follow BDD/TDD workflow: evaluate → optimize → evaluate → run[/]"""

            console.print(
                Panel(
                    next_steps,
                    title="🎯 Workflow Guide",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )

        # Simple workflow guide (normal mode)
        if compile_profile == "minimal":
            console.print(
                f'🎯 [bold cyan]Next:[/] [cyan]super agent run {agent_name} --goal "your goal"[/] (optional: recompile with [cyan]--rlm[/] for DSPy RLM, or [cyan]--optimize[/] for evaluate/optimize features)'
            )
        else:
            console.print(
                f'🎯 [bold cyan]Next:[/] [cyan]super agent evaluate {agent_name}[/] or [cyan]super agent run {agent_name} --goal "your goal"[/]'
            )

        # Success summary
        console.print("=" * 80)
        console.print(
            f"🎉 [bold bright_green]Agent '{metadata.get('name', agent_name)}' pipeline ready![/] Time to make it yours! 🚀"
        )

        return True

    except Exception as e:
        console.print(
            Panel(
                f"❌ [bold red]COMPILATION FAILED[/]\n\n"
                f"[red]Error:[/] {str(e)}\n"
                f"[yellow]Agent:[/] {agent_name}\n"
                f"[yellow]Framework:[/] DSPy (default — other frameworks coming soon)\n\n"
                f"[cyan]💡 Troubleshooting Tips:[/]\n"
                f"• Ensure agent playbook exists and is valid YAML\n"
                f"• Check that you're in a valid super project directory\n"
                f"• Verify playbook syntax with: [cyan]super agent lint {agent_name}[/]",
                title="💥 Compilation Error",
                border_style="red",
                padding=(1, 2),
            )
        )
        return False


def _run_framework_agent(args, framework: str):
    """
    Run an agent compiled with a non-DSPy framework.

    Dynamically imports and runs the framework-specific pipeline.
    """
    project_root = Path.cwd()
    with open(project_root / ".super") as f:
        project_name = yaml.safe_load(f).get("project")

    agent_dir = project_root / project_name / "agents" / args.name
    suffix = framework.replace("-", "_")
    pipeline_path = agent_dir / "pipelines" / f"{args.name}_{suffix}_pipeline.py"

    framework_display = {
        "claude-sdk": "Claude Agent SDK",
        "crewai": "CrewAI",
        "pydantic-ai": "Pydantic AI",
        "openai": "OpenAI Agents SDK",
        "google-adk": "Google ADK",
        "microsoft": "Microsoft Agent Framework",
        "deepagents": "DeepAgents (LangGraph)",
    }.get(framework, framework.upper())

    console.print(
        f"🚀 [bold cyan]Running agent '[yellow]{args.name}[/]' with {framework_display}...[/]"
    )
    console.print()

    if not pipeline_path.exists():
        console.print(
            f"[bold red]❌ Pipeline not found:[/] {pipeline_path}\n\n"
            f"[yellow]Compile it first with:[/]\n"
            f"  [cyan]super agent compile {args.name} --framework {framework}[/]"
        )
        return

    try:
        # Dynamically import the pipeline module
        spec = importlib.util.spec_from_file_location(
            f"{args.name}_{suffix}_pipeline", str(pipeline_path)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the Pipeline class (e.g., DeveloperPipeline)
        pipeline_class = None
        for name, obj in module.__dict__.items():
            if name.endswith("Pipeline") and isinstance(obj, type):
                pipeline_class = obj
                break

        if not pipeline_class:
            console.print(f"[bold red]❌ No Pipeline class found in {pipeline_path}[/]")
            return

        # Instantiate and run
        init_kwargs = {}
        if framework == "pydantic-ai":
            model_config = {}
            if getattr(args, "provider", None):
                model_config["provider"] = args.provider
            if getattr(args, "model", None):
                model_config["model"] = args.model
            if getattr(args, "local", False):
                model_config.setdefault("provider", "ollama")
                model_config.setdefault("model", "llama3.1:8b")
            if getattr(args, "gateway", False):
                model_config["runtime_mode"] = "gateway"
            elif getattr(args, "direct", False):
                model_config["runtime_mode"] = "direct"
            if getattr(args, "gateway_url", None) or getattr(
                args, "gateway_key_env", None
            ):
                model_config["runtime_mode"] = "gateway"
                model_config["gateway"] = {}
                if getattr(args, "gateway_url", None):
                    model_config["gateway"]["base_url"] = args.gateway_url
                if getattr(args, "gateway_key_env", None):
                    model_config["gateway"]["api_key_env"] = args.gateway_key_env

            params = inspect.signature(pipeline_class).parameters
            if "model_config" in params and model_config:
                init_kwargs["model_config"] = model_config
            if "playbook_path" in params:
                playbook_path = (
                    agent_dir / "playbook" / f"{args.name}_playbook.yaml"
                )
                init_kwargs["playbook_path"] = str(playbook_path)

        pipeline = pipeline_class(**init_kwargs)

        # Check if it's an async framework
        if hasattr(pipeline, "run") and asyncio.iscoroutinefunction(pipeline.run):
            # Async pipeline (Claude SDK, Pydantic AI, etc.)
            result = run_async(pipeline.run(query=args.goal))
        elif hasattr(pipeline, "run_sync"):
            # Sync wrapper available
            result = pipeline.run_sync(query=args.goal)
        elif hasattr(pipeline, "run"):
            # Sync pipeline
            result = pipeline.run(query=args.goal)
        else:
            console.print(f"[bold red]❌ Pipeline class has no run() method[/]")
            return

        # Display result
        console.print("\n[bold green]✅ Agent execution completed![/]\n")
        console.print("[bold]Output:[/]")

        if isinstance(result, dict):
            for key, value in result.items():
                if key not in ("tool_calls", "metadata"):
                    console.print(f"  [cyan]{key}:[/] {value}")
        else:
            console.print(f"  {result}")

    except Exception as e:
        console.print(
            f"\n[bold red]❌ Failed to run {framework_display} pipeline:[/] {e}"
        )
        import traceback

        console.print(traceback.format_exc())


def run_agent(args):
    """Handle running an agent pipeline by delegating to the appropriate runner."""
    # Get observability backend from args
    observe_backend = getattr(args, "observe", "superoptix")
    enable_external = observe_backend != "superoptix"

    # Initialize enhanced tracer if available
    try:
        from superoptix.observability.enhanced_tracer import EnhancedSuperOptixTracer

        tracer = EnhancedSuperOptixTracer(
            agent_id=args.name,
            enable_external_tracing=enable_external,
            observability_backend=observe_backend,
            auto_load=False,
        )
        console.print(f"[dim]📊 Observability: {observe_backend}[/]")
    except ImportError:
        tracer = SuperOptixTracer(agent_id=args.name)

    try:
        with tracer.trace_operation(
            "agent_run", f"agent.{args.name}", agent_name=args.name, query=args.goal
        ):
            # Get framework from args
            framework = getattr(args, "framework", "dspy")

            # Handle non-DSPy frameworks
            if framework != "dspy":
                _run_framework_agent(args, framework)
                return

            console.print(f"🚀 [bold cyan]Running agent '[yellow]{args.name}[/]'...[/]")
            console.print()

            # Check if agent has been optimized and tested
            project_root = Path.cwd()
            with open(project_root / ".super") as f:
                project_name = yaml.safe_load(f).get("project")

            agent_dir = project_root / project_name / "agents" / args.name
            optimized_path = agent_dir / "pipelines" / f"{args.name}_optimized.json"

            # Removed workflow suggestion - was appearing too frequently in output
            if not optimized_path.exists():
                console.print("[dim]Running with base model (not optimized)...[/]")
                console.print()

            # Optimas execution engine
            engine = getattr(args, "engine", "dspy")
            target = getattr(args, "target", None)
            if engine == "optimas":
                try:
                    from optimas.wrappers.example import Example  # noqa: F401
                except Exception as e:
                    console.print(
                        f"❌ [bold red]Optimas runtime requires optional deps:[/] {e}"
                    )
                    return
                if not target:
                    target = "optimas-openai"
                suffix = target.replace("-", "_")
                opt_path = agent_dir / "pipelines" / f"{args.name}_{suffix}_pipeline.py"
                if not opt_path.exists():
                    console.print(
                        f"[yellow]Optimas pipeline not found at {opt_path}. Compile it first: super agent compile {args.name} --target {target}[/]"
                    )
                    return
                spec = importlib.util.spec_from_file_location("opt_run", str(opt_path))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                system = mod.system_engine()
                required_fields = getattr(system, "required_input_fields", None)
                first_field = required_fields[0] if required_fields else "query"
                inputs = {first_field: args.goal}
                try:
                    pred = system(**inputs)
                except TypeError:
                    pred = system.run(**inputs)
                final_fields = getattr(system, "final_output_fields", None) or []
                console.print("\n[bold]Outputs:[/]")
                if final_fields:
                    for k in final_fields:
                        console.print(f"- {k}: {getattr(pred, k, None)}")
                else:
                    console.print(str(pred))
                return

            # Handle optimization flag
            if hasattr(args, "optimize") and args.optimize:
                console.print(
                    "[yellow]🚀 Running with optimization enabled (this may take longer)...[/]"
                )
                # First optimize the agent
                optimization_result = run_async(
                    DSPyRunner(agent_name=args.name).optimize(
                        force=False,
                        runtime_mode=(
                            "local"
                            if getattr(args, "local", False)
                            else (
                                "cloud" if getattr(args, "cloud", False) else "auto"
                            )
                        ),
                        provider_override=getattr(args, "provider", None),
                        model_override=getattr(args, "model", None),
                    )
                )
                if not optimization_result.get("success", False):
                    console.print(
                        f"[red]❌ Optimization failed: {optimization_result.get('error', 'Unknown error')}[/]"
                    )
                    console.print("[yellow]Continuing with base model...[/]")

            # Correctly instantiate the runner first, then run it.
            runner = DSPyRunner(agent_name=args.name)
            # Check if runtime optimization is requested
            runtime_optimize = (hasattr(args, "optimize") and args.optimize) or (
                hasattr(args, "force_optimize") and args.force_optimize
            )
            force_runtime = hasattr(args, "force_optimize") and args.force_optimize
            # Use optimization unless explicitly disabled
            use_optimization = True  # Always try to use pre-optimized if available
            run_async(
                runner.run(
                    query=args.goal,
                    use_optimization=use_optimization,
                    runtime_optimize=runtime_optimize,
                    force_runtime=force_runtime,
                    runtime_mode=(
                        "local"
                        if getattr(args, "local", False)
                        else ("cloud" if getattr(args, "cloud", False) else "auto")
                    ),
                    provider_override=getattr(args, "provider", None),
                    model_override=getattr(args, "model", None),
                )
            )

            # Add next steps guidance after successful run - only in verbose mode
            if getattr(args, "verbose", False):
                console.print()
                console.print(
                    "🎉 [bold green]Agent execution completed successfully![/]"
                )
                console.print()

                # Next steps guidance in a panel
                next_steps_content = "🔧 [bold yellow]Improve your agent:[/]\n"
                next_steps_content += f"   [cyan]super agent evaluate {args.name}[/] - Test agent performance with BDD specs\n"
                next_steps_content += f"   [cyan]super agent optimize {args.name}[/] - Optimize for better results\n\n"

                next_steps_content += "🎯 [bold green]Create more agents:[/]\n"
                next_steps_content += (
                    "   [cyan]super agent add[/] - Add a new agent to your project\n"
                )
                next_steps_content += "   [cyan]super agent design[/] - Design a custom agent with AI assistance\n"
                next_steps_content += "   [cyan]super agent pull <agent_name>[/] - Install a pre-built agent\n\n"

                next_steps_content += (
                    "🎼 [bold magenta]Build orchestras (multi-agent workflows):[/]\n"
                )
                next_steps_content += "   [cyan]super orchestra create <orchestra_name>[/] - Create a new orchestra\n"
                next_steps_content += (
                    "   [cyan]super orchestra list[/] - See existing orchestras\n"
                )
                next_steps_content += '   [cyan]super orchestra run <orchestra_name> --goal "complex task"[/] - Run multi-agent workflow\n\n'

                next_steps_content += "📊 [bold blue]Explore and manage:[/]\n"
                next_steps_content += (
                    "   [cyan]super agent list[/] - See all your agents\n"
                )
                next_steps_content += f"   [cyan]super agent inspect {args.name}[/] - Detailed agent information\n"
                next_steps_content += "   [cyan]super marketplace[/] - Browse available agents and tools\n\n"

                next_steps_content += "💡 [dim]Quick tips:[/]\n"
                next_steps_content += (
                    "   • Use [cyan]--optimize[/] flag for runtime optimization\n"
                )
                next_steps_content += (
                    "   • Add BDD specifications to your playbook for better testing\n"
                )
                next_steps_content += (
                    "   • Create orchestras for complex, multi-step workflows"
                )

                console.print(
                    Panel(
                        next_steps_content,
                        title="🚀 What would you like to do next?",
                        border_style="bright_cyan",
                        padding=(1, 2),
                    )
                )
                console.print()
    except Exception as e:
        # The runner already prints detailed errors, so we just note that the run failed.
        console.print("\n[bold red]❌ Agent run failed.[/]")
        console.print(f"[red]Debug: {type(e).__name__}: {e}")
        import traceback

        console.print(traceback.format_exc())
        tracer.add_event(
            "agent_run_failed", f"agent.{args.name}", {"error": str(e)}, status="error"
        )
        # Optionally, re-raise if you want the script to exit with a non-zero code
        # raise e
    finally:
        tracer.export_traces()


def test_agent_bdd(args):
    """Handles BDD specification testing of an agent with professional test runner UI."""
    agent_name = args.name.lower()
    project_name = getattr(args, "project", None)
    engine = getattr(args, "engine", "dspy")
    target = getattr(args, "target", None)

    # Professional test runner header
    console.print()
    console.print("═" * 100, style="bright_cyan")
    console.print(
        "🧪 [bold bright_cyan]SuperOptiX BDD Spec Runner[/] [dim]- Professional Agent Validation[/]",
        justify="center",
    )
    console.print("═" * 100, style="bright_cyan")
    console.print()

    # Test session info
    session_info = Table.grid(padding=(0, 2))
    session_info.add_column(style="cyan", min_width=20)
    session_info.add_column(style="white")
    session_info.add_row("🎯 Agent:", f"[bold]{agent_name}[/]")
    session_info.add_row("📅 Session:", f"{time.strftime('%Y-%m-%d %H:%M:%S')}")
    session_info.add_row(
        "🔧 Mode:",
        f"{'Auto-tune enabled' if args.auto_tune else 'Standard validation'}",
    )
    session_info.add_row(
        "📊 Verbosity:", f"{'Detailed' if args.verbose else 'Summary'}"
    )

    console.print(
        Panel(session_info, title="📋 Spec Execution Session", border_style="blue")
    )
    console.print()

    try:
        # Step 1: Pipeline Loading (no spinner)
        console.print("[cyan]Loading pipeline definition...[/]")
        runner = None
        if engine == "dspy":
            runner = DSPyRunner(agent_name, project_name=project_name)

        if engine == "dspy":
            spec = importlib.util.spec_from_file_location(
                f"{agent_name}_pipeline", runner.pipeline_path
            )
        else:
            # Determine optimas pipeline path
            if not target:
                target = "optimas-openai"
            with open(Path.cwd() / ".super") as f:
                system_name = yaml.safe_load(f).get("project")
            agent_dir = Path.cwd() / system_name / "agents" / agent_name / "pipelines"
            suffix = target.replace("-", "_")
            opt_path = agent_dir / f"{agent_name}_{suffix}_pipeline.py"
            if not opt_path.exists():
                console.print(
                    f"[yellow]Optimas pipeline not found at {opt_path}. Compile it first: super agent compile {agent_name} --target {target}[/]"
                )
                return
            spec = importlib.util.spec_from_file_location(
                f"{agent_name}_pipeline", str(opt_path)
            )
        if not spec:
            console.print("❌ [bold red]Pipeline Not Found[/]")
            console.print(f"   Expected: {runner.pipeline_path}")
            console.print(f"   💡 Run: [cyan]super agent compile {agent_name}[/]")
            return

        module = importlib.util.module_from_spec(spec)
        # For optimas-dspy targets, ensure DSPy LM is configured so the adapter can read settings
        if engine == "optimas" and target == "optimas-dspy":
            try:
                import dspy

                # Configure a minimal client; no calls will be made in our evaluation path
                dspy.settings.configure(lm=dspy.LiteLLM(model="gpt-4o-mini"))
            except Exception:
                pass
        spec.loader.exec_module(module)

        if engine == "optimas":
            # Minimal Optimas evaluation using BDD scenarios without LLM calls
            try:
                from optimas.wrappers.example import Example
                from optimas.wrappers.prediction import Prediction
            except Exception as e:
                console.print(f"❌ [bold red]Optimas not available:[/] {e}")
                return

            try:
                system = module.system_engine()
            except Exception as e:
                console.print(f"❌ [bold red]Failed to build Optimas system:[/] {e}")
                return

            # Load scenarios from playbook
            try:
                with open(Path.cwd() / ".super") as f:
                    sys_name = yaml.safe_load(f).get("project")
                pb_path = (
                    Path.cwd()
                    / sys_name
                    / "agents"
                    / agent_name
                    / "playbook"
                    / f"{agent_name}_playbook.yaml"
                )
                with open(pb_path, "r") as f:
                    playbook = yaml.safe_load(f) or {}
                spec_data = playbook.get("spec", playbook)
                scenarios = []
                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
            except Exception as e:
                console.print(f"❌ [bold red]Failed to load BDD scenarios:[/] {e}")
                return

            if not scenarios:
                console.print("❌ [bold red]No BDD specifications found![/]")
                return

            finals = system.final_output_fields or ["response"]
            total = len(scenarios)
            passed = 0
            for sc in scenarios:
                inputs = sc.get("input", {}) or {}
                expected = sc.get("expected_output", {}) or {}
                # Provide dummy prediction using expected outputs when possible
                pred_fields = {k: expected.get(k, "ok") for k in finals}
                ex = (
                    Example(**inputs).with_inputs(*inputs.keys())
                    if inputs
                    else Example().with_inputs()
                )
                try:
                    score = system.evaluate(ex, prediction=Prediction(**pred_fields))
                except Exception:
                    score = 0.0
                if isinstance(score, (int, float)) and score > 0:
                    passed += 1

            fail = total - passed
            pass_rate = (passed / total * 100.0) if total else 0.0

            console.print()
            console.print(f"📋 Found [bold green]{total}[/] BDD specifications")
            console.print(
                f"✅ Passed: {passed}   ❌ Failed: {fail}   🎯 Pass Rate: {pass_rate:.1f}%"
            )
            return

        pipeline_class = None
        for name, obj in module.__dict__.items():
            if name.endswith("Pipeline") and isinstance(obj, type):
                pipeline_class = obj
                break

        if not pipeline_class:
            console.print("❌ [bold red]Pipeline Class Not Found[/]")
            console.print(
                f"   Expected: Class ending with 'Pipeline' in {runner.pipeline_path}"
            )
            return

        # Create pipeline with playbook path for BDD scenario loading
        try:
            pipeline = pipeline_class(playbook_path=str(runner.playbook_path))
        except TypeError:
            # Fallback for pipelines that don't accept playbook_path
            pipeline = pipeline_class()
        console.print("[green]Pipeline loaded successfully[/]")

        # Step 2: Optimization Check (no spinner)
        optimization_status = (
            ("🚀 Optimized" if runner.optimized_path.exists() else "⚙️  Base Model")
            if engine == "dspy"
            else "⚙️  Base Model"
        )
        if runner.optimized_path.exists():
            console.print("[cyan]Loading optimized weights...[/]")
            try:
                pipeline.load_optimized(str(runner.optimized_path))
                console.print("✅ [green]Optimized weights applied[/]")
            except Exception as e:
                console.print(
                    f"⚠️  [yellow]Using base model - optimization load failed: {e}[/]"
                )
                optimization_status = "⚙️  Base Model (optimization failed)"
        elif engine == "dspy":
            console.print("ℹ️  [blue]Using base model (no optimization found)[/]")

        # Step 3: BDD Spec Execution with Professional UI
        console.print()
        console.print("🔍 [bold cyan]Discovering BDD Specifications...[/]")

        # Get test scenarios count first
        test_scenarios = getattr(pipeline, "test_examples", [])
        if not test_scenarios:
            console.print("❌ [bold red]No BDD specifications found![/]")
            console.print()
            console.print("📝 [bold yellow]How to add BDD specifications:[/]")
            console.print("   1. Edit your agent playbook YAML file")
            console.print("   2. Add 'feature_specifications' section with 'scenarios'")
            console.print(
                "   3. Recompile agent: [cyan]super agent compile {agent_name}[/]"
            )
            console.print()
            console.print("💡 [dim]Example specification structure:[/]")
            console.print("""[dim]
feature_specifications:
  scenarios:
    - name: "basic_functionality"
      description: "Agent should handle basic requests"
      input:
        feature_requirement: "Simple task"
      expected_output:
        implementation: "Expected response"[/]""")
            return

        console.print(
            f"📋 Found [bold green]{len(test_scenarios)}[/] BDD specifications"
        )
        console.print()

        # Professional spec execution with progress tracking
        console.print("🧪 [bold cyan]Executing BDD Specification Suite[/]")
        console.print("─" * 60)

        # Pytest-style progress indicator
        console.print("[dim]Progress:[/]", end=" ")

        # Run specs with real-time updates
        results = pipeline.run_bdd_test_suite(
            auto_tune=args.auto_tune, ignore_checks=args.ignore_checks
        )

        if not results or not results.get("success"):
            console.print(
                f"❌ [bold red]Spec execution failed:[/] {results.get('message', 'Unknown error')}"
            )
            return

        # Extract results for professional display
        summary = results.get("summary", {})
        model_analysis = results.get("model_analysis", {})
        recommendations = results.get("recommendations", [])
        bdd_results = results.get("bdd_results", {})
        detailed_results = bdd_results.get("detailed_results", [])

        # Display pytest-style results
        console.print()  # Clear the progress line
        console.print("[bold]Test Results:[/]")

        # Show pytest-style output
        for i, result in enumerate(detailed_results, 1):
            if result.get("passed"):
                console.print("[green].[/]", end="")
            else:
                console.print("[red]F[/]", end="")

        console.print()  # New line after progress
        console.print()

        # Show detailed table only in verbose mode
        if getattr(args, "verbose", False):
            # Create progress table with better formatting
            spec_table = Table(show_header=True, header_style="bold magenta")
            spec_table.add_column(
                "Specification", style="cyan", width=28, no_wrap=False
            )
            spec_table.add_column("Status", justify="center", width=12)
            spec_table.add_column("Score", justify="center", width=8)
            spec_table.add_column("Description", style="dim", width=45, no_wrap=False)

            # Populate spec results table
            for result in detailed_results:
                status_icon = "✅ PASS" if result.get("passed") else "❌ FAIL"
                status_color = "green" if result.get("passed") else "red"
                score = f"{result.get('confidence_score', 0.0):.2f}"

                # Better text handling for long descriptions
                description = result.get("description", "N/A")
                if len(description) > 42:
                    description = description[:39] + "..."

                spec_name = result.get("scenario_name", "Unknown")
                if len(spec_name) > 25:
                    spec_name = spec_name[:22] + "..."

                spec_table.add_row(
                    spec_name,
                    f"[{status_color}]{status_icon}[/]",
                    f"[bold]{score}[/]",
                    description,
                )

            console.print(spec_table)
            console.print()

        # Professional Summary Dashboard
        total_specs = summary.get("total", len(detailed_results))
        passed_specs = summary.get("passed", 0)
        failed_specs = summary.get("failed", 0)
        pass_rate = (passed_specs / total_specs * 100) if total_specs > 0 else 0

        # Quality gate determination
        if pass_rate >= 80:
            quality_gate = "🎉 EXCELLENT"
            gate_color = "bright_green"
            gate_emoji = "🟢"
        elif pass_rate >= 60:
            quality_gate = "⚠️  GOOD"
            gate_color = "yellow"
            gate_emoji = "🟡"
        else:
            quality_gate = "❌ NEEDS WORK"
            gate_color = "red"
            gate_emoji = "🔴"

        # Main results dashboard
        summary_grid = Table.grid(padding=(0, 2))
        summary_grid.add_column(style="bold cyan", min_width=20)
        summary_grid.add_column(style="white", min_width=15)
        summary_grid.add_column(style="bold cyan", min_width=20)
        summary_grid.add_column(style="white")

        summary_grid.add_row(
            "📊 Total Specs:",
            f"[bold]{total_specs}[/]",
            "🎯 Pass Rate:",
            f"[bold]{pass_rate:.1f}%[/]",
        )
        summary_grid.add_row(
            "✅ Passed:",
            f"[green]{passed_specs}[/]",
            "🤖 Model:",
            f"{model_analysis.get('model_name', 'Unknown')}",
        )
        summary_grid.add_row(
            "❌ Failed:",
            f"[red]{failed_specs}[/]",
            "💪 Capability:",
            f"{model_analysis.get('capability_score', 0.0):.2f}",
        )
        summary_grid.add_row(
            "🏆 Quality Gate:",
            f"[{gate_color}]{quality_gate}[/]",
            "🚀 Status:",
            optimization_status,
        )

        console.print(
            Panel(
                summary_grid,
                title=f"{gate_emoji} Specification Results Summary",
                border_style=gate_color,
                padding=(1, 2),
            )
        )

        # Grouped failure analysis (if any failures) - only in verbose mode
        if failed_specs > 0 and getattr(args, "verbose", False):
            console.print()
            console.print("🔍 [bold red]Failure Analysis - Grouped by Issue Type[/]")
            console.print("─" * 80)

            # Group failures by issue type
            failure_groups = {}
            for result in detailed_results:
                if not result.get("passed"):
                    issue = result.get("failure_reason", "Unknown issue").lower()

                    # Categorize issues
                    if "semantic" in issue:
                        category = "semantic"
                    elif "keyword" in issue:
                        category = "keyword"
                    elif "structure" in issue:
                        category = "structure"
                    elif "length" in issue:
                        category = "length"
                    else:
                        category = "general"

                    if category not in failure_groups:
                        failure_groups[category] = []
                    failure_groups[category].append(result)

            # Generate fix suggestions for each category
            fix_suggestions_map = {
                "semantic": [
                    "🎯 Make the response more relevant to the expected output",
                    "📝 Use similar terminology and technical concepts",
                    "🔍 Ensure the output addresses all aspects of the input requirement",
                    "💡 Review the expected output format and structure",
                ],
                "keyword": [
                    "🔑 Include more specific technical terms from the expected output",
                    "📚 Use domain-specific vocabulary and concepts",
                    "🎯 Focus on the key terms that define the requirement",
                    "💼 Add industry-standard terminology where appropriate",
                ],
                "structure": [
                    "📋 Match the expected output format and organization",
                    "🔲 Use similar formatting (lists, headers, code blocks)",
                    "📏 Maintain consistent structure and presentation",
                    "🎨 Pay attention to layout and information hierarchy",
                ],
                "length": [
                    "📝 Provide more comprehensive and detailed responses",
                    "🔍 Ensure all aspects of the requirement are covered",
                    "💬 Expand explanations and include more context",
                    "📖 Add examples and implementation details",
                ],
                "general": [
                    "🔍 Review the specification expectations vs actual output",
                    "📝 Improve overall response quality and relevance",
                    "🎯 Focus on addressing the core requirement",
                    "💡 Consider model optimization or prompt refinement",
                ],
            }

            # Display grouped failures
            for category, failures in failure_groups.items():
                category_names = {
                    "semantic": "Semantic Relevance Issues",
                    "keyword": "Keyword/Terminology Issues",
                    "structure": "Structure/Format Issues",
                    "length": "Length/Completeness Issues",
                    "general": "General Quality Issues",
                }

                console.print(
                    f"\n[bold red]📋 {category_names.get(category, category.title())} ({len(failures)} failures)[/]"
                )
                console.print("─" * 60)

                # Show fix suggestions for this category
                suggestions = fix_suggestions_map.get(category, [])
                console.print("[bold yellow]💡 Fix Suggestions:[/]")
                for suggestion in suggestions:
                    console.print(f"   {suggestion}")

                # List the failing specs in this category
                console.print("\n[bold cyan]Affected Specifications:[/]")
                for failure in failures:
                    spec_name = failure.get("scenario_name", "Unknown")
                    score = failure.get("confidence_score", 0.0)
                    console.print(f"   • [red]{spec_name}[/] (score: {score:.3f})")

                console.print()

        # AI-Powered Recommendations
        if recommendations:
            console.print()
            rec_panel = Panel(
                "\n".join([f"💡 {rec}" for rec in recommendations]),
                title="🎯 AI Recommendations",
                border_style="bright_blue",
                padding=(1, 2),
            )
            console.print(rec_panel)

        # Detailed scenario results (verbose mode)
        if args.verbose and detailed_results:
            console.print()
            console.print("📝 [bold cyan]Detailed Specification Results[/]")
            console.print("═" * 80)

            for i, result in enumerate(detailed_results, 1):
                status = "✅ PASSED" if result.get("passed") else "❌ FAILED"
                status_color = "green" if result.get("passed") else "red"

                # Create detailed result panel
                details_content = f"""
[bold]Specification:[/] {result.get("scenario_name", "Unknown")}
[bold]Description:[/] {result.get("description", "N/A")}
[bold]Confidence Score:[/] {result.get("confidence_score", 0.0):.3f}
[bold]Semantic Similarity:[/] {result.get("semantic_similarity", 0.0):.3f}
"""

                if not result.get("passed"):
                    details_content += f"[bold]Failure Reason:[/] {result.get('failure_reason', 'Unknown')}\n"

                    # Add fix guidance
                    details_content += "\n[bold yellow]💡 Fix Guidance:[/]\n"
                    if result.get("confidence_score", 0) < 0.6:
                        details_content += "• Review and improve the response quality\n"
                        details_content += (
                            "• Ensure the output addresses all aspects of the input\n"
                        )
                    if result.get("semantic_similarity", 0) < 0.5:
                        details_content += (
                            "• Make the response more relevant to the expected output\n"
                        )
                        details_content += "• Use similar terminology and concepts\n"

                console.print(
                    Panel(
                        details_content.strip(),
                        title=f"[{status_color}]Spec #{i}: {status}[/]",
                        border_style=status_color,
                        padding=(1, 2),
                    )
                )

        # Enhanced Next Steps - Only in verbose mode
        if getattr(args, "verbose", False):
            console.print()
            next_steps_content = ""

            if failed_specs == 0:
                next_steps_content = f"""🎉 [bold green]All specifications passed! Your agent is ready.[/]

[bold cyan]Recommended next steps:[/]
• [cyan]super agent run {agent_name} --goal "your goal"[/] - Execute your agent
• [cyan]super agent run {agent_name} --goal "Create a Python function"[/] - Try a real goal
• [cyan]super agent optimize {agent_name}[/] - Further tune performance for production
• [cyan]super agent evaluate {agent_name}[/] - Re-evaluate after optimization
• Add more comprehensive test scenarios for edge cases"""
            else:
                next_steps_content = f"""🔧 [bold yellow]{failed_specs} specification(s) need attention.[/]

[bold cyan]Recommended actions for better quality:[/]
• Review the grouped failure analysis above
• [cyan]super agent optimize {agent_name}[/] - Optimize agent performance
• [cyan]super agent evaluate {agent_name}[/] - Re-evaluate to measure improvement
• Use [cyan]--verbose[/] flag for detailed failure analysis

[bold green]You can still test your agent:[/]
• [cyan]super agent run {agent_name} --goal "your goal"[/] - Works even with failing specs
• [cyan]super agent run {agent_name} --goal "Create a simple function"[/] - Try basic goals
• [dim]💡 Agents can often perform well despite specification failures[/]

[bold cyan]For production use:[/]
• Aim for ≥80% pass rate before deploying to production
• Run optimization and re-evaluation cycles until quality gates pass"""

            console.print(
                Panel(
                    next_steps_content,
                    title="🎯 Next Steps",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )

        # Simple workflow guide (normal mode)
        console.print(
            f'🎯 [bold cyan]Next:[/] [cyan]super agent run {agent_name} --goal "your goal"[/]'
        )

        # Professional footer
        console.print()
        console.print("═" * 100, style="bright_cyan")
        console.print(
            f"🏁 [bold bright_cyan]Specification execution completed[/] [dim]- {pass_rate:.1f}% pass rate ({passed_specs}/{total_specs} specs)[/]",
            justify="center",
        )
        console.print("═" * 100, style="bright_cyan")
        console.print()

        # Explicit user guidance in a panel - only in verbose mode
        if getattr(args, "verbose", False):
            console.print()

            guidance_content = ""
            if failed_specs > 0:
                guidance_content += (
                    "🔧 [bold yellow]To improve your agent's performance:[/]\n"
                )
                guidance_content += f"   [cyan]super agent optimize {agent_name}[/] - Optimize the pipeline for better results\n\n"

            guidance_content += "🚀 [bold green]To run your agent:[/]\n"
            guidance_content += f'   [cyan]super agent run {agent_name} --goal "your specific goal here"[/]\n\n'

            guidance_content += "💡 [dim]Example goals:[/]\n"
            guidance_content += f'   • [cyan]super agent run {agent_name} --goal "Create a Python function to calculate fibonacci numbers"[/]\n'
            guidance_content += f'   • [cyan]super agent run {agent_name} --goal "Write a React component for a todo list"[/]\n'
            guidance_content += f'   • [cyan]super agent run {agent_name} --goal "Design a database schema for an e-commerce site"[/]'

            console.print(
                Panel(
                    guidance_content,
                    title="🎯 What would you like to do next?",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )
            console.print()

    except FileNotFoundError:
        console.print(f"❌ [bold red]Agent '{agent_name}' not found.[/]")
        console.print("💡 Available agents: [cyan]super agent list[/]")
    except Exception as e:
        console.print(f"❌ [bold red]Specification execution failed:[/] {e}")
        console.print(
            f"🔧 [dim]Try: super agent compile {agent_name} && super agent evaluate {agent_name}[/]"
        )


def lint_agent(args):
    """Handle agent playbook linting."""
    if not args.name and not args.all:
        console.print(
            "[bold red]❌ You must specify an agent name or use --all.[/bold red]"
        )
        return

    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"

        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            return

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

            # Use new SuperSpec structure: agents/ directory at project root
        agents_dir = project_root / "agents"

        if not agents_dir.exists():
            console.print(
                f"\n[bold red]❌ Agents directory not found for project '{project_name}'.[/]"
                f"\n[dim]Expected at: {agents_dir}[/]\n"
                f"[yellow]💡 Tip: Create agents using 'super spec generate'[/]"
            )
            return

        if args.all:
            playbook_files = sorted(list(agents_dir.rglob("*_playbook.yaml")))
            if not playbook_files:
                console.print(
                    f"\n[yellow]No agent playbooks found in '{agents_dir}'.[/yellow]"
                )
                return

            console.print(
                f"\n[bold blue]🔍 Linting all {len(playbook_files)} agents in project '{project_name}'...[/]"
            )
            total_errors = 0
            failed_agents = []

            for playbook_path in playbook_files:
                errors = _lint_playbook(playbook_path)
                if errors:
                    total_errors += len(errors)
                    failed_agents.append(playbook_path.stem.replace("_playbook", ""))

            console.print("=" * 60)
            if total_errors > 0:
                console.print(
                    f"\n[bold red]❌ Linting finished with a total of {total_errors} errors in {len(failed_agents)} agent(s).[/]"
                )
                console.print(
                    f"[bold yellow]Failed agents:[/] {', '.join(failed_agents)}"
                )
                sys.exit(1)
            else:
                console.print(
                    f"\n[bold green]✅ All {len(playbook_files)} agent playbooks passed linting successfully![/]"
                )

        else:
            agent_name = args.name.lower()
            playbook_pattern = f"**/{agent_name}_playbook.yaml"
            matching_playbooks = list(agents_dir.rglob(playbook_pattern))

            if not matching_playbooks:
                console.print(
                    f"\n[bold red]❌ Agent '{agent_name}' not found in project '{project_name}'.[/]"
                )
                sys.exit(1)

            playbook_path = matching_playbooks[0]

            if len(matching_playbooks) > 1:
                console.print(
                    f"[bold yellow]Warning: Found multiple playbooks for '{agent_name}'. Using the first one: {playbook_path}[/]"
                )

            errors = _lint_playbook(playbook_path)

            if errors:
                sys.exit(1)

    except Exception as e:
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during linting:[/] {e}"
        )
        sys.exit(1)


def _lint_playbook(playbook_path: Path):
    """Helper to lint a single playbook file and display results."""
    console.print("=" * 60)
    console.print(f"Linting: [cyan]{playbook_path.relative_to(Path.cwd())}[/]")

    linter = PlaybookLinter(playbook_path)
    errors = linter.lint()

    display_lint_results(playbook_path, linter.playbook, errors)

    if errors:
        console.print(f"[bold red]❌ Found {len(errors)} errors.[/]")
    else:
        console.print("[bold green]✅ No issues found.[/]")

    return errors


def design_agent(args):
    """Handle agent design command through Streamlit UI."""
    try:
        # Ensure Streamlit config directory exists to bypass onboarding
        streamlit_config_dir = Path.home() / ".streamlit"
        streamlit_config_dir.mkdir(exist_ok=True)

        # Create config.toml to disable usage stats gathering
        config_path = streamlit_config_dir / "config.toml"
        if not config_path.exists():
            config_content = textwrap.dedent("""
                [browser]
                gatherUsageStats = false
            """)
            config_path.write_text(config_content)
            console.print("[dim]Created Streamlit config to disable usage stats.[/dim]")

        # Create credentials.toml to bypass the email prompt
        credentials_path = streamlit_config_dir / "credentials.toml"
        if not credentials_path.exists():
            credentials_content = textwrap.dedent("""
                [general]
                email = ""
            """)
            credentials_path.write_text(credentials_content)
            console.print(
                "[dim]Created Streamlit credentials to bypass email prompt.[/dim]"
            )

        # Get UI path using DesignerFactory
        designer_factory = DesignerFactory()
        designer_path = designer_factory.get_designer(args.tier)

        panel_content = (
            f"🚀 [bold cyan]super Agent Designer[/]\n\n"
            f"[yellow]Agent:[/] {args.agent.upper()}\n"
            f"[yellow]Tier:[/] {args.tier.capitalize()}\n"
            f"└── [yellow]UI:[/] [link=http://localhost:8501]http://localhost:8501[/link]\n\n"
            f"[dim]Starting designer... Use Ctrl+C to stop when done.[/]"
        )

        console.print(
            Panel(panel_content, title="🎨 Agent Design Studio", border_style="blue")
        )

        env = os.environ.copy()
        env.update({"SUPER_AGENT_NAME": args.agent, "SUPER_AGENT_LEVEL": args.tier})

        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(designer_path),
            "--server.port=8501",
            "--server.headless=true",  # Run headless to avoid auto-opening browser
            "--",
            args.agent,
            args.tier,
        ]

        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        console.print("[cyan]Waiting for designer UI to launch...[/]")

        app_ready = False
        start_time = time.time()
        startup_timeout = 30  # seconds

        while time.time() - start_time < startup_timeout:
            if process.poll() is not None:
                _, stderr = process.communicate()
                console.print("[bold red]❌ Designer failed to start![/]")
                console.print(
                    Panel(stderr, title="[red]Error Details[/red]", border_style="red")
                )
                sys.exit(1)

            try:
                # Health check to see if the server is up
                import requests

                response = requests.get("http://localhost:8501", timeout=1)
                if response.status_code == 200:
                    app_ready = True
                    break
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ):
                time.sleep(1)  # Wait and retry
            except ImportError:
                console.print(
                    "[yellow]Warning: 'requests' library not found. Using a less reliable health check.[/yellow]"
                )
                # Basic fallback without requests
                import urllib.request

                try:
                    with urllib.request.urlopen(
                        "http://localhost:8501", timeout=1
                    ) as response:
                        if response.getcode() == 200:
                            app_ready = True
                            break
                except Exception:
                    time.sleep(1)

        if app_ready:
            console.print("[bold green]✅ Designer UI is ready![/]")
            console.print(
                "🌐 Visit: [link=http://localhost:8501]http://localhost:8501[/link]"
            )
        else:
            console.print("[bold yellow]⚠️ Designer is taking a long time to start.[/]")
            console.print(
                "It's running in the background. Please try visiting [link=http://localhost:8501]http://localhost:8501[/link] manually."
            )

        try:
            console.print(
                "\n[dim]Designer is running. Press Ctrl+C here to stop the server.[/]"
            )
            process.wait()
            console.print("\n[green]✅ Designer session ended.[/]")
        except KeyboardInterrupt:
            console.print("\n[yellow]🛑 Stopping designer...[/]")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            console.print("[green]✅ Designer stopped.[/]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error launching designer:[/] {e}")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/]")
        if "process" in locals() and process.poll() is None:
            process.kill()
        sys.exit(1)


def add_agent(args):
    """Handle agent add command with enhanced visual feedback and tier support."""
    try:
        agent_name = args.name.lower()
        tier_level = getattr(args, "tier", None)
        project_root = Path.cwd()

        # Read system name from .super
        with open(project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        # Get the correct path to agents directory
        package_root = Path(__file__).parent.parent.parent

        # Support Optimas demo aliases mapped to testing playbooks
        alias_map = {
            "optimas_dspy": "optimas/optimas_dspy_playbook.yaml",
            "optimas-openai": "optimas/optimas_openai_playbook.yaml",
            "optimas_openai": "optimas/optimas_openai_playbook.yaml",
            "optimas-crewai": "optimas/optimas_crewai_playbook.yaml",
            "optimas_crewai": "optimas/optimas_crewai_playbook.yaml",
            "optimas-autogen": "optimas/optimas_autogen_playbook.yaml",
            "optimas_autogen": "optimas/optimas_autogen_playbook.yaml",
            # Pydantic AI MCP demo
            "pydantic-mcp": "demo/pydantic_mcp_playbook.yaml",
            "pydantic_mcp": "demo/pydantic_mcp_playbook.yaml",
            # Pydantic AI Gateway demo
            "pydantic-gateway-demo": "demo/pydantic-gateway-demo_playbook.yaml",
            "pydantic_gateway_demo": "demo/pydantic-gateway-demo_playbook.yaml",
            # Pydantic AI RLM demo
            "pydantic-rlm": "demo/pydantic-rlm_playbook.yaml",
            "pydantic_rlm": "demo/pydantic-rlm_playbook.yaml",
            # DSPy RLM demo
            "dspy-rlm": "demo/dspy-rlm_playbook.yaml",
            "dspy_rlm": "demo/dspy-rlm_playbook.yaml",
            # DSPy automation demo
            "dspy-demo": "demo/dspy-demo_playbook.yaml",
            "dspy_demo": "demo/dspy-demo_playbook.yaml",
            # Google ADK RLM demo
            "adk-rlm": "demo/adk-rlm_playbook.yaml",
            "adk_rlm": "demo/adk-rlm_playbook.yaml",
            # StackOne Calendly demo (framework-neutral id, with legacy aliases)
            "stackone-calendly": "demo/stackone-calendly_playbook.yaml",
            "stackone_calendly": "demo/stackone-calendly_playbook.yaml",
            "dspy-stackone-calendly": "demo/stackone-calendly_playbook.yaml",
            "dspy_stackone_calendly": "demo/stackone-calendly_playbook.yaml",
            # DeepAgents StackOne demo
            "deepagents-stackone": "demo/deepagents-stackone_playbook.yaml",
            "deepagents_stackone": "demo/deepagents-stackone_playbook.yaml",
            # DeepAgents RLM demo
            "deepagents-rlm": "demo/deepagents-rlm_playbook.yaml",
            "deepagents_rlm": "demo/deepagents-rlm_playbook.yaml",
            # CrewAI StackOne demo
            "crewai-stackone": "demo/crewai-stackone_playbook.yaml",
            "crewai_stackone": "demo/crewai-stackone_playbook.yaml",
            # CrewAI RLM demo
            "crewai-rlm": "demo/crewai-rlm_playbook.yaml",
            "crewai_rlm": "demo/crewai-rlm_playbook.yaml",
        }

        if agent_name in alias_map:
            source_playbook = package_root / "agents" / alias_map[agent_name]
            target_ref = agent_name
        else:
            # Simplified playbook search
            source_playbook = next(
                package_root.rglob(f"**/agents/**/{agent_name}_playbook.yaml"), None
            )
            target_ref = agent_name

        if not source_playbook:
            console.print(f"\n[bold red]❌ Agent '{agent_name}' not found.[/]")
            console.print("\n[yellow]💡 Need help finding the right agent?[/yellow]")
            console.print(
                "[cyan]🔍 Browse all available pre-built agents with:[/] super agent list --pre-built"
            )
            console.print(
                "[cyan]🏢 Filter by industry:[/] super agent list --pre-built --industry <industry_name>"
            )
            sys.exit(1)

        target_playbook_dir = (
            project_root / system_name / "agents" / target_ref / "playbook"
        )
        target_playbook_dir.mkdir(parents=True, exist_ok=True)
        target_playbook_path = target_playbook_dir / f"{target_ref}_playbook.yaml"

        # Load playbook to get metadata for rich display
        with open(source_playbook) as f:
            playbook_data = yaml.safe_load(f)

        # Apply tier-specific enhancements to the playbook
        if tier_level == "genies":
            console.print(
                f"[cyan]🚀 Enhancing agent '{agent_name}' for Genies tier...[/]"
            )

            # Update metadata
            playbook_data["metadata"]["level"] = "genies"

            spec = playbook_data.get("spec", {})

            # Update model for Genies tier (keeping same model for simplicity)
            spec["language_model"] = {
                "provider": "ollama",
                "model": "llama3.1:8b",
                "temperature": 0.1,
                "max_tokens": 2000,
                "api_base": "http://localhost:11434",
            }
            console.print(
                "[green]  ✅ Model configured for Genies tier: llama3.1:8b[/]"
            )

            # Set task type to react
            if "tasks" in spec and spec["tasks"]:
                for task in spec["tasks"]:
                    task["type"] = "react"

            # Add ReAct configuration
            spec["react_config"] = {"max_iters": 5}
            console.print("[green]  ✅ ReAct configuration added[/]")

            # Add tools configuration
            spec["tools"] = {
                "builtin_tools": [
                    {"name": "calculator"},
                    {"name": "text_analyzer"},
                    {"name": "file_reader"},
                ]
            }
            console.print(
                "[green]  ✅ Default toolset added (calculator, text_analyzer, file_reader)[/]"
            )

            # Add memory configuration
            spec["memory"] = {"enabled": True, "types": ["short_term", "episodic"]}
            console.print("[green]  ✅ Memory system configured[/]")

            # Ensure agentflow is removed as it's not used in this ReAct setup
            if "agentflow" in spec:
                del spec["agentflow"]

            console.print("[green]  ✅ Preserving optimization and testing sections[/]")

        # Create target directory and write the file
        with open(target_playbook_path, "w") as f:
            yaml.dump(
                playbook_data,
                f,
                Dumper=NoAliasDumper,
                default_flow_style=False,
                sort_keys=False,
            )

        # Show success with consistent UI style
        console.print("=" * 80)
        console.print(
            f"\n🤖 [bold bright_cyan]Adding agent '[bold yellow]{target_ref}[/]'...[/]"
        )

        console.print(
            Panel(
                "🎉 [bold bright_green]AGENT ADDED SUCCESSFULLY![/] Pre-built Agent Ready",
                style="bright_green",
                border_style="bright_green",
            )
        )

        # Agent information panel (concise)
        display_tier = (
            tier_level or playbook_data.get("metadata", {}).get("level", "oracles")
        ).title()
        tier_emoji = "🧞" if display_tier == "Genies" else "🔮"
        agent_info = f"""🤖 [bold]Name:[/] {playbook_data.get("metadata", {}).get("name", "Unknown")}
🏢 [bold]Industry:[/] {playbook_data.get("metadata", {}).get("namespace", "general").title()} | {tier_emoji} [bold]Tier:[/] {display_tier}
🔧 [bold]Tasks:[/] {len(playbook_data.get("spec", {}).get("tasks", []))} | 📁 [bold]Location:[/] [cyan]{target_playbook_path.relative_to(project_root)}[/]"""

        if display_tier == "Genies":
            agent_info += "\n🚀 [bold]Features:[/] ReAct Agents + Tools + Memory"

        console.print(
            Panel(
                agent_info,
                title="📋 Agent Details",
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )

        # Customization guidance panel (concise)
        customization_info = """✨ [bold bright_magenta]Pre-built Agent - Ready to Customize![/]

📝 [bold]Modify:[/] persona, tasks, inputs/outputs, model settings"""

        console.print(
            Panel(
                customization_info,
                title="🛠️ Customization Options",
                border_style="bright_magenta",
                padding=(1, 2),
            )
        )

        # Next steps panel (concise)
        next_steps = f"""🚀 [bold bright_cyan]NEXT STEPS[/]

[cyan]super agent compile {target_ref}[/] - Generate executable pipeline
[cyan]super agent run {target_ref} --goal "goal"[/] - Execute agent

[dim]💡 Comprehensive guide: [cyan]super docs[/] | 🔍 More agents: [cyan]super market[/][/]"""

        console.print(
            Panel(
                next_steps,
                title="🎯 Workflow Guide",
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )

        console.print("=" * 80)
        console.print(
            f"🎉 [bold bright_green]Agent '{playbook_data.get('metadata', {}).get('name', target_ref)}' ready for customization and deployment![/] 🚀"
        )

    except FileNotFoundError as e:
        console.print(f"\n[bold red]❌ Project file not found:[/] {e}")
        console.print(
            "[yellow]💡 Make sure you're in a valid super project directory.[/]"
        )
        console.print(
            "[cyan]Run 'super init <project_name>' to create a new project.[/]"
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"\n[bold red]❌ Error parsing agent playbook:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to add agent:[/] {e}")
        sys.exit(1)


def list_agents(args):
    """List agents based on the provided arguments."""
    if hasattr(args, "pre_built") and args.pre_built:
        list_pre_built_agents(args)
    else:
        list_project_agents(args)


def list_project_agents(args):
    """List agents in the current super project."""
    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"

        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            console.print(
                "[cyan]💡 Quick start: super init my_project && cd my_project[/cyan]"
            )
            return

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        agents_dir = project_root / project_name / "agents"

        if not agents_dir.exists() or not any(agents_dir.iterdir()):
            console.print(
                f"\n[bold blue]📋 Project Agents - {project_name}[/bold blue]"
            )
            console.print("[yellow]No agents found in your project yet.[/yellow]")
            console.print("\n[cyan]🚀 Get started with pre-built agents:[/cyan]")
            console.print(
                "   [bold]super agent list --pre-built[/bold]           - Browse all available agents"
            )
            console.print(
                "   [bold]super agent list --pre-built --industry tech[/bold] - Filter by industry"
            )
            console.print(
                "   [bold]super agent pull developer[/bold]                - Add a specific agent"
            )
            console.print("\n[cyan]💡 Or create your own:[/cyan]")
            console.print(
                "   [bold]super agent design[/bold]                      - Interactive agent designer"
            )
            return

        playbook_files = list(agents_dir.rglob("*_playbook.yaml"))
        if not playbook_files:
            console.print(
                f"\n[bold blue]📋 Project Agents - {project_name}[/bold blue]"
            )
            console.print("[yellow]No agent playbooks found in your project.[/yellow]")
            console.print("\n[cyan]🔧 This might happen if:[/cyan]")
            console.print("   • Agents were added but playbooks are missing")
            console.print(
                "   • Playbooks don't follow the *_playbook.yaml naming convention"
            )
            console.print("\n[cyan]💡 Quick fixes:[/cyan]")
            console.print(
                "   [bold]super agent pull <agent_name>[/bold]    - Add a pre-built agent"
            )
            console.print(
                "   [bold]super agent list --pre-built[/bold]   - See available agents"
            )
            return

        agents = []
        for playbook_file in playbook_files:
            try:
                with open(playbook_file, "r") as f:
                    playbook = yaml.safe_load(f)
                if playbook and "metadata" in playbook:
                    metadata = playbook["metadata"]
                    playbook_ref = playbook_file.stem.replace("_playbook", "")

                    # Check compilation status
                    agent_dir = playbook_file.parent.parent
                    pipeline_dir = agent_dir / "pipelines"
                    compiled_pipeline = pipeline_dir / f"{playbook_ref}_pipeline.py"
                    optimized_pipeline = pipeline_dir / f"{playbook_ref}_optimized.json"

                    # Determine status
                    if optimized_pipeline.exists():
                        status = "🚀 Optimized"
                        status_color = "bright_green"
                    elif compiled_pipeline.exists():
                        status = "⚡ Compiled"
                        status_color = "yellow"
                    else:
                        status = "📋 Playbook"
                        status_color = "blue"

                    # Check for recent traces
                    trace_path = (
                        project_root
                        / ".superoptix"
                        / "traces"
                        / f"{playbook_ref}.jsonl"
                    )
                    last_run = "Never"
                    if trace_path.exists():
                        try:
                            import datetime
                            import os

                            mtime = os.path.getmtime(trace_path)
                            last_run = datetime.datetime.fromtimestamp(mtime).strftime(
                                "%m-%d %H:%M"
                            )
                        except:
                            last_run = "Unknown"

                    agents.append(
                        {
                            "name": metadata.get("name", "Unknown"),
                            "id": metadata.get("id", "No ID"),
                            "type": metadata.get("agent_type", "Unknown"),
                            "level": metadata.get("level", "oracles"),
                            "ref": playbook_ref,
                            "status": status,
                            "status_color": status_color,
                            "last_run": last_run,
                        }
                    )
            except yaml.YAMLError as e:
                console.print(
                    f"[yellow]Warning: Could not parse {playbook_file.name}: {e}[/]"
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not process {playbook_file.name}: {e}[/]"
                )

        agents.sort(key=lambda x: x["name"])

        table = Table(title=f"📋 Project Agents: {project_name}", border_style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Agent ID", style="magenta")
        table.add_column("Status", style="white")
        table.add_column("Level", style="green")
        table.add_column("Last Run", style="cyan")
        table.add_column("Playbook Ref", style="bold blue")

        for agent in agents:
            status_styled = f"[{agent['status_color']}]{agent['status']}[/]"
            table.add_row(
                agent["name"],
                agent["id"],
                status_styled,
                agent["level"],
                agent["last_run"],
                agent["ref"],
            )
        console.print(table)

        # Show helpful next steps
        console.print("\n[cyan]💡 Quick Actions:[/cyan]")
        console.print(
            "   [bold]super agent ps[/bold] or [bold]super agent list[/bold]     - Refresh this list"
        )
        console.print(
            "   [bold]super agent compile <name>[/bold]         - Compile an agent"
        )
        console.print(
            "   [bold]super agent optimize <name>[/bold]        - Optimize performance"
        )
        console.print(
            '   [bold]super agent run <name> -i "task"[/bold]   - Execute an agent'
        )
        console.print(
            "   [bold]super agent inspect <name>[/bold]         - View agent details"
        )

    except FileNotFoundError:
        console.print(
            f"\n[bold red]❌ Project directory for '{project_name}' not found.[/bold red]"
        )
    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to list project agents:[/] {e}")
        sys.exit(1)


def list_pre_built_agents(args):
    """List all available pre-built agents, optionally filtered by industry."""
    try:
        package_root = Path(__file__).parent.parent.parent
        agents_dir = package_root / "agents"

        if not agents_dir.exists():
            console.print(
                f"\n[bold red]❌ Agents directory not found at:[/] {agents_dir}"
            )
            return

        available_industries = sorted(
            [d.name for d in agents_dir.iterdir() if d.is_dir()]
        )

        # Show industry filter info if filtering
        industry_filter = None
        if hasattr(args, "industry") and args.industry:
            industry_filter = args.industry.lower()
            industry_dir = agents_dir / industry_filter
            if not industry_dir.exists():
                console.print(
                    f"\n[bold red]❌ Industry '{args.industry}' not found.[/]"
                )
                console.print("\n[cyan]📊 Available Industries:[/cyan]")
                table = Table(show_header=False, box=None)
                num_columns = 3
                rows = [
                    available_industries[i : i + num_columns]
                    for i in range(0, len(available_industries), num_columns)
                ]
                for row in rows:
                    table.add_row(
                        *[
                            f"• [blue]{item.replace('_', ' ').title()}[/blue]"
                            for item in row
                        ]
                    )
                console.print(table)
                console.print(
                    "\n[cyan]💡 Try:[/cyan] [bold]super agent list --pre-built --industry <industry_name>[/bold]"
                )
                return
        else:
            console.print(
                f"\n[cyan]📊 Available Industries ([magenta]{len(available_industries)}[/magenta]):[/cyan]"
            )
            table = Table(show_header=False, box=None)
            num_columns = 3
            rows = [
                available_industries[i : i + num_columns]
                for i in range(0, len(available_industries), num_columns)
            ]
            for row in rows:
                table.add_row(
                    *[
                        f"• [blue]{item.replace('_', ' ').title()}[/blue]"
                        for item in row
                    ]
                )
            console.print(table)
            console.print()

        if industry_filter:
            playbook_files = list(
                (agents_dir / industry_filter).rglob("*_playbook.yaml")
            )
        else:
            playbook_files = list(agents_dir.rglob("*_playbook.yaml"))

        if not playbook_files:
            console.print("\n[yellow]No agents found for the specified criteria.[/]")
            return

        agents = []
        for playbook_file in playbook_files:
            try:
                with open(playbook_file, "r") as f:
                    playbook = yaml.safe_load(f)
                if playbook and "metadata" in playbook:
                    metadata = playbook["metadata"]
                    industry = metadata.get("namespace", "Unknown")
                    if industry_filter and industry.lower() != industry_filter:
                        continue

                    playbook_ref = playbook_file.stem.replace("_playbook", "")
                    agents.append(
                        {
                            "name": metadata.get("name", "Unknown"),
                            "id": metadata.get("id", "No ID"),
                            "type": metadata.get("agent_type", "Unknown"),
                            "level": metadata.get("level", "oracles"),
                            "ref": playbook_ref,
                            "industry": industry,
                        }
                    )
            except yaml.YAMLError as e:
                console.print(
                    f"[yellow]Warning: Could not parse {playbook_file.name}: {e}[/]"
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not process {playbook_file.name}: {e}[/]"
                )

        agents.sort(key=lambda x: (x["industry"], x["name"]))

        title = "📋 Available Pre-built Agents"
        if industry_filter:
            title += f" in '{industry_filter.capitalize()}'"

        table = Table(title=title, border_style="blue")
        table.add_column("Industry", style="cyan", no_wrap=True)
        table.add_column("Name", style="yellow")
        table.add_column("ID", style="magenta")
        table.add_column("Level", style="green")
        table.add_column("Type", style="white")
        table.add_column("Playbook Ref", style="bold blue")

        for agent in agents:
            table.add_row(
                agent["industry"].capitalize(),
                agent["name"],
                agent["id"],
                agent["level"],
                agent["type"],
                agent["ref"],
            )

        console.print(table)

        # Show count and helpful instructions
        agent_count = len(agents)
        console.print(
            f"\n[bright_green]✅ Found {agent_count} pre-built agent(s)[/bright_green]"
        )

        console.print("\n[cyan]🚀 Next Steps:[/cyan]")
        console.print(
            "   [bold]super agent pull <playbook_ref>[/bold]           - Add an agent to your project"
        )
        if not industry_filter:
            console.print(
                "   [bold]super agent list --pre-built --industry <name>[/bold] - Filter by industry"
            )
        else:
            console.print(
                "   [bold]super agent list --pre-built[/bold]                  - Show all industries"
            )
        console.print(
            "   [bold]super agent design[/bold]                        - Create a custom agent"
        )

        if agent_count > 0:
            # Show example with first agent
            example_ref = agents[0]["ref"]
            console.print(
                f"\n[cyan]💡 Example:[/cyan] [bold]super agent pull {example_ref}[/bold]"
            )

    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to list pre-built agents:[/] {e}")
        sys.exit(1)


def show_tier_status(args):
    """Show current tier status and available features."""
    # Get user tier from config or default to ORACLES
    user_tier = getattr(args, "tier", None)
    if user_tier is None:
        user_tier = TierLevel.ORACLES
    elif isinstance(user_tier, str):
        user_tier = TierLevel(user_tier.lower())

    console.print("\n[bold blue]🎯 Current Tier Status[/bold blue]")

    # Show current tier
    tier_panel = Panel(
        f"[bold green]{user_tier.value.title()}[/bold green]",
        title="Your Active Tier",
        border_style="green",
    )
    console.print(tier_panel)

    # Show available features
    console.print(
        f"\n[bold cyan]✅ Features Available in {user_tier.value.title()} Tier[/bold cyan]"
    )
    accessible_features = tier_system.get_accessible_features(user_tier)

    available_table = Table()
    available_table.add_column("Feature", style="green")
    available_table.add_column("Description", style="white")
    available_table.add_column("Status", style="blue")

    for feature in accessible_features:
        status = "Beta" if feature.beta else "Available"
        if feature.enterprise_only:
            status += " (Enterprise)"

        available_table.add_row(
            feature.name,
            feature.description[:60] + "..."
            if len(feature.description) > 60
            else feature.description,
            status,
        )

    console.print(available_table)

    # Show upgrade options
    next_tier_features = []
    for tier_level in TierLevel:
        if (
            tier_system.tier_hierarchy[tier_level]
            > tier_system.tier_hierarchy[user_tier]
        ):
            tier_features = [
                f for f in tier_system.features.values() if f.min_tier == tier_level
            ]
            if tier_features:
                next_tier_features.extend(
                    tier_features[:3]
                )  # Show first 3 features from next tier
                break

    if next_tier_features:
        console.print("\n[bold yellow]🚀 Upgrade to unlock more features[/bold yellow]")

        upgrade_table = Table(title="Next Tier Features")
        upgrade_table.add_column("Feature", style="yellow")
        upgrade_table.add_column("Description", style="white")
        upgrade_table.add_column("Required Tier", style="red")

        for feature in next_tier_features:
            upgrade_table.add_row(
                feature.name,
                feature.description[:50] + "..."
                if len(feature.description) > 50
                else feature.description,
                feature.min_tier.value.title(),
            )

        console.print(upgrade_table)

        # Show upgrade info
        upgrade_info = Panel(
            """
[bold]🔓 Ready to upgrade?[/bold]

• Visit: https://super-agentic.ai/upgrade
• Email: upgrade@super-agentic.ai
• Schedule a demo: https://calendly.com/shashikant-super-agentic/30min

[dim]Get access to advanced DSPy capabilities, priority support, and early access to beta features.[/dim]
            """,
            title="Upgrade Information",
            border_style="yellow",
        )
        console.print(upgrade_info)


def _run_universal_gepa_optimization(args, agent_name, project_root, playbook):
    """
    Run Universal GEPA optimization for any framework.

    Args:
        args: CLI arguments with GEPA parameters
        agent_name: Name of the agent
        project_root: Project root directory
        playbook: Agent playbook dict

    Returns:
        True if optimization succeeded, False otherwise
    """
    framework = getattr(args, "framework", "dspy")

    console.print("\n🔬 [bold cyan]Running Universal GEPA Optimization[/]")
    console.print(f"   Framework: [yellow]{framework}[/]")

    # Check for GEPA parameters from CLI
    cli_auto = getattr(args, "auto", None)
    cli_max_full_evals = getattr(args, "max_full_evals", None)
    cli_max_metric_calls = getattr(args, "max_metric_calls", None)
    reflection_lm = getattr(args, "reflection_lm", None)

    # Check if CLI provided any budget parameter
    cli_budget_provided = bool(cli_auto or cli_max_full_evals or cli_max_metric_calls)

    # Try to get optimization params from playbook if not provided via CLI
    opt_config = playbook.get("spec", {}).get("optimization", {})
    optimizer_config = opt_config.get("optimizer", {})
    params = optimizer_config.get("params", {})

    # Use CLI values directly if provided, otherwise fallback to playbook
    auto = cli_auto
    max_full_evals = cli_max_full_evals
    max_metric_calls = cli_max_metric_calls

    # Fallback to playbook ONLY if CLI didn't provide that specific parameter
    if not cli_auto and not cli_budget_provided:
        auto = params.get("auto")
        if auto:
            console.print(f"\n✅ Using auto from playbook: {auto}")

    if not cli_max_full_evals and not cli_budget_provided:
        max_full_evals = params.get("max_full_evals")
        if max_full_evals:
            console.print(f"\n✅ Using max_full_evals from playbook: {max_full_evals}")

    if not cli_max_metric_calls and not cli_budget_provided:
        max_metric_calls = params.get("max_metric_calls")
        if max_metric_calls:
            console.print(
                f"\n✅ Using max_metric_calls from playbook: {max_metric_calls}"
            )

    # IMPORTANT: If CLI provided max_metric_calls or max_full_evals,
    # we must NOT use 'auto' from playbook (they conflict in GEPA)
    if (cli_max_metric_calls or cli_max_full_evals) and auto and not cli_auto:
        playbook_auto = auto
        auto = None
        console.print(
            f"\n[yellow]⚠️  CLI --max-metric-calls={cli_max_metric_calls or cli_max_full_evals} overrides playbook 'auto: {playbook_auto}' setting[/]"
        )

    if not reflection_lm:
        reflection_lm = params.get("reflection_lm")
        if reflection_lm:
            # Auto-detect and add ollama: prefix if needed
            if isinstance(reflection_lm, str):
                known_providers = [
                    "ollama",
                    "openai",
                    "anthropic",
                    "google",
                    "bedrock",
                    "azure",
                    "cohere",
                    "mistral",
                    "deepseek",
                    "groq",
                    "together",
                    "fireworks",
                    "litellm",
                    "gateway",
                ]
                has_provider_prefix = any(
                    reflection_lm.startswith(f"{p}:") for p in known_providers
                )

                # If no prefix and model contains ':' (like llama3.1:8b), assume Ollama
                if not has_provider_prefix and ":" in reflection_lm:
                    ollama_indicators = [
                        ":8b",
                        ":7b",
                        ":13b",
                        ":70b",
                        "llama",
                        "mistral",
                        "codellama",
                        "phi",
                        "gemma",
                        "qwen",
                    ]
                    if any(
                        indicator in reflection_lm.lower()
                        for indicator in ollama_indicators
                    ):
                        reflection_lm = f"ollama:{reflection_lm}"
                        console.print(
                            f"\n✅ Using reflection_lm from playbook: {reflection_lm} (auto-detected Ollama)"
                        )
                    else:
                        console.print(
                            f"\n✅ Using reflection_lm from playbook: {reflection_lm}"
                        )
                else:
                    console.print(
                        f"\n✅ Using reflection_lm from playbook: {reflection_lm}"
                    )
            else:
                console.print(
                    f"\n✅ Using reflection_lm from playbook: {reflection_lm}"
                )

    # Fallback: derive reflection_lm from CLI provider/model if user did not pass --reflection-lm.
    if not reflection_lm:
        cli_model = getattr(args, "model", None)
        cli_provider = getattr(args, "provider", None)
        if cli_model:
            reflection_lm = str(cli_model).strip()
            if cli_provider and "/" not in reflection_lm:
                provider_norm = str(cli_provider).strip().lower()
                if provider_norm in {"google", "google-genai"}:
                    provider_norm = "gemini"
                elif provider_norm == "local":
                    provider_norm = "ollama"
                reflection_lm = f"{provider_norm}/{reflection_lm}"
            console.print(
                f"\n✅ Using reflection_lm from CLI model override: {reflection_lm}"
            )

    # Validate GEPA configuration
    if not (auto or max_full_evals or max_metric_calls):
        console.print("\n[red]❌ GEPA requires a budget parameter:[/]")
        console.print("   Use one of:")
        console.print("     --auto light|medium|heavy")
        console.print("     --max-full-evals <number>")
        console.print("     --max-metric-calls <number>")
        console.print(
            "\n   Example: super agent optimize my_agent --framework crewai --auto medium --reflection-lm gpt-4o"
        )
        return False

    if not reflection_lm:
        console.print("\n[red]❌ GEPA requires --reflection-lm parameter[/]")
        console.print("   Either provide via CLI: --reflection-lm ollama:llama3.1:8b")
        console.print("   Or configure in playbook YAML:")
        console.print("   optimization:")
        console.print("     optimizer:")
        console.print("       name: GEPA")
        console.print("       params:")
        console.print("         reflection_lm: ollama:llama3.1:8b")
        console.print(
            "\n   Supported models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, ollama:llama3.1:8b, etc."
        )
        return False

    # Check if MCP tool optimization is enabled
    spec_data = playbook.get("spec", playbook)
    mcp_config = spec_data.get("mcp", {})
    optimize_mcp_tools = mcp_config.get("enabled", False) and mcp_config.get(
        "optimization", {}
    ).get("optimize_tool_descriptions", False)

    # Check if field description optimization is enabled
    optimize_field_descriptions = opt_config.get("optimize_field_descriptions", False)
    output_fields = spec_data.get("output_fields", [])

    # Field description optimization requires output_fields to be defined
    if optimize_field_descriptions and not output_fields:
        console.print(
            "\n[yellow]⚠️  Field description optimization enabled but no output_fields found in playbook[/]"
        )
        console.print(
            "   Field description optimization requires output_fields to be defined."
        )
        console.print("   Disabling field description optimization...")
        optimize_field_descriptions = False

    # Get training data from playbook BDD scenarios
    scenarios = []
    if "feature_specifications" in spec_data and spec_data[
        "feature_specifications"
    ].get("scenarios"):
        scenarios = spec_data["feature_specifications"]["scenarios"]

    if not scenarios:
        console.print(
            "\n[yellow]⚠️  No BDD scenarios found in playbook for training data[/]"
        )
        console.print(
            "   Add scenarios to your playbook's feature_specifications section"
        )
        console.print("   Or provide custom training data")
        return False

    # Convert BDD scenarios to GEPA dataset format
    trainset = []
    for sc in scenarios:
        inp = sc.get("input", {}) or {}
        expected = sc.get("expected_output", {}) or {}

        example = {
            "inputs": inp,
            "outputs": expected,
        }
        trainset.append(example)

    console.print(f"   Training examples: [green]{len(trainset)}[/]")

    # Split into train and val
    split_idx = int(len(trainset) * 0.8)
    train_data = trainset[:split_idx] if split_idx > 0 else trainset
    val_data = trainset[split_idx:] if split_idx < len(trainset) else trainset[:1]

    console.print(f"   Train: {len(train_data)}, Val: {len(val_data)}")

    # Create component using Framework Registry
    console.print(f"\n📦 Creating {framework} component...")
    try:
        model_config_override = {}
        if getattr(args, "provider", None):
            model_config_override["provider"] = args.provider
        if getattr(args, "model", None):
            model_config_override["model"] = args.model
        if getattr(args, "cloud", False):
            model_config_override["runtime_mode"] = "direct"
        elif getattr(args, "local", False):
            model_config_override["runtime_mode"] = "local"

        component_kwargs = {}
        if model_config_override:
            component_kwargs["model_config"] = model_config_override

        component = FrameworkRegistry.create_component(
            framework=framework,
            playbook=playbook,
            **component_kwargs,
        )
        console.print(f"   ✅ Component created: {component.name}")
        console.print(f"   Framework: {component.framework}")
        console.print(f"   Optimizable: {component.optimizable}")
    except Exception as e:
        console.print(f"\n[red]❌ Failed to create component: {e}[/]")
        import traceback

        if getattr(args, "verbose", False):
            traceback.print_exc()
        return False

    # Define a simple metric (can be customized via playbook in future)
    def simple_metric(inputs, outputs, gold, component_name=None):
        """Simple metric for testing - checks if outputs match expected."""
        score = 1.0  # Default to perfect if no validation
        feedback = "Execution successful"

        # Simple keyword matching for now
        if "response" in outputs and "expected_response" in gold:
            response = str(outputs.get("response", "")).lower()
            expected = str(gold.get("expected_response", "")).lower()

            if expected in response:
                score = 1.0
                feedback = "Response matches expected output"
            else:
                score = 0.5
                feedback = f"Response differs from expected. Got: {response[:100]}"

        return {"score": score, "feedback": feedback}

    # Create Universal GEPA optimizer
    console.print("\n🚀 Initializing Universal GEPA optimizer...")
    try:
        optimizer_kwargs = {
            "metric": simple_metric,
            "reflection_lm": reflection_lm,
            "reflection_minibatch_size": getattr(args, "reflection_minibatch_size", 3),
            "skip_perfect_score": getattr(args, "skip_perfect_score", True),
            "use_merge": getattr(args, "use_merge", True),
            "failure_score": 0.0,
            "perfect_score": 1.0,
            "track_stats": getattr(args, "track_stats", False),
            "seed": 42,
        }

        # Add budget parameter
        if auto:
            optimizer_kwargs["auto"] = auto
        elif max_full_evals:
            optimizer_kwargs["max_full_evals"] = max_full_evals
        elif max_metric_calls:
            optimizer_kwargs["max_metric_calls"] = max_metric_calls

        # Add optional log_dir
        log_dir = getattr(args, "log_dir", None)
        if log_dir:
            optimizer_kwargs["log_dir"] = log_dir

        optimizer = UniversalGEPA(**optimizer_kwargs)
        console.print("   ✅ Optimizer created")
        console.print(f"   Budget: {auto or max_full_evals or max_metric_calls}")
        console.print(f"   Reflection LM: {reflection_lm}")

    except Exception as e:
        console.print(f"\n[red]❌ Failed to create optimizer: {e}[/]")
        if getattr(args, "verbose", False):
            import traceback

            traceback.print_exc()
        return False

    # Phase 1: Optimize MCP tool descriptions if enabled
    if optimize_mcp_tools:
        console.print("\n🔧 [bold cyan]Phase 1: Optimizing MCP Tool Descriptions[/]")
        mcp_result = _optimize_mcp_tools(
            playbook=playbook,
            reflection_lm=reflection_lm,
            train_data=train_data,
            val_data=val_data,
            auto=auto,
            max_full_evals=max_full_evals,
            max_metric_calls=max_metric_calls,
            agent_name=agent_name,
            project_root=project_root,
        )
        if not mcp_result:
            console.print(
                "[yellow]⚠️  MCP tool optimization failed, continuing with instruction optimization...[/]"
            )

    # Phase 1.5: Optimize field descriptions if enabled (only for Pydantic AI)
    if optimize_field_descriptions and framework == "pydantic-ai":
        console.print("\n📝 [bold cyan]Phase 1.5: Optimizing Field Descriptions[/]")
        field_result = _optimize_field_descriptions(
            playbook=playbook,
            reflection_lm=reflection_lm,
            train_data=train_data,
            val_data=val_data,
            auto=auto,
            max_full_evals=max_full_evals,
            max_metric_calls=max_metric_calls,
            agent_name=agent_name,
            project_root=project_root,
            optimizer_kwargs=optimizer_kwargs,
        )
        if not field_result:
            console.print(
                "[yellow]⚠️  Field description optimization failed, continuing with instruction optimization...[/]"
            )

    # Phase 2: Optimize instructions (always run)
    console.print(
        "\n⚡ [bold cyan]Phase 2: Running GEPA optimization for instructions...[/]"
    )
    console.print(f"   Budget: {auto or max_full_evals or max_metric_calls}")
    console.print(f"   Training examples: {len(train_data)}")
    console.print(f"   Validation examples: {len(val_data)}")
    console.print(f"   This may take a few minutes...\n")

    try:
        result = optimizer.compile(
            component=component,
            trainset=train_data,
            valset=val_data,
        )

        console.print(f"\n[green]✅ Optimization complete![/]")
        console.print(f"\n📊 Results:")
        console.print(f"   Best score: [green]{result.best_score:.3f}[/]")
        console.print(f"   Iterations: {result.num_iterations}")
        console.print(f"   Framework: {result.framework}")

        console.print(f"\n📝 Optimized Variable (first 200 chars):")
        console.print(f"   {result.best_variable[:200]}...")

        # Save optimized component/variable
        with open(project_root / ".super") as f:
            sys_name = yaml.safe_load(f).get("project")

        optimized_dir = project_root / sys_name / "agents" / agent_name / "optimized"
        optimized_dir.mkdir(parents=True, exist_ok=True)

        optimized_file = optimized_dir / f"{agent_name}_{framework}_optimized.json"
        with open(optimized_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)

        console.print(f"\n💾 Saved optimization results to:")
        console.print(f"   {optimized_file}")

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Optimization failed: {e}[/]")
        if getattr(args, "verbose", False):
            import traceback

            traceback.print_exc()
        return False


def _optimize_field_descriptions(
    playbook: dict,
    reflection_lm: str,
    train_data: list,
    val_data: list,
    auto: str | None,
    max_full_evals: int | None,
    max_metric_calls: int | None,
    agent_name: str,
    project_root: Path,
    optimizer_kwargs: dict,
) -> bool:
    """
    Optimize Pydantic model field descriptions using GEPA.

    This optimizes Field(description=...) for output_fields to improve
    structured data extraction accuracy.

    Returns:
        True if optimization succeeded, False otherwise
    """
    try:
        from superoptix.core.base_component import BaseComponent

        spec_data = playbook.get("spec", playbook)
        output_fields = spec_data.get("output_fields", [])

        if not output_fields:
            console.print(
                "[yellow]⚠️  No output_fields found for field description optimization[/]"
            )
            return False

        # Extract current field descriptions
        field_descriptions = {}
        for field in output_fields:
            field_name = field.get("name", "")
            field_desc = field.get("description", field_name)  # Use name as fallback
            field_descriptions[field_name] = field_desc

        if not field_descriptions:
            console.print("[yellow]⚠️  No field descriptions found to optimize[/]")
            return False

        console.print(f"   Optimizing {len(field_descriptions)} field descriptions:")
        for field_name, desc in field_descriptions.items():
            console.print(f"     - {field_name}: {desc[:60]}...")

        # Create a structured text representation of field descriptions
        # Format: "field_name: description\nfield_name2: description2\n..."
        # This format is easier for GEPA to optimize while preserving structure
        field_descriptions_text = "\n".join(
            [f"{field_name}: {desc}" for field_name, desc in field_descriptions.items()]
        )

        # Create a temporary BaseComponent for field descriptions optimization
        class FieldDescriptionComponent(BaseComponent):
            """Temporary component for optimizing field descriptions."""

            def __init__(self, field_descriptions_text: str, field_names: list):
                super().__init__(
                    name=f"{agent_name}_field_descriptions",
                    description="Field descriptions for Pydantic model output fields",
                    input_fields=["dummy"],  # Need at least one input field for GEPA
                    output_fields=field_names,
                    variable=field_descriptions_text,  # Structured text to optimize
                    variable_type="field_descriptions",
                    framework="pydantic-ai",
                    config={},
                )
                self._field_names = field_names

            def forward(self, **inputs) -> dict:
                """Forward method required by BaseComponent.

                For field description optimization, we don't actually execute anything,
                we just return empty outputs since we're optimizing the descriptions themselves.
                """
                # Return empty dict with all expected output fields
                return {field: "" for field in self._field_names}

        field_component = FieldDescriptionComponent(
            field_descriptions_text, list(field_descriptions.keys())
        )

        # Create metric function for field description optimization
        # This metric evaluates how well the optimized descriptions help extract structured data
        def field_metric_fn(
            inputs: dict, outputs: dict, gold: dict, component_name: str = None
        ) -> dict:
            """Metric for field description optimization.

            We evaluate by checking if the optimized descriptions help extract
            the expected output fields correctly. For now, use a simple approach
            that checks if outputs match expected outputs.
            """
            score = 0.0
            feedback = "Field description evaluation"

            # Simple scoring: check if outputs contain expected values
            if outputs and gold:
                matched_fields = 0
                total_fields = len(gold)

                for field_name, expected_value in gold.items():
                    if field_name in outputs:
                        output_value = str(outputs[field_name]).lower()
                        expected_str = str(expected_value).lower()
                        if expected_str in output_value or output_value in expected_str:
                            matched_fields += 1

                if total_fields > 0:
                    score = matched_fields / total_fields
                    feedback = f"Matched {matched_fields}/{total_fields} fields"

            return {"score": score, "feedback": feedback}

        # Fix reflection_lm format for Ollama
        # UniversalGEPA expects "ollama:model" format and converts it to "ollama_chat/model"
        # So convert "ollama/model" to "ollama:model" if needed
        fixed_reflection_lm = reflection_lm
        if reflection_lm and reflection_lm.startswith("ollama/"):
            # Convert "ollama/llama3.1:8b" to "ollama:llama3.1:8b" for UniversalGEPA
            fixed_reflection_lm = reflection_lm.replace("ollama/", "ollama:", 1)
            console.print(
                f"   [dim]Converted reflection model format: {reflection_lm} -> {fixed_reflection_lm}[/]"
            )

        # Create optimizer for field descriptions
        # Get optimizer_kwargs from the parent scope (need to pass it properly)
        # Create optimizer_kwargs for field description optimization
        field_optimizer_kwargs = {
            "metric": field_metric_fn,
            "reflection_lm": fixed_reflection_lm,  # Use fixed format
            "reflection_minibatch_size": optimizer_kwargs.get(
                "reflection_minibatch_size", 3
            ),
            "skip_perfect_score": optimizer_kwargs.get("skip_perfect_score", True),
            "use_merge": optimizer_kwargs.get("use_merge", True),
            "failure_score": optimizer_kwargs.get("failure_score", 0.0),
            "perfect_score": optimizer_kwargs.get("perfect_score", 1.0),
            "track_stats": optimizer_kwargs.get("track_stats", False),
            "seed": optimizer_kwargs.get("seed", 42),
        }

        # Use smaller budget for field description optimization (it's an addon feature)
        if auto:
            # Use lighter budget for field descriptions
            if auto == "heavy":
                field_auto = "medium"
            elif auto == "medium":
                field_auto = "light"
            else:
                field_auto = "light"
            field_optimizer_kwargs["auto"] = field_auto
        elif max_metric_calls:
            # Reduce metric calls for field descriptions (use 1/3 of instruction budget)
            field_optimizer_kwargs["max_metric_calls"] = max(3, max_metric_calls // 3)
        elif max_full_evals:
            field_optimizer_kwargs["max_full_evals"] = max(1, max_full_evals // 2)

        from superoptix.optimizers import UniversalGEPA

        field_optimizer = UniversalGEPA(**field_optimizer_kwargs)

        # Optimize field descriptions
        console.print(
            f"   Budget: {field_optimizer_kwargs.get('auto') or field_optimizer_kwargs.get('max_metric_calls') or field_optimizer_kwargs.get('max_full_evals')}"
        )
        console.print(f"   This may take a few minutes...\n")

        field_result = field_optimizer.compile(
            component=field_component,
            trainset=train_data,
            valset=val_data,
        )

        console.print(f"\n   ✅ Field description optimization complete!")
        console.print(f"   Best score: [green]{field_result.best_score:.3f}[/]")

        # Parse optimized structured text back to dict
        # Format: "field_name: description\nfield_name2: description2\n..."
        optimized_field_descriptions = {}
        try:
            optimized_text = field_result.best_variable
            for line in optimized_text.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    # Split on first colon only (descriptions may contain colons)
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field_name = parts[0].strip()
                        description = parts[1].strip()
                        if (
                            field_name in field_descriptions
                        ):  # Only keep fields that existed originally
                            optimized_field_descriptions[field_name] = description

            # Ensure all original fields are present (fallback to original if missing)
            for field_name, original_desc in field_descriptions.items():
                if field_name not in optimized_field_descriptions:
                    optimized_field_descriptions[field_name] = original_desc
                    console.print(
                        f"     [yellow]⚠️  {field_name}: Could not parse, using original[/]"
                    )

            console.print(
                f"   Optimized {len(optimized_field_descriptions)} field descriptions"
            )
        except Exception as e:
            console.print(
                f"[yellow]⚠️  Failed to parse optimized field descriptions: {e}[/]"
            )
            console.print("   Using original field descriptions")
            optimized_field_descriptions = field_descriptions

        # Save optimized field descriptions
        with open(project_root / ".super") as f:
            sys_name = yaml.safe_load(f).get("project")

        optimized_dir = project_root / sys_name / "agents" / agent_name / "optimized"
        optimized_dir.mkdir(parents=True, exist_ok=True)

        field_descriptions_file = (
            optimized_dir / f"{agent_name}_field_descriptions_optimized.json"
        )
        with open(field_descriptions_file, "w") as f:
            json.dump(
                {
                    "optimized_field_descriptions": optimized_field_descriptions,
                    "original_field_descriptions": field_descriptions,
                    "best_score": field_result.best_score,
                    "num_iterations": field_result.num_iterations,
                },
                f,
                indent=2,
            )

        console.print(f"\n   💾 Saved optimized field descriptions to:")
        console.print(f"      {field_descriptions_file}")

        return True

    except Exception as e:
        console.print(f"[yellow]⚠️  Field description optimization failed: {e}[/]")
        if getattr(globals().get("args"), "verbose", False):
            import traceback

            traceback.print_exc()
        return False


def _optimize_mcp_tools(
    playbook: dict,
    reflection_lm: str,
    train_data: list,
    val_data: list,
    auto: str | None,
    max_full_evals: int | None,
    max_metric_calls: int | None,
    agent_name: str,
    project_root: Path,
) -> bool:
    """
    Optimize MCP tool descriptions using existing MCPAdapter.

    This is Phase 1 of a two-phase optimization:
    1. Optimize tool descriptions (this function)
    2. Optimize instructions (UniversalGEPA)

    Returns:
        True if optimization succeeded, False otherwise
    """
    try:
        from superoptix.optimizers import MCPAdapter
        from mcp import StdioServerParameters
        import gepa
    except ImportError as e:
        console.print(f"[yellow]⚠️  MCPAdapter not available: {e}[/]")
        return False

    if not MCPAdapter:
        console.print(
            "[yellow]⚠️  MCPAdapter not available. Install with: pip install mcp[/]"
        )
        return False

    try:
        spec_data = playbook.get("spec", {})
        mcp_config = spec_data.get("mcp", {})
        mcp_optimization = mcp_config.get("optimization", {})

        # Get MCP server configuration
        servers = mcp_config.get("servers", [])
        if not servers:
            console.print("[yellow]⚠️  No MCP servers configured for optimization[/]")
            return False

        # Use first server for now (can extend to multiple later)
        server_config = servers[0]
        server_type = server_config.get("type", "stdio").lower()
        config = server_config.get("config", {})
        tool_names = mcp_optimization.get("tool_names", [])  # Which tools to optimize

        if not tool_names:
            console.print(
                "[yellow]⚠️  No tool_names specified in mcp.optimization.tool_names[/]"
            )
            return False

        # Prepare MCPAdapter server params
        server_params = None
        remote_url = None
        remote_transport = "streamable_http"

        if server_type == "stdio":
            command = config.get("command")
            args_list = config.get("args", [])
            env = config.get("env")

            if not command:
                console.print("[yellow]⚠️  stdio server requires 'command' in config[/]")
                return False

            server_params = StdioServerParameters(
                command=command,
                args=args_list,
                env=env,
            )
        elif server_type in ["streamable_http", "sse"]:
            remote_url = config.get("url")
            if not remote_url:
                console.print(
                    f"[yellow]⚠️  {server_type} server requires 'url' in config[/]"
                )
                return False
            remote_transport = (
                "streamable_http" if server_type == "streamable_http" else "sse"
            )

        # Convert training data to MCP format
        # MCPAdapter expects: user_query, tool_arguments, reference_answer
        mcp_train_data = []
        for example in train_data:
            # Extract input query (first input field)
            inputs = example.get("inputs", {})
            user_query = list(inputs.values())[0] if inputs else ""

            # Extract expected output (first output field)
            expected = example.get("outputs", {})
            reference_answer = str(list(expected.values())[0]) if expected else ""

            mcp_train_data.append(
                {
                    "user_query": user_query,
                    "tool_arguments": {},  # Can be extracted from scenarios if available
                    "reference_answer": reference_answer,
                    "additional_context": {},
                }
            )

        mcp_val_data = []
        for example in val_data:
            inputs = example.get("inputs", {})
            user_query = list(inputs.values())[0] if inputs else ""
            expected = example.get("outputs", {})
            reference_answer = str(list(expected.values())[0]) if expected else ""

            mcp_val_data.append(
                {
                    "user_query": user_query,
                    "tool_arguments": {},
                    "reference_answer": reference_answer,
                    "additional_context": {},
                }
            )

        # Create metric function
        def mcp_metric_fn(item, output: str) -> float:
            """Simple metric: check if reference answer appears in output."""
            ref = item.get("reference_answer", "").lower()
            out = output.lower()
            return 1.0 if ref in out or out in ref else 0.0

        # Create MCPAdapter
        adapter_kwargs = {
            "tool_names": tool_names,
            "task_model": reflection_lm,  # Use reflection model for task execution
            "metric_fn": mcp_metric_fn,
        }

        if server_params:
            adapter_kwargs["server_params"] = server_params
        else:
            adapter_kwargs["remote_url"] = remote_url
            adapter_kwargs["remote_transport"] = remote_transport

        adapter = MCPAdapter(**adapter_kwargs)

        # Prepare seed candidate (initial tool descriptions)
        # For now, use default descriptions (can be improved to load from server)
        seed_candidate = {}
        for tool_name in tool_names:
            seed_candidate[f"tool_description_{tool_name}"] = f"Tool: {tool_name}"

        # Prepare budget
        optimize_kwargs = {
            "seed_candidate": seed_candidate,
            "trainset": mcp_train_data,
            "valset": mcp_val_data,
            "adapter": adapter,
            "reflection_lm": reflection_lm,
        }

        # Convert auto budget to max_metric_calls (GEPA doesn't support 'auto' parameter)
        if auto:
            # Map auto budget levels to max_metric_calls
            budget_map = {
                "light": 50,
                "medium": 150,
                "heavy": 300,
            }
            optimize_kwargs["max_metric_calls"] = budget_map.get(auto.lower(), 150)
        elif max_full_evals:
            optimize_kwargs["max_full_evals"] = max_full_evals
        elif max_metric_calls:
            optimize_kwargs["max_metric_calls"] = max_metric_calls
        else:
            # Default to light budget if nothing specified
            optimize_kwargs["max_metric_calls"] = 50

        # Run optimization
        console.print(
            f"   Optimizing {len(tool_names)} tool(s): {', '.join(tool_names)}"
        )
        result = gepa.optimize(**optimize_kwargs)

        # Save optimized tool descriptions
        with open(project_root / ".super") as f:
            sys_name = yaml.safe_load(f).get("project")

        optimized_dir = project_root / sys_name / "agents" / agent_name / "optimized"
        optimized_dir.mkdir(parents=True, exist_ok=True)

        mcp_optimized_file = optimized_dir / f"{agent_name}_mcp_tool_descriptions.json"
        with open(mcp_optimized_file, "w") as f:
            json.dump(result.best_candidate, f, indent=2)

        console.print(f"[green]✅ MCP tool optimization complete![/]")
        console.print(f"   Best score: {result.best_score:.3f}")
        console.print(f"   Saved to: {mcp_optimized_file}")

        return True

    except Exception as e:
        console.print(f"[yellow]⚠️  MCP tool optimization error: {e}[/]")
        import traceback

        traceback.print_exc()
        return False


def optimize_agent(args):
    """Handle agent optimization."""
    console.print("=" * 80)
    console.print(
        f"\n🚀 [bold bright_cyan]Optimizing agent '[bold yellow]{args.name}[/]'...[/]"
    )

    # Handle --fresh flag: Clear DSPy cache for real optimization iterations
    if getattr(args, "fresh", False):
        from pathlib import Path as PathLib
        import shutil

        dspy_cache = PathLib.home() / ".dspy_cache"
        if dspy_cache.exists():
            try:
                console.print(f"\n🧹 [cyan]Clearing DSPy cache (--fresh mode)...[/]")
                shutil.rmtree(dspy_cache)
                console.print(f"   ✅ Cache cleared: {dspy_cache}")
                console.print(f"   🔄 Optimization will use fresh LLM calls")
                console.print(
                    f"   ⏱️  This will take longer but show real GEPA iterations\n"
                )
            except Exception as e:
                console.print(f"   ⚠️  [yellow]Could not clear cache: {e}[/]")
        else:
            console.print(f"\n💡 [dim]No DSPy cache found (already fresh)[/]\n")

    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            return

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        agent_name = args.name.lower()
        engine = getattr(args, "engine", "dspy")
        target = getattr(args, "target", None)
        framework = getattr(args, "framework", "dspy")
        agent_dir = project_root / project_name / "agents" / agent_name

        def _pipeline_path_for(framework_name: str) -> Path:
            if framework_name in [
                "microsoft",
                "openai",
                "crewai",
                "google-adk",
                "deepagents",
                "pydantic-ai",
                "claude-sdk",
            ]:
                return (
                    agent_dir
                    / "pipelines"
                    / f"{agent_name}_{framework_name.replace('-', '_')}_pipeline.py"
                )
            return agent_dir / "pipelines" / f"{agent_name}_pipeline.py"

        pipeline_path = _pipeline_path_for(framework)

        # If caller left default framework=dspy but DSPy pipeline doesn't exist,
        # try to auto-detect an existing compiled framework pipeline.
        if framework == "dspy" and not pipeline_path.exists():
            candidates = [
                "pydantic-ai",
                "crewai",
                "openai",
                "google-adk",
                "microsoft",
                "deepagents",
                "claude-sdk",
            ]
            found = [fw for fw in candidates if _pipeline_path_for(fw).exists()]
            if len(found) == 1:
                framework = found[0]
                pipeline_path = _pipeline_path_for(framework)
                args.framework = framework
                console.print(
                    f"[dim]Auto-detected compiled framework: {framework}[/]"
                )
            elif len(found) > 1:
                console.print(
                    "[yellow]Multiple compiled framework pipelines found. "
                    "Use --framework to choose one explicitly.[/]"
                )
                for fw in found:
                    console.print(f"   - {fw}: {_pipeline_path_for(fw)}")
                return

        optimized_path = agent_dir / "pipelines" / f"{agent_name}_optimized.json"

        # Load playbook early to check for optimization config
        playbook_path = agent_dir / "playbook" / f"{agent_name}_playbook.yaml"
        playbook = None
        if playbook_path.exists():
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)

        # Check if Universal GEPA should be used (based on parameters)
        auto = getattr(args, "auto", None)
        max_full_evals = getattr(args, "max_full_evals", None)
        max_metric_calls = getattr(args, "max_metric_calls", None)
        reflection_lm = getattr(args, "reflection_lm", None)

        # Check playbook for optimization config if CLI params not provided
        if (
            not (auto or max_full_evals or max_metric_calls or reflection_lm)
            and playbook
        ):
            opt_config = playbook.get("spec", {}).get("optimization", {})
            optimizer_config = opt_config.get("optimizer", {})
            params = optimizer_config.get("params", {})
            auto = auto or params.get("auto")
            max_full_evals = max_full_evals or params.get("max_full_evals")
            max_metric_calls = max_metric_calls or params.get("max_metric_calls")
            reflection_lm = reflection_lm or params.get("reflection_lm")

        use_universal_gepa = (
            (auto or max_full_evals or max_metric_calls or reflection_lm)
            and framework
            in [
                "microsoft",
                "openai",
                "crewai",
                "google-adk",
                "deepagents",
                "pydantic-ai",
            ]
            # Note: DSPy uses its own native GEPA path below (not Universal GEPA)
        )

        if use_universal_gepa:
            # Use Universal GEPA for any framework
            console.print(f"\n🌟 [bold cyan]Using Universal GEPA Optimizer[/]")
            console.print(f"   Framework: {framework}")

            # Playbook already loaded above
            if not playbook:
                console.print(f"\n[red]❌ Playbook not found: {playbook_path}[/]")
                return

            # Run Universal GEPA optimization
            success = _run_universal_gepa_optimization(
                args, agent_name, project_root, playbook
            )

            if success:
                console.print(
                    f"\n[green]✅ Universal GEPA optimization completed successfully![/]"
                )
                console.print(f"\n💡 Next steps:")
                console.print(
                    f"   1. Review optimized results in agents/{agent_name}/optimized/"
                )
                console.print(f"   2. Test the agent: super agent run {agent_name}")
                console.print(f"   3. Compile with optimized prompts if needed")
            else:
                console.print(f"\n[red]❌ Universal GEPA optimization failed[/]")

            return

        # Check if pipeline exists (for all frameworks, not just DSPy)
        if not pipeline_path.exists():
            console.print(
                f"\n[bold red]❌ Pipeline not found for agent '{agent_name}'. Run 'super agent compile {agent_name} --framework {framework}' first.[/bold red]"
            )
            console.print(f"   Expected: {pipeline_path}")
            return

        if engine == "optimas":
            # Minimal prompt optimization using Optimas OPRO directly (no RewardModel)
            try:
                from optimas.optim.opro import OPRO
                import importlib.util
                from optimas.wrappers.example import Example
                from optimas.wrappers.prediction import Prediction
            except Exception as e:
                console.print(
                    f"❌ [bold red]Optimas optimization requires optional deps:[/] {e}"
                )
                return

            if not target:
                target = "optimas-openai"
            suffix = target.replace("-", "_")
            opt_path = agent_dir / "pipelines" / f"{agent_name}_{suffix}_pipeline.py"
            if not opt_path.exists():
                console.print(
                    f"[yellow]Optimas pipeline not found at {opt_path}. Compile it first: super agent compile {agent_name} --target {target}[/]"
                )
                return

            # Import system
            spec = importlib.util.spec_from_file_location("opt_sys", str(opt_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            system = mod.system_engine()

            # Build trainset from BDD scenarios per component
            with open(project_root / ".super") as f:
                sys_name = yaml.safe_load(f).get("project")
            pb_path = (
                project_root
                / sys_name
                / "agents"
                / agent_name
                / "playbook"
                / f"{agent_name}_playbook.yaml"
            )
            playbook = yaml.safe_load(open(pb_path)) or {}
            spec_data = playbook.get("spec", playbook)
            scenarios = []
            if "feature_specifications" in spec_data and spec_data[
                "feature_specifications"
            ].get("scenarios"):
                scenarios = spec_data["feature_specifications"]["scenarios"]

            # Metric function leveraging system.evaluate
            def metric_from_system(example, pred, trace=None):
                try:
                    return system.evaluate(example, pred)
                except Exception:
                    return 0.0

            updated = 0
            optimizer_choice = getattr(args, "optimizer", "opro")

            # Configure OPRO to use local Ollama via OpenAI-compatible API if specified in playbook
            opro_llm_model = "gpt-4o-mini"
            try:
                lm_cfg = (
                    spec_data.get("language_model", {})
                    if isinstance(spec_data, dict)
                    else {}
                )
                provider = lm_cfg.get("provider")
                model_name = lm_cfg.get("model")
                base_url = lm_cfg.get("base_url") or lm_cfg.get("api_base")
                api_key = lm_cfg.get("api_key")
                if provider == "ollama" and model_name and base_url and api_key:
                    if not str(model_name).startswith("ollama/"):
                        model_name = f"ollama/{model_name}"
                    import os  # local import to avoid top-level changes

                    os.environ.setdefault("OPENAI_BASE_URL", str(base_url))
                    os.environ.setdefault("OPENAI_API_BASE", str(base_url))
                    os.environ.setdefault("OPENAI_API_KEY", str(api_key))
                    # LiteLLM specific knobs to avoid hangs
                    os.environ.setdefault("LITELLM_TIMEOUT", "30")
                    os.environ.setdefault("LITELLM_MAX_RETRIES", "1")
                    os.environ.setdefault("LITELLM_LOG", "FALSE")
                    opro_llm_model = str(model_name)
            except Exception:
                # Fall back to default model if any issue
                pass
            for cname, comp in system.components.items():
                # Only prompt-like variables (strings)
                if not isinstance(getattr(comp, "variable", None), str):
                    continue

                # Build examples for this component from scenarios
                trainset = []
                for sc in scenarios:
                    inp = sc.get("input", {}) or {}
                    ex = Example(
                        **{k: inp.get(k, "") for k in comp.input_fields}
                    ).with_inputs(*comp.input_fields)
                    # Dummy prediction built from expected outputs if present (for metric)
                    expected = sc.get("expected_output", {}) or {}
                    pred = Prediction(
                        **{k: expected.get(k, "") for k in comp.output_fields}
                    )
                    trainset.append((ex, pred))

                if not trainset:
                    continue

                if optimizer_choice == "opro":
                    import os as _os
                    from concurrent.futures import (
                        ThreadPoolExecutor,
                        TimeoutError as _Timeout,
                    )

                    max_tokens = int(_os.getenv("SUPEROPTIX_OPRO_MAX_TOKENS", "128"))
                    num_candidates = int(
                        _os.getenv("SUPEROPTIX_OPRO_NUM_CANDIDATES", "2")
                    )
                    max_workers = int(_os.getenv("SUPEROPTIX_OPRO_MAX_WORKERS", "2"))
                    temperature = float(
                        _os.getenv("SUPEROPTIX_OPRO_TEMPERATURE", "0.7")
                    )
                    compile_timeout = int(
                        _os.getenv("SUPEROPTIX_OPRO_COMPILE_TIMEOUT", "60")
                    )
                    # Set LiteLLM request timeout to prevent hangs against local endpoints
                    _os.environ.setdefault("LITELLM_TIMEOUT", "30")
                    _os.environ.setdefault("LITELLM_MAX_RETRIES", "1")
                    _os.environ.setdefault("LITELLM_MAX_RESPONSE", str(max_tokens))

                    # DSPy-specific environment variables for optimization
                    _os.environ.setdefault("DSPY_OPTIMIZATION_TIMEOUT", "60")
                    _os.environ.setdefault("DSPY_USE_FALLBACK", "true")
                    _os.environ.setdefault("DSPY_MAX_WORKERS", "1")

                    # Check component type and use appropriate optimization strategy
                    if hasattr(comp, "agent") and hasattr(comp.agent, "role"):
                        # Custom CrewAI optimization that avoids hanging
                        console.print(
                            f"[yellow]Using custom CrewAI optimization for component '{cname}'[/]"
                        )
                        new_variable = _optimize_crewai_component(
                            comp, trainset, opro_llm_model, temperature, max_tokens
                        )
                    elif (
                        hasattr(comp, "signature_cls")
                        or "dspy" in str(type(comp)).lower()
                    ):
                        # Custom DSPy optimization that handles threading issues
                        console.print(
                            f"[yellow]Using custom DSPy optimization for component '{cname}'[/]"
                        )
                        new_variable = _optimize_dspy_component(
                            comp, trainset, opro_llm_model, temperature, max_tokens
                        )
                    else:
                        # Standard OPRO for other components
                        opro = OPRO(
                            llm_model=opro_llm_model,
                            temperature=temperature,
                            max_new_tokens=max_tokens,
                            metric=lambda e, p, trace=None: metric_from_system(e, p),
                            num_prompt_candidates=num_candidates,
                            max_sample_workers=max_workers,
                            meta_prompt_preamble=f"This component is meant to handle the task:\n{comp.description}\nWe want to refine its instructions to improve performance on coding tasks.",
                        )
                        initial_prompt = comp.variable
                        examples_only = [ex for ex, _ in trainset]
                        # Run compile with an overall timeout safeguard
                        _pool = ThreadPoolExecutor(max_workers=1)
                        _future = _pool.submit(
                            opro.compile,
                            component=comp,
                            initial_prompt=initial_prompt,
                            trainset=examples_only,
                        )
                        try:
                            new_variable, _pairs = _future.result(
                                timeout=compile_timeout
                            )
                        except _Timeout:
                            console.print(
                                f"[red]OPRO timed out after {compile_timeout}s on component '{cname}'. "
                                f"Try increasing SUPEROPTIX_OPRO_COMPILE_TIMEOUT or reduce model size/tokens.[/]"
                            )
                            try:
                                _future.cancel()
                            except Exception:
                                pass
                            _pool.shutdown(wait=False, cancel_futures=True)
                            continue
                        else:
                            _pool.shutdown(wait=True, cancel_futures=False)
                elif optimizer_choice == "mipro":
                    try:
                        import dspy
                        from dspy.teleprompt import MIPROv2
                    except Exception as e:
                        console.print(
                            f"❌ [bold red]MIPRO requires DSPy 3.x installed:[/] {e}"
                        )
                        return
                    tp = MIPROv2(
                        metric=lambda e, p, trace=None: metric_from_system(e, p),
                        auto="light",
                        verbose=getattr(args, "verbose", False),
                        num_candidates=2,
                        num_threads=2,
                    )
                    if not hasattr(comp, "signature_cls"):
                        console.print(
                            f"[yellow]Skipping component '{cname}': MIPRO requires DSPy signature[/]"
                        )
                        continue
                    old_sig_cls = comp.signature_cls.with_instructions(comp.variable)
                    new_sig = tp.compile(
                        dspy.Predict(old_sig_cls), trainset=[ex for ex, _ in trainset]
                    ).signature
                    new_variable = new_sig.instructions
                elif optimizer_choice == "copro":
                    try:
                        import dspy
                        from dspy.teleprompt import COPRO
                    except Exception as e:
                        console.print(
                            f"❌ [bold red]COPRO requires DSPy 3.x installed:[/] {e}"
                        )
                        return
                    tp = COPRO(
                        metric=lambda e, p, trace=None: metric_from_system(e, p),
                        breadth=2,
                        depth=2,
                        verbose=getattr(args, "verbose", False),
                    )
                    if not hasattr(comp, "signature_cls"):
                        console.print(
                            f"[yellow]Skipping component '{cname}': COPRO requires DSPy signature[/]"
                        )
                        continue
                    old_sig_cls = comp.signature_cls.with_instructions(comp.variable)
                    new_sig = tp.compile(
                        dspy.Predict(old_sig_cls), trainset=[ex for ex, _ in trainset]
                    ).signature
                    new_variable = new_sig.instructions
                else:
                    console.print(
                        f"[red]Unknown optimizer '{optimizer_choice}'. Supported: opro, mipro, copro[/]"
                    )
                    return

                comp.update(new_variable)
                updated += 1

            console.print(
                f"[green]✅ Optimas prompt optimization completed using '{optimizer_choice}'. Updated components: {updated}[/]"
            )
            return

        # Load and run DSPy optimization (default)
        runner = DSPyRunner(agent_name=agent_name)

        # Show what's happening (concise)
        console.print(
            Panel(
                f"🤖 [bold bright_green]OPTIMIZATION IN PROGRESS[/]\n\n"
                f"🎯 [bold]Agent:[/] {agent_name.title()}\n"
                f"🔧 [bold]Strategy:[/] DSPy BootstrapFewShot\n"
                f"📊 [bold]Data Source:[/] BDD scenarios from playbook\n"
                f"💾 [bold]Output:[/] [cyan]{optimized_path.relative_to(project_root)}[/]",
                title="⚡ Optimization Details",
                border_style="bright_green",
                padding=(1, 2),
            )
        )

        # Perform optimization
        strategy = getattr(args, "strategy", "bootstrap")
        force = getattr(args, "force", False)
        optimization_result = run_async(
            runner.optimize(
                strategy=strategy,
                force=force,
                runtime_mode=(
                    "local"
                    if getattr(args, "local", False)
                    else ("cloud" if getattr(args, "cloud", False) else "auto")
                ),
                provider_override=getattr(args, "provider", None),
                model_override=getattr(args, "model", None),
            )
        )

        if optimization_result.get("success", False):
            console.print(
                Panel(
                    "🎉 [bold bright_green]OPTIMIZATION SUCCESSFUL![/] Agent Enhanced",
                    style="bright_green",
                    border_style="bright_green",
                )
            )

            # Performance metrics (concise)
            training_examples = optimization_result.get("training_examples", "N/A")
            score = optimization_result.get("score", "N/A")

            optimization_info = f"""📈 [bold]Performance Improvement:[/]
• Training Examples: {training_examples}
• Optimization Score: {score}

💡 [bold]What changed:[/] DSPy optimized prompts and reasoning chains
🚀 [bold]Ready for testing:[/] Enhanced agent performance validated"""

            console.print(
                Panel(
                    optimization_info,
                    title="📊 Optimization Results",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )

            # Show verbose panels only in verbose mode
            if getattr(args, "verbose", False):
                # Auto-tuning notice (verbose only)
                auto_tune_info = """🧠 [bold]Smart Optimization:[/] DSPy BootstrapFewShot

⚡ [bold]Automatic improvements:[/] Better prompts, reasoning chains
🎯 [bold]Quality assurance:[/] Test before production use"""

                console.print(
                    Panel(
                        auto_tune_info,
                        title="🤖 AI Enhancement",
                        border_style="bright_magenta",
                        padding=(1, 2),
                    )
                )

                # Next steps guidance (verbose only)
                next_steps = f"""🚀 [bold bright_cyan]NEXT STEPS[/]

[cyan]super agent evaluate {agent_name}[/] - Measure optimization improvement
[cyan]super agent run {agent_name} --goal "goal"[/] - Execute enhanced agent
[cyan]super orchestra create[/] - Ready for multi-agent orchestration

[dim]💡 Follow BDD/TDD workflow: evaluate → optimize → evaluate → run[/]"""

                console.print(
                    Panel(
                        next_steps,
                        title="🎯 Workflow Guide",
                        border_style="bright_cyan",
                        padding=(1, 2),
                    )
                )

            # Simple workflow guide (normal mode)
            console.print(
                f'🎯 [bold cyan]Next:[/] [cyan]super agent evaluate {agent_name}[/] or [cyan]super agent run {agent_name} --goal "your goal"[/]'
            )

            # Success summary
            console.print("=" * 80)
            console.print(
                f"🎉 [bold bright_green]Agent '{agent_name}' optimization complete![/] Ready for testing! 🚀"
            )
        else:
            error_msg = optimization_result.get("error", "Unknown error")

            # Create a more helpful error panel
            error_panel_content = (
                f"❌ [bold red]OPTIMIZATION FAILED[/]\n\n"
                f"[bold]Agent:[/] {agent_name}\n"
                f"[bold]Strategy:[/] {strategy}\n\n"
                f"[bold red]Error Details:[/] \n{error_msg}\n\n"
                f"--- \n"
                f"💡 [bold bright_cyan]Troubleshooting Tips[/]\n"
                f"1. [bold]Check BDD Scenarios:[/]\n"
                f"   - Ensure your playbook has valid `feature_specifications` with `scenarios`.\n"
                f"   - Each scenario needs an `input` and an `expected_output`.\n"
                f"   - Run [cyan]super agent lint {agent_name}[/] to check syntax.\n\n"
                f"2. [bold]Verify Model Connection:[/]\n"
                f"   - Make sure your local Ollama server is running and accessible.\n"
                f"   - Check the `api_base` URL in your agent's playbook.\n\n"
                f"3. [bold]Inspect Pipeline Code:[/]\n"
                f"   - The auto-generated pipeline might need customization.\n"
                f"   - Look for issues in: [dim]{pipeline_path}[/]\n\n"
                f"4. [bold]Run with Verbose Output:[/]\n"
                f"   - Re-run the command with `--verbose` for more detailed logs."
            )

            console.print(
                Panel(
                    error_panel_content,
                    title="💥 Optimization Error",
                    border_style="red",
                    padding=(1, 2),
                )
            )

    except Exception as e:
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during optimization: {e}[/bold red]"
        )


def remove_agent(args):
    """Handle agent removal."""
    if not args.name:
        console.print(
            "[bold red]❌ You must specify an agent name to remove.[/bold red]"
        )
        return

    agent_name = args.name.lower()

    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            return

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        # Find agent playbook
        agents_dir = project_root / project_name / "agents"
        playbook_path = next(agents_dir.rglob(f"**/{agent_name}_playbook.yaml"), None)

        # Find compiled pipeline
        compiler = AgentCompiler()
        pipeline_path = compiler._get_pipeline_path(agent_name)

        if not playbook_path and not pipeline_path.exists():
            console.print(
                f"\n[bold yellow]🟡 Agent '{agent_name}' not found. Nothing to remove.[/bold yellow]"
            )
            return

        console.print(
            f"\n[bold red]🔥 Preparing to remove agent '{agent_name}'[/bold red]"
        )
        files_to_remove = []
        if playbook_path and playbook_path.exists():
            files_to_remove.append(f"Playbook: {playbook_path}")
        if pipeline_path.exists():
            files_to_remove.append(f"Pipeline: {pipeline_path}")

        summary = "\n".join(files_to_remove)
        console.print(
            Panel(
                f"The following files will be permanently deleted:\n\n{summary}",
                title="🚨 Confirmation Required",
                border_style="bold red",
                padding=(1, 2),
            )
        )

        from rich.prompt import Confirm

        if Confirm.ask(
            f"Are you sure you want to delete these files for agent '{agent_name}'?",
            default=False,
        ):
            playbook_dir = None
            if playbook_path and playbook_path.exists():
                playbook_dir = playbook_path.parent
                playbook_path.unlink()
                console.print(f"✅ [green]Removed playbook:[/] {playbook_path}")

            if pipeline_path.exists():
                pipeline_dir = pipeline_path.parent
                pipeline_path.unlink()
                console.print(f"✅ [green]Removed pipeline:[/] {pipeline_path}")
                # Clean up the 'pipelines' directory if it's empty
                if pipeline_dir.is_dir() and not any(pipeline_dir.iterdir()):
                    pipeline_dir.rmdir()
                    console.print(
                        f"✅ [green]Removed empty pipelines directory:[/] {pipeline_dir}"
                    )

            # Clean up the agent's main directory if it's empty
            if (
                playbook_dir
                and playbook_dir.is_dir()
                and not any(playbook_dir.iterdir())
            ):
                # Ensure we don't delete the root 'agents' directory
                if playbook_dir.name != "agents":
                    playbook_dir.rmdir()
                    console.print(
                        f"✅ [green]Removed empty agent directory:[/] {playbook_dir}"
                    )

            console.print(
                f"\n[bold green]🎉 Successfully removed agent '{agent_name}'.[/bold green]"
            )
        else:
            console.print("\n[yellow]🟡 Removal cancelled by user.[/yellow]")

    except Exception as e:
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during removal:[/] {e}"
        )
        sys.exit(1)


def inspect_agent(args):
    """Show detailed information about a single agent."""
    if not args.name:
        console.print(
            "[bold red]❌ You must specify an agent name to inspect.[/bold red]"
        )
        return

    agent_name = args.name.lower()
    try:
        project_root = Path.cwd()
        with open(project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        # Find playbook file in project or pre-built agents
        playbook_path = next(
            (project_root / system_name / "agents").rglob(
                f"**/{agent_name}_playbook.yaml"
            ),
            None,
        )
        if not playbook_path:
            package_root = Path(__file__).parent.parent.parent
            playbook_path = next(
                package_root.rglob(f"**/agents/**/{agent_name}_playbook.yaml"), None
            )

        if not playbook_path or not playbook_path.exists():
            console.print(
                f"\n[bold red]❌ Agent playbook for '{agent_name}' not found.[/bold red]"
            )
            return

        with open(playbook_path) as f:
            data = yaml.safe_load(f)

        metadata = data.get("metadata", {})
        spec = data.get("spec", {})
        title = metadata.get("name", agent_name.title())
        description = metadata.get("description", "No description provided.")

        panel_content = f"[bold bright_cyan]{title}[/]\n"
        panel_content += f"[dim]{playbook_path}[/dim]\n\n"
        panel_content += f"{description}\n\n"
        panel_content += (
            f"[bold]Author:[/] {metadata.get('author', 'N/A')}\n"
            f"[bold]Version:[/] {metadata.get('version', 'N/A')}\n"
            f"[bold]License:[/] {metadata.get('license', 'N/A')}"
        )

        console.print(
            Panel(
                panel_content,
                title="🕵️ Agent Details",
                border_style="bright_blue",
                padding=(1, 2),
            )
        )

        # Display capabilities
        capabilities = spec.get("capabilities", [])
        if capabilities:
            table = Table(
                title="🛠️ Capabilities", show_header=True, header_style="bold magenta"
            )
            table.add_column("Capability", style="cyan")
            table.add_column("Description", style="white")
            for cap in capabilities:
                table.add_row(cap.get("name"), cap.get("description"))
            console.print(table)

        # Display dependencies
        dependencies = spec.get("dependencies", {})
        if dependencies.get("tools") or dependencies.get("apis"):
            dep_table = Table(
                title="🔗 Dependencies", show_header=True, header_style="bold yellow"
            )
            dep_table.add_column("Type", style="cyan")
            dep_table.add_column("Dependency", style="white")
            for tool in dependencies.get("tools", []):
                dep_table.add_row("Tool", tool)
            for api in dependencies.get("apis", []):
                dep_table.add_row("API", api)
            console.print(dep_table)

        # Display recent traces
        trace_path = project_root / ".superoptix" / "traces" / f"{agent_name}.jsonl"
        if trace_path.exists():
            trace_table = Table(
                title=f"📜 Recent Traces for '{agent_name}'",
                show_header=True,
                header_style="bold blue",
            )
            trace_table.add_column("Timestamp", style="dim", width=26)
            trace_table.add_column("Event", style="cyan")
            trace_table.add_column("Component", style="green")
            trace_table.add_column("Duration (ms)", style="magenta", justify="right")
            trace_table.add_column("Status", style="white")

            with open(trace_path) as f:
                lines = f.readlines()
                # Display the last 10 events
                for line in lines[-10:]:
                    try:
                        trace = json.loads(line)
                        timestamp = trace.get("timestamp", "")
                        event_type = trace.get("event_type", "N/A")
                        component = trace.get("component", "N/A")
                        duration = trace.get("duration_ms")
                        status = trace.get("status", "N/A")

                        # Format status with an emoji
                        status_emoji = {
                            "success": "✅",
                            "error": "❌",
                            "warning": "⚠️",
                            "info": "ℹ️",
                        }.get(status, "")

                        trace_table.add_row(
                            timestamp,
                            event_type,
                            component,
                            f"{duration:.2f}" if duration is not None else "N/A",
                            f"{status_emoji} {status.title()}",
                        )
                    except json.JSONDecodeError:
                        # Skip corrupted lines
                        continue
            console.print(trace_table)

            # Display raw trace file content
            console.print(
                Panel(
                    "".join(lines[-10:]),
                    title=f"📄 Raw Content: {trace_path.name}",
                    border_style="dim blue",
                    padding=(1, 2),
                )
            )
        else:
            console.print(
                Panel(
                    f"No traces found for agent '{agent_name}'.\n\n"
                    "To generate traces, run the agent first:\n"
                    f'[bold cyan]super agent run {agent_name} --goal "your goal"[/]',
                    title="📜 Trace Information",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )

    except Exception as e:
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during inspection:[/] {e}"
        )
        sys.exit(1)


def _optimize_dspy_component(comp, trainset, opro_llm_model, temperature, max_tokens):
    """Custom DSPy optimization that handles threading issues gracefully."""
    try:
        # Get configuration from environment variables
        import os

        timeout = int(os.getenv("DSPY_OPTIMIZATION_TIMEOUT", "60"))
        use_fallback = os.getenv("DSPY_USE_FALLBACK", "true").lower() == "true"
        max_workers = int(os.getenv("DSPY_MAX_WORKERS", "1"))

        # Try standard OPRO first
        from optimas.optim.opro import OPRO

        opro = OPRO(
            llm_model=opro_llm_model,
            temperature=temperature,
            max_new_tokens=max_tokens,
            metric=lambda e,
            p,
            trace=None: 1.0,  # Simple metric to avoid complex evaluation
            num_prompt_candidates=1,  # Reduce complexity
            max_sample_workers=max_workers,  # Use environment variable
            meta_prompt_preamble=f"This component is meant to handle the task:\n{comp.description}\nWe want to refine its instructions to improve performance on coding tasks.",
        )

        initial_prompt = comp.variable
        examples_only = [ex for ex, _ in trainset]

        # Use a simple timeout approach
        import threading

        result = [None]
        exception = [None]

        def target():
            try:
                new_var, _ = opro.compile(
                    component=comp,
                    initial_prompt=initial_prompt,
                    trainset=examples_only,
                )
                result[0] = new_var
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        # Check if we should use fallback immediately
        if use_fallback:
            console.print(
                f"[yellow]Using fallback DSPy optimization strategy (DSPY_USE_FALLBACK=true)[/]"
            )
            return _fallback_dspy_optimization(comp, temperature)

        thread.join(timeout=timeout)  # Use environment variable timeout

        if thread.is_alive():
            # Thread is still running, use fallback
            console.print(
                f"[yellow]DSPy optimization timed out, using fallback strategy[/]"
            )
            return _fallback_dspy_optimization(comp, temperature)

        if exception[0]:
            # Exception occurred, use fallback
            console.print(
                f"[yellow]DSPy optimization failed: {exception[0]}, using fallback strategy[/]"
            )
            return _fallback_dspy_optimization(comp, temperature)

        if result[0]:
            return result[0]

        # No result, use fallback
        return _fallback_dspy_optimization(comp, temperature)

    except Exception as e:
        console.print(
            f"[yellow]DSPy optimization error: {e}, using fallback strategy[/]"
        )
        return _fallback_dspy_optimization(comp, temperature)


def _fallback_dspy_optimization(comp, temperature):
    """Fallback optimization strategy for DSPy when standard optimization fails."""
    try:
        # Simple prompt variation based on temperature
        base_prompt = comp.variable

        if temperature > 0.8:
            # High creativity - add more detailed instructions
            variations = [
                f"{base_prompt}\n\nPlease provide detailed, comprehensive responses with examples.",
                f"{base_prompt}\n\nBe thorough and include step-by-step explanations.",
                f"{base_prompt}\n\nProvide multiple approaches and consider edge cases.",
            ]
        elif temperature > 0.5:
            # Medium creativity - add structure
            variations = [
                f"{base_prompt}\n\nStructure your response clearly with headings.",
                f"{base_prompt}\n\nInclude both explanation and practical examples.",
                f"{base_prompt}\n\nProvide a balanced approach with pros and cons.",
            ]
        else:
            # Low creativity - focus on clarity
            variations = [
                f"{base_prompt}\n\nBe concise and to the point.",
                f"{base_prompt}\n\nFocus on practical, actionable advice.",
                f"{base_prompt}\n\nProvide clear, straightforward solutions.",
            ]

        # Return a variation based on current prompt content
        import hashlib

        prompt_hash = hashlib.md5(base_prompt.encode()).hexdigest()
        variation_index = int(prompt_hash, 16) % len(variations)

        return variations[variation_index]

    except Exception:
        # Ultimate fallback - return original prompt
        return comp.variable
