# 🚀 Microsoft Agent Framework Integration

## Overview

SuperOptiX now supports **Microsoft Agent Framework**, Microsoft's comprehensive multi-language framework for building AI agents. This integration enables you to compile, evaluate, optimize, and deploy Microsoft agents using SuperOptiX's Universal GEPA optimizer.

## ✨ What is Microsoft Agent Framework?

Microsoft Agent Framework is Microsoft's official framework for building AI agents with support for both Python and .NET. It provides:

- **Multi-language support**: Python and C#/.NET
- **Graph-based workflows**: Advanced orchestration capabilities
- **DevUI**: Interactive development interface
- **Built-in observability**: OpenTelemetry integration
- **Multiple providers**: OpenAI, Azure OpenAI, Azure AI Foundry, Copilot Studio
- **Local model support**: Works with Ollama and other OpenAI-compatible endpoints

## 📦 Installation

### Install SuperOptiX with Microsoft Agent Framework

```bash
pip install superoptix[frameworks-microsoft]
```

**Includes:**
- agent-framework (latest preview)
- azure-identity (latest)
- SuperOptiX core with GEPA 0.0.17

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)

> **Note**: SuperOptiX is now stable! Microsoft Agent Framework may still be in preview.

## 🎯 GEPA Optimization Target

SuperOptiX's GEPA optimizer can optimize the following variable in Microsoft agents:

| Variable | Description | Impact |
|----------|-------------|--------|
| **instructions** | Agent's system prompt/instructions | ⭐⭐⭐ HIGH |

### What Gets Optimized?

GEPA optimizes the agent's `instructions` field, which controls:
- Agent personality and behavior
- Response style and format
- Task approach and methodology
- Domain expertise

**Example:**

Before GEPA:
```python
instructions = "You are a helpful AI assistant."
```

After GEPA Optimization:
```python
instructions = """You are an expert AI assistant with comprehensive knowledge across domains.

Your responses are:
- Accurate and well-researched
- Clear and well-structured
- Supported by relevant examples
- Tailored to user needs

Your approach:
1. Understand the user's question carefully
2. Analyze what information is needed
3. Provide a comprehensive response
4. Offer additional insights when relevant"""
```

## 🔧 Usage

### 1. Initialize Project

```bash
super init my_microsoft_project
cd my_microsoft_project
```

### 2. Create Agent Playbook

Create `agents/assistant_microsoft_playbook.yaml`:

```yaml
apiVersion: agent/v1
kind: AgentSpec

metadata:
  name: assistant_microsoft
  description: AI assistant built with Microsoft Agent Framework

spec:
  target_framework: microsoft
  
  language_model:
    provider: ollama  # or openai, azure
    model: gpt-oss:20b
    api_base: http://localhost:11434
  
  persona:
    role: Helpful AI Assistant
    goal: Provide clear, helpful responses to user queries
    backstory: |
      You are a knowledgeable AI assistant powered by Microsoft Agent Framework.
      You provide accurate, well-structured responses across various topics.
  
  input_fields:
    - name: query
      type: string
  
  output_fields:
    - name: response
      type: string
  
  feature_specifications:
    scenarios:
      - name: Simple greeting
        input:
          query: "Hello, how are you?"
        expected_output:
          response: "greeting"
          expected_keywords:
            - hello
            - well
```

### 3. Compile Agent

```bash
super agent compile assistant_microsoft --framework microsoft
```

This generates a Python pipeline with:
- `AssistantMicrosoftComponent`: BaseComponent wrapper for GEPA
- `AssistantMicrosoftPipeline`: Complete agent pipeline
- Ollama/OpenAI/Azure chat client setup
- BDD scenario evaluation

### 4. Evaluate Agent

```bash
super agent evaluate assistant_microsoft
```

Expected output:
```
╭─────────────────────────────────────╮
│ 📊 EVALUATION RESULTS               │
├─────────────────────────────────────┤
│ Total Scenarios:   4                │
│ Passed:            3                │
│ Failed:            1                │
│ Pass Rate:         75.0%            │
╰─────────────────────────────────────╯
```

### 5. Optimize with GEPA

```bash
super agent optimize assistant_microsoft --auto medium
```

GEPA will:
1. Generate instruction variations
2. Test each on training scenarios
3. Select the best performing version
4. Save optimized agent

### 6. Evaluate Optimized Agent

```bash
super agent evaluate assistant_microsoft  # automatically loads optimized weights
```

Expected improvement:
```
╭─────────────────────────────────────╮
│ 📊 OPTIMIZED EVALUATION RESULTS     │
├─────────────────────────────────────┤
│ Total Scenarios:   4                │
│ Passed:            4                │
│ Failed:            0                │
│ Pass Rate:         100.0% ✅        │
│ Improvement:       +25 points       │
╰─────────────────────────────────────╯
```

### 7. Run Agent

```bash
super agent run assistant_microsoft --goal "What is artificial intelligence?"
```

Or interactive mode:
```bash
super agent run assistant_microsoft
```

## 🔑 Provider Configuration

### Ollama (Local Models)

```yaml
language_model:
  provider: ollama
  model: gpt-oss:20b
  api_base: http://localhost:11434
```

No API key required! Microsoft Agent Framework works seamlessly with Ollama.

### OpenAI

```yaml
language_model:
  provider: openai
  model: gpt-4o-mini
  api_key: ${OPENAI_API_KEY}
```

