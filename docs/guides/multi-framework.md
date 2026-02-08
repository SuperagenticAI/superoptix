# Multi-Framework Support Guide

**SuperOptiX Universal Framework Workflow**

Build once from SuperSpec YAML, compile to your target framework, and run either:
- minimal pipeline (default)
- optimized pipeline (`--optimize`)

RLM support is available as an experimental feature. Unified sandbox support is coming soon.

---

## Feature Highlights

- 🧪 **RLM (Experimental)**: Available now across active framework integrations where configured. Unified sandbox support is coming soon.
- 🗂️ **Connector Integration (StackOne)**: Compile one connector-enabled SuperSpec into multiple frameworks.
- 🧬 **GEPA Optimization Path**: Keep minimal runtime pipelines by default; enable optimization lifecycle with `--optimize`.
- 🧩 **Framework-Native Templates**: Generated pipelines stay close to each framework's native style.
- 📊 **Coverage View**: See the [Framework Feature Matrix](framework-feature-matrix.md) for current capability status.

---

## 📦 Installation

### Core Installation

```bash
pip install superoptix
```

**Includes:** Core framework with DSPy support

### Install Specific Frameworks

```bash
# OpenAI Agents SDK
pip install superoptix[frameworks-openai]

# Claude Agent SDK
pip install superoptix[frameworks-claude-sdk]

# Google ADK
pip install superoptix[frameworks-google]

# Microsoft Agent Framework (legacy support)
pip install superoptix[frameworks-microsoft]

# DeepAgents
pip install superoptix[frameworks-deepagents]

# Pydantic AI
pip install superoptix[frameworks-pydantic-ai]

# CrewAI
pip install superoptix[frameworks-crewai]

# All frameworks at once
pip install superoptix[frameworks]
```

---

## Overview

SuperOptiX lets you:

- Build agents in major frameworks (DSPy, OpenAI SDK, Claude SDK, CrewAI, Google ADK, DeepAgents, Pydantic AI, Microsoft legacy)
- Optimize with one universal optimizer (GEPA)
- Use the same compile/run workflow across frameworks
- Switch frameworks without rewriting code
- Compare framework behavior side by side

### Generated Artifacts (Current Behavior)

Each compile writes:
- framework pipeline file, e.g. `my_agent_openai_pipeline.py`
- sidecar compiled spec file, e.g. `my_agent_openai_pipeline_compiled_spec.json`

The pipeline reads the sidecar at runtime. If missing/corrupt, runtime now gives a clear "recompile agent" error.

---

## Supported Frameworks

### Framework Comparison

| Framework | Optimization Scope | Local Models | Best For |
|-----------|--------------------|--------------|----------|
| **DSPy** | Signatures, modules, prompts, and evaluation hooks | Ollama | Complex reasoning, research |
| **OpenAI SDK** | Agent instructions | Ollama | Simple and fast agents |
| **Claude SDK** | Agent system prompt | Cloud only | Anthropic-native agent workflows |
| **CrewAI** | Persona and task instructions | Ollama | Multi-agent teams |
| **Google ADK** | Agent instruction | Cloud only | Google ecosystem, Gemini |
| **Microsoft (Legacy)** | Agent instructions | Ollama | Existing Microsoft-framework projects |
| **DeepAgents** | System prompt | Cloud only | Complex planning, LangGraph |
| **Pydantic AI** | Instructions, output shaping, MCP/tool flow | Ollama | Type-safe outputs and tool use |

---

## Universal Workflow

The same workflow works for **ALL frameworks**:

```bash
# 1) Compile minimal pipeline (default)
super agent compile my_agent --framework <framework>

# 2) Run minimal pipeline
super agent run my_agent --framework <framework> --goal "your goal"

# 3) Compile optimized pipeline (optional)
super agent compile my_agent --framework <framework> --optimize

# 4) Run optimization loop (GEPA-backed)
super agent optimize my_agent --framework <framework> --auto light
```

Cloud/local routing (common pattern):

