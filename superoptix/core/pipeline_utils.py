"""
SuperOptiX Pipeline Utilities

This module provides mixin classes and utilities to reduce code repetition
in generated pipelines while maintaining full compatibility with the existing
SuperOptiX framework.
"""

import asyncio
import inspect
import json
import logging
import os
import math
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import dspy

# SuperOptiX Imports
from superoptix.observability.tracer import SuperOptixTracer
from superoptix.tools import (
    CalculatorTool,
    DateTimeTool,
    FileReaderTool,
    TextAnalyzerTool,
)

# RAG Support
try:
    from superoptix.core.rag_mixin import RAGMixin

    RAG_AVAILABLE = True
except ImportError:
    RAGMixin = None
    RAG_AVAILABLE = False

# DSPy Evaluation Imports
try:
    from dspy.evaluate import Evaluate
    from dspy.evaluate.auto_evaluation import SemanticF1
    from dspy.teleprompt import BootstrapFewShot, LabeledFewShot
except ImportError:
    # Fallback for older DSPy versions
    Evaluate = None
    SemanticF1 = None
    LabeledFewShot = None
    BootstrapFewShot = None

# DSPy Latest Compatibility
try:
    from dspy import ReAct, ChainOfThought
    from dspy.adapters import ChatAdapter, Tool
except ImportError:
    # Fallback to basic imports
    try:
        from dspy import ReAct, ChainOfThought
        from dspy.adapters.types.tool import Tool

        ChatAdapter = None
    except ImportError:
        Tool = None
        ReAct = None
        ChainOfThought = None
        ChatAdapter = None

logger = logging.getLogger(__name__)


class TracingMixin:
    """Mixin that provides standardized tracing and observability setup."""

    def setup_tracing(self, agent_name: str, config: Dict[str, Any] = None):
        """Initialize comprehensive tracing system with proper .superoptix/traces/ format."""
        config = config or {}

        # Create unique agent ID for tracing
        self.agent_id = f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize SuperOptiX tracer with external tracing enabled
        # The tracer will automatically handle .superoptix/traces/ directory structure
        self.tracer = SuperOptixTracer(
            agent_id=self.agent_id,
            enable_external_tracing=config.get("enable_external_tracing", False),
        )

        # Setup trace storage directory using proper .superoptix/traces format
        # This ensures consistency with the tracer's export_traces method
        project_root = Path.cwd()
        self.traces_dir = project_root / ".superoptix" / "traces"
        self.traces_dir.mkdir(parents=True, exist_ok=True)

        # Enable DSPy logging and tracing
        dspy.enable_logging()

        print(f"🔍 Tracing enabled for agent {self.agent_id}")
        print(f"📁 Traces will be stored in: {self.traces_dir.absolute()}")

        return self.tracer

    def __del__(self):
        """Ensure traces are exported when pipeline is destroyed."""
        if hasattr(self, "tracer") and self.tracer:
            try:
                # Export traces to .superoptix/traces/*.jsonl format
                self.tracer.export_traces()
            except Exception:
                pass  # Ignore errors during cleanup


