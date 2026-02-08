# 📊 SuperOptiX Observability & Tracing Guide

Welcome to the comprehensive guide for SuperOptiX's observability and monitoring system! This guide combines the complete overview, real-world experiment, and quick reference for monitoring, debugging, and analyzing your AI agents using the `super observe` command.

## 🎯 Overview

SuperOptiX provides a powerful observability system that automatically traces agent execution, tool usage, LLM calls, and performance metrics. The observability system helps you:

- **Monitor** agent performance in real-time
- **Debug** issues with detailed trace analysis
- **Analyze** patterns and optimize agent behavior
- **Track** tool usage and LLM interactions
- **Export** trace data for external analysis

## 🚀 Quick Start

Let's walk through a complete example of setting up observability for an agent:

### Step 1: Initialize a Project and Create an Agent

```bash
# Initialize a new SuperOptiX project
super init my_project
cd my_project

# Pull a pre-built agent (Genies tier for full observability features)
super agent pull developer

# Compile the agent to generate the pipeline
super agent compile developer
```

### Step 2: Run the Agent to Generate Traces

```bash
# Run the agent - this automatically enables tracing
super agent run developer --goal "Write a simple Python function to calculate the factorial of a number"
```

The agent execution automatically generates trace files in `.superoptix/traces/` with detailed information about:
- Model initialization
- Tool setup and execution
- Pipeline execution flow
- Performance metrics
- Error handling

### Step 3: Explore Observability Features

```bash
# List all agents with available traces
super observe list

# View traces for a specific agent
super observe traces developer_20250714_200501

# Launch the interactive dashboard
super observe dashboard --auto-open

# Analyze performance metrics
super observe analyze developer_20250714_200501 --days 1
```

## 📋 Available Commands

### `super observe list` - List Agents with Traces

Lists all agents that have generated trace files in your project.

```bash
super observe list
```

**Output Example:**
```
📋 Available Agents with Traces

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Agent ID                  ┃ Trace Count ┃ Last Activity       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ developer                 │ 2           │ 2025-07-14 20:05:11 │
│ developer_20250714_200501 │ 11          │ 2025-07-14 20:05:11 │
└───────────────────────────┴─────────────┴─────────────────────┘
```

### `super observe traces` - View Agent Traces

View detailed execution traces for a specific agent.

```bash
# Basic trace view
super observe traces <agent_id>

# Detailed analysis with tool and LLM information
super observe traces <agent_id> --detailed --show-tools --show-llm

# Filter by component or status
super observe traces <agent_id> --component pipeline --status success

# Export traces to JSON or CSV
super observe traces <agent_id> --export json --output traces.json
```

**Options:**
- `--component`: Filter traces by component (pipeline, tool, execution, etc.)
- `--status`: Filter by status (success, error, warning, info)
- `--limit`: Limit number of traces shown (default: 100)
- `--detailed`: Show detailed trace analysis
- `--show-tools`: Show tool execution details
- `--show-llm`: Show LLM call details
- `--export`: Export format (json, csv)
- `--output`: Output file path

**Output Example:**
```
🔍 Loading traces for agent: developer_20250714_200501
Loaded 11 trace events
              Traces for Agent: developer_20250714_200501               
┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ Time     ┃ Component ┃ Event                   ┃ Status  ┃ Duration  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 20:05:01 │ pipeline  │ model_initialized       │ success │ -         │
│ 20:05:01 │ pipeline  │ tools_setup_start       │ success │ -         │
│ 20:05:01 │ pipeline  │ tools_initialized       │ success │ -         │
│ 20:05:01 │ pipeline  │ tools_setup_end         │ success │ 0.5ms     │
│ 20:05:01 │ pipeline  │ react_agent_initialized │ success │ -         │
│ 20:05:01 │ execution │ pipeline_forward_start  │ success │ -         │
│ 20:05:05 │ tool      │ calculate_start         │ success │ -         │
│ 20:05:05 │ calculate │ tool_execution_success  │ success │ -         │
│ 20:05:05 │ tool      │ calculate_end           │ success │ 0.1ms     │
│ 20:05:11 │ pipeline  │ execution_completed     │ success │ -         │
│ 20:05:11 │ execution │ pipeline_forward_end    │ success │ 10270.0ms │
└──────────┴───────────┴─────────────────────────┴─────────┴───────────┘

📊 Total: 11 | Errors: 0 | Avg: 3423.5ms
```