```bash
# Cloud Google
super agent compile my_agent --framework <framework> --cloud --provider google-genai --model gemini-2.5-flash
super agent run my_agent --framework <framework> --cloud --provider google-genai --model gemini-2.5-flash --goal "your goal"

# Local Ollama
super agent compile my_agent --framework <framework> --local --provider ollama --model llama3.1:8b
super agent run my_agent --framework <framework> --local --provider ollama --model llama3.1:8b --goal "your goal"
```

Notes:
- `google-adk` and `deepagents` currently require cloud function-calling models.
- `claude-sdk` requires Anthropic credentials and Claude models.
- for non-DSPy frameworks, always pass `--framework <framework>` on `super agent optimize` to avoid defaulting to DSPy assets.

---

## Framework-Specific Guides

### DSPy (Stanford Research Framework)

**Best for**: Complex reasoning, research, maximum optimization flexibility

#### Quick Start

```bash
# Pull demo agent
super agent pull sentiment_analyzer

# Compile (DSPy is default)
super agent compile sentiment_analyzer

# Evaluate
super agent evaluate sentiment_analyzer

# Optimize
super agent optimize sentiment_analyzer --auto medium

# Run
super agent run sentiment_analyzer
```

#### Configuration

```yaml
# playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: my_dspy_agent
spec:
  target_framework: dspy  # or omit for default
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  persona:
    role: Research Assistant
    goal: Analyze complex topics
```

#### What GEPA Optimizes

- Signatures (input/output specs)
- Instructions for each module
- Chain-of-thought prompts
- Few-shot examples
- Module connections

**Proven Results**: 37.5% → 80% improvement

---

### OpenAI Agents SDK (Simple & Fast)

**Best for**: Simple agents, fast prototyping, 100% local & free with Ollama

#### Quick Start

```bash
# Pull demo agent (already configured for Ollama!)
super agent pull assistant_openai

# Install Ollama (if not already installed)
brew install ollama
ollama pull llama3.1:8b

# Compile & Run (no API keys needed!)
super agent compile assistant_openai --framework openai
super agent run assistant_openai --goal "Hello!"

# Evaluate
super agent evaluate assistant_openai

# Optimize
super agent optimize assistant_openai --auto medium --framework openai --reflection-lm ollama:llama3.1:8b
```

#### Configuration

**Default (FREE Ollama - already configured!)**:
```yaml
# playbook.yaml
spec:
  target_framework: openai
  language_model:
    location: local
    provider: ollama
    model: ollama:llama3.1:8b  # FREE, fast and efficient!
    api_base: http://localhost:11434
```

**Optional Cloud Models** (requires API key):
```yaml
# For OpenAI
spec:
  target_framework: openai
  language_model:
    location: cloud
    provider: openai
    model: openai:gpt-4o
    # Set: export OPENAI_API_KEY="sk-..."
```

#### What GEPA Optimizes

- Agent instructions (the main system prompt)

**Proven Results**: Excellent performance with Ollama (results vary by hardware/model)

---

### CrewAI (Multi-Agent Teams)

**Best for**: Multi-agent collaboration, role-based agents

#### Quick Start

```bash
# Pull demo agents
super agent pull researcher_crew
super agent pull content_creator_crew

# Compile
super agent compile researcher_crew --framework crewai

# Evaluate
super agent evaluate researcher_crew

# Optimize
super agent optimize content_creator_crew --auto medium --framework crewai --reflection-lm ollama:llama3.1:8b

# Run
super agent run researcher_crew
```

#### Configuration

**Basic Agent Configuration**
```yaml
spec:
  target_framework: crewai
  language_model:
    provider: ollama
    model: llama3.1:8b
  persona:
    role: Research Analyst
    goal: Conduct thorough research on topics
    backstory: |
      Experienced researcher with attention to detail.
  tasks:
    - name: research
      description: Research the given topic
      expected_output: Comprehensive research report
```

**Advanced: Combined Agent + Task Optimization**
```yaml
spec:
  target_framework: crewai
  persona:
    role: Content Creator
    goal: Create engaging content
    backstory: |
      Creative writer with audience engagement expertise.
  tasks:
    - name: write
      description: Write compelling content about the topic
      expected_output: Polished article ready for publication
```

#### What GEPA Optimizes

