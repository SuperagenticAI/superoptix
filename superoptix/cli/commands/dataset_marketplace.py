"""
Dataset marketplace CLI commands - browse and pull example datasets
"""

from pathlib import Path
import shutil
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def list_example_datasets(args):
    """List available example datasets."""
    try:
        # Find example datasets in installed SuperOptiX
        import superoptix

        examples_dir = Path(superoptix.__file__).parent / "datasets" / "examples"

        if not examples_dir.exists():
            console.print("\n[yellow]No example datasets found.[/yellow]")
            return

        # Find all dataset files
        datasets = []

        # CSV files
        for csv_file in examples_dir.glob("*.csv"):
            datasets.append(
                {
                    "name": csv_file.stem,
                    "format": "CSV",
                    "file": csv_file.name,
                    "size": f"{csv_file.stat().st_size / 1024:.1f} KB",
                }
            )

        # JSON files
        for json_file in examples_dir.glob("*.json"):
            datasets.append(
                {
                    "name": json_file.stem,
                    "format": "JSON",
                    "file": json_file.name,
                    "size": f"{json_file.stat().st_size / 1024:.1f} KB",
                }
            )

        # JSONL files
        for jsonl_file in examples_dir.glob("*.jsonl"):
            datasets.append(
                {
                    "name": jsonl_file.stem,
                    "format": "JSONL",
                    "file": jsonl_file.name,
                    "size": f"{jsonl_file.stat().st_size / 1024:.1f} KB",
                }
            )

        # Parquet files
        for parquet_file in examples_dir.glob("*.parquet"):
            datasets.append(
                {
                    "name": parquet_file.stem,
                    "format": "Parquet",
                    "file": parquet_file.name,
                    "size": f"{parquet_file.stat().st_size / 1024:.1f} KB",
                }
            )

        if not datasets:
            console.print("\n[yellow]No example datasets found.[/yellow]")
            return

        # Display as table
        console.print("\n[bold cyan]📊 Available Example Datasets[/bold cyan]\n")

        table = Table(box=box.ROUNDED, title=f"Found {len(datasets)} Example Datasets")
        table.add_column("Name", style="cyan")
        table.add_column("Format", style="yellow")
        table.add_column("File", style="white")
        table.add_column("Size", style="green")

        for ds in sorted(datasets, key=lambda x: x["name"]):
            table.add_row(ds["name"], ds["format"], ds["file"], ds["size"])

        console.print(table)

        console.print("\n[dim]💡 Pull a dataset:[/dim]")
        console.print("   [cyan]super dataset pull <dataset_name>[/cyan]")
        console.print("\n[dim]📖 Or reference directly in your playbook:[/dim]")
        console.print(f"   [dim]source: {examples_dir}/<filename>[/dim]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")


def pull_example_dataset(args):
    """Pull an example dataset to your project."""
    try:
        dataset_name = args.name

        # Find dataset in examples
        import superoptix

        examples_dir = Path(superoptix.__file__).parent / "datasets" / "examples"

        # Look for file with any extension
        found_file = None
        for ext in [".csv", ".json", ".jsonl", ".parquet"]:
            candidate = examples_dir / f"{dataset_name}{ext}"
            if candidate.exists():
                found_file = candidate
                break

        if not found_file:
            console.print(
                f"\n[bold red]❌ Dataset '{dataset_name}' not found.[/bold red]"
            )
            console.print("\n[yellow]💡 See available datasets:[/yellow]")
            console.print("   [cyan]super dataset list[/cyan]")
            return

        # Create data directories in project
        project_root = Path.cwd()
        super_file = project_root / ".super"

        data_dirs = [project_root / "data"]
        if super_file.exists():
            with open(super_file) as f:
                project_name = yaml.safe_load(f).get("project")
                if project_name:
                    legacy_dir = project_root / project_name / "data"
                    if legacy_dir not in data_dirs:
                        data_dirs.append(legacy_dir)

        copied_paths = []
        for target_dir in data_dirs:
            target_dir.mkdir(parents=True, exist_ok=True)
            dest_path = target_dir / found_file.name
            shutil.copy(found_file, dest_path)
            copied_paths.append(dest_path)

        primary_dest = copied_paths[0]
        console.print(
            f"\n[bold green]✅ Dataset '{dataset_name}' pulled successfully![/bold green]"
        )
        console.print(f"   📁 Location: {primary_dest}")
        console.print(f"   📊 Format: {found_file.suffix.replace('.', '').upper()}")
        console.print(f"   💾 Size: {primary_dest.stat().st_size / 1024:.1f} KB")
        if len(copied_paths) > 1:
            for extra_path in copied_paths[1:]:
                console.print(f"   ↪️  Also available at: {extra_path}")

        # Show usage example
        console.print("\n[bold cyan]💡 How to use:[/bold cyan]")

        # Determine mapping based on file
        if "sentiment" in dataset_name:
            mapping_example = "mapping: {input: text, output: label}"
            input_field = "text"
            output_field = "sentiment"
        elif "qa" in dataset_name:
            mapping_example = "mapping: {input: question, output: answer}"
            input_field = "question"
            output_field = "answer"
        elif "classification" in dataset_name:
            mapping_example = "mapping: {input: text, output: category}"
            input_field = "text"
            output_field = "category"
        else:
            mapping_example = "mapping: {input: <column>, output: <column>}"
            input_field = "input_field"
            output_field = "output_field"

        usage = f"""
Add to your agent playbook:

```yaml
spec:
  datasets:
    - name: {dataset_name}
      source: ./data/{found_file.name}
      format: {found_file.suffix.replace(".", "")}
      {mapping_example}
      input_field_name: {input_field}
      output_field_name: {output_field}
```

Then:
  super agent compile <your_agent>
  super agent dataset preview <your_agent>
  super agent evaluate <your_agent>
"""

        console.print(
            Panel(usage.strip(), title="📝 Usage Example", border_style="cyan")
        )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")


