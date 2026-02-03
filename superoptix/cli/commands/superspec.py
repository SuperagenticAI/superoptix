"""
SuperSpec CLI Commands

CLI integration for the SuperSpec DSL - Agent Playbook Definition Language.
Provides commands for generating, validating, and managing agent playbooks.
"""

import click
import yaml
import json
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...superspec import (
    SuperSpecXGenerator,
    SuperSpecXValidator,
    SuperSpecXParser,
    SuperSpecXSchema,
)


console = Console()


def _get_super_output_path(agent_name: str, tier: str, format: str = "yaml") -> str:
    """
    Determine the correct output path for a playbook in SuperOptiX project structure.

    Args:
        agent_name: Name of the agent
        tier: Agent tier (oracle or genie)
        format: File format (yaml or json)

    Returns:
        Correct output path
    """
    try:
        # Check if we're in a SuperOptiX project
        current_dir = Path.cwd()
        super_file = None

        # Look for .super file in current directory or parent directories
        search_dir = current_dir
        while search_dir != search_dir.parent:
            potential_super = search_dir / ".super"
            if potential_super.exists():
                super_file = potential_super
                break
            search_dir = search_dir.parent

        if super_file:
            # We're in a SuperOptiX project, use proper structure
            with open(super_file, "r") as f:
                super_config = yaml.safe_load(f)
                project_name = super_config.get("project", "project")

            # Create proper directory structure: <project_name>/agents/<agent_name>/playbook/
            project_root = super_file.parent
            safe_agent_name = agent_name.lower().replace(" ", "_").replace("-", "_")
            agent_dir = (
                project_root / project_name / "agents" / safe_agent_name / "playbook"
            )
            agent_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{safe_agent_name}_playbook.{format}"
            output_path = agent_dir / filename

            console.print(
                f"📁 Using SuperOptiX project structure: {output_path.relative_to(project_root)}"
            )
            return str(output_path)
        else:
            # Not in a SuperOptiX project, use current directory
            safe_name = agent_name.lower().replace(" ", "_").replace("-", "_")
            filename = f"{safe_name}_{tier}_playbook.{format}"
            console.print(
                f"📁 No SuperOptiX project detected, using current directory: {filename}"
            )
            return filename

    except Exception as e:
        # Fallback to current directory
        safe_name = agent_name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{safe_name}_{tier}_playbook.{format}"
        console.print(
            f"⚠️  Error determining project structure ({e}), using: {filename}"
        )
        return filename


@click.group(name="superspec")
def superspec_cli():
    """🎭 SuperSpec DSL - Agent Playbook Definition Language commands.

    🚀 Create, validate, and manage AI agent playbooks with SuperSpec DSL!

    📚 Quick Start:
      super spec generate genie my-agent --namespace software
      super spec validate my-agent_playbook.yaml
      super spec analyze ./agents/

    🎯 Available Commands:
      generate  - Create new agent playbook templates
      validate  - Check playbook syntax and structure
      analyze   - Get insights about your playbooks
      info      - Show detailed playbook information
      schema    - Explore DSL schema and features
      bootstrap - Generate multiple agents for a namespace
    """
    pass


