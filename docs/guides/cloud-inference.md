# 🌐 Cloud Inference with SuperOptiX

## 🎯 **What is Cloud Inference?**

**Cloud Inference** in SuperOptiX enables you to leverage powerful cloud-based language models (OpenAI, Anthropic, Google, and 100+ other providers) for enhanced AI agent capabilities. SuperOptiX provides seamless integration with **ALL LiteLLM providers** through DSPy, giving you access to the world's most advanced AI models.

### **Why Cloud Inference?**

```mermaid
graph LR
    A[Local Models] --> B[Limited Capabilities]
    B --> C[Basic Tasks]
    C --> D[Oracles Tier]
    
    E[Cloud Models] --> F[Advanced Capabilities]
    F --> G[Complex Reasoning]
    G --> H[Genies Tier]
    H --> I[Production Ready]
    
    style A fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff
    style B fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff
    style C fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff
    style E fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    style F fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    style G fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    style H fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    style I fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
```

### **⚠️ Important: Responsible AI Usage**

> **🚨 COST AWARENESS IS CRITICAL!**
> 
> Cloud inference can be **expensive**, especially during optimization. SuperOptiX is powerful, but you must use it **responsibly** and monitor your costs carefully.

## 🚀 **Quick Start: Cloud LLM Setup**

### **Step 1: Environment Setup**

```bash
# Initialize your project
super init cloud_agent_project
cd cloud_agent_project

# Create .env file for API keys
touch .env
```

### **Step 2: Configure API Keys**

```bash
# .env file - NEVER commit this file!
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
GROQ_API_KEY=your-groq-key-here
# Add other providers as needed
```

### **Step 3: Create Cloud Agent Playbook**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Cloud Assistant
  id: cloud_assistant
  namespace: general
  version: 1.0.0
  agent_type: Supervised
  level: genies
  description: An agent using cloud LLM for enhanced capabilities

spec:
  language_model:
    location: cloud                    # REQUIRED for cloud providers
    provider: openai                  # or "anthropic", "google", etc.
    model: gpt-4o                     # or "claude-3-opus-20240229"
    temperature: 0.7                  # OPTIONAL - Controls randomness
    max_tokens: 2000                  # OPTIONAL - Limit output length
    top_p: 1.0                        # OPTIONAL - Nucleus sampling
    cache: true                       # OPTIONAL - Enable caching
    num_retries: 3                    # OPTIONAL - Retry on failure

  persona:
    name: CloudBot
    role: AI Assistant
    goal: Provide helpful responses using cloud LLM capabilities
    traits: ["helpful", "knowledgeable", "precise"]

  tasks:
    - name: answer_question
      instruction: "Answer the user's question with clear reasoning and helpful information."
      inputs:
        - name: question
          type: str
          description: "The user's question"
          required: true
      outputs:
        - name: answer
          type: str
          description: "Comprehensive answer to the question"

  agentflow:
    - name: generate_answer
      type: Generate
      task: answer_question

  # Advanced techniques for Genies tier
  tools:
    enabled: true
    categories:
    - core
    - utilities

  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1000

  evaluation:
    builtin_metrics:
    - name: answer_correctness
      threshold: 0.8

  optimization:
    strategy: few_shot_bootstrapping
    metric: answer_correctness
    metric_threshold: 0.7
    few_shot_bootstrapping_config:
      max_bootstrapped_demos: 3  # Keep low to control costs
      max_rounds: 1
```

### **Step 4: Compile and Run**

```bash
# Compile the agent
super agent compile cloud_assistant

# Test with a simple query
super agent run cloud_assistant --input "What is machine learning?"

# Run evaluation (establishes baseline)
super agent evaluate cloud_assistant

# Optimize (⚠️ This can be expensive!)
super agent optimize cloud_assistant

