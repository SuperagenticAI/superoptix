---
title: Multi-Framework Quick Start - SuperOptiX
---

# Multi-Framework Quick Start

<div align="center">

**Build and optimize AI agents across multiple major frameworks**

Choose from DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft, or DeepAgents

</div>

---

## 🎯 What You'll Build

!!! success "Learning Outcomes"
    By the end of this guide, you'll have:

    - A fully functional AI agent in your chosen framework
    - Automated evaluation with RSpec-style BDD scenarios
    - GEPA optimization with proven improvements
    - Production-ready agent deployment

## 📋 Requirements

### 🖥️ Hardware

| Component | Requirement |
|-----------|-------------|
| **GPU RAM** | 16GB recommended for optimization |
| **System RAM** | 8GB+ recommended |
| **Network** | Stable internet connection for model downloads |

### 🐍 Software

| Software | Version |
|----------|---------|
| **Python** | 3.11 or higher |
| **Ollama** | For local LLMs |

!!! warning "Windows Users"
    Set `PYTHONUTF8=1` to ensure proper UTF-8 encoding support:
    ```cmd
    set PYTHONUTF8=1
    ```

---

## 📦 Installation

!!! tip "Stable Release Available"
    SuperOptiX is now available as a stable release.

!!! info "Git Required"
    Git is required for installation. Verify: `git --version`

    **Install Git:**

    - **macOS:** `xcode-select --install`
    - **Linux:** `sudo apt-get install git`
    - **Windows:** [Download Git](https://git-scm.com/downloads)

!!! tip "Framework-Free Core"
    SuperOptiX core is now **framework-independent**! Install only what you need.

**Choose your framework(s) and install SuperOptiX with `uv tool install`:**

=== "Core Only (Includes DSPy)"
    ```bash
    uv tool install superoptix
    ```
    **Includes:** CLI tools, SuperSpec DSL, YAML processing, DSPy
    
    **Use for:** GEPA optimization, DSPy pipelines, evaluation

=== "DSPy Framework"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-dspy]"
    ```
    **Includes:** SuperOptiX core + DSPy + GEPA
    
    ⚠️ **Cannot be installed with CrewAI** (json-repair conflict)

=== "OpenAI Agents SDK"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-openai]"
    ```
    **Includes:** openai-agents, openai SDK

=== "Google ADK"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-google]"
    ```
    **Includes:** google-adk, google-generativeai
    
    **Setup API Key:**
    ```bash
    export GOOGLE_API_KEY=your-google-api-key
    ```

=== "Claude Agent SDK"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-claude-sdk]"
    ```
    **Includes:** claude-agent-sdk

    **Setup API Key:**
    ```bash
    export ANTHROPIC_API_KEY=your-anthropic-api-key
    ```

=== "Microsoft Agent Framework"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-microsoft]"
    ```
    **Includes:** agent-framework, azure-identity
    
    **Note:** This integration is maintained as legacy support.

=== "DeepAgents"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-deepagents]"
    ```
    **Includes:** deepagents

=== "CrewAI"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks-crewai]"
    ```
    **Includes:** crewai
    
    ⚠️ **Cannot be installed with DSPy** (json-repair conflict)

=== "All DSPy-Compatible Frameworks"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks]"
    ```
    **Includes:** DSPy, OpenAI SDK, Claude SDK, Google ADK, Microsoft, DeepAgents
    
    **Excludes:** CrewAI (due to DSPy conflict)

=== "With MCP Optimization"
    ```bash
    uv tool install superoptix --with "superoptix[frameworks,mcp]"
    ```
    **Includes:** DSPy-compatible frameworks + MCP SDK

=== "Everything (DSPy path)"
    ```bash
    uv tool install superoptix --with "superoptix[all]"
    ```
    **Includes:** DSPy + compatible frameworks + vector DBs + observability
    
    **Excludes:** CrewAI

!!! tip "First Execution"
    The first execution of `super` commands may take a few seconds as Python compiles bytecodes.

---

## 🚀 Step 1: Initialize Project

```bash
# Create a new project
super init my_first_agent
cd my_first_agent
```

!!! example "Project Structure"
    This creates a standard project structure:

    ```
    my_first_agent/
    ├── agents/          # Agent playbooks
    ├── pipelines/       # Compiled agents
    ├── evals/          # Evaluation results
    └── optimizers/     # Optimization data
    ```

