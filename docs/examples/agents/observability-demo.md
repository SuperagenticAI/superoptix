# 📊 Observability Demo Agent

The Observability Demo Agent showcases **monitoring and debugging** capabilities in SuperOptiX. This demo focuses specifically on how to configure and use observability features for monitoring, tracing, and debugging agent performance.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 📊 **Observability Integration**: How to configure observability in SuperOptiX agents
- 📈 **Performance Monitoring**: Real-time monitoring and metrics
- 🐛 **Debugging Capabilities**: Tracing and debugging tools
- ⚙️ **Playbook Configuration**: How to set up observability in agent playbooks

## 🚀 **Setup Observability Demo**

### **1. Install Ollama Model**

```bash
# Install the Ollama model used in this demo
super model install qwen3.5:9b
```

### **2. Start Ollama Server**

```bash
# Start Ollama server (runs on port 11434 by default)
ollama serve
```

### **3. Pull and Run the Demo**

```bash
# Pull the Observability demo agent
super agent pull observability_demo

# Compile the agent
super agent compile observability_demo

# Run the agent
super agent run observability_demo --goal "What observability features are available and how do they work?"
```

## 🔧 **Observability Configuration in Playbook**

The Observability demo showcases how to configure observability in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: ollama
  model: qwen3.5:9b
  api_base: http://localhost:11434
  temperature: 0.7
  max_tokens: 2048
```

### **Observability Configuration**
```yaml
react_config:
  max_iters: 5
  max_tool_calls: 3
  tool_selection_strategy: automatic
  reasoning_style: step_by_step
  error_handling: retry
  enable_tracing: true
  enable_metrics: true
  enable_debugging: true
```

**Key Observability Configuration Points**:

- 🔍 **`enable_tracing: true`**: Enables request/response tracing
- 📊 **`enable_metrics: true`**: Enables performance metrics collection
- 🐛 **`enable_debugging: true`**: Enables debugging capabilities
- 🔄 **`error_handling: retry`**: Automatic error retry with logging
- 🧠 **`reasoning_style: step_by_step`**: Detailed reasoning logs

## 📊 **Observability: Your AI's Health Monitor**

Observability gives you complete visibility into your AI agent's performance, health, and behavior. It's like having a comprehensive monitoring system for your AI:

### **🔍 What You Can Monitor**
- **📈 Performance Metrics**: Real-time tracking of response times, throughput, and efficiency
- **🔍 Request Tracing**: Follow every request from start to finish through the system
- **🐛 Debugging Tools**: Step-by-step debugging to identify and fix issues
- **📊 Analytics Dashboard**: Visual insights into your AI's behavior and performance

### **🎯 Key Capabilities**
- **🚨 Proactive Alerting**: Get notified before problems become critical
- **📝 Comprehensive Logging**: Detailed logs for troubleshooting and analysis
- **🎛️ Performance Tuning**: Identify bottlenecks and optimize performance
- **🔧 Production Ready**: Built for monitoring AI systems in production environments

## 🔧 **Customizing Observability Configuration**

### **Adjust Tracing Settings**
Edit `agents/observability_demo/playbook/observability_demo_playbook.yaml`:

```yaml
react_config:
  enable_tracing: true
  enable_metrics: true
  enable_debugging: true
  trace_level: detailed  # More detailed tracing
```

### **Change Error Handling**
```yaml
react_config:
  error_handling: log_and_continue  # Different error handling strategy
  max_retries: 3  # Maximum retry attempts
```

### **Disable Observability Features**
```yaml
react_config:
  enable_tracing: false  # Disable tracing
  enable_metrics: true
  enable_debugging: true
```

## 🚨 **Troubleshooting Observability**

### **Common Issues**

1. **Ollama Server Not Running**
   ```bash
   # Check if Ollama server is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama server
   ollama serve
   ```

2. **Observability Not Working**
   ```bash
   # Check observability configuration
   super agent inspect observability_demo
   
   # Verify observability is enabled
   ```

3. **Performance Issues**
   ```bash
   # Check agent logs
   super agent logs observability_demo
   
   # Monitor performance metrics
   ```

### **Getting Help**
```bash
# Check agent status
super agent inspect observability_demo

# View agent logs
super agent logs observability_demo

# Get observability help
super agent --help
```

## 📚 Related Documentation

- [Observability Guide](../../guides/observability.md) - Complete observability setup and usage
- [Debugging Guide](../../debugging-guide.md) - Debugging techniques and tools
- [Agent Development](../../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other Framework Features**: Explore [Tools](tools-demo.md) or [Memory](memory-demo.md) demos 