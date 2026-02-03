# Weights & Biases Demo

## 🎯 Overview

This demo shows how to use **Weights & Biases (W&B)** with SuperOptiX to track agent experiments, GEPA optimization runs, and multi-framework comparisons.

**What you'll learn**:
- ✅ Set up W&B integration
- ✅ Track agent execution metrics
- ✅ Monitor GEPA optimization
- ✅ Compare different frameworks
- ✅ Create custom dashboards

---

## 🚀 Quick Demo

### 1. Setup W&B

```bash
# Install W&B
pip install wandb

# Login to W&B
wandb login
# Enter your API key from: https://wandb.ai/authorize
```

### 2. Run Agent with W&B Tracking

```bash
# Initialize project
super init wb_demo
cd wb_demo

# Pull a demo agent
super agent pull assistant_openai

# Compile and run with W&B tracking
super agent compile assistant_openai
super agent run assistant_openai \
  --query "What is artificial intelligence?" \
  --observe wandb \
  --tags ["demo", "openai-sdk"]
```

### 3. View Results in W&B

Visit: https://wandb.ai/your-username/superoptix

You'll see:
- **Execution metrics** (latency, token usage, cost)
- **Agent performance** (success rate, response quality)
- **Custom tags** for organization

---

## 📊 Advanced Demo: GEPA Optimization

### Track Optimization Runs

```bash
# Run GEPA optimization with W&B tracking
super agent optimize assistant_openai \
  --auto medium \
  --observe wandb \
  --tags ["gepa", "optimization", "medium"]

# View optimization progress in W&B
# Look for metrics like:
# - gepa/generation
# - gepa/fitness_score
# - gepa/improvement
```

### Optimization Dashboard

In W&B, create a dashboard with:

**GEPA Progress Panel**:
```python
# Query: run.tags contains "gepa"
# Metrics: gepa/fitness_score
# Chart: Line plot over generations
```

**Improvement Panel**:
```python
# Query: run.tags contains "optimization"
# Metrics: gepa/improvement
# Chart: Bar chart showing score increases
```

---

## 🔬 Multi-Framework Comparison Demo

### Compare Different Frameworks

```bash
# Test DSPy agent
super agent pull sentiment_analyzer
super agent compile sentiment_analyzer
super agent run sentiment_analyzer \
  --query "This is amazing!" \
  --observe wandb \
  --tags ["framework:dspy", "comparison"]

# Test OpenAI SDK agent
super agent run assistant_openai \
  --query "This is amazing!" \
  --observe wandb \
  --tags ["framework:openai", "comparison"]

# Test CrewAI agent
super agent pull researcher_crew
super agent compile researcher_crew
super agent run researcher_crew \
  --query "Research artificial intelligence trends" \
  --observe wandb \
  --tags ["framework:crewai", "comparison"]
```

### Framework Comparison Dashboard

Create a comparison dashboard:

**Accuracy Comparison**:
```python
# Query: run.tags contains "comparison"
# Metrics: execution/accuracy
# Chart: Bar chart by framework
```

**Latency Comparison**:
```python
# Query: run.tags contains "comparison"
# Metrics: execution/latency
# Chart: Box plot by framework
```

---

## 🎨 Custom Metrics Demo

### Add Custom Business Metrics

```python
# Create custom_metrics.py
import wandb
import time

def track_custom_metrics(agent_response, user_query):
    """Track custom business metrics."""
    
    # Calculate business value
    business_value = len(agent_response) * 0.1  # Simple example
    
    # Calculate user satisfaction (mock)
    user_satisfaction = 0.8 if "helpful" in agent_response.lower() else 0.6
    
    # Calculate cost per interaction
    cost_per_interaction = 0.002  # Mock cost
    
    # Log to W&B
    wandb.log({
        "business/value": business_value,
        "business/user_satisfaction": user_satisfaction,
        "business/cost_per_interaction": cost_per_interaction,
        "business/response_length": len(agent_response),
        "business/query_complexity": len(user_query.split())
    })

# Use in your agent
def run_agent_with_custom_metrics():
    response = "This is a helpful response about AI."
    track_custom_metrics(response, "What is AI?")
```

### Run with Custom Metrics

```bash
# Run agent with custom metrics
python custom_metrics.py
super agent run assistant_openai \
  --query "Explain machine learning" \
  --observe wandb \
  --tags ["custom-metrics", "business-tracking"]
```

---

## 📈 Hyperparameter Optimization Demo

### Create Sweep Configuration

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

