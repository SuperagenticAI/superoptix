# 📋 Changelog

All notable changes to SuperOptiX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Dependency modernization.** All framework integrations moved onto their current
  upstream releases after ~4 months of drift:

  | Framework | Was | Now |
  |---|---|---|
  | DSPy | 3.1.2 (no floor) | 3.3.1 (`>=3.3`) |
  | OpenAI Agents SDK | 0.14.1 | 0.20.0 |
  | Google ADK | 1.14.1 | 2.7.0 |
  | Pydantic AI | 1.22.0 | 2.31.1 |
  | DeepAgents | 0.5.6 (capped `<0.6.0`) | 0.7.11 |
  | Claude Agent SDK | 0.1.31 | 0.2.148 |
  | Microsoft Agent Framework | 1.0.0rc3 (beta pin) | 1.16.0 (1.0 GA) |
  | LiteLLM | 1.81.6 | 1.100.x |

- **Refreshed default model IDs across playbooks, templates, docs, and examples**
  (~380 references). `gpt-4o*` → `gpt-5.6-terra` / `gpt-5.6-luna`,
  `gemini-2.x` → `gemini-3.7-flash` / `gemini-3.1-pro-preview` / `gemini-3.5-flash-lite`,
  `claude-3.x` and `claude-*-4*` → `claude-sonnet-5` / `claude-opus-5` / `claude-haiku-4-5-20251001`.

- CrewAI documentation corrected. The historical DSPy `json-repair` conflict is
  resolved upstream (CrewAI 1.15+ requires `json-repair~=0.60.1`, satisfying DSPy 3.3).
  The live constraint is `chromadb~=1.1.0` vs SuperOptiX's `chromadb>=1.5.5` extras,
  so CrewAI installs as `pip install superoptix "crewai>=1.15"` in its own environment.

