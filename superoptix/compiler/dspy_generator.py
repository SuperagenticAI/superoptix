import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jinja2 import Environment, FileSystemLoader

from ..models.tier_system import TierLevel, tier_system


class DSPyOraclesPipelineGenerator:
    """Generates DSPy pipeline code from playbook."""

    def __init__(
        self,
        agent_name: str,
        template_path: Optional[Path] = None,
        user_tier: TierLevel = TierLevel.ORACLES,
    ):
        """Initialize generator with agent name, template path, and user tier."""
        self.agent_name = agent_name
        self.user_tier = user_tier
        self.project_root = self._find_project_root()
        self.template_path = template_path or (
            Path(__file__).parent.parent
            / "templates"
            / "pipeline"
            / "dspy_oracles_pipeline.py.jinja2"
        )

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found at {self.template_path}")

    def _find_project_root(self) -> Path:
        """Find project root by looking for .super file."""
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".super").exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError("Could not find .super file")

    def _get_system_name(self) -> str:
        """Get system name from project root path."""
        try:
            # First try to get the system name from the .super file
            with open(self.project_root / ".super") as f:
                config = yaml.safe_load(f)
                if "system" in config:
                    # Return raw system name without prefix
                    return config["system"]
        except Exception:
            # Silently ignore and fallback to directory search
            pass

        # Fallback to directory search
        for item in self.project_root.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and not item.name == "superoptix"
                and "semantic" in item.name
            ):
                return "semantic"  # Just return 'semantic' as system name

        raise FileNotFoundError(
            "Could not find semantic system directory in project root"
        )

    def _load_playbook(self) -> Dict[str, Any]:
        """Load agent playbook."""
        try:
            """Load agent playbook from yaml file."""
            with open(self.project_root / ".super") as f:
                system_name = yaml.safe_load(f).get("project")

            playbook_path = (
                self.project_root
                / f"{system_name}"
                / "agents"
                / self.agent_name.lower()
                / "playbook"
                / f"{self.agent_name.lower()}_playbook.yaml"
            )

            if not playbook_path.exists():
                raise FileNotFoundError(f"Playbook not found at {playbook_path}")

            with open(playbook_path) as f:
                return yaml.safe_load(f)

        except Exception as e:
            raise RuntimeError(f"Failed to load playbook: {str(e)}") from e

    def _format_docstring(self, text: str) -> str:
        """Format multiline text as proper docstring."""
        if not text:
            return ""
        lines = text.strip().split("\n")
        return "\n        ".join(lines)

    def _format_type(self, type_str: str) -> str:
        """Convert YAML type to Python type."""
        type_mapping = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "List",
            "dict": "Dict[str, Any]",
        }
        return type_mapping.get(type_str, type_str)

    def _format_validation(self, validation: Dict) -> str:
        """Format validation rules as Pydantic validators."""
        if not validation:
            return ""

        rules = []
        if "min_length" in validation:
            rules.append(f"min_length={validation['min_length']}")
        if "max_length" in validation:
            rules.append(f"max_length={validation['max_length']}")
        if "regex" in validation:
            rules.append(f"regex='{validation['regex']}'")

        return ", ".join(rules)

    def _prepare_template_context(self, playbook: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for template rendering with proper formatting."""
        try:
            # Extract data following new playbook schema
            metadata = playbook.get("metadata", {})
            spec = playbook.get("spec", {})

            context = {
                "agent_name": metadata.get("name", self.agent_name),
                "agent_id": metadata.get("id", self.agent_name.lower()),
                "metadata": metadata,
                "spec": spec,
                "lm_config": spec.get("language_model", {}),
                "tasks": spec.get("tasks", []),
                "evaluation": spec.get("evaluation", {}),
                "optimization": spec.get("optimization", {}),
                "examples": playbook.get("examples", {}),
                "RAG_AVAILABLE": True,  # Enable RAG support in templates
            }

            # Format examples for the template
            feature_spec = spec.get("feature_specifications", {})
            context["scenarios"] = feature_spec.get("scenarios", [])

            # Extract input/output fields from first task for signature generation
            tasks = spec.get("tasks", [])
            if tasks and len(tasks) > 0:
                first_task = tasks[0]
                spec["input_fields"] = first_task.get("inputs", [])
                spec["output_fields"] = first_task.get("outputs", [])

            # Ensure all required validation fields are available in context
            if not context["evaluation"]:
                context["evaluation"] = {
                    "builtin_metrics": [
                        {"name": "answer_correctness", "threshold": 0.7}
                    ],
                    "threshold": 0.7,
                }

            if not context["optimization"]:
                context["optimization"] = {
                    "strategy": "few_shot_bootstrapping",
                    "metric": "answer_correctness",
                }

            # Validate required fields - now more lenient for basic functionality
            required_fields = ["metadata", "spec"]
            missing_fields = [
                field for field in required_fields if not context.get(field)
            ]

            if missing_fields:
                raise ValueError(
                    f"Missing critical fields in playbook: {', '.join(missing_fields)}"
                )

            # Ensure tasks exist with proper structure
            if not context["tasks"]:
                # Create default task structure for backward compatibility
                context["tasks"] = [
                    {
                        "name": "default_task",
                        "inputs": [
                            {
                                "name": "query",
                                "type": "str",
                                "description": "User input",
                            }
                        ],
                        "outputs": [
                            {
                                "name": "response",
                                "type": "str",
                                "description": "Generated response",
                            }
                        ],
                    }
                ]

            # Format multiline strings
            for task in context["tasks"]:
                if "description" in task:
                    task["description"] = self._format_docstring(task["description"])
                if "instruction" in task:
                    task["instruction"] = self._format_docstring(task["instruction"])

            # Format persona fields if present
            if "persona" in spec:
                persona = spec["persona"]
                if "backstory" in persona:
                    persona["backstory"] = self._format_docstring(persona["backstory"])
                if "job_description" in persona:
                    persona["job_description"] = self._format_docstring(
                        persona["job_description"]
                    )

            # Clean up formatted strings by removing multiple newlines
            def clean_text(text: str) -> str:
                if not text:
                    return ""
                # Replace multiple newlines with single newline
                text = re.sub(r"\n\s*\n", "\n", text)
                # Remove trailing whitespace from each line
                text = "\n".join(line.rstrip() for line in text.split("\n"))
                return text

            # Apply cleaning to all text fields
            for task in context["tasks"]:
                if "description" in task:
                    task["description"] = clean_text(task["description"])
                if "instruction" in task:
                    task["instruction"] = clean_text(task["instruction"])

            if "persona" in spec:
                persona = spec["persona"]
                if "backstory" in persona:
                    persona["backstory"] = clean_text(persona["backstory"])
                if "job_description" in persona:
                    persona["job_description"] = clean_text(persona["job_description"])

            return context

        except KeyError as e:
            raise ValueError(f"Missing required field in playbook: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to prepare template context: {str(e)}") from e

    def generate(self) -> Path:
        """Generate DSPy pipeline from playbook."""
        try:
            playbook = self._load_playbook()

            # Validate tier access before generating
            tier_issues = tier_system.validate_playbook_features(
                playbook, self.user_tier
            )
            if tier_issues["blocked_features"]:
                self._handle_tier_restrictions(tier_issues)

            context = self._prepare_template_context(playbook)

            # Select appropriate template based on tier and features
            selected_template = self._select_template_for_tier(playbook)

            env = Environment(
                loader=FileSystemLoader(str(selected_template.parent)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )

            # Add custom filters
            env.filters["clean"] = self._clean_text
            env.filters["oneline"] = lambda x: " ".join(str(x).split())

            template = env.get_template(selected_template.name)
            code = template.render(**context)

            # Enhanced cleanup of the generated code for validation compatibility
            code = re.sub(
                r"\n\s*\n\s*\n+", "\n\n", code
            )  # Replace multiple newlines with double
            code = re.sub(r"{\s*\n\s*}", "{}", code)  # Clean empty dicts
            code = re.sub(r"\[\s*\n\s*\]", "[]", code)  # Clean empty lists
            code = re.sub(r",\s*\n\s*}", " }", code)  # Clean trailing commas in dicts
            code = re.sub(r",\s*\n\s*\]", " ]", code)  # Clean trailing commas in lists

            # Fix common validation field issues
            code = re.sub(
                r'result\["is_valid"\]\s*=\s*eval_score\s*>\s*0\.5\s*\n\s*result\["validation_score"\]\s*=\s*eval_score',
                'result["is_valid"] = eval_score > 0.5\n                result["validation_score"] = eval_score',
                code,
            )

            # Ensure proper spacing around validation assignments
            code = re.sub(
                r'result\["([^"]+)"\]\s*=\s*([^\n]+)', r'result["\1"] = \2', code
            )

            # Clean up any malformed template expressions
            code = re.sub(
                r"{%\s*if[^%]*%}[\s\n]*{%\s*endif\s*%}", "", code
            )  # Remove empty if blocks
            code = re.sub(
                r"{%\s*for[^%]*%}[\s\n]*{%\s*endfor\s*%}", "", code
            )  # Remove empty for blocks

            # Format with black if available
            try:
                import black

                code = black.format_str(code, mode=black.FileMode())
            except ImportError:
                # Manual formatting if black is not available
                lines = code.split("\n")
                formatted_lines = []
                indent_level = 0

                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        formatted_lines.append("")
                        continue

                    # Adjust indentation
                    if stripped.startswith(
                        (
                            "def ",
                            "class ",
                            "if ",
                            "for ",
                            "while ",
                            "with ",
                            "try:",
                            "except",
                            "else:",
                            "elif",
                        )
                    ):
                        formatted_lines.append("    " * indent_level + stripped)
                        if stripped.endswith(":"):
                            indent_level += 1
                    elif stripped in ("else:", "elif", "except:", "finally:"):
                        indent_level = max(0, indent_level - 1)
                        formatted_lines.append("    " * indent_level + stripped)
                        indent_level += 1
                    elif stripped.startswith(
                        ("return", "break", "continue", "pass", "raise")
                    ):
                        formatted_lines.append("    " * indent_level + stripped)
                    else:
                        formatted_lines.append("    " * indent_level + stripped)

                code = "\n".join(formatted_lines)
            except Exception as format_error:
                print(f"Warning: Code formatting failed: {format_error}")
                # Continue with unformatted code

            # Get system name from .super file
            with open(self.project_root / ".super") as f:
                system_name = yaml.safe_load(f).get("project")

            # Save pipeline file
            pipeline_dir = (
                self.project_root
                / f"{system_name}"
                / "agents"
                / self.agent_name.lower()
                / "pipeline"
            )
            pipeline_dir.mkdir(parents=True, exist_ok=True)

            pipeline_path = pipeline_dir / f"{self.agent_name.lower()}_pipeline.py"
            pipeline_path.write_text(code)

            print(f"✅ Generated DSPy pipeline: {pipeline_path}")
            return pipeline_path

        except Exception as e:
            print(f"❌ Failed to generate pipeline: {str(e)}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean up formatted strings and normalize whitespace."""
        if not text:
            return ""
        # Remove extra whitespace and normalize newlines
        text = re.sub(
            r"\s*\n\s*\n\s*", "\n", text
        )  # Replace multiple newlines with single
        text = re.sub(r"^\s*\n", "", text)  # Remove leading newlines
        text = re.sub(r"\n\s*$", "", text)  # Remove trailing newlines
        text = re.sub(r"[ \t]+", " ", text)  # Normalize horizontal whitespace
        # Ensure consistent indentation
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(line for line in lines if line)

    def _handle_tier_restrictions(self, tier_issues: Dict[str, list]):
        """Handle tier-restricted features with upgrade messages."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Display blocked features
        console.print("\n[bold red]❌ Tier Restriction Detected[/bold red]")

        blocked_table = Table(title="Blocked Features")
        blocked_table.add_column("Feature", style="cyan")
        blocked_table.add_column("Issue", style="red")

        for issue in tier_issues["blocked_features"]:
            parts = issue.split(" requires ")
            feature = parts[0] if len(parts) > 1 else issue
            requirement = parts[1] if len(parts) > 1 else "Higher tier"
            blocked_table.add_row(feature, f"Requires {requirement}")

        console.print(blocked_table)

        # Show upgrade message
        upgrade_panel = Panel(
            f"""
🚀 **Upgrade Required**

📈 **Your Current Tier:** {self.user_tier.value.title()}
⬆️  **Upgrade to unlock these features**

🔓 **Upgrade Options:**
   • Visit: https://super-agentic.ai/upgrade
   • Email: upgrade@super-agentic.ai
   • Schedule a demo: https://calendly.com/shashikant-super-agentic/30min

💡 **Benefits of upgrading:**
   • Access to advanced DSPy capabilities
   • ReAct agents with tool integration
   • Advanced optimization strategies
   • Priority support and documentation
   • Early access to beta features

🛠️  **Alternative:** You can modify your playbook to use features available in your current tier.
            """,
            title="Upgrade Required",
            border_style="yellow",
        )

        console.print(upgrade_panel)

        # Raise exception to stop generation
        raise RuntimeError(
            f"Tier restrictions prevent generation. Upgrade required for: {', '.join(tier_issues['blocked_features'])}"
        )

    def _select_template_for_tier(self, playbook: Dict[str, Any]) -> Path:
        """Select the appropriate template based on tier and playbook features."""
        spec = playbook.get("spec", {})
        templates_dir = Path(__file__).parent.parent / "templates" / "pipeline"

        # Check if tools are requested (Genie tier feature)
        if spec.get("components", {}).get("tools") and tier_system.check_feature_access(
            "tool_integration", self.user_tier
        ):
            react_template = templates_dir / "dspy_react_pipeline.py.jinja2"
            if react_template.exists():
                return react_template

        # Default to oracles pipeline
        return templates_dir / "dspy_oracles_pipeline.py.jinja2"
