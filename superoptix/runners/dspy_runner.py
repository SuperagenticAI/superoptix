"""DSPy Runner for executing agent pipelines."""

import importlib.util
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Dict

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def to_pascal_case(text: str) -> str:
    """
    Converts snake_case or kebab-case to PascalCase, preserving compound words.

    Examples:
        research_agent_deepagents -> ResearchAgentDeepAgents
        sentiment_analyzer -> SentimentAnalyzer
        pydantic-mcp -> PydanticMcp
    """
    # Replace hyphens with underscores, then split on underscores
    text = text.replace("-", "_")
    words = text.split("_")
    pascal_words = []

    for word in words:
        # Skip empty words
        if not word:
            continue
        # Preserve known compound words/frameworks
        if word.lower() in ["deepagents", "crewai", "openai", "pydantic"]:
            # Keep compound words capitalized properly
            if word.lower() == "deepagents":
                pascal_words.append("DeepAgents")
            elif word.lower() == "crewai":
                pascal_words.append("CrewAI")
            elif word.lower() == "openai":
                pascal_words.append("OpenAI")
            elif word.lower() == "pydantic":
                pascal_words.append("Pydantic")
            else:
                pascal_words.append(word.capitalize())
        else:
            pascal_words.append(word.capitalize())

    return "".join(pascal_words)


