# 🔧 Installation Guide

Welcome to SuperOptiX! This guide will help you install the Full Stack Agentic AI Optimization Framework on your system.

!!! tip "🚀 Quick Start"
    **New to SuperOptiX?** Start with our [Quick Start Guide](quick-start.md) after installation!

!!! tip "Stable Release Available!"
    SuperOptiX is now available as a stable release. We recommend using `uv` for the best experience.
    ```bash
    uv tool install superoptix
    ```

## 📋 Prerequisites

### Required

- **Python 3.11+** (required)
- **Git** (required for DSPy installation)
- **Package Manager** (uv recommended, pip also supported)

### Verify Requirements

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Check Git
git --version  # Should show git version
```

### Install Git (if needed)

=== "macOS"
    ```bash
    xcode-select --install
    ```

=== "Linux"
    ```bash
    # Ubuntu/Debian
    sudo apt-get install git
    
    # CentOS/RHEL
    sudo yum install git
    ```

=== "Windows"
    Download from [git-scm.com](https://git-scm.com/downloads)

!!! warning "Python Version Requirement"
    SuperOptiX requires **Python 3.11 or higher**. Check your version with:
    ```bash
    python --version
    ```

## 🎯 Installation Methods

!!! tip "Framework-Free Core"
    **SuperOptiX core is now framework-independent!** 🎉
    
    Install only what you need. Choose from 6 AI frameworks, or use core without any.

### Recommended: Using uv

We highly recommend using `uv` for faster, more reliable installations.

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install SuperOptiX CLI globally (isolated tool env)
uv tool install superoptix

# Verify
super --version
```

### Add Framework Dependencies with uv Tool

Use `--with` to install framework dependencies in the same tool environment:

```bash
# OpenAI SDK support
uv tool install superoptix --with "superoptix[frameworks-openai]"

# Claude SDK support
uv tool install superoptix --with "superoptix[frameworks-claude-sdk]"

# Google ADK support
uv tool install superoptix --with "superoptix[frameworks-google]"

# Pydantic AI support
uv tool install superoptix --with "superoptix[frameworks-pydantic-ai]"
```

Upgrade later:

```bash
uv tool upgrade superoptix
```

### Alternative: Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install SuperOptiX
pip install superoptix
```

## 📦 Optional Frameworks & Extras

Customize your installation by adding only what you need:

### 🌐 AI Frameworks

| Framework | Install Command | Includes |
|-----------|----------------|----------|
| **DSPy** ⭐ | `uv tool install superoptix --with "superoptix[frameworks-dspy]"` | DSPy + GEPA |
| **OpenAI SDK** | `uv tool install superoptix --with "superoptix[frameworks-openai]"` | openai-agents, openai SDK |
| **Claude SDK** | `uv tool install superoptix --with "superoptix[frameworks-claude-sdk]"` | claude-agent-sdk |
| **Google ADK** | `uv tool install superoptix --with "superoptix[frameworks-google]"` | google-adk, google-generativeai |
| **Microsoft (Legacy)** | `uv tool install superoptix --with "superoptix[frameworks-microsoft]"` | agent-framework, azure-identity |
| **DeepAgents** | `uv tool install superoptix --with "superoptix[frameworks-deepagents]"` | deepagents |
| **Pydantic AI** | `uv tool install superoptix --with "superoptix[frameworks-pydantic-ai]"` | Pydantic AI |
| **CrewAI** ⚠️ | `uv tool install superoptix --with "superoptix[frameworks-crewai]"` | crewai (conflicts with DSPy) |

⭐ **Recommended:** DSPy for GEPA optimization  
⚠️ **Note:** CrewAI and DSPy cannot be installed together in the same environment.

### 🔌 Tool Optimization & MCP

```bash
uv tool install superoptix --with "superoptix[mcp]"
```

### 🧠 Vector Databases (RAG)

```bash
# All vector databases
uv tool install superoptix --with "superoptix[vectordb]"

# Or specific ones
uv tool install superoptix --with "superoptix[chromadb]"    # ChromaDB (recommended)
uv tool install superoptix --with "superoptix[qdrant]"      # Qdrant
```

### 🔍 Observability

```bash
uv tool install superoptix --with "superoptix[observability]"
```
Includes MLflow, Pandas, Plotly.

### 💻 Local Model Management

```bash
# Apple Silicon (MLX)
uv tool install superoptix --with "superoptix[mlx]"

# HuggingFace
uv tool install superoptix --with "superoptix[huggingface]"
```

## 🔍 Verification

After installation, verify SuperOptiX is working correctly:

```bash
# Check CLI
super --version

# Check available commands
super --help
```

## 🚀 Next Steps

1. **Set up your LLM**: Follow our [LLM Setup Guide](llm-setup.md)
2. **Create your first agent**: Try our [Quick Start Guide](quick-start.md)
3. **Explore the framework**: Check out our [Agent Patterns](agent-patterns.md)

## 🆘 Troubleshooting

### Common Issues

**Import Error**: Make sure you're using Python 3.11+
```bash
python --version
```

**Package Not Found**: Update pip/uv
```bash
uv tool upgrade superoptix
```

**CrewAI Installation Conflicts**: If you encounter dependency conflicts when installing CrewAI with SuperOptiX:
```bash
# The issue: CrewAI requires json-repair==0.25.2, but DSPy needs json-repair>=0.30.0
# Solution: Install manually with --no-deps flag
uv tool install superoptix --with "superoptix[frameworks-dspy]"  # Install DSPy support first
uv tool install superoptix --with crewai==0.157.0  # Add CrewAI manually
uv tool install superoptix --with "json-repair>=0.30.0"  # Ensure compatible version
```

### Still Having Issues?

- 📖 Check our [Troubleshooting Guide](troubleshooting.md)
- 🐛 Report issues on [GitHub](https://github.com/SuperagenticAI/superoptix/issues)
