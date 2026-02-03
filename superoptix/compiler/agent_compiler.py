import re
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


def clean_filter(text):
    """A Jinja2 filter to clean up multiline strings for docstrings."""
    return " ".join(text.strip().split())


def to_pascal_case(text: str) -> str:
    """
    Converts snake_case to PascalCase, preserving compound words.

    Examples:
        research_agent_deepagents -> ResearchAgentDeepAgents
        sentiment_analyzer -> SentimentAnalyzer
    """
    words = text.split("_")
    pascal_words = []

    for word in words:
        # Preserve known compound words/frameworks
        if word.lower() in ["deepagents", "crewai", "openai"]:
            # Keep compound words capitalized properly
            if word.lower() == "deepagents":
                pascal_words.append("DeepAgents")
            elif word.lower() == "crewai":
                pascal_words.append("CrewAI")
            elif word.lower() == "openai":
                pascal_words.append("OpenAI")
            else:
                pascal_words.append(word.capitalize())
        else:
            pascal_words.append(word.capitalize())

    return "".join(pascal_words)


def to_snake_case(text: str) -> str:
    """Converts any text to snake_case for Python compatibility."""
    if not text:
        return text

    # First, strip all whitespace from beginning and end
    text = text.strip()

    # First, handle camelCase and PascalCase
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)

    # Replace spaces, hyphens, and other non-alphanumeric chars with underscores
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text)

    # Convert to lowercase
    text = text.lower()

    # Remove multiple consecutive underscores
    text = re.sub(r"_+", "_", text)

    # Remove leading/trailing underscores
    text = text.strip("_")

    # Ensure it starts with a letter or underscore (Python identifier rules)
    if text and text[0].isdigit():
        text = f"field_{text}"

    return text or "field"


def convert_names_to_snake_case(data: Any) -> Any:
    """Recursively convert all 'name' fields in the data structure to snake_case."""
    if isinstance(data, dict):
        converted = {}
        for key, value in data.items():
            if key == "name" and isinstance(value, str):
                # Convert the name field to snake_case
                converted[key] = to_snake_case(value)
            else:
                # Recursively process nested structures
                converted[key] = convert_names_to_snake_case(value)
        return converted
    elif isinstance(data, list):
        return [convert_names_to_snake_case(item) for item in data]
    else:
        return data