def show_dataset_details(args):
    """Show details about an example dataset."""
    try:
        dataset_name = args.name

        # Find dataset
        import superoptix

        examples_dir = Path(superoptix.__file__).parent / "datasets" / "examples"

        found_file = None
        for ext in [".csv", ".json", ".jsonl", ".parquet"]:
            candidate = examples_dir / f"{dataset_name}{ext}"
            if candidate.exists():
                found_file = candidate
                break

        if not found_file:
            console.print(
                f"\n[bold red]❌ Dataset '{dataset_name}' not found.[/bold red]"
            )
            return

        # Load and analyze
        from superoptix.datasets.loader import DatasetLoader

        # Create temp config
        if "sentiment" in dataset_name:
            mapping = {"input": "text", "output": "label"}
        elif "qa" in dataset_name:
            mapping = {"input": "question", "output": "answer"}
        elif "classification" in dataset_name:
            mapping = {"input": "text", "output": "category"}
        else:
            mapping = {"input": "text", "output": "label"}

        config = {
            "name": dataset_name,
            "source": str(found_file),
            "format": found_file.suffix.replace(".", ""),
            "mapping": mapping,
        }

        loader = DatasetLoader(config)
        stats = loader.get_stats()
        records = loader.load()

        # Display info
        console.print(f"\n[bold cyan]📊 Dataset: {dataset_name}[/bold cyan]\n")

        info = f"""[bold]Name:[/bold] {stats["name"]}
[bold]Format:[/bold] {stats["format"].upper()}
[bold]File:[/bold] {found_file.name}
[bold]Size:[/bold] {found_file.stat().st_size / 1024:.1f} KB
[bold]Total Examples:[/bold] {stats["total_examples"]}
[bold]Input Fields:[/bold] {", ".join(stats.get("input_fields", []))}
[bold]Output Fields:[/bold] {", ".join(stats.get("output_fields", []))}"""

        console.print(Panel(info, border_style="cyan"))

        # Show sample
        console.print("\n[bold yellow]📝 Sample Data (first 3):[/bold yellow]\n")

        table = Table(box=box.SIMPLE)
        table.add_column("#", style="cyan")

        if records:
            for key in records[0]["input"].keys():
                table.add_column(f"Input: {key}", style="yellow")
            for key in records[0]["output"].keys():
                table.add_column(f"Output: {key}", style="green")

            for i, record in enumerate(records[:3]):
                row = [str(i + 1)]
                for val in record["input"].values():
                    val_str = str(val)
                    row.append(val_str[:50] + "..." if len(val_str) > 50 else val_str)
                for val in record["output"].values():
                    row.append(str(val))
                table.add_row(*row)

            console.print(table)

        # Show how to pull
        console.print(f"\n[dim]💡 Pull this dataset:[/dim]")
        console.print(f"   [cyan]super dataset pull {dataset_name}[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