class ModelSetupMixin:
    """Mixin that provides standardized model configuration across tiers."""

    def setup_language_model(self, spec: Dict[str, Any], tier: str = "mid") -> dspy.LM:
        """Configure language model with tier-specific optimizations."""

        # Extract model configuration from spec
        model_config = spec.get("language_model", {})
        model_name = model_config.get("model", self._get_default_model(tier))
        provider = model_config.get("provider", "ollama")

        print(
            f"🚀 Configuring {model_name} with {provider} for {tier}-tier capabilities"
        )

        # Configure ChatAdapter for better local model compatibility
        if ChatAdapter and provider.lower() == "ollama":
            current_adapter = getattr(dspy.settings, "adapter", None)
            if not isinstance(current_adapter, ChatAdapter):
                print("📝 Using ChatAdapter for optimal local model compatibility")
                dspy.settings.adapter = ChatAdapter()
            else:
                # Adapter already configured; skip re-assignment.
                print(
                    "🔁 ChatAdapter already configured – skipping reconfiguration to avoid DSPy async conflicts"
                )

        # Build LM configuration
        lm_config = {
            "model": f"{provider}_chat/{model_name}"
            if provider == "ollama"
            else model_name,
            "temperature": model_config.get(
                "temperature", self._get_default_temperature(tier)
            ),
            "max_tokens": model_config.get(
                "max_tokens", self._get_default_max_tokens(tier)
            ),
        }

        # Add provider-specific configuration
        if provider == "ollama":
            lm_config.update(
                {
                    "api_base": model_config.get("api_base", "http://localhost:11434"),
                    "api_key": "",  # No API key needed for Ollama
                    "max_retries": 2,
                    "timeout": 30,
                }
            )
        elif provider == "mlx":
            # Use custom_openai provider for MLX (LiteLLM supports MLX through custom_openai)
            lm_config.update(
                {
                    "model": f"custom_openai/{model_name}",
                    "api_base": model_config.get("api_base", "http://localhost:8000"),
                    "api_key": "dummy-key",  # MLX doesn't require real API key, but LiteLLM expects one
                    "max_retries": 2,
                    "timeout": 30,
                }
            )
        elif model_config.get("api_base"):
            lm_config["api_base"] = model_config["api_base"]

        try:
            lm = dspy.LM(**lm_config)
            print(f"✅ Model connection successful: {provider}/{model_name}")

            # Log successful initialization if tracer is available
            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "model_initialized",
                    "pipeline",
                    data={
                        "model": model_name,
                        "provider": provider,
                        "tier": tier,
                        "adapter": "ChatAdapter"
                        if ChatAdapter and provider == "ollama"
                        else "default",
                    },
                    status="success",
                )

            return lm

        except Exception as e:
            error_msg = f"Failed to initialize model: {str(e)}"
            print(f"❌ {error_msg}")

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "model_init_failed",
                    "pipeline",
                    data={"error": error_msg},
                    status="error",
                )

            raise RuntimeError(error_msg)

    def setup_reflection_lm(self, lm_config: dict) -> dspy.LM:
        """Robustly configure a reflection LM from a config dict (model, provider, etc)."""
        from dspy import LM

        model_name = lm_config.get("model", "llama3.1:8b")
        provider = lm_config.get("provider", "ollama")
        temperature = lm_config.get("temperature", 0.0)
        max_tokens = lm_config.get("max_tokens", 32000)
        if provider == "ollama":
            model_str = (
                f"ollama_chat/{model_name}"
                if not model_name.startswith("ollama_chat/")
                else model_name
            )
            print(
                f"[REFLECTION_LM DEBUG] Using Ollama LM: {model_str}, api_base=http://localhost:11434"
            )
            return LM(
                model_str,
                api_base="http://localhost:11434",
                api_key="",
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            print(
                f"[REFLECTION_LM DEBUG] Using generic LM: model={model_name}, provider={provider}, temperature={temperature}, max_tokens={max_tokens}"
            )
            return LM(
                model=model_name,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    def _get_default_model(self, tier: str) -> str:
        """Get default model for tier."""
        defaults = {
            "oracles": "llama3.2:1b",
            "genies": "llama3.1:8b",
            "sage": "llama3.1:70b",
        }
        return defaults.get(tier, "llama3.1:8b")

    def _get_default_temperature(self, tier: str) -> float:
        """Get default temperature for tier."""
        defaults = {"oracles": 0.7, "genies": 0.1, "sage": 0.0}
        return defaults.get(tier, 0.1)

    def _get_default_max_tokens(self, tier: str) -> int:
        """Get default max tokens for tier."""
        defaults = {"oracles": 1000, "genies": 2000, "sage": 4000}
        return defaults.get(tier, 2000)


class ToolsMixin:
    """Mixin that provides standardized tool registration and management."""

    def setup_tools(self, spec_data=None):
        """Setup standard tools with tracing and custom tool support."""
        if hasattr(self, "tracer"):
            with self.tracer.trace_operation("tools_setup", "pipeline"):
                return self._setup_tools_internal(spec_data)
        else:
            return self._setup_tools_internal(spec_data)

    def _setup_tools_internal(self, spec_data=None):
        """Internal tool setup logic with custom tool support."""
        self.tools = []
        tool_count = 0

        # Get tools configuration from spec data
        tools_config = {}
        if spec_data and isinstance(spec_data, dict):
            tools_config = spec_data.get("tools", {})
        elif hasattr(self, "spec") and isinstance(self.spec, dict):
            tools_config = self.spec.get("tools", {})

        try:
            # Load built-in tools
            builtin_tools = tools_config.get("builtin_tools", [])
            if not builtin_tools:
                # Default tools if none specified
                builtin_tools = [
                    {"name": "calculator", "enabled": True},
                    {"name": "text_analyzer", "enabled": True},
                    {"name": "file_reader", "enabled": True},
                    {"name": "datetime", "enabled": True},
                ]

            tool_count += self._setup_builtin_tools(builtin_tools)

            # Load custom tools
            custom_tools = tools_config.get("custom_tools", [])
            tool_count += self._setup_custom_tools(custom_tools)

            print(f"✅ {tool_count} tools configured successfully")

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tools_initialized",
                    "pipeline",
                    data={
                        "tool_count": tool_count,
                        "tools": [
                            getattr(tool, "name", str(tool)) for tool in self.tools
                        ],
                    },
                    status="success",
                )

            return self.tools

        except Exception as e:
            error_msg = f"Failed to setup tools: {str(e)}"
            print(f"❌ {error_msg}")

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tools_setup_failed",
                    "pipeline",
                    data={"error": error_msg},
                    status="error",
                )

            # Continue without tools rather than failing
            self.tools = []
            return self.tools

    def _setup_builtin_tools(self, builtin_tools):
        """Setup built-in tools from configuration."""
        tool_count = 0

        for tool_config in builtin_tools:
            if not isinstance(tool_config, dict) or "name" not in tool_config:
                continue

            tool_name = tool_config["name"]
            enabled = tool_config.get("enabled", True)

            if not enabled:
                continue

            if tool_name == "calculator":
                tool_count += self._add_calculator_tool(tool_config.get("config", {}))
            elif tool_name == "datetime":
                tool_count += self._add_datetime_tool(tool_config.get("config", {}))
            elif tool_name == "text_analyzer":
                tool_count += self._add_text_analyzer_tool(
                    tool_config.get("config", {})
                )
            elif tool_name == "file_reader":
                tool_count += self._add_file_reader_tool(tool_config.get("config", {}))
            elif tool_name == "web_search":
                tool_count += self._add_web_search_tool(tool_config.get("config", {}))
            elif tool_name == "json_processor":
                tool_count += self._add_json_processor_tool(
                    tool_config.get("config", {})
                )

        return tool_count

    def _setup_custom_tools(self, custom_tools):
        """Setup custom tools from configuration."""
        tool_count = 0

        for tool_config in custom_tools:
            if not isinstance(tool_config, dict):
                continue

            required_fields = ["name", "description", "function_name", "parameters"]
            if not all(field in tool_config for field in required_fields):
                print(
                    f"⚠️ Skipping custom tool: missing required fields {required_fields}"
                )
                continue

            try:
                tool_count += self._add_custom_tool(tool_config)
            except Exception as e:
                print(
                    f"⚠️ Failed to add custom tool '{tool_config.get('name', 'unknown')}': {str(e)}"
                )

        return tool_count

    def _add_custom_tool(self, tool_config):
        """Add a single custom tool from configuration."""
        tool_name = tool_config["name"]
        description = tool_config["description"]
        function_name = tool_config["function_name"]
        parameters = tool_config["parameters"]
        implementation = tool_config.get("implementation", "")

        # Create custom tool function
        def custom_tool_wrapper(*args, **kwargs):
            """Wrapper for custom tool execution."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation(
                    f"custom_{tool_name}", "tool", args=args, kwargs=kwargs
                ):
                    return self._execute_custom_tool(
                        tool_name, function_name, implementation, *args, **kwargs
                    )
            else:
                return self._execute_custom_tool(
                    tool_name, function_name, implementation, *args, **kwargs
                )

        # Build function signature dynamically
        param_list = []
        for param in parameters:
            param_name = param["name"]
            param_type = param.get("type", "str")
            required = param.get("required", True)
            _ = param.get("description", "")  # noqa: F841 – description not used yet

            if required:
                param_list.append(f"{param_name}: {param_type}")
            else:
                param_list.append(f"{param_name}: {param_type} = None")

        # Update function annotations and docstring
        custom_tool_wrapper.__name__ = function_name
        custom_tool_wrapper.__doc__ = f"{description}\n\nParameters:\n" + "\n".join(
            [
                f"- {p['name']} ({p.get('type', 'str')}): {p.get('description', '')}"
                for p in parameters
            ]
        )

        if Tool:
            self.tools.append(Tool(custom_tool_wrapper, name=tool_name))
            return 1
        else:
            print(f"⚠️ DSPy Tool not available, skipping custom tool '{tool_name}'")
            return 0

    def _execute_custom_tool(
        self, tool_name, function_name, implementation, *args, **kwargs
    ):
        """Execute custom tool with safety checks."""
        try:
            # Create a safe execution environment
            safe_globals = {
                "__builtins__": {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "max": max,
                    "min": min,
                    "sum": sum,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "reversed": reversed,
                },
                "datetime": datetime,
                "json": json,
                "os": os,
                "Path": Path,
                "math": math if "math" in globals() else None,
            }
            safe_locals = {}

            # Execute the implementation code
            if implementation.strip():
                exec(implementation, safe_globals, safe_locals)

                # Call the function
                if function_name in safe_locals:
                    func = safe_locals[function_name]
                    result = func(*args, **kwargs)

                    if hasattr(self, "tracer"):
                        self.tracer.add_event(
                            "custom_tool_success",
                            f"custom_{tool_name}",
                            data={"result": str(result)[:200]},  # Truncate for logging
                            status="success",
                        )

                    return result
                else:
                    return f"❌ Function '{function_name}' not found in implementation"
            else:
                return f"❌ No implementation provided for custom tool '{tool_name}'"

        except Exception as e:
            error_msg = f"Custom tool '{tool_name}' error: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "custom_tool_error",
                    f"custom_{tool_name}",
                    data={"error": error_msg},
                    status="error",
                )

            return f"❌ {error_msg}"

    def _add_calculator_tool(self, config):
        """Add calculator tool with configuration."""
        precision = config.get("precision", 10)

        def calculate(expression: str) -> str:
            """Perform mathematical calculations safely."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation(
                    "calculate", "tool", expression=expression
                ):
                    return self._execute_calculator(expression, precision)
            else:
                return self._execute_calculator(expression, precision)

        if Tool:
            self.tools.append(Tool(calculate, name="calculator"))
            return 1
        return 0

    def _add_datetime_tool(self, config):
        """Add datetime tool with configuration."""

        def get_current_time(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
            """Get current date and time."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation("get_current_time", "tool"):
                    return self._execute_datetime(format_string)
            else:
                return self._execute_datetime(format_string)

        if Tool:
            self.tools.append(Tool(get_current_time, name="datetime"))
            return 1
        return 0

    def _add_text_analyzer_tool(self, config):
        """Add text analyzer tool with configuration."""

        def analyze_text(text: str) -> str:
            """Analyze text for basic statistics."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation(
                    "analyze_text", "tool", text_length=len(text)
                ):
                    return self._execute_text_analyzer(text)
            else:
                return self._execute_text_analyzer(text)

        if Tool:
            self.tools.append(Tool(analyze_text, name="text_analyzer"))
            return 1
        return 0

    def _add_file_reader_tool(self, config):
        """Add file reader tool with configuration."""
        allowed_extensions = config.get(
            "allowed_extensions", ["txt", "md", "json", "yaml", "csv"]
        )
        max_file_size = config.get("max_file_size", "5MB")

        # Convert max_file_size to MB integer
        if isinstance(max_file_size, str) and max_file_size.endswith("MB"):
            max_file_size_mb = int(max_file_size[:-2])
        else:
            max_file_size_mb = 5

        def read_file(file_path: str) -> str:
            """Read file contents safely."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation(
                    "read_file", "tool", file_path=file_path
                ):
                    return self._execute_file_reader(
                        file_path, allowed_extensions, max_file_size_mb
                    )
            else:
                return self._execute_file_reader(
                    file_path, allowed_extensions, max_file_size_mb
                )

        if Tool:
            self.tools.append(Tool(read_file, name="file_reader"))
            return 1
        return 0

    def _add_web_search_tool(self, config):
        """Add web search tool with configuration."""
        max_results = config.get("max_results", 3)
        search_engine = config.get("search_engine", "duckduckgo")

        def web_search(query: str) -> str:
            """Search the web for information."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation("web_search", "tool", query=query):
                    return self._execute_web_search(query, search_engine, max_results)
            else:
                return self._execute_web_search(query, search_engine, max_results)

        if Tool:
            self.tools.append(Tool(web_search, name="web_search"))
            return 1
        return 0

    def _add_json_processor_tool(self, config):
        """Add JSON processor tool with configuration."""

        def process_json(json_string: str, operation: str = "parse") -> str:
            """Process JSON data safely."""
            if hasattr(self, "tracer"):
                with self.tracer.trace_operation(
                    "process_json", "tool", operation=operation
                ):
                    return self._execute_json_processor(json_string, operation)
            else:
                return self._execute_json_processor(json_string, operation)

        if Tool:
            self.tools.append(Tool(process_json, name="json_processor"))
            return 1
        return 0

    def _execute_calculator(self, expression: str, precision: int = 10) -> str:
        """Execute calculator tool with error handling."""
        try:
            calc_tool = CalculatorTool(precision=precision)
            result = calc_tool.calculate(expression)

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "calculate",
                    data={"expression": expression, "result": result},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"Calculation failed: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "calculate",
                    data={"expression": expression, "error": error_msg},
                    status="error",
                )

            return error_msg

    def _execute_datetime(self, format_string: str) -> str:
        """Execute datetime tool with error handling."""
        try:
            datetime_tool = DateTimeTool()
            result = datetime_tool.get_current_time(format_string)

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "get_current_time",
                    data={"format": format_string, "result": result},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"DateTime error: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "get_current_time",
                    data={"error": error_msg},
                    status="error",
                )

            return error_msg

    def _execute_text_analyzer(self, text: str) -> str:
        """Execute text analyzer tool with error handling."""
        try:
            analyzer_tool = TextAnalyzerTool()
            result = analyzer_tool.analyze_text(text)

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "analyze_text",
                    data={"text_length": len(text), "analysis": "completed"},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"Text analysis failed: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "analyze_text",
                    data={"error": error_msg},
                    status="error",
                )

            return error_msg

    def _execute_file_reader(
        self,
        file_path: str,
        allowed_extensions: List[str] = None,
        max_file_size_mb: int = 5,
    ) -> str:
        """Execute file reader tool with error handling."""
        try:
            file_tool = FileReaderTool(
                allowed_extensions=allowed_extensions
                or ["txt", "md", "json", "yaml", "csv"],
                max_file_size_mb=max_file_size_mb,
            )
            result = file_tool.read_file(file_path)

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "read_file",
                    data={"file_path": file_path, "success": True},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"File read failed: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "read_file",
                    data={"file_path": file_path, "error": error_msg},
                    status="error",
                )

            return error_msg

    def _execute_web_search(
        self, query: str, search_engine: str = "duckduckgo", max_results: int = 3
    ) -> str:
        """Execute web search tool with error handling."""
        try:
            from superoptix.tools import WebSearchTool

            search_tool = WebSearchTool(engine=search_engine, max_results=max_results)
            result = search_tool.search(query)

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "web_search",
                    data={"query": query, "engine": search_engine},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"Web search failed: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "web_search",
                    data={"query": query, "error": error_msg},
                    status="error",
                )

            return error_msg

    def _execute_json_processor(
        self, json_string: str, operation: str = "parse"
    ) -> str:
        """Execute JSON processor tool with error handling."""
        try:
            from superoptix.tools import JSONProcessorTool

            json_tool = JSONProcessorTool()

            if operation == "parse":
                result = json_tool.parse_json(json_string)
            else:
                result = f"❌ Unknown JSON operation: {operation}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_success",
                    "process_json",
                    data={"operation": operation, "success": True},
                    status="success",
                )

            return result

        except Exception as e:
            error_msg = f"JSON processing failed: {str(e)}"

            if hasattr(self, "tracer"):
                self.tracer.add_event(
                    "tool_execution_error",
                    "process_json",
                    data={"operation": operation, "error": error_msg},
                    status="error",
                )

            return error_msg


