# 🔧 Troubleshooting Guide

This guide covers common issues and their solutions when working with SuperOptiX.

For fast error-to-fix mapping, use [Troubleshooting by Symptom](guides/troubleshooting-by-symptom.md).

## 🚨 Dependency Conflicts

### CrewAI Installation Conflicts

**Problem:** You encounter dependency conflicts when trying to install CrewAI with SuperOptiX.

**Error Message:**
```
ERROR: Cannot install crewai==0.157.0 and dspy==3.0.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    dspy 3.0.0 depends on json-repair>=0.30.0
    crewai 0.157.0 depends on json-repair==0.25.2
```

**Root Cause:**
This is a **known dependency conflict** between CrewAI and DSPy due to incompatible `json-repair` version requirements:
- **DSPy 3.0.0** requires `json-repair>=0.30.0`
- **CrewAI 0.157.0** requires `json-repair==0.25.2` (exact version)

**Solution:**
Install CrewAI manually after installing SuperOptiX with DSPy support:

```bash
# Install SuperOptiX with DSPy support (this gets compatible json-repair)
pip install "superoptix[optimas]"

# Install CrewAI without dependencies to avoid conflicts
pip install crewai==0.157.0 --no-deps

# Ensure compatible json-repair version
pip install "json-repair>=0.30.0"
```

**Why This Works:**
- The `--no-deps` flag prevents pip from trying to resolve conflicting dependencies
- We manually install the version of `json-repair` that satisfies both packages
- Both packages work together at runtime despite metadata conflicts

**Alternative Solutions:**
1. **Use only CrewAI**: Install SuperOptiX without DSPy support, then add CrewAI normally
2. **Wait for updates**: Monitor for newer CrewAI versions that might fix the dependency conflict
3. **Use different versions**: Consider using older versions of DSPy if compatible with your needs

## 🔍 Build Issues

### Build Fails or `uv build` Missing

**Problem:** Build fails due to missing build tooling or an older uv version.

**Solutions:**
- Install build tooling: `uv pip install build` (or `pip install build`).
- Use `uv build` if available, otherwise run `uv run python -m build --wheel`.

## 🐍 Python Version Issues

### Python Version Too Old

**Problem:** SuperOptiX requires Python 3.11+ but you have an older version.

**Solution:**
Upgrade to Python 3.11 or higher:

```bash
# Check current version
python --version

# Install Python 3.11+ (example for macOS with Homebrew)
brew install python@3.11

# Or use conda
conda create -n superoptix python=3.11 -y
conda activate superoptix
```

## 📦 Package Installation Issues

### Permission Errors

**Problem:** Installation fails due to permission issues.

**Solution:**
Use virtual environments:

```bash
# Create virtual environment
python -m venv superoptix-env

# Activate (Linux/macOS)
source superoptix-env/bin/activate

# Activate (Windows)
superoptix-env\Scripts\activate

# Install SuperOptiX
pip install superoptix
```

### Package Not Found

**Problem:** SuperOptiX package cannot be found.

**Solution:**
Update pip and check PyPI:

```bash
# Update pip
pip install --upgrade pip

# Check if package exists
pip search superoptix

# Install from PyPI
pip install superoptix
```

## 🚀 Still Having Issues?

If you're still experiencing problems:

1. **📖 Check this guide** for your specific error
2. **🔍 Search existing issues** on [GitHub](https://mailto:hello@super-agentic.ai)
3. **🐛 Report new issues** with detailed error messages and system information
4. **💬 Join our community** for support and discussions

**When reporting issues, please include:**
- Python version (`python --version`)
- Operating system and version
- Complete error message
- Steps to reproduce the issue
- Package versions (`pip list | grep superoptix`) 
