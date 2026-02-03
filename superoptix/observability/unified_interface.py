"""Unified observability interface for SuperOptiX.

Provides a simple, consistent API for logging to any observability backend.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from superoptix.observability.enhanced_tracer import (
    EnhancedSuperOptixTracer,
)

logger = logging.getLogger(__name__)


class ObservabilityBackend(Enum):
    """Supported observability backends."""

    SUPEROPTIX = "superoptix"  # Local-first default
    MLFLOW = "mlflow"
    LANGFUSE = "langfuse"
    WANDB = "wandb"
    ALL = "all"  # Log to all backends


class UnifiedObservability:
    """Unified interface for all observability backends.

    This class provides a single, simple API for logging to any observability
    backend (MLFlow, LangFuse, W&B, or SuperOptiX local storage).

    Examples:
            >>> # Use SuperOptiX local storage
            >>> obs = UnifiedObservability(agent_id="my_agent")
            >>> obs.log_agent_run("my_agent", "dspy", accuracy=0.85)

            >>> # Use MLFlow
            >>> obs = UnifiedObservability(
            ...     agent_id="my_agent",
            ...     backend=ObservabilityBackend.MLFLOW
            ... )

            >>> # Use all backends
            >>> obs = UnifiedObservability(
            ...     agent_id="my_agent",
            ...     backend=ObservabilityBackend.ALL
            ... )

            >>> # Log GEPA optimization
            >>> obs.log_optimization(
            ...     agent_name="my_agent",
            ...     optimizer="GEPA",
            ...     initial_score=0.65,
            ...     final_score=0.82,
            ...     iterations=20
            ... )

            >>> # Log protocol usage
            >>> obs.log_protocol(
            ...     agent_name="my_agent",
            ...     protocol_type="mcp",
            ...     server="mcp://localhost:8080",
            ...     tools_discovered=5,
            ...     tools_used=["search", "read"]
            ... )
    """

    def __init__(
        self,
        agent_id: str,
        backend: Union[ObservabilityBackend, str] = ObservabilityBackend.SUPEROPTIX,
        enable_external: bool = True,
        auto_load: bool = False,
    ):
        """Initialize unified observability.

        Args:
                agent_id: Unique identifier for the agent
                backend: Backend to use (superoptix, mlflow, langfuse, wandb, all)
                enable_external: Enable external tracing systems
                auto_load: Auto-load existing traces
        """
        self.agent_id = agent_id

        # Convert string to enum
        if isinstance(backend, str):
            try:
                self.backend = ObservabilityBackend(backend.lower())
            except ValueError:
                logger.warning(f"Unknown backend '{backend}', using superoptix")
                self.backend = ObservabilityBackend.SUPEROPTIX
        else:
            self.backend = backend

        # Initialize enhanced tracer
        self.tracer = EnhancedSuperOptixTracer(
            agent_id=agent_id,
            enable_external_tracing=enable_external
            and self.backend != ObservabilityBackend.SUPEROPTIX,
            observability_backend=self.backend.value
            if self.backend != ObservabilityBackend.SUPEROPTIX
            else None,
            auto_load=auto_load,
        )

        logger.info(
            f"Initialized observability for {agent_id} (backend: {self.backend.value})"
        )

    def log_agent_run(
        self,
        agent_name: str,
        framework: str,
        accuracy: Optional[float] = None,
        cost_usd: Optional[float] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[float] = None,
        success_rate: Optional[float] = None,
        **extra_metrics,
    ):
        """Log agent execution run.

        Simple, unified interface for logging agent runs to any backend.

        Args:
                agent_name: Name of the agent
                framework: Framework used (dspy, crewai, langraph, etc.)
                accuracy: Accuracy score (0-1)
                cost_usd: Cost in USD
                tokens_used: Total tokens used
                latency_ms: Latency in milliseconds
                success_rate: Success rate (0-1)
                **extra_metrics: Additional custom metrics
        """
        self.tracer.log_agent_run(
            agent_name=agent_name,
            framework=framework,
            accuracy=accuracy,
            cost_usd=cost_usd,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            success_rate=success_rate,
            **extra_metrics,
        )

    def log_optimization(
        self,
        agent_name: str,
        optimizer: str,
        initial_score: float,
        final_score: float,
        iterations: int,
        population_size: int = 10,
        duration_seconds: Optional[float] = None,
        best_prompt: Optional[str] = None,
        **extra_data,
    ):
        """Log optimization run (GEPA, SIMBA, etc.).

        Args:
                agent_name: Name of the agent
                optimizer: Optimizer name (GEPA, SIMBA, MIPROv2, etc.)
                initial_score: Initial performance score
                final_score: Final performance score
                iterations: Number of optimization iterations
                population_size: Population size (for genetic algorithms)
                duration_seconds: Time taken for optimization
                best_prompt: Best prompt found
                **extra_data: Additional optimizer-specific data
        """
        if optimizer.upper() == "GEPA":
            self.tracer.log_gepa_optimization(
                agent_name=agent_name,
                initial_score=initial_score,
                final_score=final_score,
                iterations=iterations,
                population_size=population_size,
                duration_seconds=duration_seconds,
                best_prompt=best_prompt,
                evolution_history=extra_data.get("evolution_history"),
            )
        else:
            # Generic optimization logging
            self.tracer.add_event(
                event_type=f"{optimizer}_optimization",
                component="optimizer",
                data={
                    "agent_name": agent_name,
                    "optimizer": optimizer,
                    "initial_score": initial_score,
                    "final_score": final_score,
                    "improvement": final_score - initial_score,
                    "iterations": iterations,
                    "duration_seconds": duration_seconds,
                    **extra_data,
                },
                status="success",
            )

    def log_protocol(
        self,
        agent_name: str,
        protocol_type: str,
        server: str,
        tools_discovered: int,
        tools_used: List[str],
        tool_success_rate: float = 1.0,
        avg_latency_ms: float = 0.0,
        total_calls: int = 0,
    ):
        """Log protocol usage (MCP, Agent2Agent).

        Args:
                agent_name: Name of the agent
                protocol_type: Type of protocol (mcp, agent2agent)
                server: URI of the protocol server
                tools_discovered: Number of tools discovered
                tools_used: List of tool names used
                tool_success_rate: Success rate of tool calls (0-1)
                avg_latency_ms: Average latency per tool call
                total_calls: Total number of tool calls
        """
        self.tracer.log_protocol_usage(
            agent_name=agent_name,
            protocol_type=protocol_type,
            server_uri=server,
            tools_discovered=tools_discovered,
            tools_used=tools_used,
            tool_success_rate=tool_success_rate,
            avg_latency_ms=avg_latency_ms,
            total_calls=total_calls,
        )

    def log_framework_comparison(
        self, agent_name: str, frameworks: Dict[str, Dict[str, float]]
    ):
        """Log multi-framework comparison.

        Args:
                agent_name: Name of the agent
                frameworks: Dict mapping framework name to metrics

        Example:
                frameworks = {
                        "dspy": {"accuracy": 0.85, "cost": 0.05},
                        "crewai": {"accuracy": 0.78, "cost": 0.08}
                }
        """
        self.tracer.log_multi_framework_comparison(
            agent_name=agent_name, frameworks=frameworks
        )

    def log_cost(
        self,
        agent_name: str,
        provider: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
    ):
        """Log cost information.

        Args:
                agent_name: Name of the agent
                provider: LLM provider (openai, anthropic, etc.)
                model: Model name (gpt-4, claude-3, etc.)
                tokens_input: Input tokens used
                tokens_output: Output tokens generated
                cost_usd: Total cost in USD
        """
        self.tracer.add_event(
            event_type="cost_tracking",
            component="llm",
            data={
                "agent_name": agent_name,
                "provider": provider,
                "model": model,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "tokens_total": tokens_input + tokens_output,
                "cost_usd": cost_usd,
            },
            status="success",
        )

    def start_trace(self, operation_name: str, component: str, **metadata):
        """Start a trace operation (context manager).

        Args:
                operation_name: Name of the operation
                component: Component name
                **metadata: Additional metadata

        Returns:
                Context manager for tracing
        """
        return self.tracer.trace_operation(operation_name, component, **metadata)

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all metrics.

        Returns:
                Dictionary with summary statistics
        """
        return self.tracer.get_agent_summary()

    def export(self, filename: Optional[str] = None, format: str = "json") -> str:
        """Export all metrics to file.

        Args:
                filename: Optional filename to save to
                format: Export format (json, jsonl)

        Returns:
                Exported data as string
        """
        if format == "json":
            return self.tracer.export_agent_metrics(filename)
        elif format == "jsonl":
            return self.tracer.export_traces(format="jsonl", filename=filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def cleanup(self):
        """Clean up external tracers (e.g., finish W&B run)."""
        if "wandb" in self.tracer.external_tracers:
            try:
                wandb = self.tracer.external_tracers["wandb"]
                wandb.finish()
                logger.info("W&B run finished")
            except Exception as e:
                logger.warning(f"Error finishing W&B run: {e}")


# Convenience function for quick setup
def get_observability(
    agent_id: str, backend: str = "superoptix", enable_external: bool = True
) -> UnifiedObservability:
    """Get observability instance with specified backend.

    Args:
            agent_id: Unique identifier for the agent
            backend: Backend to use (superoptix, mlflow, langfuse, wandb, all)
            enable_external: Enable external tracing

    Returns:
            UnifiedObservability instance

    Examples:
            >>> obs = get_observability("my_agent", backend="mlflow")
            >>> obs.log_agent_run("my_agent", "dspy", accuracy=0.85)
    """
    return UnifiedObservability(
        agent_id=agent_id, backend=backend, enable_external=enable_external
    )