# Re-evaluate to measure improvement
super agent evaluate cloud_assistant
```

## 🌍 **Supported Cloud Providers**

SuperOptiX supports **ALL LiteLLM providers** through DSPy integration:

### **Major Cloud Providers**

| Provider | Models | API Key Variable | Cost per 1K tokens | Best For |
|----------|--------|------------------|-------------------|----------|
| **OpenAI** | GPT-4, GPT-3.5 | `OPENAI_API_KEY` | $0.005-0.03 | General purpose, coding |
| **Anthropic** | Claude | `ANTHROPIC_API_KEY` | $0.015-0.075 | Reasoning, analysis |
| **Google** | Gemini | `GOOGLE_API_KEY` | $0.0005-0.007 | Cost-effective, multimodal |
| **Azure** | Azure OpenAI | `AZURE_OPENAI_API_KEY` | $0.005-0.03 | Enterprise, compliance |
| **Mistral** | Mistral AI | `MISTRAL_API_KEY` | $0.002-0.014 | Fast, cost-effective |
| **Cohere** | Command | `COHERE_API_KEY` | $0.001-0.015 | RAG, embeddings |
| **Groq** | Fast Inference | `GROQ_API_KEY` | $0.0001-0.0008 | Ultra-fast inference |
| **DeepSeek** | DeepSeek | `DEEPSEEK_API_KEY` | $0.001-0.014 | Coding, reasoning |

### **Cost-Effective Alternatives**

| Provider | Models | Cost per 1K tokens | Use Case |
|----------|--------|-------------------|----------|
| **Together AI** | Open Models | $0.0002-0.002 | Development, testing |
| **Fireworks AI** | Custom Models | $0.0001-0.001 | High-performance, low-cost |
| **Perplexity** | Search + AI | $0.001-0.005 | Research, search |
| **OpenRouter** | Model Aggregator | $0.0001-0.015 | Multiple providers |
| **Replicate** | Open Source Models | $0.0001-0.001 | Custom models |

## 💰 **Cost Management: Critical Guidelines**

> **📊 IMPORTANT: Data and pricing information in this guide is for reference only and can change anytime. Do not take it for granted. Always check current pricing with your chosen provider before making decisions.**

### **🚨 OPTIMIZATION COST WARNING**

> **⚠️ OPTIMIZATION CAN BE VERY EXPENSIVE!**
> 
> The `super agent optimize` command can make **hundreds or thousands of API calls** depending on your configuration. Always start with conservative settings.

### **Cost Estimation Examples**

| Model | Input Tokens | Output Tokens | Cost per 1K tokens | Optimization Calls | Estimated Cost |
|-------|--------------|---------------|-------------------|-------------------|----------------|
| GPT-4o | 1000 | 500 | $0.005 | 100 | $0.50 |
| GPT-4o | 1000 | 500 | $0.005 | 1000 | $5.00 |
| Claude-3-Opus | 1000 | 500 | $0.015 | 100 | $1.50 |
| Claude-3-Opus | 1000 | 500 | $0.015 | 1000 | $15.00 |
| GPT-4o-mini | 1000 | 500 | $0.00015 | 1000 | $0.15 |

### **Cost Control Strategies**

#### **1. Development Workflow (Cost-Effective)**

```bash
# Start with cheaper models for development
super spec generate oracle dev_agent --namespace development

# Edit playbook to use cost-effective model
spec:
  language_model:
    location: cloud
    provider: openai
    model: gpt-4o-mini  # Much cheaper than gpt-4o
    temperature: 0.7
    max_tokens: 1000    # Limit output length
    cache: true         # Enable caching
```

#### **2. Conservative Optimization Settings**

```yaml
optimization:
  strategy: few_shot_bootstrapping
  metric: answer_correctness
  metric_threshold: 0.7
  few_shot_bootstrapping_config:
    max_bootstrapped_demos: 2  # Keep very low
    max_rounds: 1              # Single round only
```

#### **3. Usage Monitoring**

```bash
# Monitor your usage in real-time
super observability dashboard

# Check token usage in traces
super agent inspect your_agent

# Set up usage alerts
export OPENAI_USAGE_ALERT=10  # Alert at $10
export ANTHROPIC_USAGE_ALERT=10
```

#### **4. Caching Strategy**

```yaml
spec:
  language_model:
    location: cloud
    provider: openai
    model: gpt-4o
    cache: true              # Cache responses
    cache_in_memory: true    # Use memory cache
    num_retries: 2           # Limit retries
```

## 🔧 **Provider-Specific Configurations**

### **OpenAI (Most Popular)**

```yaml
spec:
  language_model:
    location: cloud
    provider: openai
    model: gpt-4o              # Latest model
    # Alternative models:
    # model: gpt-4o-mini       # Cheaper option
    # model: gpt-3.5-turbo     # Budget option
    temperature: 0.7
    max_tokens: 2000
    top_p: 1.0
    frequency_penalty: 0.0
    presence_penalty: 0.0
    cache: true
    num_retries: 3
```

### **Anthropic Claude (Best for Reasoning)**

```yaml
spec:
  language_model:
    location: cloud
    provider: anthropic
    model: claude-3-opus-20240229    # Most capable
    # Alternative models:
    # model: claude-3-sonnet-20240229  # Balanced
    # model: claude-3-haiku-20240307   # Fastest
    temperature: 0.7
    max_tokens: 2000
    top_p: 1.0
    cache: true
```

### **Google Gemini (Cost-Effective)**

```yaml
spec:
  language_model:
    location: cloud
    provider: google
    model: gemini-pro              # Text model
    # model: gemini-pro-vision     # Multimodal
    temperature: 0.7
    max_tokens: 2000
    cache: true
```

### **Groq (Ultra-Fast)**

```yaml
spec:
  language_model:
    location: cloud
    provider: groq
    model: llama3-70b-8192         # Very fast
    # model: mixtral-8x7b-32768    # Alternative
    temperature: 0.7
    max_tokens: 2000
    cache: true
```

### **Together AI (Cost-Effective Development)**

```yaml
spec:
  language_model:
    location: cloud
    provider: together-ai
    model: meta-llama/Llama-3.1-405B-Instruct
    temperature: 0.7
    max_tokens: 2000
    cache: true
