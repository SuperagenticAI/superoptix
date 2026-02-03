# Model Management Guide

SuperOptiX provides a unified model management system that supports multiple backends including Ollama, MLX, HuggingFace, LM Studio, vLLM, and SGLang. This guide covers how to install, manage, and use models across different backends.

## Quick Start

The easiest way to use models is with the `super model run` command:

```bash
# Run a model with auto-installation
super model run llama3.2:3b "Write a Python function to add two numbers"

# Specify backend explicitly
super model run llama3.2:3b "Write a hello world program" --backend ollama

# Interactive mode
super model run llama3.2:3b "" --interactive
```

## Installing Models

### Basic Installation

```bash
# Install Ollama model (default backend)
super model install llama3.2:3b --backend ollama

# Install MLX model
super model install mlx-community/Llama-3.2-3B-Instruct-4bit --backend mlx

# Install HuggingFace model
super model install microsoft/phi-1_5 --backend huggingface
```

### Backend-Specific Installation

Each backend has different installation methods:

- **Ollama**: Uses `ollama pull` internally
- **MLX**: Downloads from HuggingFace Hub and converts to MLX format
- **HuggingFace**: Downloads using transformers library
- **LM Studio**: Manual installation via desktop app

### GPT-OSS (OpenAI's Open Source)
- **Best for:** Advanced reasoning, complex tasks
- **Models:** GPT-OSS-20B, GPT-OSS-120B
- **Installation:** 
  - `super model install gpt-oss:20b` (Ollama - best performance)
  - `super model install lmstudio-community/gpt-oss-20b-MLX-8bit --backend mlx` (Apple Silicon - native support)
