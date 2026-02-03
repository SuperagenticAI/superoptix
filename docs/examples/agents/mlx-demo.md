# 🍎 MLX Demo Agent

The MLX Demo Agent showcases **Apple Silicon optimization** with MLX models in SuperOptiX. This demo focuses specifically on how to configure and use MLX models for native Apple Silicon performance.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🍎 **MLX Model Integration**: How to configure MLX models in SuperOptiX
- ⚡ **Apple Silicon Optimization**: Native performance on Apple Silicon Macs
- 🏠 **Local Model Usage**: Running models completely offline
- ⚙️ **Playbook Configuration**: How to set up MLX in agent playbooks

## 🚀 **Setup MLX Model**

### **1. Install MLX Dependencies**

```bash
# Install MLX dependencies
pip install "superoptix[mlx]"
```

### **2. Install MLX Model**

```bash
# Install the MLX model used in this demo
super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
```

### **3. Start MLX Server**

```bash
# Start MLX server on port 8000
super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000
```

### **4. Pull and Run the Demo**

```bash
# Pull the MLX demo agent
super agent pull mlx_demo

# Compile the agent
super agent compile mlx_demo

# Run the agent
super agent run mlx_demo --goal "What are the key features of MLX?"
```

## 🔧 **MLX Configuration in Playbook**

The MLX demo showcases how to configure MLX models in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: mlx
  model: mlx-community/Llama-3.2-3B-Instruct-4bit
  api_base: http://localhost:8000
  temperature: 0.7
  max_tokens: 2048
```

**Key Configuration Points**:

- 🎯 **`provider: mlx`**: Specifies MLX as the model backend
- 🤖 **`model`**: The MLX model identifier
- 🌐 **`api_base`**: MLX server endpoint (default: http://localhost:8000)
- 🌡️ **`temperature`**: Controls response creativity (0.7 = balanced)
- 📏 **`max_tokens`**: Maximum response length



## 🍎 **Why Choose MLX?**

MLX is Apple's native machine learning framework, designed specifically for Apple Silicon Macs. It offers:

- **⚡ Native Performance**: Leverages Apple's Metal Performance Shaders for blazing-fast inference
- **🔋 Battery Efficient**: Optimized power consumption perfect for MacBook users
- **💾 Memory Smart**: Efficient memory usage with 4-bit quantized models
- **🏠 Completely Local**: No internet required after model download
- **🚀 Instant Start**: Quick model loading and inference times

## 🔧 **Customizing MLX Configuration**

### **Change Model**
Edit `agents/mlx_demo/playbook/mlx_demo_playbook.yaml`:

```yaml
language_model:
  model: mlx-community/phi-2  # Different MLX model
  api_base: http://localhost:8000
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
  api_base: http://localhost:9000  # Custom port
```

## 🚨 **Troubleshooting MLX**

### **Common Issues**

1. **MLX Server Not Running**
   ```bash
   # Check if MLX server is running
   curl http://localhost:8000/health
   
   # Start MLX server
   super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000
   ```

2. **Model Not Installed**
   ```bash
   # Check installed MLX models
   super model list --backend mlx
   
   # Install the required model
   super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
   ```

3. **Apple Silicon Required**
   - MLX only works on Apple Silicon Macs (M1, M2, M3)
   - Use Ollama for Intel Macs

### **Getting Help**
```bash
# Check agent status
super agent inspect mlx_demo

# View agent logs
super agent logs mlx_demo

# Get MLX help
super model server --help
```

## 📚 Related Documentation

- [Model Management](../guides/model-management.md) - Managing MLX models
- [Agent Development](../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other Model Backends**: Explore [Ollama](ollama-demo), [HuggingFace](huggingface-demo), or [LM Studio](lmstudio-demo) demos 