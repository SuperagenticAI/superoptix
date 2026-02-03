# 🐛 Debugging Guide

Having trouble with SuperOptiX? This guide will help you diagnose and fix common issues, from installation to agent orchestration.

---

## 🚦 Common Errors & Fixes

- **Installation issues:**  
  - Python version mismatch  
  - Missing dependencies  
  - **Solution:** Check `pyproject.toml`, use a clean virtual environment

- **CLI errors:**  
  - “command not found”, “not a super project”  
  - **Solution:** Run from project root, ensure `.super` file exists

- **Agent compilation errors:**  
  - YAML syntax errors, missing playbooks  
  - **Solution:** Validate YAML, check agent directory

- **Model/server errors:**  
  - Model not found, server not running  
  - **Solution:** Check model install, server logs, port conflicts

- **Memory/tool integration errors:**  
  - Backend not installed, misconfigured settings  
  - **Solution:** Check backend install, review config

---

## 🛠️ Debugging Tools & Techniques

- Use `super <command> --verbose` for more output
- Check logs in `logs/` or as printed in the terminal
- Use Python debuggers (`pdb`, IDE breakpoints)
- Enable tracing/observability (if available)

---

## 📝 Troubleshooting Checklist

1. Are you in the project root? (`.super` file present)
2. Did you activate your virtual environment?
3. Are all dependencies installed?
4. Is your YAML valid? (use [YAML Linter](https://www.yamllint.com/))
5. Is the model installed and server running?
6. Are you using the correct CLI command?

---

## ❓ FAQ

- **“Why do I get ‘command not found’?”**  
  Make sure you installed SuperOptiX and activated your environment.

- **“Why does my agent not appear?”**  
  Check the agent directory and playbook naming.

- **“Why do I get a backend error?”**  
  Ensure the required backend (memory, tool, model) is installed and configured.

---

## 📚 Additional Resources

- [Documentation](../index)

---

*If you find a bug, please report it with your OS, Python version, CLI command, and error output!* 