- `super model install openai/gpt-oss-20b --backend huggingface` (Limited on Apple Silicon)
- **Execution:** Direct inference
- **Features:** Apache 2.0 license, MXFP4 quantization, Apple Silicon native support
- **Resources:** [GPT-OSS-120B](https://huggingface.co/openai/gpt-oss-120b), [GPT-OSS-20B](https://huggingface.co/openai/gpt-oss-20b), [Ollama Library](https://ollama.com/library/gpt-oss)

### MLX
- **Best for:** Apple Silicon optimization, GPT-OSS native support
- **Models:** MLX-community models, GPT-OSS models
- **Installation:** Downloads from HuggingFace Hub
- **Execution:** Direct MLX-LM inference
- **Features:** Native Apple Silicon support for GPT-OSS models

## Running Models

### Basic Usage

```bash
# Run with auto-detection
super model run <model_name> "<prompt>"

# Examples
super model run llama3.2:3b "Write a Python function to calculate fibonacci"
super model run mlx-community/phi-2 "Explain quantum computing in simple terms"
super model run microsoft/phi-1_5 "Write a simple calculator program"
```

### Interactive Mode

```bash
# Start interactive session
super model run <model_name> "" --interactive

# Example
super model run llama3.2:3b "Write a story" --interactive
```

### Advanced Parameters

```bash
# Control generation parameters
super model run llama3.2:3b "Write a story" --temperature 0.9
super model run llama3.2:3b "Explain AI" --max-tokens 500
super model run llama3.2:3b "Write a poem" --temperature 0.8 --max-tokens 200
```

### Backend-Specific Examples

## 🤖 GPT-OSS Models

SuperOptiX now supports OpenAI's latest open-source language models: **GPT-OSS-20B** and **GPT-OSS-120B**. These models are designed for advanced reasoning and agentic tasks.

### 🎯 GPT-OSS Model Overview

| Model | Parameters | Active Parameters | Best For | Hardware Requirements |
|-------|------------|-------------------|----------|----------------------|
| **GPT-OSS-20B** | 21B | 3.6B | Lower latency, local/specialized use cases | 16GB+ RAM |
| **GPT-OSS-120B** | 117B | 5.1B | Production, general purpose, high reasoning | Single H100 GPU |

### 🚀 Key Features

- **🔓 Apache 2.0 License**: Build freely without copyleft restrictions
- **⚡ Native MXFP4 Quantization**: Optimized for efficient inference

### 📦 Installing GPT-OSS Models

#### Via MLX-LM (Apple Silicon - Native Support)

```bash
# Install GPT-OSS models via MLX-LM (Apple Silicon only)
super model install openai_gpt-oss-20b --backend mlx
super model install lmstudio-community/gpt-oss-120b-MLX-8bit --backend mlx

# Test the models
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "Explain quantum computing with detailed reasoning" --backend mlx
```

#### Via Ollama (Cross-Platform - Best Performance)

```bash
# Install GPT-OSS models
super model install gpt-oss:20b
super model install gpt-oss:120b

# Test the models
super model run gpt-oss:20b "Explain quantum computing with detailed reasoning" --backend ollama
```

#### Via HuggingFace (Limited on Apple Silicon)

```bash
# Install GPT-OSS models via MLX (Apple Silicon - Recommended)
super model install lmstudio-community/gpt-oss-20b-MLX-8bit --backend mlx
super model install lmstudio-community/gpt-oss-120b-MLX-8bit --backend mlx

# Test the models
super model run lmstudio-community/gpt-oss-20b-MLX-8bit "Explain quantum computing with detailed reasoning" --backend mlx
```

#### Via HuggingFace

```bash
# Install via MLX (Apple Silicon - Recommended)
super model install lmstudio-community/gpt-oss-20b-MLX-8bit --backend mlx
super model install lmstudio-community/gpt-oss-120b-MLX-8bit --backend mlx

# Start server
super model server mlx lmstudio-community/gpt-oss-20b-MLX-8bit --port 8000
```

### 🎯 Using GPT-OSS Models

```bash
# Simple question
super model run gpt-oss:20b "What is 2+2?"

# Explain a concept
super model run gpt-oss:20b "Explain machine learning"

# Complex task
super model run gpt-oss:20b "Design a distributed system architecture"
```

### 🔧 Basic Usage Examples

```bash
# Simple calculation
super model run gpt-oss:20b "Calculate the factorial of 10"

# Get information
super model run gpt-oss:20b "What's the latest news about AI?"

# Complex problem solving
super model run gpt-oss:120b "Solve: A train leaves station A at 2 PM traveling at 60 mph. Another train leaves station B at 3 PM traveling at 80 mph. When will they meet if the stations are 300 miles apart?"
```

### 🎯 Performance Recommendations

| Use Case | Recommended Model | Hardware |
|----------|------------------|----------|
| **Quick responses** | GPT-OSS-20B | 16GB+ RAM |
| **Complex tasks** | GPT-OSS-120B | H100 GPU |
| **Local development** | GPT-OSS-20B | 16GB+ RAM |

## Auto-Installation

Models are automatically installed when they're not found:
>>>>>>> open

```bash
# Ollama models
super model run llama3.2:3b "Hello world"

# MLX models
super model run mlx-community/Llama-3.2-3B-Instruct-4bit "Hello world"

# HuggingFace models
super model run microsoft/phi-1_5 "Hello world"
```

## Managing Models

### Listing Models

```bash
# List all installed models
super model list

# List by backend
super model list --backend ollama
super model list --backend mlx
super model list --backend huggingface

# Filter by size
super model list --size small

# Filter by task
super model list --task code
```

### Removing Models

```bash
# Remove from specific backend
super model remove llama3.2:3b --backend ollama

# Remove from all backends
super model remove llama3.2:3b --all-backends

# Auto-detect backend
super model remove llama3.2:3b
```

### Getting Model Information

```bash
# Get detailed model info
super model info llama3.2:3b

# Get info for specific backend
super model info microsoft/phi-1_5 --backend huggingface
```

### Refreshing Cache

```bash
# Refresh model cache
super model refresh
```

## Backend-Specific Features

### MLX Commands

MLX provides advanced features for Apple Silicon optimization:

```bash
# Convert HuggingFace models to MLX
super model mlx convert microsoft/phi-2 --output phi-2-mlx

# Quantize MLX models
super model mlx quantize phi-2-mlx --bits 4 --group-size 64

# Finetune MLX models
super model mlx finetune phi-2-mlx training_data --type lora --iters 1000

# Evaluate MLX models
super model mlx evaluate phi-2-mlx --tasks mmlu,arc,hellaswag

# Fuse adapters into base model
super model mlx fuse phi-2-mlx --adapter-path adapters --save-path fused_model
```

### MLX Evaluation

Evaluate MLX models on standardized benchmarks using LM-Eval integration:

```bash
# Basic evaluation
super model mlx evaluate phi-2-mlx --tasks mmlu,arc,hellaswag

# Advanced evaluation with custom parameters
super model mlx evaluate phi-2-mlx \
  --tasks mmlu,arc,hellaswag \
  --output-dir results \
  --batch-size 32 \
  --shots 5 \
  --limit 100 \
  --seed 42

# Evaluation with chat template
super model mlx evaluate phi-2-mlx \
  --tasks mmlu \
  --chat-template \
  --max-tokens 2048
```

**Setup Requirements:**
```bash
# Install evaluation dependencies
pip install lm_eval

# Verify MLX-LM installation
python -c "import mlx_lm; print('MLX-LM ready')"
```

**Dependencies:**
- `lm_eval` - Required for evaluation (install with: `pip install lm_eval`)
- `mlx_lm` - Required for MLX operations

**Supported Tasks:**
- `mmlu` - Massive Multitask Language Understanding
- `arc` - AI2 Reasoning Challenge
- `hellaswag` - HellaSwag
- `winogrande` - Winogrande
- `truthfulqa` - TruthfulQA
- `gsm8k` - Grade School Math 8K

**Evaluation Parameters:**
- `--tasks`: Comma-separated list of evaluation tasks
- `--output-dir`: Directory to save results
- `--batch-size`: Batch size for evaluation (default: 16)
- `--shots`: Number of few-shot examples
- `--limit`: Limit examples per task
- `--seed`: Random seed for reproducibility
- `--max-tokens`: Maximum tokens for generation
- `--chat-template`: Use chat template for evaluation

### MLX Fusion

Fuse finetuned adapters (LoRA/DoRA) into base models for deployment:

```bash
# Basic fusion
super model mlx fuse phi-2-mlx --adapter-path adapters

# Fusion with dequantization
super model mlx fuse phi-2-mlx --adapter-path adapters --dequantize

# Fusion with GGUF export
super model mlx fuse phi-2-mlx \
  --adapter-path adapters \
  --export-gguf \
  --gguf-path phi-2-fused.gguf

# Fusion with HuggingFace upload
super model mlx fuse phi-2-mlx \
  --adapter-path adapters \
  --upload username/phi-2-fused
```

**Fusion Parameters:**
- `--adapter-path`: Path to trained adapter weights (default: adapters)
- `--save-path`: Output path for fused model (default: fused_model)
- `--dequantize`: Generate a dequantized model
- `--export-gguf`: Export model in GGUF format
- `--gguf-path`: Path for GGUF export (default: ggml-model-f16.gguf)
- `--upload`: HuggingFace repo to upload fused model to

**Supported Model Types for GGUF Export:**
- `llama` - Llama models
- `mixtral` - Mixtral models  
- `mistral` - Mistral models

### MLX Finetuning

```bash
# LoRA finetuning
super model mlx finetune microsoft_phi-2 training_data --type lora --iters 1000

# DoRA finetuning
super model mlx finetune microsoft_phi-2 training_data --type dora --iters 1000

# Full finetuning
super model mlx finetune microsoft_phi-2 training_data --type full --iters 1000
```

### Advanced MLX Configuration

```bash
# Custom LoRA parameters
super model mlx finetune model_name training_data --type lora --rank 8 --scale 20.0

# DoRA with dropout
super model mlx finetune model_name training_data --type dora --rank 8 --dropout 0.1

# Full finetuning with gradient checkpointing
super model mlx finetune model_name training_data --type full --layers 16

# Advanced training configuration
super model mlx finetune model_name training_data \
  --type lora \
  --batch-size 4 \
  --lr 1e-5 \
  --iters 1000 \
  --max-length 2048 \
  --report-steps 10 \
  --eval-steps 200 \
  --save-steps 100

# With WandB logging
super model mlx finetune model_name training_data --wandb my_project

# Resume from checkpoint
super model mlx finetune model_name training_data \
  --resume checkpoint_path \
  --iters 500

# Test after training
super model mlx finetune model_name training_data \
  --test \
  --grad-checkpoint
```

### Training Data Format

MLX finetuning requires JSONL format:

```
training_data/
├── train.jsonl    # Training examples
├── valid.jsonl    # Validation examples
└── test.jsonl     # Test examples
```

Each JSONL file contains one JSON object per line:
```json
{"text": "Your training text here"}
{"text": "Another training example"}
```

### vLLM Commands

vLLM provides high-performance inference for production environments:

```bash
# Serve vLLM models
super model vllm serve llama-2-7b --host 0.0.0.0 --port 8000

# Generate text with vLLM
super model vllm generate llama-2-7b "Explain quantum computing" --max-tokens 200

# Benchmark vLLM models
super model vllm benchmark llama-2-7b --num-requests 100 --request-rate 10

# Quantize vLLM models
super model vllm quantize llama-2-7b --quantization awq --bits 4
```

### vLLM Setup Requirements

**System Requirements:**
- Linux environment (Ubuntu 20.04+ recommended)
- NVIDIA GPU with CUDA support
- CUDA 11.8+ and cuDNN 8.9+
- Python 3.8+

**Dependency Structure:**
- **vLLM is an optional dependency** - not included in base SuperOptiX installation
- Users can install vLLM separately or via SuperOptiX extras
- SuperOptiX provides helpful error messages if vLLM is not available

**Installation Options:**

**Option 1: Install vLLM separately (Recommended)**
```bash
# Install vLLM directly
pip install vllm

# Verify installation
python -c "import vllm; print('✅ vLLM installed')"

# Check GPU support
python -c "from vllm import LLM; print('✅ GPU support available')"
```

**Option 2: Install with SuperOptiX vLLM dependency**
```bash
# Install SuperOptiX with vLLM support
pip install superoptix[vllm]

# Verify installation
python -c "import vllm; print('✅ vLLM installed via SuperOptiX')"
```

**Note:** 
- vLLM is an **optional dependency** that users need to install separately or via the `[vllm]` extra
- SuperOptiX will provide helpful error messages if vLLM is not available when trying to use vLLM commands
- vLLM can run on CPU for testing but requires NVIDIA GPU for optimal performance

### vLLM Serving

Serve models for high-performance inference:

```bash
# Basic serving
super model vllm serve llama-2-7b --host localhost --port 8000

# Multi-GPU serving
super model vllm serve llama-2-7b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9

# Quantized model serving
super model vllm serve llama-2-7b \
  --quantization awq \
  --trust-remote-code \
  --max-model-len 4096
```

**Serving Parameters:**
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8000)
- `--tensor-parallel-size`: Number of GPUs for tensor parallelism
- `--gpu-memory-utilization`: GPU memory utilization (0.0-1.0)
- `--max-model-len`: Maximum model length
- `--quantization`: Quantization method (awq, gptq, squeezellm)
- `--trust-remote-code`: Trust remote code execution
- `--download-dir`: Directory to download models

