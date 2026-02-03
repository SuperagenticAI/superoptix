from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install

install()  # Install rich traceback handler

console = Console()


class PlaybookLinter:
    """Linter for agent playbooks."""

    def __init__(self, playbook_path: Union[str, Path]):
        """Initialize linter with playbook path."""
        self.playbook_path = Path(playbook_path)
        self.playbook: Dict[str, Any] = self._load_playbook()
        self.errors: List[str] = []
        self.tier_spec: Dict[str, Any] = {}

    def _load_playbook(self) -> Dict[str, Any]:
        """Load playbook from file."""
        try:
            with open(self.playbook_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load playbook: {e}") from e

    def _get_tier_spec(self) -> Dict[str, Any]:
        """Load the spec for the agent's tier."""
        level = self.playbook.get("metadata", {}).get("level", "oracles")

        # Validate tier level
        valid_tiers = ["oracles", "genies"]
        if level not in valid_tiers:
            self.errors.append(
                f"Invalid tier '{level}'. Valid options: {', '.join(valid_tiers)}"
            )
            return {}

        spec_path = (
            Path(__file__).parent.parent
            / "examples"
            / "specs"
            / "tiers"
            / f"{level}_spec.yaml"
        )

        if not spec_path.exists():
            self.errors.append(
                f"Spec file for level '{level}' not found at {spec_path}"
            )
            return {}

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load spec for level '{level}': {e}")
            return {}

    def lint(self) -> List[str]:
        """Lint the playbook against its tier-specific spec."""
        self.tier_spec = self._get_tier_spec()
        if not self.tier_spec:
            return self.errors

        self._lint_against_spec(self.tier_spec, self.playbook, "playbook")
        return self.errors

    def _lint_against_spec(
        self, spec: Dict[str, Any], playbook: Dict[str, Any], path: str
    ):
        """Recursively check for required fields."""
        if not isinstance(spec, dict) or not isinstance(playbook, dict):
            return

        for key, value in spec.items():
            if key not in playbook:
                self.errors.append(f"Missing required field: '{path}.{key}'")
            elif isinstance(value, dict):
                self._lint_against_spec(value, playbook[key], f"{path}.{key}")


def display_lint_results(playbook_path: Path, playbook: Dict, errors: List[str]):
    """Display linting results in a formatted way."""
    metadata = playbook.get("metadata", {})

    if not errors:
        result_panel = Panel(
            f"[bold green]✓[/bold green] Success! No linting errors found for agent '{metadata.get('name', 'N/A')}'.",
            title="[bold green]Validation Passed[/bold green]",
            border_style="green",
            expand=False,
        )
        console.print(result_panel)
        return

    error_messages = "\n".join(f"[bold red]✗[/bold red] {error}" for error in errors)
    full_report = f"Found {len(errors)} error(s):\n\n{error_messages}"

    result_panel = Panel(
        full_report,
        title="[bold red]Validation Failed[/bold red]",
        border_style="red",
        expand=False,
    )
    console.print(Panel(f"[bold]File:[/bold] {playbook_path}", expand=False))
    console.print(result_panel)

    console.print("\n[bold]Full Playbook Content:[/bold]")
    yaml_str = yaml.dump(playbook)
    console.print(Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True))
