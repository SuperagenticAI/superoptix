import sys
from datetime import datetime
from pathlib import Path

import click
import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table

from superoptix.cli.utils import run_async
from superoptix.models.base_models import (
    AgentTier,
    TierFeatures,
    TierValidator,
)
from superoptix.runners.orchestra_runner import EnhancedOrchestraRunner

console = Console()


def _get_project_agents(project_name: str, project_root: Path) -> list[str]:
    """Scans the project for existing agent playbook references."""
    agents = []
    agents_dir = project_root / project_name / "agents"
    if not agents_dir.exists():
        return []

    playbook_files = sorted(list(agents_dir.rglob("*_playbook.yaml")))
    for playbook_file in playbook_files:
        # The agent's reference ID is the name of the playbook file without the suffix.
        agent_ref = playbook_file.stem.replace("_playbook", "")
        agents.append(agent_ref)
    return agents


def _load_agent_tasks(
    project_name: str, project_root: Path, agent_names: list[str]
) -> list[dict]:
    """Load tasks from agent playbooks."""
    agent_tasks = []
    agents_dir = project_root / project_name / "agents"

    for agent_name in agent_names:
        try:
            playbook_path = (
                agents_dir / agent_name / "playbook" / f"{agent_name}_playbook.yaml"
            )
            if not playbook_path.exists():
                # Try alternative path structure
                playbook_files = list(
                    agents_dir.rglob(f"**/{agent_name}_playbook.yaml")
                )
                if playbook_files:
                    playbook_path = playbook_files[0]
                else:
                    continue

            with open(playbook_path, "r") as f:
                playbook = yaml.safe_load(f)

            spec = playbook.get("spec", {})
            tasks = spec.get("tasks", [])

            for task in tasks:
                task_name = task.get("name", f"{agent_name}_task")
                instruction = task.get("instruction", "")

                # Create a meaningful description from the instruction
                if instruction:
                    # Clean up the instruction to make it suitable for orchestra description
                    description = instruction.replace("You are a ", "").replace(
                        "You are an ", ""
                    )
                    if "Think through" in description:
                        description = description.split("Think through")[1].strip()
                    if "systematically" in description:
                        description = description.replace("systematically", "").strip()
                    # Clean up any remaining redundant phrases
                    description = description.replace(
                        f"{agent_name.replace('_', ' ').title()}.", ""
                    ).strip()
                    if description.endswith("."):
                        description = description[:-1]
                    # Make it goal-oriented - use template placeholder instead of Python variable
                    description = f"Apply {agent_name.replace('_', ' ')} expertise to '{{goal}}'. {description}"
                else:
                    description = (
                        f"Execute {task_name.replace('_', ' ')} for '{{goal}}'"
                    )

                agent_tasks.append(
                    {
                        "agent_name": agent_name,
                        "task_name": task_name,
                        "description": description,
                    }
                )
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not load tasks from {agent_name}: {e}[/]"
            )
            continue

    return agent_tasks