### vLLM Generation

Generate text with high-performance inference:

```bash
# Basic generation
super model vllm generate llama-2-7b "Write a story about" --max-tokens 200

# Streaming generation
super model vllm generate llama-2-7b "Explain AI:" \
  --max-tokens 500 \
  --temperature 0.8 \
  --stream

# Controlled generation
super model vllm generate llama-2-7b "Complete this:" \
  --max-tokens 100 \
  --temperature 0.1 \
  --top-p 0.9 \
  --stop "END,###"
```

**Generation Parameters:**
- `--max-tokens`: Maximum tokens to generate
- `--temperature`: Sampling temperature (0.0-2.0)
- `--top-p`: Top-p sampling parameter (0.0-1.0)
- `--top-k`: Top-k sampling parameter
- `--stop`: Stop sequences (comma-separated)
- `--stream`: Enable streaming generation
- `--tensor-parallel-size`: Number of GPUs
- `--quantization`: Quantization method

### vLLM Benchmarking

Benchmark models for performance analysis:

```bash
# Basic benchmarking
super model vllm benchmark llama-2-7b \
  --num-requests 100 \
  --request-rate 10

# Performance benchmarking
super model vllm benchmark llama-2-7b \
  --num-requests 1000 \
  --request-rate 50 \
  --prompt-length 512 \
  --max-tokens 128 \
  --tensor-parallel-size 2

# Quantized model benchmarking
super model vllm benchmark llama-2-7b \
  --quantization awq \
  --num-requests 500 \
  --request-rate 25
```