@superspec_cli.command()
@click.option(
    "--tier",
    "-t",
    type=click.Choice(["oracles", "genies"]),
    required=True,
    help="🎯 Agent tier: oracle (basic) or genie (advanced)",
)
@click.option(
    "--name",
    "-n",
    required=True,
    help="🤖 Agent name (e.g., 'data-analyst', 'customer-support')",
)
@click.option(
    "--namespace",
    "-ns",
    default="software",
    type=click.Choice(SuperSpecXSchema.VALID_NAMESPACES),
    help="🏷️ Agent namespace (software, finance, healthcare, etc.)",
)
@click.option("--role", "-r", default="Assistant", help="👤 Agent role description")
@click.option("--description", "-d", help="📝 Detailed agent description")
@click.option(
    "--output",
    "-o",
    help="📁 Output directory or file path (auto-creates filename if directory)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="📄 Output format (yaml or json)",
)
@click.option(
    "--memory/--no-memory", default=True, help="💾 Enable memory system (Genie only)"
)
@click.option(
    "--tools/--no-tools", default=True, help="🔧 Enable tool integration (Genie only)"
)
@click.option(
    "--rag/--no-rag", default=False, help="🔍 Enable RAG/retrieval (Genie only)"
)
def generate(
    tier: str,
    name: str,
    namespace: str,
    role: str,
    description: str,
    output: str,
    format: str,
    memory: bool,
    tools: bool,
    rag: bool,
):
    """🎨 Generate agent playbook templates.

    ✨ Examples:
      super spec generate genie data-analyst --namespace finance
      super spec generate oracle chatbot --output ./my-agents/
      super spec generate genie assistant --no-rag --format json

    🎯 Tiers:
      oracle - Basic agent with chain-of-thought reasoning
      genie  - Advanced agent with memory, tools, and optimization
    """
    try:
        generator = SuperSpecXGenerator()

        # Generate playbook based on tier
        playbook = generator.generate_playbook(
            tier=tier, role=name, namespace=namespace
        )

        # Determine output file path
        if not output:
            output = _get_super_output_path(name, tier, format)
        else:
            output_path = Path(output)
            if output_path.is_dir() or str(output).endswith("/"):
                # If output is a directory, construct the filename
                safe_agent_name = name.lower().replace(" ", "_").replace("-", "_")
                filename = f"{safe_agent_name}_playbook.{format}"
                output = str(output_path / filename)
            else:
                # If parent directory does not exist, create it
                parent_dir = output_path.parent
                parent_dir.mkdir(parents=True, exist_ok=True)

        # Save template
        if generator.save_template(playbook, output, format):
            console.print(
                f"✅ Generated {tier} agent playbook: [bold green]{output}[/bold green]"
            )

            # Show template info
            info = generator.get_template_info(playbook)
            console.print(f"📋 Agent: {info['name']} (Tier: {info['tier']})")
            console.print(f"🏷️  Namespace: {info['namespace']}")
            if info["features"]:
                console.print(f"⚡ Features: {', '.join(info['features'])}")
        else:
            console.print("❌ Failed to save template", style="red")

    except Exception as e:
        console.print(f"❌ Error generating template: {str(e)}", style="red")


@superspec_cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--verbose", "-v", is_flag=True, help="🔍 Show detailed validation output"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="📊 Output format (table or json)",
)
def validate(files: List[str], verbose: bool, format: str):
    """✅ Validate agent playbook files.

    🔍 Checks syntax, structure, and compliance with SuperSpec schema.

    ✨ Examples:
      super spec validate my-agent_playbook.yaml
      super spec validate *.yaml --verbose
      super spec validate agent1.yaml agent2.yaml --format json

    📋 Validates:
      • YAML/JSON syntax
      • Required fields and structure
      • Tier-specific constraints
      • Namespace compatibility
    """
    validator = SuperSpecXValidator()
    results = []

    # Process each file
    for file_path in files:
        result = validator.validate_file(file_path)
        results.append(result)

    if format == "json":
        # JSON output
        console.print(json.dumps(results, indent=2))
        return

    # Table output
    table = Table(title="🔍 SuperSpec Validation Results")
    table.add_column("📄 File", style="cyan")
    table.add_column("✅ Status", style="bold")
    table.add_column("🎯 Tier", style="magenta")
    table.add_column("❌ Errors", style="red")
    table.add_column("⚠️  Warnings", style="yellow")

    for result in results:
        file_name = Path(result.get("file_path", "")).name
        status = "✅ Valid" if result["valid"] else "❌ Invalid"
        tier = result.get("tier", "unknown")
        error_count = len(result["errors"])
        warning_count = len(result["warnings"])

        table.add_row(
            file_name,
            status,
            tier,
            str(error_count) if error_count > 0 else "-",
            str(warning_count) if warning_count > 0 else "-",
        )

    console.print(table)

    # Show detailed errors if verbose
    if verbose:
        for result in results:
            if result["errors"] or result["warnings"]:
                file_name = Path(result.get("file_path", "")).name

                panel_content = []
                if result["errors"]:
                    panel_content.append("[red]❌ Errors:[/red]")
                    for error in result["errors"]:
                        panel_content.append(f"  • {error}")

                if result["warnings"]:
                    if panel_content:
                        panel_content.append("")
                    panel_content.append("[yellow]⚠️  Warnings:[/yellow]")
                    for warning in result["warnings"]:
                        panel_content.append(f"  • {warning}")

                if panel_content:
                    console.print(
                        Panel(
                            "\n".join(panel_content),
                            title=f"📄 {file_name}",
                            border_style="red" if result["errors"] else "yellow",
                        )
                    )

    # Show summary
    summary = validator.get_validation_summary(results)
    console.print(
        f"\n📊 Summary: {summary['valid_files']}/{summary['total_files']} valid "
        f"({summary['validation_rate']:.1%})"
    )


