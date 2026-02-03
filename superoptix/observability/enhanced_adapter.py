"""Enhanced DSPy Adapter with comprehensive observability and debugging features."""

import os
import time
from typing import Any, Dict, Optional

import dspy

from ..memory import AgentMemory
from .callbacks import SuperOptixCallback
from .debugger import InteractiveDebugger
from .tracer import SuperOptixTracer


class ObservabilityEnhancedDSPyAdapter:
    """DSPy adapter with comprehensive observability and debugging features."""

    def __init__(self, config: Dict[str, Any], agent_id: Optional[str] = None):
        self.config = config
        self.dspy = dspy
        self.agent_id = (
            agent_id or f"agent_{config.get('persona', {}).get('name', 'default')}"
        )

        # Initialize observability components
        self.tracer = SuperOptixTracer(self.agent_id, enable_external_tracing=True)

        # Initialize memory system with observability
        memory_config = config.get("memory", {})
        if memory_config.get("enabled", True):
            self.memory = AgentMemory(
                agent_id=self.agent_id,
                enable_embeddings=memory_config.get("enable_embeddings", True),
            )
        else:
            self.memory = None

        # Setup DSPy callback for detailed tracing
        self.callback = SuperOptixCallback(self.tracer, self.memory)

        # Initialize interactive debugger
        self.debugger = InteractiveDebugger(self.tracer, self.memory)

        # Observability configuration
        obs_config = config.get("observability", {})
        self.debug_mode = obs_config.get("debug_mode", False)
        self.trace_memory_operations = obs_config.get("trace_memory", True)
        self.enable_breakpoints = obs_config.get("enable_breakpoints", False)
        self.step_mode = obs_config.get("step_mode", False)

        # Performance monitoring
        self.performance_metrics = {
            "total_executions": 0,
            "total_errors": 0,
            "average_response_time": 0,
            "memory_usage_trend": [],
        }

        # Setup LM and configure observability
        self._setup_lm()
        self._configure_observability()

    def _setup_lm(self):
        """Set up DSPy language model with observability."""
        with self.tracer.trace_operation("lm_setup", "dspy_adapter"):
            provider = self.config.get("llm", {}).get("provider", "ollama").lower()

            if provider == "ollama":
                lm = self.dspy.LM(
                    f"ollama_chat/{self.config['llm'].get('model', 'llama2:13b')}",
                    api_base=self.config["llm"].get(
                        "api_base", "http://localhost:11434"
                    ),
                    api_key="",
                )
            elif provider == "openai":
                if "OPENAI_API_KEY" not in os.environ:
                    raise ValueError(
                        "OpenAI API key not found in environment variables"
                    )
                lm = self.dspy.OpenAI(
                    model=self.config["llm"]["model"],
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=self.config["llm"].get("temperature", 0.7),
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            # Store LM for context usage instead of global configuration
            self.lm = lm
            # Note: callbacks will be used with dspy.context() when needed

    def _configure_observability(self):
        """Configure observability settings and external integrations."""
        obs_config = self.config.get("observability", {})

        # Enable external tracing if configured
        if obs_config.get("enable_mlflow", False):
            try:
                import mlflow

                mlflow.dspy.autolog()
                print("✅ MLflow auto-logging enabled")
            except ImportError:
                print("⚠️  MLflow not available - install with: pip install mlflow")

        if obs_config.get("enable_langfuse", False):
            try:
                from openinference.instrumentation.dspy import DSPyInstrumentor

                DSPyInstrumentor().instrument()
                print("✅ Langfuse instrumentation enabled")
            except ImportError:
                print("⚠️  Langfuse instrumentation not available")

        # Configure debugger settings
        if self.enable_breakpoints:
            self.debugger.break_on_error = obs_config.get("break_on_error", True)
            self.debugger.break_on_memory_ops = obs_config.get("break_on_memory", False)

        if self.step_mode:
            self.debugger.enable_step_mode()

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with comprehensive observability."""
        with self.tracer.trace_operation("agent_execution", "dspy_adapter"):
            start_time = time.time()

            try:
                query = inputs.get("query", "")
                inputs.get("context", {})

                # Simple execution for now
                result = f"Processed query: {query}"

                # Update performance metrics
                execution_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(execution_time, success=True)

                # Get comprehensive observability data
                observability_data = self._get_observability_data(execution_time)

                return {"result": result, "observability": observability_data}

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(execution_time, success=False)
                raise RuntimeError(f"DSPy pipeline execution failed: {str(e)}") from e

    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update performance tracking metrics."""
        self.performance_metrics["total_executions"] += 1
        if not success:
            self.performance_metrics["total_errors"] += 1

        # Update average response time
        current_avg = self.performance_metrics["average_response_time"]
        total_execs = self.performance_metrics["total_executions"]
        new_avg = ((current_avg * (total_execs - 1)) + execution_time) / total_execs
        self.performance_metrics["average_response_time"] = new_avg

    def _get_observability_data(self, execution_time: float) -> Dict[str, Any]:
        """Get comprehensive observability data."""
        data = {
            "execution_time_ms": execution_time,
            "performance_metrics": self.performance_metrics,
            "trace_stats": self.tracer.get_trace_summary(),
            "callback_stats": self.callback.get_callback_stats(),
        }

        if self.memory:
            data["memory_stats"] = self.memory.get_memory_summary()

        return data

    def get_observability_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive observability dashboard data."""
        return {
            "agent_info": {
                "agent_id": self.agent_id,
                "config": self.config.get("persona", {}),
                "observability_enabled": True,
                "debug_mode": self.debug_mode,
                "memory_enabled": self.memory is not None,
            },
            "performance_metrics": self.performance_metrics,
            "trace_stats": self.tracer.get_trace_summary(),
            "callback_stats": self.callback.get_callback_stats(),
            "recent_traces": [t.to_dict() for t in self.tracer.traces[-10:]],
            "memory_stats": self.memory.get_memory_summary() if self.memory else None,
        }

    def enable_debug_mode(self):
        """Enable interactive debugging mode."""
        self.debug_mode = True
        print("🐛 Debug mode enabled.")

    def disable_debug_mode(self):
        """Disable interactive debugging mode."""
        self.debug_mode = False
        print("✅ Debug mode disabled.")

    def export_traces(self, format: str = "json", filename: str = None) -> str:
        """Export traces in various formats."""
        return self.tracer.export_traces(format, filename)

    def enable_step_mode(self):
        """Enable step-by-step execution."""
        self.debugger.enable_step_mode()

    def disable_step_mode(self):
        """Disable step-by-step execution."""
        self.debugger.disable_step_mode()

    def add_breakpoint(self, component: str, operation: str = None):
        """Add a debugging breakpoint."""
        self.debugger.add_breakpoint(component, operation)

    def remove_breakpoint(self, component: str, operation: str = None):
        """Remove a debugging breakpoint."""
        self.debugger.remove_breakpoint(component, operation)

    def get_error_analysis(self) -> Dict[str, Any]:
        """Get detailed error analysis."""
        error_traces = self.tracer.get_error_traces()

        if not error_traces:
            return {"total_errors": 0, "error_analysis": "No errors found"}

        # Analyze errors by component and type
        error_by_component = {}
        error_by_type = {}

        for trace in error_traces:
            comp = trace.component
            error_by_component[comp] = error_by_component.get(comp, 0) + 1

            trace.data.get("error", "Unknown error")
            error_type = trace.data.get("error_type", "Unknown")
            error_by_type[error_type] = error_by_type.get(error_type, 0) + 1

        return {
            "total_errors": len(error_traces),
            "error_by_component": error_by_component,
            "error_by_type": error_by_type,
            "recent_errors": [
                {
                    "timestamp": trace.timestamp.isoformat(),
                    "component": trace.component,
                    "error": trace.data.get("error", "Unknown"),
                    "error_type": trace.data.get("error_type", "Unknown"),
                }
                for trace in error_traces[-10:]
            ],
        }

    # Legacy compatibility methods
    def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from user feedback and update memory."""
        if not self.memory:
            return False

        try:
            # Extract insights from feedback
            insights = []

            if feedback.get("helpful", False):
                insights.append("User found the response helpful")

            if feedback.get("accuracy") == "high":
                insights.append("Response was accurate")

            if feedback.get("clarity") == "high":
                insights.append("Response was clear and well-explained")

            # Store feedback patterns
            patterns = {
                "feedback_type": feedback.get("type", "general"),
                "satisfaction_level": feedback.get("satisfaction", "unknown"),
                "improvement_areas": feedback.get("improvements", []),
            }

            return self.memory.learn_from_interaction(insights, patterns)

        except Exception as e:
            print(f"Error learning from feedback: {e}")
            return False

    def get_memory_insights(self) -> Dict[str, Any]:
        """Get insights from the agent's memory."""
        if not self.memory:
            return {"error": "Memory system not available"}

        try:
            return self.memory.get_memory_insights()
        except Exception as e:
            return {"error": f"Error getting memory insights: {e}"}

    def clear_session_memory(self):
        """Clear session-specific memory while preserving long-term knowledge."""
        if not self.memory:
            return False

        try:
            self.memory.short_term.clear_conversation()
            self.memory.short_term.clear_working_memory()
            self.memory.context.clear_context("session")
            return True
        except Exception as e:
            print(f"Error clearing session memory: {e}")
            return False

    def save_memory_state(self) -> bool:
        """Save current memory state for persistence."""
        if not self.memory:
            return False
        return self.memory.save_memory_state()

    def cleanup_memory(self) -> Dict[str, int]:
        """Perform memory cleanup and return statistics."""
        if not self.memory:
            return {"error": "Memory system not available"}
        return self.memory.cleanup_memory()
