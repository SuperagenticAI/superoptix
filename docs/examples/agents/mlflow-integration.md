# 🧪 MLFlow Integration

Learn how to integrate SuperOptiX with MLFlow for comprehensive experiment tracking, model monitoring, and observability.

## 🎯 Overview

MLFlow is a popular open-source platform (third-party) for managing the complete machine learning lifecycle. This integration allows you to:

- **Track experiments** with detailed metrics and parameters
- **Monitor model performance** across different runs
- **Compare agent versions** and configurations
- **Export trace data** to MLFlow for analysis
- **Visualize agent behavior** in MLFlow UI

## 🚀 Quick Setup

### Prerequisites

```bash
# Install MLFlow
pip install mlflow

# Install SuperOptiX with MLFlow support
pip install superoptix[mlflow]
```

### Basic Configuration

Create a configuration file `mlflow_config.yaml`:

```yaml
# mlflow_config.yaml
mlflow:
  tracking_uri: "http://localhost:5000"  # MLFlow server URL
  experiment_name: "superoptix_agents"
  log_artifacts: true
  log_metrics: true
  log_params: true
  
# SuperOptiX observability configuration
observability:
  enabled: true
  backends:
    - mlflow
  trace_export:
    format: "mlflow"
    batch_size: 100
```

## 🔧 Integration Setup

### Step 1: Start MLFlow Server

```bash
# Start MLFlow tracking server
mlflow server --host 0.0.0.0 --port 5000

# Or use MLFlow UI
mlflow ui --host 0.0.0.0 --port 5000
```

### Step 2: Configure SuperOptiX

Update your agent playbook to include MLFlow integration:

```yaml
# developer_playbook.yaml
name: "Developer Assistant"
description: "AI developer with MLFlow integration"
tier: "genies"

# ... existing configuration ...

observability:
  enabled: true
  backends:
    - mlflow
  mlflow:
    experiment_name: "developer_agent"
    tracking_uri: "http://localhost:5000"
    log_artifacts: true
    log_metrics: true
    log_params: true
    tags:
      agent_type: "developer"
      tier: "genies"
      version: "1.0.0"
```

### Step 3: Run Agent with MLFlow Tracking

```bash
# Initialize project
super init mlflow_demo
cd mlflow_demo

# Pull and compile agent
super agent pull developer
super agent compile developer

# Run with MLFlow tracking
super agent run developer --goal "Write a Python function to calculate fibonacci numbers"
```

## 📊 MLFlow Integration Features

### Automatic Experiment Tracking

SuperOptiX automatically logs the following to MLFlow:

**Parameters:**
- Agent configuration
- Model settings
- Tool configurations
- Execution parameters

**Metrics:**
- Execution time
- Token usage
- Tool usage frequency
- Success/failure rates
- Memory usage

**Artifacts:**
- Trace files (JSONL format)
- Generated code
- Tool outputs
- Error logs

### Example MLFlow Run

```python
# MLFlow run structure
{
  "run_id": "abc123",
  "experiment_name": "developer_agent",
  "parameters": {
    "agent_name": "developer",
    "tier": "genies",
    "model": "llama3.1:8b",
    "temperature": 0.7,
    "max_tokens": 2048
  },
  "metrics": {
    "execution_time_ms": 10270.0,
    "total_tokens": 1250,
    "tools_used": 3,
    "success_rate": 1.0
  },
  "artifacts": {
    "traces.jsonl": "path/to/traces.jsonl",
    "generated_code.py": "path/to/output.py",
    "tool_outputs.json": "path/to/tools.json"
  }
}
```

## 🔍 Advanced Configuration

### Custom Metrics Logging

Extend the MLFlow integration with custom metrics:

```yaml
# Custom metrics configuration
observability:
  mlflow:
    custom_metrics:
      - name: "code_quality_score"
        type: "float"
        description: "Code quality assessment score"
      - name: "tool_efficiency"
        type: "float"
        description: "Tool usage efficiency ratio"
      - name: "response_relevance"
        type: "float"
        description: "Response relevance score"
```