class DSPyRunner:
    """Runner for DSPy-based agents."""

    def __init__(
        self, agent_name: str, project_name: str = None, project_root: Path = None
    ):
        self.agent_name = agent_name.lower()

        # Use provided project root or find it
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = self._find_project_root()

        if project_name:
            self.system_name = project_name
        else:
            with open(self.project_root / ".super") as f:
                self.system_name = yaml.safe_load(f).get("project")

        # Calculate paths
        self.agent_path = (
            self.project_root / self.system_name / "agents" / self.agent_name
        )

        # Detect pipeline file (framework-specific or default)
        pipelines_dir = self.agent_path / "pipelines"
        self.pipeline_path = self._find_pipeline_file(pipelines_dir)

        self.optimized_path = (
            self.agent_path / "pipelines" / f"{self.agent_name}_optimized.json"
        )
        self.playbook_path = (
            self.agent_path / "playbook" / f"{self.agent_name}_playbook.yaml"
        )

    def _find_project_root(self) -> Path:
        """Find project root by looking for .super file."""
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".super").exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError("Could not find .super file")

    def _find_pipeline_file(self, pipelines_dir: Path) -> Path:
        """
        Find the pipeline file, checking for framework-specific versions.

        Checks in order:
        1. {agent_name}_deepagents_pipeline.py (DeepAgents framework)
        2. {agent_name}_crewai_pipeline.py (CrewAI framework)
        3. {agent_name}_microsoft_pipeline.py (Microsoft framework)
        4. {agent_name}_openai_pipeline.py (OpenAI framework)
        5. {agent_name}_pipeline.py (default DSPy)

        Args:
            pipelines_dir: Directory containing pipeline files

        Returns:
            Path to the pipeline file

        Raises:
            FileNotFoundError: If no pipeline file is found
        """
        if not pipelines_dir.exists():
            raise FileNotFoundError(f"Pipelines directory not found: {pipelines_dir}")

        # Check for framework-specific pipelines first
        framework_variants = [
            "deepagents",
            "crewai",
            "microsoft",
            "openai",
            "google_adk",
            "pydantic_ai",  # Pydantic AI framework
        ]

        for framework in framework_variants:
            framework_pipeline = (
                pipelines_dir / f"{self.agent_name}_{framework}_pipeline.py"
            )
            if framework_pipeline.exists():
                return framework_pipeline

        # Fall back to default DSPy pipeline
        default_pipeline = pipelines_dir / f"{self.agent_name}_pipeline.py"
        if default_pipeline.exists():
            return default_pipeline

        # No pipeline found
        raise FileNotFoundError(
            f"No pipeline file found for agent '{self.agent_name}' in {pipelines_dir}"
        )

    async def optimize(
        self, strategy: str = "bootstrap", force: bool = False
    ) -> Dict[str, Any]:
        """Optimize the agent pipeline using DSPy optimization techniques."""
        optimization_result = {
            "started_at": str(time.time()),
            "success": False,
            "training_examples": 0,
            "score": None,
            "usage_stats": {},
            "error": None,
        }

        try:
            console.print("\n[yellow]🔍 Checking for existing optimized pipeline...[/]")

            # Check if optimized version already exists
            if self.optimized_path.exists() and not force:
                console.print(
                    f"\n[yellow]⚠️ Optimized pipeline already exists at {self.optimized_path}[/]"
                )
                console.print(
                    "[yellow]Use --force to re-optimize or run with existing optimization[/]"
                )
                optimization_result["success"] = True
                optimization_result["note"] = "Already optimized"
                return optimization_result

            console.print(
                Panel(
                    "🔧 DSPy Optimization in progress\n\n• This step fine-tunes prompts and may take several minutes.\n• API calls can incur compute cost – monitor your provider dashboard.\n• You can abort anytime with CTRL+C; your base pipeline remains intact.",
                    title="🚀 Optimization Notice",
                    border_style="bright_magenta",
                )
            )
            console.print(
                f"\n[yellow]🚀 Starting optimization using '[bold]{strategy}[/]' strategy...[/]"
            )

            # Import and execute the pipeline module
            import importlib.util
            import sys

            spec = importlib.util.spec_from_file_location(
                f"{self.agent_name}_pipeline", self.pipeline_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Get pipeline class
            pipeline_class_name = f"{to_pascal_case(self.agent_name)}Pipeline"
            pipeline_class = getattr(module, pipeline_class_name)
            pipeline = pipeline_class()

            # Load playbook to get functional tests
            if self.playbook_path.exists():
                with open(self.playbook_path, "r") as f:
                    playbook = yaml.safe_load(f) or {}

                spec_data = playbook.get("spec", playbook)
                scenarios = None

                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
                elif "scenarios" in spec_data:
                    scenarios = spec_data["scenarios"]

                if scenarios:
                    console.print(
                        f"[green]✅ Found {len(scenarios)} scenarios for optimization[/]"
                    )

                    # --------------------------------------------------
                    # 🔄  Transform scenarios -> training examples
                    # --------------------------------------------------
                    training_examples = []
                    for sc in scenarios:
                        if isinstance(sc, dict):
                            inputs = sc.get("input", {})
                            expected = sc.get("expected_output", {})
                            if inputs or expected:
                                # Merge in the same way BDDTestMixin does
                                training_examples.append({**inputs, **expected})
                            else:
                                # Fallback: if already flattened assume valid
                                training_examples.append(sc)
                        else:
                            # Unexpected format – skip gracefully
                            continue

                    # The pipeline's train method now handles saving and returns stats.
                    train_stats = pipeline.train(
                        training_data=training_examples,
                        save_optimized=True,
                        optimized_path=str(self.optimized_path),
                    )

                    # Update the main optimization result with the stats from the train method
                    optimization_result.update(train_stats)

                else:
                    optimization_result["error"] = (
                        "No scenarios found in playbook for optimization"
                    )
            else:
                optimization_result["error"] = (
                    f"Playbook not found at {self.playbook_path}"
                )

        except Exception as e:
            optimization_result["error"] = str(e)
            console.print(f"[red]❌ Optimization failed: {e}[/]")

        optimization_result["completed_at"] = str(time.time())
        return optimization_result

    async def run(
        self,
        query: str,
        use_optimization: bool = True,
        runtime_optimize: bool = False,
        force_runtime: bool = False,
    ) -> Any:
        """Run DSPy agent with given query."""
        # Suppress the specific Pydantic UserWarning that can be noisy.
        warnings.filterwarnings(
            "ignore", category=UserWarning, message="Pydantic serializer warnings.*"
        )

        # Track optimization status for better user feedback
        optimization_status = {
            "used_pre_optimized": False,
            "runtime_optimization": runtime_optimize,
            "optimization_available": False,
            "optimization_used": False,
        }

        try:
            # Check for optimized pipeline first
            optimization_status["optimization_available"] = self.optimized_path.exists()

            # Smart handling when both --optimize flag and pre-optimized file exist
            if runtime_optimize and self.optimized_path.exists() and not force_runtime:
                console.print(
                    f"\n[yellow]⚠️ Pre-optimized pipeline already exists at {self.optimized_path.name}[/]"
                )
                console.print(
                    "[yellow]You used --optimize flag, but optimization is already available.[/]"
                )
                console.print("\n[cyan]Options:[/]")
                console.print(
                    "[green]1. Use existing pre-optimized pipeline (FAST, recommended)[/]"
                )
                console.print(
                    "[yellow]2. Perform fresh runtime optimization (SLOW, may overwrite existing)[/]"
                )

                # For now, default to pre-optimized (safer and faster)
                console.print(
                    "\n[green]💡 Using existing pre-optimized pipeline for better performance.[/]"
                )
                console.print(
                    f'[dim]To force fresh optimization, use: super agent run {self.agent_name} --force-optimize --goal "goal"[/]'
                )
                console.print(
                    f"[dim]Or use: super agent optimize {self.agent_name} --force[/]"
                )

                # Override runtime_optimize to use pre-optimized
                runtime_optimize = False
                use_optimized = True
                optimization_status["used_pre_optimized"] = True
                optimization_status["optimization_used"] = True
                optimization_status["runtime_optimization"] = False
            elif force_runtime and self.optimized_path.exists():
                console.print(
                    "\n[yellow]🔄 Force runtime optimization requested - ignoring existing pre-optimized pipeline[/]"
                )
                use_optimized = False
            else:
                use_optimized = (
                    use_optimization
                    and self.optimized_path.exists()
                    and not runtime_optimize
                )

            if use_optimized:
                if not optimization_status.get(
                    "used_pre_optimized"
                ):  # Only print if not already printed above
                    optimization_status["used_pre_optimized"] = True
                    optimization_status["optimization_used"] = True
                console.print(
                    f"\n[green]🚀 Using pre-optimized pipeline from {self.optimized_path.name}[/]"
                )
            elif runtime_optimize:
                console.print(
                    "\n[yellow]⚡ Runtime optimization will be performed (slower execution)[/]"
                )
            elif self.optimized_path.exists():
                console.print(
                    "\n[yellow]📝 Pre-optimized pipeline available but runtime optimization requested[/]"
                )
            else:
                console.print(
                    "\n[yellow]📝 Using base pipeline (no optimization available)[/]"
                )

            console.print(f"\n[yellow]Looking for pipeline at:[/] {self.pipeline_path}")

            if not self.pipeline_path.exists():
                raise FileNotFoundError(f"Pipeline not found at {self.pipeline_path}")

            # Check if we need to use a fallback approach for Ollama models
            use_fallback = False
            playbook = {}
            if self.playbook_path.exists():
                with open(self.playbook_path, "r") as f:
                    playbook = yaml.safe_load(f) or {}

            spec_data = playbook.get("spec", playbook)

            llm_config = {}
            if "llm" in spec_data:
                llm_config = spec_data["llm"]
            elif "agents" in spec_data and spec_data["agents"]:
                for agent in spec_data["agents"]:
                    if "llm" in agent:
                        llm_config = agent["llm"]
                        break

            provider = llm_config.get("provider", "").lower()
            model = llm_config.get("model", "").lower()

            if provider == "ollama" and ("llama" in model or "qwen" in model):
                use_fallback = True
                console.print(
                    "\n[yellow]⚠️ Note: Using compatibility mode for Ollama model.[/]"
                )

            if use_fallback:
                # Patch DSPy settings for better Ollama compatibility

                def patched_setup_lm(self):
                    console.print("[dim]Setting up language model for Ollama...[/]")
                    import dspy

                    try:
                        # Try using the model directly
                        return dspy.OllamaLocal(
                            model=llm_config.get("model", "llama3.2:1b"),
                            base_url=llm_config.get(
                                "base_url", "http://localhost:11434"
                            ),
                            temperature=llm_config.get("temperature", 0.7),
                            max_tokens=llm_config.get("max_tokens", 2000),
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning: Ollama setup issue ({e}), trying fallback...[/]"
                        )
                        # Fallback to basic configuration
                        import litellm

                        litellm.set_verbose = False
                        return dspy.LiteLLM(
                            model=f"ollama/{llm_config.get('model', 'llama3.2:1b')}",
                            api_base=llm_config.get(
                                "base_url", "http://localhost:11434"
                            ),
                            temperature=llm_config.get("temperature", 0.7),
                            max_tokens=llm_config.get("max_tokens", 2000),
                        )

                # Apply the patch by adding it to the module's environment
                if not hasattr(sys.modules[__name__], "_ollama_patch_applied"):
                    sys.modules[__name__]._ollama_patch_applied = True

            # Load pipeline module
            spec = importlib.util.spec_from_file_location(
                f"{self.agent_name}_pipeline", self.pipeline_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module

            # Apply the patch if using fallback
            if use_fallback and hasattr(module, "setup_language_model"):
                # Preserve but don't expose original function to avoid unused-variable lint
                def patched_setup():
                    console.print(
                        "[dim]Using patched language model setup for Ollama...[/]"
                    )
                    import dspy

                    try:
                        # Try using the model directly
                        return dspy.OllamaLocal(
                            model=llm_config.get("model", "llama3.2:1b"),
                            base_url=llm_config.get(
                                "base_url", "http://localhost:11434"
                            ),
                            temperature=llm_config.get("temperature", 0.7),
                            max_tokens=llm_config.get("max_tokens", 2000),
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning: Ollama setup issue ({e}), trying fallback...[/]"
                        )
                        # Fallback to basic configuration
                        import litellm

                        litellm.set_verbose = False
                        return dspy.LiteLLM(
                            model=f"ollama/{llm_config.get('model', 'llama3.2:1b')}",
                            api_base=llm_config.get(
                                "base_url", "http://localhost:11434"
                            ),
                            temperature=llm_config.get("temperature", 0.7),
                            max_tokens=llm_config.get("max_tokens", 2000),
                        )

                # Replace the function in the module
                module.setup_language_model = patched_setup

            spec.loader.exec_module(module)

            # Initialize pipeline
            pipeline_class_name = f"{to_pascal_case(self.agent_name)}Pipeline"
            pipeline_class = getattr(module, pipeline_class_name, None)

            if not pipeline_class:
                # Fallback for older template naming
                pipeline_class_name = (
                    f"{self.agent_name.title().replace('_', '')}Pipeline"
                )
                pipeline_class = getattr(module, pipeline_class_name)

            pipeline = pipeline_class()

            # Load optimized model if available and requested
            if use_optimized:
                try:
                    console.print(
                        f"[cyan]📦 Loading pre-optimized model from {self.optimized_path.name}[/]"
                    )
                    if hasattr(pipeline.module, "load"):
                        pipeline.module.load(str(self.optimized_path))
                        pipeline.is_trained = True
                        console.print(
                            "[green]✅ Pre-optimized model loaded successfully[/]"
                        )
                    else:
                        console.print(
                            "[yellow]⚠️ Pipeline doesn't support loading, falling back to base model[/]"
                        )
                        use_optimized = False
                        optimization_status["used_pre_optimized"] = False
                        optimization_status["optimization_used"] = False
                except Exception as e:
                    console.print(
                        f"[yellow]⚠️ Failed to load pre-optimized model: {e}. Using base model.[/]"
                    )
                    use_optimized = False
                    optimization_status["used_pre_optimized"] = False
                    optimization_status["optimization_used"] = False

            # Handle runtime optimization
            if runtime_optimize and not use_optimized:
                console.print("[yellow]🔄 Performing runtime optimization...[/]")
                # Train pipeline if functional tests exist to be used as golden examples
                training_examples = []
                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
                    # Adapt to the format expected by the pipeline's train method
                    training_examples = [
                        {"input": test["input"], "output": test["expected_output"]}
                        for test in scenarios
                    ]

                if training_examples:
                    console.print(
                        f"[green]📚 Found {len(training_examples)} scenarios for optimization[/]"
                    )
                    training_stats = pipeline.train(training_examples)
                    if training_stats.get("success", False):
                        optimization_status["optimization_used"] = True
                        console.print(
                            "[green]✅ Runtime optimization completed successfully[/]"
                        )
                    else:
                        console.print(
                            "[yellow]⚠️ Runtime optimization failed, using base model[/]"
                        )
                else:
                    console.print(
                        "[yellow]⚠️ No scenarios available for optimization, using base model[/]"
                    )

            # Basic setup if no optimization is used
            elif not use_optimized:
                # Note: Only train if this is an explicit optimization run
                # This prevents automatic training on every run
                # Only call setup() if it exists (DSPy-specific, not needed for other frameworks)
                if hasattr(pipeline, "setup") and callable(getattr(pipeline, "setup")):
                    pipeline.setup()  # Basic setup without training

            # Show execution start
            console.print(
                Panel(
                    f"[bold blue]🤖 Running {self.agent_name.title()} Pipeline[/]\n\n"
                    f"[cyan]Executing Task:[/] {query}\n",
                    title="Agent Execution",
                    border_style="blue",
                )
            )

            # Run pipeline with error handling
            try:
                # Different frameworks use different execution methods
                if hasattr(pipeline, "run") and callable(getattr(pipeline, "run")):
                    # Non-DSPy frameworks (DeepAgents, CrewAI, OpenAI, etc.) use .run()
                    # Check if run() is async
                    import inspect

                    if inspect.iscoroutinefunction(pipeline.run):
                        result = await pipeline.run(query=query)
                    else:
                        result = pipeline.run(query=query)
                elif callable(pipeline):
                    # DSPy pipelines are callable
                    result = await pipeline(query)
                else:
                    raise AttributeError(
                        f"Pipeline has no callable method (run or __call__)"
                    )

                # ------------------------------------------------------------------
                # 🎯 Basic validation if pipeline didn't provide one
                # ------------------------------------------------------------------
                if isinstance(result, dict) and "is_valid" not in result:
                    # Heuristic: check that at least one non-meta field is non-empty
                    user_fields = [
                        k
                        for k in result.keys()
                        if not k.startswith("_")
                        and k not in ("agent_id", "usage", "trained")
                    ]
                    non_empty = any(
                        bool(str(result.get(f, "")).strip()) for f in user_fields
                    )
                    result["is_valid"] = non_empty
                    if not non_empty:
                        result["validation_warnings"] = (
                            "All primary output fields are empty"
                        )
                    else:
                        result["validation_warnings"] = []

            except Exception as e:
                error_str = str(e)

                # Check for the specific Ollama KeyError: 'name' error
                if (
                    "KeyError: 'name'" in error_str
                    or "litellm.APIConnectionError: 'name'" in error_str
                ):
                    console.print("\n[red]❌ Model Compatibility Error[/]")
                    console.print(
                        "\n[yellow]The current model does not support structured output format required by DSPy.[/]"
                    )
                    console.print(
                        "\n[cyan]Please try one of the following solutions:[/]"
                    )
                    console.print(
                        "1. [bold]Use a different model[/] in your playbook configuration:"
                    )
                    console.print(
                        "   - OpenAI models (gpt-3.5-turbo, gpt-4) support structured output"
                    )
                    console.print(
                        "   - For Ollama, try models like llama3:70b or mixtral:8x7b"
                    )
                    console.print(
                        "2. [bold]Update your playbook[/] to use a compatible model:"
                    )
                    console.print(
                        "   - Edit the model field in your agent's playbook.yaml file"
                    )
                    console.print("   - Example: model: gpt-3.5-turbo")
                    console.print("\n[yellow]To edit your playbook:[/]")
                    console.print(
                        f"  nano {self.project_root}/{self.system_name}/agents/{self.agent_name}/playbook/{self.agent_name}_playbook.yaml"
                    )
                    return None

                # Generic error handling for other errors
                console.print(
                    f"\n[red]❌ Error during pipeline execution:[/] {error_str}"
                )
                console.print(
                    "\n[yellow]This might be due to a JSON parsing error or model compatibility issue.[/]"
                )
                console.print("\n[cyan]Suggestions:[/]")
                console.print(
                    "1. Try using a different model in your playbook configuration"
                )
                console.print("2. Check if Ollama is running with the correct model")
                console.print("3. Try a simpler query")
                console.print("\n[yellow]Technical details:[/]")
                console.print(f"{error_str}")
                return None

            # Add optimization status to result
            if result and isinstance(result, dict):
                result["_optimization_status"] = optimization_status

            # Display results
            if result:
                # Results table
                results_table = Table(title="Analysis Results")
                results_table.add_column("Aspect", style="cyan")
                results_table.add_column("Value", style="green")

                for key, value in result.items():
                    if key not in [
                        "evaluation",
                        "is_valid",
                        "is_optimized",
                        "validation_warnings",
                        "_optimization_status",  # Hide internal optimization status
                    ]:
                        results_table.add_row(key.title(), str(value))

                console.print(results_table)

                # Evaluation table
                if "evaluation" in result:
                    eval_table = Table(title="Evaluation Metrics")
                    eval_table.add_column("Metric", style="cyan")
                    eval_table.add_column("Score", style="green")

                    for metric, score in result["evaluation"].items():
                        if isinstance(score, float):
                            eval_table.add_row(metric.title(), f"{score:.2f}")
                        else:
                            eval_table.add_row(metric.title(), str(score))

                    console.print(eval_table)

                # Enhanced optimization status display
                opt_status = result.get("_optimization_status", optimization_status)

                if opt_status["used_pre_optimized"]:
                    console.print("\n[green]Pre-Optimized Pipeline: ✅ YES[/]")
                    console.print("[green]Runtime Optimization: ⚪ NO[/]")
                elif (
                    opt_status["runtime_optimization"]
                    and opt_status["optimization_used"]
                ):
                    console.print("\n[yellow]Pre-Optimized Pipeline: ⚪ NO[/]")
                    console.print("[green]Runtime Optimization: ✅ YES[/]")
                elif opt_status["optimization_available"]:
                    console.print(
                        "\n[yellow]Pre-Optimized Pipeline: ⚠️ Available but not used[/]"
                    )
                    console.print("[yellow]Runtime Optimization: ⚪ NO[/]")
                    console.print(
                        f"[dim]💡 Use 'super agent run {self.agent_name} --goal \"goal\"' to use pre-optimization[/]"
                    )
                else:
                    console.print("\n[yellow]Pre-Optimized Pipeline: ⚪ NO[/]")
                    console.print("[yellow]Runtime Optimization: ⚪ NO[/]")
                    console.print(
                        f"[dim]💡 Run 'super agent optimize {self.agent_name}' to create optimized version[/]"
                    )

                # Validation status
                color = "green" if result.get("is_valid", False) else "red"
                status = "✅ PASSED" if result.get("is_valid", False) else "❌ FAILED"
                console.print(f"\n[{color}]Validation Status: {status}[/]")

                if "validation_warnings" in result:
                    console.print(
                        f"[yellow]Validation Warnings: {result['validation_warnings']}[/]"
                    )

                # Return the full result object for orchestration purposes
                return result

            return None

        except FileNotFoundError as e:
            console.print(f"\n[red]❌ Error:[/] {e}")
            return None
        except Exception as e:
            console.print(f"\n[red]❌ An unexpected error occurred:[/] {e}")
            import traceback

            traceback.print_exc()
            return None
        finally:
            # Restore warnings
            warnings.resetwarnings()

    @staticmethod
    def format_result(result: Dict[str, Any]) -> str:
        """Format result for display."""
        if isinstance(result, dict):
            return "\n".join(f"{k}: {v}" for k, v in result.items())
        return str(result)
