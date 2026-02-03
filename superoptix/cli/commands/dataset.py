"""
Dataset management CLI commands for SuperOptiX
"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def preview_dataset(args):
    """Preview examples from configured datasets."""
    try:
        agent_name = args.name.lower()
        limit = getattr(args, "limit", 5)

        # Find project root
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print("\n[bold red]❌ Not a valid super project.[/bold red]")
            return

        with open(super_file) as f:
            project_name = yaml.safe_load(f).get("project")

        # Load playbook
        playbook_path = (
            project_root
            / project_name
            / "agents"
            / agent_name
            / "playbook"
            / f"{agent_name}_playbook.yaml"
        )
        if not playbook_path.exists():
            console.print(
                f"\n[bold red]❌ Playbook not found: {playbook_path}[/bold red]"
            )
            return

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Get datasets config
        datasets_config = playbook.get("spec", {}).get("datasets", [])

        if not datasets_config:
            console.print(
                f"\n[yellow]No datasets configured for agent '{agent_name}'[/yellow]"
            )
            console.print("\n💡 Add datasets to your playbook:")
            console.print("```yaml")
            console.print("spec:")
            console.print("  datasets:")
            console.print("    - name: training_data")
            console.print("      source: ./data/train.csv")
            console.print("      format: csv")
            console.print("      mapping:")
            console.print("        input: text_column")
            console.print("        output: label_column")
            console.print("```")
            return

        # Load and preview datasets
        from superoptix.datasets.loader import DatasetLoader

        for dataset_config in datasets_config:
            dataset_name = dataset_config.get("name", "unnamed")

            console.print(f"\n[bold cyan]Dataset: {dataset_name}[/bold cyan]")
            console.print(f"Source: {dataset_config.get('source')}")
            console.print(f"Format: {dataset_config.get('format', 'csv')}")

            try:
                loader = DatasetLoader(dataset_config)
                records = loader.load()

                # Create preview table
                table = Table(
                    title=f"Preview: {dataset_name} (showing {min(limit, len(records))} of {len(records)})",
                    box=box.ROUNDED,
                )

                # Add columns based on first record
                if records:
                    first_record = records[0]
                    table.add_column("#", style="cyan", width=4)

                    # Input columns
                    for key in first_record["input"].keys():
                        table.add_column(f"Input: {key}", style="yellow")

                    # Output columns
                    for key in first_record["output"].keys():
                        table.add_column(f"Output: {key}", style="green")

                    # Add rows
                    for i, record in enumerate(records[:limit]):
                        row = [str(i + 1)]

                        # Add input values
                        for val in record["input"].values():
                            val_str = str(val)
                            row.append(
                                val_str[:50] + "..." if len(val_str) > 50 else val_str
                            )

                        # Add output values
                        for val in record["output"].values():
                            val_str = str(val)
                            row.append(
                                val_str[:30] + "..." if len(val_str) > 30 else val_str
                            )

                        table.add_row(*row)

                    console.print(table)
                else:
                    console.print("[yellow]No records found in dataset[/yellow]")

            except Exception as e:
                console.print(f"[red]❌ Error loading dataset: {e}[/red]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")


def validate_dataset(args):
    """Validate dataset configuration in playbook."""
    try:
        agent_name = args.name.lower()

        # Find project root
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print("\n[bold red]❌ Not a valid super project.[/bold red]")
            return

        with open(super_file) as f:
            project_name = yaml.safe_load(f).get("project")

        # Load playbook
        playbook_path = (
            project_root
            / project_name
            / "agents"
            / agent_name
            / "playbook"
            / f"{agent_name}_playbook.yaml"
        )
        if not playbook_path.exists():
            console.print(
                f"\n[bold red]❌ Playbook not found: {playbook_path}[/bold red]"
            )
            return

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Get datasets config
        datasets_config = playbook.get("spec", {}).get("datasets", [])

        if not datasets_config:
            console.print(
                f"\n[yellow]No datasets configured for agent '{agent_name}'[/yellow]"
            )
            return

        # Validate each dataset
        from superoptix.datasets.validators import DatasetValidator

        console.print(
            f"\n[bold cyan]Validating {len(datasets_config)} dataset(s)...[/bold cyan]\n"
        )

        all_valid = True
        for dataset_config in datasets_config:
            dataset_name = dataset_config.get("name", "unnamed")

            is_valid, errors = DatasetValidator.validate_config(dataset_config)

            if is_valid:
                console.print(f"✅ [green]{dataset_name}: Valid[/green]")
            else:
                console.print(f"❌ [red]{dataset_name}: Invalid[/red]")
                for error in errors:
                    console.print(f"   • {error}")
                all_valid = False

        if all_valid:
            console.print(f"\n[bold green]✅ All datasets valid![/bold green]")
        else:
            console.print(
                f"\n[bold red]❌ Some datasets have errors. Fix them before using.[/bold red]"
            )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")


def dataset_info(args):
    """Show statistics about configured datasets."""
    try:
        agent_name = args.name.lower()

        # Find project root
        project_root = Path.cwd()
        super_file = project_root / ".super"
        if not super_file.exists():
            console.print("\n[bold red]❌ Not a valid super project.[/bold red]")
            return

        with open(super_file) as f:
            project_name = yaml.safe_load(f).get("project")

        # Load playbook
        playbook_path = (
            project_root
            / project_name
            / "agents"
            / agent_name
            / "playbook"
            / f"{agent_name}_playbook.yaml"
        )
        if not playbook_path.exists():
            console.print(
                f"\n[bold red]❌ Playbook not found: {playbook_path}[/bold red]"
            )
            return

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Get datasets config
        datasets_config = playbook.get("spec", {}).get("datasets", [])

        if not datasets_config:
            console.print(
                f"\n[yellow]No datasets configured for agent '{agent_name}'[/yellow]"
            )
            return

        # Load and show stats for each dataset
        from superoptix.datasets.loader import DatasetLoader

        console.print(
            f"\n[bold cyan]Dataset Information for: {agent_name}[/bold cyan]\n"
        )

        total_examples = 0
        for dataset_config in datasets_config:
            dataset_name = dataset_config.get("name", "unnamed")

            try:
                loader = DatasetLoader(dataset_config)
                stats = loader.get_stats()

                total_examples += stats["total_examples"]

                # Create info panel
                info = f"""[bold]Name:[/bold] {stats["name"]}
[bold]Source:[/bold] {stats["source"]}
[bold]Format:[/bold] {stats["format"]}
[bold]Total Examples:[/bold] {stats["total_examples"]}
[bold]Split:[/bold] {stats["split"]}
[bold]Shuffled:[/bold] {stats["shuffled"]}"""

                if "limit_applied" in stats:
                    info += f"\n[bold]Limit Applied:[/bold] {stats['limit_applied']}"

                if "input_fields" in stats:
                    info += f"\n[bold]Input Fields:[/bold] {', '.join(stats['input_fields'])}"

                if "output_fields" in stats:
                    info += f"\n[bold]Output Fields:[/bold] {', '.join(stats['output_fields'])}"

                console.print(
                    Panel(info, title=f"📊 {dataset_name}", border_style="cyan")
                )

            except Exception as e:
                console.print(f"[red]❌ Error loading {dataset_name}: {e}[/red]")

        console.print(
            f"\n[bold green]Total Examples Across All Datasets: {total_examples}[/bold green]"
        )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