class AgentCompiler:
    """Compiles agent playbook into a framework-specific pipeline."""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.template_env = Environment(
            loader=FileSystemLoader(
                Path(__file__).parent.parent / "templates" / "pipeline"
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template_env.filters["clean"] = clean_filter
        self.template_env.filters["to_pascal_case"] = to_pascal_case
        self.template_env.filters["to_snake_case"] = to_snake_case

        # Mixin templates for different tiers - simplified for current version
        self.mixin_templates = {
            "oracles": "dspy_oracles_mixin_pipeline.py.jinja2",
            "genies": "dspy_genies_mixin_pipeline.py.jinja2",
        }

        # Optional fully abstracted template for developers who want maximum reduction
        self.abstracted_template = "dspy_abstracted_pipeline.py.jinja2"

        # Explicit DSPy template - pure DSPy code with no mixins (RECOMMENDED for DSPy users)
        # This template generates self-contained, transparent code that DSPy users can understand and modify
        self.explicit_template = "dspy_pipeline_explicit.py.jinja2"

        # Protocol-first template (Agenspy approach) - automatic tool discovery via protocols
        # This template uses protocol-first approach for automatic tool discovery from MCP servers
        self.agenspy_template = "dspy_pipeline_agenspy.py.jinja2"

        # Optimas templates (target-specific)
        self.optimas_templates = {
            "optimas-dspy": "optimas_dspy_pipeline.py.jinja2",
            "optimas-crewai": "optimas_crewai_pipeline.py.jinja2",
            "optimas-autogen": "optimas_autogen_pipeline.py.jinja2",
            "optimas-openai": "optimas_openai_pipeline.py.jinja2",
        }

    def _find_project_root(self) -> Path:
        """Find project root by looking for .super file."""
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".super").exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError(
            "Could not find .super file. Please run 'super init <project_name>' first."
        )

    def _load_playbook_and_get_context(
        self, agent_name: str, tier_level: str = None
    ) -> Dict[str, Any]:
        """Loads playbook and creates a context dictionary for templates."""
        with open(self.project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        playbook_path = next(
            (self.project_root / system_name / "agents").rglob(
                f"**/{agent_name}_playbook.yaml"
            ),
            None,
        )

        if not playbook_path:
            # Fallback to searching the source agents directory
            package_root = Path(__file__).parent.parent.parent
            playbook_path = next(
                package_root.rglob(f"**/agents/**/{agent_name}_playbook.yaml"), None
            )
            if not playbook_path:
                raise FileNotFoundError(f"Playbook for agent '{agent_name}' not found.")

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Convert all name fields to snake_case for DSPy compatibility
        playbook_snake_case = convert_names_to_snake_case(playbook)

        console.print(
            "[dim]🐍 Converted field names to snake_case for DSPy compatibility[/]"
        )

        # Determine effective tier
        effective_tier = self._extract_tier_level(playbook_snake_case, tier_level)

        # Apply tier-specific enhancements to spec
        spec = playbook_snake_case.get("spec", {})
        if effective_tier == "genies":
            # Enable genies-tier features that exist in the playbook
            # Handle both legacy (react_config) and new SuperSpec DSL (tool_calling) formats
            if "react_config" in spec:
                spec["react_config"]["enabled"] = True
            elif "tool_calling" in spec:
                # Convert SuperSpec DSL to legacy format for compatibility
                spec["react_config"] = {"enabled": True}
            if "tools" in spec:
                spec["tools"]["enabled"] = True
            if "memory" in spec:
                spec["memory"]["enabled"] = True

        # Extract input/output fields from first task for signature generation
        tasks = spec.get("tasks", [])
        if tasks and len(tasks) > 0:
            first_task = tasks[0]
            spec["input_fields"] = first_task.get("inputs", [])
            spec["output_fields"] = first_task.get("outputs", [])

        return {
            "metadata": playbook_snake_case.get("metadata", {}),
            "spec": spec,
            "agent_name": to_snake_case(agent_name),
            "tier_level": effective_tier,
        }

    def _get_pipeline_path(self, agent_name: str, target: str | None = None) -> Path:
        """Constructs the path for the output pipeline file."""
        with open(self.project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        agent_dir = self.project_root / system_name / "agents" / agent_name
        if target and target != "dspy":
            suffix = target.replace("-", "_")
            return agent_dir / "pipelines" / f"{agent_name}_{suffix}_pipeline.py"
        return agent_dir / "pipelines" / f"{agent_name}_pipeline.py"

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renders a Jinja2 template."""
        template = self.template_env.get_template(template_name)
        return template.render(context)

    def _get_template_for_tier(
        self, tier_level: str, use_abstracted: bool = False, use_explicit: bool = True
    ) -> str:
        """Return the correct pipeline template for the requested tier.

        Template Selection Priority:
        1. Explicit template (use_explicit=True, DEFAULT) - Pure DSPy code, no mixins
        2. Abstracted template (use_abstracted=True) - Maximum code reduction
        3. Mixin template (fallback) - Mixin-based for backward compatibility

        The explicit template is now the default for best DSPy user experience.
        """
        if use_explicit:
            return self.explicit_template
        if use_abstracted:
            return self.abstracted_template
        return self.mixin_templates.get(tier_level, self.mixin_templates["oracles"])

    def compile(
        self,
        args,
        tier_level: str = None,
        use_abstracted: bool = False,
        use_explicit: bool = True,
    ) -> None:
        """Compile agent playbook into a runnable pipeline with tier awareness and template selection.

        Template Selection:
        - use_explicit=True (DEFAULT): Pure DSPy code, no mixins, fully transparent
        - use_abstracted=True: Maximum code reduction with SuperOptixPipeline base class
        - Neither: Mixin-based templates (legacy, backward compatibility)
        """
        try:
            agent_name = args.name
            target = getattr(args, "target", "dspy")
            framework = getattr(args, "framework", "dspy")

            # If framework is specified and not dspy, use the new multi-framework registry
            if framework != "dspy":
                self._compile_with_framework_registry(agent_name, framework, tier_level)
                return

            # Otherwise, use the existing DSPy compilation path
            context = self._load_playbook_and_get_context(agent_name, tier_level)
            context["compile_target"] = target
            pipeline_path = self._get_pipeline_path(agent_name, target)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)

            # Detect tool backend (protocol-first vs tool-first)
            spec = context.get("spec", {})
            tool_backend = spec.get("tool_backend", "dspy")  # Default to tool-first
            mcp_servers = spec.get("mcp_servers", [])
            use_protocol_first = (tool_backend == "agenspy") or (len(mcp_servers) > 0)

            # Choose template
            effective_tier = context["tier_level"]
            if target == "dspy":
                if use_protocol_first:
                    # Protocol-first approach (Agenspy)
                    template_name = self.agenspy_template
                else:
                    # Tool-first approach (standard DSPy)
                    template_name = self._get_template_for_tier(
                        effective_tier, use_abstracted, use_explicit
                    )
            else:
                template_name = self.optimas_templates.get(target)
                if not template_name:
                    raise ValueError(f"Unsupported compile target: {target}")

            # Show compilation message with approach details
            tier_display = effective_tier.title()

            if use_protocol_first:
                approach_text = "Protocol-First "
                reduction_text = " (Agenspy - Automatic tool discovery via MCP)"
            elif use_explicit:
                approach_text = "Explicit DSPy "
                reduction_text = " (Pure DSPy - No mixins, fully transparent)"
            elif use_abstracted:
                approach_text = "Abstracted "
                reduction_text = " (~85% code reduction)"
            else:
                approach_text = "Mixin "
                reduction_text = " (Legacy template)"

            console.print(
                f"\n[bold green]🤖 Generating {approach_text}{tier_display}-Tier pipeline{reduction_text}...[/bold green]"
            )

            if target != "dspy":
                console.print(
                    "[cyan]🧠 Optimas Target: Generating pipeline wired to Optimas adapters[/]"
                )
            elif use_protocol_first:
                # NEW: Protocol-first template
                console.print(
                    "[cyan]🔌 Protocol-First Approach: Automatic tool discovery from MCP servers[/]"
                )
                console.print(
                    "[green]🤖 Agenspy Integration: Vendored protocol-first components[/]"
                )
                console.print(
                    "[bright_yellow]🛠️  Auto Tool Discovery: No manual tool loading or registration[/]"
                )
                console.print(
                    "[magenta]🎯 Key Differentiator: Protocol-level optimization + session management[/]"
                )
                if mcp_servers:
                    console.print(
                        f"[bright_cyan]📡 MCP Servers: {len(mcp_servers)} configured ({', '.join(mcp_servers[:2])}{'...' if len(mcp_servers) > 2 else ''})[/]"
                    )
            elif use_explicit:
                # NEW DEFAULT: Explicit DSPy template
                console.print(
                    "[cyan]✨ Explicit DSPy Code: Pure DSPy patterns with no SuperOptiX mixins[/]"
                )
                console.print(
                    "[green]🔓 No Vendor Lock-in: All code is visible, transparent, and yours to modify[/]"
                )
                console.print(
                    "[bright_yellow]📚 DSPy-Native: Familiar patterns that DSPy users already know[/]"
                )
                console.print(
                    "[magenta]🎯 Features: Includes RAG, MCP tools, GEPA optimization - all explicit![/]"
                )
            elif use_abstracted:
                console.print(
                    "[cyan]🏗️  Infrastructure Abstraction: Auto-tracing + Tool management + Spec execution[/]"
                )
                console.print(
                    "[green]🔧 Developer Controls: DSPy signatures + modules + forward logic[/]"
                )
                console.print(
                    "[yellow]⚠️  Warning: Full abstraction - may break existing commands[/]"
                )
            else:
                # Legacy mixin behavior
                console.print(
                    "[cyan]🧩 Mixin Pipeline (Legacy): Reusable components for complex agents.[/]"
                )
                console.print(
                    "[yellow]⚠️  Note: Consider using --explicit for better transparency[/]"
                )
                console.print(
                    "[green]🔧 Developer Controls: Modular mixins keep your codebase clean and customizable[/]"
                )

            if effective_tier == "genies":
                console.print(
                    "[cyan]🔧 Genies-Tier Features: ReAct Agents + Tool Integration + RAG Support + Memory[/]"
                )
            else:
                console.print(
                    "[cyan]🔧 Oracles-Tier Features: Basic Chain of Thought + Sequential Orchestra[/]"
                )

            full_pipeline_code = self._render_template(template_name, context)
            pipeline_path.write_text(full_pipeline_code)

            if use_protocol_first:
                approach_note = " (protocol-first/agenspy)"
            elif use_explicit:
                approach_note = " (explicit DSPy)"
            elif use_abstracted:
                approach_note = " (abstracted)"
            else:
                approach_note = " (mixin/legacy)"

            console.print(
                f"✅ Successfully generated {tier_display}-tier pipeline{approach_note} at: {pipeline_path}"
            )

            # Show guidance based on approach (only in verbose mode)
            if getattr(args, "verbose", False):
                if use_protocol_first:
                    # NEW: Protocol-first guidance
                    console.print("\n[dim]💡 Protocol-first pipeline features:[/]")
                    console.print(
                        "[dim]   • Automatic tool discovery from MCP servers[/]"
                    )
                    console.print(
                        "[dim]   • No manual tool loading or registration required[/]"
                    )
                    console.print(
                        "[dim]   • Protocol-level optimization compatible with GEPA[/]"
                    )
                    console.print(
                        "[dim]   • Session management for stateful interactions[/]"
                    )
                    console.print(
                        "[dim]   • Foundation for Agent2Agent protocol (future)[/]"
                    )
                    console.print(
                        "[dim]   • Key differentiator: SuperOptiX protocol-first approach[/]"
                    )
                elif use_explicit:
                    # NEW DEFAULT: Explicit template guidance
                    console.print("\n[dim]💡 Explicit DSPy pipeline features:[/]")
                    console.print(
                        "[dim]   • All code visible and understandable - no hidden mixins[/]"
                    )
                    console.print(
                        "[dim]   • Standard DSPy patterns (ChainOfThought, ReAct, Retrieve)[/]"
                    )
                    console.print(
                        "[dim]   • Copy-pasteable code you can modify and customize[/]"
                    )
                    console.print(
                        "[dim]   • RAG setup, MCP tools, evaluation - all explicit![/]"
                    )
                    console.print(
                        "[dim]   • GEPA optimization built-in with standard DSPy API[/]"
                    )
                    console.print(
                        "[dim]   • No vendor lock-in - 100% your code to own and modify[/]"
                    )
                elif use_abstracted:
                    console.print("\n[dim]💡 Abstracted pipeline features:[/]")
                    console.print(
                        "[dim]   • Infrastructure auto-handled by SuperOptixPipeline[/]"
                    )
                    console.print(
                        "[dim]   • Focus on DSPy signatures and forward logic[/]"
                    )
                    console.print("[dim]   • Built-in executable spec execution[/]")
                    console.print("[dim]   • Automatic tracing and tool management[/]")
                else:
                    # Legacy mixin guidance
                    console.print("\n[dim]💡 Mixin pipeline features (Legacy):[/]")
                    console.print("[dim]   • Promotes code reuse and modularity[/]")
                    console.print(
                        "[dim]   • Separates pipeline logic into reusable mixins[/]"
                    )
                    console.print(
                        "[dim]   • Consider migrating to --explicit for better transparency[/]"
                    )

                if effective_tier == "genies":
                    console.print(
                        "\n[dim]💡 Genies tier includes all Oracles features[/]"
                    )

                self.show_tier_features(effective_tier)

        except FileNotFoundError as e:
            console.print(f"\n[bold red]❌ Error:[/] {e}")
        except Exception as e:
            console.print(f"\n[bold red]❌ Compilation failed:[/] {e}")
            raise

    def _compile_with_framework_registry(
        self, agent_name: str, framework: str, tier_level: str = None
    ) -> None:
        """
        Compile using the new multi-framework registry.

        This method routes compilation to framework-specific adapters.
        """
        from ..adapters.framework_registry import FrameworkRegistry

        try:
            # Load playbook
            context = self._load_playbook_and_get_context(agent_name, tier_level)

            # Get the framework adapter
            console.print(
                f"\n[bold green]🚀 Compiling with {framework.upper()} framework...[/bold green]"
            )

            # Get output path
            pipeline_path = self._get_pipeline_path(agent_name, framework)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if framework is implemented
            framework_info = FrameworkRegistry.get_framework_info(framework)

            if not framework_info["implemented"]:
                console.print(
                    f"\n[bold yellow]⚠️  {framework.upper()} framework adapter is not yet implemented.[/bold yellow]"
                )
                console.print(f"\n[cyan]📋 Implementation Status:[/]")
                console.print(f"  • Framework: {framework_info['name']}")
                console.print(f"  • Async Required: {framework_info['requires_async']}")
                console.print(f"  • Status: Coming soon!")
                console.print(f"\n[dim]💡 Use --framework dspy (default) for now.[/]")
                console.print(f"[dim]📅 Multi-framework support roadmap:[/]")
                console.print(f"[dim]  • Week 4: Microsoft Agent Framework[/]")
                console.print(f"[dim]  • Week 5: OpenAI Agents SDK[/]")
                console.print(f"[dim]  • Week 6: DeepAgent (LangGraph)[/]")
                console.print(f"[dim]  • Week 7: CrewAI[/]")
                console.print(f"[dim]  • Week 8: Google ADK[/]")
                return

            # Use FrameworkRegistry to compile
            generated_path = FrameworkRegistry.compile_agent(
                framework=framework, playbook=context, output_path=str(pipeline_path)
            )

            console.print(
                f"✅ Successfully compiled with {framework.upper()} framework: {generated_path}"
            )

        except Exception as e:
            console.print(f"\n[bold red]❌ Framework compilation failed:[/] {e}")
            raise

    def _extract_tier_level(
        self, playbook_snake_case: Dict[str, Any], user_tier: str = None
    ) -> str:
        """Extract and validate tier level from playbook or user input."""
        # Remove leading/trailing underscores
        playbook_tier = playbook_snake_case.get("metadata", {}).get("level", "oracles")

        # User override has priority
        effective_tier = user_tier or playbook_tier

        # Validate tier
        valid_tiers = ["oracles", "genies"]
        if effective_tier not in valid_tiers:
            console.print(
                f"[red]❌ Invalid tier '{effective_tier}'. Only Oracles and Genies tiers are supported in current version.[/]"
            )
            console.print(f"[yellow]Valid tiers:[/] {', '.join(valid_tiers)}")
            raise ValueError(f"Unsupported tier: {effective_tier}")

        if effective_tier == "genies":
            # Enable genies-tier features that exist in the playbook
            spec = playbook_snake_case.get("spec", {})
            if "tools" in spec:
                console.print(
                    "[green]✅ Tools configuration detected for Genies tier[/]"
                )
            if "react_config" in spec:
                console.print(
                    "[green]✅ ReAct configuration detected for Genies tier[/]"
                )
            elif "tool_calling" in spec:
                console.print(
                    "[green]✅ Tool calling configuration detected for Genies tier[/]"
                )
            if "memory" in spec:
                console.print(
                    "[green]✅ Memory configuration detected for Genies tier[/]"
                )

        return effective_tier

    def _select_template(self, tier_level: str) -> str:
        """Select the appropriate template based on tier level."""
        return self.mixin_templates.get(tier_level, self.mixin_templates["oracles"])

    def show_tier_features(self, tier: str = None):
        """Show available features for each tier"""
        if tier:
            tiers_to_show = [tier]
        else:
            tiers_to_show = ["oracles", "genies"]

        for tier_name in tiers_to_show:
            console.print(f"\n[bold blue]🎯 {tier_name.title()} Tier Features[/]")

            if tier_name == "oracles":
                features = [
                    "Basic Predict and Chain of Thought modules",
                    "Bootstrap Few-Shot optimization",
                    "Basic evaluation metrics",
                    "Sequential task orchestration",
                    "Basic tracing and observability",
                ]
            elif tier_name == "genies":
                features = [
                    "All Oracles features plus:",
                    "ReAct agents with tool integration",
                    "RAG (Retrieval-Augmented Generation)",
                    "Agent memory (short-term and episodic)",
                    "Basic streaming responses",
                    "JSON/XML adapters",
                ]

            for feature in features:
                console.print(f"[green]  ✅ {feature}[/]")

            if tier_name == "genies":
                console.print("\n[dim]💡 Genies tier includes all Oracles features[/]")

        console.print(
            "\n[yellow]ℹ️  Advanced features available in commercial version[/]"
        )
