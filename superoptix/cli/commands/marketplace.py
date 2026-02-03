"""
SuperOptiX Marketplace CLI Commands
===================================

Unified discovery hub for agents and tools - your AI component marketplace.
"""

from pathlib import Path

import yaml
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def marketplace_dashboard(args):
    """Show the main marketplace dashboard with overview and stats."""
    console.print("\n🏪 [bold bright_cyan]SuperOptiX Marketplace[/bold bright_cyan]")
    console.print("═" * 70)
    console.print("[dim]Your one-stop shop for AI agents and tools[/dim]\n")

    # Get stats
    agent_stats = _get_agent_stats()
    tool_stats = _get_tool_stats()

    # Create overview cards
    agent_card = Panel(
        f"[bold cyan]🤖 {agent_stats['total']} Agents[/bold cyan]\n"
        f"📊 {agent_stats['industries']} Industries\n"
        f"🎯 {agent_stats['oracle']} Oracle • {agent_stats['genie']} Genie\n"
        f"🚀 {agent_stats['autonomous']} Autonomous • {agent_stats['supervised']} Supervised",
        title="[bold]Agents",
        border_style="cyan",
    )

    tool_card = Panel(
        f"[bold yellow]🛠️ {tool_stats['total']} Tools[/bold yellow]\n"
        f"📂 {tool_stats['categories']} Categories\n"
        f"🎯 Genie-tier ready\n"
        f"⚡ Production tested",
        title="[bold]Tools",
        border_style="yellow",
    )

    featured_card = Panel(
        "[bold green]⭐ Featured[/bold green]\n"
        "🔥 developer (software)\n"
        "🔍 WebSearchTool\n"
        "🧮 CalculatorTool",
        title="[bold]Popular",
        border_style="green",
    )

    console.print(Columns([agent_card, tool_card, featured_card]))

    # Quick actions
    console.print("\n[cyan]🚀 Quick Actions:[/cyan]")
    console.print("   [bold]super market browse agents[/bold]      - Browse all agents")
    console.print("   [bold]super market browse tools[/bold]       - Browse all tools")
    console.print("   [bold]super market search <term>[/bold]      - Universal search")
    console.print("   [bold]super market featured[/bold]           - See popular items")

    # Show recent activity if in project
    project_root = Path.cwd()
    if (project_root / ".super").exists():
        _show_project_context()
    else:
        console.print(
            "\n[dim]💡 Run in a project directory for personalized recommendations[/dim]"
        )


def browse_marketplace(args):
    """Browse marketplace by category."""
    item_type = getattr(args, "type", None)

    if item_type == "agents":
        browse_agents(args)
    elif item_type == "tools":
        browse_tools(args)
    elif item_type == "industries":
        browse_industries(args)
    elif item_type == "categories":
        browse_categories(args)
    else:
        console.print(
            "[red]❌ Please specify what to browse: agents, tools, industries, or categories[/]"
        )
        console.print("[cyan]💡 Examples:[/]")
        console.print("   [bold]super marketplace browse agents[/bold]")
        console.print(
            "   [bold]super marketplace browse tools --category research[/bold]"
        )


def browse_agents(args):
    """Browse agents with enhanced filtering."""
    # Import existing agent list functionality
    from .agent import list_pre_built_agents

    console.print("🤖 [bold bright_cyan]Marketplace: Agents[/bold bright_cyan]")
    console.print("═" * 50)

    # Show additional marketplace-specific context
    if hasattr(args, "industry") and args.industry:
        console.print(f"🏢 [cyan]Filtering by industry:[/cyan] {args.industry}")

    # Use existing agent listing with enhancements
    list_pre_built_agents(args)

    # Add marketplace-specific quick actions
    console.print("\n[cyan]🛍️ Marketplace Actions:[/cyan]")
    console.print(
        "   [bold]super marketplace show <agent_name>[/bold]    - View detailed info"
    )
    console.print(
        "   [bold]super marketplace deps <agent_name>[/bold]    - Check tool dependencies"
    )
    console.print(
        "   [bold]super marketplace install agent <name>[/bold] - Quick install (same as super agent pull)"
    )