### Azure OpenAI

```yaml
language_model:
  provider: azure
  model: gpt-4o
  api_base: https://your-resource.openai.azure.com
  api_key: ${AZURE_OPENAI_API_KEY}
```

## 📊 Framework Comparison

| Feature | Microsoft | OpenAI SDK | Google ADK | CrewAI |
|---------|-----------|------------|------------|--------|
| Ollama Support | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| Azure Integration | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Multi-Language | ✅ .NET+Py | ❌ No | ❌ No | ❌ No |
| Workflows | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| DevUI | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Optimizable Variables | 1 | 1 | 1 | 5 |
| Built-in Observability | ✅ Yes | ❌ No | ✅ Yes | ❌ No |

## 🎯 Best Use Cases

Microsoft Agent Framework is ideal for:

- **Enterprise deployments**: Azure integration, enterprise-grade features
- **Multi-language teams**: Python and .NET support
- **Complex workflows**: Graph-based orchestration
- **Azure ecosystem**: Native Azure OpenAI and AI Foundry support
- **Local development**: Ollama compatibility for development
- **Production monitoring**: Built-in OpenTelemetry observability

## 🧪 Example: Complete Workflow

```bash
# 1. Initialize
super init weather_assistant_ms
cd weather_assistant_ms

# 2. Create playbook
cat > agents/weather_ms_playbook.yaml << 'EOF'
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: weather_ms
  description: Weather information assistant using Microsoft framework
spec:
  target_framework: microsoft
  language_model:
    provider: ollama
    model: gpt-oss:20b
    api_base: http://localhost:11434
  persona:
    role: Weather Information Specialist
    goal: Provide accurate weather information and forecasts
  input_fields:
    - name: query
      type: string
  output_fields:
    - name: response
      type: string
  feature_specifications:
    scenarios:
      - name: Weather query
        input:
          query: "What's the weather like today?"
        expected_output:
          expected_keywords:
            - weather
            - forecast
EOF

# 3. Compile
super agent compile weather_ms --framework microsoft

# 4. Evaluate baseline
super agent evaluate weather_ms

# 5. Optimize
super agent optimize weather_ms --auto medium

# 6. Evaluate optimized
super agent evaluate weather_ms  # automatically loads optimized weights

# 7. Run
super agent run weather_ms --goal "Will it rain tomorrow?"
```

## 🔍 Under the Hood

### Generated Component Structure

```python
class AssistantMicrosoftComponent(BaseComponent):
    """BaseComponent wrapper for Microsoft ChatAgent."""
    
    def __init__(self, instructions=None, ...):
        super().__init__(
            name="assistant_microsoft",
            variable=instructions,  # GEPA optimizes this!
            variable_type="instructions",
            framework="microsoft",
            ...
        )
    
    async def forward(self, **inputs):
        # Create Microsoft ChatAgent
        agent = self._chat_client.create_agent(
            name="assistant",
            instructions=self.variable,  # GEPA-optimized!
            tools=self._tools,
        )
        
        # Execute
        response = await agent.run(inputs["query"])
        return {"response": response.text}
    
    def update(self, new_variable):
        # Called by GEPA during optimization
        self.variable = new_variable
```

### Chat Client Initialization

SuperOptiX automatically selects the appropriate chat client:

```python
# Ollama
chat_client = OpenAIChatClient(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model_id="gpt-oss:20b"
)

# Azure OpenAI
chat_client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_name="gpt-4o"
)

# Standard OpenAI
chat_client = OpenAIChatClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_id="gpt-4o-mini"
)
```

## 🚀 Advanced Features

### 1. Custom Tools

Add tools to your Microsoft agent:

```yaml
# In playbook
spec:
  tools:
    - name: get_weather
      description: Get weather for a location
      parameters:
        location:
          type: string
          description: City name
```

### 2. Temperature Control

```yaml
language_model:
  provider: ollama
  model: gpt-oss:20b
  temperature: 0.7
  max_tokens: 500
```

### 3. Multi-Turn Conversations

Microsoft Agent Framework maintains conversation state via threads:

```python
# Automatic thread management
response1 = await agent.run("Hello")
response2 = await agent.run("What did I just say?")
# Agent remembers previous context
```

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError: No module named 'agent_framework'

**Solution**: Install Microsoft Agent Framework
```bash
pip install agent-framework
```

### Issue: API Key Not Set

**Solution**: Set environment variables
```bash
export OPENAI_API_KEY=sk-...
# or
export AZURE_OPENAI_ENDPOINT=https://...
export AZURE_OPENAI_API_KEY=...
```

### Issue: Ollama Connection Failed

**Solution**: Ensure Ollama is running
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull gpt-oss:20b
```

## 📚 Learn More

- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [SuperOptiX GEPA Guide](./gepa-guide.md)
- [Multi-Framework Support](./multi-framework.md)

## 🎉 Summary

Microsoft Agent Framework integration brings:

- ✅ **Enterprise-grade** agent development
- ✅ **Multi-language** support (Python + .NET)
- ✅ **Azure integration** for enterprise deployments
- ✅ **Ollama compatibility** for local development
- ✅ **GEPA optimization** for improved performance
- ✅ **Built-in observability** with OpenTelemetry
- ✅ **Production-ready** workflows and orchestration

SuperOptiX makes it easy to build, optimize, and deploy Microsoft agents! 🚀