def create_orchestra(args):
    """Create a new orchestra definition file, populating it with existing agents."""
    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            sys.exit(1)

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        orchestra_name = args.name.lower().replace(" ", "_")
        # Primary nested path: <project_root>/<project_name>/orchestras
        orchestras_dir = project_root / project_name / "orchestras"
        # Fallback to flat structure if nested does not exist
        if not orchestras_dir.exists():
            flat_dir = project_root / "orchestras"
            if flat_dir.exists():
                orchestras_dir = flat_dir

        orchestras_dir.mkdir(exist_ok=True)

        orchestra_file = orchestras_dir / f"{orchestra_name}_orchestra.yaml"
        if orchestra_file.exists():
            console.print(
                f"\n[bold red]❌ Orchestra '{orchestra_name}' already exists at:[/] {orchestra_file}"
            )
            sys.exit(1)

        # Intelligently find existing agents
        project_agents = _get_project_agents(project_name, project_root)
        if project_agents:
            console.print(
                f"🔎 Found {len(project_agents)} existing agent(s): {', '.join(project_agents)}. Adding them to the orchestra."
            )

            # Load tasks from agent playbooks
            agent_tasks = _load_agent_tasks(project_name, project_root, project_agents)
            if agent_tasks:
                console.print(
                    f"📝 Loaded {len(agent_tasks)} task(s) from agent playbooks."
                )
            else:
                console.print(
                    "⚠️  No tasks found in agent playbooks. Using default task structure."
                )
        else:
            console.print(
                "🤔 No existing agents found. Creating a default orchestra with placeholder agents."
            )
            agent_tasks = []

        # Prepare template context
        context = {
            "orchestra_name": orchestra_name,
            "project_name": project_name,
            "agent_tasks": agent_tasks,
            "execution_strategy": "sequential",  # Default for free version
            "max_parallel_tasks": 1,  # Default for free version - sequential only
            "task_timeout_seconds": 300,
            "timestamp": datetime.now().isoformat(),
        }

        package_root = Path(__file__).parent.parent.parent
        template_dir = package_root / "templates" / "orchestra"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("orchestra.yaml.jinja2")
        content = template.render(context)

        with open(orchestra_file, "w") as f:
            f.write(content)

        console.print(
            f"\n[bold green]✅ Created new orchestra definition at:[/] {orchestra_file.relative_to(project_root)}"
        )
        if agent_tasks:
            console.print(
                "[bold cyan]👉 Orchestra automatically configured with tasks from agent playbooks.[/bold cyan]"
            )
            console.print(
                f"[cyan]   Found {len(agent_tasks)} task(s): {', '.join([task['task_name'] for task in agent_tasks])}[/cyan]"
            )

        # Simple workflow guide (normal mode)
        console.print(
            f'🎯 [bold cyan]Next:[/] [cyan]super orchestra run {orchestra_name} --goal "your goal"[/]'
        )

        # Add helpful guidance about customization - only in verbose mode
        if getattr(args, "verbose", False):
            console.print("\n[bold yellow]💡 Customization Guidance:[/bold yellow]")
            console.print(
                "[yellow]   This is an automatic orchestra created based on your agent playbooks.[/yellow]"
            )
            console.print(
                "[yellow]   You should refine this orchestra based on your specific goal to make it more targeted.[/yellow]"
            )
            console.print("[yellow]   You can:[/yellow]")
            console.print(
                "[yellow]   • Add more agents that align with your goal[/yellow]"
            )
            console.print(
                "[yellow]   • Modify task descriptions to be more specific[/yellow]"
            )
            console.print(
                "[yellow]   • Adjust execution strategy (sequential/parallel)[/yellow]"
            )
            console.print("[yellow]   • Add dependencies between tasks[/yellow]")
            console.print("[yellow]   • Set custom timeouts and priorities[/yellow]")

            # Add version limitation information
            console.print("\n[bold blue]📋 Version Information:[/bold blue]")
            console.print(
                "[blue]   🆓 Free Version: Sequential execution strategy only[/blue]"
            )
            console.print(
                "[blue]   💎 Pro Version: Parallel, hierarchical, mixed strategies + Kubernetes orchestration[/blue]"
            )
            console.print(
                "[blue]   ℹ️  Orchestra kind 'basic' is supported in both versions[/blue]"
            )

            console.print(
                f'\n[cyan]🚀 Ready to run: super orchestra run {orchestra_name} --goal "your specific goal here"[/cyan]'
            )
            console.print(
                f"[cyan]📝 Edit file: {orchestra_file.relative_to(project_root)}[/cyan]"
            )

            # Add workflow guidance
            console.print(
                "\n[bold magenta]🎯 Orchestra Workflow Recommendations:[/bold magenta]"
            )
            console.print(
                "[magenta]   Before running this orchestra, ensure your agents are optimized:[/magenta]"
            )
            console.print(
                "[magenta]   1. Compile all agents: [cyan]super agent compile --all[/]"
            )
            console.print(
                "[magenta]   2. Evaluate baseline: [cyan]super agent evaluate <agent_name>[/]"
            )
            console.print(
                "[magenta]   3. Optimize agents: [cyan]super agent optimize <agent_name>[/]"
            )
            console.print(
                "[magenta]   4. Re-evaluate improvement: [cyan]super agent evaluate <agent_name>[/]"
            )
            console.print(
                f'[magenta]   5. Then run orchestra: [cyan]super orchestra run {orchestra_name} --goal "goal"[/]'
            )
            console.print()
            console.print(
                "[dim]💡 Well-optimized individual agents lead to better orchestration results![/]"
            )

    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to create orchestra:[/] {e}")
        sys.exit(1)


