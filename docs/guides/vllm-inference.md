# 🚀 vLLM Production Inference

<div align="center">
  <img src="../logo.png" alt="SuperOptiX Logo" width="150" style="margin-bottom: 10px;"/>
  <h2 style="margin-top: 10px; margin-bottom: 10px;">vLLM High-Performance Inference</h2>
  <p style="margin-top: 10px; margin-bottom: 20px;"><strong>Production-grade LLM serving with vLLM</strong></p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="../model-management/" style="background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🧠 Model Management</a>
  <a href="../cloud-inference/" style="background: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">☁️ Cloud Inference</a>
  <a href="./sglang-inference/" style="background: #FF9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚡ SGLang</a>
</div>

---

## 🎯 What is vLLM?

**vLLM** is a high-throughput and memory-efficient inference and serving engine for Large Language Models (LLMs). It's designed for production deployments with:

- **High Throughput**: Serve multiple requests efficiently with continuous batching
- **Memory Efficiency**: PagedAttention algorithm reduces memory usage
- **Production Ready**: Built for scale and reliability
- **OpenAI Compatible**: Drop-in replacement for OpenAI API

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h3 style="color: #4CAF50;">Advantages</h3>
      <ul>
        <li>3-10x faster than HuggingFace</li>
        <li>Up to 24x higher throughput</li>
        <li>Reduced memory footprint</li>
        <li>Continuous batching</li>
        <li>OpenAI API compatible</li>
      </ul>
    </td>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h3 style="color: #2196F3;">🎯 Best For</h3>
      <ul>
        <li>Production deployments</li>
        <li>High-volume serving</li>
        <li>Multi-user applications</li>
        <li>Enterprise workloads</li>
        <li>API-based serving</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Installation

### Option 1: pip (Recommended)

```bash
# Install vLLM
pip install vllm

# For CUDA 12.1
pip install vllm

# For CUDA 11.8
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu118
```

### Option 2: Docker

```bash
# Pull vLLM Docker image
docker pull vllm/vllm-openai:latest

# Run vLLM server
docker run --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model meta-llama/Llama-3-8B-Instruct
```

---

## 🔧 Configuration

### Start vLLM Server

```bash
# Basic vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 8000

# With advanced settings
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 8000 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096
```

### SuperOptiX Configuration

```yaml
spec:
  language_model:
    provider: openai  # vLLM is OpenAI API compatible
    model: meta-llama/Llama-3-8B-Instruct
    api_base: http://localhost:8000/v1
    api_key: "dummy"  # vLLM doesn't require real API key
    temperature: 0.7
    max_tokens: 1000
```

---

## 📊 Performance Comparison

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Engine</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Throughput</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Memory</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Latency</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">vLLM</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">24x ⭐</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Low </strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Fast </strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">HuggingFace</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">1x (baseline)</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">High</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Moderate</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">5x</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Medium</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Fast</td>
  </tr>
</table>

---

## 🔬 Advanced Configuration

### Tensor Parallelism (Multi-GPU)

```bash
# Use 4 GPUs
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70B-Instruct \
    --tensor-parallel-size 4 \
    --port 8000
```

### Quantization for Memory Efficiency

```bash
# AWQ 4-bit quantization
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-70B-AWQ \
    --quantization awq \
    --port 8000

# GPTQ quantization
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-70B-GPTQ \
    --quantization gptq \
    --port 8000
```

### Custom Sampling Parameters

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.95 \
    --max-num-seqs 256 \
    --port 8000
```

---

## 📝 SuperOptiX Integration Example

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: vllm_production_agent
  id: vllm_production_agent
  namespace: production
  version: 1.0.0
  level: genies

spec:
  target_framework: dspy
  
  language_model:
    provider: openai  # vLLM is OpenAI compatible
    model: meta-llama/Llama-3-8B-Instruct
    api_base: http://localhost:8000/v1
    api_key: "dummy"
    temperature: 0.7
    max_tokens: 2000
  
  persona:
    role: Production AI Assistant
    goal: Provide fast, reliable responses at scale
  
  input_fields:
    - name: query
      type: str
  
  output_fields:
    - name: response
      type: str
  
  feature_specifications:
    scenarios:
      - name: Performance test
        input:
          query: "Explain vLLM benefits"
        expected_output:
          response: "vLLM explanation"
```

---

## 🔄 Usage with SuperOptiX CLI

```bash
# Initialize project
super init vllm_project
cd vllm_project

# Start vLLM server (in background)
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 8000 &

# Create agent with vLLM
super agent pull assistant_openai

# Update playbook to use vLLM endpoint
# Edit agents/demo/assistant_openai_playbook.yaml:
#   language_model:
#     provider: openai
#     api_base: http://localhost:8000/v1

# Compile and run
super agent compile assistant_openai
super agent run assistant_openai --goal "Hello from vLLM!"
```

---

## 📈 Benchmarks

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Model Size</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">vLLM Tokens/sec</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">HuggingFace Tokens/sec</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Speedup</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">7B</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">~1500</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">~150</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">10x ⚡</strong></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">13B</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">~1000</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">~100</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">10x ⚡</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">70B</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">~300</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">~15</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">20x 🚀</strong></td>
  </tr>
</table>

---

## 🎯 Use Cases

<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="padding: 20px; text-align: center; width: 33%; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h2>🏢</h2>
      <h4>Enterprise APIs</h4>
      <p>Serve thousands of users simultaneously with high throughput</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 33%; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h2>🤖</h2>
      <h4>Multi-Agent Systems</h4>
      <p>Run multiple agents efficiently with batch processing</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 33%; border: 2px solid rgba(255, 152, 0, 0.3); background: rgba(255, 152, 0, 0.05);">
      <h2>⚡</h2>
      <h4>Real-Time Applications</h4>
      <p>Low-latency inference for interactive applications</p>
    </td>
  </tr>
</table>

---

## 🔬 Advanced Features

### PagedAttention

vLLM's revolutionary memory management:

```python
# PagedAttention automatically manages KV cache
# No configuration needed - it just works!
```

### Continuous Batching

```bash
# vLLM automatically batches incoming requests
# Optimal throughput without manual tuning
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --max-num-seqs 256  # Max concurrent sequences
```

### Speculative Decoding

```bash
# Use smaller model for speculation, larger for verification
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70B-Instruct \
    --speculative-model meta-llama/Llama-3-8B-Instruct \
    --num-speculative-tokens 5
```

---

## 🌐 Deployment

### Production Deployment

```bash
# Production settings
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.9 \
    --max-num-seqs 256 \
    --disable-log-requests
```

### Docker Compose

```yaml
version: '3.8'
services:
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    command: >
      --model meta-llama/Llama-3-8B-Instruct
      --tensor-parallel-size 2
      --gpu-memory-utilization 0.9
```

---

## 🚀 Next Steps

<div align="center" style="margin: 30px 0;">
  <a href="./sglang-inference/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚡ Try SGLang</a>
  <a href="../model-management/" style="background: #2196F3; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🧠 Model Management</a>
  <a href="../cloud-inference/" style="background: #FF9800; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">☁️ Cloud Inference</a>
</div>

---

## 📚 Resources

- **Official Documentation**: [https://docs.vllm.ai](https://docs.vllm.ai)
- **GitHub**: [https://github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Paper**: "Efficient Memory Management for Large Language Model Serving with PagedAttention"

