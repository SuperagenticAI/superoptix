# 🍎 MLX Demo Agent

A demonstration agent showcasing SuperOptiX's integration with MLX local models on Apple Silicon.

## 🚀 What This Agent Does

The MLX Demo Agent is designed to showcase the power of running SuperOptiX agents locally with MLX models. It provides:

- **Code Assistance**: Write and explain Python functions, algorithms, and programming concepts
- **Concept Explanations**: Clear explanations of programming concepts with examples
- **Problem Solving**: Step-by-step solutions to programming challenges
- **Educational Content**: Learning-focused responses with practical applications

## 🎯 Perfect For

- **Learning Programming**: Get clear explanations of algorithms and data structures
- **Code Review**: Receive feedback and suggestions for your code
- **Algorithm Implementation**: See working examples of common algorithms
- **Concept Understanding**: Deep dive into programming concepts with examples

## 🛠️ Setup Instructions

### 1. Install MLX Model
```bash
super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
```

### 2. Start MLX Server
```bash
# In a separate terminal (default port 8000)
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit

# Or specify a custom port
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit --port 9000
```

### 3. Pull and Run the Agent
```bash
# Pull the agent
super agent pull mlx_demo

# Compile the agent
super agent compile mlx_demo

# Run with a coding question
super agent run mlx_demo "Write a Python function to calculate fibonacci numbers"
```

## 🔧 Custom Port Configuration

**Advanced users can run MLX servers on custom ports:**

### Server on Custom Port
```bash
# Start server on port 9000
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit --port 9000

# Or manually
python -m mlx_lm.server --model mlx-community_Llama-3.2-3B-Instruct-4bit --port 9000
```

### Update Playbook Configuration
Edit your agent playbook to use the custom port:
```yaml
spec:
  language_model:
    provider: mlx
    model: mlx-community/Llama-3.2-3B-Instruct-4bit
    api_base: http://localhost:9000  # Custom port
    temperature: 0.7
    max_tokens: 2048
```

### Multiple MLX Servers
You can run multiple MLX models on different ports:
```bash
# Terminal 1: Llama model on port 8000
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit --port 8000

# Terminal 2: CodeLlama model on port 8001
super model server mlx mlx-community_CodeLlama-7b-Instruct-hf-4bit --port 8001
```

Then configure different agents to use different ports:
```yaml
# Agent 1: Uses Llama on port 8000
language_model:
  provider: mlx
  model: mlx-community/Llama-3.2-3B-Instruct-4bit
  api_base: http://localhost:8000

# Agent 2: Uses CodeLlama on port 8001
language_model:
  provider: mlx
  model: mlx-community/CodeLlama-7b-Instruct-hf-4bit
  api_base: http://localhost:8001
```

## 🎯 Example Queries

### Code Implementation
```bash
super agent run mlx_demo "Implement a binary search algorithm in Python"
super agent run mlx_demo "Write a function to reverse a linked list"
super agent run mlx_demo "Create a Python class for a stack data structure"
```

### Concept Explanations
```bash
super agent run mlx_demo "Explain recursion with examples"
super agent run mlx_demo "What is dynamic programming and when should I use it?"
super agent run mlx_demo "Explain time complexity and Big O notation"
```

### Problem Solving
```bash
super agent run mlx_demo "How would you find the longest palindrome in a string?"
super agent run mlx_demo "Design an algorithm to detect cycles in a linked list"
super agent run mlx_demo "Implement a function to check if a binary tree is balanced"
```

## 🔧 Technical Details

- **Model**: `mlx-community/Llama-3.2-3B-Instruct-4bit`
- **Provider**: MLX (Apple Silicon optimized)
- **Tier**: Oracle (single-step reasoning)
- **Server**: Local MLX server on port 8000
- **Features**: Full DSPy compatibility, BDD testing, optimization ready

## 🎉 Benefits

- **Local Processing**: All inference happens on your Mac
- **No API Costs**: Completely free to use
- **Full Privacy**: Your data never leaves your machine
- **Fast Response**: Optimized for Apple Silicon
- **Educational**: Designed for learning and understanding

## 🚨 Troubleshooting

### Server Not Starting
```bash
# Check if model is installed
super model list --backend mlx

# Restart server
pkill -f mlx_lm.server
super model server mlx mlx-community_Llama-3.2-3B-Instruct-4bit
```

### Connection Issues
```bash
# Test server connectivity
curl http://localhost:8000/health

# Check if port is in use
lsof -i :8000
```

## 📚 Related Documentation

- [MLX DSPy Integration Guide](../docs/MLX_DSPY_INTEGRATION_GUIDE.md)
- [Local Model Servers Guide](../docs/LOCAL_MODEL_SERVERS_GUIDE.md)
- [Getting Started Guide](../docs/GETTING_STARTED.md)

---

**Ready to experience local AI with SuperOptiX and MLX? Try the demo agent today!** 🚀 