def browse_tools(args):
    """Browse available DSPy tools."""
    try:
        from ...tools.tool_registry import get_tool_registry
    except ImportError:
        console.print("[red]❌ Tool registry not available[/]")
        return

    console.print("🛠️ [bold bright_yellow]Marketplace: Tools[/bold bright_yellow]")
    console.print("═" * 50)

    registry = get_tool_registry()
    category_filter = getattr(args, "category", None)

    # Get tools with filtering
    if category_filter:
        console.print(f"📂 [yellow]Filtering by category:[/yellow] {category_filter}")
        tools = registry.get_tools_by_category(category_filter)
    else:
        tools = registry.list_tools()
        # Show categories overview first
        categories = registry.list_categories()
        console.print(f"📂 [yellow]Available Categories ({len(categories)}):[/yellow]")

        cat_table = Table(show_header=False, box=None)
        # Create category items with counts
        cat_items = [
            (cat, len(registry.get_tools_by_category(cat))) for cat in categories
        ]

        # Display categories in columns
        rows = [cat_items[i : i + 3] for i in range(0, len(cat_items), 3)]
        for row in rows:
            cat_table.add_row(
                *[
                    f"• [blue]{cat.replace('_', ' ').title()}[/blue] ({count})"
                    for cat, count in row
                ]
            )
        console.print(cat_table)
        console.print()

    if not tools:
        console.print("[yellow]No tools found matching criteria.[/]")
        return

    # Display tools table
    table = Table(title="🛠️ Available Tools", border_style="yellow")
    table.add_column("Name", style="bold yellow")
    table.add_column("Category", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Industry", style="green")
    table.add_column("Tags", style="dim")

    for tool_name in tools:
        metadata = registry.get_tool_metadata(tool_name)
        if metadata:
            table.add_row(
                metadata.name,
                metadata.category.replace("_", " ").title(),
                metadata.description[:50] + "..."
                if len(metadata.description) > 50
                else metadata.description,
                metadata.industry,
                ", ".join(metadata.tags[:3]) if metadata.tags else "N/A",
            )

    console.print(table)

    # Show tool count and actions
    console.print(f"\n[bright_green]✅ Found {len(tools)} tool(s)[/bright_green]")
    console.print("\n[cyan]🛍️ Marketplace Actions:[/cyan]")
    console.print(
        "   [bold]super marketplace show <tool_name>[/bold]     - View detailed info"
    )
    console.print(
        "   [bold]super marketplace examples <tool_name>[/bold] - See usage examples"
    )
    if not category_filter:
        console.print(
            "   [bold]super marketplace browse tools --category <name>[/bold] - Filter by category"
        )


def browse_industries(args):
    """Show agent industries overview."""
    package_root = Path(__file__).parent.parent.parent
    agents_dir = package_root / "agents"

    if not agents_dir.exists():
        console.print("[red]❌ Agents directory not found[/]")
        return

    console.print(
        "🏢 [bold bright_magenta]Marketplace: Industries[/bold bright_magenta]"
    )
    console.print("═" * 50)

    industries = {}
    for industry_dir in agents_dir.iterdir():
        if industry_dir.is_dir():
            agent_count = len(list(industry_dir.glob("*_playbook.yaml")))
            if agent_count > 0:
                industries[industry_dir.name] = agent_count

    # Create industry table
    table = Table(title="🏢 Industries & Agent Counts", border_style="magenta")
    table.add_column("Industry", style="bold magenta")
    table.add_column("Agents", style="cyan")
    table.add_column("Browse", style="green")

    for industry, count in sorted(industries.items()):
        industry_display = industry.replace("_", " ").title()
        browse_cmd = f"super market browse agents --industry {industry}"
        table.add_row(industry_display, str(count), browse_cmd)

    console.print(table)
    console.print(
        f"\n[bright_green]✅ {len(industries)} industries • {sum(industries.values())} total agents[/bright_green]"
    )


def browse_categories(args):
    """Show tool categories overview."""
    from ..tools.tool_registry import get_registry

    console.print(
        "📂 [bold bright_blue]Marketplace: Tool Categories[/bold bright_blue]"
    )
    console.print("═" * 50)

    registry = get_registry()
    categories = registry.get_tools_by_category()

    # Create categories table
    table = Table(title="📂 Tool Categories", border_style="blue")
    table.add_column("Category", style="bold blue")
    table.add_column("Tools", style="cyan")
    table.add_column("Examples", style="yellow")
    table.add_column("Browse", style="green")

    for category, tool_list in sorted(categories.items()):
        category_display = category.replace("_", " ").title()
        examples = ", ".join(tool_list[:2])
        if len(tool_list) > 2:
            examples += f" + {len(tool_list) - 2} more"
        browse_cmd = f"super market browse tools --category {category}"
        table.add_row(category_display, str(len(tool_list)), examples, browse_cmd)

    console.print(table)
    console.print(
        f"\n[bright_green]✅ {len(categories)} categories • {sum(len(tools) for tools in categories.values())} total tools[/bright_green]"
    )


def search_marketplace(args):
    """Universal search across agents and tools."""
    query = args.query
    console.print(
        f"🔍 [bold bright_cyan]Marketplace Search:[/bold bright_cyan] '{query}'"
    )
    console.print("═" * 60)

    # Search agents
    agent_results = _search_agents(query)
    tool_results = _search_tools(query)

    total_results = len(agent_results) + len(tool_results)

    if total_results == 0:
        console.print("[yellow]No results found.[/]")
        console.print("\n[cyan]💡 Try:[/cyan]")
        console.print("   • Broader search terms")
        console.print(
            "   • Browse by category: [bold]super marketplace browse agents[/bold]"
        )
        console.print(
            "   • Browse by industry: [bold]super marketplace browse industries[/bold]"
        )
        return

    console.print(f"[bright_green]✅ Found {total_results} result(s)[/bright_green]\n")

    # Show agent results
    if agent_results:
        console.print("🤖 [bold cyan]Agents[/bold cyan]")
        agent_table = Table(
            show_header=True, header_style="bold cyan", border_style="cyan"
        )
        agent_table.add_column("Name", style="yellow")
        agent_table.add_column("Industry", style="cyan")
        agent_table.add_column("Type", style="green")
        agent_table.add_column("Install", style="bold blue")

        for agent in agent_results[:5]:  # Show top 5
            agent_table.add_row(
                agent["name"],
                agent["industry"].replace("_", " ").title(),
                agent["type"],
                f"super marketplace install agent {agent['ref']}",
            )

        console.print(agent_table)
        if len(agent_results) > 5:
            console.print(f"[dim]... and {len(agent_results) - 5} more agents[/dim]")
        console.print()

    # Show tool results
    if tool_results:
        console.print("🛠️ [bold yellow]Tools[/bold yellow]")
        tool_table = Table(
            show_header=True, header_style="bold yellow", border_style="yellow"
        )
        tool_table.add_column("Name", style="bold yellow")
        tool_table.add_column("Category", style="cyan")
        tool_table.add_column("Description", style="white")

        for tool in tool_results:
            tool_table.add_row(
                tool["name"],
                tool["category"].replace("_", " ").title(),
                tool["description"][:60] + "..."
                if len(tool["description"]) > 60
                else tool["description"],
            )

        console.print(tool_table)
        console.print()

    # Quick actions
    console.print("[cyan]🔍 Search Actions:[/cyan]")
    console.print(
        "   [bold]super marketplace show <name>[/bold]    - View detailed info"
    )
    console.print(
        "   [bold]super marketplace install <type> <name>[/bold] - Install component"
    )


def show_component(args):
    """Show detailed information about a specific component."""
    name = args.name

    # Try to find as tool first
    try:
        from ...tools.tool_registry import get_registry

        registry = get_registry()
        tool_metadata = registry.get_tool_metadata(name)
    except ImportError:
        tool_metadata = None

    if tool_metadata:
        _show_tool_details(tool_metadata)
        return

    # Try to find as agent
    agent_info = _find_agent_by_name(name)
    if agent_info:
        _show_agent_details(agent_info)
        return

    console.print(f"[red]❌ Component '{name}' not found in marketplace[/]")
    console.print("\n[cyan]💡 Try:[/cyan]")
    console.print(f"   [bold]super marketplace search {name}[/bold]")
    console.print("   [bold]super marketplace browse agents[/bold]")
    console.print("   [bold]super marketplace browse tools[/bold]")


def show_featured(args):
    """Show featured/popular components."""
    console.print(
        "⭐ [bold bright_green]Marketplace: Featured Components[/bold bright_green]"
    )
    console.print("═" * 55)

    # Curated featured items
    featured_agents = [
        {
            "name": "developer",
            "industry": "software",
            "reason": "Most versatile coding assistant",
        },
        {
            "name": "financial_advisor",
            "industry": "finance",
            "reason": "Popular for financial analysis",
        },
        {
            "name": "content_creator",
            "industry": "marketing",
            "reason": "Great for content generation",
        },
    ]

    featured_tools = [
        {
            "name": "WebSearchTool",
            "category": "research",
            "reason": "Essential for information gathering",
        },
        {
            "name": "CalculatorTool",
            "category": "computation",
            "reason": "Most used mathematical tool",
        },
        {
            "name": "FileReaderTool",
            "category": "data_access",
            "reason": "Critical for document processing",
        },
    ]

    # Featured agents
    console.print("🤖 [bold cyan]Featured Agents[/bold cyan]")
    agent_table = Table(border_style="cyan")
    agent_table.add_column("Agent", style="yellow")
    agent_table.add_column("Industry", style="cyan")
    agent_table.add_column("Why Featured", style="green")
    agent_table.add_column("Install", style="bold blue")

    for agent in featured_agents:
        agent_table.add_row(
            agent["name"],
            agent["industry"].title(),
            agent["reason"],
            f"super marketplace install agent {agent['name']}",
        )

    console.print(agent_table)
    console.print()

    # Featured tools
    console.print("🛠️ [bold yellow]Featured Tools[/bold yellow]")
    tool_table = Table(border_style="yellow")
    tool_table.add_column("Tool", style="bold yellow")
    tool_table.add_column("Category", style="cyan")
    tool_table.add_column("Why Featured", style="green")

    for tool in featured_tools:
        tool_table.add_row(
            tool["name"], tool["category"].replace("_", " ").title(), tool["reason"]
        )

    console.print(tool_table)

    console.print("\n[cyan]⭐ Featured Actions:[/cyan]")
    console.print(
        "   [bold]super marketplace show <name>[/bold]    - View detailed info"
    )
    console.print(
        "   [bold]super marketplace install <type> <name>[/bold] - Install component"
    )


def install_component(args):
    """Install a component (convenience wrapper)."""
    component_type = args.type
    name = args.name

    if component_type == "agent":
        console.print(f"🤖 [cyan]Installing agent '{name}' via marketplace...[/cyan]")
        from .agent import add_agent

        # Create args object for add_agent
        class AgentArgs:
            def __init__(self, name):
                self.name = name
                self.tier = "oracle"
                self.force = False

        add_agent(AgentArgs(name))

    elif component_type == "tool":
        console.print(f"🛠️ [yellow]Installing tool '{name}' via marketplace...[/yellow]")
        console.print(
            "[dim]Note: Tools are automatically available once installed. No additional setup needed.[/dim]"
        )

    else:
        console.print(f"[red]❌ Unknown component type: {component_type}[/]")
        console.print("[cyan]💡 Use: agent or tool[/cyan]")


# Helper functions
def _get_agent_stats():
    """Get agent statistics."""
    package_root = Path(__file__).parent.parent.parent
    agents_dir = package_root / "agents"

    stats = {
        "total": 0,
        "industries": 0,
        "oracle": 0,
        "genie": 0,
        "autonomous": 0,
        "supervised": 0,
    }

    if agents_dir.exists():
        industries = 0
        for industry_dir in agents_dir.iterdir():
            if industry_dir.is_dir():
                playbooks = list(industry_dir.glob("*_playbook.yaml"))
                if playbooks:
                    industries += 1
                    for playbook in playbooks:
                        try:
                            with open(playbook) as f:
                                data = yaml.safe_load(f)
                                if data and "metadata" in data:
                                    stats["total"] += 1
                                    # Analyze metadata
                                    meta = data["metadata"]
                                    if meta.get("level") == "oracle":
                                        stats["oracle"] += 1
                                    elif meta.get("level") == "genie":
                                        stats["genie"] += 1

                                    if meta.get("agent_type") == "Autonomous":
                                        stats["autonomous"] += 1
                                    else:
                                        stats["supervised"] += 1
                        except:
                            continue

        stats["industries"] = industries

    return stats


def _get_tool_stats():
    """Get tool statistics."""
    try:
        from ...tools.tool_registry import get_tool_registry

        registry = get_tool_registry()
        stats = registry.get_registry_stats()

        return {"total": stats["total_tools"], "categories": stats["categories"]}
    except ImportError:
        return {"total": 0, "categories": 0}


def _show_project_context():
    """Show project-specific marketplace context."""
    try:
        project_root = Path.cwd()
        with open(project_root / ".super") as f:
            project_name = yaml.safe_load(f).get("project")

        # Count project agents
        agents_dir = project_root / project_name / "agents"
        project_agent_count = 0
        if agents_dir.exists():
            project_agent_count = len(list(agents_dir.rglob("*_playbook.yaml")))

        console.print(
            f"\n[dim]📋 Current Project: {project_name} ({project_agent_count} agents)[/dim]"
        )

    except:
        pass


def _search_agents(query):
    """Search agents by name, description, industry."""
    package_root = Path(__file__).parent.parent.parent
    agents_dir = package_root / "agents"

    results = []
    query_lower = query.lower()

    if agents_dir.exists():
        for playbook_file in agents_dir.rglob("*_playbook.yaml"):
            try:
                with open(playbook_file) as f:
                    data = yaml.safe_load(f)
                    if data and "metadata" in data:
                        meta = data["metadata"]
                        # Check if query matches
                        if (
                            query_lower in meta.get("name", "").lower()
                            or query_lower in meta.get("description", "").lower()
                            or query_lower in meta.get("namespace", "").lower()
                            or query_lower in playbook_file.stem.lower()
                        ):
                            results.append(
                                {
                                    "name": meta.get("name", "Unknown"),
                                    "industry": meta.get("namespace", "unknown"),
                                    "type": meta.get("agent_type", "Unknown"),
                                    "ref": playbook_file.stem.replace("_playbook", ""),
                                }
                            )
            except:
                continue

    return results


def _search_tools(query):
    """Search tools by name, description, category."""
    try:
        from ...tools.tool_registry import get_tool_registry

        registry = get_tool_registry()
        matching_tools = registry.search_tools(query)

        results = []
        for tool_name in matching_tools:
            metadata = registry.get_tool_metadata(tool_name)
            if metadata:
                results.append(
                    {
                        "name": metadata.name,
                        "category": metadata.category,
                        "description": metadata.description,
                    }
                )

        return results
    except ImportError:
        return []


def _find_agent_by_name(name):
    """Find agent by name or reference."""
    package_root = Path(__file__).parent.parent.parent
    agents_dir = package_root / "agents"

    if agents_dir.exists():
        # Try exact playbook match first
        playbook_path = None
        for potential_path in agents_dir.rglob(f"{name}_playbook.yaml"):
            playbook_path = potential_path
            break

        if not playbook_path:
            # Try searching by metadata name
            for playbook_file in agents_dir.rglob("*_playbook.yaml"):
                try:
                    with open(playbook_file) as f:
                        data = yaml.safe_load(f)
                        if data and "metadata" in data:
                            if data["metadata"].get("name", "").lower() == name.lower():
                                playbook_path = playbook_file
                                break
                except:
                    continue

        if playbook_path:
            try:
                with open(playbook_path) as f:
                    data = yaml.safe_load(f)
                    return {
                        "path": playbook_path,
                        "data": data,
                        "ref": playbook_path.stem.replace("_playbook", ""),
                    }
            except:
                pass

    return None


def _show_tool_details(metadata):
    """Show detailed tool information."""
    console.print(f"🛠️ [bold bright_yellow]{metadata.name}[/bold bright_yellow]")
    console.print("═" * 60)

    # Basic info panel
    info_content = f"""[bold]Description:[/] {metadata.description}

[bold]Category:[/] {metadata.category.replace("_", " ").title()}
[bold]Industry:[/] {metadata.industry}
[bold]Tags:[/] {", ".join(metadata.tags) if metadata.tags else "None"}"""

    console.print(
        Panel(info_content, title="📋 Tool Information", border_style="yellow")
    )

    # Tags and capabilities
    if metadata.tags:
        console.print("\n🏷️ [bold]Tags[/bold]")
        tag_text = " ".join([f"[blue]#{tag}[/blue]" for tag in metadata.tags])
        console.print(tag_text)

    # Usage info
    console.print("\n📖 [bold]Usage Information[/bold]")
    usage_content = f"""This tool can be created using the factory function:
[cyan]from superoptix.tools import create_tool_by_name
tool = create_tool_by_name('{metadata.name}')[/cyan]

Or import the class directly:
[cyan]from superoptix.tools.categories.{metadata.category.lower()} import {metadata.name.replace("_", "").title()}Tool[/cyan]"""
    console.print(Panel(usage_content, border_style="green"))

    # Quick actions
    console.print("\n[cyan]🔗 Related Actions:[/cyan]")
    console.print(
        f"   [bold]super marketplace browse tools --category {metadata.category.lower()}[/bold] - Similar tools"
    )
    console.print(
        f"   [bold]super marketplace search {metadata.industry}[/bold] - Industry tools"
    )


def _show_agent_details(agent_info):
    """Show detailed agent information."""
    data = agent_info["data"]
    metadata = data.get("metadata", {})
    spec = data.get("spec", {})

    console.print(
        f"🤖 [bold bright_cyan]{metadata.get('name', 'Unknown Agent')}[/bold bright_cyan]"
    )
    console.print("═" * 60)

    # Basic info panel
    info_content = f"""[bold]Description:[/] {metadata.get("description", "No description available")}

[bold]Industry:[/] {metadata.get("namespace", "Unknown").replace("_", " ").title()}
[bold]Type:[/] {metadata.get("agent_type", "Unknown")}
        [bold]Tier Level:[/] {metadata.get("level", "oracle")}
[bold]Version:[/] {metadata.get("version", "1.0.0")}
[bold]License:[/] {metadata.get("license", "MIT")}"""

    console.print(
        Panel(info_content, title="📋 Agent Information", border_style="cyan")
    )

    # Capabilities
    capabilities = spec.get("capabilities", [])
    if capabilities:
        console.print("\n🎯 [bold]Capabilities[/bold]")
        cap_table = Table(border_style="green")
        cap_table.add_column("Capability", style="cyan")
        cap_table.add_column("Description", style="white")

        for cap in capabilities[:5]:  # Show top 5
            cap_table.add_row(
                cap.get("name", "Unknown"), cap.get("description", "No description")
            )

        console.print(cap_table)
        if len(capabilities) > 5:
            console.print(
                f"[dim]... and {len(capabilities) - 5} more capabilities[/dim]"
            )

    # Dependencies
    dependencies = spec.get("dependencies", {})
    if dependencies.get("tools") or dependencies.get("apis"):
        console.print("\n🔗 [bold]Dependencies[/bold]")
        dep_table = Table(border_style="yellow")
        dep_table.add_column("Type", style="yellow")
        dep_table.add_column("Dependency", style="white")

        for tool in dependencies.get("tools", []):
            dep_table.add_row("Tool", tool)
        for api in dependencies.get("apis", []):
            dep_table.add_row("API", api)

        console.print(dep_table)

    # Quick actions
    console.print("\n[cyan]🚀 Agent Actions:[/cyan]")
    console.print(
        f"   [bold]super marketplace install agent {agent_info['ref']}[/bold] - Add to project"
    )
    console.print(
        f"   [bold]super marketplace deps {agent_info['ref']}[/bold] - Check dependencies"
    )
    console.print(
        f"   [bold]super marketplace search {metadata.get('namespace', '')}[/bold] - Similar agents"
    )