### `super observe dashboard` - Launch Interactive Dashboard

Launch a web-based dashboard for real-time monitoring and analysis.

```bash
# Launch dashboard with default settings
super observe dashboard

# Launch with custom port and auto-open browser
super observe dashboard --port 8502 --host localhost --auto-open

# Monitor a specific agent
super observe dashboard --agent-id developer_20250714_200501
```

**Options:**
- `--port`: Dashboard port (default: 8501)
- `--host`: Dashboard host (default: localhost)
- `--auto-open`: Automatically open browser
- `--agent-id`: Monitor specific agent

The dashboard provides:
- Real-time trace visualization
- Performance metrics and charts
- Tool usage analytics
- Error tracking and debugging
- Memory and context analysis

### `super observe analyze` - Performance Analysis

Analyze agent performance over time and generate insights.

```bash
# Analyze last 7 days (default)
super observe analyze <agent_id>

# Analyze specific time period
super observe analyze <agent_id> --days 30
```

**Output Example:**
```
📊 Performance Summary for Agent: developer_20250714_200501
 Total Events              11         
 Successful Events         11         
 Error Events              0          
 Warning Events            0          
 Average Duration          3423.5 ms  
 Median Duration           0.5 ms     
 95th Percentile Duration  10270.0 ms 
```

### `super observe check` - Trace Configuration Check

Check pipeline tracing configuration and verify trace generation.

```bash
# Check trace configuration
super observe check

# Check with test run
super observe check --agent-id <agent_id> --run-test

# Check DSPy configuration
super observe check --check-dspy
```

**Options:**
- `--agent-id`: Test specific agent
- `--run-test`: Run a test agent execution
- `--check-dspy`: Check DSPy configuration

### `super observe debug` - Interactive Debugging

Start an interactive debugging session for an agent.

```bash
# Start debug session
super observe debug agent <agent_id>

# Enable step-by-step debugging
super observe debug agent <agent_id> --enable-step-mode

# Break on errors or memory operations
super observe debug agent <agent_id> --break-on-error --break-on-memory
```

**Debug Commands:**
- `help`: Show available commands
- `continue`: Continue execution
- `step`: Step through execution
- `breakpoint <component>`: Set breakpoint
- `inspect`: Inspect current state
- `memory`: View memory contents
- `trace`: Show execution trace
- `export`: Export debug data

## 📊 Trace Data Structure

SuperOptiX generates comprehensive trace data in JSONL format. Each trace event contains:

```json
{
  "event_id": "unique-event-identifier",
  "timestamp": "2025-07-14T20:05:01.215246",
  "event_type": "model_initialized",
  "component": "pipeline",
  "data": {
    "model": "llama3.1:8b",
    "provider": "ollama",
    "tier": "genies",
    "adapter": "ChatAdapter"
  },
  "parent_id": null,
  "duration_ms": null,
  "status": "success",
  "metadata": null
}
```

**Event Types:**
- `model_initialized`: Model setup and configuration
- `tools_setup_start/end`: Tool initialization
- `tools_initialized`: Tool registration
- `react_agent_initialized`: ReAct agent setup
- `pipeline_forward_start/end`: Main execution flow
- `calculate_start/end`: Tool execution
- `tool_execution_success`: Tool results
- `execution_completed`: Pipeline completion

**Components:**
- `pipeline`: Core pipeline operations
- `execution`: Main execution flow
- `tool`: Tool execution
- `calculate`: Calculator tool
- `text_analyzer`: Text analysis tool
- `file_reader`: File reading tool

