# 🧪 MLFlow Integration Guide for SuperOptiX

This guide documents a complete, real-world workflow for integrating MLFlow with SuperOptiX, including all commands, troubleshooting, and actual outputs.

---

## Install MLFlow

```bash
pip install mlflow
```

**Output:**
```
Requirement already satisfied: mlflow in /Users/local/miniconda3/lib/python3.12/site-packages (3.1.1)
... (truncated for brevity)
Successfully installed cachetools-5.5.2
```

---

## Start the MLFlow Server

```bash
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts
```

**If you see an error about the port being in use:**
```
[ERROR] Connection in use: ('0.0.0.0', 5000)
[ERROR] connection to ('0.0.0.0', 5000) failed: [Errno 48] Address already in use
Running the mlflow server failed. Please see the logs above for details.
```

**Solution:** Use a different port (e.g., 5001):

```bash
mlflow server --host 0.0.0.0 --port 5001 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts
```

**Output:**
```
[INFO] Listening at: http://0.0.0.0:5001 (3817)
[INFO] Using worker: sync
[INFO] Booting worker with pid: ...
```

---

## Initialize a SuperOptiX Project

```bash
super init mlflow_demo
cd mlflow_demo
```

**Output:**
```
🎉 SUCCESS! Your full-blown shippable Agentic System 'mlflow_demo' is ready!
... (truncated)
```

---

## Pull and Compile a Developer Agent

```bash
super agent pull developer
super agent compile developer
```

**Output:**
```
🎉 AGENT ADDED SUCCESSFULLY! Pre-built Agent Ready
... (truncated)
🎉 COMPILATION SUCCESSFUL! Pipeline Generated
... (truncated)
```

---

## Add MLFlow Observability to the Playbook

Edit `mlflow_demo/mlflow_demo/agents/developer/playbook/developer_playbook.yaml` and add:

```yaml
observability:
  enabled: true
  backends:
    - mlflow
  mlflow:
    experiment_name: "developer_agent"
    tracking_uri: "http://localhost:5001"
    log_artifacts: true
    log_metrics: true
    log_params: true
    tags:
      agent_type: "developer"
      tier: "genies"
      version: "1.0.0"
      environment: "development"
```

---

## Run the Agent

```bash
super agent run developer --goal "Write a Python function to calculate the factorial of a number with proper error handling"
```

**Output:**
```
🚀 Running agent 'developer'...
... (truncated)
🎉 Agent execution completed successfully!
```

---

## Check Trace Files

```bash
ls -la .superoptix/traces/
```

**Output:**
```
-rw-r--r--@ 1 shashi  staff  1018 ... developer.jsonl
-rw-r--r--@ 1 shashi  staff  9626 ... developer_20250714_204941.jsonl
```

---

## View Traces with SuperOptiX CLI

```bash
super observe list
super observe traces developer_20250714_204941 --detailed
```

**Output:**
```
📋 Available Agents with Traces
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Agent ID                  ┃ Trace Count ┃ Last Activity       ┃
... (truncated)
Loaded 23 trace events
📊 TRACE ANALYSIS SUMMARY
... (truncated)
```

---

## Test MLFlow Logging with Python

Create `test_mlflow_integration.py`:

```python
import mlflow
import json
from datetime import datetime
mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("superoptix_mlflow_test")
with mlflow.start_run(run_name="superoptix_test_run") as run:
    mlflow.log_param("agent_name", "developer")
    mlflow.log_metric("execution_time_ms", 15766.66)
    mlflow.set_tag("test_run", "true")
    trace_data = {"event_id": "test_event_123", "timestamp": datetime.now().isoformat()}
    with open("test_trace.json", "w") as f:
        json.dump(trace_data, f, indent=2)
    mlflow.log_artifact("test_trace.json")
```

**Run it:**
```bash
python test_mlflow_integration.py
```

**Output:**
```
🧪 SuperOptiX MLFlow Integration Test
MLFlow server is running and accessible
... (truncated)
Successfully logged data to MLFlow run: ...
```

---

## Run the Full Demo Script

Create and run `demo_mlflow_superoptix.py` (see project for full code):

```bash
python demo_mlflow_superoptix.py
```

**Output:**
```
🧪 SuperOptiX + MLFlow Integration Demo
MLFlow server is accessible
🎯 Demo 1/3: Write a Python function to calculate the sum of two numbers
🤖 Running agent with goal: ...
Agent execution completed in ...ms
... (truncated)
🎉 Demo completed successfully!
📋 MLFlow UI: http://localhost:5001
```

---

## Access the MLFlow UI

Open your browser to:
```
http://localhost:5001
```

You’ll see all experiments, runs, metrics, parameters, and artifacts.

---

## Troubleshooting