GEPA can optimize:
- **Agent profile**: role, goal, backstory
- **Task configuration**: description, expected_output
- **Combined optimization**: agent profile + task configuration for better results

**Proven Results**: Excellent performance with Ollama (results vary by hardware/model)

---

### Google ADK (Gemini Native)

**Best for**: Google ecosystem, Gemini integration, free access

#### Quick Start

```bash
# Set API key
export GOOGLE_API_KEY="your-key-here"

# Pull demo agent
super agent pull assistant_adk

# Compile
super agent compile assistant_adk --framework google-adk

# Evaluate
super agent evaluate assistant_adk

# Optimize
super agent optimize assistant_adk --auto medium --framework google-adk --reflection-lm ollama:llama3.1:8b

# Run
super agent run assistant_adk
```

#### Configuration

```yaml
spec:
  target_framework: google-adk
  language_model:
    provider: google
    model: gemini-2.0-flash  # Free access!
  persona:
    instructions: |
      You are a helpful AI assistant powered by Google's Gemini.
```

#### What GEPA Optimizes

- Agent instruction (system prompt)

---

### Microsoft Agent Framework (Enterprise)

**Best for**: Azure integration, .NET support, enterprise workflows

#### Quick Start

```bash
# Pull demo agent
super agent pull assistant_microsoft

# Compile
super agent compile assistant_microsoft --framework microsoft

# Evaluate
super agent evaluate assistant_microsoft

# Optimize
super agent optimize assistant_microsoft --auto medium --framework microsoft --reflection-lm ollama:llama3.1:8b

# Run
super agent run assistant_microsoft
```

#### Configuration

**With Ollama**:
```yaml
spec:
  target_framework: microsoft
  language_model:
    provider: ollama
    model: gpt-oss:20b
    api_base: http://localhost:11434
```

**With Azure OpenAI**:
```yaml
spec:
  target_framework: microsoft
  language_model:
    provider: azure
    azure_endpoint: https://your-resource.openai.azure.com
    azure_deployment_name: gpt-4
    azure_api_version: 2024-02-15-preview
```

#### What GEPA Optimizes

- Agent instructions (system prompt)

---

### DeepAgents (LangGraph Planning)

**Best for**: Complex planning, multi-step reasoning, advanced workflows

#### Quick Start

```bash
# Pull demo agent
super agent pull research_agent_deepagents

# Compile
super agent compile research_agent_deepagents --framework deepagents

# Evaluate
super agent evaluate research_agent_deepagents

# Optimize
super agent optimize research_agent_deepagents --auto medium --framework deepagents --reflection-lm ollama:llama3.1:8b

# Run
super agent run research_agent_deepagents
```

#### Configuration

```yaml
spec:
  target_framework: deepagents
  language_model:
    provider: ollama
    model: llama3.1:8b
  persona:
    system_prompt: |
      You are a research agent that plans and executes complex research tasks.
```

#### What GEPA Optimizes

- System prompt (planning instructions)

---

## Choosing the Right Framework

### Decision Matrix

**Choose DSPy if**:
- You need maximum optimization flexibility
- You want to optimize multiple variables
- You're doing research or complex reasoning
- You want proven 37.5% → 80% improvements

**Choose OpenAI SDK if**:
- You want the simplest API
- You need fast prototyping
- You're building simple assistants
- You want Ollama compatibility

**Choose CrewAI if**:
- You need multiple agents working together
- You want role-based collaboration
- You need task delegation
- You want agent + task combined optimization

**Choose Google ADK if**:
- You're in the Google ecosystem
- You want Gemini 2.0 Flash (free access!)
- You need session management
- You want Google-native features

**Choose Microsoft if**:
- You're using Azure OpenAI
- You need .NET integration
- You're in enterprise environment
- You want built-in observability

**Choose DeepAgents if**:
- You need complex planning graphs
- You want LangGraph integration
- You need multi-step reasoning
- You want advanced agentic workflows

---

## Framework Switching

Switch frameworks without rewriting code!

