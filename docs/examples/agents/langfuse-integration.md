# 🔍 LangFuse Integration

Learn how to integrate SuperOptiX with LangFuse for comprehensive LLM observability, tracing, and performance monitoring.

## 🎯 Overview

LangFuse is a modern observability platform specifically designed for LLM applications. This integration provides:

- **Real-time LLM tracing** with detailed token usage
- **Performance monitoring** and cost tracking
- **User feedback collection** and evaluation
- **A/B testing** for different agent configurations
- **Production debugging** with full trace visibility

## 🚀 Quick Setup

### Prerequisites

```bash
# Install LangFuse
pip install langfuse

# Install SuperOptiX with LangFuse support
pip install superoptix[langfuse]
```

### Basic Configuration

Create a configuration file `langfuse_config.yaml`:

```yaml
# langfuse_config.yaml
langfuse:
  public_key: "your-public-key"
  secret_key: "your-secret-key"
  host: "https://cloud.langfuse.com"  # or self-hosted URL
  
# SuperOptiX observability configuration
observability:
  enabled: true
  backends:
    - langfuse
  trace_export:
    format: "langfuse"
    batch_size: 50
```

## 🔧 Integration Setup

### Step 1: Set Up LangFuse

**Option A: LangFuse Cloud (Recommended)**
1. Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
2. Create a new project
3. Get your API keys from the project settings

**Option B: Self-Hosted LangFuse**
```bash
# Using Docker Compose
wget https://raw.githubusercontent.com/langfuse/langfuse/main/docker-compose.yml
docker-compose up -d
```

### Step 2: Configure SuperOptiX

Update your agent playbook to include LangFuse integration:

```yaml
# developer_playbook.yaml
name: "Developer Assistant"
description: "AI developer with LangFuse integration"
tier: "genies"

# ... existing configuration ...

observability:
  enabled: true
  backends:
    - langfuse
  langfuse:
    public_key: "your-public-key"
    secret_key: "your-secret-key"
    host: "https://cloud.langfuse.com"
    project: "superoptix-agents"
    tags:
      agent_type: "developer"
      tier: "genies"
      environment: "development"
```

### Step 3: Run Agent with LangFuse Tracking

```bash
# Set environment variables
export LANGFUSE_PUBLIC_KEY="your-public-key"
export LANGFUSE_SECRET_KEY="your-secret-key"

# Initialize project
super init langfuse_demo
cd langfuse_demo

# Pull and compile agent
super agent pull developer --tier genies
super agent compile developer

# Run with LangFuse tracking
super agent run developer --goal "Create a REST API endpoint in Python"
```

## 📊 LangFuse Integration Features

### Automatic LLM Tracing

SuperOptiX automatically captures detailed LLM interactions:

**Trace Structure:**
```json
{
  "id": "trace-123",
  "name": "developer_agent_execution",
  "input": {
    "goal": "Create a REST API endpoint in Python",
    "agent_config": {...}
  },
  "output": {
    "response": "Here's a Python REST API endpoint...",
    "generated_code": "..."
  },
  "metadata": {
    "agent_type": "developer",
    "tier": "genies",
    "model": "llama3.1:8b"
  }
}
```

**Span Details:**
- **Model calls** with token usage and costs
- **Tool executions** with input/output
- **Memory operations** with context retrieval
- **Pipeline steps** with timing information

### Performance Metrics

LangFuse tracks comprehensive performance data:

**LLM Metrics:**
- Token usage (input/output)
- Response time
- Cost per request
- Model performance

**Agent Metrics:**
- Tool usage frequency
- Memory hit rates
- Success/failure rates
- User satisfaction scores

## 🔍 Advanced Configuration

### Custom Trace Attributes

Add custom attributes to traces:

```yaml
observability:
  langfuse:
    custom_attributes:
      - name: "code_complexity"
        type: "number"
        description: "Complexity score of generated code"
      - name: "user_expertise"
        type: "string"
        description: "User expertise level"
      - name: "task_difficulty"
        type: "number"
        description: "Task difficulty rating"
```

### User Feedback Integration

Collect and track user feedback:

```yaml
observability:
  langfuse:
    feedback:
      enabled: true
      score_range: [1, 5]
      comment_enabled: true
      categories:
        - "accuracy"
        - "helpfulness"
        - "code_quality"
```

### A/B Testing Support

Configure A/B testing for different agent configurations:

```yaml
observability:
  langfuse:
    ab_testing:
      enabled: true
      variants:
        - name: "baseline"
          config:
            temperature: 0.7
            model: "llama3.1:8b"
        - name: "optimized"
          config:
            temperature: 0.5
            model: "llama3.1:70b"
```