### Batch Processing

Configure batch processing for high-volume scenarios:

```yaml
observability:
  mlflow:
    batch_processing:
      enabled: true
      batch_size: 100
      flush_interval: 30  # seconds
      max_queue_size: 1000
```

### Custom Tags and Metadata

Add custom tags and metadata to MLFlow runs:

```yaml
observability:
  mlflow:
    tags:
      environment: "production"
      team: "ai_engineering"
      project: "code_assistant"
    metadata:
      version: "1.2.0"
      deployment: "kubernetes"
      region: "us-west-2"
```

## 📈 Monitoring and Analysis

### MLFlow UI Dashboard

Access the MLFlow UI to view experiments:

```bash
# Open MLFlow UI
open http://localhost:5000
```

**Available Views:**
- **Experiments**: Compare different agent runs
- **Runs**: Detailed run information
- **Metrics**: Performance trends over time
- **Artifacts**: Generated outputs and traces
- **Parameters**: Configuration comparisons

### Custom Dashboards

Create custom dashboards using MLFlow's API:

```python
import mlflow
import pandas as pd

# Query experiments
experiments = mlflow.search_experiments()
runs = mlflow.search_runs(experiment_names=["developer_agent"])

# Analyze performance trends
performance_df = runs[["execution_time_ms", "total_tokens", "success_rate"]]
print(performance_df.describe())
```

### Alerting and Notifications

Set up alerts for performance degradation:

```python
# Example alerting script
def check_performance_alerts():
    runs = mlflow.search_runs(experiment_names=["developer_agent"])
    latest_run = runs.iloc[0]
    
    if latest_run["execution_time_ms"] > 15000:  # 15 seconds
        send_alert("Agent execution time exceeded threshold")
    
    if latest_run["success_rate"] < 0.9:
        send_alert("Agent success rate below threshold")
```

## 🔧 Troubleshooting

### Common Issues

**1. MLFlow Server Connection**
```bash
# Check MLFlow server status
curl http://localhost:5000/health

# Restart MLFlow server
mlflow server --host 0.0.0.0 --port 5000
```

**2. Authentication Issues**
```bash
# Set MLFlow tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# Or configure in code
mlflow.set_tracking_uri("http://localhost:5000")
```

**3. Artifact Storage**
```bash
# Configure artifact storage
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts
```

### Debug Mode

Enable debug logging for MLFlow integration:

```yaml
observability:
  mlflow:
    debug: true
    log_level: "DEBUG"
```

## 🚀 Production Deployment

### MLFlow Server Setup

For production deployments, use a robust MLFlow setup:

```bash
# Using PostgreSQL backend
mlflow server \
  --backend-store-uri postgresql://user:pass@host:port/db \
  --default-artifact-root s3://bucket/mlflow \
  --host 0.0.0.0 \
  --port 5000
```

### Kubernetes Deployment

Deploy MLFlow with Kubernetes:

```yaml
# mlflow-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: python:3.9
        command: ["mlflow", "server"]
        args: ["--host", "0.0.0.0", "--port", "5000"]
        ports:
        - containerPort: 5000
```

## 📚 Related Resources

- **[Observability Guide](../guides/observability.md)** - Complete observability overview
- **[Agent Development](../guides/agent-development.md)** - Build custom agents
- **[MLFlow Documentation](https://mlflow.org/docs/latest/index.html)** - Official MLFlow docs
- **[SuperOptiX CLI Reference](../reference/cli.md)** - CLI commands reference

## 🎯 Next Steps

1. **Set up MLFlow server** for your environment
2. **Configure agent playbooks** with MLFlow integration
3. **Monitor agent performance** through MLFlow UI
4. **Set up alerts** for performance degradation
5. **Scale to production** with robust MLFlow deployment

---

**Ready to track your SuperOptiX agents with MLFlow? Start with the basic setup and scale up as needed! 🚀** 