```bash
# Start with DSPy
super agent compile my_agent --framework dspy
super agent evaluate my_agent

# Try OpenAI SDK
super agent compile my_agent --framework openai
super agent evaluate my_agent

# Compare results!
```

---

## Optimization Comparison

### GEPA Results Across Frameworks

| Framework | Demo Agent | Baseline | After GEPA | Improvement |
|-----------|------------|----------|------------|-------------|
| DSPy | sentiment_analyzer | Good | Improved | Significant improvement (results vary) |
| OpenAI SDK | assistant_openai | Excellent | Excellent | Maintained performance (results vary) |
| CrewAI | content_creator_crew | Good | Improved | Significant improvement (results vary) |
| Google ADK | assistant_adk | TBD | TBD | Ready |
| Microsoft | assistant_microsoft | TBD | TBD | Ready |
| DeepAgents | research_agent | TBD | TBD | Ready |

---

## Advanced: Multi-Framework Projects

### Example: Compare All Frameworks

```bash
# Create project
super init comparison_project
cd comparison_project

# Pull same agent for all frameworks
for fw in dspy openai crewai google-adk microsoft deepagents; do
  super agent pull assistant_${fw}
  super agent compile assistant_${fw} --framework ${fw}
  super agent evaluate assistant_${fw}
  super agent optimize assistant_${fw} --auto medium
  super agent evaluate assistant_${fw}  # automatically loads optimized weights
done

# Compare results!
```

---

## CLI Quick Reference

```bash
# List all demo agents
super agent list --pre-built

# Pull specific framework demo
super agent pull sentiment_analyzer      # DSPy
super agent pull assistant_openai        # OpenAI SDK
super agent pull researcher_crew         # CrewAI
super agent pull assistant_adk           # Google ADK
super agent pull assistant_microsoft     # Microsoft
super agent pull research_agent_deepagents  # DeepAgents

# Compile with framework
super agent compile <agent> --framework <framework>

# Evaluate
super agent evaluate <agent>

# Optimize (same command for all!)
super agent optimize <agent> --auto medium

# Run
super agent run <agent>
```

---

## Troubleshooting

### Issue: "Framework not found"

**Solution**: Install framework-specific dependencies

```bash
# OpenAI SDK
pip install openai-agents-sdk

# CrewAI
pip install crewai

# Google ADK
pip install google-adk

# Microsoft
pip install agent-framework

# DeepAgents (LangGraph)
pip install langgraph langchain-anthropic

# Pydantic AI
pip install pydantic-ai==1.31.0
```

### Issue: "Ollama not supported"

**Solution**: Some frameworks have limitations

- **Google ADK**: Requires Gemini API key (cloud only)
- **DeepAgents**: Check LangChain compatibility

### Issue: "Optimization not working"

**Solution**: Ensure GEPA is configured

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium
```

---

## Next Steps

1. **Try all frameworks**: Pull demo agents and compare
2. **Read framework guides**: Check individual integration docs
3. **Build custom agents**: Create your own with SuperSpec
4. **Optimize everything**: GEPA works on all frameworks!

### Framework-Specific Docs

- [DSPy Integration](dspy-optimizers.md)
- [OpenAI SDK Integration](openai-sdk-integration.md)
- [CrewAI Integration](crewai-integration.md) & [Advanced](crewai-task-optimization.md)
- [Google ADK Integration](google-adk-integration.md)
- [Microsoft Integration](microsoft-framework-integration.md)
- [DeepAgents Integration](deepagents-integration.md)
- [Pydantic AI Integration](pydantic-ai-integration.md) & [MCP Demo](pydantic-ai-mcp-demo.md)

### Related Docs

- [GEPA Optimization](gepa-optimization.md)
- [Evaluation & Testing](evaluation-testing.md)
- [SuperSpec DSL](superspec.md)

### Tutorials

- [**OpenAI SDK + GEPA Optimization Tutorial**](../tutorials/openai-sdk-gepa-optimization.md) - Complete step-by-step guide to building custom agents with native OpenAI SDK patterns and optimizing them with GEPA

---

Ready to build your own optimized agent? Start with the [OpenAI SDK + GEPA Tutorial](../tutorials/openai-sdk-gepa-optimization.md)!