## 📈 Monitoring and Analysis

### LangFuse Dashboard

Access the LangFuse dashboard for real-time monitoring:

```bash
# Open LangFuse dashboard
open https://cloud.langfuse.com
```

**Available Views:**
- **Traces**: Individual execution traces
- **Sessions**: User interaction sessions
- **Metrics**: Performance dashboards
- **Feedback**: User feedback analysis
- **Costs**: Token usage and cost tracking

### Custom Analytics

Use LangFuse API for custom analytics:

```python
from langfuse import Langfuse

# Initialize LangFuse client
langfuse = Langfuse(
    public_key="your-public-key",
    secret_key="your-secret-key"
)

# Query traces
traces = langfuse.get_traces(
    project_id="your-project-id",
    limit=100
)

# Analyze performance
for trace in traces:
    print(f"Trace: {trace.name}")
    print(f"Duration: {trace.duration}ms")
    print(f"Tokens: {trace.input_tokens + trace.output_tokens}")
    print(f"Cost: ${trace.cost}")
```

### Alerting and Notifications

Set up alerts for performance issues:

```python
# Example alerting script
def check_langfuse_alerts():
    traces = langfuse.get_traces(limit=10)
    
    for trace in traces:
        if trace.duration > 30000:  # 30 seconds
            send_alert(f"Slow execution: {trace.name}")
        
        if trace.cost > 0.10:  # $0.10
            send_alert(f"High cost execution: {trace.name}")
```

## 🔧 Troubleshooting

### Common Issues

**1. Authentication Errors**
```bash
# Verify API keys
curl -H "Authorization: Bearer your-secret-key" \
     https://cloud.langfuse.com/api/public/traces
```

**2. Connection Issues**
```bash
# Test LangFuse connection
python -c "
from langfuse import Langfuse
langfuse = Langfuse(public_key='your-key', secret_key='your-secret')
print('Connection successful')
"
```

**3. Missing Traces**
```yaml
# Enable debug logging
observability:
  langfuse:
    debug: true
    log_level: "DEBUG"
    flush_interval: 5  # seconds
```

### Debug Mode

Enable comprehensive debugging:

```yaml
observability:
  langfuse:
    debug: true
    log_level: "DEBUG"
    verbose: true
    test_mode: true  # For development
```

## 🚀 Production Deployment

### Environment Configuration

Set up production environment variables:

```bash
# Production environment
export LANGFUSE_PUBLIC_KEY="prod-public-key"
export LANGFUSE_SECRET_KEY="prod-secret-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"
export LANGFUSE_PROJECT="production-agents"
```

### Kubernetes Integration

Deploy with Kubernetes secrets:

```yaml
# langfuse-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: langfuse-credentials
type: Opaque
data:
  public-key: <base64-encoded-public-key>
  secret-key: <base64-encoded-secret-key>
```

### Load Balancing

For high-volume deployments:

```yaml
observability:
  langfuse:
    load_balancing:
      enabled: true
      batch_size: 100
      flush_interval: 10
      max_retries: 3
      retry_delay: 1
```

## 📊 Cost Tracking

### Token Usage Monitoring

Track and optimize token usage:

```python
# Cost analysis script
def analyze_costs():
    traces = langfuse.get_traces(limit=1000)
    
    total_cost = sum(trace.cost for trace in traces)
    total_tokens = sum(trace.input_tokens + trace.output_tokens for trace in traces)
    
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Cost per token: ${total_cost/total_tokens:.6f}")
```

### Cost Optimization

Implement cost optimization strategies:

```yaml
observability:
  langfuse:
    cost_optimization:
      enabled: true
      alerts:
        cost_threshold: 0.05  # $0.05 per request
        token_threshold: 2000  # 2000 tokens per request
      recommendations:
        enabled: true
        model_switching: true
        prompt_optimization: true
```

## 📚 Related Resources

- **[Observability Guide](../guides/observability.md)** - Complete observability overview
- **[Agent Development](../guides/agent-development.md)** - Build custom agents
- **[LangFuse Documentation](https://langfuse.com/docs)** - Official LangFuse docs
- **[SuperOptiX CLI Reference](../reference/cli.md)** - CLI commands reference

## 🎯 Next Steps

1. **Set up LangFuse account** and get API keys
2. **Configure agent playbooks** with LangFuse integration
3. **Monitor agent performance** through LangFuse dashboard
4. **Set up cost tracking** and optimization alerts
5. **Implement user feedback** collection
6. **Scale to production** with robust monitoring

---

**Ready to monitor your SuperOptiX agents with LangFuse? Start with the basic setup and unlock powerful LLM observability! 🚀** 