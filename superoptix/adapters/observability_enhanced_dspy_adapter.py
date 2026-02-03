"""Enhanced DSPy Adapter with comprehensive observability and monitoring."""

import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import dspy
from dspy.utils.callback import BaseCallback

from ..memory import AgentMemory


@dataclass
class TraceEvent:
    """Represents a single trace event."""

    event_id: str
    timestamp: datetime
    event_type: str
    component: str
    data: Dict[str, Any]
    parent_id: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "success"  # success, error, warning
    metadata: Optional[Dict[str, Any]] = None


class SuperOptixTracer:
    """Comprehensive tracer for SuperOptiX agent execution."""

    def __init__(self, agent_id: str, enable_external_tracing: bool = True):
        self.agent_id = agent_id
        self.enable_external_tracing = enable_external_tracing
        self.traces: List[TraceEvent] = []
        self.current_trace_stack: List[str] = []
        self._lock = threading.RLock()

        # External tracing integrations
        self.external_tracers = {}
        self._setup_external_tracers()

    def _setup_external_tracers(self):
        """Setup external tracing integrations (MLflow, Langfuse, etc.)."""
        if not self.enable_external_tracing:
            return

        # MLflow integration
        try:
            import mlflow

            mlflow.set_experiment(f"SuperOptiX-{self.agent_id}")
            self.external_tracers["mlflow"] = mlflow
        except ImportError:
            pass

        # Langfuse integration
        try:
            from langfuse import Langfuse

            langfuse = Langfuse()
            if langfuse.auth_check():
                self.external_tracers["langfuse"] = langfuse
        except ImportError:
            pass

    @contextmanager
    def trace_operation(self, operation_name: str, component: str, **metadata):
        """Context manager for tracing operations with timing."""
        event_id = str(uuid.uuid4())
        start_time = time.time()
        parent_id = self.current_trace_stack[-1] if self.current_trace_stack else None

        with self._lock:
            self.current_trace_stack.append(event_id)

        try:
            # Create start event
            start_event = TraceEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                event_type=f"{operation_name}_start",
                component=component,
                data={"operation": operation_name, **metadata},
                parent_id=parent_id,
                metadata=metadata,
            )
            self._add_trace_event(start_event)

            yield event_id

            # Create success end event
            duration = (time.time() - start_time) * 1000
            end_event = TraceEvent(
                event_id=f"{event_id}_end",
                timestamp=datetime.now(),
                event_type=f"{operation_name}_end",
                component=component,
                data={"operation": operation_name, "duration_ms": duration, **metadata},
                parent_id=event_id,
                duration_ms=duration,
                status="success",
            )
            self._add_trace_event(end_event)

        except Exception as e:
            # Create error end event
            duration = (time.time() - start_time) * 1000
            error_event = TraceEvent(
                event_id=f"{event_id}_error",
                timestamp=datetime.now(),
                event_type=f"{operation_name}_error",
                component=component,
                data={
                    "operation": operation_name,
                    "error": str(e),
                    "duration_ms": duration,
                    **metadata,
                },
                parent_id=event_id,
                duration_ms=duration,
                status="error",
            )
            self._add_trace_event(error_event)
            raise
        finally:
            with self._lock:
                if (
                    self.current_trace_stack
                    and self.current_trace_stack[-1] == event_id
                ):
                    self.current_trace_stack.pop()

    def _add_trace_event(self, event: TraceEvent):
        """Add trace event to internal storage and external tracers."""
        with self._lock:
            self.traces.append(event)

        # Send to external tracers
        self._send_to_external_tracers(event)

    def _send_to_external_tracers(self, event: TraceEvent):
        """Send trace event to external tracing systems."""
        # MLflow integration
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                with mlflow.start_run(nested=True):
                    mlflow.log_params(
                        {
                            "event_type": event.event_type,
                            "component": event.component,
                            "agent_id": self.agent_id,
                        }
                    )
                    if event.duration_ms:
                        mlflow.log_metric("duration_ms", event.duration_ms)
                    mlflow.log_dict(event.data, "event_data.json")
            except Exception:
                pass  # Don't fail on tracing errors

        # Langfuse integration
        if "langfuse" in self.external_tracers:
            try:
                langfuse = self.external_tracers["langfuse"]
                langfuse.trace(
                    name=event.event_type,
                    input=event.data,
                    metadata={
                        "component": event.component,
                        "agent_id": self.agent_id,
                        "event_id": event.event_id,
                        "parent_id": event.parent_id,
                        "status": event.status,
                    },
                )
            except Exception:
                pass  # Don't fail on tracing errors

    def get_trace_summary(self) -> Dict[str, Any]:
        """Get comprehensive trace summary."""
        with self._lock:
            total_events = len(self.traces)
            error_events = len([t for t in self.traces if t.status == "error"])
            components = set(t.component for t in self.traces)

            # Calculate performance metrics
            durations = [
                t.duration_ms for t in self.traces if t.duration_ms is not None
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0

            return {
                "agent_id": self.agent_id,
                "total_events": total_events,
                "error_events": error_events,
                "error_rate": error_events / total_events if total_events > 0 else 0,
                "components_traced": list(components),
                "average_duration_ms": avg_duration,
                "trace_count": len(self.traces),
                "external_tracers": list(self.external_tracers.keys()),
            }


class SuperOptixCallback(BaseCallback):
    """Custom DSPy callback for SuperOptiX observability."""

    def __init__(self, tracer: SuperOptixTracer, memory: AgentMemory):
        self.tracer = tracer
        self.memory = memory
        self.module_stack = []

    def on_module_start(self, call_id, inputs):
        """Called when a DSPy module starts execution."""
        module_info = {
            "call_id": call_id,
            "inputs": str(inputs)[:200],  # Truncate for logging
            "input_count": len(inputs) if isinstance(inputs, dict) else 1,
        }

        # Add to memory tracking
        self.memory.add_interaction_event(
            event_type="dspy_module_start",
            description=f"DSPy module started: {call_id}",
            data=module_info,
        )

        self.module_stack.append(call_id)

    def on_module_end(self, call_id, outputs, exception):
        """Called when a DSPy module completes execution."""
        if exception:
            status = "error"
            result_info = {"error": str(exception)}
        else:
            status = "success"
            result_info = {
                "outputs": str(outputs)[:200],  # Truncate for logging
                "output_count": len(outputs) if isinstance(outputs, dict) else 1,
            }

        # Add to memory tracking
        self.memory.add_interaction_event(
            event_type="dspy_module_end",
            description=f"DSPy module completed: {call_id}",
            data={**result_info, "status": status},
        )

        if self.module_stack and self.module_stack[-1] == call_id:
            self.module_stack.pop()

    def on_lm_start(self, call_id, inputs):
        """Called when LM call starts."""
        lm_info = {
            "call_id": call_id,
            "prompt_length": len(str(inputs)),
            "timestamp": datetime.now().isoformat(),
        }

        self.memory.add_interaction_event(
            event_type="llm_call_start",
            description="Language model call initiated",
            data=lm_info,
        )

    def on_lm_end(self, call_id, outputs, exception):
        """Called when LM call completes."""
        if exception:
            lm_result = {"error": str(exception), "status": "failed"}
        else:
            lm_result = {"response_length": len(str(outputs)), "status": "success"}

        self.memory.add_interaction_event(
            event_type="llm_call_end",
            description="Language model call completed",
            data=lm_result,
        )

    def on_tool_start(self, call_id, inputs):
        """Called when tool execution starts."""
        tool_info = {"call_id": call_id, "tool_inputs": str(inputs)[:100]}

        self.memory.add_interaction_event(
            event_type="tool_execution_start",
            description="Tool execution started",
            data=tool_info,
        )

    def on_tool_end(self, call_id, outputs, exception):
        """Called when tool execution completes."""
        if exception:
            tool_result = {"error": str(exception), "status": "failed"}
        else:
            tool_result = {"tool_outputs": str(outputs)[:100], "status": "success"}

        self.memory.add_interaction_event(
            event_type="tool_execution_end",
            description="Tool execution completed",
            data=tool_result,
        )


class ObservabilityEnhancedDSPyAdapter:
    """DSPy adapter with comprehensive observability and debugging features."""

    def __init__(self, config: Dict[str, Any], agent_id: Optional[str] = None):
        self.config = config
        self.dspy = dspy
        self.agent_id = (
            agent_id or f"agent_{config.get('persona', {}).get('name', 'default')}"
        )

        # Initialize observability components
        self.tracer = SuperOptixTracer(self.agent_id)

        # Initialize memory system with observability
        self.memory = AgentMemory(
            agent_id=self.agent_id,
            enable_embeddings=config.get("memory", {}).get("enable_embeddings", True),
        )

        # Setup DSPy callback for detailed tracing
        self.callback = SuperOptixCallback(self.tracer, self.memory)

        # Observability configuration
        self.debug_mode = config.get("observability", {}).get("debug_mode", False)
        self.trace_memory_operations = config.get("observability", {}).get(
            "trace_memory", True
        )
        self.enable_breakpoints = config.get("observability", {}).get(
            "enable_breakpoints", False
        )

        # Performance monitoring
        self.performance_metrics = {
            "total_executions": 0,
            "total_errors": 0,
            "average_response_time": 0,
            "memory_usage_trend": [],
        }

        self._setup_lm()
        self._configure_observability()

    def _setup_lm(self):
        """Set up DSPy language model with observability."""
        with self.tracer.trace_operation("lm_setup", "dspy_adapter"):
            provider = self.config["llm"].get("provider", "ollama").lower()

            if provider == "ollama":
                lm = self.dspy.LM(
                    f"ollama_chat/{self.config['llm'].get('model', 'llama3.2:1b')}",
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
        """Configure observability settings."""
        obs_config = self.config.get("observability", {})

        # Enable external tracing if configured
        if obs_config.get("enable_mlflow", False):
            try:
                import mlflow

                mlflow.dspy.autolog()
            except ImportError:
                print("Warning: MLflow not available for tracing")

        if obs_config.get("enable_langfuse", False):
            try:
                from openinference.instrumentation.dspy import DSPyInstrumentor

                DSPyInstrumentor().instrument()
            except ImportError:
                print("Warning: Langfuse instrumentation not available")

    def setup_agent(self) -> Any:
        """Set up DSPy agent with comprehensive observability."""
        with self.tracer.trace_operation("agent_setup", "dspy_adapter"):
            # Define signature for input/output
            class ObservableAgentSignature(self.dspy.Signature):
                """Signature with observability metadata."""

                context = self.dspy.InputField(desc="Relevant context and memory")
                query = self.dspy.InputField(desc="The user's input query")
                result = self.dspy.OutputField(desc="The agent's response")

            # Create agent module with full observability
            class ObservableAgentModule(self.dspy.Module):
                def __init__(
                    self,
                    config,
                    dspy_instance,
                    memory_system,
                    tracer,
                    debug_mode,
                    lm,
                    callback,
                ):
                    super().__init__()
                    self.config = config
                    self.dspy = dspy_instance
                    self.memory = memory_system
                    self.tracer = tracer
                    self.debug_mode = debug_mode
                    self.lm = lm
                    self.callback = callback

                def forward(
                    self, query: str, user_context: Optional[Dict] = None
                ) -> dict:
                    with self.tracer.trace_operation(
                        "agent_forward", "agent_module", query=query[:50]
                    ):
                        # Debug breakpoint if enabled
                        if self.debug_mode:
                            self._debug_breakpoint(
                                "agent_start", {"query": query, "context": user_context}
                            )

                        # Start interaction tracking
                        episode_id = self.memory.start_interaction(user_context or {})

                        try:
                            # Memory retrieval with tracing
                            with self.tracer.trace_operation(
                                "memory_retrieval", "memory_system"
                            ):
                                conversation_context = (
                                    self.memory.get_conversation_context()
                                )
                                relevant_memories = self.memory.recall(query, limit=3)

                            # Context building with tracing
                            with self.tracer.trace_operation(
                                "context_building", "agent_module"
                            ):
                                context_string = self._build_context(
                                    query, relevant_memories, conversation_context
                                )

                            # Debug breakpoint before LLM call
                            if self.debug_mode:
                                self._debug_breakpoint(
                                    "before_llm",
                                    {
                                        "context_length": len(context_string),
                                        "memory_count": len(relevant_memories),
                                    },
                                )

                            # LLM prediction with tracing
                            with self.tracer.trace_operation(
                                "llm_prediction", "dspy_module"
                            ):
                                with self.dspy.context(
                                    lm=self.lm, callbacks=[self.callback]
                                ):
                                    predictor = self.dspy.Predict(
                                        ObservableAgentSignature
                                    )
                                    response = predictor(
                                        context=context_string, query=query
                                    )

                            result = response.result

                            # Memory storage with tracing
                            with self.tracer.trace_operation(
                                "memory_storage", "memory_system"
                            ):
                                self._store_interaction(query, result)

                            # Debug breakpoint after completion
                            if self.debug_mode:
                                self._debug_breakpoint(
                                    "agent_complete",
                                    {
                                        "result_length": len(result),
                                        "episode_id": episode_id,
                                    },
                                )

                            # End interaction successfully
                            self.memory.end_interaction(
                                {
                                    "success": True,
                                    "response_generated": True,
                                    "query_type": "general",
                                }
                            )

                            return {"result": result, "episode_id": episode_id}

                        except Exception as e:
                            # Error handling with tracing
                            self.memory.end_interaction(
                                {"success": False, "error": str(e), "query": query}
                            )

                            if self.debug_mode:
                                self._debug_breakpoint("agent_error", {"error": str(e)})

                            raise e

                def _build_context(
                    self, query: str, memories: List, conversation: Dict
                ) -> str:
                    """Build context string with observability."""
                    context_parts = []

                    # Add persona information
                    persona = self.config.get("persona", {})
                    context_parts.append(f"You are {persona.get('name', 'Assistant')}.")

                    # Add relevant memories
                    if memories:
                        context_parts.append("\nRelevant past knowledge:")
                        for memory in memories:
                            context_parts.append(f"- {memory['content'][:100]}...")

                    # Add recent conversation
                    recent_conversation = conversation.get("recent_conversation", [])
                    if recent_conversation:
                        context_parts.append("\nRecent conversation:")
                        for msg in recent_conversation[-3:]:
                            context_parts.append(
                                f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}..."
                            )

                    return "\n".join(context_parts)

                def _store_interaction(self, query: str, result: str):
                    """Store interaction with observability."""
                    # Store in memory
                    self.memory.remember(
                        content=f"Q: {query}\nA: {result}",
                        memory_type="short",
                        importance=0.7,
                        ttl=3600,
                    )

                    # Add to conversation history
                    self.memory.short_term.add_to_conversation("user", query)
                    self.memory.short_term.add_to_conversation("assistant", result)

                    # Log interaction events
                    self.memory.add_interaction_event(
                        event_type="agent_response",
                        description="Agent provided response",
                        data={
                            "response_length": len(result),
                            "query_length": len(query),
                        },
                    )

                def _debug_breakpoint(self, breakpoint_name: str, data: Dict[str, Any]):
                    """Interactive debugging breakpoint."""
                    if not self.debug_mode:
                        return

                    print(f"\n🔍 DEBUG BREAKPOINT: {breakpoint_name}")
                    print(f"📊 Data: {data}")
                    print(
                        "📝 Available commands: continue (c), inspect (i), memory (m), trace (t), quit (q)"
                    )

                    while True:
                        cmd = input("🐛 Debug> ").strip().lower()

                        if cmd in ["c", "continue"]:
                            break
                        elif cmd in ["i", "inspect"]:
                            self._inspect_state()
                        elif cmd in ["m", "memory"]:
                            self._inspect_memory()
                        elif cmd in ["t", "trace"]:
                            self._inspect_trace()
                        elif cmd in ["q", "quit"]:
                            raise KeyboardInterrupt("Debug session terminated")
                        else:
                            print("Unknown command. Use: c, i, m, t, q")

                def _inspect_state(self):
                    """Inspect current agent state."""
                    print("\n📋 Current Agent State:")
                    print(f"  Agent ID: {self.memory.agent_id}")
                    print(
                        f"  Config: {self.config.get('persona', {}).get('name', 'Unknown')}"
                    )
                    print(f"  Memory enabled: {self.memory is not None}")

                def _inspect_memory(self):
                    """Inspect memory state."""
                    summary = self.memory.get_memory_summary()
                    print("\n🧠 Memory State:")
                    print(f"  Interactions: {summary['interaction_count']}")
                    print(f"  Short-term items: {summary['short_term_memory']['size']}")
                    print(
                        f"  Long-term items: {summary['long_term_memory']['total_items']}"
                    )
                    print(
                        f"  Active episodes: {summary['episodic_memory']['active_episodes']}"
                    )

                def _inspect_trace(self):
                    """Inspect trace information."""
                    trace_summary = self.tracer.get_trace_summary()
                    print("\n🔍 Trace Information:")
                    print(f"  Total events: {trace_summary['total_events']}")
                    print(f"  Error rate: {trace_summary['error_rate']:.2%}")
                    print(
                        f"  Average duration: {trace_summary['average_duration_ms']:.2f}ms"
                    )
                    print(
                        f"  Components: {', '.join(trace_summary['components_traced'])}"
                    )

            return ObservableAgentModule(
                self.config,
                self.dspy,
                self.memory,
                self.tracer,
                self.debug_mode,
                self.lm,
                self.callback,
            )

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with comprehensive observability."""
        with self.tracer.trace_operation("agent_execution", "dspy_adapter"):
            start_time = time.time()

            try:
                agent = self.setup_agent()
                query = inputs.get("query", "")
                user_context = inputs.get("context", {})

                result = agent(query, user_context)

                # Update performance metrics
                execution_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(execution_time, success=True)

                # Get comprehensive observability data
                memory_summary = self.memory.get_memory_summary()
                trace_summary = self.tracer.get_trace_summary()

                return {
                    "result": result["result"],
                    "episode_id": result.get("episode_id"),
                    "observability": {
                        "execution_time_ms": execution_time,
                        "memory_stats": memory_summary,
                        "trace_stats": trace_summary,
                        "performance_metrics": self.performance_metrics,
                    },
                }

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

        # Track memory usage trend
        memory_summary = self.memory.get_memory_summary()
        memory_usage = {
            "timestamp": datetime.now().isoformat(),
            "short_term_size": memory_summary["short_term_memory"]["size"],
            "long_term_size": memory_summary["long_term_memory"]["total_items"],
            "active_episodes": memory_summary["episodic_memory"]["active_episodes"],
        }

        # Keep only last 100 measurements
        self.performance_metrics["memory_usage_trend"].append(memory_usage)
        if len(self.performance_metrics["memory_usage_trend"]) > 100:
            self.performance_metrics["memory_usage_trend"].pop(0)

    def get_observability_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive observability dashboard data."""
        return {
            "agent_info": {
                "agent_id": self.agent_id,
                "config": self.config.get("persona", {}),
                "observability_enabled": True,
            },
            "performance_metrics": self.performance_metrics,
            "memory_stats": self.memory.get_memory_summary(),
            "trace_stats": self.tracer.get_trace_summary(),
            "recent_traces": self.tracer.traces[-10:],  # Last 10 traces
            "debug_mode": self.debug_mode,
        }

    def enable_debug_mode(self):
        """Enable interactive debugging mode."""
        self.debug_mode = True
        print("🐛 Debug mode enabled. Breakpoints will be triggered during execution.")

    def disable_debug_mode(self):
        """Disable interactive debugging mode."""
        self.debug_mode = False
        print("✅ Debug mode disabled.")

    def export_traces(self, format: str = "json") -> str:
        """Export traces in various formats."""
        if format == "json":
            import json

            return json.dumps(
                [
                    {
                        "event_id": t.event_id,
                        "timestamp": t.timestamp.isoformat(),
                        "event_type": t.event_type,
                        "component": t.component,
                        "data": t.data,
                        "duration_ms": t.duration_ms,
                        "status": t.status,
                    }
                    for t in self.tracer.traces
                ],
                indent=2,
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")
