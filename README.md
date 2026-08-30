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

  <div style="margin: 16px 0 10px 0;">
    <a href="https://superoptix.ai">
      <img src="https://img.shields.io/badge/Website-superoptix.ai-111827?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Website" />
    </a>
    <a href="https://superagenticai.github.io/superoptix/">
      <img src="https://img.shields.io/badge/Docs-Open%20Documentation-0f766e?style=for-the-badge&logo=gitbook&logoColor=white" alt="Docs" />
    </a>
    <a href="https://superagenticai.github.io/superoptix/guides/a2a-guide/">
      <img src="https://img.shields.io/badge/A2A-v1%20Guide-0ea5e9?style=for-the-badge&logo=bookstack&logoColor=white" alt="A2A v1 Guide" />
    </a>
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

# Microsoft Agent Framework
uv tool install superoptix --with "superoptix[frameworks-microsoft]"
```

### CrewAI

CrewAI installs alongside SuperOptiX rather than as an extra:

```bash
pip install superoptix "crewai>=1.15"
```

Use a CrewAI-only environment for this: CrewAI requires `chromadb~=1.1.0`, while
SuperOptiX's `chromadb` / `turboagents` / `vectordb` extras require `chromadb>=1.5.5`.
The older DSPy/CrewAI `json-repair` conflict no longer applies — CrewAI 1.15+ and
DSPy 3.3 co-install cleanly.

### Alternative with `pip`

```bash
pip install superoptix
```

Requirements: Python 3.11+

---

## Framework Support

SuperOptiX supports compiling and running agents across:

| Framework | Minimum version | Extra |
|---|---|---|
| DSPy | 3.3+ | included in core |
| OpenAI Agents SDK | 0.20.x | `frameworks-openai` |
| Claude Agent SDK | 0.2+ | `frameworks-claude-sdk` |
| Pydantic AI | 2.31.x | `frameworks-pydantic-ai` |
| Google ADK | 2.7+ | `frameworks-google` |
| DeepAgents | 0.7.x | `frameworks-deepagents` |
| Microsoft Agent Framework | 1.16+ (1.0 GA) | `frameworks-microsoft` |
| CrewAI | 1.15+ | separate install (see above) |

Two upper bounds are upstream constraints, not choices:

- **OpenAI Agents SDK is held at `<0.21`.** 0.22+ requires `openai>=3.0`, while
  LiteLLM (a DSPy dependency) still requires `openai<3.0`.
- **Pydantic AI is held at `<2.32`.** 2.36 requires `opentelemetry-api==1.44`,
  while Google ADK 2.x caps it at `<=1.42.1`.

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
- TurboAgents-backed GEPA vector stores for Chroma, FAISS, LanceDB, and SurrealDB
- Minimal runtime pipelines by default with optional optimization lifecycle
- Core A2A v1 agent-to-agent interoperability

---

## TurboAgents Reference Integration

SuperOptiX is now the first full reference integration for `turboagents`.

Current validated state:

- `turboagents-chroma` is wired into the shared RAG layer and covered by focused runtime tests
- `turboagents-lancedb` is validated through the real `rag_lancedb_demo` flow
- `turboagents-surrealdb` is validated through the real OpenAI Agents and Pydantic AI SurrealDB demo flows
- the DSPy SurrealDB path is still blocked by a local LiteLLM and Ollama compatibility issue, not by the TurboAgents retrieval layer itself

Current backends exposed through SuperOptiX are:

- `turboagents-chroma`
- `turboagents-faiss`
- `turboagents-lancedb`
- `turboagents-surrealdb`

Read more:

- TurboAgents integration guide: https://superagenticai.github.io/superoptix/guides/turboagents-integration/
- Chroma demo: https://superagenticai.github.io/superoptix/examples/agents/rag-chroma-demo/
- LanceDB demo: https://superagenticai.github.io/superoptix/examples/agents/rag-lancedb-demo/
- SurrealDB frameworks guide: https://superagenticai.github.io/superoptix/examples/agents/surrealdb-frameworks-demo/

---

## A2A v1 Support

SuperOptiX implements the core A2A `1.0` protocol shape.

That includes:

- v1 Agent Cards with `supportedInterfaces[]`
- v1 task and message semantics
- v1 method surface such as `SendMessage`, `GetTask`, `CancelTask`, and `SubscribeToTask`
- serving compiled agents over A2A with `super agent serve <name> --protocol a2a`
- calling remote A2A agents through the SuperOptiX A2A client
- packaged A2A demos for DSPy, Pydantic AI, and Google ADK

Install the optional A2A extra:

```bash
pip install "superoptix[a2a]"
```

> SuperOptiX implements the A2A v1 wire shape directly over FastAPI rather than
> wrapping the `a2a-sdk` package. The extra installs the HTTP server stack only.

For the full packaged demo set:

```bash
pip install "superoptix[a2a,frameworks-pydantic-ai,frameworks-google]"
```

For demo details:

- DSPy demo: no model API key required
- Pydantic AI demo: no model API key required
- Google ADK demo: requires `GOOGLE_API_KEY`

Read more:

- A2A introduction: https://superagenticai.github.io/superoptix/guides/a2a-introduction/
- A2A guide: https://superagenticai.github.io/superoptix/guides/a2a-guide/
- A2A demo guide: https://superagenticai.github.io/superoptix/guides/a2a-demo-guide/

---

## Documentation

- Docs home: https://superagenticai.github.io/superoptix/
- Golden workflow: https://superagenticai.github.io/superoptix/guides/golden-workflow/
- Framework feature matrix: https://superagenticai.github.io/superoptix/guides/framework-feature-matrix/
- TurboAgents integration: https://superagenticai.github.io/superoptix/guides/turboagents-integration/
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
