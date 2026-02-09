# Enhanced Observability in SuperOptiX

## 🎯 Overview

SuperOptiX provides **comprehensive observability** with support for multiple backends:
- **SuperOptiX** (local-first, default)
- **MLFlow** (ML experiment tracking)
- **LangFuse** (LLM observability)
- **Weights & Biases** (experiment tracking)
- **All** (log to all backends simultaneously)

**Unique Feature**: Agent-specific metrics including GEPA optimization, protocol usage, and multi-framework comparison.

---

## ⚡ Quick Start

### Run Agent with Observability

```bash
# Use default (local storage)
super agent run my_agent --goal "Analyze data" --observe superoptix

# Use MLFlow
super agent run my_agent --goal "Analyze data" --observe mlflow

# Use Weights & Biases
super agent run my_agent --goal "Analyze data" --observe wandb

# Use all backends
super agent run my_agent --goal "Analyze data" --observe all
```

### View Dashboard

```bash
# Start local dashboard
python -c "from superoptix.observability.simple_dashboard import start_dashboard; start_dashboard()"

# Opens at http://localhost:8000
```

---

## 📊 Supported Backends

### SuperOptiX (Local-First)

**Pros**:
- No setup required
- Works offline
- Fast queries
- Privacy-friendly
- Built-in dashboard

**Best For**:
- Development
- Testing
- Offline work
- Privacy-sensitive projects

### MLFlow

**Pros**:
- Industry standard
- Excellent artifact management
- Model registry
- Experiment comparison

**Best For**:
- ML experiments
- Model versioning
- Team collaboration
- Production ML

**Setup**:
```bash
pip install mlflow
mlflow ui  # View at http://localhost:5000
```

### LangFuse

**Pros**:
- LLM-specific features
- Automatic token tracking
- Built-in cost calculation
- User feedback collection

**Best For**:
- LLM applications
- Real-time monitoring
- Cost optimization
- A/B testing

**Setup**:
```bash
pip install langfuse
# Set environment variables
export LANGFUSE_PUBLIC_KEY="..."
export LANGFUSE_SECRET_KEY="..."
```

### Weights & Biases

**Pros**:
- Beautiful visualizations
- Experiment tracking
- Team collaboration
- Hyperparameter tuning

**Best For**:
- Research projects
- Experiment comparison
- Hyperparameter optimization
- Team sharing

**Setup**:
```bash
pip install wandb
wandb login
```

---

## 🌟 Agent-Specific Metrics

### GEPA Optimization Tracking

SuperOptiX automatically tracks GEPA optimization runs:

```python
from superoptix.observability import get_observability

obs = get_observability("my_agent", backend="mlflow")

obs.log_optimization(
    agent_name="my_agent",
    optimizer="GEPA",
    initial_score=0.65,
    final_score=0.82,
    iterations=20,
    population_size=10,
    duration_seconds=120
)

# MLFlow shows:
# - Initial vs final score
# - Improvement: +17%
# - Iterations: 20
# - Duration: 120s
```

### Protocol Usage Monitoring

Track MCP server usage and tool discovery:

```python
obs.log_protocol(
    agent_name="github_agent",
    protocol_type="mcp",
    server="mcp://localhost:8080/github",
    tools_discovered=5,
    tools_used=["search_repositories", "get_file_contents"],
    tool_success_rate=0.95,
    avg_latency_ms=250,
    total_calls=20
)

# Dashboard shows:
# - Protocol type (MCP)
# - Tools discovered: 5
# - Tools used: 2
# - Success rate: 95%
# - Avg latency: 250ms
```

### Multi-Framework Comparison

Compare agent performance across frameworks:

```python
frameworks = {
    "dspy": {"accuracy": 0.85, "cost": 0.05, "latency_ms": 1200},
    "crewai": {"accuracy": 0.78, "cost": 0.08, "latency_ms": 1800},
    "langraph": {"accuracy": 0.80, "cost": 0.06, "latency_ms": 1500}
}

obs.log_framework_comparison(
    agent_name="test_agent",
    frameworks=frameworks
)

# Shows:
# - Best framework: dspy
# - Side-by-side metrics
# - Performance comparison chart
```

### Cost Tracking

Track LLM costs per agent and provider:

```python
obs.log_cost(
    agent_name="my_agent",
    provider="openai",
    model="gpt-4",
    tokens_input=800,
    tokens_output=700,
    cost_usd=0.045
)

# Dashboard shows:
# - Total cost: $0.045
# - Tokens: 1,500
# - Cost per 1K tokens: $0.03
```

---

## 🔧 Advanced Usage

### Programmatic Usage

```python
from superoptix.observability import EnhancedSuperOptixTracer

# Create tracer with specific backend
tracer = EnhancedSuperOptixTracer(
    agent_id="my_agent",
    enable_external_tracing=True,
    observability_backend="wandb",
    auto_load=False
)

# Log agent run
tracer.log_agent_run(
    agent_name="my_agent",
    framework="dspy",
    accuracy=0.85,
    cost_usd=0.05,
    tokens_used=1500,
    latency_ms=1200,
    success_rate=0.95
)

# Log optimization
tracer.log_gepa_optimization(
    agent_name="my_agent",
    initial_score=0.65,
    final_score=0.82,
    iterations=20,
    population_size=10
)

# Get summary
summary = tracer.get_agent_summary()
print(f"Total runs: {summary['total_runs']}")
print(f"Total cost: ${summary['total_cost_usd']:.2f}")
print(f"Avg accuracy: {summary['avg_accuracy']:.2f}")

# Export metrics
tracer.export_agent_metrics("metrics.json")
```

