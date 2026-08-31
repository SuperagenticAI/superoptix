# 🤗 HuggingFace Demo Agent

The HuggingFace Demo Agent showcases **advanced NLP capabilities** with HuggingFace models in SuperOptiX. This demo focuses specifically on how to configure and use HuggingFace models for sophisticated language understanding and generation.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🤗 **HuggingFace Model Integration**: How to configure HuggingFace models in SuperOptiX
- 🧠 **Advanced NLP Capabilities**: Access to cutting-edge transformer models
- 🏠 **Local Model Usage**: Running models completely offline
- ⚙️ **Playbook Configuration**: How to set up HuggingFace in agent playbooks

## 🚀 **Setup HuggingFace Model**

### **1. Install HuggingFace Dependencies**

```bash
# Install HuggingFace dependencies
uv pip install "superoptix[huggingface]"
```

### **2. Install HuggingFace Model**

```bash
# Install the HuggingFace model used in this demo
super model install -b huggingface microsoft/Phi-4
```

### **3. Start HuggingFace Server**

```bash
# Start HuggingFace server on port 8001
super model server huggingface microsoft/Phi-4 --port 8001
```

### **4. Pull and Run the Demo**

```bash
# Pull the HuggingFace demo agent
super agent pull huggingface_demo

# Compile the agent
super agent compile huggingface_demo

# Run the agent
super agent run huggingface_demo --goal "What are the key features of HuggingFace?"
```

## 🔧 **HuggingFace Configuration in Playbook**

The HuggingFace demo showcases how to configure HuggingFace models in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: huggingface
  model: microsoft/Phi-4
  api_base: http://localhost:8001
  temperature: 0.7
  max_tokens: 2048
```

**Key Configuration Points**:

- 🎯 **`provider: huggingface`**: Specifies HuggingFace as the model backend
- 🤖 **`model`**: The HuggingFace model identifier
- 🌐 **`api_base`**: HuggingFace server endpoint (default: http://localhost:8001)
- 🌡️ **`temperature`**: Controls response creativity (0.7 = balanced)
- 📏 **`max_tokens`**: Maximum response length

## 🤗 **HuggingFace: The NLP Powerhouse**

HuggingFace is the go-to platform for state-of-the-art natural language processing. It offers unparalleled access to the latest AI research:

- **🏆 State-of-the-Art**: Access to cutting-edge transformer models and architectures
- **📚 Model Library**: Thousands of pre-trained models for every NLP task
- **🔧 Custom Models**: Support for your own fine-tuned models and research
- **🧪 Research Ready**: Perfect for academic research and experimentation
- **🔓 Open Source Models**: Most models are open source and freely available
- **🌐 Open Source**: Backed by the largest NLP community in the world

## 🔧 **Customizing HuggingFace Configuration**

### **Change Model**
Edit `agents/huggingface_demo/playbook/huggingface_demo_playbook.yaml`:

```yaml
language_model:
  model: microsoft/DialoGPT-small  # Different HuggingFace model
  api_base: http://localhost:8001
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
  api_base: http://localhost:9001  # Custom port
```

## 🚨 **Troubleshooting HuggingFace**

### **Common Issues**

1. **HuggingFace Server Not Running**
   ```bash
   # Check if HuggingFace server is running
   curl http://localhost:8001/health
   
   # Start HuggingFace server
   super model server huggingface microsoft/Phi-4 --port 8001
   ```

2. **Model Not Installed**
   ```bash
   # Check installed HuggingFace models
   super model list --backend huggingface
   
   # Install the required model
   super model install -b huggingface microsoft/Phi-4
   ```

3. **Performance Issues**
   - Ensure sufficient GPU memory for large models
   - Close other resource-intensive applications
   - Consider using smaller models for faster responses

### **Getting Help**
```bash
# Check agent status
super agent inspect huggingface_demo

# View agent logs
super agent logs huggingface_demo

# Get HuggingFace help
super model server --help
```

## 📚 **Related Resources**

- [HuggingFace Setup Guide](../../llm-setup.md#huggingface) - Complete HuggingFace setup instructions
- [Model Management](../../guides/model-management.md) - Managing HuggingFace models
- [Agent Development](../../guides/agent-development.md) - Building custom agents

## 🎉 **Next Steps**

After exploring the HuggingFace demo:

1. **Try Other Model Backends**: Explore [MLX](mlx-demo.md), [Ollama](ollama-demo.md), or [LM Studio](lmstudio-demo.md) demos
2. **Customize**: Modify the playbook for your specific HuggingFace needs
3. **Build Your Own**: Use this as a template for your custom HuggingFace agent

---

**Ready to explore advanced NLP? Start with the HuggingFace demo! 🚀** 