## 🔬 Real-World Experiment: Developer Agent

This section documents our comprehensive experiment with the SuperOptiX observability system using a developer agent.

### 🎯 Experiment Overview

**Goal**: Document and demonstrate the `super observe` command functionality by creating a test agent, running it, and analyzing the generated traces.

**Agent Used**: Developer Assistant (Genies tier)
**Task**: Write a simple Python function to calculate the factorial of a number

### 🚀 Experiment Steps

#### Step 1: Project Initialization

```bash
# Initialize a new SuperOptiX project
super init swe
cd swe
```

**Result**: Created a new SuperOptiX project with the `.super` file marker.

#### Step 2: Agent Creation

```bash
# Pull a pre-built developer agent with Genies tier
super agent pull developer
```

**Result**: Successfully added the Developer Assistant agent with:
- **Name**: Developer Assistant
- **Industry**: Software
- **Tier**: Genies
- **Features**: ReAct Agents + Tools + Memory
- **Location**: `swe/agents/developer/playbook/developer_playbook.yaml`

#### Step 3: Agent Compilation

```bash
# Compile the agent to generate executable pipeline
super agent compile developer
```

**Result**: Generated a Genies-tier pipeline with:
- **Framework**: DSPy (Mixin template)
- **Features**: ReAct, Tools, RAG Support, Memory
- **Output**: `swe/agents/developer/pipelines/developer_pipeline.py`
- **BDD Scenarios**: 5 found for testing

#### Step 4: Agent Execution

```bash
# Run the agent with a specific goal
super agent run developer --goal "Write a simple Python function to calculate the factorial of a number"
```

**Result**: Agent executed successfully with:
- **Agent ID**: `developer_20250714_200501`
- **Model**: `llama3.1:8b` (Ollama backend)
- **Tools**: 3 tools configured (calculator, text_analyzer, file_reader)
- **Execution Time**: 10.27 seconds
- **Status**: Success 
### 📊 Trace Analysis Results

#### Trace File Generation

The agent execution automatically generated trace files in `.superoptix/traces/`:

```
📁 Trace Files Generated:
├── .superoptix/traces/developer_20250714_200501.jsonl (4057 bytes)
└── .superoptix/traces/developer.jsonl (960 bytes)
```

#### Key Trace Events Observed

1. **Model Initialization**: `model_initialized` - Model setup with Ollama backend
2. **Tool Setup**: `tools_setup_start/end` - Tool initialization (0.5ms)
3. **Tool Registration**: `tools_initialized` - 3 tools registered
4. **ReAct Setup**: `react_agent_initialized` - ReAct agent configuration
5. **Execution Start**: `pipeline_forward_start` - Main execution begins
6. **Tool Execution**: `calculate_start/end` - Calculator tool used (0.1ms)
7. **Execution Complete**: `pipeline_forward_end` - Total execution (10270ms)

#### Performance Insights

- **Total execution time**: 10.27 seconds
- **Tool execution time**: 0.1ms (calculator tool)
- **Setup overhead**: 0.5ms for tool initialization
- **LLM processing**: Majority of time spent in LLM inference

### 🎯 Key Findings

#### Automatic Tracing
- **Tracing is automatic**: No manual configuration required
- **Comprehensive coverage**: Captures model, tools, execution, and performance data
- **Structured format**: JSONL format for easy parsing and analysis

#### Rich Trace Data
- **Event hierarchy**: Parent-child relationships between events
- **Timing information**: Precise duration measurements
- **Component separation**: Clear separation of pipeline, execution, and tool events
- **Status tracking**: Success, error, warning, and info statuses

#### Tool Usage Analysis
- **Tools used**: Calculator tool attempted (with syntax error)
- **Tool integration**: Seamless integration with ReAct framework
- **Error handling**: Graceful handling of tool execution errors

