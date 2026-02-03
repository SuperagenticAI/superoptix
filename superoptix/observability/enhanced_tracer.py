"""Enhanced tracing system with agent-specific metrics for SuperOptiX.

This module extends the base tracer with:
- GEPA optimization tracking
- Protocol usage metrics (MCP, Agent2Agent)
- Multi-framework comparison
- Cost and token tracking
- Weights & Biases integration
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from superoptix.observability.tracer import SuperOptixTracer

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Agent-specific performance metrics."""

    agent_name: str
    framework: str  # dspy, crewai, langraph, etc.
    accuracy: Optional[float] = None
    cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    success_rate: Optional[float] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass
class GEPAOptimizationMetrics:
    """GEPA-specific optimization metrics."""

    agent_name: str
    initial_score: float
    final_score: float
    improvement: float
    iterations: int
    population_size: int
    generations: int
    optimizer_name: str = "GEPA"
    duration_seconds: Optional[float] = None
    best_prompt: Optional[str] = None
    evolution_history: Optional[List[Dict]] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass
class ProtocolUsageMetrics:
    """Protocol usage metrics (MCP, Agent2Agent, etc.)."""

    agent_name: str
    protocol_type: str  # mcp, agent2agent
    server_uri: str
    tools_discovered: int
    tools_used: List[str]
    tool_success_rate: float
    avg_latency_ms: float
    total_calls: int
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result


