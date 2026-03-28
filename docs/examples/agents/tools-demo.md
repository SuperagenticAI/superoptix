# 🛠️ Tools Demo Agent

The Tools Demo Agent showcases **comprehensive tool integration** capabilities in SuperOptiX. This demo focuses specifically on how to configure and use tools across multiple categories for enhanced agent functionality.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🛠️ **Tool Integration**: How to configure tools in SuperOptiX agents
- 📦 **Multi-Category Tools**: Access to tools across 20+ categories
- ⚡ **Tool Execution**: How agents use tools to perform tasks
- ⚙️ **Playbook Configuration**: How to set up tools in agent playbooks

## 🚀 **Setup Tools Demo**

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
# Pull the Tools demo agent
super agent pull tools_demo

# Compile the agent
super agent compile tools_demo

# Run the agent
super agent run tools_demo --goal "What tools are available and how do they work?"
```

## 🔧 **Tools Configuration in Playbook**

The Tools demo showcases how to configure tools in the agent playbook:

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

### **Tools Configuration**
```yaml
tools:
  enabled: true
  categories:
  - development
  - core
  - utilities
  - education
  - finance
  - health
  - marketing
  - research
  specific_tools:
  - calculator
  - file_reader
  - text_analyzer
  - web_search
  - date_time
  - json_processor
  - code_formatter
  - image_analyzer
  - weather_checker
  - currency_converter
```

**Key Tools Configuration Points**:

- **`enabled: true`**: Enables tool functionality
- 📂 **`categories`**: Tool categories to include
- 🔧 **`specific_tools`**: Individual tools to enable
- 🏷️ **Tool Categories**: development, core, utilities, education, finance, health, marketing, research



## 🛠️ **Your AI's Swiss Army Knife**

SuperOptiX provides access to a comprehensive toolkit that transforms your AI agent into a multi-talented assistant. From basic utilities to specialized industry tools:

### **🔧 Core Capabilities**
- **🧮 Calculator**: Complex mathematical operations and financial calculations
- **📄 File Reader**: Read, analyze, and process any text-based files
- **🔍 Text Analyzer**: Sentiment analysis, entity extraction, and text processing
- **🌐 Web Search**: Real-time information retrieval from the internet
- **📅 Date & Time**: Calendar operations, scheduling, and time calculations

### **🎯 Specialized Domains**
- **💼 Finance**: Investment analysis, market data, and financial planning
- **🏥 Healthcare**: Medical information, health metrics, and wellness tools
- **📚 Education**: Learning assistance, content creation, and educational resources
- **📈 Marketing**: Campaign analysis, SEO tools, and social media management
- **🔬 Research**: Data analysis, research assistance, and academic tools

## 🔧 **Customizing Tools Configuration**

### **Enable Specific Categories**
Edit `agents/tools_demo/playbook/tools_demo_playbook.yaml`:

```yaml
tools:
  categories:
  - development
  - core
  - utilities
  - your_custom_category
```

### **Enable Specific Tools**
```yaml
tools:
  specific_tools:
  - calculator
  - file_reader
  - your_custom_tool
```

### **Disable Tools**
```yaml
tools:
  enabled: false  # Disable all tools
```

## 🚨 **Troubleshooting Tools**

### **Common Issues**

1. **Ollama Server Not Running**
   ```bash
   # Check if Ollama server is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama server
   ollama serve
   ```

2. **Tools Not Working**
   ```bash
   # Check tools configuration
   super agent inspect tools_demo
   
   # Verify tools are enabled
   ```

3. **Tool Execution Errors**
   ```bash
   # Check agent logs
   super agent logs tools_demo
   
   # Verify tool dependencies
   ```

### **Getting Help**
```bash
# Check agent status
super agent inspect tools_demo

# View agent logs
super agent logs tools_demo

# Get tools help
super agent --help
```

## 📚 Related Documentation

- [Tool Development](../../guides/tool-development.md) - Building custom tools
- [Tool Categories](../../reference/api/tools.md) - Available tool categories
- [Agent Development](../../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other Framework Features**: Explore [Memory](memory-demo.md) or [Observability](observability-demo.md) demos 