**Benchmarking Parameters:**
- `--num-requests`: Number of requests to process
- `--request-rate`: Requests per second
- `--prompt-length`: Prompt length in tokens
- `--max-tokens`: Maximum tokens to generate
- `--tensor-parallel-size`: Number of GPUs
- `--quantization`: Quantization method

### vLLM Quantization

Quantize models for reduced memory usage:

```bash
# AWQ quantization
super model vllm quantize llama-2-7b \
  --quantization awq \
  --bits 4 \
  --group-size 128

# GPTQ quantization
super model vllm quantize llama-2-7b \
  --quantization gptq \
  --bits 4 \
  --group-size 128 \
  --trust-remote-code

# SqueezeLLM quantization
super model vllm quantize llama-2-7b \
  --quantization squeezellm \
  --bits 4 \
  --group-size 128
```

**Quantization Parameters:**
- `--output-dir`: Output directory (default: quantized_model)
- `--quantization`: Quantization method (awq, gptq, squeezellm)
- `--bits`: Bits for quantization (2, 3, 4, 8)
- `--group-size`: Group size for quantization
- `--trust-remote-code`: Trust remote code execution

### vLLM Troubleshooting

**Common Issues:**
- **CUDA out of memory**: Reduce `--gpu-memory-utilization` or use quantization
- **Model not found**: Ensure model is available on HuggingFace Hub
- **Quantization errors**: Check model compatibility with quantization method
- **Performance issues**: Adjust `--tensor-parallel-size` and `--gpu-memory-utilization`

