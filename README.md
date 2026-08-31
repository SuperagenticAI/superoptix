<div align="center">
  <a href="https://superagenticai.github.io/superoptix/">
    <img src="https://raw.githubusercontent.com/SuperagenticAI/superoptix/main/docs/logo.png" alt="SuperOptiX Logo" width="260" />
  </a>
  <h1>SuperOptiX AI</h1>
  <h3><strong>Agent-to-Agent (A2A) Interoperability and Optimization Layer</strong></h3>
  <p>Make the agents you already run A2A-compliant, and get them discovered.</p>

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
    A2A 1.0 at full conformance, an adapt path for eight agent runtimes, and
    GEPA optimization of how agents are discovered.
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
uv tool install superoptix --with "crewai>=1.15"
```

Use a CrewAI-only environment for this: CrewAI requires `chromadb~=1.1.0`, while
SuperOptiX's `chromadb` / `turboagents` / `vectordb` extras require `chromadb>=1.5.5`.
The older DSPy/CrewAI `json-repair` conflict no longer applies — CrewAI 1.15+ and
DSPy 3.3 co-install cleanly.

### Adding SuperOptiX to an existing project

```bash
uv add superoptix
```

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

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

- Adapt agents built outside SuperOptiX to A2A 1.0 without modifying them
- A2A 1.0 server at 100% conformance against the official Technology Compatibility Kit
- Routing-quality measurement and GEPA optimization over the Agent Card
- GEPA optimization flow across frameworks
- TurboAgents-backed GEPA vector stores for Chroma, FAISS, LanceDB, and SurrealDB
- Minimal runtime pipelines by default with optional optimization lifecycle

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

## A2A Support

SuperOptiX implements the A2A `1.0` protocol directly over FastAPI. The
`a2a-sdk` package is not a dependency.

### Conformance

Measured with the [official A2A TCK](https://github.com/a2aproject/a2a-tck):

| Level | Compliance |
|---|---|
| MUST | 100% |
| SHOULD | 100% |
| MAY | 100% |

The suite runs in CI on every change to the protocol layer, with a floor that
fails the build if compliance regresses.

### Adapting an existing agent

Agents built before you adopted SuperOptiX can be given an A2A endpoint without
being rewritten:

```bash
super a2a adapt --entrypoint mycrew:crew --framework crewai
uvicorn a2a.a2a_server:app --port 8000
```

This reads the agent's structure, derives the skills a calling agent would route
on, and writes an Agent Card and a server. Your code is not modified.
Introspectors ship for all eight supported frameworks; the framework is detected
when not specified.

### Protocol surface

- All eleven A2A 1.0 methods answer. Push-notification configuration and the
  extended agent card return the errors the spec defines for an agent that does
  not offer them, rather than a 404
- JSON-RPC 2.0 and HTTP+JSON bindings
- `0.3` and `1.0` served from one endpoint, selected with the `A2A-Version`
  header, so agents on the pre-1.0 line remain reachable
- Serving compiled agents with `super agent serve <name> --protocol a2a`
- Calling remote A2A agents through the SuperOptiX A2A client

gRPC and signed Agent Cards are not implemented.

### MCP

Agents adapted by SuperOptiX keep using their MCP tools. SuperOptiX changes how
an agent is reached, not how it works. Exposing an agent as an MCP server is not
supported.

Install the optional A2A extra:

```bash
uv tool install superoptix --with "superoptix[a2a]"
```

For the full packaged demo set:

```bash
uv tool install superoptix --with "superoptix[a2a,frameworks-pydantic-ai,frameworks-google]"
```

For demo details:

- DSPy demo: no model API key required
- Pydantic AI demo: no model API key required
- Google ADK demo: requires `GOOGLE_API_KEY`

Read more:

- A2A introduction: https://superagenticai.github.io/superoptix/guides/a2a-introduction/
- Adapting an existing agent: https://superagenticai.github.io/superoptix/guides/a2a-adapt/
- A2A conformance: https://superagenticai.github.io/superoptix/guides/a2a-conformance/
- Routing quality: https://superagenticai.github.io/superoptix/guides/a2a-routing/
- A2A guide: https://superagenticai.github.io/superoptix/guides/a2a-guide/
- A2A demo guide: https://superagenticai.github.io/superoptix/guides/a2a-demo-guide/

---

## Documentation

- Docs home: https://superagenticai.github.io/superoptix/
- Golden workflow: https://superagenticai.github.io/superoptix/guides/golden-workflow/
- Framework feature matrix: https://superagenticai.github.io/superoptix/guides/framework-feature-matrix/
- TurboAgents integration: https://superagenticai.github.io/superoptix/guides/turboagents-integration/
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