## ⚡ Quick Reference

### 🚀 Essential Commands

#### List Agents with Traces
```bash
super observe list
```

#### View Agent Traces
```bash
# Basic trace view
super observe traces <agent_id>

# Detailed analysis
super observe traces <agent_id> --detailed --show-tools --show-llm

# Filter by component
super observe traces <agent_id> --component pipeline

# Export traces
super observe traces <agent_id> --export json --output traces.json
```

#### Launch Dashboard
```bash
# Default dashboard
super observe dashboard

# Custom port and auto-open
super observe dashboard --port 8502 --auto-open

# Monitor specific agent
super observe dashboard --agent-id <agent_id>
```

#### Performance Analysis
```bash
# Analyze last 7 days (default)
super observe analyze <agent_id>

# Analyze specific period
super observe analyze <agent_id> --days 30
```

#### Debug Agent
```bash
# Start debug session
super observe debug agent <agent_id>

# Step-by-step debugging
super observe debug agent <agent_id> --enable-step-mode

# Break on errors
super observe debug agent <agent_id> --break-on-error
```

#### Check Configuration
```bash
# Check trace configuration
super observe check

# Test with specific agent
super observe check --agent-id <agent_id> --run-test
```

### 📋 Command Options Summary

#### `super observe traces` Options
- `--component`: Filter by component (pipeline, tool, execution)
- `--status`: Filter by status (success, error, warning, info)
- `--limit`: Limit number of traces (default: 100)
- `--detailed`: Show detailed analysis
- `--show-tools`: Show tool execution details
- `--show-llm`: Show LLM call details
- `--export`: Export format (json, csv)
- `--output`: Output file path

#### `super observe dashboard` Options
- `--port`: Dashboard port (default: 8501)
- `--host`: Dashboard host (default: localhost)
- `--auto-open`: Automatically open browser
- `--agent-id`: Monitor specific agent

#### `super observe analyze` Options
- `--days`: Number of days to analyze (default: 7)

#### `super observe debug` Options
- `--enable-step-mode`: Enable step-by-step debugging
- `--break-on-error`: Break on error
- `--break-on-memory`: Break on memory operations

### 🔍 Debug Commands

Once in debug mode:
- `help`: Show available commands
- `continue`: Continue execution
- `step`: Step through execution
- `breakpoint <component>`: Set breakpoint
- `inspect`: Inspect current state
- `memory`: View memory contents
- `trace`: Show execution trace
- `export`: Export debug data

### 🎯 Common Event Types

- `model_initialized`: Model setup
- `tools_setup_start/end`: Tool initialization
- `tools_initialized`: Tool registration
- `react_agent_initialized`: ReAct setup
- `pipeline_forward_start/end`: Main execution
- `calculate_start/end`: Tool execution
- `tool_execution_success`: Tool results
- `execution_completed`: Pipeline completion

### 🔧 Common Components

- `pipeline`: Core pipeline operations
- `execution`: Main execution flow
- `tool`: Tool execution
- `calculate`: Calculator tool
- `text_analyzer`: Text analysis tool
- `file_reader`: File reading tool

## 🔧 Advanced Features

### External Tracing Integrations

SuperOptiX supports integration with external tracing systems:

- **MLflow**: For experiment tracking and model management
- **Langfuse**: For LLM application monitoring
- **Custom tracers**: Extensible tracing framework

### Performance Monitoring

The observability system tracks:
- Execution duration and timing
- Tool usage patterns
- LLM call performance
- Error rates and types
- Memory usage trends
- Component-specific metrics

### Debugging Capabilities

- **Step-by-step execution**: Walk through agent execution
- **Breakpoints**: Set breakpoints on specific components
- **State inspection**: Examine agent state at any point
- **Memory analysis**: View memory contents and operations
- **Error tracking**: Detailed error analysis and debugging

## 🎯 Best Practices

### Enable Tracing for All Agents