@superspec_cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--pattern",
    "-p",
    default="*.yaml",
    help="🔍 File pattern to match (default: *.yaml)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="📊 Output format (table or json)",
)
def analyze(path: str, pattern: str, format: str):
    """📊 Analyze agent playbooks in a directory.

    🔍 Get insights about your agent collection: tier distribution, feature usage, and more.

    ✨ Examples:
      super spec analyze ./agents/
      super spec analyze my-playbook.yaml
      super spec analyze ./ --pattern "*.json" --format json

    📈 Provides:
      • Agent overview and statistics
      • Tier and namespace distribution
      • Feature usage analysis
      • Task count and complexity metrics
    """
    parser = SuperSpecXParser()

    path_obj = Path(path)
    if path_obj.is_file():
        # Single file
        spec = parser.parse_file(path)
        if spec:
            specs = [spec]
        else:
            console.print("❌ Failed to parse file", style="red")
            return
    else:
        # Directory
        specs = parser.parse_directory(path, pattern)

    if not specs:
        console.print("No valid playbooks found", style="yellow")
        return

    # Get analysis summary
    summary = parser.get_parsing_summary()

    if format == "json":
        # JSON output
        analysis_data = {
            "summary": summary,
            "agents": [
                {
                    "name": spec.metadata.name,
                    "tier": spec.metadata.level,
                    "namespace": spec.metadata.namespace,
                    "tasks": len(spec.tasks),
                    "has_memory": spec.memory is not None,
                    "has_tools": spec.tool_calling is not None,
                    "has_rag": spec.retrieval is not None,
                }
                for spec in specs
            ],
        }
        console.print(json.dumps(analysis_data, indent=2))
        return

    # Table output
    console.print(f"📁 Analyzed {len(specs)} agent playbooks\n")

    # Overview table
    overview_table = Table(title="🤖 Agent Overview")
    overview_table.add_column("🤖 Name", style="cyan")
    overview_table.add_column("🎯 Tier", style="magenta")
    overview_table.add_column("🏷️  Namespace", style="green")
    overview_table.add_column("📋 Tasks", style="blue")
    overview_table.add_column("⚡ Features", style="yellow")

    for spec in specs:
        features = []
        if spec.memory:
            features.append("💾 Memory")
        if spec.tool_calling:
            features.append("🔧 Tools")
        if spec.retrieval:
            features.append("🔍 RAG")
        if spec.agentflow:
            features.append("🔄 AgentFlow")

        overview_table.add_row(
            spec.metadata.name,
            spec.metadata.level,
            spec.metadata.namespace or "none",
            str(len(spec.tasks)),
            ", ".join(features) if features else "Basic",
        )

    console.print(overview_table)

    # Distribution statistics
    console.print("\n📊 Statistics:")

    tier_dist = summary["tier_distribution"]
    if tier_dist:
        console.print("🎯 Tier Distribution:")
        for tier, count in tier_dist.items():
            console.print(f"  • {tier.title()}: {count}")

    namespace_dist = summary["namespace_distribution"]
    if namespace_dist:
        console.print("🏷️  Namespace Distribution:")
        for namespace, count in namespace_dist.items():
            console.print(f"  • {namespace}: {count}")

    feature_usage = summary["feature_usage"]
    if feature_usage:
        console.print("⚡ Feature Usage:")
        for feature, count in feature_usage.items():
            if count > 0:
                console.print(f"  • {feature}: {count}")