**Performance Optimization:**
- Use appropriate quantization for memory constraints
- Adjust tensor parallelism based on GPU count
- Monitor GPU memory utilization
- Use appropriate model lengths for your use case

### SGLang Commands

SGLang provides streaming and optimization for production environments:

```bash
# Serve SGLang models
super model sglang serve llama-2-7b --host 0.0.0.0 --port 8000

# Generate text with SGLang
super model sglang generate llama-2-7b "Explain streaming generation" --max-tokens 200

# Optimize SGLang models
super model sglang optimize llama-2-7b --optimization O2

# Benchmark SGLang models
super model sglang benchmark llama-2-7b --num-requests 100 --request-rate 10
```

### SGLang Setup Requirements

**System Requirements:**
- Linux environment (Ubuntu 20.04+ recommended)
- NVIDIA GPU with CUDA support
- CUDA 11.8+ and cuDNN 8.9+
- Python 3.8+

**Dependency Structure:**
- **SGLang is an optional dependency** - not included in base SuperOptiX installation
- Users can install SGLang separately or via SuperOptiX extras
- SuperOptiX provides helpful error messages if SGLang is not available

**Installation Options:**

**Option 1: Install SGLang separately (Recommended)**
```bash
# Install SGLang directly
pip install sglang

# Verify installation
python -c "import sglang; print('✅ SGLang installed')"

# Check GPU support
python -c "from sglang import SGLang; print('✅ GPU support available')"
```