Always run agents with tracing enabled to capture comprehensive execution data:

```bash
# Tracing is automatically enabled for all agent runs
super agent run <agent_id> --goal "your goal"
```

### Regular Performance Analysis

Schedule regular performance analysis to identify optimization opportunities:

```bash
# Weekly performance review
super observe analyze <agent_id> --days 7

# Monthly trend analysis
super observe analyze <agent_id> --days 30
```

### Monitor Tool Usage

Track tool usage patterns to optimize agent capabilities:

```bash
# View tool execution details
super observe traces <agent_id> --show-tools --detailed
```

### Debug Production Issues

Use the debugging system to troubleshoot production problems:

```bash
# Interactive debugging session
super observe debug agent <agent_id> --break-on-error
```

### Export Trace Data

Export trace data for external analysis and reporting:

```bash
# Export to JSON for analysis
super observe traces <agent_id> --export json --output analysis.json

# Export to CSV for spreadsheet analysis
super observe traces <agent_id> --export csv --output data.csv
```

## 🚨 Troubleshooting

### No Traces Found

If you don't see any traces:

1. **Verify agent execution**: Ensure the agent has been run at least once
2. **Check project structure**: Make sure you're in a SuperOptiX project directory
3. **Verify trace directory**: Check `.superoptix/traces/` for trace files
4. **Run trace check**: Use `super observe check` to diagnose issues

### Dashboard Not Starting

If the dashboard fails to start:

1. **Check port availability**: Ensure port 8501 (or your chosen port) is free
2. **Verify Streamlit installation**: Install with `pip install streamlit`
3. **Check permissions**: Ensure write access to `/tmp/` directory
4. **Review logs**: Check for error messages in the console output

### Performance Issues

If you experience performance problems:

1. **Limit trace data**: Use `--limit` to reduce trace output
2. **Filter traces**: Use `--component` and `--status` filters
3. **Export selectively**: Export only necessary data
4. **Monitor disk usage**: Clean up old trace files periodically

## 📈 Performance Metrics

### Key Metrics to Monitor
- **Total Events**: Number of trace events
- **Success Rate**: Percentage of successful events
- **Error Rate**: Percentage of error events
- **Average Duration**: Mean execution time
- **95th Percentile**: Performance threshold
- **Tool Usage**: Frequency of tool calls
- **LLM Calls**: Number of model interactions

### Typical Values
- **Setup Time**: 0.1-1.0ms
- **Tool Execution**: 0.1-10ms
- **LLM Processing**: 1-30 seconds
- **Total Execution**: 1-60 seconds

## 🎉 Quick Start Workflow

1. **Run an agent** to generate traces:
   ```bash
   super agent run <agent_id> --goal "your task"
   ```

2. **List available traces**:
   ```bash
   super observe list
   ```

3. **View traces** for analysis:
   ```bash
   super observe traces <agent_id> --detailed
   ```

4. **Launch dashboard** for monitoring:
   ```bash
   super observe dashboard --auto-open
   ```

5. **Analyze performance**:
   ```bash
   super observe analyze <agent_id> --days 7
   ```

6. **Debug issues** if needed:
   ```bash
   super observe debug agent <agent_id> --break-on-error
   ```

## 📚 Related Documentation

- [Agent Development Guide](agent-development.md) - Learn how to create and customize agents
- [Tool Development Guide](tool-development.md) - Build custom tools for your agents
- [Memory System Guide](memory.md) - Understand agent memory and context management
- [Evaluation and Testing Guide](evaluation-testing.md) - Test and validate your agents
- [CLI Reference](../reference/cli.md) - Complete CLI command reference

## 🎉 Conclusion

The SuperOptiX observability system provides comprehensive monitoring, debugging, and analysis capabilities for your AI agents. By following this guide, you can effectively monitor agent performance, debug issues, and optimize your agentic AI workflows.

Start exploring your agents today with `super observe list` and discover the power of comprehensive AI observability! 🚀
 