def list_orchestras(args):
    """List all available orchestras in the project."""
    try:
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print(
                "\n[bold red]❌ Not a valid super project. Run 'super init <project_name>' to get started.[/bold red]"
            )
            sys.exit(1)

        with open(super_file) as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        # Prefer nested structure; fallback to flat
        orchestras_dir = project_root / project_name / "orchestras"
        if not orchestras_dir.exists():
            flat_dir = project_root / "orchestras"
            if flat_dir.exists():
                orchestras_dir = flat_dir

        if not orchestras_dir.exists() or not any(orchestras_dir.iterdir()):
            console.print(
                f"\n[yellow]No orchestras found in project '{project_name}'.[/yellow]"
            )
            console.print(
                "[cyan]💡 Use 'super orchestra create <orchestra_name>' to create a new one.[/cyan]"
            )
            return

        orchestra_files = sorted(list(orchestras_dir.glob("*_orchestra.yaml")))
        if not orchestra_files:
            console.print(
                f"\n[yellow]No orchestras found in project '{project_name}'.[/yellow]"
            )
            return

        table = Table(
            title=f"🎵 Orchestras in Project: {project_name}", border_style="blue"
        )
        table.add_column("ID", style="bold blue")
        table.add_column("Name", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Agents", style="cyan")
        table.add_column("Tasks", style="magenta")

        for orchestra_file in orchestra_files:
            try:
                with open(orchestra_file, "r") as f:
                    orchestra_def = yaml.safe_load(f)

                orchestra_info = orchestra_def.get("orchestra", {})
                orchestra_id = orchestra_info.get(
                    "id", orchestra_file.stem.replace("_orchestra", "")
                )
                name = orchestra_info.get("name", "Unknown")
                description = orchestra_info.get("description", "No description.")
                agents = orchestra_def.get("agents", [])
                tasks = orchestra_def.get("tasks", [])

                table.add_row(
                    orchestra_id, name, description, str(len(agents)), str(len(tasks))
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not parse {orchestra_file.name}: {e}[/]"
                )

        console.print(table)

    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to list orchestras:[/] {e}")
        sys.exit(1)


def get_agent_tier_from_context() -> AgentTier:
    """Get agent tier from context or configuration."""
    # For now, this is a placeholder - in a real implementation,
    # this would check user configuration, project settings, etc.
    return AgentTier.ORACLES


def parse_agent_tier(tier_str: str) -> AgentTier:
    """Parse agent tier from string, with validation."""
    tier_str = tier_str.lower()

    valid_tiers = {
        "oracles": AgentTier.ORACLES,
        "genies": AgentTier.GENIES,
    }

    if tier_str not in valid_tiers:
        raise click.BadParameter(
            f"Invalid tier '{tier_str}'. Valid options: {', '.join(valid_tiers.keys())}"
        )

    return valid_tiers[tier_str]


def validate_tier_and_show_help(agent_tier: AgentTier, orchestra_config: dict):
    """Validate tier access and show helpful information."""
    try:
        TierValidator.validate_orchestration_access(agent_tier, orchestra_config)
    except Exception:
        # Validation will have already printed helpful error messages
        return False
    return True


@click.group(name="orchestra")
def orchestra_commands():
    """Orchestrate multiple agents to accomplish complex goals."""
    pass


@click.command()
@click.argument("orchestra_id")
@click.option("--goal", required=True, help="Goal description for the orchestra")
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["sequential", "parallel", "hierarchical", "mixed"]),
    help="Override the execution strategy defined in the orchestra file",
)
@click.option("--max-parallel", "-p", type=int, help="Override maximum parallel tasks")
@click.option("--timeout", "-t", type=int, help="Override task timeout in seconds")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--project", help="Project name (auto-detected if not specified)")
@click.option(
    "--tier",
    type=click.Choice([t.value for t in AgentTier]),
    help="Specify agent tier (overrides auto-detection)",
)
@click.option(
    "--dry-run", is_flag=True, help="Validate configuration without executing"
)
@click.option("--workspace-path", "-w", help="Override workspace directory path")
def run(
    orchestra_id: str,
    goal: str,
    strategy: str = None,
    max_parallel: int = None,
    timeout: int = None,
    verbose: bool = False,
    project: str = None,
    tier: str = None,
    dry_run: bool = False,
    workspace_path: str = None,
):
    """Run an orchestra to accomplish a goal."""

    # Determine agent tier
    if tier:
        agent_tier = parse_agent_tier(tier)
    else:
        agent_tier = get_agent_tier_from_context()

    console.print(f"[blue]🎭 Agent Tier:[/] {agent_tier.value}")

    # Find orchestra file using .super file as project marker (same as agent discovery)
    try:
        current_path = Path.cwd()
        project_root = current_path

        # Find project root by looking for .super file
        while project_root != project_root.parent:
            if (project_root / ".super").exists():
                break
            project_root = project_root.parent
        else:
            console.print(
                "[red]❌ Could not find .super file. Please run 'super init <project_name>' first.[/]"
            )
            sys.exit(1)

        # Get project name from .super file
        with open(project_root / ".super") as f:
            config = yaml.safe_load(f)
            project_name = config.get("project")

        if not project_name:
            console.print("[red]❌ Invalid .super file: missing project name.[/]")
            sys.exit(1)

        # Common search patterns for orchestra files
        patterns = [
            f"{orchestra_id}_orchestra.yaml",
            f"{orchestra_id}.yaml",
            f"{orchestra_id}_orchestra.yml",
            f"{orchestra_id}.yml",
        ]

        # Search nested directory first, then flat fallback
        orchestras_dir = project_root / project_name / "orchestras"
        if not orchestras_dir.exists():
            flat_dir = project_root / "orchestras"
            if flat_dir.exists():
                orchestras_dir = flat_dir

        orchestra_file = None

        if orchestras_dir.exists():
            for pattern in patterns:
                potential_file = orchestras_dir / pattern
                if potential_file.exists():
                    orchestra_file = potential_file
                    break

        # Also search using rglob pattern for nested structures
        if not orchestra_file:
            for pattern in patterns:
                matches = list(project_root.rglob(pattern))
                if matches:
                    orchestra_file = matches[0]  # Return first match
                    break

        # Final fallback: scan all *_orchestra.yaml files and match inside YAML 'id' if present
        if not orchestra_file:
            for yaml_file in project_root.rglob("*_orchestra.yaml"):
                try:
                    with open(yaml_file, "r") as f:
                        data = yaml.safe_load(f)
                        orch_info = data.get("orchestra", {})
                        if (
                            orch_info.get(
                                "id", yaml_file.stem.replace("_orchestra", "")
                            )
                            == orchestra_id
                        ):
                            orchestra_file = yaml_file
                            break
                except Exception:
                    continue

        if not orchestra_file:
            console.print(
                f"[red]❌ Orchestra '{orchestra_id}' not found in project '{project_name}'.[/]"
            )
            console.print(f"[yellow]Searched in:[/] {orchestras_dir}")
            console.print("[yellow]Available orchestras:[/]")
            if orchestras_dir.exists():
                available = [
                    f.stem.replace("_orchestra", "")
                    for f in orchestras_dir.glob("*_orchestra.yaml")
                ]
                if available:
                    console.print(f"  • {', '.join(available)}")
                else:
                    console.print("  • No orchestras found")
            else:
                console.print("  • Orchestras directory doesn't exist")
            console.print(
                f"[cyan]💡 Use 'super orchestra create {orchestra_id}' to create a new orchestra.[/cyan]"
            )
            sys.exit(1)

        console.print(f"[green]📁 Found orchestra file:[/] {orchestra_file}")

    except Exception as e:
        console.print(f"[red]❌ Error finding orchestra file: {e}[/]")
        sys.exit(1)

    try:
        # Load orchestra configuration for validation
        with open(orchestra_file, "r") as f:
            orchestra_data = yaml.safe_load(f)

        # Prepare config for tier validation
        orchestra_config = orchestra_data.get("orchestra", {})
        execution_config = orchestra_config.get("execution", {})

        # Apply CLI overrides for validation
        config_for_validation = {
            "execution": {
                "max_parallel_tasks": max_parallel
                or execution_config.get(
                    "max_parallel_tasks", 1
                ),  # Default to 1 for free version
                "strategy": strategy or execution_config.get("strategy", "sequential"),
            },
            "orchestration_type": orchestra_config.get("orchestration_type", "basic"),
        }

        # Apply advanced feature detection
        if orchestra_data.get("apiVersion") == "orchestra/v2":
            config_for_validation["apiVersion"] = "orchestra/v2"
        if "replicas" in orchestra_config:
            config_for_validation["replicas"] = orchestra_config["replicas"]

        # Validate tier access
        console.print("[blue]🔐 Validating tier permissions...[/]")
        validation_result = TierValidator.validate_orchestration_access(
            agent_tier, config_for_validation
        )

        if not validation_result["valid"]:
            console.print("\n❌ [bold red]Tier Permission Error[/]")
            console.print(f"[yellow]Current Tier:[/] {agent_tier.value}")

            for error in validation_result["errors"]:
                console.print(f"[red]• {error}[/]")

            # Show available features
            features = validation_result["available_features"]
            console.print(
                f"\n[green]✅ Available Features for {agent_tier.value} tier:[/]"
            )

            table = Table(title="Tier Features")
            table.add_column("Feature", style="cyan")
            table.add_column("Available", style="green")
            table.add_column("Limit", style="yellow")

            table.add_row(
                "Orchestration Types",
                str([t.value for t in features["orchestration_types"]]),
                "-",
            )
            table.add_row(
                "Max Parallel Tasks", "✅", str(features["max_parallel_tasks"])
            )
            table.add_row(
                "Execution Strategies", str(features["execution_strategies"]), "-"
            )
            table.add_row(
                "Auto-scaling", "✅" if features.get("auto_scaling") else "❌", "-"
            )
            table.add_row(
                "Agent Replicas", "✅" if features.get("replicas") else "❌", "-"
            )
            table.add_row(
                "Advanced Networking",
                "✅" if features.get("advanced_networking") else "❌",
                "-",
            )
            table.add_row(
                "Custom Operators", "✅" if features.get("operators") else "❌", "-"
            )

            console.print(table)

            # Show upgrade suggestions
            if agent_tier in [AgentTier.ORACLES, AgentTier.GENIES]:
                console.print(
                    "\n[blue]💡 Upgrade to Protocols+ tier to unlock Kubernetes-style orchestration![/]"
                )

            # Show CLI suggestions
            console.print(
                f"\n[blue]📋 Suggested alternatives for {agent_tier.value} tier:[/]"
            )
            basic_alternatives = []

            if max_parallel and max_parallel > features["max_parallel_tasks"]:
                basic_alternatives.append(
                    f"--max-parallel {features['max_parallel_tasks']}"
                )

            if basic_alternatives:
                alt_cmd = f'super orchestra run {orchestra_id} --goal "{goal}" {" ".join(basic_alternatives)}'
                console.print(f"[cyan]{alt_cmd}[/]")

            sys.exit(1)

        console.print("[green]✅ Tier validation passed![/]")

        # Show what features are being used
        if verbose:
            features = validation_result["available_features"]
            console.print("\n[blue]🎯 Execution Plan:[/]")
            console.print(
                f"[cyan]• Strategy:[/] {config_for_validation['execution']['strategy']}"
            )
            console.print(
                f"[cyan]• Max Parallel:[/] {config_for_validation['execution']['max_parallel_tasks']}"
            )
            console.print(
                f"[cyan]• Orchestration Type:[/] {config_for_validation['orchestration_type']}"
            )

        # If dry-run, exit after validation
        if dry_run:
            console.print(
                f"[green]🏁 Dry run completed successfully - configuration is valid for {agent_tier.value} tier[/]"
            )
            return

        # Create and run the enhanced orchestra runner
        console.print("[blue]🎼 Initializing Enhanced Orchestra Runner...[/]")

        runner = EnhancedOrchestraRunner(
            orchestra_file=str(orchestra_file),
            workspace_path=workspace_path,
            agent_tier=agent_tier,
        )

        # Run the orchestra
        result = run_async(runner.run_orchestra(goal))

        # Display results
        if result["success"]:
            console.print("\n[green]🎉 Orchestra execution completed successfully![/]")

            if verbose:
                console.print("\n[blue]📊 Execution Statistics:[/]")
                stats = result["stats"]
                console.print(
                    f"[cyan]• Total Execution Time:[/] {result['total_execution_time']:.2f}s"
                )
                console.print(f"[cyan]• Completed Tasks:[/] {stats['completed_tasks']}")
                console.print(f"[cyan]• Failed Tasks:[/] {stats['failed_tasks']}")

                # Show task results
                console.print("\n[blue]📋 Task Results:[/]")
                for task_name, task_result in result["task_results"].items():
                    status = "✅" if task_result["success"] else "❌"
                    time_str = f"{task_result.get('execution_time', 0):.2f}s"
                    console.print(f"  {status} {task_name}: {time_str}")
        else:
            console.print("\n[red]❌ Orchestra execution failed![/]")
            console.print(f"[red]Error:[/] {result.get('error', 'Unknown error')}")

            if "current_tier" in result:
                console.print(f"[yellow]Current Tier:[/] {result['current_tier']}")

            sys.exit(1)

    except FileNotFoundError:
        console.print(f"[red]❌ Orchestra file not found: {orchestra_file}[/]")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]❌ Invalid YAML in orchestra file: {e}[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/]")
        if verbose:
            import traceback

            console.print(f"[red]{traceback.format_exc()}[/]")
        sys.exit(1)