@superspec_cli.command()
@click.argument("file", type=click.Path(exists=True))
def info(file: str):
    """📋 Show detailed information about an agent playbook.

    🔍 Get comprehensive details about a specific agent: metadata, features, tasks, and more.

    ✨ Examples:
      super spec info my-agent_playbook.yaml
      super spec info ./agents/developer/playbook/developer_playbook.yaml

    📊 Shows:
      • Agent metadata and configuration
      • Language model settings
      • Task definitions and flow
      • Feature capabilities
      • Validation status
    """
    parser = SuperSpecXParser()
    spec = parser.parse_file(file)

    if not spec:
        console.print("❌ Failed to parse playbook file", style="red")
        return

    # Basic information
    console.print(
        Panel(
            f"[bold cyan]{spec.metadata.name}[/bold cyan]\n"
            f"🆔 ID: {spec.metadata.id}\n"
            f"📦 Version: {spec.metadata.version}\n"
            f"🎯 Tier: [magenta]{spec.metadata.level}[/magenta]\n"
            f"🏷️  Namespace: [green]{spec.metadata.namespace or 'none'}[/green]\n"
            f"📈 Stage: {spec.metadata.stage}\n"
            f"🎭 Type: {spec.metadata.agent_type}",
            title="📋 Agent Information",
        )
    )

    # Description
    if spec.metadata.description:
        console.print(Panel(spec.metadata.description, title="📝 Description"))

    # Language Model
    lm = spec.language_model
    console.print(
        Panel(
            f"🤖 Provider: [blue]{lm.get('provider', 'unknown')}[/blue]\n"
            f"🧠 Model: {lm.get('model', 'unknown')}\n"
            f"🌡️  Temperature: {lm.get('temperature', 0.0)}\n"
            f"📏 Max Tokens: {lm.get('max_tokens', 'default')}",
            title="🧠 Language Model",
        )
    )

    # Tasks
    if spec.tasks:
        tasks_info = []
        for task in spec.tasks:
            input_count = len(task.inputs) if task.inputs else 0
            output_count = len(task.outputs) if task.outputs else 0
            tasks_info.append(f"• {task.name} ({input_count}→{output_count})")

        console.print(
            Panel("\n".join(tasks_info), title=f"📋 Tasks ({len(spec.tasks)})")
        )

    # Agent Flow
    if spec.agentflow:
        flow_info = []
        for step in spec.agentflow:
            depends = (
                f" (depends: {', '.join(step.depends_on)})" if step.depends_on else ""
            )
            flow_info.append(f"• {step.name}: {step.type}{depends}")

        console.print(
            Panel(
                "\n".join(flow_info),
                title=f"🔄 Agent Flow ({len(spec.agentflow)} steps)",
            )
        )

    # Features
    features_info = []
    if spec.memory:
        features_info.append("💾 Memory: Enabled")
    if spec.tool_calling:
        tools = spec.tool_calling.get("available_tools", [])
        features_info.append(f"🔧 Tools: {len(tools)} available")
    if spec.retrieval:
        retriever = spec.retrieval.get("retriever_type", "unknown")
        features_info.append(f"🔍 RAG: {retriever}")
    if spec.optimization:
        strategy = spec.optimization.get("strategy", "unknown")
        features_info.append(f"⚡ Optimization: {strategy}")

    if features_info:
        console.print(Panel("\n".join(features_info), title="✨ Features"))

    # Validation check
    validator = SuperSpecXValidator()
    result = validator.validate(
        spec.__dict__
        if hasattr(spec.__dict__, "get")
        else {
            "apiVersion": spec.api_version,
            "kind": spec.kind,
            "metadata": spec.metadata.__dict__,
            "spec": {
                "language_model": spec.language_model,
                "tasks": [task.__dict__ for task in spec.tasks],
                "persona": spec.persona,
                "agentflow": [step.__dict__ for step in spec.agentflow]
                if spec.agentflow
                else None,
                "memory": spec.memory,
                "tool_calling": spec.tool_calling,
                "retrieval": spec.retrieval,
            },
        }
    )

    validation_status = "✅ Valid" if result["valid"] else "❌ Invalid"
    console.print(
        Panel(
            f"🔍 Validation: {validation_status}\n"
            f"❌ Errors: {len(result['errors'])}\n"
            f"⚠️  Warnings: {len(result['warnings'])}",
            title="✅ Validation Status",
            border_style="green" if result["valid"] else "red",
        )
    )