class BDDTestMixin:
    """Enhanced BDD Testing functionality with professional test runner capabilities."""

    def load_bdd_scenarios(self, spec_data: Dict[str, Any]) -> List[dspy.Example]:
        """Load BDD specifications from spec with enhanced validation."""
        scenarios = spec_data.get("feature_specifications", {}).get("scenarios", [])
        examples = []

        for scenario in scenarios:
            try:
                # Extract inputs and expected outputs from scenario
                inputs = scenario.get("input", {})
                expected_outputs = scenario.get("expected_output", {})

                # Create example with metadata
                example_data = {**inputs, **expected_outputs}
                example = dspy.Example(**example_data).with_inputs(*inputs.keys())

                # Add metadata for better test reporting
                example.scenario_name = scenario.get("name", "unnamed_specification")
                example.description = scenario.get(
                    "description", "No description provided"
                )
                example.category = scenario.get("category", "general")

                examples.append(example)
            except Exception as e:
                print(
                    f"⚠️  Warning: Skipping invalid specification '{scenario.get('name', 'unknown')}': {e}"
                )
                continue

        if examples:
            print(f"📋 Loaded {len(examples)} BDD specifications for execution")
        else:
            print("⚠️  No valid BDD specifications found")

        return examples

    def run_bdd_test_suite(
        self, auto_tune: bool = False, ignore_checks: bool = False
    ) -> Dict[str, Any]:
        """Run comprehensive BDD specification suite with progress bar and concise reporting."""
        if not self.test_examples:
            return {
                "success": False,
                "message": "No BDD specifications defined in feature_specifications",
                "summary": {"total": 0, "passed": 0, "failed": 0, "pass_rate": "0.00%"},
                "bdd_results": {"detailed_results": []},
                "model_analysis": {},
                "recommendations": [],
            }

        # ------------------------------------------------------------------
        # 🏃 Execute scenarios with live progress
        # ------------------------------------------------------------------
        from rich.console import Console
        from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

        console = Console()

        detailed_results = []
        total = len(self.test_examples)
        passed_scenarios = 0

        console.print(f"🧪 Running [cyan]{total}[/] BDD specifications...")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            transient=True,
        ) as prog:
            task_id = prog.add_task("Executing", total=total)
            for scenario in self.test_examples:
                result = self._execute_single_scenario(scenario)
                detailed_results.append(result)
                prog.advance(task_id)

                symbol = "✅" if (result.get("passed") or ignore_checks) else "❌"
                console.print(
                    f"{symbol} {getattr(scenario, 'scenario_name', 'Unnamed')}",
                    highlight=False,
                )
                if result.get("passed"):
                    passed_scenarios += 1

        # ------------------------------------------------------------------
        # 🚦 Ignore checks – force pass
        # ------------------------------------------------------------------
        if ignore_checks:
            for r in detailed_results:
                r["passed"] = True
            passed_scenarios = total
            console.print(
                "[yellow]⚠️  Validation checks ignored – treating all scenarios as passed.[/]"
            )

        # ------------------------------------------------------------------
        # 📊 Aggregate metrics
        # ------------------------------------------------------------------
        pass_rate = (passed_scenarios / total * 100) if total else 0

        model_analysis = self._analyze_model_performance(detailed_results)
        recommendations = self._generate_recommendations(detailed_results, pass_rate)

        return {
            "success": True,
            "summary": {
                "total": total,
                "passed": passed_scenarios,
                "failed": total - passed_scenarios,
                "pass_rate": f"{pass_rate:.1f}%",
            },
            "bdd_results": {
                "detailed_results": detailed_results,
                "total_scenarios": total,
                "scenarios_passed": passed_scenarios,
                "scenarios_failed": total - passed_scenarios,
                "pass_rate": f"{pass_rate:.1f}%",
                "bdd_score": pass_rate / 100,
            },
            "model_analysis": model_analysis,
            "recommendations": recommendations,
        }

    def _execute_single_scenario(self, scenario: dspy.Example) -> Dict[str, Any]:
        """Execute a single BDD scenario with comprehensive evaluation."""
        scenario_name = getattr(scenario, "scenario_name", "Unknown")
        description = getattr(scenario, "description", "No description")

        try:
            # Get inputs for the scenario
            inputs = {key: getattr(scenario, key) for key in scenario.inputs()}

            # Execute the agent
            if hasattr(self, "run"):
                result = self.run(**inputs)
            elif hasattr(self, "forward"):
                result = self.forward(**inputs)
            else:
                return {
                    "scenario_name": scenario_name,
                    "description": description,
                    "passed": False,
                    "confidence_score": 0.0,
                    "failure_reason": "No run() or forward() method available",
                }

            # Get expected outputs
            expected_outputs = {
                key: getattr(scenario, key) for key in scenario.labels()
            }

            if not expected_outputs:
                # Simple existence check if no expected outputs
                passed = bool(result and len(str(result).strip()) > 0)
                return {
                    "scenario_name": scenario_name,
                    "description": description,
                    "passed": passed,
                    "confidence_score": 1.0 if passed else 0.0,
                    "failure_reason": None
                    if passed
                    else "Empty or no response generated",
                    "actual_output": str(result),
                    "expected_output": "Non-empty response",
                }

            # Comprehensive evaluation
            evaluation_result = self._evaluate_scenario_output(
                result, expected_outputs, scenario
            )

            return {
                "scenario_name": scenario_name,
                "description": description,
                "passed": evaluation_result["passed"],
                "confidence_score": evaluation_result["confidence_score"],
                "semantic_similarity": evaluation_result.get(
                    "semantic_similarity", 0.0
                ),
                "failure_reason": evaluation_result.get("failure_reason"),
                "actual_output": str(result),
                "expected_output": expected_outputs,
                "criteria_breakdown": evaluation_result.get("criteria_breakdown", {}),
            }

        except Exception as e:
            return {
                "scenario_name": scenario_name,
                "description": description,
                "passed": False,
                "confidence_score": 0.0,
                "failure_reason": f"Execution error: {str(e)}",
                "error": str(e),
            }

    def _evaluate_scenario_output(
        self,
        actual_output: Any,
        expected_outputs: Dict[str, Any],
        scenario: dspy.Example,
    ) -> Dict[str, Any]:
        """Evaluate scenario output using multiple criteria."""
        actual_str = str(actual_output).strip()

        # Handle different expected output formats
        if len(expected_outputs) == 1:
            expected_str = str(list(expected_outputs.values())[0]).strip()
        else:
            expected_str = str(expected_outputs).strip()

        if not actual_str:
            return {
                "passed": False,
                "confidence_score": 0.0,
                "failure_reason": "Empty response generated",
            }

        # Multi-criteria evaluation
        try:
            # 1. Semantic similarity (using simple heuristics)
            semantic_score = self._calculate_semantic_similarity(
                actual_str, expected_str
            )

            # 2. Keyword presence
            keyword_score = self._calculate_keyword_presence(actual_str, expected_str)

            # 3. Length appropriateness
            length_score = self._calculate_length_score(actual_str, expected_str)

            # 4. Structure similarity
            structure_score = self._calculate_structure_score(actual_str, expected_str)

            # Weighted final score
            weights = {"semantic": 0.5, "keyword": 0.2, "structure": 0.2, "length": 0.1}

            confidence_score = (
                semantic_score * weights["semantic"]
                + keyword_score * weights["keyword"]
                + structure_score * weights["structure"]
                + length_score * weights["length"]
            )

            # Determine pass/fail
            threshold = 0.6  # 60% threshold for passing
            passed = confidence_score >= threshold

            failure_reason = None
            if not passed:
                if semantic_score < 0.5:
                    failure_reason = "semantic meaning differs significantly"
                elif keyword_score < 0.3:
                    failure_reason = "missing key terms or concepts"
                elif structure_score < 0.4:
                    failure_reason = "output structure doesn't match expectations"
                elif length_score < 0.5:
                    failure_reason = "response length inappropriate"
                else:
                    failure_reason = "overall quality below threshold"

            return {
                "passed": passed,
                "confidence_score": confidence_score,
                "semantic_similarity": semantic_score,
                "failure_reason": failure_reason,
                "criteria_breakdown": {
                    "semantic_similarity": semantic_score,
                    "keyword_presence": keyword_score,
                    "structure_match": structure_score,
                    "output_length": length_score,
                },
            }

        except Exception as e:
            return {
                "passed": False,
                "confidence_score": 0.0,
                "failure_reason": f"Evaluation error: {str(e)}",
            }

    def _calculate_semantic_similarity(self, actual: str, expected: str) -> float:
        """Calculate semantic similarity using simple text analysis."""
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())

        if not expected_words:
            return 1.0 if not actual_words else 0.5

        # Jaccard similarity
        intersection = actual_words.intersection(expected_words)
        union = actual_words.union(expected_words)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_keyword_presence(self, actual: str, expected: str) -> float:
        """Calculate how many important keywords are present."""
        # Extract important words (longer than 3 chars, excluding common words)
        common_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        expected_keywords = {
            word.lower()
            for word in expected.split()
            if len(word) > 3 and word.lower() not in common_words
        }
        actual_keywords = {
            word.lower()
            for word in actual.split()
            if len(word) > 3 and word.lower() not in common_words
        }

        if not expected_keywords:
            return 1.0

        found_keywords = actual_keywords.intersection(expected_keywords)
        return len(found_keywords) / len(expected_keywords)

    def _calculate_length_score(self, actual: str, expected: str) -> float:
        """Calculate appropriateness of response length."""
        actual_len = len(actual.split())
        expected_len = len(expected.split())

        if expected_len == 0:
            return 1.0 if actual_len > 0 else 0.0

        ratio = actual_len / expected_len

        # Optimal range is 0.5x to 2x expected length
        if 0.5 <= ratio <= 2.0:
            return 1.0
        elif 0.25 <= ratio < 0.5 or 2.0 < ratio <= 4.0:
            return 0.7
        else:
            return 0.3

    def _calculate_structure_score(self, actual: str, expected: str) -> float:
        """Calculate structural similarity (lines, paragraphs, formatting)."""
        actual_lines = len(actual.split("\n"))
        expected_lines = len(expected.split("\n"))

        # Check for similar number of lines/paragraphs
        if expected_lines == 0:
            return 1.0

        line_ratio = min(actual_lines, expected_lines) / max(
            actual_lines, expected_lines
        )

        # Check for similar formatting patterns
        actual_has_bullets = "•" in actual or "*" in actual or "-" in actual
        expected_has_bullets = "•" in expected or "*" in expected or "-" in expected

        format_match = 1.0 if actual_has_bullets == expected_has_bullets else 0.5

        return (line_ratio + format_match) / 2

    def _analyze_model_performance(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze model performance and capabilities."""
        if not results:
            return {"model_name": "Unknown", "capability_score": 0.0}

        # Calculate average scores
        total_score = sum(r.get("confidence_score", 0.0) for r in results)
        avg_score = total_score / len(results)

        # Determine model capability based on performance
        if avg_score >= 0.8:
            capability_assessment = "High - suitable for complex tasks"
        elif avg_score >= 0.6:
            capability_assessment = "Medium - good for standard tasks"
        elif avg_score >= 0.4:
            capability_assessment = "Basic - suitable for simple tasks"
        else:
            capability_assessment = "Limited - needs improvement or different model"

        # Suggest model upgrades based on performance
        suggested_upgrade = "None needed"
        if avg_score < 0.6:
            suggested_upgrade = "Consider llama3.1:8b or gpt-4 for better performance"
        elif avg_score < 0.4:
            suggested_upgrade = (
                "Strongly recommend gpt-4 or claude-3 for reliable results"
            )

        # Get model name safely
        model_name = "Unknown"
        try:
            if hasattr(self, "lm") and self.lm:
                if hasattr(self.lm, "model"):
                    model_name = self.lm.model
                elif hasattr(self.lm, "_model"):
                    model_name = self.lm._model
                elif hasattr(self.lm, "kwargs") and "model" in self.lm.kwargs:
                    model_name = self.lm.kwargs["model"]
                else:
                    model_name = str(type(self.lm).__name__)
        except Exception:
            model_name = "Unknown"

        return {
            "model_name": model_name,
            "capability_score": avg_score,
            "capability_assessment": capability_assessment,
            "suggested_upgrade": suggested_upgrade,
            "performance_category": "excellent"
            if avg_score >= 0.8
            else "good"
            if avg_score >= 0.6
            else "needs_improvement",
        }

    def _generate_recommendations(
        self, results: List[Dict[str, Any]], pass_rate: float
    ) -> List[str]:
        """Generate actionable recommendations based on test results."""
        recommendations = []

        if not results:
            recommendations.append(
                "Add BDD scenarios to your agent playbook for proper testing"
            )
            return recommendations

        failed_results = [r for r in results if not r.get("passed")]

        if pass_rate == 100:
            recommendations.append(
                "Excellent! All scenarios pass. Consider adding more comprehensive test cases."
            )
            recommendations.append("Your agent is ready for production use.")
        elif pass_rate >= 80:
            recommendations.append(
                f"Good performance! {len(failed_results)} scenario(s) need minor improvements."
            )
            recommendations.append("Review failing scenarios and refine agent context.")
        elif pass_rate >= 60:
            recommendations.append(
                f"Moderate performance. {len(failed_results)} scenarios failing."
            )
            recommendations.append(
                "Consider running optimization: super agent optimize <agent_name>"
            )
            recommendations.append(
                "Review and improve scenario expectations or agent capabilities."
            )
        else:
            recommendations.append(
                f"Poor performance. {len(failed_results)} scenarios failing."
            )
            recommendations.append(
                "Strong recommendation: Run optimization before production use."
            )
            recommendations.append(
                "Consider using a more capable model (llama3.1:8b or gpt-4)."
            )
            recommendations.append("Review scenario complexity vs model capabilities.")

        # Analysis-based recommendations
        semantic_issues = sum(
            1
            for r in failed_results
            if r.get("failure_reason", "").startswith("semantic")
        )
        keyword_issues = sum(
            1 for r in failed_results if "keyword" in r.get("failure_reason", "")
        )
        structure_issues = sum(
            1 for r in failed_results if "structure" in r.get("failure_reason", "")
        )

        if semantic_issues > 0:
            recommendations.append(
                f"Fix semantic relevance in {semantic_issues} scenario(s) - improve response clarity."
            )
        if keyword_issues > 0:
            recommendations.append(
                f"Add missing technical terms in {keyword_issues} scenario(s)."
            )
        if structure_issues > 0:
            recommendations.append(
                f"Improve output formatting in {structure_issues} scenario(s)."
            )

        return recommendations

    def create_examples(
        self, data: List[Dict[str, Any]], input_keys: List[str] | None = None
    ) -> List[dspy.Example]:
        """Convert raw dict records *data* into ``dspy.Example`` objects.

        Generated SuperOptiX pipelines – as well as the training/evaluation
        helpers inside :pyclass:`TrainingMixin` – expect the convenience
        method ``self.create_examples`` to be present.  Recent versions of
        DSPy expose a **module level** :pyfunc:`dspy.create_examples` helper,
        however calling it via ``self`` resulted in an ``AttributeError`` and
        broke optimisation commands like ``super agent optimize``.

        By defining a thin wrapper here we:
        1. Preserve the original ergonomic call-site syntax (``self.create_examples``).
        2. Gracefully fall back to a minimal implementation when DSPy is
           either missing or its helper signature changes between versions.
        3. Keep the logic in one central place so newly generated pipelines
           inherit the fix automatically without code regeneration.
        """
        try:
            # Newer DSPy releases ship the helper at module scope.
            from dspy import create_examples as dspy_create_examples  # type: ignore

            if input_keys is not None:
                return dspy_create_examples(data, input_keys)
            # Older signatures may not support *input_keys* – try without.
            return dspy_create_examples(data)
        except (ImportError, AttributeError, TypeError):
            # Fallback: manual construction to maintain basic functionality.
            examples: List[dspy.Example] = []
            for record in data:
                try:
                    example = dspy.Example(**record)
                    if input_keys:
                        example = example.with_inputs(*input_keys)
                    else:
                        example = example.with_inputs(*record.keys())
                    examples.append(example)
                except Exception as e:
                    print(f"⚠️  Skipping invalid training example: {e}")
            return examples


class UsageTrackingMixin:
    """Mixin that provides standardized usage tracking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usage_stats = {}
        self.current_call_usage = {}

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    def reset_copy(self):
        """Return a fresh copy of the pipeline with cleared usage stats.

        Some DSPy optimizers (e.g., BootstrapFewShot, LabeledFewShot) expect
        the module they optimise to expose a ``reset_copy`` method that
        yields an *independent* instance ready for a new optimisation epoch.
        Failing to implement this leads to errors such as::

            'FooPipeline' object has no attribute 'reset_copy'

        We recreate the module via its constructor if possible; otherwise we
        fall back to ``copy.deepcopy``. Usage statistics are reset either way
        to ensure clean accounting.
        """

        import copy

        try:
            fresh = self.__class__()
        except Exception:
            # As a safety-net fall back to deepcopy which works for most
            # objects as long as their state is picklable.
            fresh = copy.deepcopy(self)

        # Ensure usage tracking state starts from scratch on the new copy.
        if hasattr(fresh, "usage_stats"):
            fresh.usage_stats = {}
        if hasattr(fresh, "current_call_usage"):
            fresh.current_call_usage = {}

        return fresh

    @contextmanager
    def usage_tracking_context(self):
        """Context manager to aggregate DSPy token usage safely.

        The previous implementation yielded twice (once in the main flow and
        again in the ``except`` branch) which breaks the contract of
        ``contextlib.contextmanager`` and surfaces as ``generator didn't stop
        after throw()`` errors inside optimisers.  The new version guarantees
        exactly **one** yield regardless of success or failure of the usage
        tracker.
        """

        self.current_call_usage = {}

        tracker_cm = None
        tracker = None
        try:
            # Attempt to enter DSPy's usage tracker. This can fail for local
            # builds or stripped-down versions, so we guard it.
            tracker_cm = dspy.track_usage()
            tracker = tracker_cm.__enter__()
        except Exception as e:
            # Gracefully degrade when tracking is unavailable.
            print(f"Warning: Usage tracking failed ({e}), continuing without it.")

        try:
            # Yield control back to the caller (exactly once!)
            yield
        finally:
            # If we managed to start the tracker, harvest stats now.
            if tracker is not None:
                try:
                    usage_data = tracker.get_total_tokens() or {}
                    self.current_call_usage = usage_data
                    self.safe_update_usage_stats(self.usage_stats, usage_data)
                except Exception:
                    pass

            # Ensure we properly exit the tracker context manager to avoid
            # resource leaks even when exceptions were raised in the body.
            if tracker_cm is not None:
                try:
                    tracker_cm.__exit__(None, None, None)
                except Exception:
                    pass

    def safe_update_usage_stats(
        self, cumulative_stats: Dict[str, Any], new_usage: Dict[str, Any]
    ) -> None:
        """Safely update cumulative usage statistics handling None values."""
        for model, stats in new_usage.items():
            if model not in cumulative_stats:
                cumulative_stats[model] = {}
            if isinstance(stats, dict):
                for key, value in stats.items():
                    # Handle None values from models that don't report usage
                    if value is not None:
                        current_value = cumulative_stats[model].get(key, 0)
                        if current_value is not None:
                            cumulative_stats[model][key] = current_value + value
                        else:
                            cumulative_stats[model][key] = value
                    else:
                        # If model doesn't report this metric, initialize to 0
                        if key not in cumulative_stats[model]:
                            cumulative_stats[model][key] = 0

    # ------------------------------------------------------------------
    # Pickling helpers (DSPy optimiser relies on deepcopy)
    # ------------------------------------------------------------------
    def __getstate__(self):
        """Return a state dictionary safe for ``pickle`` / ``deepcopy``.

        Some objects (e.g. httpx clients, thread locks, LM adapters) held by
        the pipeline cannot be pickled.  We strip them from the state so that
        ``copy.deepcopy`` used inside DSPy optimisers works without raising
        ``TypeError: cannot pickle '_thread.RLock' object``.
        """

        import pickle

        state = self.__dict__.copy()

        # Remove known heavy / unpicklable attributes explicitly.
        for attr in ("tracer", "lm", "tools"):
            if attr in state:
                state[attr] = None

        # Additionally, drop anything that still fails basic pickling.
        for key in list(state.keys()):
            try:
                pickle.dumps(state[key])
            except Exception:
                state[key] = None

        return state


class EvaluationMixin:
    """Mixin that provides standardized evaluation framework."""

    def semantic_f1_metric(
        self,
        gold: dspy.Example,
        pred: dspy.Prediction,
        input_field: str = "query",
        output_field: str = "response",
    ) -> float:
        """Semantic F1 evaluation metric with fallback."""
        try:
            if not SemanticF1:
                return self._fallback_similarity_metric(
                    gold, pred, input_field, output_field
                )

            # Get the actual data from the gold example and prediction
            question = getattr(gold, input_field)
            ground_truth = getattr(gold, output_field)
            system_response = getattr(pred, output_field)

            # Use SemanticF1 from dspy.evaluate.auto_evaluation
            metric = SemanticF1()

            # Create temporary objects with expected field names
            temp_example = dspy.Example(question=question, response=ground_truth)
            temp_pred = dspy.Prediction(response=system_response)

            if hasattr(self, "lm"):
                with dspy.context(lm=self.lm):
                    score = metric(temp_example, temp_pred)
            else:
                score = metric(temp_example, temp_pred)

            return score

        except Exception as e:
            print(
                f"Warning: Semantic evaluation failed ({e}), using fallback similarity"
            )
            return self._fallback_similarity_metric(
                gold, pred, input_field, output_field
            )

    def _fallback_similarity_metric(
        self,
        gold: dspy.Example,
        pred: dspy.Prediction,
        input_field: str,
        output_field: str,
    ) -> float:
        """Fallback similarity metric using word overlap."""
        try:
            ground_truth = getattr(gold, output_field)
            system_response = getattr(pred, output_field)

            if not ground_truth or not system_response:
                return 0.0

            # Simple word overlap similarity
            words_gold = set(str(ground_truth).lower().split())
            words_pred = set(str(system_response).lower().split())

            if not words_gold:
                return 0.0

            intersection = words_gold.intersection(words_pred)
            union = words_gold.union(words_pred)

            return len(intersection) / len(union) if union else 0.0

        except Exception:
            return 0.0

    def evaluate_pipeline(
        self,
        test_data: List[Dict[str, Any]],
        input_field: str = "query",
        output_field: str = "response",
    ) -> Dict[str, Any]:
        """Evaluate pipeline performance on test data."""
        if not test_data:
            return {
                "total_examples": 0,
                "average_score": 0.0,
                "scores": [],
                "success": False,
                "error": "No test data provided",
            }

        try:
            # Create examples
            examples = self.create_examples(test_data, [input_field])

            if not examples:
                return {
                    "total_examples": 0,
                    "average_score": 0.0,
                    "scores": [],
                    "success": False,
                    "error": "Failed to create valid examples",
                }

            scores = []

            print(f"📊 Evaluating pipeline on {len(examples)} examples...")

            for example in examples:
                try:
                    # Get prediction
                    inputs = {key: getattr(example, key) for key in example.inputs()}
                    prediction = self.run(**inputs) if hasattr(self, "run") else {}

                    # Convert prediction to dspy.Prediction if needed
                    if not isinstance(prediction, dspy.Prediction):
                        pred_obj = dspy.Prediction()
                        if isinstance(prediction, dict):
                            for key, value in prediction.items():
                                setattr(pred_obj, key, value)
                        else:
                            setattr(pred_obj, output_field, str(prediction))
                        prediction = pred_obj

                    # Calculate score
                    score = self.semantic_f1_metric(
                        example, prediction, input_field, output_field
                    )
                    scores.append(score)

                except Exception as e:
                    print(f"Warning: Failed to evaluate example: {e}")
                    scores.append(0.0)

            average_score = sum(scores) / len(scores) if scores else 0.0

            return {
                "total_examples": len(examples),
                "average_score": average_score,
                "scores": scores,
                "success": True,
                "error": None,
            }

        except Exception as e:
            error_msg = f"Evaluation failed: {str(e)}"
            print(f"❌ {error_msg}")

            return {
                "total_examples": 0,
                "average_score": 0.0,
                "scores": [],
                "success": False,
                "error": error_msg,
            }


class PipelineUtilities:
    """Collection of pipeline utility functions that can be imported individually."""

    @staticmethod
    def setup_language_model_quick(
        model_name: str = "llama3.1:8b",
        provider: str = "ollama",
        temperature: float = 0.1,
    ) -> dspy.LM:
        """Quick model setup for simple use cases."""
        if provider == "ollama":
            return dspy.LM(
                model=f"ollama_chat/{model_name}",
                api_base="http://localhost:11434",
                api_key="",
                temperature=temperature,
                max_tokens=2000,
                max_retries=2,
                timeout=30,
            )
        else:
            return dspy.LM(model=model_name, temperature=temperature)

    @staticmethod
    def create_react_agent(signature_class, tools: List = None, max_iters: int = 5):
        """Create a ReAct agent with fallback to ChainOfThought."""
        try:
            if ReAct and tools:
                return ReAct(
                    signature=signature_class,
                    tools=tools,
                    max_iters=max_iters,
                )
            elif ChainOfThought:
                return ChainOfThought(signature_class)
            else:
                return dspy.Predict(signature_class)
        except Exception as e:
            print(f"Warning: Failed to create ReAct agent: {e}")
            return dspy.Predict(signature_class)

    @staticmethod
    def get_optimizer(tier: str, k: int = 5):
        """Get appropriate optimizer for tier - DEPRECATED: Use get_custom_optimizer instead."""
        from .optimizer_factory import DSPyOptimizerFactory

        # Use the new factory for better optimizer selection
        return DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier=tier, training_data_size=k, optimizer_config=None
        )

    @staticmethod
    def get_custom_optimizer(optimizer_name: str, params: dict = None, lm=None):
        """Get custom optimizer by name with parameters using the new factory."""
        from .optimizer_factory import DSPyOptimizerFactory

        # Convert old-style params to new format
        if params is None:
            params = {}

        # Extract LM config from params if available
        lm_config = None
        if lm is not None:
            lm_config = {
                "model": getattr(lm, "model", "llama3.1:8b"),
                "provider": "ollama",
            }

        try:
            return DSPyOptimizerFactory.create_optimizer(
                optimizer_name=optimizer_name, params=params, lm_config=lm_config
            )
        except Exception as e:
            print(
                f"[SuperOptiX] Warning: Could not create optimizer {optimizer_name}: {e}"
            )

            # Fallback to dummy optimizer
            class DummyOptimizer:
                def compile(self, module, trainset=None):
                    return module

            return DummyOptimizer()