---

## 🎨 Step 2: Choose Your Framework and Pull an Agent

!!! info "Framework Support"
    SuperOptiX supports multiple major frameworks. Choose the one that fits your needs:

=== "DSPy (Recommended)"

    ```bash
    # DSPy: Stanford research framework
    super agent pull sentiment_analyzer
    ```

    **Best for**: Complex reasoning, research, multiple optimizable variables

    **Status**: Proven GEPA optimization results

=== "OpenAI SDK"

    ```bash
    # OpenAI SDK: Simple and fast
    super agent pull assistant_openai
    ```

    **Best for**: Simple agents, fast prototyping

    **Status**: Proven GEPA optimization results

=== "CrewAI"

    ```bash
    # CrewAI: Multi-agent collaboration
    super agent pull researcher_crew
    ```

    **Best for**: Multi-agent teams, role-based agents

    **Status**: Proven GEPA optimization results

=== "Google ADK"

    ```bash
    # Google ADK: Gemini 2.0 native
    super agent pull assistant_adk
    ```

    **Best for**: Gemini integration, free tier available

    **Status**: Ready for optimization

=== "Microsoft"

    ```bash
    # Microsoft: Enterprise Azure
    super agent pull assistant_microsoft
    ```

    **Best for**: Enterprise Azure integration

    **Status**: Ready for optimization

=== "DeepAgents"

    ```bash
    # DeepAgents: Complex planning
    super agent pull research_agent_deepagents
    ```

    **Best for**: LangGraph planning, advanced reasoning

    **Status**: Ready for optimization

!!! tip "Browse All Agents"
    ```bash
    # See all pre-built agents
    super market browse agents

    # List demo agents
    super agent list --pre-built
    ```

---

## 🔧 Step 3: Compile the Agent

```bash
# Compile for your chosen framework
super agent compile <agent_name>

# Example: DSPy
super agent compile sentiment_analyzer

# Example: OpenAI SDK
super agent compile assistant_openai
```

!!! success "Compilation Output"
    This generates framework-specific Python code in the `pipelines/` directory.

---

## 📊 Step 4: Evaluate Performance

```bash
# Run baseline evaluation
super agent evaluate <agent_name>

# Example
super agent evaluate sentiment_analyzer
```

!!! example "Evaluation Output"
    You'll see baseline results showing:

    ```
    Evaluation Results:
    ==================
    Pass Rate: X% (scenarios passed/total)
    Average Score: X.X/10
    ```

---

## 🧬 Step 5: Optimize with GEPA

!!! tip "The Magic Step"
    **GEPA (Genetic-Pareto)** automatically improves your agent's performance!

### 🌟 The Universal Optimizer

!!! success "Framework Support"
    - Works on **ALL frameworks** (DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft, DeepAgents)
    - Proven optimization results across frameworks
    - Sample efficient: Works with minimal training scenarios
    - Framework-agnostic: Same command for all frameworks!

```bash
# GEPA works on ALL frameworks! Same command!
super agent optimize <agent_name> --auto medium

# Examples:
super agent optimize sentiment_analyzer --auto medium        # DSPy
super agent optimize assistant_openai --auto medium          # OpenAI SDK
super agent optimize researcher_crew --auto medium           # CrewAI
super agent optimize assistant_adk --auto medium             # Google ADK
super agent optimize assistant_microsoft --auto medium       # Microsoft
super agent optimize research_agent_deepagents --auto medium # DeepAgents
```

### ⚙️ Optimization Levels

| Level | Best For |
|-------|----------|
| `light` | Quick iteration, prototyping |
| `medium` | Most use cases (Recommended) |
| `intensive` | Critical production agents |

!!! warning "API Usage"
    Optimization makes multiple LLM API calls. Monitor your usage if using cloud models. Works great with Ollama (local, free)!

---

## 📈 Step 6: Re-evaluate to See Improvement

```bash
# Evaluate optimized version
super agent evaluate <agent_name>  # automatically loads optimized weights
```

!!! success "See the Improvements"
    You'll see improvements in:

    ```
    Evaluation Results (Optimized):
    ================================
    Pass Rate: Improved ⬆️
    Average Score: Improved ⬆️
    ```

    The optimized agent automatically loads the improved weights from GEPA optimization!

