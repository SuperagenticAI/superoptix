# 🤖 Google ADK Integration

## Overview

SuperOptiX now supports **Google ADK (Agent Development Kit)** - Google's code-first Python toolkit optimized for Gemini models. This integration brings GEPA optimization to Google's enterprise-grade agent framework.

**Key Features:**
- ✅ **Gemini 2.0 Flash** integration (Google's latest model!)
- ✅ **GEPA optimization** of agent instructions
- ✅ **Production deployment** (Cloud Run, Vertex AI)
- ✅ **Built-in evaluation** framework
- ✅ **Standard SuperOptiX workflow** (compile/evaluate/optimize/run)

---

## Quick Start

### 1. Prerequisites

**Install SuperOptiX with Google ADK:**

```bash
pip install superoptix[frameworks-google]
```

**Includes:**
- google-adk 1.17.0
- google-generativeai (latest)
- SuperOptiX core with GEPA 0.0.17

**Get a Google API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a free API key
3. Set environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### 2. Create Project

```bash
super init my_project
cd my_project
```

### 3. Pull Demo Agent

```bash
super agent pull assistant_adk
```

### 4. Compile

```bash
super agent compile assistant_adk --framework google-adk
```

### 5. Evaluate

```bash
export GOOGLE_API_KEY="your-key"  # Required!
super agent evaluate assistant_adk
```

### 6. Optimize

```bash
super agent optimize assistant_adk --auto medium
```

### 7. Run

```bash
super agent run assistant_adk --goal "What is AI?"
```

---

## How It Works

### SuperOptiX Workflow with Google ADK

```mermaid
graph LR
    A[SuperSpec YAML] -->|compile| B[Google ADK Python]
    B -->|evaluate| C[BDD Scenarios]
    C -->|optimize| D[GEPA Optimizer]
    D -->|run| E[runner.run]
```

### 1. **Compile**: SuperSpec → Google ADK

**Input:** SuperSpec playbook (YAML)

```yaml
persona:
  role: Helpful AI Assistant
  goal: Provide accurate responses
  backstory: You are powered by Google's Gemini
```

**Output:** Google ADK Python code

```python
from google.adk import Agent, Runner
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = Agent(
    model="gemini-2.0-flash",
    name="assistant_adk",
    description="AI assistant built with Google ADK",
    instruction="""You are a Helpful AI Assistant
Your goal is: Provide accurate, helpful responses
You are powered by Google's Gemini...""",
    tools=[],
)

runner = InMemoryRunner(agent=agent, app_name="superoptix_assistant")
```

### 2. **Evaluate**: Test on BDD Scenarios

```python
# Create session
session = await runner.session_service.create_session(app_name, user_id)

# Run agent
content = types.Content(role='user', parts=[types.Part.from_text(text=query)])
async for event in runner.run_async(user_id, session.id, content):
    response = event.content.parts[0].text
```

### 3. **Optimize**: GEPA Optimizes Instruction

**Optimizable Variable:**

```
You are a Helpful AI Assistant
Your goal is: Provide accurate responses
You are powered by Google's Gemini.
```

**GEPA Process:**
1. Generate 5-10 instruction variations
2. Test each on training scenarios
3. Select best performer
4. Save optimized instruction

**Example Optimized Output:**

```
You are an expert AI assistant specialized in providing accurate, well-researched responses.

Your goal is: Deliver comprehensive answers that are:
  - Factually accurate and up-to-date
  - Well-structured and easy to understand
  - Backed by reasoning and examples
  - Tailored to the user's level of understanding

Your approach:
  1. Carefully analyze the user's question
  2. Break down complex queries into manageable parts
  3. Provide clear, step-by-step explanations
  4. Include relevant examples and analogies
  5. Verify accuracy before responding

Background: You are powered by Google's Gemini 2.0, a state-of-the-art
AI model with advanced reasoning capabilities. You excel at explaining
complex topics clearly and providing actionable insights.
```

### 4. **Run**: Execute with Optimized Instruction

```bash
super agent run assistant_adk --goal "Explain quantum computing"
# Uses optimized instruction → Better results!
```

---

## What GEPA Can Optimize

### Primary Target: Instruction

GEPA optimizes the **instruction** field - the system prompt guiding agent behavior:

| Component | Impact | Example |
|-----------|--------|---------|
| **instruction** | HIGH | "You are a helpful assistant" → "You are an expert AI assistant specializing in..." |

**Why Single Variable?**
- Clear optimization target
- Directly impacts behavior
- Similar to OpenAI SDK (proven successful)
- Measurable improvements

**Note:** Unlike CrewAI (5 variables), Google ADK has **1 optimizable variable** like OpenAI SDK.

---

## Creating Google ADK Agents

### SuperSpec Playbook Structure

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: assistant_adk
  id: assistant_adk
  version: 1.0.0

spec:
  target_framework: google-adk
  
  # LLM Configuration - Gemini models
  language_model:
    provider: google
    model: gemini-2.0-flash  # Free tier!
    # Alternative: gemini-1.5-pro, gemini-1.5-flash
  
  # Input/Output Fields
  input_fields:
    - name: query
      type: str
      required: true
  
  output_fields:
    - name: response
      type: str
      required: true
  
  # Agent Configuration (builds instruction for GEPA)
  persona:
    role: AI Assistant
    goal: Help users with questions
    backstory: |
      You are a helpful AI assistant powered by Gemini.
      You provide accurate, clear responses.
    traits:
      - helpful
      - accurate
  
  reasoning:
    steps:
      - Understand the question
      - Formulate response
      - Provide insights
  
  # BDD Scenarios
  feature_specifications:
    scenarios:
      - name: Simple greeting
        input:
          query: "Hello, how are you?"
        expected_output:
          response: "I am doing well"
          expected_keywords:
            - hello
            - well
```

### Field Mapping: SuperSpec → Google ADK

| SuperSpec Field | Google ADK Field | Usage |
|-----------------|------------------|-------|
| `persona.role` + `goal` + `backstory` | `Agent.instruction` | Combined into instruction |
| `language_model.model` | `Agent.model` | Model name |
| `metadata.description` | `Agent.description` | Agent description |
| `tools` | `Agent.tools` | Tool list |

---

## Model Configuration

### Supported Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-2.0-flash` | Latest, fastest, FREE tier! | ✅ **Recommended** |
| `gemini-1.5-pro` | More capable, longer context | Complex tasks |
| `gemini-1.5-flash` | Fast, efficient | Simple tasks |

### API Key Setup

**Option 1: AI Studio (Easiest)**
```bash
# Get free API key
Visit: https://aistudio.google.com/apikey

# Set environment variable
export GOOGLE_API_KEY="your-api-key-here"
```

**Option 2: Google Cloud (Production)**
```bash
# Authenticate with gcloud
gcloud auth application-default login

# ADK will use Application Default Credentials
```

### Example Configuration

```yaml
language_model:
  provider: google
  model: gemini-2.0-flash
  # No API key in playbook - use env var GOOGLE_API_KEY
```

---

## Evaluation

### How Evaluation Works

1. **Load BDD scenarios** from playbook
2. **Execute agent** on each scenario: `runner.run_async(user_id, session_id, message)`
3. **Compare outputs** with expected keywords
4. **Calculate pass rate**

### Example Evaluation

```bash
export GOOGLE_API_KEY="your-key"
super agent evaluate assistant_adk
```

**Output:**

```
🔍 Evaluating assistant_adk...
Testing 4 BDD scenarios:

✅ Simple greeting: PASS
✅ Question answering: PASS
✅ Explanation request: PASS
✅ Math question: PASS

============================================================
Overall: 4/4 PASS (100.0%)
============================================================
```

### Writing Good BDD Scenarios

**Best Practices:**
- ✅ Test diverse question types
- ✅ Include specific keywords
- ✅ Test edge cases
- ✅ Use realistic examples

**Example:**

```yaml
scenarios:
  - name: Factual question
    input:
      query: "What is the capital of France?"
    expected_output:
      response: "Paris"
      expected_keywords:
        - Paris
        - capital
        - France
  
  - name: Explanation
    input:
      query: "Explain photosynthesis"
    expected_output:
      response: "Process explanation"
      expected_keywords:
        - light
        - energy
        - plants
        - process
```

---

## Optimization

### GEPA Optimization Process

```bash
export GOOGLE_API_KEY="your-key"
super agent optimize assistant_adk --auto medium
```

**What Happens:**

1. **Split scenarios**: Train (50%) + Validation (50%)
2. **Current instruction**: Extract from playbook
3. **Generate variations**: 5-10 different instructions
4. **Test each**: Run on training scenarios
5. **Validate**: Test best candidates on validation set
6. **Select best**: Save optimized instruction

### Optimization Levels

| Level | Variations | Iterations | Time | Cost (Gemini Free) |
|-------|------------|------------|------|-------------------|
| `light` | 3-5 | 2-3 | 5-10 min | Free |
| `medium` | 5-10 | 3-5 | 15-30 min | Free |
| `heavy` | 10-20 | 5-10 | 30-60 min | May hit rate limits |

### Expected Improvement

| Baseline | After GEPA | Improvement |
|----------|------------|-------------|
| 70-80% | 85-92% | +15-20% |
| 80-90% | 90-95% | +10-15% |
| 90-95% | 93-98% | +3-8% |

---

## Google ADK vs Other Frameworks

| Feature | DSPy | DeepAgents | OpenAI SDK | CrewAI | **Google ADK** |
|---------|------|------------|-----------|--------|---------------|
| **Local Models** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Cloud Models** | ✅ | ✅ | ✅ | ✅ | ✅ Gemini |
| **Multi-Agent** | ❌ | Sub-agents | Handoffs | ✅ | ✅ Sequential/Parallel |
| **Optimizable Vars** | 10+ | 1 | 1 | 5 | **1** |
| **Best For** | Prompts | Planning | Simple | Teams | Google Ecosystem |
| **API Keys Needed** | No | No | No | No | ✅ Yes |
| **Evaluation** | DSPy | Custom | Custom | Custom | ✅ Built-in |
| **Deployment** | DIY | DIY | DIY | DIY | ✅ Cloud Run/Vertex |

### When to Use Google ADK

✅ **Best for:**
- Google Cloud deployments
- Gemini models (state-of-the-art!)
- Production enterprise systems
- Built-in evaluation needs
- Agent-to-Agent (A2A) protocol

❌ **Not ideal for:**
- Local-only development (needs API key)
- Ollama/open-source models
- Cost-sensitive prototyping

---

## Troubleshooting

### Common Issues

#### 1. Missing API Key

**Error:** `google.auth.exceptions.DefaultCredentialsError`

**Solution:**

```bash
# Get free API key
Visit: https://aistudio.google.com/apikey

# Set environment variable
export GOOGLE_API_KEY="your-api-key-here"

# Or use gcloud auth
gcloud auth application-default login
```

#### 2. Google ADK Not Installed

**Error:** `ImportError: No module named 'google.adk'`

**Solution:**

```bash
pip install google-adk
```

#### 3. Rate Limits

**Error:** `Resource exhausted: Quota exceeded`

**Solution:**
- Use `--auto light` for optimization
- Wait a few minutes between runs
- Upgrade to paid tier for higher limits

#### 4. Model Not Found

**Error:** `Model 'gemini-x' not found`

**Solution:** Use supported models:
- `gemini-2.0-flash` (recommended)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

---

## Advanced Features

### Context Caching (Google ADK Specific)

Google ADK supports context caching for performance:

```python
agent = Agent(
    model="gemini-2.0-flash",
    static_instruction="Static content that never changes...",
    instruction="Dynamic content with placeholders: {variable}",
    ...
)
```

**Benefits:**
- Faster responses
- Lower costs
- Better performance

**Note:** GEPA optimizes `instruction`, not `static_instruction`

### Multi-Agent Support (Future)

Google ADK supports multi-agent architectures:
- Sequential agents
- Parallel agents
- Agent hierarchies

**Future enhancement:** GEPA optimization for multi-agent coordination

---

## Resources

### Official Documentation
- [Google ADK Docs](https://google.github.io/adk-docs/)
- [Google ADK GitHub](https://github.com/google/adk-python)
- [Gemini API](https://ai.google.dev/gemini-api/docs)

### Community
- [Reddit: r/agentdevelopmentkit](https://www.reddit.com/r/agentdevelopmentkit/)
- [SuperOptiX Forum](https://community.superoptix.dev)

### Learning
- [ADK Samples](https://github.com/google/adk-samples)
- [SuperOptiX Tutorials](https://superoptix.dev/tutorials)

---

## Next Steps

1. **Try the Demo:**
   ```bash
   export GOOGLE_API_KEY="your-key"
   super init my_project && cd my_project
   super agent pull assistant_adk
   super agent compile assistant_adk --framework google-adk
   super agent evaluate assistant_adk
   ```

2. **Optimize:**
   ```bash
   super agent optimize assistant_adk --auto medium
   super agent evaluate assistant_adk  # See improvement!
   ```

3. **Deploy:**
   - Use Google ADK's built-in deployment tools
   - Deploy to Cloud Run or Vertex AI
   - Production-ready!

---

## Support

Need help?

- 📖 [Documentation](https://superoptix.dev)
- 💬 [Discord Community](https://Documentation: https://superagenticai.github.io/superoptix/)
- 🐛 [GitHub Issues](https://mailto:hello@super-agentic.ai)

---

**Happy Optimizing with Google Gemini! 🚀**


