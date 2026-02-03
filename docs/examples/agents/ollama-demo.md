# 🦙 Ollama Demo Agent

The Ollama Demo Agent showcases **easy local model management** with Ollama in SuperOptiX. This demo focuses specifically on how to configure and use Ollama models for simple, reliable local inference.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🦙 **Ollama Model Integration**: How to configure Ollama models in SuperOptiX
- 🚀 **Easy Model Management**: Simple model installation and management
- 🏠 **Local Model Usage**: Running models completely offline
- ⚙️ **Playbook Configuration**: How to set up Ollama in agent playbooks

## 🚀 **Setup Ollama Model**

### **1. Install Ollama**

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai/download for Windows
```

### **2. Install Ollama Model**

```bash
# Install the Ollama model used in this demo
super model install llama3.2:8b
```

### **3. Start Ollama Server**

```bash
# Start Ollama server (runs on port 11434 by default)
ollama serve
```

### **4. Pull and Run the Demo**

```bash
# Pull the Ollama demo agent
super agent pull ollama_demo

# Compile the agent
super agent compile ollama_demo

# Run the agent
super agent run ollama_demo --goal "What are the key features of Ollama?"
```

## 🔧 **Ollama Configuration in Playbook**

The Ollama demo showcases how to configure Ollama models in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: ollama
  model: llama3.2:8b
  api_base: http://localhost:11434
  temperature: 0.7
  max_tokens: 2048
```

**Key Configuration Points**:

- 🎯 **`provider: ollama`**: Specifies Ollama as the model backend
- 🤖 **`model`**: The Ollama model identifier
- 🌐 **`api_base`**: Ollama server endpoint (default: http://localhost:11434)
- 🌡️ **`temperature`**: Controls response creativity (0.7 = balanced)
- 📏 **`max_tokens`**: Maximum response length



## 🦙 **The Ollama Advantage**

Ollama makes local AI accessible to everyone. It's the simplest way to run powerful language models on your own machine:

- **🎯 One Command Setup**: Install any model with a single command
- **🔄 Seamless Updates**: Models update automatically in the background
- **🌍 Cross-Platform**: Works perfectly on macOS, Linux, and Windows
- **🏠 True Local**: Runs completely offline once installed
- **⚡ Lightning Fast**: Optimized for your local hardware
- **💡 Beginner Friendly**: Perfect for newcomers to local AI

## 🔧 **Customizing Ollama Configuration**

### **Change Model**
Edit `agents/ollama_demo/playbook/ollama_demo_playbook.yaml`:

```yaml
language_model:
  model: llama3.2:3b  # Different Ollama model
  api_base: http://localhost:11434
```

### **Adjust Performance Settings**
```yaml
language_model:
  temperature: 0.9  # More creative responses
  max_tokens: 4096  # Longer responses
```

### **Use Different Port**
```yaml
language_model:
  api_base: http://localhost:8080  # Custom port
```

## 🚨 **Troubleshooting Ollama**

### **Common Issues**

1. **Ollama Server Not Running**
   ```bash
   # Check if Ollama server is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama server
   ollama serve
   ```

2. **Model Not Installed**
   ```bash
   # Check installed Ollama models
   super model list --backend ollama
   
   # Install the required model
   super model install llama3.2:8b
   ```

3. **Performance Issues**
   - Ensure sufficient RAM (8GB+ recommended)
   - Close other resource-intensive applications
   - Consider using smaller models for faster responses

### **Getting Help**
```bash
# Check agent status
super agent inspect ollama_demo

# View agent logs
super agent logs ollama_demo

# Get Ollama help
ollama --help
```

## 📚 **Related Resources**

- [Ollama Setup Guide](../llm-setup.md#ollama-recommended) - Complete Ollama setup instructions
- [Model Management](../guides/model-management.md) - Managing Ollama models
- [Agent Development](../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other Model Backends**: Explore [MLX](mlx-demo), [HuggingFace](huggingface-demo), or [LM Studio](lmstudio-demo) demos 