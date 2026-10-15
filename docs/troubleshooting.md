# 🔧 Troubleshooting Guide

This guide covers common issues and their solutions when working with SuperOptiX.

For fast error-to-fix mapping, use [Troubleshooting by Symptom](guides/troubleshooting-by-symptom.md).

## 🚨 Dependency Conflicts

### CrewAI Installation Conflicts

**Problem:** You see a resolver conflict when installing CrewAI with SuperOptiX.

**Cause:** Older CrewAI releases pinned versions that clash with SuperOptiX extras:
`json-repair==0.25.2` (CrewAI before 1.15) and `chromadb~=1.1.0` (CrewAI 1.15.0 to 1.15.23).
Both are resolved upstream. CrewAI 1.15.24 and later use `json-repair~=0.60.1` and
`chromadb~=1.5.9`.

**Solution:** Install a current CrewAI next to SuperOptiX. No `--no-deps` workaround is needed.

```bash
uv pip install superoptix "crewai>=1.15.24"
```

**Google ADK note:** CrewAI is not in the `frameworks` extra. CrewAI needs
`opentelemetry-api>=1.42`, Microsoft Agent Framework's telemetry stack then needs `>=1.43`,
and Google ADK 2.8+ caps it at `<=1.42.1`. Combining CrewAI with the full `frameworks` extra
resolves, but with `google-adk` 2.7.0. If you need the latest ADK, use a separate environment
for CrewAI.

## 🔍 Build Issues

### Build Fails or `uv build` Missing

**Problem:** Build fails due to missing build tooling or an older uv version.

**Solutions:**
- Install build tooling: `uv pip install build` (or `uv pip install build`).
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
uv pip install superoptix
```

### Package Not Found

**Problem:** SuperOptiX package cannot be found.

**Solution:**
Update pip and check PyPI:

```bash
# Update pip
uv pip install --upgrade pip

# Check if package exists
pip search superoptix

# Install from PyPI
uv pip install superoptix
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