class TrainingMixin(UsageTrackingMixin, EvaluationMixin, BDDTestMixin):
    """Generic training / optimisation helper shared by all optimised pipelines.

    It centralises the logic that used to live in every template:
      • Retrieves/derives training examples (or falls back to BDD scenarios).
      • Shows a rich.progress bar while converting raw dicts → dspy.Example.
      • Selects the proper DSPy optimiser via PipelineUtilities.get_optimizer.
      • Saves the optimised weights when requested.
    """

    def _auto_prepare_examples(
        self, training_data: List[Dict[str, Any]], input_field: str, output_field: str
    ):
        """Render a progress bar while copying data – purely cosmetic."""
        from rich.progress import Progress

        converted: List[Dict[str, Any]] = []
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Preparing examples...", total=len(training_data)
            )
            for item in training_data:
                converted.append(
                    {
                        input_field: item.get(input_field, ""),
                        output_field: item.get(output_field, ""),
                    }
                )
                progress.advance(task)
        return converted

    def train(
        self,
        training_data: List[Dict[str, Any]] | None = None,
        *,
        tier: str = "oracles",
        save_optimized: bool = False,
        optimized_path: str | None = None,
        k: int | None = None,
    ) -> Dict[str, Any]:
        """Universal train/optimise method.

        Parameters
        ----------
        training_data : list[dict] | None
            List of {input_field: str, output_field: str} pairs.  If *None*, the
            method falls back to the first N BDD scenarios attached to the
            pipeline (``self.test_examples``).
        tier : str
            "oracles" (default) or "genies"  – controls default optimiser *k*.
        save_optimized : bool
            Persist optimiser weights to *optimized_path*.
        optimized_path : str | None
            Destination file for weights.
        k : int | None
            Override the optimiser's *k* hyper-parameter.
        """

        stats = {
            "started_at": datetime.now().isoformat(),
            "training_data_size": 0,
            "success": False,
            "usage_stats": {},
            "error": None,
        }

        # ------------------------------------------------------------------
        # 1. Gather examples -------------------------------------------------
        # ------------------------------------------------------------------
        if not training_data:
            scenarios = getattr(self, "test_examples", None) or []
            if scenarios:
                training_data = []
                # Deduce fields from first scenario
                attrs = scenarios[0].__dict__.keys()
                input_field = (
                    "feature_specification"
                    if "feature_specification" in attrs
                    else "query"
                )
                output_candidates = [
                    a for a in attrs if a not in (input_field, "reasoning", "query")
                ]
                output_field = output_candidates[0] if output_candidates else "response"

                limit = 8 if tier == "genies" else 3
                for ex in scenarios[:limit]:
                    training_data.append(
                        {
                            input_field: getattr(ex, input_field, ""),
                            output_field: getattr(ex, output_field, ""),
                        }
                    )
            else:
                print("ℹ️  No training data available – using base model")
                stats["success"] = True
                stats["note"] = "No training data provided"
                return stats

        # Identify canonical fields from first record
        sample = training_data[0]
        input_field = next(iter(sample.keys()))
        output_field = next((k for k in sample if k != input_field), "response")

        stats["training_data_size"] = len(training_data)
        print(f"🚀 Training with {len(training_data)} examples…")

        # Ensure any additional required fields (e.g. 'context') exist
        required_inputs = {input_field}
        # Try to discover additional inputs from the executor's annotations
        executor = getattr(self, "react", None) or getattr(self, "module", None) or self
        if hasattr(executor, "__annotations__"):
            required_inputs |= {
                k
                for k, v in executor.__annotations__.items()
                if k not in (output_field,) and k not in training_data[0]
            }

        # Provide empty strings for missing fields to avoid DSPy warnings
        for item in training_data:
            for fld in required_inputs:
                item.setdefault(fld, "")

        training_data = self._auto_prepare_examples(
            training_data, input_field, output_field
        )

        # ------------------------------------------------------------------
        # 2. Optimiser & compilation ---------------------------------------
        # ------------------------------------------------------------------
        if k is None:
            k = 8 if tier == "genies" else 5

        optimizer = PipelineUtilities.get_optimizer(tier, k=min(len(training_data), k))

        try:
            with self.usage_tracking_context():
                with dspy.context(lm=self.lm):
                    # Only include real input fields (exclude label/output).
                    input_keys_list = [input_field]
                    if "context" in training_data[0] and input_field != "context":
                        input_keys_list.append("context")
                    trainset = self.create_examples(training_data, input_keys_list)
                    if not trainset:
                        raise ValueError("No valid examples after conversion")

                    target = (
                        getattr(self, "react", None)
                        or getattr(self, "module", None)
                        or self
                    )
                    # Visual feedback while DSPy optimiser runs (can be slow)
                    from rich.progress import Progress, SpinnerColumn, TextColumn

                    with Progress(
                        SpinnerColumn(), TextColumn("[cyan]{task.description}")
                    ) as pbar:
                        t = pbar.add_task("Optimising with DSPy…", total=None)
                        compiled = optimizer.compile(target, trainset=trainset)
                        pbar.update(t, completed=1)

                    # Persist the result back
                    if hasattr(self, "react"):
                        self.react = compiled
                    elif hasattr(self, "module"):
                        self.module = compiled

                    self.is_trained = True

                    if save_optimized and optimized_path:
                        try:
                            compiled.save(optimized_path)
                            stats["optimized_saved"] = True
                            stats["optimized_path"] = optimized_path
                        except Exception as e:
                            print(f"⚠️  Could not save weights: {e}")
                            stats["optimized_saved"] = False

            stats["usage_stats"] = self.current_call_usage
            stats["success"] = True
        except Exception as e:
            stats["error"] = str(e)
            print(f"❌ Training failed: {e}")

        stats["completed_at"] = datetime.now().isoformat()
        return stats


