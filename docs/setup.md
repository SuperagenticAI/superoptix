# 🔧 Installation Guide

Welcome to SuperOptiX! This guide will help you install the Full Stack Agentic AI Optimization Framework on your system.

!!! tip "🚀 Quick Start"
    **New to SuperOptiX?** Start with our [Quick Start Guide](quick-start.md) after installation!

!!! tip "Stable Release Available!"
    SuperOptiX is now available as a stable release. We recommend using `uv` for the best experience.
    ```bash
    uv pip install superoptix
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
# 1. Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create a virtual environment
uv venv

# 3. Activate the environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 4. Install SuperOptiX
uv pip install superoptix
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
| **DSPy** ⭐ | `uv pip install superoptix[frameworks-dspy]` | DSPy + GEPA |
| **OpenAI SDK** | `uv pip install superoptix[frameworks-openai]` | openai-agents, openai SDK |
| **Google ADK** | `uv pip install superoptix[frameworks-google]` | google-adk, google-generativeai |
| **Microsoft** | `uv pip install superoptix[frameworks-microsoft]` | agent-framework, azure-identity |
| **DeepAgents** | `uv pip install superoptix[frameworks-deepagents]` | deepagents |
| **Pydantic AI** | `uv pip install superoptix[frameworks-pydantic-ai]` | Pydantic AI |
| **CrewAI** ⚠️ | `uv pip install superoptix[frameworks-crewai]` | crewai (conflicts with DSPy) |

⭐ **Recommended:** DSPy for GEPA optimization  
⚠️ **Note:** CrewAI and DSPy cannot be installed together in the same environment.

### 🔌 Tool Optimization & MCP

```bash
uv pip install superoptix[mcp]
```

### 🧠 Vector Databases (RAG)

```bash
# All vector databases
uv pip install "superoptix[vectordb]"

# Or specific ones
uv pip install "superoptix[chromadb]"    # ChromaDB (recommended)
uv pip install "superoptix[qdrant]"      # Qdrant (production)
```

### 🔍 Observability

```bash
uv pip install "superoptix[observability]"
```
Includes MLflow, Pandas, Plotly.

### 💻 Local Model Management

```bash
# Apple Silicon (MLX)
uv pip install "superoptix[mlx]"

# HuggingFace
uv pip install "superoptix[huggingface]"
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
uv pip install --upgrade superoptix
```

**CrewAI Installation Conflicts**: If you encounter dependency conflicts when installing CrewAI with SuperOptiX:
```bash
# The issue: CrewAI requires json-repair==0.25.2, but DSPy needs json-repair>=0.30.0
# Solution: Install manually with --no-deps flag
uv pip install "superoptix[optimas]"  # Install DSPy support first
uv pip install crewai==0.157.0 --no-deps  # Install CrewAI without dependencies
uv pip install "json-repair>=0.30.0"  # Ensure compatible version
```

### Still Having Issues?

- 📖 Check our [Troubleshooting Guide](troubleshooting.md)
- 🐛 Report issues on [GitHub](https://github.com/SuperagenticAI/superoptix/issues)