@superspec_cli.command()
@click.option(
    "--tier",
    "-t",
    type=click.Choice(["oracles", "genies"]),
    help="🎯 Show features for specific tier",
)
def schema(tier: Optional[str]):
    """📚 Show SuperSpec DSL schema information.

    🔍 Explore the DSL structure, supported features, and tier capabilities.

    ✨ Examples:
      super spec schema
      super spec schema --tier genie
      super spec schema --tier oracle

    📖 Provides:
      • Schema overview and structure
      • Tier feature comparison
      • Allowed and forbidden features
      • Namespace and component information
    """
    schema_obj = SuperSpecXSchema()

    if tier:
        # Show tier-specific information
        features = schema_obj.get_tier_features(tier)

        console.print(
            Panel(
                f"[bold]{tier.title()} Tier Features[/bold]",
                title="🎯 Tier Information",
            )
        )

        if "agentflow_types" in features:
            console.print(
                Panel(
                    "\n".join(
                        f"• {step_type}" for step_type in features["agentflow_types"]
                    ),
                    title="🔄 Allowed AgentFlow Steps",
                )
            )

        if "forbidden_features" in features:
            console.print(
                Panel(
                    "\n".join(
                        f"• {feature}" for feature in features["forbidden_features"]
                    ),
                    title="🚫 Forbidden Features",
                    border_style="red",
                )
            )

        if "allowed_features" in features:
            console.print(
                Panel(
                    "\n".join(
                        f"• {feature}" for feature in features["allowed_features"]
                    ),
                    title="✅ Additional Features",
                    border_style="green",
                )
            )
    else:
        # Show general schema information
        console.print(
            Panel(
                "[bold]SuperSpec DSL Schema Overview[/bold]\n\n"
                f"📊 Supported Tiers: {', '.join(schema_obj.VALID_TIERS)}\n"
                f"🏷️  Namespaces: {len(schema_obj.VALID_NAMESPACES)} available\n"
                f"🔧 Components: feature_specifications, evaluation, optimization",
                title="📚 Schema Information",
            )
        )

        # Tier comparison
        comparison_table = Table(title="🎯 Tier Feature Comparison")
        comparison_table.add_column("⚡ Feature", style="cyan")
        comparison_table.add_column("🎭 Oracle", style="blue")
        comparison_table.add_column("🧞 Genie", style="magenta")

        _ = schema_obj.get_tier_features("oracles")  # noqa: F841
        _ = schema_obj.get_tier_features("genies")  # noqa: F841

        comparison_table.add_row("🔗 Chain of Thought", "✅", "✅")
        comparison_table.add_row("⚡ Basic Optimization", "✅", "✅")
        comparison_table.add_row("🎼 Sequential Orchestra", "✅", "✅")
        comparison_table.add_row("💾 Memory System", "❌", "✅")
        comparison_table.add_row("🔧 Tool Integration", "❌", "✅")
        comparison_table.add_row("🔍 RAG/Retrieval", "❌", "✅")
        comparison_table.add_row("🌊 Streaming", "❌", "✅")

        console.print(comparison_table)


