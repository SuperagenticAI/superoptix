# Weights & Biases Integration

## 🎯 Overview

SuperOptiX provides **native integration** with Weights & Biases (W&B) for experiment tracking, model monitoring, and team collaboration. This integration allows you to track agent performance, GEPA optimization runs, and multi-framework comparisons in your existing W&B workflows.

**Key Features**:
- ✅ **Agent-specific metrics** (GEPA optimization, protocol usage)
- ✅ **Multi-framework tracking** (DSPy, OpenAI SDK, CrewAI, etc.)
- ✅ **Team collaboration** (shared experiments, dashboards)
- ✅ **Model versioning** (track agent improvements over time)
- ✅ **Hyperparameter optimization** (GEPA parameter tuning)

---

## ⚡ Quick Start

### 1. Install W&B

```bash
pip install wandb
wandb login
```

### 2. Run Agent with W&B

```bash
# Track agent execution
super agent run my_agent --goal "Analyze data" --observe wandb

# Track optimization runs
super agent optimize my_agent --auto medium --observe wandb

# Track evaluation
super agent evaluate my_agent --observe wandb
```

### 3. View in W&B Dashboard

Visit: https://wandb.ai/your-username/superoptix

---

## 📊 What Gets Tracked

### Agent Execution Metrics

| Metric | Description | Example |
|--------|-------------|---------|
| `execution/latency` | Response time | 1.2s |
| `execution/success_rate` | Task completion rate | 95% |
| `execution/token_usage` | LLM token consumption | 1,250 tokens |
| `execution/cost` | Estimated cost | $0.002 |

### GEPA Optimization Metrics

| Metric | Description | Example |
|--------|-------------|---------|
| `gepa/generation` | Optimization generation | 5 |
| `gepa/fitness_score` | Current best score | 0.85 |
| `gepa/improvement` | Score improvement | +0.12 |
| `gepa/population_size` | Population size | 20 |

### Framework Comparison Metrics

| Metric | Description | Example |
|--------|-------------|---------|
| `comparison/dspy/accuracy` | DSPy framework accuracy | 0.80 |
| `comparison/openai/accuracy` | OpenAI SDK accuracy | 0.95 |
| `comparison/crewai/accuracy` | CrewAI accuracy | 0.88 |

---

## 🔧 Configuration

### Basic Configuration

```yaml
# In your playbook
spec:
  observability:
    backend: wandb
    config:
      project: "my-agent-project"
      entity: "my-team"  # Optional
      tags: ["production", "v2"]
```

### Advanced Configuration

```python
from superoptix.observability import get_observability

# Custom W&B configuration
obs = get_observability(
    agent_name="my_agent",
    backend="wandb",
    config={
        "project": "superoptix-agents",
        "entity": "my-company",
        "tags": ["production", "customer-support"],
        "group": "agent-optimization",
        "job_type": "gepa-optimization"
    }
)
```

---

## 📈 Dashboard Setup

### 1. Create Custom Dashboard

In W&B, create a new dashboard with these panels:

**Agent Performance Panel**:
```python
# Query: agent_name = "my_agent"
# Metrics: execution/latency, execution/success_rate
# Chart: Line plot over time
```

**GEPA Optimization Panel**:
```python
# Query: run.tags contains "gepa"
# Metrics: gepa/fitness_score, gepa/improvement
# Chart: Scatter plot (generation vs fitness)
```

**Framework Comparison Panel**:
```python
# Query: run.tags contains "comparison"
# Metrics: comparison/*/accuracy
# Chart: Bar chart by framework
```

### 2. Automated Reports

```python
# Generate weekly performance report
super agent report my_agent --format wandb --period weekly
```

---

## 🚀 Advanced Features

### 1. Hyperparameter Optimization

```bash
# Track GEPA parameter tuning
super agent optimize my_agent \
  --auto intensive \
  --observe wandb \
  --wandb-sweep \
  --sweep-config sweep_config.yaml
```

**sweep_config.yaml**:
```yaml
program: "super agent optimize"
method: bayes
metric:
  name: "gepa/fitness_score"
  goal: maximize
parameters:
  reflection_lm:
    values: ["qwen3:8b", "llama3:8b", "gemma2:9b"]
  reflection_minibatch_size:
    distribution: int_uniform
    min: 2
    max: 8
  auto:
    values: ["light", "medium", "intensive"]
```