### Run Hyperparameter Sweep

```bash
# Initialize sweep
wandb sweep sweep_config.yaml

# Run sweep (replace SWEEP_ID with actual ID)
wandb agent your-username/superoptix/SWEEP_ID
```

### View Sweep Results

In W&B:
1. Go to your project
2. Click on "Sweeps" tab
3. View parallel coordinates plot
4. See best parameters highlighted

---

## 🏢 Team Collaboration Demo

### Shared Project Setup

```bash
# Create shared project
wandb init --project "team-agent-experiments" --entity "my-company"

# Run experiments with team tags
super agent run assistant_openai \
  --query "Customer support query" \
  --observe wandb \
  --entity "my-company" \
  --project "team-agent-experiments" \
  --tags ["team:engineering", "customer-support", "production"]
```

### Team Dashboard

Create team dashboard with:

**Team Performance Panel**:
```python
# Query: run.tags contains "team:engineering"
# Metrics: execution/success_rate
# Chart: Line plot over time
```

**Customer Support Panel**:
```python
# Query: run.tags contains "customer-support"
# Metrics: execution/latency, execution/success_rate
# Chart: Multi-line plot
```

---

## 🔍 Debugging Demo

### Enable Debug Mode

```bash
# Enable W&B debug logging
export WANDB_DEBUG=true

# Run with verbose output
super agent run assistant_openai \
  --query "Debug test" \
  --observe wandb \
  --verbose \
  --tags ["debug", "testing"]
```

### Check W&B Logs

```bash
# View W&B logs
tail -f ~/.local/share/wandb/debug.log

# Check W&B status
wandb status
```

---

## 📊 Example Dashboard Queries

### Agent Performance Dashboard

```python
# Panel 1: Execution Metrics
# Query: run.tags contains "production"
# Metrics: execution/latency, execution/success_rate
# Chart: Time series

# Panel 2: Cost Tracking
# Query: run.tags contains "production"
# Metrics: execution/cost, execution/token_usage
# Chart: Scatter plot

# Panel 3: Framework Comparison
# Query: run.tags contains "comparison"
# Metrics: execution/accuracy
# Chart: Bar chart by framework
```

### GEPA Optimization Dashboard

```python
# Panel 1: Optimization Progress
# Query: run.tags contains "gepa"
# Metrics: gepa/fitness_score
# Chart: Line plot over generations

# Panel 2: Parameter Impact
# Query: run.tags contains "optimization"
# Metrics: gepa/improvement
# Chart: Scatter plot by parameter

# Panel 3: Best Runs
# Query: run.tags contains "gepa"
# Metrics: gepa/fitness_score
# Chart: Table sorted by fitness score
```

---

## 🎯 Best Practices Demo

### 1. Consistent Tagging

```bash
# Use hierarchical tags
super agent run my_agent \
  --observe wandb \
  --tags ["framework:dspy", "tier:genies", "stage:production", "version:v2.1"]
```

### 2. Project Organization

```bash
# Organize by project type
super agent run my_agent --observe wandb --project "superoptix-development"
super agent run my_agent --observe wandb --project "superoptix-production"
super agent run my_agent --observe wandb --project "superoptix-research"
```

### 3. Metric Naming

```python
# Use consistent metric names
wandb.log({
    "execution/latency": 1.2,
    "execution/success_rate": 0.95,
    "gepa/fitness_score": 0.85,
    "business/value": 10.5,
    "custom/user_satisfaction": 0.8
})
```

---

## 🔗 Integration Examples

### With MLFlow

```bash
# Log to both W&B and MLFlow
super agent run my_agent --observe all --tags ["multi-backend"]
```

### With LangFuse

```bash
# Use W&B for metrics, LangFuse for traces
super agent run my_agent --observe wandb --tags ["metrics"]
super agent run my_agent --observe langfuse --tags ["traces"]
```

---

## 📚 Next Steps

1. **Complete the demos** above
2. **Create your own dashboard** in W&B
3. **Set up team collaboration** with shared projects
4. **Try hyperparameter optimization** with sweeps
5. **Integrate with your existing workflow**

**Ready to start?** Begin with the [Quick Demo](#-quick-demo) section!

---

## 🔗 Related Resources

- [Weights & Biases Integration Guide](../guides/weights-biases-integration.md)
- [Enhanced Observability Guide](../guides/enhanced-observability.md)
- [GEPA Optimization Guide](../guides/gepa-optimization.md)
- [Multi-Framework Guide](../guides/multi-framework.md)