@click.command()
@click.option(
    "--tier",
    type=click.Choice([t.value for t in AgentTier]),
    help="Show features for specific tier",
)
def features(tier: str = None):
    """Show available features by tier."""

    if tier:
        agent_tier = parse_agent_tier(tier)
        tiers_to_show = [agent_tier]
    else:
        tiers_to_show = list(AgentTier)

    for agent_tier in tiers_to_show:
        _ = TierFeatures.get_available_features(agent_tier)  # noqa: F841

        console.print(f"\n[bold blue]🎯 {agent_tier.value.title()} Tier Features[/]")

        table = Table()
        table.add_column("Feature", style="cyan")
        table.add_column("Available", style="green")
        table.add_column("Details", style="yellow")

        table.add_row(
            "Orchestration",
            "Sequential Only",
            "Basic task orchestration",
        )
        table.add_row("Basic Optimization", "✅", "BootstrapFewShot")
        table.add_row("Basic Evaluation", "✅", "Exact match, F1 score")

        if agent_tier == AgentTier.GENIES:
            table.add_row("ReAct Tools", "✅", "Tool integration")
            table.add_row("RAG Retrieval", "✅", "Knowledge connection")
            table.add_row("Agent Memory", "✅", "Short-term & episodic")
            table.add_row("Basic Streaming", "✅", "Real-time responses")

        console.print(table)

        if agent_tier == AgentTier.ORACLES:
            console.print("[dim]💡 Upgrade to Genies tier for enhanced capabilities[/]")

    console.print("\n[yellow]ℹ️  Advanced features available in commercial version[/]")


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--tier",
    type=click.Choice([t.value for t in AgentTier]),
    help="Validate against specific tier",
)
def validate(config_file: str, tier: str = None):
    """Validate orchestra configuration against tier restrictions."""

    # Determine agent tier
    if tier:
        agent_tier = parse_agent_tier(tier)
    else:
        agent_tier = get_agent_tier_from_context()

    console.print(
        f"[blue]🔍 Validating {config_file} for {agent_tier.value} tier...[/]"
    )

    try:
        with open(config_file, "r") as f:
            orchestra_data = yaml.safe_load(f)

        # Extract config for validation
        orchestra_config = orchestra_data.get("orchestra", {})
        config_for_validation = {
            "execution": orchestra_config.get("execution", {}),
            "orchestration_type": orchestra_config.get("orchestration_type", "basic"),
        }

        # Apply advanced feature detection
        if orchestra_data.get("apiVersion") == "orchestra/v2":
            config_for_validation["apiVersion"] = "orchestra/v2"
        if "replicas" in orchestra_config:
            config_for_validation["replicas"] = orchestra_config["replicas"]

        # Perform validation
        result = TierValidator.validate_orchestration_access(
            agent_tier, config_for_validation
        )

        if result["valid"]:
            console.print(
                f"[green]✅ Configuration is valid for {agent_tier.value} tier![/]"
            )

            console.print("\n[blue]📋 Validated Features:[/]")
            console.print(
                f"[cyan]• Max Parallel Tasks:[/] {config_for_validation.get('execution', {}).get('max_parallel_tasks', 'default')}"
            )
            console.print(
                f"[cyan]• Orchestration Type:[/] {config_for_validation['orchestration_type']}"
            )

        else:
            console.print(
                f"[red]❌ Configuration is invalid for {agent_tier.value} tier![/]"
            )
            for error in result["errors"]:
                console.print(f"[red]• {error}[/]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/]")
        sys.exit(1)