### Local Storage Direct Access

```python
from superoptix.observability.local_storage import LocalObservabilityStorage

storage = LocalObservabilityStorage()

# Query recent runs
runs = storage.get_agent_runs("my_agent", limit=10)
for run in runs:
    print(f"{run['timestamp']}: {run['accuracy']:.2f}")

# Get cost summary
cost = storage.get_cost_summary("my_agent", days=30)
print(f"30-day cost: ${cost['total_cost_usd']:.2f}")

# Get optimization summary
opts = storage.get_optimization_summary("my_agent")
print(f"Avg improvement: +{opts['avg_improvement']:.2%}")

# Export to MLFlow
storage.export_to_mlflow("my_agent")
```

### Dashboard API

```bash
# Start dashboard server
python -m superoptix.observability.simple_dashboard

# API endpoints available:
# GET /                      - Dashboard UI
# GET /api/dashboard         - All dashboard data
# GET /api/runs              - Agent runs
# GET /api/optimizations     - Optimization history
# GET /api/protocols         - Protocol usage
# GET /api/cost/summary      - Cost summary
```

---

## 📈 Example Workflow

### Complete Optimization & Monitoring Workflow

```bash
# Create agent with observability
super agent compile my_agent

# Run baseline (with observability)
super agent run my_agent --goal "Test query" --observe mlflow

# Evaluate
super agent evaluate my_agent

# Optimize with GEPA (auto-tracked)
super agent optimize my_agent --auto medium

# Run optimized (compare metrics)
super agent run my_agent --goal "Test query" --observe mlflow

# View results
mlflow ui  # See before/after comparison
```

---

## 🎯 Best Practices

### Choose the Right Backend

```bash
# Development: Use local
super agent run my_agent --goal "..." --observe superoptix

# Team work: Use MLFlow
super agent run my_agent --goal "..." --observe mlflow

# Research: Use W&B
super agent run my_agent --goal "..." --observe wandb

# Production: Use all + export
super agent run my_agent --goal "..." --observe all
```

### Track Optimization History

```python
# Before each optimization
obs.log_agent_run(agent_name, framework, accuracy=baseline_score)

# During optimization (automatic if using CLI)
# super agent optimize my_agent --auto medium

# After optimization
obs.log_agent_run(agent_name, framework, accuracy=optimized_score)
```

### Monitor Protocol Usage

```python
# Log protocol connections
obs.log_protocol(
    agent_name="agent",
    protocol_type="mcp",
    server="mcp://...",
    tools_discovered=5,
    tools_used=tools_list
)

# Track over time to see:
# - Tool usage patterns
# - Success rates
# - Latency trends
```

---

## 🐛 Troubleshooting

### MLFlow Not Logging

**Issue**: Metrics not appearing in MLFlow

**Solution**:
1. Ensure MLFlow is installed: `pip install mlflow`
2. Start MLFlow UI: `mlflow ui`
3. Check experiment name matches: `SuperOptiX-{agent_name}`
4. Verify environment variables if using remote tracking

### W&B Authentication Failed

**Issue**: "wandb authentication failed"

**Solution**:
1. Login: `wandb login`
2. Provide API key (get from https://wandb.ai/authorize)
3. Verify: `wandb verify`

### Dashboard Not Starting

**Issue**: Dashboard won't start

**Solution**:
1. Install FastAPI: `pip install fastapi uvicorn`
2. Check port 8000 is free: `lsof -i :8000`
3. Try different port: `start_dashboard(port=8001)`

---

## 📚 API Reference

### UnifiedObservability

```python
from superoptix.observability.unified_interface import get_observability

obs = get_observability(
    agent_id="my_agent",
    backend="mlflow",  # or langfuse, wandb, all
    enable_external=True
)

# Log agent run
obs.log_agent_run(
    agent_name="agent",
    framework="dspy",
    accuracy=0.85,
    cost_usd=0.05,
    tokens_used=1500
)

# Log optimization
obs.log_optimization(
    agent_name="agent",
    optimizer="GEPA",
    initial_score=0.65,
    final_score=0.82,
    iterations=20
)

# Log protocol usage
obs.log_protocol(
    agent_name="agent",
    protocol_type="mcp",
    server="mcp://...",
    tools_discovered=5,
    tools_used=["tool1", "tool2"]
)

# Get summary
summary = obs.get_summary()

# Export
obs.export("metrics.json", format="json")

# Cleanup
obs.cleanup()
```

---

## 🎓 Examples

See complete examples in:
- `examples/observability/mlflow_example.py`
- `examples/observability/wandb_example.py`
- `examples/observability/local_storage_example.py`

---

## 🚀 What Makes SuperOptiX Different

### Unique Agent-Specific Metrics

No other platform tracks:
- GEPA optimization iterations and improvements
- Protocol usage (MCP servers, tools discovered)
- Multi-framework performance comparison
- Agent-specific cost breakdown

### Local-First Architecture

- Works without internet
- No cloud dependency
- Privacy-friendly
- Fast queries
- Export when ready

### User Choice

- Pick any backend
- Mix backends
- No vendor lock-in
- Enterprise-approved tools

---

## 🎯 Next Steps

1. **Try the local dashboard**: `python -m superoptix.observability.simple_dashboard`
2. **Integrate with your favorite tool**: Use `--observe` flag
3. **Track your optimizations**: GEPA metrics automatically logged
4. **Monitor protocols**: See MCP usage in real-time

---

**SuperOptiX: The ONLY framework with agent-specific observability!** 🚀

---

*Last Updated: 2025-10-20*
*Version: 1.0.0*

