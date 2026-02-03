# 🤗 HuggingFace Demo Agent

A demonstration agent showcasing SuperOptiX's integration with HuggingFace local models.

## 🚀 What This Agent Does

The HuggingFace Demo Agent is designed to showcase the power of running SuperOptiX agents locally with HuggingFace models. It provides:

- **Conversational AI**: Natural conversations and assistance
- **Concept Explanations**: Clear explanations of technical concepts and topics
- **Problem Solving**: Step-by-step solutions to various problems
- **Educational Content**: Learning-focused responses with practical applications

## 🎯 Perfect For

- **Learning & Education**: Get clear explanations of concepts and topics
- **Conversational AI**: Experience natural language interactions
- **Problem Solving**: Receive step-by-step guidance for various problems
- **Local AI Testing**: See how local HuggingFace models perform
- **Privacy-Focused AI**: All processing happens locally on your machine

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
# Install required packages
pip install transformers torch fastapi uvicorn
# or with uv
uv pip install transformers torch fastapi uvicorn
```

### 2. Start HuggingFace Server
```bash
# In a separate terminal (default port 8001)
super model server huggingface microsoft/DialoGPT-small

# Or specify a custom port
super model server huggingface microsoft/DialoGPT-small --port 9001
```

### 3. Pull and Run the Agent
```bash
# Pull the agent
super agent pull huggingface_demo

# Compile the agent
super agent compile huggingface_demo

# Run with a question
super agent run huggingface_demo "What is machine learning?"
```

## 🔧 Custom Port Configuration

**Advanced users can run HuggingFace servers on custom ports:**

### Server on Custom Port
```bash
# Start server on port 9001
super model server huggingface microsoft/DialoGPT-small --port 9001
```

Update your playbook to use the custom port:
```yaml
spec:
  language_model:
    provider: huggingface
    model: microsoft/DialoGPT-small
    api_base: http://localhost:9001  # Custom port
```

### Multiple HuggingFace Models
```bash
# Terminal 1: Server on port 8001
super model server huggingface microsoft/DialoGPT-small --port 8001

# Terminal 2: Server on port 8002
super model server huggingface facebook/opt-125m --port 8002
```

## 🎉 Benefits

- **Local Processing**: All inference happens on your machine
- **No API Costs**: Completely free to use
- **Full Privacy**: Your data never leaves your machine
- **Fast Response**: Optimized for local inference
- **Educational**: Designed for learning and understanding

## 🚨 Troubleshooting

### Server Not Starting
```bash
# Check if dependencies are installed
pip list | grep transformers

# Restart server
pkill -f huggingface_server
super model server huggingface microsoft/DialoGPT-small
```

### Connection Issues
```bash
# Test server connectivity
curl http://localhost:8001/health

# Check if port is in use
lsof -i :8001
```

### Model Loading Issues
```bash
# Check available models
super model list --backend huggingface

# Try a different model
super model server huggingface facebook/opt-125m --port 8001
```

## 📚 Related Documentation

- [HuggingFace DSPy Integration Guide](../docs/HUGGINGFACE_DSPY_INTEGRATION_GUIDE.md)
- [Local Model Servers Guide](../docs/LOCAL_MODEL_SERVERS_GUIDE.md)
- [Getting Started Guide](../docs/GETTING_STARTED.md)

---

**Ready to experience local AI with SuperOptiX and HuggingFace? Try the demo agent today!** 🚀 