### Fixed
- **A2A conformance: 100% MUST / 100% SHOULD / 100% MAY**, up from 42.6% MUST, measured
  with the official [A2A TCK](https://github.com/a2aproject/a2a-tck). Four fixes:
  - `Task` no longer carries `createdAt` / `lastModified`. The A2A 1.0 Task
    schema sets `additionalProperties: false`, so every task was failing schema
    validation. Timestamps moved beside the task; `status.timestamp` is unchanged.
  - **JSON-RPC errors now return HTTP 200** with the failure inside the envelope,
    and A2A errors carry a `google.rpc.ErrorInfo` entry in the `data` array
    (spec 9.5). Returning 4xx made conformant clients treat the response as a
    transport failure and never read the error code.
  - **The JSON-RPC route is served with and without a trailing slash.** A client
    using the interface URL as an HTTP base and posting to `/` resolves to
    `<rpc_url>/`; Starlette answered the mismatch with an empty 307 body that
    JSON-RPC clients cannot parse. This single fix moved compliance 54% → 77%.
  - `CancelTask` on a terminal task now returns `TaskNotCancelableError` instead
    of silently succeeding, and the push-notification methods return
    `PushNotificationNotSupportedError` rather than `MethodNotFound`.
  - **A follow-up message carrying a `taskId` continues that task** instead of
    forking a new one, and the runtime now sees the message it is answering
    rather than the first message in the history.
  - **Subscribers always observe status transitions.** The publish flag gated the
    streaming caller's own feed; anyone attached via `SubscribeToTask` never saw
    the task finish and their stream hung open.
  - `SendMessage` validates its task reference: unknown task, terminal task and
    mismatched `contextId` are each rejected with the spec'd error.
  - `GetTask` honours `historyLength`; runtimes may declare a non-terminal state
    (`input_required`), return artifacts, or answer with a bare `Message`.
- HTTP+JSON errors now use AIP-193 bodies with ProtoJSON `details`, unsupported
  media types return 415 rather than FastAPI's 422, and `A2A-Version` is
  negotiated against the 1.0 and 0.3 lines the card advertises.

### Added
- `superoptix/protocols/a2a/errors.py` — the A2A error binding table (JSON-RPC
  code, HTTP status, ErrorInfo reason) with ProtoJSON payload builders.
- `superoptix/protocols/a2a/tck_sut.py` — the conformance harness. The TCK drives
  protocol states through magic `messageId` prefixes; the published agent must
  not honour client-supplied ids that way, so the hooks live in a separate app
  sharing the same server implementation.
- `.github/workflows/a2a-conformance.yml` — runs the official TCK against the SUT
  harness on every change to the protocol or runtime packages, publishes the
  compatibility report as a build artifact, and fails if MUST-level compliance
  regresses below 100%.

### Removed
- **StackOne connector integration.** Removed across the tree: the
  `StackOneBridge` adapter, three connector agent playbooks (HRIS, ATS, CRM),
  four demo playbooks, the benchmark suite, nine examples, the
  `build_stackone_tools` / `resolve_stackone_config` helpers in every runtime,
  the `stackone` tool mode in SuperSpec and its validator rules, the Jinja
  template branches, the `connectors-stackone` extra, and the docs. Agent tool
  lists are now built from the framework's own tools and MCP servers.

### Removed
- **The harness runtime and `super harness run/serve`.** SuperQode already ships
  this layer with a 6-stage execution model and a 97-harness hub; SuperOptiX was
  carrying a smaller second copy. Nothing in the optimizer or the A2A layers
  imported it — it was a self-contained product surface, so the cut is complete
  rather than surgical. This includes the Codex CLI backend, which put a coding
  agent inside the agent-framework product.
- **RLM.** SuperQode ships Native RLM as a flagship feature; two implementations
  of one idea in a single portfolio is worse than one good one. Removed across
  the tree: the `rlm_code` runtime and mode utils, five demo playbooks, the
  SuperSpec schema/validator/parser fields, per-framework `rlm` config blocks,
  Jinja template branches, the `--rlm` compile flag, the `rlm-native` and
  `rlm-code` extras, and the docs. `run_agent_with_optional_rlm` is now simply
  `run_agent`. All eight frameworks still compile to valid pipelines.

### Removed
- **`torch`, `transformers` and `accelerate` are no longer core dependencies.**
  Only `superoptix/models/backends/huggingface*.py` imports them, always lazily,
  and they were already declared in the `huggingface` and `ml-cross-platform`
  extras. They added ~545 MB to every install (torch alone is 491 MB) for an
  optional local-inference backend. `pip install "superoptix[a2a]"` drops from
  ~650 MB to ~219 MB. Install `superoptix[huggingface]` to use that backend.

### Changed
- **Repositioned as the Agent-to-Agent (A2A) interoperability and optimization
  layer.** The previous description, "Full Stack Agentic AI Optimization
  Framework", no longer matched the product after the harness, RLM and connector
  removals. Applied to `pyproject.toml`, the README, the documentation index and
  the CLI banner.
- The MCP relationship is now stated in the direction it exists. Adapted agents
  continue to use their MCP tools; exposing an agent as an MCP server is not
  supported, and the documentation says so rather than implying two-way support.

### Fixed
- **Documentation site build.** Removing RLM left an empty `🧪 RLM` navigation
  section in `mkdocs.yml`. A nav entry with no children parses as null, which
  invalidates the entire nav, so `mkdocs build` aborted with
  `Config value 'nav': Expected nav to be a list, got None`.

### Added
- Documentation for the A2A work: [Adapting an existing agent](guides/a2a-adapt.md),
  [A2A conformance](guides/a2a-conformance.md) and
  [Routing quality](guides/a2a-routing.md), covering the eight introspectors,
  entrypoint resolution, the generated intermediate representation, TCK
  procedure, 0.3/1.0 negotiation, the error binding table, and the routing
  metric with its evaluation-set constraint.
- `super a2a adapt` documented in the CLI reference, and A2A capability added to
  the framework feature matrix.

### Changed
- **Corrected documentation that contradicted the current implementation.** The
  A2A introduction, guide and integration checklist still told readers that A2A
  support arrived through `a2a-sdk[http-server]==0.3.25`, a dependency removed
  earlier in this release. They now describe the direct implementation and point
  at measured conformance results.
- README rewritten around what the release actually does: adapting existing
  agents, conformance figures, and the protocol surface with its gaps stated.
- Framework version claims across the documentation corrected to match
  `pyproject.toml` — DeepAgents 0.2.0 to 0.7, DSPy 3.0 to 3.3, CrewAI 0.157 to
  1.15, `openai-agents>=0.14` to `>=0.20,<0.21`, and the Microsoft Agent
  Framework beta pin to 1.16. "Microsoft (Legacy)" relabelled, since that
  framework reached 1.0 GA in April 2026.

### Added
- **All eight frameworks now adapt.** `super a2a adapt` gained introspectors for
  OpenAI Agents SDK, Pydantic AI, Google ADK, Microsoft Agent Framework, Claude
  Agent SDK and DeepAgents, joining CrewAI and DSPy. Each reader is small
  because the IR and every emitter are shared — a framework needs one reader in,
  and gets the Agent Card, the server, the 0.3 bridge and the routing metric for
  free. Object shapes were read from the installed packages, not inferred:

  | Framework | Skills derived from |
  |---|---|
  | OpenAI Agents SDK | `tools[].name` / `.description` |
  | Pydantic AI | `_function_toolset.tools` |
  | Google ADK | `description`, plus `sub_agents` |
  | Microsoft Agent Framework | `description` / `instructions` |
  | Claude Agent SDK | `AgentDefinition.description` or `ClaudeAgentOptions.system_prompt` |
  | DeepAgents | subagent `name` / `description` |

- **0.3 ↔ 1.0 negotiation** (`superoptix/protocols/a2a/bridge.py`). One endpoint
  serves both spec lines: a caller sending `A2A-Version: 0.3` receives 0.3 task
  states (`completed`), roles (`agent`), `kind`-tagged Parts and a card with a
  top-level `url`, while a 1.0 caller is unaffected. This is table stakes rather
  than differentiation, but the installed base is on 0.3 — five of the eight
  frameworks declare no A2A at all and the three that do are pinned pre-1.0 — so
  without it the brownfield claim is false for most of the market.

### Added
- **Routing-quality metric** (`superoptix/protocols/a2a/routing/`). Scores how
  well other agents can route to yours, because a gateway makes an agent
  reachable but only its Agent Card makes it worth reaching. Three numbers,
  since "invisible" and "confusable" fail differently: **discovery** (surfaced at
  all), **invocation** (chosen first), and **confusion** (lost to a sibling
  rather than being unseen).

  The metric moves on description quality alone. Four sibling support skills,
  identical queries, differing only in how each describes itself:

  | Catalogue | Invocation | Discovery |
  |---|---|---|
  | Vague (`"Handle a customer query"`) | 12.5% | 75% |
  | Specific (names the vocabulary users bring) | 100% | 100% |

  Ships a deterministic `LexicalRouter` so baselines are reproducible without a
  provider, and an `LLMRouter` for use as a held-out validator — optimising and
  scoring with one router measures that router's reading habits, not
  interoperability.

- **GEPA over the routing surface** (`routing/optimize.py`). Optimises
  `skills[].description` and `skills[].examples`, exactly what the adapt IR
  declares optimisable; identity and protocol fields stay out of reach. Failures
  are fed back as text naming the sibling that stole the query, which is what
  GEPA reflects on. On the vague catalogue above it lifts invocation from
  **12.5% to 75%**.

### Known limitation
- **The routing eval set must come from outside the Agent Card.** Deterministic
  query generation from the card is circular: every field either is the
  description under optimisation or was derived from it, so a generated query
  wins by echoing what it is meant to test. `generate_cases(hard=True)` withholds
  the skill name to reduce the leak and is useful as a smoke test, but a
  meaningful benchmark needs LLM-generated caller-vocabulary queries or real
  traffic. GEPA's own `gskill` avoids this by mining tasks from a repository —
  ground truth independent of the artifact being optimised. There is no
  equivalent free source here.

### Added
- **`super a2a adapt` — make an agent you already built speak A2A 1.0.**
  Point it at your own code and it emits an Agent Card and a conformant server
  without modifying the agent:

  ```
  super a2a adapt --entrypoint mycrew:crew --framework crewai
  super a2a adapt --entrypoint app.rag:program --framework dspy --out ./a2a
  ```

  Introspectors ship for **CrewAI** (crews, tasks and agents) and **DSPy**
  (modules and signatures); the framework is detected when not given. A DSPy
  signature is unusually good source material — it already names its inputs and
  outputs with per-field descriptions, which maps almost directly onto a skill.

  The generated agent **scores 86.3% MUST on the official A2A TCK**, identical
  to SuperOptiX's own published endpoint; every remaining failure is a TCK test
  hook that a production agent deliberately does not implement.

- **SuperSpec as a generated intermediate representation**
  (`superoptix/protocols/a2a/adapt/`). On the adapt path SuperSpec is emitted by
  introspection rather than written by hand — the user never authors one. Each
  framework needs one introspector in and shares every emitter out, which is
  what makes covering eight of them tractable, and the IR records which fields
  GEPA may later rewrite (`skills[].description`, `skills[].examples` — the
  routing interface other agents read, never identity or protocol fields).

### Added
- **Public A2A endpoint and Agent Card** (`superoptix/protocols/a2a/public/`).
  Two deterministic, vendor-neutral skills served over A2A — no model calls, no
  user code, no credentials:
  - `framework-a2a-readiness` — A2A support and spec line for each of the eight
    supported agent frameworks, answered from published package metadata.
  - `agent-card-review` — scores an A2A Agent Card for 1.0 conformance and
    discoverability.
  Deployable as an ASGI app (`superoptix.protocols.a2a.public.app:app`); see
  `deploy/a2a/` for the Render blueprint and publishing guide.
- Agent Card builder now emits the full A2A 1.0 field set: top-level
  `protocolVersion` and `url`, `preferredTransport`, `securitySchemes`,
  `iconUrl`, `documentationUrl`, and optional dual advertisement of the 0.3 line
  so pre-1.0 clients can still negotiate.

### Fixed
- **`__version__` no longer drifts from the release version.** It read `0.2.24`
  while `pyproject.toml` declared `0.2.25`; it is now derived from installed
  package metadata.
- **`superoptix[a2a]` no longer depends on `a2a-sdk`.** The package was declared in
  three extras but never imported — SuperOptiX implements the A2A v1 wire shape
  directly over FastAPI. The extra had been supplying FastAPI transitively via
  `a2a-sdk[http-server]`; `fastapi` and `sse-starlette` are now declared explicitly,
  and the obsolete `a2a-sdk==0.3.25` pin (the pre-1.0 SDK line) is gone.
- Removed `google-generativeai` from the Google extra. It is deprecated upstream
  (superseded by `google-genai`) and was never imported.
- Repaired 13 dead documentation navigation links. The entire API Reference nav
  subtree pointed at `docs/reference/**` files that do not exist.
- Surfaced previously orphaned documentation in the nav: the harness & sandbox
  guide, memory & context optimization guide, the three ADRs, glossary, changelog,
  and contributing guide.

### Removed
- Internal DeepAgents/Gemini working notes moved out of `docs/` into `dev-notes/`
  so they are no longer published to the documentation site.
- Stray `research_agent_deepagents_playbook.yaml.bak` removed from version control.

## [0.2.25] - 2026-04-15

### Added
- **OpenAI Agents SDK Support** - Full adoption of the new OpenAI Agents SDK as a first-class framework target alongside DSPy, Claude SDK, Pydantic AI, CrewAI, Google ADK, and DeepAgents.
- New CLI command `super agent pull --framework openai-agents` to pull agents compatible with the OpenAI Agents SDK.
- New CLI command `super agent compile <agent> --framework openai-agents` to compile SuperSpecs into OpenAI Agents SDK pipelines.
- SuperSpec schema extensions for OpenAI Agents SDK configuration (`spec.openai_agents`).
- New validators for OpenAI Agents SDK-specific settings including tracing, tracingoff, maxTurns, and handoffs.
- Jinja2 pipeline templates for OpenAI Agents SDK: `openai_pipeline_minimal.py.jinja2` and `openai_pipeline_optimized.py.jinja2`.

### Changed
- OpenAI SDK integration docs now clarify the distinction between the legacy OpenAI SDK and the new OpenAI Agents SDK.
- Feature matrix updated to show OpenAI Agents SDK as a supported framework target.

### Documentation
- Added ADR (Architecture Decision Record) for OpenAI Harness Sandbox Adoption.
- Added OpenAI Agents SDK adoption summary guide with migration details.

## [0.2.24] - 2026-04-08

### Added
- Arize Phoenix observability integration for SuperOptiX framework runtimes via the shared Phoenix helper path.
- Pullable DSPy demo agent `arize-phoenix-demo` for trace-first Phoenix demos with `super agent pull arize-phoenix-demo`.

### Changed
- Demo and examples navigation now includes a dedicated Arize Phoenix example page.
- Observability docs now include a user-facing Phoenix walkthrough covering both `super agent pull arize-phoenix-demo` and adapting `super agent pull developer` with `spec.phoenix`.

### Fixed
- Phoenix session span setup now tolerates tracers that do not expose OpenInference-style `set_input`, avoiding runtime failure during traced DSPy runs.

### Documentation
- Added a detailed Arize Phoenix demo guide with setup, pull, compile, run, and troubleshooting steps.
- Expanded observability documentation to show how to configure `spec.phoenix` in a pulled agent playbook.

## [0.2.23] - 2026-03-28

### Fixed
- DSPy Ollama model normalization now strips `ollama:` and `ollama/` prefixes before constructing LiteLLM-compatible `ollama_chat/...` model names.
- DSPy local Qwen playbooks no longer fail immediately with invalid model names when using Ollama-backed runtimes.

## [0.2.22] - 2026-03-28

### Added
- TurboAgents-backed Chroma retrieval support in the shared RAG path and GEPA vector-store layer.
- TurboAgents integration docs and demo coverage for Chroma, LanceDB, and SurrealDB.
- Source-checkout guidance for validating TurboAgents-backed RAG flows across SuperOptiX frameworks.

### Changed
- SuperOptiX demo playbooks now prefer Qwen local models for the current TurboAgents validation path.
- SurrealDB seed tooling now writes TurboAgents-compatible payloads and matches runtime embedding truncation.
- TurboAgents docs now describe SuperOptiX as the first full reference integration.

### Fixed
- TurboAgents SurrealDB auth is preserved in the shared RAG setup path.
- DSPy runner and minimal pipeline template now pass `api_base` through to DSPy LM setup.
- Dependency metadata now excludes compromised LiteLLM releases `1.82.7` and `1.82.8`.

### Security
- SuperOptiX now blocks LiteLLM `1.82.7` and `1.82.8` in dependency resolution after the March 2026 PyPI compromise advisory.

## [0.2.20] - 2026-03-15

### 🚀 Added
- Packaged Google ADK A2A demo assets and pull alias support for `a2a-adk-demo`.
- Packaged Google ADK A2A server demo module for installed-package usage.

### 🔄 Changed
- Updated A2A docs and README to reflect DSPy, Pydantic AI, and Google ADK demo coverage.
- Prepared the follow-up package release so installed users can pull the Google ADK A2A demo without a source checkout.

## [0.2.19] - 2026-03-15

### 🚀 Added
- Core A2A v1 support as a native SuperOptiX protocol capability.
- `super agent serve <name> --protocol a2a` for exposing compiled agents over A2A.
- A2A client and server bridges with Agent Card generation and task-oriented interoperability.
- Packaged A2A demos for DSPy and Pydantic AI, plus pullable demo agents.

### 🔄 Changed
- Replaced the old Agenspy-oriented protocol path with a neutral runtime and protocol architecture.
- Updated the website and docs to present A2A as a first-class top-level SuperOptiX capability.

### 📚 Documentation
- Added dedicated A2A v1 introduction, guide, demo guide, and integration checklist documentation.
- Added website navigation and landing page coverage for A2A support.

## [0.2.12] - 2026-03-04

### 🚀 Added
- SurrealDB GraphRAG demo playbooks for all supported frameworks (DSPy, OpenAI, Claude SDK, Microsoft, PydanticAI, CrewAI, Google ADK, DeepAgents).
- Lean SurrealDB parity checks in test matrix for both RAG and GraphRAG playbooks.

### 🔄 Changed
- SurrealDB docs rewritten for beginner-first setup and troubleshooting.
- SurrealDB docs now use source-independent seeding commands via `python -m superoptix.agents.demo.setup_surrealdb_seed`.
- SurrealDB examples index updated to reflect full feature coverage.

### 🐛 Fixed
- DSPy SurrealDB runtime compile/run parity in demo flow.
- SurrealDB GraphRAG feature detection compatibility (RELATE probe parsing).
- SurrealDB graph traversal query compatibility for parser variants that reject wildcard `->*` syntax.

### 📚 Documentation
- Added explicit SurrealDB feature coverage map with tags and runnable commands (vector, hybrid, GraphRAG, multi, temporal, server embeddings, live utility, MCP tool, capability gating).
- Added beginner-friendly runbooks for SurrealDB local and Docker workflows with expected outputs and error-to-fix steps.

## [0.2.9] - 2026-02-21

### 🚀 Added
- **SurrealDB RAG Integration**: Added native SurrealDB retriever support in runner-managed RAG flows
  - Added `surrealdb` retriever setup/query/document-ingest paths in `RAGMixin`
  - Added SurrealDB vector store adapter for GEPA RAG (`surrealdb_store.py`)
  - Added SuperSpec validation/schema support for `surrealdb` retriever type
- **Framework Demo Agents**: Added new SurrealDB RAG demo playbooks for:
  - DSPy embedded mode: `rag_surrealdb_demo`
  - DSPy Docker mode: `rag_surrealdb_docker_demo`
  - PydanticAI: `rag_surrealdb_pydanticai_demo`
  - CrewAI: `rag_surrealdb_crewai_demo`
  - Google ADK: `rag_surrealdb_adk_demo`

### 🔄 Changed
- **Framework Pipeline RAG Context Injection**: Updated minimal pipeline templates to inject retrieved SurrealDB context for:
  - `pydantic_ai_pipeline_minimal.py.jinja2`
  - `crewai_pipeline_minimal.py.jinja2`
  - `google_adk_pipeline_minimal.py.jinja2`
- **SurrealDB URL Handling**: Improved URL normalization for SurrealDB server endpoints to reduce transport/path mismatch issues.

### 📚 Documentation
- Added detailed SurrealDB documentation pages:
  - Embedded demo guide
  - Docker demo guide
  - Framework guide for DSPy, PydanticAI, CrewAI, and Google ADK
- Updated docs navigation and examples index with SurrealDB sections and quick-start workflows.

### ✅ Tests
- Added SurrealDB vector store tests in `tests/test_surrealdb_vector_store.py`.

## [0.1.0b17] - 2025-08-18

### 🔧 Fixed
- **Agent Naming Consistency**: Fixed inconsistent agent IDs (hyphens vs underscores) across all GEPA agents
  - Standardized all agent IDs to use underscores to match filename convention
  - Fixed: `advanced_math_gepa`, `enterprise_extractor_gepa`, `medical_assistant_gepa`, `contract_analyzer_gepa`, `privacy_delegate_gepa`, `data_science_gepa`, `security_analyzer_gepa`, `gepa_demo`
- **Genies Tier Optimization Bug**: Fixed `input_field` variable scope error in DSPy Genies pipeline template
  - Resolved "name 'input_field' is not defined" error during optimization
  - Added proper variable scoping in train() and evaluate() methods
  - Genies tier agents now optimize successfully with BootstrapFewShot, SIMBA, and BetterTogether optimizers

### 📚 Documentation
- **Comprehensive GEPA Documentation**: Added detailed documentation for all 8 GEPA agents across multiple domains
  - Mathematics: `advanced_math_gepa`, `data_science_gepa`
  - Healthcare: `medical_assistant_gepa`
  - Legal: `contract_analyzer_gepa`
  - Enterprise: `enterprise_extractor_gepa`
  - Security: `security_analyzer_gepa`, `privacy_delegate_gepa`
  - Demo: `gepa_demo`
- **DSPy Optimizers Quick Start Guide**: Added comprehensive quick start commands for all 8 DSPy optimizers
  - Complete workflows (pull, compile, optimize, test) for each optimizer
  - Domain-specific examples and use cases
  - Performance comparisons and best practices
- **GEPA Limitations Documentation**: Added critical guidance about GEPA compatibility
  - Clear warning that GEPA doesn't work with tool-calling agents (Genies tier+)
  - Detailed explanation of why (complex output formats, tool call parsing issues)
  - Alternative optimizer recommendations for each tier
  - Agent tier compatibility table

### 🚀 Enhanced
- **Ready-to-Run Commands**: All documentation now includes copy-paste commands with proper timeouts
- **Agent Discovery**: Complete tables of all available agents organized by domain and optimizer
- **Practical Examples**: Real-world goals and use cases for every agent type

## [0.1.0b16] - 2025-01-07

### 🚀 Added
- **🍎 Apple Silicon GPT-OSS Support**: MLX-LM v0.26.3 now provides native Apple Silicon support for GPT-OSS models
  - **No More Mixed Precision Issues**: MLX-LM handles MXFP4 quantization properly on Apple Silicon
  - **Native Performance**: GPT-OSS models now run natively without CPU fallback
  - **Multiple Backend Options**: Users can choose between MLX (native) and Ollama (performance)
- **🆕 GPT-OSS Model Support**: Added support for OpenAI's latest open-source models (GPT-OSS-20B and GPT-OSS-120B)
  - Apache 2.0 license for commercial use
  - Native MXFP4 quantization for efficient inference
  - Resources: [GPT-OSS-120B](https://huggingface.co/openai/gpt-oss-120b), [GPT-OSS-20B](https://huggingface.co/openai/gpt-oss-20b), [Ollama Library](https://ollama.com/library/gpt-oss)
- **MLX Model Evaluation**: Added `super model mlx evaluate` command for benchmarking MLX models using LM-Eval integration
- **MLX Model Fusion**: Added `super model mlx fuse` command for fusing finetuned adapters into base models
- **Backend-Specific Commands**: Reorganized model commands with `super model mlx`, `super model vllm`, `super model sglang` subcommands
- **Advanced MLX Features**: Support for evaluation tasks (mmlu, arc, hellaswag, etc.), fusion with dequantization, GGUF export, and HuggingFace upload
- **vLLM High-Performance Inference**: Added `super model vllm serve`, `super model vllm generate`, `super model vllm benchmark`, and `super model vllm quantize` commands for production-grade inference
- **vLLM Advanced Features**: Support for multi-GPU serving, streaming generation, performance benchmarking, and model quantization (AWQ, GPTQ, SqueezeLLM)
- **vLLM Optional Dependency**: Added vLLM as optional dependency with `pip install superoptix[vllm]` for Linux systems with NVIDIA GPUs
- **SGLang Streaming & Optimization**: Added `super model sglang serve`, `super model sglang generate`, `super model sglang optimize`, and `super model sglang benchmark` commands for streaming and optimization
- **SGLang Advanced Features**: Support for streaming generation, performance optimization (O0-O3), advanced batching, and real-time inference
- **SGLang Optional Dependency**: Added SGLang as optional dependency with `pip install superoptix[sglang]` for Linux systems with NVIDIA GPUs
- **MLX Experimental Features**: Added experimental `super model convert` and `super model quantize` commands for MLX model conversion and quantization (see `MLX_EXPERIMENTAL_FEATURES.md`)
- **Auto-installation**: Enhanced `super model run` with automatic model installation and backend detection

### 🔧 Updated
- **MLX Dependencies**: Updated to MLX-LM v0.26.3 for native GPT-OSS support on Apple Silicon
- **Model Management**: Enhanced MLX backend with better error handling and format validation
- **CLI Improvements**: Simplified UX by removing `--force` flags for cleaner commands

### 🐛 Fixed
- **Apple Silicon Compatibility**: Resolved mixed precision issues that prevented GPT-OSS models from running on Apple Silicon
- **HuggingFace Backend Limitations**: Documented that HuggingFace backend still has mixed precision issues on Apple Silicon

### 📚 Documentation
- **Apple Silicon Guide**: Updated documentation to reflect GPT-OSS support via MLX-LM and Ollama backends
- **Performance Comparison**: Added performance metrics comparing MLX-LM vs Ollama vs HuggingFace backends


## [0.1.0b11] - 2025-01-06

### 🚀 Added
- **Simplified Model Installation**: Completely redesigned model installation system for MLX and HuggingFace backends
- **Detailed Progress Display**: Added file-by-file download progress for large models with safetensors/bin files
- **Improved Model Detection**: Fixed model detection logic to properly identify installed models vs metadata-only downloads

### 🔧 Updated
- **MLX Backend**: Simplified installation using direct `snapshot_download` with single-threaded progress display
- **HuggingFace Backend**: Streamlined installation with detailed file-by-file progress for large models
- **CLI Integration**: Enhanced `super model install` command with proper model detection and progress display
- **Model Detection Logic**: Fixed detection to require actual model files (`.safetensors`, `.bin`) not just config files

### 🐛 Fixed
- **Model Installation Issues**: Resolved problems with large model downloads getting stuck at "Fetching files: 0%"
- **False Positive Detection**: Fixed issue where models with only metadata were incorrectly shown as "installed"
- **Progress Display**: Fixed missing detailed progress for individual model file downloads

### 📚 Documentation
- **Installation Guide**: Updated `SIMPLE_MODEL_INSTALLATION.md` with new simplified approach
- **Testing Scripts**: Added `test_simple_install.py` for validating model installation functionality

### 🔄 Changed
- **Installation Approach**: Removed complex validation and progress tracking in favor of simple, reliable downloads
- **Progress Display**: Switched from custom progress bars to standard HuggingFace Hub progress display
- **Error Handling**: Simplified error handling with clear, actionable error messages

### 🎯 Technical Details
- **Single-Threaded Downloads**: Uses `max_workers=1` to force detailed progress display for large models
- **Direct Download**: Uses `snapshot_download` without complex parameters for reliability
- **Proper Detection**: Checks for actual model files in snapshots directory, not just metadata

---

## [0.1.0] - 2024-12-XX

### 🎉 Initial Release

This is the first release of SuperOptiX - "The Kubernetes of Agentic AI"!

### 🚀 Added

#### 🏗️ Core Framework
- **DSPy-Native Architecture**: Built on DSPy 3.0 for self-improving agent programs
- **Agent Playbook System**: Declarative agent configuration with YAML
- **Multi-Agent Orchestration**: Sophisticated agent coordination and workflow management
- **Memory Systems**: Long-term, short-term, and episodic memory backends
- **Evaluation Framework**: Built-in testing and quality metrics for agents

#### 🛠️ CLI Tools
- `super init`: Initialize new agentic projects with full scaffolding
- `super agent create`: Generate agent templates and configurations
- `super compile`: Compile agents with DSPy optimization
- `super orchestra`: Multi-agent orchestration and deployment
- `super run`: Execute individual agents and agent workflows

#### 🎯 Agent Templates
- **Business & Consulting**: Strategy consultants, business analysts, change managers
- **Software Development**: Developers, QA engineers, DevOps, architects
- **Healthcare**: Medical assistants, health educators, mental health coaches
- **Education**: Tutors, instructors, study coaches across multiple subjects
- **Finance**: Financial advisors, budget analysts, investment researchers
- **Marketing**: Content creators, SEO specialists, campaign strategists
- **Legal**: Contract analyzers, compliance checkers, legal researchers
- **And many more!** (20+ industry categories)

#### 🧠 Memory & Context
- **Redis Backend**: Scalable memory storage for production deployments
- **Vector Memory**: Semantic memory search and retrieval
- **Context Management**: Intelligent context window optimization
- **Memory Persistence**: Long-term agent memory across sessions

#### 🔍 Observability & Debugging
- **Real-time Monitoring**: Agent performance and behavior tracking
- **Token Usage Analytics**: Cost and performance optimization
- **Debug Dashboard**: Visual debugging tools for agent development
- **Comprehensive Logging**: Detailed execution traces and metrics

#### 🧪 Testing & Quality
- **Agent BDD**: Behavior-driven development for agents
- **Automated Evaluation**: Quality metrics and regression testing
- **Performance Benchmarks**: Agent performance measurement tools
- **Safety Checks**: Built-in guardrails and safety validation

#### 🔌 Integrations
- **DSPy 3.0**: Full integration with latest DSPy features
- **MLFlow**: Experiment tracking and model management
- **FastAPI**: Production-ready API deployment
- **Streamlit**: Rapid UI development for agent interfaces

#### 📚 Documentation & Examples
- **Comprehensive Guides**: Step-by-step tutorials and documentation
- **Code Examples**: Real-world agent implementations
- **Best Practices**: Industry-standard development patterns
- **API Reference**: Complete API documentation

### 🎯 Key Features

- **🔥 Evaluation-First Development**: Every agent is testable and measurable
- **🚀 Auto-Optimization**: DSPy-powered prompt and pipeline optimization
- **🎼 Orchestration**: Kubernetes-style multi-agent coordination
- **🛡️ Production-Ready**: Enterprise-grade reliability and monitoring
- **🔧 Modular Design**: Swap components, models, and tools at runtime
- **📊 Rich Analytics**: Comprehensive performance and quality metrics

### �� Highlights

- **200+ Agent Templates**: Pre-built agents for every industry
- **DSPy 3.0 Integration**: Leverage the latest in self-improving programs
- **Enterprise Security**: Built-in security best practices and compliance
- **Cloud-Native**: Designed for modern cloud deployments
- **Developer Experience**: Intuitive CLI and comprehensive tooling

### 📦 Installation

```bash
pip install superoptix
```

### 🚀 Quick Start

```bash
# Create your first agentic system
super init my_agent_system
cd my_agent_system

# Create and run an agent
super agent create customer_service --template=support
super run customer_service "How can I help you today?"
```

### 🤝 Community

- **GitHub**: https://github.com/SuperagenticAI/superoptix
- **Documentation**: https://github.com/SuperagenticAI/superoptix/docs
- **Discussions**: https://github.com/SuperagenticAI/superoptix/discussions

---

## Release Notes Format

For each release, we document:

### 🚀 Added
New features and capabilities

### 🔄 Changed
Changes to existing functionality

### 🗑️ Deprecated
Features that will be removed in future versions

### 🐛 Fixed
Bug fixes and issue resolutions

### 🔒 Security
Security-related improvements and fixes

### ⚡ Performance
Performance improvements and optimizations

---

## Unreleased Features Preview

### 🔮 Coming Soon

#### v0.2.0 - "Agent Intelligence"
- **Advanced Reasoning**: Multi-step reasoning capabilities
- **Tool Integration**: Enhanced tool calling and API integration
- **Visual Agents**: Image and video processing capabilities
- **Agent Marketplace**: Community-driven agent sharing platform

#### v0.3.0 - "Enterprise Scale"
- **Kubernetes Deployment**: Native K8s orchestration
- **Enterprise SSO**: Advanced authentication and authorization
- **Audit Logging**: Comprehensive audit trails
- **SLA Monitoring**: Service level agreement tracking

#### v0.4.0 - "AI Evolution"
- **Self-Improving Agents**: Agents that evolve based on usage
- **Federated Learning**: Cross-agent knowledge sharing
- **Custom Models**: Support for fine-tuned and custom models
- **Agent Analytics**: Advanced analytics and insights

---

**🎯 Stay Updated**: Watch our repository and join our community to stay informed about the latest releases and features!

**🤝 Contribute**: Help us build the future of agentic AI by contributing to SuperOptiX! 