**Option 2: Install with SuperOptiX SGLang dependency**
```bash
# Install SuperOptiX with SGLang support
pip install superoptix[sglang]

# Verify installation
python -c "import sglang; print('✅ SGLang installed via SuperOptiX')"
```

**Note:** 
- SGLang is an **optional dependency** that users need to install separately or via the `[sglang]` extra
- SuperOptiX will provide helpful error messages if SGLang is not available when trying to use SGLang commands
- SGLang can run on CPU for testing but requires NVIDIA GPU for optimal performance

### SGLang Serving

Serve models for streaming and optimization:

```bash
# Basic serving
super model sglang serve llama-2-7b --host localhost --port 8000

# High-performance serving
super model sglang serve llama-2-7b \
  --host 0.0.0.0 \
  --port 8000 \
  --max-batch-size 64 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 512 \
  --gpu-memory-utilization 0.95

# Streaming-optimized serving
super model sglang serve llama-2-7b \
  --max-batch-size 32 \
  --max-num-batched-tokens 4096 \
  --trust-remote-code
```

**Serving Parameters:**
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8000)
- `--max-batch-size`: Maximum batch size (default: 32)
- `--max-num-batched-tokens`: Maximum number of batched tokens (default: 4096)
- `--max-num-seqs`: Maximum number of sequences (default: 256)
- `--gpu-memory-utilization`: GPU memory utilization (0.0-1.0)
- `--trust-remote-code`: Trust remote code execution

### SGLang Generation

Generate text with streaming and optimization:

```bash
# Basic generation
super model sglang generate llama-2-7b "Write a story about" --max-tokens 200

# Streaming generation
super model sglang generate llama-2-7b "Explain AI:" \
  --max-tokens 500 \
  --temperature 0.8 \
  --stream \
  --max-batch-size 16

# Optimized generation
super model sglang generate llama-2-7b "Complete this:" \
  --max-tokens 100 \
  --temperature 0.1 \
  --top-p 0.9 \
  --stop "END,###" \
  --max-batch-size 32
```

**Generation Parameters:**
- `--max-tokens`: Maximum tokens to generate
- `--temperature`: Sampling temperature (0.0-2.0)
- `--top-p`: Top-p sampling parameter (0.0-1.0)
- `--top-k`: Top-k sampling parameter
- `--stop`: Stop sequences (comma-separated)
- `--stream`: Enable streaming generation
- `--max-batch-size`: Maximum batch size

### SGLang Optimization

Optimize models for performance:

```bash
# Performance optimization
super model sglang optimize llama-2-7b \
  --optimization O2 \
  --max-batch-size 64 \
  --max-num-batched-tokens 8192 \
  --gpu-memory-utilization 0.95

# Memory optimization
super model sglang optimize llama-2-7b \
  --optimization O1 \
  --max-batch-size 32 \
  --max-num-batched-tokens 4096 \
  --gpu-memory-utilization 0.8
```

**Optimization Parameters:**
- `--optimization`: Optimization level (O0, O1, O2, O3)
- `--max-batch-size`: Maximum batch size
- `--max-num-batched-tokens`: Maximum number of batched tokens
- `--gpu-memory-utilization`: GPU memory utilization
- `--trust-remote-code`: Trust remote code execution

### SGLang Benchmarking

Benchmark models for performance analysis:

