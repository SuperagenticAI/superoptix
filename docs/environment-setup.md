# 🐍 Environment Setup Guide

This guide covers setting up your development environment for SuperOptiX, including Python environments, virtual environments, and best practices for different operating systems.

## 🎯 Overview

A properly configured environment is crucial for SuperOptiX development. This guide covers:

- **🐍 Python Setup**: Installing and configuring Python
- **🔧 Virtual Environments**: Isolating project dependencies (uv recommended)
- **📦 Package Management**: Using uv, pip, conda, and poetry
- **🛠️ Development Tools**: IDE setup and debugging tools

## 🐍 Python Setup

### **Python Version Requirements**

SuperOptiX requires Python 3.11+ (3.12 recommended):

```bash
# Check your Python version
python --version
# or
python3 --version

# Should show Python 3.11.x or 3.12.x
```

### **Installing Python**

=== "🍎 macOS"
    ```bash
    # Using Homebrew (recommended)
    brew install python@3.12
    
    # Using uv (to manage python versions)
    uv python install 3.12
    ```

=== "🐧 Linux (Ubuntu/Debian)"
    ```bash
    # Update package list
    sudo apt update
    
    # Install Python 3.12
    sudo apt install python3.12 python3.12-venv python3.12-pip
    ```

=== "🪟 Windows"
    ```bash
    # Using winget
    winget install Python.Python.3.12
    
    # Using uv
    uv python install 3.12
    ```
    
    !!! warning "Windows Users - Important!"
        
        **On Windows, set PYTHONUTF8=1** to ensure proper UTF-8 encoding support:
        
        ```cmd
        set PYTHONUTF8=1
        ```
        
        Or add it to your system environment variables for permanent setting.

## 🔧 Virtual Environments

### **Why Virtual Environments?**

Virtual environments isolate project dependencies, preventing conflicts between different projects:

- **Isolation**: Each project has its own Python packages
- **Reproducibility**: Exact dependency versions for consistent builds
- **Clean Development**: No system-wide package pollution
- **Easy Cleanup**: Remove entire environment when done

=== "⚡ uv (Recommended)"
    `uv` is an extremely fast Python package installer and resolver, written in Rust.

    ```bash
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Create a new virtual environment
    uv venv
    
    # Activate the environment
    # macOS/Linux:
    source .venv/bin/activate
    # Windows:
    .venv\Scripts\activate
    
    # Install SuperOptiX
    uv pip install superoptix
    ```

=== "🐍 venv (Built-in)"
    ```bash
    # Create a new virtual environment
    python -m venv superoptix-env
    
    # Activate the environment
    # On macOS/Linux:
    source superoptix-env/bin/activate
    
    # On Windows:
    superoptix-env\Scripts\activate
    
    # Install SuperOptiX
    pip install superoptix
    ```

=== "📦 conda"
    ```bash
    # Create a new conda environment
    conda create -n superoptix python=3.12
    
    # Activate the environment
    conda activate superoptix
    
    # Install SuperOptiX
    pip install superoptix
    ```

## 📦 Package Management

=== "⚡ uv (Recommended)"
    ```bash
    # Install SuperOptiX
    uv pip install superoptix
    
    # Install with optional dependencies
    uv pip install "superoptix[vectordb,ui,observability]"

    # Install as a global CLI tool
    uv tool install superoptix
    
    # Create requirements.txt
    uv pip freeze > requirements.txt
    
    # Install from requirements
    uv pip install -r requirements.txt
    ```

=== "📦 pip (Standard)"
    ```bash
    # Install SuperOptiX
    pip install superoptix
    
    # Install with optional dependencies
    pip install superoptix[vectordb,ui,observability]
    
    # Install latest version
    pip install --upgrade superoptix
    ```

## 🛠️ Development Tools

### **IDE Setup**

=== "💻 VS Code"
    ```bash
    # Install VS Code extensions
    code --install-extension ms-python.python
    code --install-extension charliermarsh.ruff
    ```

=== "🚀 Cursor"
    ```bash
    # Install Cursor extensions
    # Cursor comes with excellent Python support built-in
    ```

### **Code Quality Tools**

#### **Ruff (Code Formatting & Linting)**

Ruff is an extremely fast Python linter and formatter written in Rust:

```bash
# Install Ruff
uv pip install ruff

# Format code
ruff format .

# Lint code
ruff check .
```

## 🔧 Environment Variables

### **Setting Environment Variables**

=== "🍎 macOS/Linux"
    ```bash
    # Temporary (current session)
    export OPENAI_API_KEY="your-api-key"
    export ANTHROPIC_API_KEY="your-api-key"
    
    # Permanent (add to ~/.bashrc or ~/.zshrc)
    echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.bashrc
    source ~/.bashrc
    ```

=== "🪟 Windows"
    ```cmd
    # Temporary (current session)
    set OPENAI_API_KEY=your-api-key
    
    # Permanent (System Properties > Environment Variables)
    # Or use PowerShell:
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key", "User")
    ```

=== "📄 .env Files"
    ```bash
    # Create .env file
    cat > .env << EOF
    OPENAI_API_KEY=your-api-key
    ANTHROPIC_API_KEY=your-api-key
    EOF
    
    # Load with python-dotenv
    uv pip install python-dotenv
    ```

## 🧪 Testing Your Environment

### **Environment Validation**

```bash
# Test Python installation
python --version

# Test SuperOptiX installation
super --version

# Test basic functionality
python -c "import superoptix; print('SuperOptiX imported successfully!')"
```

## 🚨 Troubleshooting

### **Performance Optimization**

=== "⚡ Using uv for Faster Installs"
    ```bash
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Use uv instead of pip
    uv pip install superoptix
    ```

## 📚 Next Steps

1. **Install SuperOptiX** following the [Installation Guide](setup.md)
2. **Configure LLMs** with the [LLM Setup Guide](llm-setup.md)
3. **Create your first agent** with the [Quick Start Guide](quick-start.md)