- **Port in use:** Use a different port (e.g., 5001)
- **No runs in MLFlow UI:** Check playbook config and server status
- **Missing traces:** Check `.superoptix/traces/` and agent logs

---

## Summary

You now have:
- End-to-end MLFlow integration with SuperOptiX
- Real agent runs tracked in MLFlow
- Trace and artifact management
- Performance analysis and troubleshooting

---

**Ready to scale up? Use this workflow as a template for production ML observability!** 

---

## 🔄 Choosing Between MLFlow and LangFuse

Both MLFlow and LangFuse provide excellent observability for SuperOptiX agents, but they serve different use cases:

### 🧪 MLFlow - Best for:
- **ML Experiment Tracking**: Traditional ML workflows and experiments
- **Artifact Management**: Code, models, and data versioning
- **Reproducibility**: Detailed experiment tracking and comparison
- **Team Collaboration**: Experiment sharing and model registry
- **Production ML**: Model deployment and lifecycle management

### 🔍 LangFuse - Best for:
- **LLM Observability**: Specialized for language model applications
- **Real-time Tracing**: Detailed token usage and cost tracking
- **User Feedback**: Built-in feedback collection and scoring
- **A/B Testing**: LLM prompt and model comparison
- **Production LLM**: Live monitoring and debugging

### 📊 Quick Comparison

| Feature | MLFlow | LangFuse |
|---------|--------|----------|
| **Primary Focus** | ML Experiments | LLM Observability |
| **Token Tracking** | Manual | Automatic |
| **Cost Tracking** | Manual | Built-in |
| **User Feedback** | Manual | Native |
| **A/B Testing** | Manual | Built-in |
| **Real-time UI** | Limited | Excellent |
| **Artifact Storage** | Excellent | Good |
| **Experiment Tracking** | Excellent | Good |

### 🎯 When to Use Each

**Choose MLFlow if:**
- You're doing traditional ML experiments
- You need detailed artifact versioning
- You want to track model performance over time
- You're building ML pipelines

**Choose LangFuse if:**
- You're building LLM applications
- You need real-time cost tracking
- You want user feedback integration
- You're doing prompt engineering
- You need A/B testing for LLMs

---

## Understanding Local Files and Artifacts

### Project Structure After MLFlow Integration

```
SuperOptiX/
├── mlflow_demo/                # Your SuperOptiX demo project
│   ├── ...                     # Agent code, playbooks, pipelines, etc.
│   └── .superoptix/traces/     # JSONL trace files for each agent run
├── mlflow.db                   # SQLite database for MLFlow experiment tracking
├── mlflow_artifacts/           # Directory where MLFlow stores run artifacts (traces, code, outputs)
```

### What Each File/Folder Is For

- **mlflow_demo/**: Your SuperOptiX project, including agent configs and code.
- **mlflow_demo/.superoptix/traces/**: Raw trace files (JSONL) for every agent run. Useful for debugging, custom analytics, or exporting to other tools.
- **mlflow.db**: The MLFlow experiment tracking database (SQLite). All run metadata, parameters, metrics, and artifact references are stored here.
- **mlflow_artifacts/**: MLFlow’s artifact store. Each run gets a subfolder with all logged files (traces, generated code, outputs, etc.).

### Example: Listing and Inspecting Files

```bash
# List trace files for all agent runs
ls -lh mlflow_demo/.superoptix/traces/

# List all MLFlow artifacts for all runs
ls -lh mlflow_artifacts/*

# Inspect the MLFlow database (optional, advanced)
sqlite3 mlflow.db ".tables"
sqlite3 mlflow.db "SELECT * FROM runs LIMIT 3;"
```

### Downloading and Using Artifacts

- **From the MLFlow UI:**  
  Go to http://localhost:5001, select a run, and download any artifact (trace, code, output) directly from the web interface.

- **From the Filesystem:**  
  Artifacts are stored in `mlflow_artifacts/<run_id>/`. You can copy, analyze, or share these files as needed.

### Using Traces for Custom Analysis

You can load and analyze trace files (JSONL) with Python or any tool that supports JSONL:

```python
import json

with open('mlflow_demo/.superoptix/traces/developer_20250714_204941.jsonl') as f:
    for line in f:
        event = json.loads(line)
        print(event['event_type'], event['timestamp'])
```

---

## 📚 Related Resources

- **[Observability Guide](observability.md)** - Complete observability overview
- **[LangFuse Integration Guide](langfuse-integration.md)** - LangFuse observability integration
- **[Agent Development](agent-development.md)** - Build custom agents
- **[MLFlow Documentation](https://mlflow.org/docs/latest/index.html)** - Official MLFlow docs
- **[SuperOptiX CLI Reference](../reference/cli.md)** - CLI commands reference

--- 