```bash
# Basic benchmarking
super model sglang benchmark llama-2-7b \
  --num-requests 100 \
  --request-rate 10

# Performance benchmarking
super model sglang benchmark llama-2-7b \
  --num-requests 1000 \
  --request-rate 50 \
  --prompt-length 512 \
  --max-tokens 128 \
  --max-batch-size 64

# Streaming benchmarking
super model sglang benchmark llama-2-7b \
  --num-requests 500 \
  --request-rate 25 \
  --prompt-length 256 \
  --max-tokens 64 \
  --max-batch-size 32
```

**Benchmarking Parameters:**
- `--num-requests`: Number of requests to process
- `--request-rate`: Requests per second
- `--prompt-length`: Prompt length in tokens
- `--max-tokens`: Maximum tokens to generate
- `--max-batch-size`: Maximum batch size

### SGLang Troubleshooting

**Common Issues:**
- **CUDA out of memory**: Reduce `--gpu-memory-utilization` or batch size
- **Model not found**: Ensure model is available on HuggingFace Hub
- **Streaming errors**: Check `--max-batch-size` and `--max-num-batched-tokens`
- **Performance issues**: Adjust optimization level and batch parameters

**Performance Optimization:**
- Use appropriate optimization levels (O0-O3) for your use case
- Adjust batch sizes based on GPU memory
- Monitor GPU memory utilization
- Use streaming for real-time applications

## Server Management

### Starting Local Servers

```bash
# Start MLX server
super model server mlx mlx-community/phi-2 --port 8000

# Start HuggingFace server
super model server huggingface microsoft/phi-1_5 --port 8001
```

### Using Servers in Playbooks

```yaml
language_model:
  provider: mlx
  model: mlx-community/phi-2
  api_base: http://localhost:8000
```

### Model Conversion and Quantization

Convert and quantize models for MLX backend:

```bash
# Convert HuggingFace model to MLX format
super model convert microsoft/phi-2 --quantize --bits 4

# Quantize existing MLX model
super model quantize my-model --bits 4 --output my-model-q4

# Dequantize a quantized model
super model quantize my-model-q4 --dequantize --output my-model-dequantized
```

**Note:** These commands are experimental and require MLX backend to be available.

## Troubleshooting

### Common Issues

**Model not found:**
```bash
# Check available models
super model list --backend <backend>

# Install missing model
super model install <model_name> --backend <backend>

# Refresh cache
super model refresh
```

**Backend not working:**
```bash
# Check backend status
super model backends

# Verify installation
super model info <model_name>
```

**LM Studio models:**
- LM Studio models must be installed via the desktop app
- Use `super model server lmstudio <model>` to start server
- Models cannot be removed via CLI (use desktop app)

**MLX Evaluation Issues:**
- **Missing lm_eval**: Install with `pip install lm_eval`
- **Model not found**: Ensure model is properly installed with `super model list --backend mlx`
- **Memory issues**: Use `--limit` to reduce evaluation examples
- **Slow evaluation**: Use `--batch-size` to optimize performance

**MLX Fusion Issues:**
- **Adapter not found**: Check adapter path with `ls adapters/`
- **Model type unsupported**: GGUF export supports llama, mixtral, mistral only
- **Upload failed**: Ensure HuggingFace token is configured
- **Local model not found**: Use full path to local model directory
- **404 HuggingFace error**: Ensure model exists on HuggingFace Hub or use local path

### Auto-Installation Workflow

```bash
# Try to run model (auto-installs if needed)
super model run <model_name> "test"

# Install explicitly if needed
super model install <model_name> --backend <backend>

# Run again
super model run <model_name> "test" --backend <backend>
```

## Best Practices

### Model Selection

- **Small models**: Good for testing and development
- **Medium models**: Balance of performance and resource usage
- **Large models**: Best performance, requires more resources

## Resources

