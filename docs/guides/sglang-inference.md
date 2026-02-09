# ⚡ SGLang Production Inference

<div align="center">
  <img src="../logo.png" alt="SuperOptiX Logo" width="150" style="margin-bottom: 10px;"/>
  <h2 style="margin-top: 10px; margin-bottom: 10px;">SGLang High-Performance Inference</h2>
  <p style="margin-top: 10px; margin-bottom: 20px;"><strong>Structured generation and fast inference with SGLang</strong></p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="../model-management/" style="background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🧠 Model Management</a>
  <a href="./vllm-inference/" style="background: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 vLLM</a>
  <a href="../cloud-inference/" style="background: #FF9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">☁️ Cloud Inference</a>
</div>

---

## 🎯 What is SGLang?

**SGLang** (Structured Generation Language) is a fast serving framework for large language models and vision language models with:

- **Structured Generation**: Native support for constrained output formats (JSON, regex, etc.)
- **RadixAttention**: Advanced KV cache reuse across requests
- **High Performance**: Competitive with or faster than vLLM on many workloads
- **OpenAI Compatible**: Drop-in replacement for OpenAI API

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h3 style="color: #4CAF50;">Unique Features</h3>
      <ul>
        <li>Structured output generation (JSON, regex)</li>
        <li>RadixAttention for cache reuse</li>
        <li>Faster than vLLM on structured tasks</li>
        <li>Multi-modal support (Vision + Language)</li>
        <li>OpenAI API compatible</li>
      </ul>
    </td>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h3 style="color: #2196F3;">🎯 Best For</h3>
      <ul>
        <li>Structured data extraction</li>
        <li>JSON output requirements</li>
        <li>Agentic workflows with tools</li>
        <li>Multi-modal applications</li>
        <li>High cache-hit workloads</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Installation

### Option 1: pip

```bash
# Install SGLang
pip install "sglang[all]"

# Or minimal install
pip install sglang
```

### Option 2: Docker

```bash
# Pull SGLang Docker image
docker pull lmsysorg/sglang:latest

# Run SGLang server
docker run --gpus all \
    -p 30000:30000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --ipc=host \
    lmsysorg/sglang:latest \
    python3 -m sglang.launch_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 30000
```

---

## 🔧 Configuration

### Start SGLang Server

```bash
# Basic SGLang server
python -m sglang.launch_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 30000

# With advanced settings
python -m sglang.launch_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 30000 \
    --tp 2 \
    --mem-fraction-static 0.9 \
    --max-running-requests 256
```

### SuperOptiX Configuration

```yaml
spec:
  language_model:
    provider: openai  # SGLang is OpenAI API compatible
    model: meta-llama/Llama-3-8B-Instruct
    api_base: http://localhost:30000/v1
    api_key: "dummy"  # SGLang doesn't require real API key
    temperature: 0.7
    max_tokens: 1000
```

---

## 🎯 Structured Generation

SGLang's killer feature is structured output:

### JSON Schema Enforcement

```python
from sglang import function, gen

@function
def extract_info(s, text):
    s += f"Extract structured info from: {text}\n"
    s += gen("output", max_tokens=200, 
             regex=r'\{"name": "[^"]+", "age": \d+, "email": "[^"]+"}\')

# Guaranteed JSON output!
```

### With SuperOptiX

```yaml
spec:
  language_model:
    provider: openai
    model: meta-llama/Llama-3-8B-Instruct
    api_base: http://localhost:30000/v1
    response_format: json_object  # Structured output
  
  output_fields:
    - name: response
      type: str
      format: json  # Enforce JSON
```

---

## 📊 vLLM vs SGLang Comparison

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Feature</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">vLLM</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">SGLang</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Throughput</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Excellent</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Excellent </strong></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Structured Output</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Basic</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">Advanced 🏆</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Cache Reuse</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Good</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">RadixAttention 🚀</strong></td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Multi-Modal</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Limited</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #9C27B0;">Vision + Language </strong></td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Maturity</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Production </strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Emerging ⚡</td>
  </tr>
</table>

---

## 📝 SuperOptiX Integration Example

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: sglang_structured_agent
  id: sglang_structured_agent
  namespace: production
  version: 1.0.0
  level: genies

spec:
  target_framework: dspy
  
  language_model:
    provider: openai  # SGLang is OpenAI compatible
    model: meta-llama/Llama-3-8B-Instruct
    api_base: http://localhost:30000/v1
    api_key: "dummy"
    temperature: 0.7
    max_tokens: 2000
    response_format: json_object  # Structured output!
  
  persona:
    role: Data Extraction Specialist
    goal: Extract structured information accurately
  
  input_fields:
    - name: text
      type: str
  
  output_fields:
    - name: response
      type: str
      format: json
  
  feature_specifications:
    scenarios:
      - name: JSON extraction
        input:
          text: "John Doe is 30 years old, email: john@example.com"
        expected_output:
          response: '{"name": "John Doe", "age": 30}'
          expected_keywords:
            - John Doe
            - "30"
```

---

## 🔄 Usage with SuperOptiX CLI

```bash
# Start SGLang server
python -m sglang.launch_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 30000 &

# Create agent with SGLang
super agent pull assistant_openai

# Update playbook to use SGLang endpoint
# Edit agents/demo/assistant_openai_playbook.yaml:
#   language_model:
#     provider: openai
#     api_base: http://localhost:30000/v1

# Compile and run
super agent compile assistant_openai
super agent run assistant_openai --goal "Extract info: Alice, age 25, alice@email.com"
```

---

## 🚀 Next Steps

<div align="center" style="margin: 30px 0;">
  <a href="./vllm-inference/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 Try vLLM</a>
  <a href="../model-management/" style="background: #2196F3; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🧠 Model Management</a>
  <a href="../cloud-inference/" style="background: #FF9800; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">☁️ Cloud Inference</a>
</div>

---

## 📚 Resources

- **Official Documentation**: [https://sglang.readthedocs.io](https://sglang.readthedocs.io)
- **GitHub**: [https://github.com/sgl-project/sglang](https://github.com/sgl-project/sglang)
- **Paper**: "SGLang: Efficient Execution of Structured Language Model Programs"

