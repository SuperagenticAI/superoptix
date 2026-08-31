# 🤖 LLM Setup Guide

Welcome to SuperOptiX's LLM Setup Guide! This guide will help you configure and use local language models for your AI agents. We focus on local models for privacy, speed, and cost-effectiveness.

!!! tip "🚀 Quick Start"
    **New to local models?** Start with [Ollama](#ollama-recommended) - it's the easiest option for beginners!

## 🎯 Overview

SuperOptiX supports multiple local model backends, each optimized for different use cases:

| Backend | Best For | Platform | Ease of Use | Performance |
|---------|----------|----------|-------------|-------------|
| **🦙 Ollama** | Beginners, All platforms | Cross-platform | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **🤖 GPT-OSS** | Advanced reasoning, Agentic tasks | Cross-platform | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **🍎 MLX** | Apple Silicon users | macOS only | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **🎮 LM Studio** | Windows users | Windows/macOS | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **🤗 HuggingFace** | Advanced users | All platforms | ⭐⭐ | ⭐⭐⭐⭐⭐ |

!!! warning "Production Inference Engines"
    **vLLM, SGLang, and TGI** are not included in the current version of SuperOptiX. These production-worthy inference engines are part of our enterprise offering.

## 🦙 Ollama (Recommended)

**Ollama** is the easiest way to run local models on any platform. Perfect for beginners!

### 🚀 Quick Setup

=== "🍎 macOS"
    ```bash
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Start Ollama (runs in background)
    ollama serve
    ```

=== "🐧 Linux"
    ```bash
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Start Ollama
    ollama serve
    ```

=== "🪟 Windows"
    ```powershell
    # Download from https://ollama.ai/download
    # Or use winget
    winget install Ollama.Ollama
    
    # Start Ollama
    ollama serve
    ```

### 📦 Install Models with SuperOptiX

```bash
# Install recommended models by tier
super model install qwen3.5:2b      # Oracles tier - Small tasks, fast responses
super model install qwen3.5:9b      # Genies tier - Complex reasoning, tools, memory
super model install qwen3.5:2b      # Alternative small model
super model install qwen2.5:7b       # Great all-rounder
```

<details><summary><strong>Show Output</strong></summary>

```
🚀 SuperOptiX Model Intelligence - Installing qwen3.5:2b
🦙 Pulling model qwen3.5:2b from Ollama...
⏳ This may take a few minutes depending on your internet connection and model size.

pulling manifest 
pulling dde5aa3fc5ff: 100% ▕██████████████████████████████████████████████▏ 2.0 GB                         
pulling 966de95ca8a6: 100% ▕██████████████████████████████████████████████▏ 1.4 KB                         
pulling fcc5a6bec9da: 100% ▕██████████████████████████████████████████████▏ 7.7 KB                         
pulling a70ff7e570d9: 100% ▕██████████████████████████████████████████████▏ 6.0 KB                         
pulling 56bb8bd477a5: 100% ▕██████████████████████████████████████████████▏   96 B                         
pulling 34bb5ab01051: 100% ▕██████████████████████████████████████████████▏  561 B                         
verifying sha256 digest 
writing manifest 
success 
Model pulled successfully!

💡 You can now use it with SuperOptiX:
  super model dspy ollama/qwen3.5:2b

📊 Model details:
  • Size: small
  • Task: chat
  • Parameters: 3B

🎉 Installation completed successfully!
🦙 Ollama running on http://localhost:11434 ready to use with SuperOptiX!
```

</details>

### 🖥️ Server Management

**💡 Important**: Ollama automatically starts its server when you run `ollama serve` or when you first use a model. You don't need to manually start the server unless you want custom configuration.

```bash
# Start Ollama server (runs on port 11434 by default)
ollama serve

# Or simply use a model - server starts automatically
ollama run qwen3.5:2b
```

**🔧 Custom Configuration**: Only start the server manually if you need:
- Different port: `OLLAMA_HOST=0.0.0.0:8080 ollama serve`
- Custom model path: `OLLAMA_MODELS=/custom/path ollama serve`
- GPU configuration: `OLLAMA_GPU_LAYERS=35 ollama serve`

**Automatic Detection**: SuperOptiX automatically detects and connects to Ollama running on the default port (11434). No additional configuration needed!

### 📋 Manage Ollama Models

```bash
# List installed models
super model list --backend ollama
```

**Example Output:**
```
                🚀 SuperOptiX Model Intelligence - 3 models                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ Model                   ┃  Backend  ┃    Status    ┃  Size   ┃   Task    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ qwen3.5:9b             │ 🦙 ollama │ installed │ medium  │   chat    │
│ qwen3.5:2b             │ 🦙 ollama │ installed │  tiny   │   chat    │
│ nomic-embed-text:latest │ 🦙 ollama │ installed │ Unknown │ embedding │
└─────────────────────────┴───────────┴──────────────┴─────────┴───────────┘
```

```bash
# Get model information
super model info qwen3.5:2b

# List all available models
super model list --all
```

## 🤖 GPT-OSS Models (OpenAI's Open Source)

**GPT-OSS** models are OpenAI's latest open-weight language models designed for powerful reasoning, agentic tasks, and versatile developer use cases. SuperOptiX now supports both GPT-OSS-20B and GPT-OSS-120B models with **native Apple Silicon support**!

### 🍎 Apple Silicon Support

**MLX-LM v0.26.3** now provides native Apple Silicon support for GPT-OSS models, resolving the mixed precision issues that previously prevented these models from running on Apple Silicon.

| Backend | Model | Status | Performance | Apple Silicon | **Recommendation** |
|---------|-------|--------|-------------|---------------|-------------------|
| **🦙 Ollama** | gpt-oss:20b | **Works** | **19.7 t/s** | **Optimized format** | **⭐ RECOMMENDED** |
| **🍎 MLX-LM** | openai_gpt-oss-20b | **Works** | 5.2 t/s | **Native support** | **Apple Silicon only** |
| **🤗 HuggingFace** | openai/gpt-oss-20b | **Broken** | N/A | **Mixed precision errors** | **Avoid on Apple Silicon** |

### 🎯 GPT-OSS Model Overview

| Model | Parameters | Active Parameters | Best For | Hardware Requirements |
|-------|------------|-------------------|----------|----------------------|
| **GPT-OSS-20B** | 21B | 3.6B | Lower latency, local/specialized use cases | 16GB+ RAM |
| **GPT-OSS-120B** | 117B | 5.1B | Production, general purpose, high reasoning | Single H100 GPU |

!!! tip "🚀 **Recommended: Use Ollama for GPT-OSS Models**"
    **For the best performance and reliability with GPT-OSS models, we recommend using Ollama:**
    
    - **Best Performance**: 19.7 t/s vs 5.2 t/s (MLX) vs N/A (HuggingFace)
    - **Cross-Platform**: Works on all platforms (Windows, macOS, Linux)
    - **Easy Setup**: Simple installation and model management
    - **Optimized Format**: GGUF format optimized for local inference
    - **No Server Required**: Direct model execution
    
    **Install and use GPT-OSS with Ollama:**
    ```bash
    # Install GPT-OSS models
    super model install gpt-oss:20b
    super model install gpt-oss:120b
    
    # Use in playbooks
    language_model:
      provider: ollama
      model: gpt-oss:20b
      api_base: http://localhost:11434
    ```

### 🚀 Key Features

- **🔓 Apache 2.0 License:** Build freely without copyleft restrictions
- **⚡ Native MXFP4 Quantization:** Optimized for efficient inference
- **🍎 Apple Silicon Native:** No more mixed precision issues

### 📦 Install GPT-OSS Models

#### Via Ollama (Cross-Platform - **RECOMMENDED**)

```bash
# Install GPT-OSS models via Ollama (Best Performance)
super model install gpt-oss:20b
super model install gpt-oss:120b

# Or use direct Ollama commands
ollama pull gpt-oss:20b
ollama pull gpt-oss:120b

# Run with Ollama backend
super model run gpt-oss:20b "Your prompt" --backend ollama
```

#### Via MLX-LM (Apple Silicon - Native Support)

```bash
# Install GPT-OSS models via Ollama
super model install gpt-oss:20b
super model install gpt-oss:120b

# Or use direct Ollama commands
ollama pull gpt-oss:20b
ollama pull gpt-oss:120b

# Run with Ollama backend
super model run gpt-oss:20b "Your prompt" --backend ollama
```

<details><summary><strong>Show Ollama Installation Output</strong></summary>

```
🚀 SuperOptiX Model Intelligence - Installing gpt-oss:20b
🦙 Pulling model gpt-oss:20b from Ollama...
⏳ This may take a few minutes depending on your internet connection and model size.

pulling manifest 
pulling 8f7b3c2a1d4e: 100% ▕██████████████████████████████████████████████▏ 12.5 GB                         
pulling 9a2b4c6d8e0f: 100% ▕██████████████████████████████████████████████▏ 1.2 KB                         
verifying sha256 digest 
writing manifest 
success 
Model pulled successfully!

💡 You can now use it with SuperOptiX:
  super model dspy ollama/gpt-oss:20b

📊 Model details:
  • Size: large
  • Task: chat
  • Parameters: 21B (3.6B active)

🎉 Installation completed successfully!
🦙 Ollama running on http://localhost:11434 ready to use with SuperOptiX!
```

</details>

#### Via HuggingFace

```bash
# Install GPT-OSS models via HuggingFace
super model install openai/gpt-oss-20b --backend huggingface
super model install openai/gpt-oss-120b --backend huggingface

# Start HuggingFace server
super model server huggingface openai/gpt-oss-20b --port 8001
super model server huggingface openai/gpt-oss-120b --port 8002
```

<details><summary><strong>Show HuggingFace Installation Output</strong></summary>

```
🚀 SuperOptiX Model Intelligence - Installing openai/gpt-oss-20b
🤗 Downloading model from HuggingFace...
⏳ This may take several minutes depending on your internet connection and model size.

Downloading model files...
  • config.json: 100% ▕██████████████████████████████████████████████▏ 2.1 KB
  • model.safetensors: 100% ▕██████████████████████████████████████████████▏ 12.5 GB
  • tokenizer.json: 100% ▕██████████████████████████████████████████████▏ 1.8 MB
  • tokenizer_config.json: 100% ▕██████████████████████████████████████████████▏ 1.2 KB

Model downloaded successfully!

💡 You can now use it with SuperOptiX:
  super model server huggingface openai/gpt-oss-20b --port 8001

📊 Model details:
  • Size: large
  • Task: chat
  • Parameters: 21B (3.6B active)
  • License: Apache 2.0

🎉 Installation completed successfully!
```

</details>

### 🎯 Using GPT-OSS with SuperOptiX

#### **Configure Playbook for GPT-OSS**

```yaml
# Example playbook configuration for GPT-OSS
language_model:
  provider: mlx  # or ollama or huggingface
  model: lmstudio-community/gpt-oss-20b-MLX-8bit  # for MLX-LM
  # model: gpt-oss:20b  # for Ollama
  # model: openai/gpt-oss-20b  # for HuggingFace
  api_base: http://localhost:11434  # for Ollama
  # api_base: http://localhost:8001  # for HuggingFace
  temperature: 0.7
  max_tokens: 2048

# GPT-OSS Language Model Configuration Examples

**🦙 Ollama Backend (Cross-platform - RECOMMENDED):**
```yaml
language_model:
  provider: ollama
  model: gpt-oss:20b
  api_base: http://localhost:11434
  temperature: 0.7
  max_tokens: 4096
```

**🍎 MLX Backend (Apple Silicon - Native Support):**
```yaml
language_model:
  provider: mlx
  model: lmstudio-community/gpt-oss-20b-MLX-8bit
  api_base: http://localhost:8000
  temperature: 0.7
  max_tokens: 4096
```

**🤗 HuggingFace Backend (Limited on Apple Silicon):**
```yaml
language_model:
  provider: huggingface
  model: openai/gpt-oss-20b
  api_base: http://localhost:8001
  temperature: 0.7
  max_tokens: 4096
```

### 🚀 **Starting MLX Server for GPT-OSS**

Before using GPT-OSS with MLX in your playbook, start the MLX server:

```bash
# Start MLX server for GPT-OSS model
super model server mlx lmstudio-community/gpt-oss-20b-MLX-8bit --port 8000

# Or start on a different port
super model server mlx lmstudio-community/gpt-oss-20b-MLX-8bit --port 9000
```

**Server Output:**
```
🍎 MLX Local Server
Starting MLX server for lmstudio-community/gpt-oss-20b-MLX-8bit on port 8000...
🚀 Starting MLX server...
python -m mlx_lm.server --model lmstudio-community/gpt-oss-20b-MLX-8bit --port 8000
MLX server is running on http://localhost:8000
```

**Note:** Keep the server running while using GPT-OSS models in your playbooks.

```

#### **Test GPT-OSS Models**

```bash
# Test with MLX-LM backend (Apple Silicon - Native)
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "Explain quantum computing with detailed reasoning" --backend mlx

# Test with Ollama backend (Cross-platform - Best Performance)
super model run gpt-oss:20b "Explain quantum computing with detailed reasoning" --backend ollama

# Test with HuggingFace backend (Limited on Apple Silicon)
super model run openai/gpt-oss-20b "Write a Python function to solve the traveling salesman problem" --backend huggingface
```

#### **Basic Usage Examples**

```bash
# MLX-LM (Apple Silicon - Native support)
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "What is 2+2?" --backend mlx
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "Explain machine learning" --backend mlx
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "Design a distributed system architecture" --backend mlx

# Ollama (Cross-platform - Best performance)
super model run gpt-oss:20b "What is 2+2?" --backend ollama
super model run gpt-oss:20b "Explain machine learning" --backend ollama
super model run gpt-oss:20b "Design a distributed system architecture" --backend ollama
```

### 📋 Manage GPT-OSS Models

```bash
# List installed GPT-OSS models
super model list | grep gpt-oss

# Get detailed information
super model info gpt-oss:20b
super model info openai/gpt-oss-120b

# Test model performance
super model test gpt-oss:20b "Hello, how are you?"
```

### 🎯 Performance Recommendations

| Use Case | Recommended Model | Hardware |
|----------|------------------|----------|
| **Quick responses** | GPT-OSS-20B | 16GB+ RAM |
| **Complex tasks** | GPT-OSS-120B | H100 GPU |
| **Local development** | GPT-OSS-20B | 16GB+ RAM |

### 🔧 Troubleshooting GPT-OSS

=== "Apple Silicon Mixed Precision Issues"
    
    **Error:** `error: 'mps.matmul' op detected operation with both F16 and BF16 operands which is not supported`
    
    **Solution:**
    ```bash
    # Use MLX-LM backend (native Apple Silicon support)
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "prompt" --backend mlx
    
    # Or use Ollama backend (optimized format)
    super model run gpt-oss:20b "prompt" --backend ollama
    ```

=== "Model Not Found"
    
    **Error:** `Model not found` or `Model does not exist`
    
    **Solution:**
    ```bash
    # For MLX-LM (Apple Silicon)
super model install lmstudio-community/gpt-oss-20b-MLX-8bit --backend mlx
    
    # For Ollama
    ollama pull gpt-oss:20b
    ollama pull gpt-oss:120b
    
    # For HuggingFace
    super model install openai/gpt-oss-20b --backend huggingface
    super model install openai/gpt-oss-120b --backend huggingface
    ```

=== "Out of Memory"
    
    **Error:** `CUDA out of memory` or `Not enough memory`
    
    **Solution:**
    ```bash
    # Use smaller model
    super model install gpt-oss:20b  # Instead of 120b
    
    # Use CPU inference
    super model server huggingface openai/gpt-oss-20b --device cpu
    ```

=== "Server Connection Failed"
    
    **Error:** `Connection refused` or `Cannot connect to server`
    
    **Solution:**
    ```bash
    # Check Ollama server
    ollama serve
    
    # Check HuggingFace server
    super model server huggingface openai/gpt-oss-20b --port 8001
    ```

### 📚 Resources

- [GPT-OSS-120B Model](https://huggingface.co/openai/gpt-oss-120b) - HuggingFace repository
- [GPT-OSS-20B Model](https://huggingface.co/openai/gpt-oss-20b) - HuggingFace repository
- [Ollama Library](https://ollama.com/library/gpt-oss) - Ollama model library
- [SuperOptiX Documentation](https://superoptix.ai) - Complete framework documentation
- [DSPy Framework](https://dspy.ai) - Foundation framework

## 🍎 MLX (Apple Silicon)

**MLX** is Apple's native machine learning framework, offering blazing-fast inference on Apple Silicon Macs. **MLX-LM v0.26.3** now provides native support for GPT-OSS models!

!!! tip "Apple Silicon Only"
    MLX only works on Apple Silicon Macs (M1, M2, M3). If you're on Intel Mac, use Ollama instead.

### 🚀 Setup MLX

```bash
# Install MLX dependencies
pip install mlx-lm==0.26.3

# Or install with SuperOptiX
pip install "superoptix[mlx]"
```

### 📦 Install MLX Models

```bash
# Install GPT-OSS models (native Apple Silicon support)
super model install openai/gpt-oss-20b --backend mlx
super model install openai/gpt-oss-120b --backend mlx

# Install popular MLX models
super model install -b mlx mlx-community/phi-2
super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit
super model install -b mlx mlx-community/Mistral-7B-Instruct-v0.2-4bit
super model install -b mlx lmstudio-community/gpt-oss-20b-MLX-8bit
```

### 🖥️ Start MLX Servers

```bash
# Start MLX server on specific port
super model server mlx phi-2 --port 8000
super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000
```

**Example Output:**
```
🍎 MLX Local Server
Starting MLX server for mlx-community_Llama-3.2-3B-Instruct-4bit on port 8000...
🚀 Starting MLX server...
📡 Server will be available at: http://localhost:8000
💡 Use this URL in your playbook's api_base configuration
🔧 Manual server startup command:
   python -m mlx_lm.server --model mlx-community_Llama-3.2-3B-Instruct-4bit --port 8000
📋 Example playbook configuration:
   language_model:
     provider: mlx
     model: mlx-community_Llama-3.2-3B-Instruct-4bit
     api_base: http://localhost:8000
🔄 Executing: /path/to/python -m mlx_lm.server --model mlx-community_Llama-3.2-3B-Instruct-4bit --port 8000
⏳ Server is starting... (Press Ctrl+C to stop)
```

### 📋 Manage MLX Models

```bash
# List MLX models
super model list --backend mlx
```

**Example Output:**
```
                    🚀 SuperOptiX Model Intelligence - 1 models                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┓
┃ Model                                    ┃ Backend ┃    Status    ┃ Size  ┃ Task ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━┩
│ mlx-community_Llama-3.2-3B-Instruct-4bit │ 🍎 mlx  │ installed │ small │ chat │
└──────────────────────────────────────────┴─────────┴──────────────┴───────┴──────┘
```

```bash
# Get model information
super model info mlx-community/phi-2
super model info mlx-community_Llama-3.2-3B-Instruct-4bit

# Models are ready to use with SuperOptiX agents
```

## 🎮 LM Studio

**LM Studio** provides a user-friendly interface for running local models, especially popular on Windows.

### 🚀 Setup LM Studio

1. **Download LM Studio** from [https://lmstudio.ai](https://lmstudio.ai)
2. **Install and launch** LM Studio
3. **Download a model** through the interface
4. **Start the server** (default port: 1234)

### 📦 Install Models with SuperOptiX

```bash
# Install models (use the name from LM Studio)
super model install -b lmstudio qwen2.5-3b-instruct
super model install -b lmstudio qwen2.5-7b-instruct
super model install -b lmstudio your-model-name
```

### 🖥️ Start LM Studio Servers

```bash
# Start server with specific model
super model server lmstudio qwen2.5-3b-instruct --port 1234
super model server lmstudio qwen2.5-7b-instruct --port 1234
```

**Example Output:**
```
🎮 LM Studio Local Server
Starting LM Studio server for qwen2.5-3b-instruct on port 1234...
🚀 Starting LM Studio server...
📡 Server will be available at: http://localhost:1234
💡 Use this URL in your playbook's api_base configuration
🔧 Manual server startup command:
   # Start server in LM Studio app first, then connect
📋 Example playbook configuration:
   language_model:
     provider: lmstudio
     model: qwen2.5-3b-instruct
     api_base: http://localhost:1234
⏳ Server is starting... (Press Ctrl+C to stop)
```

### 📋 Manage LM Studio Models

```bash
# List LM Studio models
super model list --backend lmstudio
```

**Example Output:**
```
                  🚀 SuperOptiX Model Intelligence - 3 models                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━┓
┃ Model                          ┃   Backend   ┃    Status    ┃  Size  ┃ Task ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━┩
│ qwen2.5-3b-instruct            │ 🎮 lmstudio │ installed │ small  │ chat │
│ qwen2.5-7b-instruct            │ 🎮 lmstudio │ installed │ medium │ chat │
│ llama-4-scout-17b-16e-instruct │ 🎮 lmstudio │ installed │ medium │ chat │
└────────────────────────────────┴─────────────┴──────────────┴────────┴──────┘
```

```bash
# Get model information
super model info qwen2.5-3b-instruct

# Models are ready to use with SuperOptiX agents
```

## 🤗 HuggingFace

**HuggingFace** offers access to thousands of models, perfect for advanced users who want maximum flexibility.

### 🚀 Setup HuggingFace

```bash
# Install HuggingFace dependencies
pip install transformers torch fastapi uvicorn

# Or install with SuperOptiX
pip install "superoptix[huggingface]"
```

### 📦 Install HuggingFace Models

```bash
# Install popular models
super model install -b huggingface microsoft/Phi-4
super model install -b huggingface microsoft/DialoGPT-small
super model install -b huggingface microsoft/DialoGPT-medium
super model install -b huggingface meta-llama/Llama-2-7b-chat-hf
```

### 🖥️ Start HuggingFace Servers

```bash
# Start server with specific model
super model server huggingface microsoft/Phi-4 --port 8001
super model server huggingface microsoft/DialoGPT-small --port 8001
super model server huggingface microsoft/DialoGPT-medium --port 8001
```

**Example Output:**
```
🤗 HuggingFace Local Server
Starting HuggingFace server for microsoft/DialoGPT-small on port 8002...
🚀 Starting HuggingFace server...
📡 Server will be available at: http://localhost:8002
💡 Use this URL in your playbook's api_base configuration
🔧 Manual server startup command:
   python -m superoptix.models.backends.huggingface_server microsoft/DialoGPT-small --port 8002
📋 Example playbook configuration:
   language_model:
     provider: huggingface
     model: microsoft/DialoGPT-small
     api_base: http://localhost:8002
Device set to use cpu
INFO:     Started server process [4652]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```

### 📋 Manage HuggingFace Models

```bash
# List HuggingFace models
super model list --backend huggingface
```

**Example Output:**
```
                🚀 SuperOptiX Model Intelligence - 2 models                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┓
┃ Model                    ┃    Backend     ┃    Status    ┃ Size  ┃ Task ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━┩
│ microsoft/DialoGPT-small │ 🤗 huggingface │ installed │ small │ chat │
│ microsoft/Phi-4          │ 🤗 huggingface │ installed │ small │ chat │
└──────────────────────────┴────────────────┴──────────────┴───────┴──────┘
```

```bash
# Get model information
super model info microsoft/Phi-4
super model info microsoft/DialoGPT-small

# Models are ready to use with SuperOptiX agents
```

## 🎯 Model Management Commands

### 🖥️ Server Commands

```bash
# Get help for server commands
super model server --help
```

**Example Output:**
```
usage: super model server [-h] [--port PORT] {mlx,huggingface,lmstudio} model_name

🚀 Start local model servers for MLX, HuggingFace, or LM Studio. Examples: 
super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit 
super model server huggingface microsoft/DialoGPT-small --port 8001
super model server lmstudio qwen2.5-3b-instruct 

Backends: 
mlx Apple Silicon optimized (default: port 8000) 
huggingface Transformers models (default: port 8001) 
lmstudio Desktop app models (default: port 1234) 

Note: Ollama servers use 'ollama serve' command separately.

positional arguments:
  {mlx,huggingface,lmstudio}  Backend type
  model_name                   Model name to start server for

options:
  -h, --help                   show this help message and exit
  --port PORT, -p PORT         Port to run server on
```

### 📋 List and Explore Models

```bash
# List all installed models
super model list
```

**Example Output:**
```
                           🚀 SuperOptiX Model Intelligence - 9 models                   
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ Model                                    ┃    Backend     ┃    Status    ┃  Size   ┃   Task    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ qwen2.5-3b-instruct                      │  🎮 lmstudio   │ installed │  small  │   chat    │
│ qwen2.5-7b-instruct                      │  🎮 lmstudio   │ installed │ medium  │   chat    │
│ llama-4-scout-17b-16e-instruct           │  🎮 lmstudio   │ installed │ medium  │   chat    │
│ qwen3.5:9b                              │   🦙 ollama    │ installed │ medium  │   chat    │
│ qwen3.5:2b                              │   🦙 ollama    │ installed │  tiny   │   chat    │
│ microsoft/DialoGPT-small                 │ 🤗 huggingface │ installed │  small  │   chat    │
│ microsoft/Phi-4                          │ 🤗 huggingface │ installed │  small  │   chat    │
│ mlx-community_Llama-3.2-3B-Instruct-4bit │     🍎 mlx     │ installed │  small  │   chat    │
│ nomic-embed-text:latest                  │   🦙 ollama    │ installed │ Unknown │ embedding │
└──────────────────────────────────────────┴────────────────┴──────────────┴─────────┴───────────┘

🔍 Discover more models: super model discover
📥 Install a model: super model install <model_name>
```

```bash
# List all available models (including uninstalled)
super model list --all

# Filter by backend
super model list --backend ollama
super model list --backend mlx
super model list --backend lmstudio
super model list --backend huggingface

# Verbose information
super model list --verbose
```

### 📊 Get Model Information

```bash
# Get detailed model info
super model info qwen3.5:2b
super model info mlx-community/phi-2
super model info microsoft/Phi-4
super model info qwen2.5-3b-instruct
```

## 🎯 Choose Your Setup

### 🚀 **Beginner (Recommended)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install SuperOptiX
pip install superoptix

# Install a model
super model install qwen3.5:2b

# Models are ready to use with SuperOptiX agents
```

### 🍎 **Apple Silicon User**
```bash
# Install MLX dependencies
pip install mlx-lm

# Install SuperOptiX
pip install superoptix

# Install MLX model
super model install -b mlx mlx-community/phi-2

# Start server
super model server mlx phi-2 --port 8000

# Models are ready to use with SuperOptiX agents
```

### 🎮 **Windows User**
```bash
# Install LM Studio from https://lmstudio.ai
# Download a model in LM Studio
# Start server in LM Studio

# Install SuperOptiX
pip install superoptix

# Connect to LM Studio
super model server lmstudio your-model-name --port 1234

# Models are ready to use with SuperOptiX agents
```

### 🤗 **Advanced User**
```bash
# Install HuggingFace dependencies
pip install transformers torch fastapi uvicorn

# Install SuperOptiX
pip install superoptix

# Install HuggingFace model
super model install -b huggingface microsoft/Phi-4

# Start server
super model server huggingface microsoft/Phi-4 --port 8001

# Models are ready to use with SuperOptiX agents
```

## 🔧 Advanced Configuration

### 🌐 Multiple Servers

Run multiple models simultaneously:

```bash
# Terminal 1: Ollama model
# Models are ready to use with SuperOptiX agents

# Terminal 2: MLX model (Apple Silicon)
super model server mlx phi-2 --port 8000
# Models are ready to use with SuperOptiX agents

# Terminal 3: HuggingFace model
super model server huggingface microsoft/Phi-4 --port 8001
# Models are ready to use with SuperOptiX agents

# Terminal 4: LM Studio model
super model server lmstudio qwen2.5-3b-instruct --port 1234
# Models are ready to use with SuperOptiX agents
```

## 🚨 Troubleshooting

### Common Issues

=== "Model Not Found"
    
    **Error:** `Model not found` or `Model does not exist`
    
    **Solution:**
    ```bash
    # Check available models
    super model list --all
    
    # Use correct model name
    super model install qwen3.5:2b  # Correct
    super model install llama3.2     # Wrong
    ```

=== "Server Connection Failed"
    
    **Error:** `Connection refused` or `Cannot connect to server`
    
    **Solution:**
    ```bash
    # Check if server is running
    # For Ollama: ollama serve
    # For MLX: super model server mlx phi-2 --port 8000
    # For LM Studio: Start in LM Studio app
    # For HuggingFace: super model server huggingface model --port 8001
    ```

=== "Port Already in Use"
    
    **Error:** `Address already in use`
    
    **Solution:**
    ```bash
    # Use different port
    super model server mlx phi-2 --port 8001
    super model server huggingface microsoft/Phi-4 --port 8002
    ```

=== "Apple Silicon Required"
    
    **Error:** `MLX requires Apple Silicon`
    
    **Solution:**
    ```bash
    # Use Ollama instead
    super model install qwen3.5:2b
    super model dspy ollama/qwen3.5:2b
    ```

=== "Missing Python Packages"
    
    **Error:** `ModuleNotFoundError: No module named 'mlx_lm'` or `ModuleNotFoundError: No module named 'transformers'`
    
    **Solution:**
    ```bash
    # Install MLX dependencies
    pip install mlx-lm
    
    # Install HuggingFace dependencies
    pip install transformers torch fastapi uvicorn
    
    # Or install with SuperOptiX extras
    pip install "superoptix[mlx]"
    pip install "superoptix[huggingface]"
    ```

=== "Missing CLI Tools"
    
    **Error:** `Command 'ollama' not found` or `Command 'lms' not found`
    
    **Solution:**
    ```bash
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Install LM Studio
    # Download from https://lmstudio.ai
    # Or use winget on Windows:
    winget install LMStudio.LMStudio
    
    # Verify installation
    ollama --version
    lms --version
    ```

=== "Authentication Errors"
    
    **Error:** `401 Unauthorized` or `Repository Not Found`
    
    **Solution:**
    ```bash
    # For HuggingFace models, login:
    huggingface-cli login
    
    # For MLX models, ensure you have access:
    # Some models require accepting terms on HuggingFace website
    
    # Use public models instead:
    super model install -b mlx mlx-community/phi-2
    super model install -b huggingface microsoft/Phi-4
    ```

## 🎉 Next Steps

Now that you have your local models set up:

1. **🚀 [Quick Start Guide](quick-start.md)** - Build your first agent with local models
2. **🤖 [Create Your First Genies Agent](tutorials/genies-agent.md)** - Step-by-step tutorial
3. **🏪 [Marketplace](guides/marketplace.md)** - Discover pre-built agents
4. **🔍 [Model Intelligence Guide](guides/model-intelligence.md)** - Advanced model management

## 💬 Need Help?

- **📖 [Documentation](index.md)** - Comprehensive guides
- **🐛 [Support Portal](https://support.super-agentic.ai)** - Report bugs

---

<div style="background: linear-gradient(90deg, #ede9fe, #fbcfe8, #fef3c7, #fdf6e3, #ede9fe); border-radius: 18px; padding: 2.2rem 1.2rem; margin: 2.2rem 0; box-shadow: 0 4px 24px 0 rgba(124,58,237,0.10);">
<h2 style="margin-top:0;">🤖 Ready to Run Local Models?</h2>
</div>

## 🤗 HuggingFace

**HuggingFace** offers access to thousands of models, perfect for advanced users who want maximum flexibility.

### 🚀 Setup HuggingFace

```bash
# Install HuggingFace dependencies
pip install transformers torch fastapi uvicorn

# Or install with SuperOptiX
pip install "superoptix[huggingface]"
```

### 📦 Install HuggingFace Models

```bash
# Install popular models
super model install -b huggingface microsoft/Phi-4
super model install -b huggingface microsoft/DialoGPT-small
super model install -b huggingface microsoft/DialoGPT-medium
super model install -b huggingface meta-llama/Llama-2-7b-chat-hf
```

### 🖥️ Start HuggingFace Servers

```bash
# Start server with specific model
super model server huggingface microsoft/Phi-4 --port 8001
super model server huggingface microsoft/DialoGPT-small --port 8001
super model server huggingface microsoft/DialoGPT-medium --port 8001
```

**Example Output:**
```
🤗 HuggingFace Local Server
Starting HuggingFace server for microsoft/DialoGPT-small on port 8002...
🚀 Starting HuggingFace server...
📡 Server will be available at: http://localhost:8002
💡 Use this URL in your playbook's api_base configuration
🔧 Manual server startup command:
   python -m superoptix.models.backends.huggingface_server microsoft/DialoGPT-small --port 8002
📋 Example playbook configuration:
   language_model:
     provider: huggingface
     model: microsoft/DialoGPT-small
     api_base: http://localhost:8002
Device set to use cpu
INFO:     Started server process [4652]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```

### 📋 Manage HuggingFace Models

```bash
# List HuggingFace models
super model list --backend huggingface
```

**Example Output:**
```
                🚀 SuperOptiX Model Intelligence - 2 models                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┓
┃ Model                    ┃    Backend     ┃    Status    ┃ Size  ┃ Task ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━┩
│ microsoft/DialoGPT-small │ 🤗 huggingface │ installed │ small │ chat │
│ microsoft/Phi-4          │ 🤗 huggingface │ installed │ small │ chat │
└──────────────────────────┴────────────────┴──────────────┴───────┴──────┘
```

```bash
# Get model information
super model info microsoft/Phi-4
super model info microsoft/DialoGPT-small

# Models are ready to use with SuperOptiX agents
```
