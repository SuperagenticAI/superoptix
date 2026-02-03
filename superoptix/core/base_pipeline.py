"""
SuperOptix Base Pipeline - Abstract Common Functionality
========================================================

This base class abstracts repetitive boilerplate while maintaining developer control
over DSPy signatures, forward logic, and custom tools/evaluations.
"""

from abc import ABC, ABCMeta, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import dspy
from dspy.evaluate.auto_evaluation import SemanticF1

# SuperOptix framework imports
from superoptix.observability.tracer import SuperOptixTracer
from superoptix.tools.factories.tool_factory import get_default_tools

# Memory import with graceful fallback
try:
    from superoptix.memory import AgentMemory
except ImportError:
    # Graceful fallback if memory system not available
    AgentMemory = None


# Create a metaclass that resolves the conflict between dspy.Module and ABC
class SuperOptixMeta(type(dspy.Module), ABCMeta):
    pass


class SuperOptixPipeline(dspy.Module, ABC, metaclass=SuperOptixMeta):
    """
    Abstract base class for SuperOptix pipelines.

    Abstracts:
    - Tracing and observability setup
    - Tool management and registration
    - Model configuration and optimization
    - BDD test execution and evaluation
    - Usage tracking and performance monitoring

    Developers customize:
    - DSPy signature definition
    - Forward pass logic
    - Custom tools (optional)
    - Custom evaluation metrics (optional)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()  # Initialize dspy.Module
        self.config = config or {}
        self.tier_level = self.config.get("tier_level", "oracles")
        self.is_trained = False
        self.module = self  # For runner compatibility

        # Auto-setup framework components
        self._setup_tracing()
        self._setup_language_model()
        self._setup_tools()
        self._setup_memory()
        self._setup_evaluation()

        # Call user-defined setup
        self.setup()

    # =================================================================
    # ABSTRACT METHODS - Must be implemented by developers
    # =================================================================

    @abstractmethod
    def get_signature(self) -> dspy.Signature:
        """Return the DSPy signature for this agent."""
        pass

    @abstractmethod
    def forward(self, **kwargs) -> dspy.Prediction:
        """Implement the core reasoning logic."""
        pass

    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the agent name for tracing/logging."""
        pass

    # =================================================================
    # OPTIONAL CUSTOMIZATION HOOKS
    # =================================================================

    def setup(self) -> None:
        """Override for custom initialization."""
        pass

    def get_custom_tools(self) -> List[Any]:
        """Override to add custom tools beyond built-ins."""
        return []

    def get_custom_evaluation_metric(self) -> Optional[callable]:
        """Override to provide custom evaluation beyond semantic F1."""
        return None

    def get_bdd_scenarios(self) -> List[Dict[str, Any]]:
        """Override to provide custom BDD scenarios."""
        return self._load_default_bdd_scenarios()

    # =================================================================
    # FRAMEWORK ABSTRACTIONS - Auto-handled
    # =================================================================

    def _setup_tracing(self):
        """Auto-setup comprehensive tracing."""
        agent_name = self.get_agent_name()
        self.agent_id = f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.tracer = SuperOptixTracer(
            agent_id=self.agent_id,
            enable_external_tracing=self.config.get("enable_external_tracing", False),
        )

        # Setup trace storage
        self.traces_dir = Path(self.config.get("traces_dir", "traces"))
        self.traces_dir.mkdir(parents=True, exist_ok=True)

        dspy.enable_logging()
        print(f"🔍 Auto-tracing enabled for {agent_name}")

    def _setup_language_model(self):
        """Auto-setup language model with tier-appropriate defaults."""
        with self.tracer.trace_operation("model_init", "pipeline"):
            tier_models = {
                "oracles": "llama3.2:1b",
                "genies": "llama3.1:8b",
                "sage": "llama3.1:70b",
            }

            model_name = self.config.get("model", tier_models[self.tier_level])
            provider = self.config.get("provider", "ollama")

            self.lm = dspy.LM(
                model=f"ollama_chat/{model_name}",
                api_base=self.config.get("api_base", "http://localhost:11434"),
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens", 2000),
            )

            print(
                f"✅ Auto-configured {provider}/{model_name} for {self.tier_level}-tier"
            )

    def _setup_tools(self):
        """Auto-setup tools with custom additions."""
        with self.tracer.trace_operation("tools_setup", "pipeline"):
            # Start with default tools
            self.tools = get_default_tools()

            # Add custom tools if provided
            custom_tools = self.get_custom_tools()
            self.tools.extend(custom_tools)

            print(f"🛠️  Auto-configured {len(self.tools)} tools")

    def _setup_memory(self):
        """Auto-setup memory system if configured."""
        if self.config.get("enable_memory", False) and AgentMemory is not None:
            self.memory = AgentMemory(
                agent_id=self.agent_id, **self.config.get("memory_config", {})
            )
            print("🧠 Auto-configured memory system")
        else:
            self.memory = None
            if self.config.get("enable_memory", False) and AgentMemory is None:
                print("⚠️  Memory system requested but not available")

    def _setup_evaluation(self):
        """Auto-setup evaluation framework."""
        self.evaluator = None
        self.bdd_results = {}
        self.usage_stats = {}
        print("📊 Auto-configured evaluation framework")

    # =================================================================
    # BDD SPEC EXECUTION - Fully abstracted infrastructure
    # =================================================================

    def run_executable_specs(self, auto_tune: bool = False) -> Dict[str, Any]:
        """Execute BDD specifications as executable specs with auto-tuning."""
        print(f"\n📋 Running executable specifications for {self.get_agent_name()}...")

        specs = self.get_bdd_scenarios()  # Keep method name for compatibility
        results = {"specifications": [], "summary": {}}

        for spec in specs:
            spec_result = self._execute_specification(spec)
            results["specifications"].append(spec_result)

        # Calculate summary
        total = len(results["specifications"])
        passed = sum(1 for s in results["specifications"] if s["status"] == "PASS")

        results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": passed / total if total > 0 else 0,
        }

        # Auto-tune if requested and success rate is low
        if auto_tune and results["summary"]["success_rate"] < 0.7:
            self._auto_tune_from_failures(results)

        return results

    # Legacy alias for backward compatibility with test runner
    def run_bdd_test_suite(self, auto_tune: bool = False) -> Dict[str, Any]:
        """Legacy method - use run_executable_specs instead."""
        return self.run_executable_specs(auto_tune)

    # Additional compatibility methods
    def _run_bdd_scenarios(self) -> Dict[str, Any]:
        """Legacy method for test runner compatibility."""
        return self.run_executable_specs()

    def _load_test_data(self) -> List[dspy.Example]:
        """Legacy method for test runner compatibility."""
        scenarios = self.get_bdd_scenarios()
        examples = []
        for scenario in scenarios:
            try:
                example_data = {
                    "input": scenario["input"],
                    "expected": scenario["expected"],
                }
                example = dspy.Example(**example_data)
                examples.append(example)
            except Exception:
                continue
        return examples

    def _execute_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single BDD specification."""
        with self.tracer.trace_operation("spec_execution", "evaluation"):
            try:
                # Run the agent with the specification input
                prediction = self.forward(**spec["input"])

                # Evaluate against expected output using custom or default metrics
                score = self._evaluate_prediction(prediction, spec["expected"])

                return {
                    "name": spec["name"],
                    "status": "PASS" if score >= 0.7 else "FAIL",
                    "score": score,
                    "prediction": str(prediction),
                    "expected": spec["expected"],
                }
            except Exception as e:
                return {"name": spec["name"], "status": "ERROR", "error": str(e)}

    def _evaluate_prediction(
        self, prediction: dspy.Prediction, expected: Dict[str, Any]
    ) -> float:
        """Evaluate prediction against expected output."""
        # Use custom metric if provided, otherwise semantic F1
        custom_metric = self.get_custom_evaluation_metric()
        if custom_metric:
            return custom_metric(prediction, expected)

        # Default semantic evaluation
        try:
            metric = SemanticF1()
            with dspy.context(lm=self.lm):
                temp_example = dspy.Example(response=expected.get("response", ""))
                temp_pred = dspy.Prediction(response=str(prediction))
                return metric(temp_example, temp_pred)
        except:
            # Fallback to simple similarity
            return self._simple_similarity(str(prediction), str(expected))

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Simple word overlap similarity as fallback."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    def _auto_tune_from_failures(self, results: Dict[str, Any]):
        """Auto-tune based on failure patterns."""
        failed_scenarios = [s for s in results["scenarios"] if s["status"] == "FAIL"]

        print(f"🔧 Auto-tuning: Found {len(failed_scenarios)} failures")

        # Simple auto-tuning: adjust temperature based on failure patterns
        if len(failed_scenarios) > len(results["scenarios"]) * 0.5:
            self.lm.temperature = min(0.8, self.lm.temperature + 0.1)
            print(f"📈 Increased temperature to {self.lm.temperature}")

    def _load_default_bdd_scenarios(self) -> List[Dict[str, Any]]:
        """Load default BDD scenarios for the agent."""
        # Try to load from agent-specific file
        agent_name = self.get_agent_name()
        bdd_file = Path(f"bdd_scenarios/{agent_name}_scenarios.yaml")

        if bdd_file.exists():
            import yaml

            with open(bdd_file) as f:
                return yaml.safe_load(f).get("scenarios", [])

        # Fallback to basic scenarios
        return [
            {
                "name": "Basic functionality test",
                "input": {"query": "Hello, can you help me?"},
                "expected": {"response": "Hello! Yes, I can help you."},
            }
        ]

    # =================================================================
    # USAGE TRACKING - Auto-handled
    # =================================================================

    @contextmanager
    def track_usage(self):
        """Auto-track usage statistics."""
        try:
            with dspy.track_usage() as tracker:
                yield
            self.usage_stats = tracker.get_total_tokens() or {}
        except:
            yield  # Graceful fallback

    # =================================================================
    # PUBLIC API - Simplified for developers
    # =================================================================

    def run(self, query: str = None, **kwargs) -> Dict[str, Any]:
        """Synchronous run method for compatibility."""
        # Handle the common case where query is passed
        if query is not None:
            # Simple approach: use the first field in the signature or 'query' as fallback
            signature = self.get_signature()

            # Try to get field names from the signature class
            if hasattr(signature, "__annotations__"):
                input_fields = list(signature.__annotations__.keys())
                # Filter out output fields (this is a simple heuristic)
                if input_fields:
                    first_input_field = input_fields[0]  # Use first field
                    kwargs[first_input_field] = query
                else:
                    kwargs["query"] = query  # Fallback
            else:
                kwargs["query"] = query  # Fallback

        with self.tracer.trace_operation("agent_execution", "pipeline"):
            with self.track_usage():
                prediction = self.forward(**kwargs)

                return {
                    "prediction": prediction,
                    "agent_id": self.agent_id,
                    "usage": self.usage_stats,
                }

    async def __call__(self, query: str = None, **kwargs) -> Dict[str, Any]:
        """Main execution interface with auto-tracing."""
        # Handle the common case where query is passed as positional arg
        if query is not None:
            # Simple approach: use the first field in the signature or 'query' as fallback
            signature = self.get_signature()

            # Try to get field names from the signature class
            if hasattr(signature, "__annotations__"):
                input_fields = list(signature.__annotations__.keys())
                # Filter out output fields (this is a simple heuristic)
                if input_fields:
                    first_input_field = input_fields[0]  # Use first field
                    kwargs[first_input_field] = query
                else:
                    kwargs["query"] = query  # Fallback
            else:
                kwargs["query"] = query  # Fallback

        with self.tracer.trace_operation("agent_execution", "pipeline"):
            with self.track_usage():
                prediction = self.forward(**kwargs)

                return {
                    "prediction": prediction,
                    "agent_id": self.agent_id,
                    "usage": self.usage_stats,
                }

    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Auto-train with framework optimizations."""
        with self.tracer.trace_operation("training", "pipeline"):
            # Convert to DSPy examples
            examples = [dspy.Example(**item) for item in training_data]

            # Use tier-appropriate optimizer
            if self.tier_level == "oracles":
                from dspy.teleprompt import LabeledFewShot

                optimizer = LabeledFewShot()
            else:
                from dspy.teleprompt import BootstrapFewShot

                optimizer = BootstrapFewShot()

            # Use self as the module to train (since we inherit from ABC which is compatible)
            # Create a wrapper that DSPy can optimize
            optimized = optimizer.compile(self, trainset=examples)

            # Store the optimized state
            if hasattr(optimized, "predictor"):
                self.predictor = optimized.predictor
            if hasattr(optimized, "react_agent"):
                self.react_agent = optimized.react_agent

            self.is_trained = True
            return {"status": "trained", "examples": len(examples)}

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage and performance summary."""
        return {
            "usage_stats": self.usage_stats,
            "performance_stats": self.tracer.performance_stats,
            "is_trained": self.is_trained,
            "tier_level": self.tier_level,
        }
