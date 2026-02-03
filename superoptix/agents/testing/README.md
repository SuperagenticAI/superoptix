# 🧪 Testing Agents

This directory contains demonstration agents for testing SuperOptiX integrations with different local model backends.

## 🎮 Available Demo Agents

### LM Studio Demo Agent
- **File**: `lmstudio_demo_playbook.yaml`
- **Description**: Demonstrates LM Studio integration with SuperOptiX and DSPy
- **Features**: 
  - Full DSPy pipeline integration
  - Memory system with episodic memory
  - Tool integration (web search, file operations, code execution)
  - Observability and tracing
  - Multiple task types (Q&A, code generation, creative writing, problem solving)

### MLX Demo Agent
- **File**: `mlx_demo_playbook.yaml`
- **Description**: Demonstrates MLX integration for Apple Silicon
- **Features**: Apple Silicon optimized models with full DSPy compatibility

### HuggingFace Demo Agent
- **File**: `huggingface_demo_playbook.yaml`
- **Description**: Demonstrates HuggingFace integration
- **Features**: Transformers ecosystem models with local inference

## 🚀 Quick Start

### LM Studio Demo
```bash
# 1. Install LM Studio from https://lmstudio.ai
# 2. Download and load a model in LM Studio
# 3. Start LM Studio server (Local Server tab)
# 4. Run the demo agent
super agent run lmstudio_demo_playbook.yaml

# Test with specific prompt
super agent run lmstudio_demo_playbook.yaml --prompt "Write a Python function to calculate fibonacci numbers"
```

### MLX Demo
```bash
# 1. Install MLX model
super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit

# 2. Start MLX server
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit

# 3. Run the demo agent
super agent run mlx_demo_playbook.yaml
```

### HuggingFace Demo
```bash
# 1. Start HuggingFace server
super model server huggingface microsoft/DialoGPT-small

# 2. Run the demo agent
super agent run huggingface_demo_playbook.yaml
```

## 📋 Configuration

### LM Studio Configuration
```yaml
language_model:
  provider: "lmstudio"
  model: "llama-3.2-3b"  # Replace with your loaded model
  api_base: "http://localhost:1234"
  temperature: 0.7
  max_tokens: 512
```

### MLX Configuration
```yaml
language_model:
  provider: "mlx"
  model: "mlx-community/Llama-3.2-3B-Instruct-4bit"
  api_base: "http://localhost:8000"
  temperature: 0.7
  max_tokens: 512
```

### HuggingFace Configuration
```yaml
language_model:
  provider: "huggingface"
  model: "microsoft/DialoGPT-small"
  api_base: "http://localhost:8001"
  temperature: 0.7
  max_tokens: 256
```

## 🎯 Example Tasks

### LM Studio Demo Tasks
- **Q&A**: "Explain how machine learning works"
- **Code Generation**: "Write a Python function to sort a list"
- **Creative Writing**: "Write a story about a robot learning to paint"
- **Problem Solving**: "How can I optimize my website's performance?"

### MLX Demo Tasks
- **Code Review**: "Review this Python function for best practices"
- **Technical Explanation**: "Explain recursion with examples"
- **Algorithm Design**: "Design an efficient sorting algorithm"

### HuggingFace Demo Tasks
- **Conversation**: "Let's chat about technology"
- **Language Learning**: "Help me practice Spanish"
- **Content Generation**: "Generate a short story"

## 🔧 Troubleshooting

### Common Issues
1. **Connection Errors**: Ensure the model server is running
2. **Model Not Found**: Check model names match exactly
3. **DSPy Integration**: Ensure `dspy-ai` and `litellm` are installed

### Debug Commands
```bash
# Check backend status
super model backends

# List available models
super model list --backend <backend_name>

# Test model connection
super model test <backend>/<model_name>

# Check server status
curl <api_base>/v1/models
```

## 📚 Related Documentation

- [LM Studio DSPy Integration Guide](../../../docs/LMSTUDIO_DSPY_INTEGRATION.md)
- [MLX DSPy Integration Guide](../../../docs/MLX_DSPY_INTEGRATION_GUIDE.md)
- [HuggingFace DSPy Integration Guide](../../../docs/HUGGINGFACE_DSPY_INTEGRATION_GUIDE.md)
- [Local Model Servers Guide](../../../docs/LOCAL_MODEL_SERVERS_GUIDE.md)
- [Local Model Examples](../../../docs/LOCAL_MODEL_EXAMPLES.md)

## 🤝 Contributing

To add new demo agents:
1. Create a YAML playbook file
2. Update this README with agent details
3. Test the agent thoroughly
4. Add to the marketplace if appropriate

## 📄 License

These demo agents are part of SuperOptiX and follow the same license terms. 