```

## 🎯 **Best Practices for Cloud Inference**

### **✅ DO's**

#### **1. Start Small and Scale Up**

```bash
# Phase 1: Development with cheap models
super spec generate oracle dev_agent
# Use gpt-4o-mini or gemini-pro

# Phase 2: Testing with better models
# Switch to gpt-4o or claude-3-sonnet

# Phase 3: Production with best models
# Use gpt-4o or claude-3-opus
```

#### **2. Use Conservative Optimization**

```yaml
optimization:
  strategy: few_shot_bootstrapping
  metric: answer_correctness
  metric_threshold: 0.7
  few_shot_bootstrapping_config:
    max_bootstrapped_demos: 2  # Start very low
    max_rounds: 1              # Single round
```

#### **3. Implement Caching**

```yaml
spec:
  language_model:
    location: cloud
    provider: openai
    model: gpt-4o
    cache: true              # Essential for cost control
    cache_in_memory: true    # Fast access
```

#### **4. Monitor Usage Religiously**

```bash
# Set up monitoring
super observability dashboard

# Check usage before optimization
super agent inspect your_agent --show-usage

# Set budget alerts
export OPENAI_USAGE_ALERT=5   # Alert at $5
```

### **❌ DON'Ts**

#### **1. Don't Skip Cost Monitoring**

```bash
# ❌ Bad: No monitoring
super agent optimize expensive_agent

# ✅ Good: Monitor first
super agent inspect expensive_agent --show-usage
super agent optimize expensive_agent --max-iterations 5
```

#### **2. Don't Use Expensive Models for Development**

```yaml
# ❌ Bad: Expensive for development
spec:
  language_model:
    provider: openai
    model: gpt-4o  # Expensive

# ✅ Good: Cost-effective for development
spec:
  language_model:
    provider: openai
    model: gpt-4o-mini  # Much cheaper
```

#### **3. Don't Ignore Rate Limits**

```yaml
# ❌ Bad: No rate limiting
spec:
  language_model:
    provider: openai
    model: gpt-4o

# ✅ Good: Proper rate limiting
spec:
  language_model:
    provider: openai
    model: gpt-4o
    num_retries: 3
    request_timeout: 30
    cache: true
```

## 🔍 **Troubleshooting Cloud Inference**

### **Common Issues and Solutions**

#### **1. API Key Not Found**

```bash
# Error: OpenAI API key not found

# Solution: Check your .env file
cat .env | grep OPENAI_API_KEY

# Make sure the key is set correctly
export OPENAI_API_KEY=your-actual-key-here
```

#### **2. Rate Limiting**

```bash
# Error: Rate limit exceeded

# Solution: Add delays and retries
spec:
  language_model:
    location: cloud
    provider: openai
    model: gpt-4o
    num_retries: 5
    request_timeout: 60
    cache: true  # Reduce API calls
```

#### **3. High Costs**

```bash
# Monitor usage
super observability dashboard

# Check token usage
super agent inspect your_agent --show-usage

# Switch to cheaper model
# Edit playbook: model: gpt-4o-mini
```

#### **4. Model Not Found**

```bash
# Error: Model not found

# Solution: Use exact model identifiers
# OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
# Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229
# Google: gemini-pro, gemini-pro-vision
```

### **Debug Commands**

```bash
# Test API connection
super agent evaluate your_agent --verbose

# Check configuration
super agent inspect your_agent

# Monitor real-time usage
super observability dashboard --live

# View detailed traces
super agent inspect your_agent --show-traces
```



## 🎯 **Summary: Responsible Cloud Inference**

### **Key Principles**

1. **🎯 Start Small**: Use cost-effective models for development
2. **💰 Monitor Costs**: Always track your usage and set alerts
3. **🔄 Cache Aggressively**: Reduce redundant API calls
4. **⚡ Optimize Conservatively**: Use minimal optimization settings
5. **🔒 Secure Keys**: Never commit API keys to version control
6. **📊 Track Performance**: Monitor both cost and quality metrics

### **Cost-Effective Workflow**

```bash
# 1. Development (Cheap)
super spec generate oracle dev_agent
# Use gpt-4o-mini or gemini-pro

# 2. Testing (Balanced)
# Switch to gpt-4o or claude-3-sonnet

# 3. Production (Best)
# Use gpt-4o or claude-3-opus with caching

# 4. Monitor (Always)
super observability dashboard
```

### **Quick Reference**

| Phase | Model | Cost | Use Case |
|-------|-------|------|----------|
| **Development** | gpt-4o-mini | $0.00015/1K | Coding, testing |
| **Testing** | gpt-4o | $0.005/1K | Validation |
| **Production** | gpt-4o | $0.005/1K | Live deployment |

---

**Remember**: SuperOptiX is powerful, but **use it responsibly**! Monitor your costs, start small, and scale up gradually. The key to successful cloud inference is finding the right balance between performance and cost. 🚀

💡 **Pro Tip**: Always test with cheaper models first, and only use expensive models when you're confident in your configuration and have proper cost monitoring in place! 