class EnhancedSuperOptixTracer(SuperOptixTracer):
    """Enhanced tracer with agent-specific metrics and W&B support."""

    def __init__(
        self,
        agent_id: str,
        enable_external_tracing: bool = False,
        observability_backend: Optional[str] = None,  # mlflow, langfuse, wandb, all
        auto_load: bool = True,
    ):
        """Initialize enhanced tracer.

        Args:
            agent_id: Unique identifier for the agent
            enable_external_tracing: Enable external tracing systems
            observability_backend: Specific backend to use (mlflow, langfuse, wandb, all)
            auto_load: Auto-load existing traces
        """
        # Set backend BEFORE calling super().__init__
        self.observability_backend = observability_backend or "all"

        # Agent-specific metrics storage
        self.agent_metrics: List[AgentMetrics] = []
        self.gepa_metrics: List[GEPAOptimizationMetrics] = []
        self.protocol_metrics: List[ProtocolUsageMetrics] = []

        # Now call parent __init__ which will call _setup_external_tracers
        super().__init__(agent_id, enable_external_tracing, auto_load)

        # Setup W&B if requested
        if enable_external_tracing and observability_backend in ["wandb", "all"]:
            self._setup_wandb()

    def _setup_external_tracers(self):
        """Setup external tracing integrations with backend filtering."""
        if not self.enable_external_tracing:
            return

        backend = self.observability_backend

        # MLflow integration
        if backend in ["mlflow", "all"]:
            try:
                import mlflow

                mlflow.set_experiment(f"SuperOptiX-{self.agent_id}")
                self.external_tracers["mlflow"] = mlflow
                logger.info(f"✅ MLflow tracing enabled for agent {self.agent_id}")
            except ImportError:
                logger.warning(
                    "⚠️  MLflow not available - install with: pip install mlflow"
                )

        # Langfuse integration
        if backend in ["langfuse", "all"]:
            try:
                from langfuse import Langfuse

                langfuse = Langfuse()
                if langfuse.auth_check():
                    self.external_tracers["langfuse"] = langfuse
                    logger.info(
                        f"✅ Langfuse tracing enabled for agent {self.agent_id}"
                    )
            except ImportError:
                logger.warning(
                    "⚠️  Langfuse not available - install with: pip install langfuse"
                )
            except Exception:
                logger.warning("⚠️  Langfuse authentication failed - check credentials")

    def _setup_wandb(self):
        """Setup Weights & Biases integration."""
        try:
            import wandb

            # Initialize W&B run
            wandb.init(
                project="superoptix",
                name=self.agent_id,
                tags=["superoptix", "agent", self.agent_id],
                config={
                    "agent_id": self.agent_id,
                    "framework": "superoptix",
                },
            )

            self.external_tracers["wandb"] = wandb
            logger.info(
                f"✅ Weights & Biases tracing enabled for agent {self.agent_id}"
            )

        except ImportError:
            logger.warning(
                "⚠️  Weights & Biases not available - install with: pip install wandb"
            )
        except Exception as e:
            logger.warning(f"⚠️  W&B initialization failed: {e}")

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
        """Log agent execution metrics.

        Args:
            agent_name: Name of the agent
            framework: Framework used (dspy, crewai, etc.)
            accuracy: Accuracy score (0-1)
            cost_usd: Cost in USD
            tokens_used: Total tokens used
            latency_ms: Latency in milliseconds
            success_rate: Success rate (0-1)
            **extra_metrics: Additional custom metrics
        """
        metrics = AgentMetrics(
            agent_name=agent_name,
            framework=framework,
            accuracy=accuracy,
            cost_usd=cost_usd,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            success_rate=success_rate,
            timestamp=datetime.now(),
        )

        self.agent_metrics.append(metrics)

        # Log to external tracers
        self._log_agent_metrics_external(metrics, extra_metrics)

        # Add trace event
        self.add_event(
            event_type="agent_run",
            component="agent_execution",
            data={
                "agent_name": agent_name,
                "framework": framework,
                "accuracy": accuracy,
                "cost_usd": cost_usd,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "success_rate": success_rate,
                **extra_metrics,
            },
            status="success",
        )

        logger.info(f"Logged agent run: {agent_name} ({framework})")

    def log_gepa_optimization(
        self,
        agent_name: str,
        initial_score: float,
        final_score: float,
        iterations: int,
        population_size: int = 10,
        generations: int = None,
        duration_seconds: Optional[float] = None,
        best_prompt: Optional[str] = None,
        evolution_history: Optional[List[Dict]] = None,
    ):
        """Log GEPA optimization metrics.

        Args:
            agent_name: Name of the agent
            initial_score: Initial performance score
            final_score: Final performance score after optimization
            iterations: Number of optimization iterations
            population_size: Size of the population
            generations: Number of generations
            duration_seconds: Time taken for optimization
            best_prompt: Best prompt found
            evolution_history: History of evolution
        """
        improvement = final_score - initial_score
        generations = generations or (iterations // population_size)

        metrics = GEPAOptimizationMetrics(
            agent_name=agent_name,
            initial_score=initial_score,
            final_score=final_score,
            improvement=improvement,
            iterations=iterations,
            population_size=population_size,
            generations=generations,
            duration_seconds=duration_seconds,
            best_prompt=best_prompt,
            evolution_history=evolution_history,
            timestamp=datetime.now(),
        )

        self.gepa_metrics.append(metrics)

        # Log to external tracers
        self._log_gepa_metrics_external(metrics)

        # Add trace event
        self.add_event(
            event_type="gepa_optimization",
            component="optimizer",
            data=metrics.to_dict(),
            status="success",
        )

        logger.info(
            f"GEPA optimization for {agent_name}: "
            f"{initial_score:.3f} → {final_score:.3f} "
            f"(+{improvement:.3f}, {iterations} iterations)"
        )

    def log_protocol_usage(
        self,
        agent_name: str,
        protocol_type: str,
        server_uri: str,
        tools_discovered: int,
        tools_used: List[str],
        tool_success_rate: float = 1.0,
        avg_latency_ms: float = 0.0,
        total_calls: int = 0,
    ):
        """Log protocol usage metrics (MCP, Agent2Agent, etc.).

        Args:
            agent_name: Name of the agent
            protocol_type: Type of protocol (mcp, agent2agent)
            server_uri: URI of the protocol server
            tools_discovered: Number of tools discovered
            tools_used: List of tool names used
            tool_success_rate: Success rate of tool calls (0-1)
            avg_latency_ms: Average latency per tool call
            total_calls: Total number of tool calls
        """
        metrics = ProtocolUsageMetrics(
            agent_name=agent_name,
            protocol_type=protocol_type,
            server_uri=server_uri,
            tools_discovered=tools_discovered,
            tools_used=tools_used,
            tool_success_rate=tool_success_rate,
            avg_latency_ms=avg_latency_ms,
            total_calls=total_calls,
            timestamp=datetime.now(),
        )

        self.protocol_metrics.append(metrics)

        # Log to external tracers
        self._log_protocol_metrics_external(metrics)

        # Add trace event
        self.add_event(
            event_type="protocol_usage",
            component="protocol",
            data=metrics.to_dict(),
            status="success",
        )

        logger.info(
            f"Protocol usage for {agent_name}: "
            f"{protocol_type} @ {server_uri}, "
            f"{len(tools_used)}/{tools_discovered} tools used"
        )

    def log_multi_framework_comparison(
        self, agent_name: str, frameworks: Dict[str, Dict[str, float]]
    ):
        """Log multi-framework comparison metrics.

        Args:
            agent_name: Name of the agent
            frameworks: Dict mapping framework name to metrics dict

        Example:
            frameworks = {
                "dspy": {"accuracy": 0.85, "cost": 0.05, "latency_ms": 1200},
                "crewai": {"accuracy": 0.78, "cost": 0.08, "latency_ms": 1800},
                "langraph": {"accuracy": 0.80, "cost": 0.06, "latency_ms": 1500}
            }
        """
        # Determine best framework by accuracy
        best_framework = max(frameworks.items(), key=lambda x: x[1].get("accuracy", 0))

        comparison_data = {
            "agent_name": agent_name,
            "frameworks": frameworks,
            "best_framework": best_framework[0],
            "best_accuracy": best_framework[1].get("accuracy", 0),
            "timestamp": datetime.now().isoformat(),
        }

        # Log to external tracers
        self._log_multi_framework_external(comparison_data)

        # Add trace event
        self.add_event(
            event_type="multi_framework_comparison",
            component="evaluation",
            data=comparison_data,
            status="success",
        )

        logger.info(
            f"Multi-framework comparison for {agent_name}: "
            f"Best = {best_framework[0]} ({best_framework[1].get('accuracy', 0):.3f})"
        )

    def _log_agent_metrics_external(self, metrics: AgentMetrics, extra_metrics: Dict):
        """Log agent metrics to external tracers."""
        # MLflow
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                with mlflow.start_run(
                    run_name=f"{metrics.agent_name}_run", nested=True
                ):
                    mlflow.log_params(
                        {
                            "agent_name": metrics.agent_name,
                            "framework": metrics.framework,
                        }
                    )

                    if metrics.accuracy is not None:
                        mlflow.log_metric("accuracy", metrics.accuracy)
                    if metrics.cost_usd is not None:
                        mlflow.log_metric("cost_usd", metrics.cost_usd)
                    if metrics.tokens_used is not None:
                        mlflow.log_metric("tokens_used", metrics.tokens_used)
                    if metrics.latency_ms is not None:
                        mlflow.log_metric("latency_ms", metrics.latency_ms)
                    if metrics.success_rate is not None:
                        mlflow.log_metric("success_rate", metrics.success_rate)

                    # Log extra metrics
                    for key, value in extra_metrics.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
            except Exception as e:
                logger.warning(f"MLflow logging failed: {e}")

        # Langfuse
        if "langfuse" in self.external_tracers:
            try:
                langfuse = self.external_tracers["langfuse"]
                langfuse.generation(
                    name=f"{metrics.agent_name}_run",
                    metadata=metrics.to_dict(),
                    usage={"total": metrics.tokens_used or 0},
                    cost=metrics.cost_usd,
                )
            except Exception as e:
                logger.warning(f"Langfuse logging failed: {e}")

        # Weights & Biases
        if "wandb" in self.external_tracers:
            try:
                wandb = self.external_tracers["wandb"]
                log_dict = {
                    f"agent_run/{metrics.agent_name}/accuracy": metrics.accuracy,
                    f"agent_run/{metrics.agent_name}/cost_usd": metrics.cost_usd,
                    f"agent_run/{metrics.agent_name}/tokens": metrics.tokens_used,
                    f"agent_run/{metrics.agent_name}/latency_ms": metrics.latency_ms,
                    f"agent_run/{metrics.agent_name}/success_rate": metrics.success_rate,
                }
                # Filter out None values
                log_dict = {k: v for k, v in log_dict.items() if v is not None}
                wandb.log(log_dict)
            except Exception as e:
                logger.warning(f"W&B logging failed: {e}")

    def _log_gepa_metrics_external(self, metrics: GEPAOptimizationMetrics):
        """Log GEPA metrics to external tracers."""
        # MLflow
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                with mlflow.start_run(
                    run_name=f"{metrics.agent_name}_gepa", nested=True
                ):
                    mlflow.log_params(
                        {
                            "agent_name": metrics.agent_name,
                            "optimizer": metrics.optimizer_name,
                            "iterations": metrics.iterations,
                            "population_size": metrics.population_size,
                            "generations": metrics.generations,
                        }
                    )
                    mlflow.log_metrics(
                        {
                            "initial_score": metrics.initial_score,
                            "final_score": metrics.final_score,
                            "improvement": metrics.improvement,
                        }
                    )
                    if metrics.duration_seconds:
                        mlflow.log_metric("duration_seconds", metrics.duration_seconds)
                    if metrics.best_prompt:
                        mlflow.log_text(metrics.best_prompt, "best_prompt.txt")
            except Exception as e:
                logger.warning(f"MLflow GEPA logging failed: {e}")

        # Langfuse
        if "langfuse" in self.external_tracers:
            try:
                langfuse = self.external_tracers["langfuse"]
                langfuse.trace(
                    name=f"{metrics.agent_name}_gepa_optimization",
                    metadata=metrics.to_dict(),
                )
            except Exception as e:
                logger.warning(f"Langfuse GEPA logging failed: {e}")

        # Weights & Biases
        if "wandb" in self.external_tracers:
            try:
                wandb = self.external_tracers["wandb"]
                wandb.log(
                    {
                        f"gepa/{metrics.agent_name}/initial_score": metrics.initial_score,
                        f"gepa/{metrics.agent_name}/final_score": metrics.final_score,
                        f"gepa/{metrics.agent_name}/improvement": metrics.improvement,
                        f"gepa/{metrics.agent_name}/iterations": metrics.iterations,
                    }
                )

                # Log evolution history as table if available
                if metrics.evolution_history:
                    table = wandb.Table(
                        columns=["generation", "best_score", "avg_score"],
                        data=[
                            [
                                h.get("generation", i),
                                h.get("best_score"),
                                h.get("avg_score"),
                            ]
                            for i, h in enumerate(metrics.evolution_history)
                        ],
                    )
                    wandb.log({f"gepa/{metrics.agent_name}/evolution": table})
            except Exception as e:
                logger.warning(f"W&B GEPA logging failed: {e}")

    def _log_protocol_metrics_external(self, metrics: ProtocolUsageMetrics):
        """Log protocol metrics to external tracers."""
        # MLflow
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                with mlflow.start_run(
                    run_name=f"{metrics.agent_name}_protocol", nested=True
                ):
                    mlflow.log_params(
                        {
                            "agent_name": metrics.agent_name,
                            "protocol_type": metrics.protocol_type,
                            "server_uri": metrics.server_uri,
                        }
                    )
                    mlflow.log_metrics(
                        {
                            "tools_discovered": metrics.tools_discovered,
                            "tools_used_count": len(metrics.tools_used),
                            "tool_success_rate": metrics.tool_success_rate,
                            "avg_latency_ms": metrics.avg_latency_ms,
                            "total_calls": metrics.total_calls,
                        }
                    )
                    mlflow.log_dict(
                        {"tools_used": metrics.tools_used}, "tools_used.json"
                    )
            except Exception as e:
                logger.warning(f"MLflow protocol logging failed: {e}")

        # Weights & Biases
        if "wandb" in self.external_tracers:
            try:
                wandb = self.external_tracers["wandb"]
                wandb.log(
                    {
                        f"protocol/{metrics.protocol_type}/tools_discovered": metrics.tools_discovered,
                        f"protocol/{metrics.protocol_type}/tools_used": len(
                            metrics.tools_used
                        ),
                        f"protocol/{metrics.protocol_type}/success_rate": metrics.tool_success_rate,
                        f"protocol/{metrics.protocol_type}/latency_ms": metrics.avg_latency_ms,
                    }
                )
            except Exception as e:
                logger.warning(f"W&B protocol logging failed: {e}")

    def _log_multi_framework_external(self, comparison_data: Dict):
        """Log multi-framework comparison to external tracers."""
        # MLflow
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                agent_name = comparison_data["agent_name"]
                with mlflow.start_run(run_name=f"{agent_name}_comparison", nested=True):
                    for framework, metrics in comparison_data["frameworks"].items():
                        for metric_name, value in metrics.items():
                            mlflow.log_metric(f"{framework}_{metric_name}", value)

                    mlflow.log_param(
                        "best_framework", comparison_data["best_framework"]
                    )
                    mlflow.log_dict(comparison_data, "framework_comparison.json")
            except Exception as e:
                logger.warning(f"MLflow comparison logging failed: {e}")

        # Weights & Biases
        if "wandb" in self.external_tracers:
            try:
                wandb = self.external_tracers["wandb"]
                agent_name = comparison_data["agent_name"]

                # Log as bar chart
                frameworks = list(comparison_data["frameworks"].keys())
                accuracies = [
                    comparison_data["frameworks"][f].get("accuracy", 0)
                    for f in frameworks
                ]
                costs = [
                    comparison_data["frameworks"][f].get("cost", 0) for f in frameworks
                ]

                table = wandb.Table(
                    columns=["framework", "accuracy", "cost"],
                    data=[[f, a, c] for f, a, c in zip(frameworks, accuracies, costs)],
                )
                wandb.log({f"comparison/{agent_name}/frameworks": table})
            except Exception as e:
                logger.warning(f"W&B comparison logging failed: {e}")

    def export_agent_metrics(self, filename: Optional[str] = None) -> str:
        """Export agent-specific metrics to JSON.

        Args:
            filename: Optional filename to save to

        Returns:
            JSON string of metrics
        """
        export_data = {
            "agent_id": self.agent_id,
            "export_timestamp": datetime.now().isoformat(),
            "agent_metrics": [m.to_dict() for m in self.agent_metrics],
            "gepa_metrics": [m.to_dict() for m in self.gepa_metrics],
            "protocol_metrics": [m.to_dict() for m in self.protocol_metrics],
        }

        json_str = json.dumps(export_data, indent=2)

        if filename:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w") as f:
                f.write(json_str)
            logger.info(f"Agent metrics exported to {filename}")

        return json_str

    def get_agent_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of agent metrics.

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "agent_id": self.agent_id,
            "total_runs": len(self.agent_metrics),
            "total_optimizations": len(self.gepa_metrics),
            "total_protocol_usage": len(self.protocol_metrics),
        }

        # Agent metrics summary
        if self.agent_metrics:
            accuracies = [
                m.accuracy for m in self.agent_metrics if m.accuracy is not None
            ]
            costs = [m.cost_usd for m in self.agent_metrics if m.cost_usd is not None]
            tokens = [
                m.tokens_used for m in self.agent_metrics if m.tokens_used is not None
            ]

            summary["avg_accuracy"] = (
                sum(accuracies) / len(accuracies) if accuracies else 0
            )
            summary["total_cost_usd"] = sum(costs) if costs else 0
            summary["total_tokens"] = sum(tokens) if tokens else 0

        # GEPA summary
        if self.gepa_metrics:
            improvements = [m.improvement for m in self.gepa_metrics]
            summary["avg_gepa_improvement"] = sum(improvements) / len(improvements)
            summary["total_gepa_iterations"] = sum(
                m.iterations for m in self.gepa_metrics
            )

        # Protocol summary
        if self.protocol_metrics:
            protocols_used = set(m.protocol_type for m in self.protocol_metrics)
            total_tools = sum(m.tools_discovered for m in self.protocol_metrics)
            summary["protocols_used"] = list(protocols_used)
            summary["total_tools_discovered"] = total_tools

        # Include base trace summary
        summary["trace_summary"] = self.get_trace_summary()

        return summary