class CLITestShimMixin:
    """Thin wrapper that exposes run_bdd_test_suite for legacy CLI calls."""

    def run_bdd_test_suite(self, auto_tune: bool = False, ignore_checks: bool = False):
        return super().run_bdd_test_suite(
            auto_tune=auto_tune, ignore_checks=ignore_checks
        )

    # ------------------------------------------------------------------
    # Legacy DSL compatibility: provide a no-op setup method.
    # ------------------------------------------------------------------
    def setup(self):
        """Legacy no-operation setup to satisfy older CLI runners.

        Recent slim pipelines fully initialise themselves inside ``__init__``.
        However, the existing `dspy_runner` still invokes ``pipeline.setup()``
        unconditionally when no optimized weights are loaded.  Implementing
        this stub avoids AttributeError crashes while preserving backwards
        compatibility.
        """

        print("✅ Pipeline initialisation already complete – setup skipped.")

        return {
            "status": "ready",
            "model": getattr(getattr(self, "lm", None), "model", "unknown"),
            "tools": len(getattr(self, "tools", [])),
            "tier": "genies" if hasattr(self, "react") else "oracles",
        }


# ---------------------------------------------------------------------------
#  ExecutionMixin – unified forward & run helpers
# ---------------------------------------------------------------------------


class ExecutionMixin:
    """Provides async `forward` and sync `run` wrappers shared by all pipelines.

    It supports three possible underlying executors:
    • self.react  – a ReAct agent (genie tier)
    • self.module – a plain dspy.Module (oracle tier)
    • fallback    – call `self` if it is itself callable.
    """

    # ---------- async forward ------------------------------------------------
    async def forward(self, question: str, context: str = "") -> Dict[str, Any]:
        """Execute the agent; detects the correct executor automatically."""
        start = datetime.now()

        executor = getattr(self, "react", None) or getattr(self, "module", None) or self

        # Determine canonical input field via inspect to ensure correct mapping
        try:
            param_names = list(inspect.signature(executor).parameters)
        except (ValueError, TypeError):
            param_names = []

        preferred_order = [
            "feature_specification",  # BDD/QA agents
            "question",  # Common ReAct signatures
            "query",  # Generic pipelines
            "input",  # Fallback generic
        ]

        _ = next(
            (p for p in preferred_order if p in param_names),
            param_names[0] if param_names else "query",
        )  # noqa: F841

        # Provide the question under multiple possible field names so that
        # whichever the compiled module expects will be satisfied. This
        # eliminates DSPy warnings about missing inputs when we cannot
        # reliably introspect the optimiser-compiled object.

        inputs = {
            "context": context,
            "feature_specification": question,
            "question": question,
            "query": question,
            "input": question,
        }

        try:
            if callable(executor):
                # Ensure the language model is active for this call
                if hasattr(self, "lm") and self.lm is not None:
                    with dspy.context(lm=self.lm):
                        result = executor(**inputs)
                else:
                    result = executor(**inputs)
            else:
                raise AttributeError("Executor is not callable")

            # Await coroutine if needed
            if hasattr(result, "__await__"):
                result = await result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0,
            }

        duration = (datetime.now() - start).total_seconds()

        # If result is already a dict, attach metadata and return
        if isinstance(result, dict):
            result.setdefault("success", True)
            result.setdefault("execution_time", duration)
            return result

        # Handle DSPy Prediction objects: extract meaningful fields
        try:
            from dspy.predict import Prediction  # type: ignore
        except ImportError:
            Prediction = None

        if Prediction and isinstance(result, Prediction):
            payload = {
                k: v
                for k, v in vars(result).items()
                if k not in ("trajectory",) and not k.startswith("_")
            }

            if not payload:
                payload["response"] = str(getattr(result, "answer", "")) or str(result)

            payload["success"] = True
            payload["execution_time"] = duration
            return payload

        # Fallback: return string representation
        return {
            "response": str(result),
            "success": True,
            "execution_time": duration,
        }

    # ---------- sync wrapper --------------------------------------------------
    def run(self, **inputs):
        """Blocking wrapper that delegates to *forward* safely from sync code."""
        question = (
            inputs.get("feature_specification")
            or inputs.get("query")
            or inputs.get("question")
            or ""
        )
        context = inputs.get("context", "")

        import concurrent.futures

        try:
            asyncio.get_running_loop()  # ensure loop exists
            with concurrent.futures.ThreadPoolExecutor() as pool:
                fut = pool.submit(lambda: asyncio.run(self.forward(question, context)))
                return fut.result()
        except RuntimeError:
            # no running loop – create a new one
            return asyncio.run(self.forward(question, context))

    # ---------- dunder-call wrapper -----------------------------------------
    async def __call__(self, *args, **kwargs):
        """Make the pipeline itself awaitable/callable.

        The ``dspy_runner`` expects to invoke pipelines directly with
            ``await pipeline(query)``
        This shim forwards the call to :meth:`forward`, extracting *question*
        and optional *context* arguments from ``args`` / ``kwargs``.
        """

        # Allow flexible invocation styles
        if args and isinstance(args[0], str):
            question = args[0]
            context = args[1] if len(args) > 1 else kwargs.get("context", "")
        else:
            question = kwargs.get("question") or kwargs.get("query") or ""
            context = kwargs.get("context", "")

        return await self.forward(question, context)
