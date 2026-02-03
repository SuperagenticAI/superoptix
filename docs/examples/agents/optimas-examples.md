---
title: Optimas Examples
---

# ⚡ Optimas Examples

Working examples and demos for all Optimas integration targets. These examples have been verified to work correctly with the latest SuperOptiX version.

Background reading and references:

- Optimas website: [optimas.stanford.edu](https://optimas.stanford.edu)
- Optimas paper (Wu et al., 2025): [arXiv: 2507.03041](https://www.arxiv.org/pdf/2507.03041)
- DSPy: [dspy.ai](https://dspy.ai)
- CrewAI: [docs.crewai.com](https://docs.crewai.com)
- AutoGen: [microsoft.github.io/autogen](https://microsoft.github.io/autogen/)
- OpenAI Agent SDK: [platform.openai.com/docs/agents](https://platform.openai.com/docs/agents)
- LiteLLM: [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)

## 🚀 Quick Demo

### Pull Demo Playbooks

```bash
# Initialize a new project
super init test_optimas
cd test_optimas

# Pull working demo playbooks for each target
super agent pull optimas_openai      # OpenAI SDK (recommended)
super agent pull optimas_crewai      # CrewAI
super agent pull optimas_autogen     # AutoGen
super agent pull optimas_dspy        # DSPy
```

### Full Flow Example

```bash
# 1. Compile
super agent compile optimas_openai --target optimas-openai

# 2. Evaluate
super agent evaluate optimas_openai --engine optimas --target optimas-openai

# 3. Optimize
SUPEROPTIX_OPRO_MAX_TOKENS=256 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=3 \
SUPEROPTIX_OPRO_MAX_WORKERS=3 \
super agent optimize optimas_openai --engine optimas --target optimas-openai --optimizer opro

# 4. Run
super agent run optimas_openai --engine optimas --target optimas-openai --goal "Write a Python function to add two numbers"
```

## 🎯 Target-Specific Examples

### 1. OpenAI SDK Target (Recommended)

**Status**: ✅ **Fully Working** - Most reliable target

#### Quick Demo
```bash
# Pull and test
super agent pull optimas_openai
super agent compile optimas_openai --target optimas-openai
super agent evaluate optimas_openai --engine optimas --target optimas-openai
```

#### Full Workflow with Optimization
```bash
# Optimize with environment variables
SUPEROPTIX_OPRO_MAX_TOKENS=256 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=3 \
SUPEROPTIX_OPRO_MAX_WORKERS=3 \
SUPEROPTIX_OPRO_TEMPERATURE=0.8 \
SUPEROPTIX_OPRO_COMPILE_TIMEOUT=120 \
super agent optimize optimas_openai --engine optimas --target optimas-openai

# Run optimized agent
super agent run optimas_openai --engine optimas --target optimas-openai --goal "Write a Python function to calculate prime numbers"
```

#### Why It's Great
- No threading issues
- Fast optimization and execution
- Works perfectly with all optimizers
- Most stable target for production use

### 2. CrewAI Target

**Status**: ✅ **Fully Working** - Excellent for multi-agent workflows

#### Quick Demo
```bash
# Pull and test
super agent pull optimas_crewai
super agent compile optimas_crewai --target optimas-crewai
super agent evaluate optimas_crewai --engine optimas --target optimas-crewai
```

#### Full Workflow with Optimization
```bash
# Optimize with environment variables
SUPEROPTIX_OPRO_MAX_TOKENS=256 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=3 \
SUPEROPTIX_OPRO_MAX_WORKERS=3 \
SUPEROPTIX_OPRO_TEMPERATURE=0.8 \
LITELLM_TIMEOUT=60 \
LITELLM_MAX_RETRIES=3 \
super agent optimize optimas_crewai --engine optimas --target optimas-crewai

# Run optimized agent
super agent run optimas_crewai --engine optimas --target optimas-crewai --goal "Write a Python function to calculate factorial"
```

#### Dependencies Required
```bash
# Install manually to avoid conflicts
pip install crewai
pip install json-repair>=0.30.0
```

#### Why It's Great
- Excellent for multi-agent scenarios
- Fast optimization and execution
- No threading issues
- Great for team-based tasks

### 3. AutoGen Target

**Status**: ⚠️ **Mostly Working** - Optimization can be slow

#### Quick Demo
```bash
# Pull and test
super agent pull optimas_autogen
super agent compile optimas_autogen --target optimas-autogen
super agent evaluate optimas_autogen --engine optimas --target optimas-autogen
```

#### Full Workflow with Optimization
```bash
# Optimize with extended timeout
SUPEROPTIX_OPRO_MAX_TOKENS=256 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=3 \
SUPEROPTIX_OPRO_MAX_WORKERS=3 \
SUPEROPTIX_OPRO_COMPILE_TIMEOUT=180 \
LITELLM_TIMEOUT=60 \
LITELLM_MAX_RETRIES=3 \
super agent optimize optimas_autogen --engine optimas --target optimas-autogen

# Run optimized agent
super agent run optimas_autogen --engine optimas --target optimas-autogen --goal "Write a Python function to reverse a string"
```

#### Configuration Requirements
```yaml
# Requires detailed model_info for non-OpenAI models
language_model:
  provider: ollama
  model: llama3.2:1b
  base_url: http://localhost:11434
  api_key: ""
  model_info:
    model_name: "llama3.2:1b"
    max_tokens: 4096
    temperature: 0.7
    top_p: 0.9
```

#### Why It's Great
- Excellent for complex multi-agent workflows
- Reliable execution despite slow optimization
- Great for conversational agents
- Handles complex interactions well

### 4. DSPy Target

**Status**: ✅ **Fully Working** - All optimizers now working properly

#### Quick Demo
```bash
# Pull and test
super agent pull optimas_dspy
super agent compile optimas_dspy --target optimas-dspy
super agent evaluate optimas_dspy --engine optimas --target optimas-dspy
```

#### Full Workflow with Optimization
```bash
# Optimize with environment variables
SUPEROPTIX_OPRO_MAX_TOKENS=256 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=3 \
SUPEROPTIX_OPRO_MAX_WORKERS=3 \
SUPEROPTIX_OPRO_TEMPERATURE=0.8 \
super agent optimize optimas_dspy --engine optimas --target optimas-dspy

# Run optimized agent
super agent run optimas_dspy --engine optimas --target optimas-dspy --goal "Write a Python function to calculate fibonacci numbers"
```

#### Root Cause
The issue is with LiteLLM library version compatibility:
- DSPy 3.0.0 uses LiteLLM for model communication
- LiteLLM has threading issues with concurrent operations
- When Optimas tries to run multiple optimization iterations, the thread pool gets corrupted

#### Workarounds
```bash
# Option 1: Use other targets for optimization
# Option 2: Reduce concurrency (may still fail)
SUPEROPTIX_OPRO_MAX_WORKERS=1
# Option 3: Use for research only (avoid optimization)
```

## 🎯 Optimizer Options

The `--optimizer` flag allows you to specify which optimization method to use:

### Available Optimizers

- **`--optimizer opro`**: OPRO (Optimization by PROmpting) - Single-iteration optimization
- **`--optimizer mipro`**: MIPRO (Multi-Iteration PROmpting) - Multi-iteration optimization  
- **`--optimizer copro`**: COPRO (Cooperative PROmpting) - Cooperative optimization

### Example Usage

```bash
# OPRO optimization (default)
super agent optimize <agent> --engine optimas --target <target> --optimizer opro

# MIPRO optimization (great for DSPy)
super agent optimize <agent> --engine optimas --target <target> --optimizer mipro

# COPRO optimization (cooperative approach)
super agent optimize <agent> --engine optimas --target <target> --optimizer copro
```

## 🔧 Environment Variable Examples

### Fast Optimization (Development)
```bash
SUPEROPTIX_OPRO_MAX_TOKENS=128 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=2 \
SUPEROPTIX_OPRO_MAX_WORKERS=2 \
SUPEROPTIX_OPRO_TEMPERATURE=0.7 \
SUPEROPTIX_OPRO_COMPILE_TIMEOUT=60 \
super agent optimize <agent> --engine optimas --target <target>
```

### High-Quality Optimization (Production)
```bash
SUPEROPTIX_OPRO_MAX_TOKENS=512 \
SUPEROPTIX_OPRO_NUM_CANDIDATES=5 \
SUPEROPTIX_OPRO_MAX_WORKERS=4 \
SUPEROPTIX_OPRO_TEMPERATURE=0.9 \
SUPEROPTIX_OPRO_COMPILE_TIMEOUT=300 \
super agent optimize <agent> --engine optimas --target <target>
```

### LiteLLM Configuration
```bash
LITELLM_TIMEOUT=60 \
LITELLM_MAX_RETRIES=3 \
LITELLM_MAX_RESPONSE=4000 \
LITELLM_CACHE_ENABLED=false \
LITELLM_LOG_LEVEL=ERROR \
super agent optimize <agent> --engine optimas --target <target>
```

## 🚨 Known Limitations

### 1. DSPy Optimization Issues
- **Problem**: LiteLLM threading conflicts during optimization
- **Impact**: Cannot use DSPy target for production optimization
- **Workaround**: Use OpenAI SDK or CrewAI targets instead

### 2. AutoGen Optimization Speed
- **Problem**: Optimization can be slow (120s+ timeout)
- **Impact**: Slower development iteration
- **Workaround**: Increase timeout or use faster models

### 3. CrewAI Dependencies
- **Problem**: Manual installation required due to conflicts
- **Impact**: Additional setup steps
- **Workaround**: Follow manual installation instructions

### 4. LiteLLM Version Compatibility
- **Problem**: DSPy 3.0.0 + LiteLLM threading issues
- **Impact**: DSPy target optimization fails
- **Workaround**: Use other targets or wait for LiteLLM fixes

## 🎯 Recommendations

### For Production Use
1. **Primary**: OpenAI SDK target (most reliable)
2. **Secondary**: CrewAI target (excellent for multi-agent)
3. **Avoid**: DSPy target (optimization issues)

### For Development
1. **Quick Testing**: OpenAI SDK target
2. **Multi-agent**: CrewAI target
3. **Research**: DSPy target (compile/evaluate only)

### For Optimization
1. **Fast**: OpenAI SDK or CrewAI targets
2. **Quality**: Increase timeout and parameters
3. **Avoid**: DSPy target optimization

## 🔗 Next Steps

- **Start Here**: [Optimas Integration Guide](../guides/optimas-integration.md)
- **CLI Reference**: [Command Reference](../reference/cli.md)
- **Agent Development**: [Building Custom Agents](../guides/agent-development.md)
- **Troubleshooting**: [Common Issues & Solutions](../guides/optimas-integration.md#troubleshooting)