- [SuperOptiX Documentation](https://superoptix.ai) - Complete framework documentation
- [DSPy Framework](https://dspy.ai) - Foundation framework
- [GPT-OSS-120B Model](https://huggingface.co/openai/gpt-oss-120b) - HuggingFace repository
- [GPT-OSS-20B Model](https://huggingface.co/openai/gpt-oss-20b) - HuggingFace repository
- [Ollama Library](https://ollama.com/library/gpt-oss) - Ollama model library

## Next Steps

### Backend Selection

- **Ollama**: Easiest for local development
- **MLX**: Best for Apple Silicon performance
- **HuggingFace**: Widest model support
- **LM Studio**: Good for desktop workflows

### Performance Optimization

```bash
# Use appropriate model sizes
super model list --size small    # For testing
super model list --size medium   # For development
super model list --size large    # For production

# Optimize generation parameters
super model run model "prompt" --max-tokens 100 --temperature 0.7
```

## Examples

### Complete Workflow

```bash
# 1. Discover models
super model discover

# 2. Install model
super model install llama3.2:3b --backend ollama

# 3. Run model
super model run llama3.2:3b "Write a Python function to sort a list"

# 4. Try different model
super model run microsoft/phi-1_5 "Write a JavaScript function to validate email"

# 5. Interactive session
super model run llama3.2:3b "Write a blog post about AI trends"

# 6. Try MLX model
super model run mlx-community/phi-2 "Write a short story about a robot"

# 7. Advanced usage
super model run microsoft/phi-1_5 "Analyze this text: [your text here]"

# 8. Educational
super model run llama3.2:3b "Explain machine learning in simple terms"
``` 

### Testing MLX Features

**1. Verify Dependencies:**
```bash
# Check MLX-LM installation
python -c "import mlx_lm; print('✅ MLX-LM installed')"

# Check LM-Eval installation (for evaluation)
python -c "import lm_eval; print('✅ LM-Eval installed')"
```

**2. Test Command Structure:**
```bash
# Verify all MLX commands are available
super model mlx --help
super model mlx evaluate --help
super model mlx fuse --help
super model mlx finetune --help
super model mlx convert --help
super model mlx quantize --help
```

**3. Test with Real Models:**
```bash
# List available MLX models
super model list --backend mlx

# Test evaluation (requires lm_eval)
super model mlx evaluate microsoft_phi-2 --tasks mmlu --limit 10

# Test fusion (requires adapter files)
super model mlx fuse microsoft_phi-2 --adapter-path ./adapters
```

**4. Common Test Scenarios:**
- **Evaluation**: Test with small models and limited examples
- **Fusion**: Test with existing adapter files from finetuning
- **Error Handling**: Test with non-existent models/paths
- **Performance**: Test with different batch sizes and limits 

## Dependency Overview

SuperOptiX uses a modular dependency structure to keep the base installation lightweight:

### **Core Dependencies** (Always Included)
- Basic CLI functionality
- Model management
- DSPy integration
- Core utilities

### **Optional Dependencies** (Install as needed)

**Backend-Specific:**
```bash
# MLX (Apple Silicon only)
pip install superoptix[mlx]

# vLLM (Linux with NVIDIA GPU)
pip install superoptix[vllm]

# SGLang (Linux with NVIDIA GPU)
pip install superoptix[sglang]

# HuggingFace (Cross-platform)
pip install superoptix[huggingface]
```

**Vector Databases:**
```bash
# Individual databases
pip install superoptix[chromadb]
pip install superoptix[lancedb]
pip install superoptix[weaviate]
pip install superoptix[qdrant]
pip install superoptix[milvus]

# All vector databases
pip install superoptix[vectordb]
```

**Observability:**
```bash
pip install superoptix[observability]
```

**UI Components:**
```bash
pip install superoptix[ui]
```

**Complete Installation:**
```bash
# All features (excluding MLX on non-Apple platforms)
pip install superoptix[all]

# All features including MLX (use with caution on non-Apple platforms)
pip install superoptix[all-with-mlx]
``` 