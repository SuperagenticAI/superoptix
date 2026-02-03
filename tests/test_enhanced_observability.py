"""Tests for enhanced observability system."""

import pytest
from datetime import datetime

from superoptix.observability.enhanced_tracer import (
    EnhancedSuperOptixTracer,
    AgentMetrics,
    GEPAOptimizationMetrics,
    ProtocolUsageMetrics,
)


class TestAgentMetrics:
    """Test AgentMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating agent metrics."""
        metrics = AgentMetrics(
            agent_name="test_agent",
            framework="dspy",
            accuracy=0.85,
            cost_usd=0.05,
            tokens_used=1500,
            latency_ms=1200,
            success_rate=0.95,
            timestamp=datetime.now(),
        )

        assert metrics.agent_name == "test_agent"
        assert metrics.framework == "dspy"
        assert metrics.accuracy == 0.85
        assert metrics.cost_usd == 0.05
        assert metrics.tokens_used == 1500
        assert metrics.latency_ms == 1200
        assert metrics.success_rate == 0.95

    def test_metrics_to_dict(self):
        """Test converting metrics to dict."""
        metrics = AgentMetrics(
            agent_name="test", framework="dspy", accuracy=0.85, timestamp=datetime.now()
        )

        result = metrics.to_dict()

        assert isinstance(result, dict)
        assert result["agent_name"] == "test"
        assert result["framework"] == "dspy"
        assert result["accuracy"] == 0.85
        assert "timestamp" in result


class TestGEPAOptimizationMetrics:
    """Test GEPA optimization metrics."""

    def test_gepa_metrics_creation(self):
        """Test creating GEPA metrics."""
        metrics = GEPAOptimizationMetrics(
            agent_name="test_agent",
            initial_score=0.65,
            final_score=0.82,
            improvement=0.17,
            iterations=20,
            population_size=10,
            generations=2,
            duration_seconds=120.5,
        )

        assert metrics.agent_name == "test_agent"
        assert metrics.initial_score == 0.65
        assert metrics.final_score == 0.82
        assert metrics.improvement == 0.17
        assert metrics.iterations == 20
        assert metrics.population_size == 10
        assert metrics.generations == 2

    def test_gepa_metrics_to_dict(self):
        """Test converting GEPA metrics to dict."""
        metrics = GEPAOptimizationMetrics(
            agent_name="test",
            initial_score=0.6,
            final_score=0.8,
            improvement=0.2,
            iterations=10,
            population_size=5,
            generations=2,
            timestamp=datetime.now(),
        )

        result = metrics.to_dict()

        assert isinstance(result, dict)
        assert result["improvement"] == 0.2
        assert "timestamp" in result


class TestProtocolUsageMetrics:
    """Test protocol usage metrics."""

    def test_protocol_metrics_creation(self):
        """Test creating protocol metrics."""
        metrics = ProtocolUsageMetrics(
            agent_name="test_agent",
            protocol_type="mcp",
            server_uri="mcp://localhost:8080/github",
            tools_discovered=5,
            tools_used=["search", "read_file"],
            tool_success_rate=0.95,
            avg_latency_ms=250.5,
            total_calls=20,
        )

        assert metrics.agent_name == "test_agent"
        assert metrics.protocol_type == "mcp"
        assert metrics.tools_discovered == 5
        assert len(metrics.tools_used) == 2
        assert metrics.tool_success_rate == 0.95


class TestEnhancedSuperOptixTracer:
    """Test enhanced tracer functionality."""

    def test_tracer_initialization(self):
        """Test tracer initialization."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test_agent", enable_external_tracing=False, auto_load=False
        )

        assert tracer.agent_id == "test_agent"
        assert len(tracer.agent_metrics) == 0
        assert len(tracer.gepa_metrics) == 0
        assert len(tracer.protocol_metrics) == 0

    def test_log_agent_run(self):
        """Test logging agent run."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        tracer.log_agent_run(
            agent_name="test_agent",
            framework="dspy",
            accuracy=0.85,
            cost_usd=0.05,
            tokens_used=1500,
            latency_ms=1200,
            success_rate=0.95,
        )

        assert len(tracer.agent_metrics) == 1
        assert tracer.agent_metrics[0].agent_name == "test_agent"
        assert tracer.agent_metrics[0].accuracy == 0.85

    def test_log_gepa_optimization(self):
        """Test logging GEPA optimization."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        tracer.log_gepa_optimization(
            agent_name="test_agent",
            initial_score=0.65,
            final_score=0.82,
            iterations=20,
            population_size=10,
            duration_seconds=120.5,
        )

        assert len(tracer.gepa_metrics) == 1
        metrics = tracer.gepa_metrics[0]
        assert abs(metrics.improvement - 0.17) < 0.01  # Floating point tolerance
        assert metrics.generations == 2  # 20 iterations / 10 population

    def test_log_protocol_usage(self):
        """Test logging protocol usage."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        tracer.log_protocol_usage(
            agent_name="test_agent",
            protocol_type="mcp",
            server_uri="mcp://localhost:8080",
            tools_discovered=5,
            tools_used=["search", "read_file"],
            tool_success_rate=0.95,
            avg_latency_ms=250.5,
            total_calls=20,
        )

        assert len(tracer.protocol_metrics) == 1
        assert tracer.protocol_metrics[0].protocol_type == "mcp"
        assert len(tracer.protocol_metrics[0].tools_used) == 2

    def test_log_multi_framework_comparison(self):
        """Test logging multi-framework comparison."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        frameworks = {
            "dspy": {"accuracy": 0.85, "cost": 0.05, "latency_ms": 1200},
            "crewai": {"accuracy": 0.78, "cost": 0.08, "latency_ms": 1800},
        }

        tracer.log_multi_framework_comparison(
            agent_name="test_agent", frameworks=frameworks
        )

        # Check that event was added
        comparison_events = [
            e for e in tracer.traces if e.event_type == "multi_framework_comparison"
        ]
        assert len(comparison_events) == 1
        assert comparison_events[0].data["best_framework"] == "dspy"

    def test_export_agent_metrics(self):
        """Test exporting agent metrics."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        # Add some metrics
        tracer.log_agent_run(agent_name="test", framework="dspy", accuracy=0.85)

        tracer.log_gepa_optimization(
            agent_name="test",
            initial_score=0.6,
            final_score=0.8,
            iterations=10,
            population_size=5,
        )

        # Export
        export = tracer.export_agent_metrics()

        assert "agent_metrics" in export
        assert "gepa_metrics" in export
        assert len(tracer.agent_metrics) == 1
        assert len(tracer.gepa_metrics) == 1

    def test_get_agent_summary(self):
        """Test getting agent summary."""
        tracer = EnhancedSuperOptixTracer(
            agent_id="test", enable_external_tracing=False, auto_load=False
        )

        # Add metrics
        tracer.log_agent_run(
            agent_name="test",
            framework="dspy",
            accuracy=0.85,
            cost_usd=0.05,
            tokens_used=1500,
        )

        tracer.log_agent_run(
            agent_name="test",
            framework="dspy",
            accuracy=0.90,
            cost_usd=0.03,
            tokens_used=1200,
        )

        summary = tracer.get_agent_summary()

        assert summary["total_runs"] == 2
        assert summary["avg_accuracy"] == 0.875  # (0.85 + 0.90) / 2
        assert summary["total_cost_usd"] == 0.08  # 0.05 + 0.03
        assert summary["total_tokens"] == 2700  # 1500 + 1200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