### 2. Model Versioning

```python
# Track model improvements
super agent run my_agent \
  --goal "Process documents" \
  --observe wandb \
  --model-version "v2.1" \
  --tags ["production", "document-processing"]
```

### 3. Team Collaboration

```bash
# Share experiments with team
super agent run my_agent \
  --goal "Customer support" \
  --observe wandb \
  --entity "my-company" \
  --project "customer-agents" \
  --tags ["team-shared", "customer-support"]
```

---

## 🔍 Troubleshooting

### Common Issues

**Issue**: "wandb authentication failed"
```bash
# Solution
wandb login
# Enter API key from: https://wandb.ai/authorize
```

**Issue**: "Project not found"
```bash
# Solution: Create project first
wandb init --project "my-superoptix-project"
```

**Issue**: "Entity not found"
```bash
# Solution: Check entity name
wandb whoami
# Use correct entity name or omit for personal account
```

### Debug Mode

```bash
# Enable debug logging
export WANDB_DEBUG=true
super agent run my_agent --observe wandb --verbose
```

---

## 📊 Example Workflows

### 1. Agent Development Workflow

```bash
# 1. Initial development
super agent run my_agent --observe wandb --tags ["development"]

# 2. Optimization
super agent optimize my_agent --observe wandb --tags ["optimization"]

# 3. Evaluation
super agent evaluate my_agent --observe wandb --tags ["evaluation"]

# 4. Production deployment
super agent run my_agent --observe wandb --tags ["production"]
```

### 2. Multi-Framework Comparison

```bash
# Compare frameworks
super agent run sentiment_analyzer --observe wandb --tags ["dspy", "comparison"]
super agent run assistant_openai --observe wandb --tags ["openai", "comparison"]
super agent run researcher_crew --observe wandb --tags ["crewai", "comparison"]
```

### 3. A/B Testing

```bash
# Test different configurations
super agent run my_agent \
  --observe wandb \
  --tags ["ab-test", "config-a"] \
  --config config_a.yaml

super agent run my_agent \
  --observe wandb \
  --tags ["ab-test", "config-b"] \
  --config config_b.yaml
```

---

## 🎯 Best Practices

### 1. Project Organization

```
📁 W&B Projects Structure:
├── superoptix-agents/          # Main project
├── superoptix-gepa/            # GEPA optimization runs
├── superoptix-comparison/       # Framework comparisons
└── superoptix-production/      # Production monitoring
```

### 2. Tagging Strategy

```bash
# Use consistent tags
--tags ["framework:dspy", "tier:genies", "stage:production"]
--tags ["optimization:gepa", "auto:medium", "run:001"]
--tags ["comparison", "framework:openai", "metric:accuracy"]
```

### 3. Metric Naming

```python
# Use hierarchical naming
"execution/latency"
"execution/success_rate"
"gepa/fitness_score"
"gepa/improvement"
"comparison/dspy/accuracy"
"comparison/openai/accuracy"
```

---

## 🔗 Integration Examples

### With MLFlow

```bash
# Log to both W&B and MLFlow
super agent run my_agent --observe all
```

### With LangFuse

```bash
# Use W&B for metrics, LangFuse for traces
super agent run my_agent --observe wandb
super agent run my_agent --observe langfuse
```

### With Custom Metrics

```python
import wandb

# Add custom metrics
wandb.log({
    "custom/business_metric": calculate_business_value(),
    "custom/user_satisfaction": get_user_rating(),
    "custom/cost_per_interaction": calculate_cost()
})
```

---

## 📚 Resources

- **W&B Documentation**: https://docs.wandb.ai/
- **SuperOptiX Observability**: [Enhanced Observability Guide](enhanced-observability.md)
- **GEPA Optimization**: [GEPA Guide](gepa-optimization.md)
- **Multi-Framework Support**: [Multi-Framework Guide](multi-framework.md)

---

## 🎉 Next Steps

1. **Set up W&B account**: https://wandb.ai/signup
2. **Install and login**: `pip install wandb && wandb login`
3. **Run your first tracked agent**: `super agent run my_agent --observe wandb`
4. **Create custom dashboard** in W&B
5. **Set up team collaboration** with shared projects

**Ready to track your agent experiments?** Start with the [Quick Start](#-quick-start) section above!