---

## 🎯 Step 7: Run Your Optimized Agent

```bash
# Run the optimized agent
super agent run <agent_name>

# Example with custom input
super agent run sentiment_analyzer \
  --input "This product exceeded all my expectations!"
```

---

## 🔄 Complete Example Workflow

!!! example "Full DSPy Sentiment Analyzer Workflow"
    Here's the complete end-to-end workflow:

    ```bash
    # 1. Initialize
    super init sentiment_project
    cd sentiment_project

    # 2. Pull agent
    super agent pull sentiment_analyzer

    # 3. Compile
    super agent compile sentiment_analyzer

    # 4. Baseline evaluation
    super agent evaluate sentiment_analyzer

    # 5. Optimize with GEPA
    super agent optimize sentiment_analyzer --auto medium

    # 6. Re-evaluate (automatically loads optimized weights)
    super agent evaluate sentiment_analyzer

    # 7. Run your optimized agent
    super agent run sentiment_analyzer
    ```

---

## 🎓 What's Next?

!!! success "Congratulations!"
    You've just built, evaluated, and optimized your first AI agent with SuperOptiX!

### 📚 Learn More

| Resource | Description |
|----------|-------------|
| [Multi-Framework Guide](../guides/multi-framework.md) | Compare all supported frameworks |
| [GEPA Optimization](../guides/gepa-optimization.md) | Deep dive into optimization |
| [SuperSpec DSL](../guides/superspec.md) | Build custom agents |
| [Evaluation & Testing](../guides/evaluation-testing.md) | Advanced testing strategies |

### 🔄 Try Different Frameworks

!!! example "Explore Other Frameworks"
    ```bash
    # Try OpenAI SDK
    super agent pull assistant_openai
    super agent compile assistant_openai
    super agent evaluate assistant_openai
    super agent optimize assistant_openai --auto medium

    # Try CrewAI
    super agent pull researcher_crew
    super agent compile researcher_crew
    super agent evaluate researcher_crew
    super agent optimize researcher_crew --auto medium
    ```

### 🎨 Build Custom Agents

!!! tip "Create Your Own Agent"
    Create your own agent with SuperSpec:

    ```yaml
    # my_agent_playbook.yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: my_custom_agent
    spec:
      target_framework: dspy  # or openai, crewai, google-adk, microsoft, deepagents
      language_model:
        provider: ollama
        model: llama3.1:8b
      persona:
        role: Data Analyst
        goal: Analyze data and provide insights
      feature_specifications:
        scenarios:
          - name: Basic analysis
            input:
              data: "Sales data for Q1"
            expected_output:
              analysis: "Comprehensive analysis"
    ```

    Then compile and optimize:

    ```bash
    super agent compile my_custom_agent
    super agent evaluate my_custom_agent
    super agent optimize my_custom_agent --auto medium
    ```

---

## 🆘 Troubleshooting

### ❓ Common Issues

!!! question "Installation fails"
    **Solution**: Try using `pip install superoptix[all]` or check Python version with `python --version` (must be 3.11+)

!!! question "Optimization fails"
    **Solution**: Check that you have sufficient GPU RAM and Ollama is running with `ollama list`

!!! question "No improvement after optimization"
    **Solution**: Ensure your RSpec-style BDD scenarios are well-defined and provide clear success criteria

### 💬 Get Help

!!! help "Support Resources"
    - 📖 **Documentation**: [https://superoptix.ai/docs](https://superoptix.ai/docs)
    - 🐛 **GitHub Issues**: [https://github.com/SuperagenticAI/SuperOptiX/issues](https://github.com/SuperagenticAI/SuperOptiX/issues)
    - 🌐 **Website**: [https://superoptix.ai](https://superoptix.ai)

---

## Summary

!!! success "What You've Accomplished"

    | Skill | Status |
    |-------|--------|
    | Install SuperOptiX | Complete |
    | Initialize a project | Complete |
    | Choose from multiple frameworks | Complete |
    | Compile agents | Complete |
    | Evaluate performance | Complete |
    | Optimize with GEPA | Complete |
    | Deploy to production | Complete |

!!! note "Ready to Build More?"
    Check out our [Guides](../guides/index.md) for in-depth tutorials!
