<div align="center">
  <a href="https://superagenticai.github.io/superoptix/">
    <img src="https://raw.githubusercontent.com/SuperagenticAI/superoptix/main/docs/logo.png" alt="SuperOptiX Logo" width="260" />
  </a>
  <h1>SuperOptiX AI</h1>
  <h3><strong>Full Stack Agentic AI Optimization Framework</strong></h3>

  <div style="margin: 20px 0;">
    <a href="https://badge.fury.io/py/superoptix">
      <img src="https://badge.fury.io/py/superoptix.svg" alt="PyPI version" />
    </a>
    <a href="LICENCE">
      <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0" />
    </a>
    <a href="https://www.python.org/downloads/">
      <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+" />
    </a>
    <img src="https://img.shields.io/badge/frameworks-8-purple.svg" alt="8 Frameworks" />
  </div>

  <p style="font-size: 1.0em; margin: 10px 0;">
    Evaluation-first workflow, framework-native pipelines, and GEPA optimization.
  </p>
</div>

---

## Quick Install

### Recommended CLI install with `uv`

```bash
uv tool install superoptix
super --help
```

### Add framework dependencies in the same tool environment

```bash
# OpenAI Agents SDK
uv tool install superoptix --with "superoptix[frameworks-openai]"

# Claude Agent SDK
uv tool install superoptix --with "superoptix[frameworks-claude-sdk]"

# Google ADK
uv tool install superoptix --with "superoptix[frameworks-google]"

# Pydantic AI
uv tool install superoptix --with "superoptix[frameworks-pydantic-ai]"

# DeepAgents
uv tool install superoptix --with "superoptix[frameworks-deepagents]"

# Microsoft Agent Framework (legacy support)
uv tool install superoptix --with "superoptix[frameworks-microsoft]"

# CrewAI (see note below)
uv tool install superoptix --with "superoptix[frameworks-crewai]"
```

CrewAI and DSPy have dependency constraints that may require separate environments in some setups.

### Alternative with `pip`

```bash
pip install superoptix
```

Requirements: Python 3.11+

---

## Framework Support

SuperOptiX supports compiling and running agents across:

- DSPy
- OpenAI Agents SDK
- Claude Agent SDK
- Pydantic AI
- CrewAI
- Google ADK
- DeepAgents
- Microsoft Agent Framework (legacy support)

---

## Core Workflow

```bash
# Pull
super agent pull developer

# Compile minimal pipeline
super agent compile developer --framework dspy

# Run
super agent run developer --framework dspy --goal "Design a migration strategy"

# Optional optimization path
super agent compile developer --framework dspy --optimize
super agent optimize developer --framework dspy --auto light
```

---

## Featured Capabilities

- RLM support (experimental)
- StackOne connector integrations for SaaS tools
- GEPA optimization flow across frameworks
- Minimal runtime pipelines by default with optional optimization lifecycle

---

## Documentation

- Docs home: https://superagenticai.github.io/superoptix/
- Golden workflow: https://superagenticai.github.io/superoptix/guides/golden-workflow/
- Framework feature matrix: https://superagenticai.github.io/superoptix/guides/framework-feature-matrix/
- StackOne integration: https://superagenticai.github.io/superoptix/guides/stackone-integration/
- RLM (experimental): https://superagenticai.github.io/superoptix/guides/rlm-experimental/
- Troubleshooting by symptom: https://superagenticai.github.io/superoptix/guides/troubleshooting-by-symptom/

---

## SuperOptiX Lite (Companion Repo)

For a lightweight, MIT-licensed starter kit focused on OpenAI Agents SDK + GEPA:

```bash
git clone https://github.com/SuperagenticAI/superoptix-lite-openai.git
```

---

## Support

- Website: https://superoptix.ai
- GitHub: https://github.com/SuperagenticAI/superoptix
- PyPI: https://pypi.org/project/superoptix/

---

## Telemetry

SuperOptiX collects anonymous usage data to improve the tool.

To disable telemetry:

```bash
export SUPEROPTIX_TELEMETRY=false
```

---

## License

Apache License 2.0. See [LICENCE](LICENCE).