@superspec_cli.command()
@click.option(
    "--namespace",
    "-ns",
    required=True,
    type=click.Choice(SuperSpecXSchema.VALID_NAMESPACES),
    help="🏷️ Target namespace (software, finance, healthcare, etc.)",
)
@click.option(
    "--output-dir",
    "-o",
    default="./generated_agents",
    help="📁 Output directory for generated agents",
)
@click.option(
    "--tiers",
    "-t",
    multiple=True,
    type=click.Choice(["oracles", "genies"]),
    default=["oracles", "genies"],
    help="🎯 Tiers to generate (oracle, genie)",
)
def bootstrap(namespace: str, output_dir: str, tiers: List[str]):
    """🚀 Bootstrap agents for a namespace with common roles.

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
    """
    generator = SuperSpecXGenerator()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"🚀 Bootstrapping {namespace} agents...")

    # Generate templates
    generated_files = generator.generate_namespace_templates(
        namespace=namespace, output_dir=output_dir, tiers=list(tiers)
    )

    if generated_files:
        console.print(f"✅ Generated {len(generated_files)} playbook templates:")
        for file_path in generated_files:
            console.print(f"  📄 {file_path}")

        console.print("\n💡 Next steps:")
        console.print("  1. Review and customize the generated playbooks")
        console.print(
            f"  2. Validate: [cyan]super spec validate {output_dir}/*.yaml[/cyan]"
        )
        console.print("  3. Compile: [cyan]super agent compile <playbook>[/cyan]")
    else:
        console.print("❌ No templates were generated", style="red")


# Add the superspec command group to the main CLI
def register_superspec_commands(cli_group):
    """Register SuperSpec commands with the main CLI."""
    cli_group.add_command(superspec_cli)


# Wrapper functions for argparse integration with main CLI
def generate_agent(args):
    """Wrapper for generate command using argparse."""
    # Directly call the function instead of using CliRunner
    generate.callback(
        tier=args.tier,
        name=args.name,
        namespace=getattr(args, "namespace", "software"),
        role=getattr(args, "role", "Assistant"),
        description=getattr(args, "description", None),
        output=getattr(args, "output", None),
        format=getattr(args, "format", "yaml"),
        memory=getattr(args, "memory", True),
        tools=getattr(args, "tools", True),
        rag=getattr(args, "rag", False),
    )


def validate_agents(args):
    """Wrapper for validate command using argparse."""
    # Directly call the function instead of using CliRunner
    validate.callback(
        files=list(args.files),
        verbose=getattr(args, "verbose", False),
        format=getattr(args, "format", "table"),
    )


def analyze_agents(args):
    """Wrapper for analyze command using argparse."""
    # Directly call the function instead of using CliRunner
    analyze.callback(
        path=args.path,
        pattern=getattr(args, "pattern", "*.yaml"),
        format=getattr(args, "format", "table"),
    )


def show_info(args):
    """Wrapper for info command using argparse."""
    # Directly call the function instead of using CliRunner
    info.callback(file=args.file)


def show_schema(args):
    """Wrapper for schema command using argparse."""
    # Directly call the function instead of using CliRunner
    schema.callback(tier=getattr(args, "tier", None))


def bootstrap_namespace(args):
    """Wrapper for bootstrap command using argparse."""
    # Directly call the function instead of using CliRunner
    bootstrap.callback(
        namespace=args.namespace,
        output_dir=getattr(args, "output_dir", "./generated_agents"),
        tiers=getattr(args, "tiers", ["oracle", "genie"]),
    )