@click.command()
@click.argument("name")
def create(name: str):
    """Create a new orchestra definition file."""

    class Args:
        def __init__(self, name):
            self.name = name

    create_orchestra(Args(name))


@click.command()
def list_cmd():
    """List all available orchestras in the project."""

    class Args:
        pass

    list_orchestras(Args())


# Add commands to the group
orchestra_commands.add_command(run)
orchestra_commands.add_command(features)
orchestra_commands.add_command(validate)

# Add the new commands
orchestra_commands.add_command(create)
orchestra_commands.add_command(list_cmd, name="list")


# Backward compatibility function
def run_orchestra(args):
    """Run an orchestra using the old CLI interface."""
    from pathlib import Path

    from superoptix.runners.orchestra_runner import EnhancedOrchestraRunner

    # Extract parameters from args
    orchestra_id = args.name
    input_data = args.goal
    getattr(args, "strategy", None)
    getattr(args, "max_parallel", None)
    getattr(args, "timeout", None)
    verbose = getattr(args, "verbose", False)
    getattr(args, "project", None)
    tier = getattr(args, "tier", None)
    workspace_path = getattr(args, "workspace_path", None)

    # Determine agent tier
    if tier:
        agent_tier = parse_agent_tier(tier)
    else:
        agent_tier = get_agent_tier_from_context()

    console.print(f"🎼 [bold blue]Running Orchestra:[/] {orchestra_id}")
    console.print(f"[blue]🎭 Agent Tier:[/] {agent_tier.value}")

    try:
        # Find orchestra file
        current_path = Path.cwd()
        orchestra_file = None

        # Enhanced search patterns for orchestra files
        search_patterns = [
            # Direct patterns
            f"{orchestra_id}_orchestra.yaml",
            f"{orchestra_id}.yaml",
            # Local orchestras directory
            f"orchestras/{orchestra_id}_orchestra.yaml",
            f"orchestras/{orchestra_id}.yaml",
            # SWE project patterns
            f"swe/swe/orchestras/{orchestra_id}_orchestra.yaml",
            f"swe/orchestras/{orchestra_id}_orchestra.yaml",
            # Relative to parent directory (if running from subdirectory)
            f"../swe/swe/orchestras/{orchestra_id}_orchestra.yaml",
            f"../orchestras/{orchestra_id}_orchestra.yaml",
            # When running from swe subdirectory
            f"swe/orchestras/{orchestra_id}_orchestra.yaml",
            f"./swe/orchestras/{orchestra_id}_orchestra.yaml",
        ]

        # First, try the standard search patterns
        for pattern in search_patterns:
            potential_file = current_path / pattern
            if potential_file.exists():
                orchestra_file = potential_file
                break

        # If not found, try searching upwards for project root and then search
        if not orchestra_file:
            search_path = current_path
            for _ in range(3):  # Search up to 3 levels up
                for pattern in [
                    f"swe/swe/orchestras/{orchestra_id}_orchestra.yaml",
                    f"orchestras/{orchestra_id}_orchestra.yaml",
                    f"{orchestra_id}_orchestra.yaml",
                ]:
                    potential_file = search_path / pattern
                    if potential_file.exists():
                        orchestra_file = potential_file
                        break

                if orchestra_file:
                    break

                # Move up one directory
                parent = search_path.parent
                if parent == search_path:  # Reached filesystem root
                    break
                search_path = parent

        # Final fallback: scan all *_orchestra.yaml files and match inside YAML 'id' if present
        if not orchestra_file:
            for yaml_file in current_path.rglob("*_orchestra.yaml"):
                try:
                    with open(yaml_file, "r") as f:
                        data = yaml.safe_load(f)
                        orch_info = data.get("orchestra", {})
                        if (
                            orch_info.get(
                                "id", yaml_file.stem.replace("_orchestra", "")
                            )
                            == orchestra_id
                        ):
                            orchestra_file = yaml_file
                            break
                except Exception:
                    continue

        if not orchestra_file:
            console.print(f"[red]❌ Orchestra file not found for ID: {orchestra_id}[/]")
            return

        console.print(f"[green]📁 Using orchestra file:[/] {orchestra_file}")

        # Create enhanced orchestra runner with tier support
        runner = EnhancedOrchestraRunner(
            orchestra_file=str(orchestra_file),
            workspace_path=workspace_path,
            agent_tier=agent_tier,
        )

        # Run the orchestra
        result = run_async(runner.run_orchestra(input_data))

        # Display results
        if result["success"]:
            console.print("[green]🎉 Orchestra completed successfully![/]")

            if verbose:
                stats = result["stats"]
                console.print("\n[blue]📊 Execution Statistics:[/]")
                console.print(
                    f"[cyan]• Total Time:[/] {result['total_execution_time']:.2f}s"
                )
                console.print(f"[cyan]• Completed Tasks:[/] {stats['completed_tasks']}")
                console.print(f"[cyan]• Failed Tasks:[/] {stats['failed_tasks']}")
        else:
            console.print(
                f"[red]❌ Orchestra execution failed: {result.get('error')}[/]"
            )
            if "current_tier" in result:
                console.print(f"[yellow]Current Tier:[/] {result['current_tier']}")

    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/]")
