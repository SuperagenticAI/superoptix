# 🎮 LM Studio Demo Agent

The LM Studio Demo Agent showcases **GUI-based model management** with LM Studio in SuperOptiX. This demo focuses specifically on how to configure and use LM Studio models with a visual interface for model management.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🎮 **LM Studio Model Integration**: How to configure LM Studio models in SuperOptiX
- 🖥️ **GUI Model Management**: Visual interface for model management
- 🏠 **Local Model Usage**: Running models completely offline
- ⚙️ **Playbook Configuration**: How to set up LM Studio in agent playbooks

## 🚀 **Setup LM Studio Model**

### **1. Install LM Studio**

```bash
# Download and install LM Studio from https://lmstudio.ai
# Launch LM Studio and download a model through the interface
```

### **2. Install LM Studio Model**

```bash
# Install the LM Studio model used in this demo
super model install -b lmstudio qwen2.5-7b-instruct
```

### **3. Start LM Studio Server**

```bash
# Start LM Studio server on port 1234
super model server lmstudio qwen2.5-7b-instruct --port 1234
```

### **4. Pull and Run the Demo**

```bash
# Pull the LM Studio demo agent
super agent pull lmstudio_demo

# Compile the agent
super agent compile lmstudio_demo

# Run the agent
super agent run lmstudio_demo --goal "What are the key features of LM Studio?"
```

## 🔧 **LM Studio Configuration in Playbook**

The LM Studio demo showcases how to configure LM Studio models in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: lmstudio
  model: qwen2.5-7b-instruct
  api_base: http://localhost:1234
  temperature: 0.7
  max_tokens: 2048
```

**Key Configuration Points**:

- 🎯 **`provider: lmstudio`**: Specifies LM Studio as the model backend
- 🤖 **`model`**: The LM Studio model identifier
- 🌐 **`api_base`**: LM Studio server endpoint (default: http://localhost:1234)
- 🌡️ **`temperature`**: Controls response creativity (0.7 = balanced)
- 📏 **`max_tokens`**: Maximum response length

## 🎮 **LM Studio: Visual AI Management**

LM Studio brings the power of local AI with the simplicity of a graphical interface. Perfect for users who prefer visual tools:

- **🖥️ Visual Interface**: Beautiful GUI for managing models and conversations
- **📊 Real-time Monitoring**: Watch your model's performance in real-time
- **🎯 Easy Model Selection**: Browse and select models with a visual interface
- **🖱️ Point-and-Click**: No command line required for basic operations
- **🪟 Windows Native**: Optimized for Windows users with familiar interface
- **🍎 macOS Support**: Also works great on macOS systems

## 🔧 **Customizing LM Studio Configuration**

### **Change Model**
Edit `agents/lmstudio_demo/playbook/lmstudio_demo_playbook.yaml`:

```yaml
language_model:
  model: qwen2.5-3b-instruct  # Different LM Studio model
  api_base: http://localhost:1234
```

### **Adjust Performance Settings**
```yaml
language_model:
  temperature: 0.5  # More precise responses
  max_tokens: 4096  # Longer responses
```

### **Use Different Port**
```yaml
language_model:
  api_base: http://localhost:8080  # Custom port
```

## 🚨 **Troubleshooting LM Studio**

### **Common Issues**

1. **LM Studio Server Not Running**
   ```bash
   # Check if LM Studio server is running
   curl http://localhost:1234/v1/models
   
   # Start LM Studio server
   super model server lmstudio qwen3.5:9b --port 1234
   ```

2. **Model Not Installed**
   ```bash
   # Check installed LM Studio models
   super model list --backend lmstudio
   
   # Install the required model
   super model install -b lmstudio qwen3.5:9b
   ```

3. **Performance Issues**
   - Ensure sufficient RAM (8GB+ recommended)
   - Close other resource-intensive applications
   - Consider using smaller models for faster responses

### **Getting Help**
```bash
# Check agent status
super agent inspect lmstudio_demo

# View agent logs
super agent logs lmstudio_demo

# Get LM Studio help
super model server --help
```

## 📚 **Related Resources**

- [LM Studio Setup Guide](../../llm-setup.md#lm-studio) - Complete LM Studio setup instructions
- [Model Management](../../guides/model-management.md) - Managing LM Studio models
- [Agent Development](../../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other Model Backends**: Explore [MLX](mlx-demo.md), [Ollama](ollama-demo.md), or [HuggingFace](huggingface-demo.md) demos

---

**Ready to explore GUI model management? Start with the LM Studio demo! 🚀** 
