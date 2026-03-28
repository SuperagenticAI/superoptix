# SurrealDB

This is the single SurrealDB guide for SuperOptiX.

It combines the earlier beginner demo, Docker demo, and framework guide into one page so you can find everything in one place.
It starts with the fastest way to run it, then explains the integration in a more technical way.

If you want the companion demo repository with generated pipelines, checked-in playbooks, and recorded SuperOptiX traces, see:

- https://github.com/SuperagenticAI/SurrealOptiX

For the longer architectural write-up behind this integration, see:

- https://super-agentic.ai/resources/super-posts/surrealdb-agent-memory-superoptix

## What This Guide Covers

You will learn how to:

- start SurrealDB
- seed demo data
- run standard RAG
- run GraphRAG
- run the same SurrealDB-backed behavior across multiple frameworks
- understand which SurrealDB features are already integrated in SuperOptiX
- understand where `turboagents-surrealdb` now fits into the SuperOptiX retrieval story

This guide is written in two layers:

- the first half is a practical quickstart
- the second half explains the runtime, data model, retrieval modes, memory behavior, and operational details

## Start Here

If this is your first time using SurrealDB with SuperOptiX, follow the page in this order:

1. read `Time Needed` and `Before You Start`
2. complete `Quick Start`
3. stop only when you see `Validation Status: PASSED`
4. then complete `GraphRAG Quick Start`
5. only after that, use `Framework Demo IDs` and the technical sections

If you are already comfortable with SuperOptiX and only want the internals, you can skip ahead to:

- `Technical Architecture`
- `Retrieval Modes Explained`
- `Configuration Reference`
- `Operational Notes`

If you want the framework-specific demo commands immediately, jump here:

- [SurrealDB Across Frameworks](#surrealdb-across-frameworks)

If you want the working companion project while following this guide, use:

- https://github.com/SuperagenticAI/SurrealOptiX

## SurrealDB Feature Coverage

This table lists every SurrealDB capability currently integrated in SuperOptiX.

| Feature Tag | Feature Name | Status | Where To Run It |
|---|---|---|---|
| `surrealdb-vector-rag` | Vector retrieval | Supported | `rag_surrealdb_*_demo` |
| `surrealdb-hybrid-rag` | Hybrid retrieval (vector + lexical) | Supported | any `rag_surrealdb_*_demo` with `retrieval_mode: hybrid` |
| `surrealdb-graphrag` | GraphRAG (vector + RELATE traversal) | Supported | `graphrag_surrealdb_*_demo` |
| `surrealdb-multi-rag` | Multi mode (hybrid + graph expansion) | Supported | custom playbook with `retrieval_mode: multi` |
| `surrealdb-temporal-memory` | Temporal memory (`history`, `retrieve_at`) | Supported | `temporal_memory_surrealdb_demo` |
| `surrealdb-server-embeddings` | Server-side embeddings (`fn::embed`) with fallback | Supported | any SurrealDB RAG playbook with `embedding_mode: server` |
| `surrealdb-live-memory` | Live memory stream utility (`LIVE SELECT`) | Supported utility | `superoptix.memory.LiveMemorySubscriber` |
| `surrealdb-mcp-readonly` | Read-only SurrealDB MCP tool (`surrealdb_query`) | Supported | built-in tool config |
| `surrealdb-capability-gating` | Runtime capability detection + graceful fallback | Supported | automatic at runtime |
| `turboagents-surrealdb-rag` | TurboAgents-backed SurrealDB compressed retrieval | Supported | `rag_surrealdb_demo` with `retriever_type: turboagents-surrealdb` |

## TurboAgents-SurrealDB Path

The standard SuperOptiX SurrealDB integration is still available, but the main standard RAG demos now use the `turboagents-surrealdb` retriever path.

That means:

- SuperOptiX still uses the normal RAG configuration surface
- SurrealDB remains the storage and candidate-search backend
- TurboAgents provides compressed retrieval and reranking under the same agent flow

This is the current recommended path if you want to evaluate TurboAgents inside SuperOptiX without leaving the standard playbook model.

## Validation Matrix

Current local framework validation for `turboagents-surrealdb` is:

| Framework | Status | Validation |
| --- | --- | --- |
| OpenAI Agents | Passed | `rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"` returned the seeded token explanation |
| Pydantic AI | Passed | `rag_surrealdb_pydanticai_demo --framework pydantic-ai --goal "What is NEON-FOX-742?"` returned the seeded token explanation |
| DSPy | Blocked | Local LiteLLM and Ollama path still fails on `qwen3.5:9b` with `invalid model name`; retrieval is not the blocker |

Seed helper details:

- `superoptix.agents.demo.setup_surrealdb_seed` now understands `turboagents-surrealdb` directly
- the helper writes TurboAgents-compatible SurrealDB payloads
- sentence-transformer embeddings are trimmed or padded to the configured TurboAgents dimension during seeding so seeded data matches runtime behavior

Recommended local validation flow:

```bash
uv run python superoptix/agents/demo/setup_surrealdb_seed.py
super agent run rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"
super agent run rag_surrealdb_pydanticai_demo --framework pydantic-ai --goal "What is NEON-FOX-742?"
```

## Technical Architecture

SurrealDB is integrated at the shared runtime layer, not as one-off framework-specific code.

That matters because the same SurrealDB behavior is reused across DSPy, OpenAI SDK, Claude SDK, Microsoft, PydanticAI, CrewAI, Google ADK, and DeepAgents.

The runtime is split into these pieces:

| Layer | Responsibility | Technical role |
|---|---|---|
| RAG runtime | Retrieval during agent execution | parses SurrealDB config, generates query embeddings, runs vector, hybrid, graph, or multi retrieval |
| GEPA SurrealDB vector store | Optimizer-side retrieval adapter | exposes SurrealDB search to the GEPA RAG adapter |
| SurrealDB memory backend | Persistent agent memory | stores key-value memory and optional temporal history |
| Live memory subscriber | Real-time memory updates | uses `LIVE SELECT` over WebSocket |
| MCP read-only tool | Safe query access for agents | exposes `surrealdb_query` with statement allowlist and row limits |
| Feature detector | Version and capability probing | checks whether server features such as `RELATE` or `fn::embed` are actually available |

In practice, the integration flow looks like this:

1. a standard RAG playbook selects `retriever_type: turboagents-surrealdb`
2. SuperOptiX compiles the same playbook into the target framework
3. at runtime, the shared RAG layer talks to SurrealDB
4. framework adapters receive the same retrieved context regardless of framework
5. optional memory and MCP features can point at the same SurrealDB deployment

## Data Model And Indexing

The default RAG table is:

- `rag_documents`

Each RAG record follows this logical structure:

```json
{
  "content": "document text",
  "embedding": [0.123, -0.456, 0.789],
  "metadata": {
    "seed_id": "seed-001",
    "source": "superoptix_surreal_seed_v1",
    "topic": "retrieval"
  }
}
```

For GraphRAG seeds, SuperOptiX uses deterministic record IDs so graph traversal is stable:

- `rag_documents:superoptix`
- `rag_documents:surrealdb`
- `rag_documents:vector_search`

Those graph-oriented rows still live in `rag_documents`, but they also have:

- `metadata.entity_id`
- typed relations created with `RELATE`

The seeding utility attempts to create these indexes:

- HNSW index on the vector field for kNN search
- BM25 full-text index on the content field for hybrid retrieval
- index on `metadata.entity_id` for graph-oriented records

On older SurrealDB versions, index creation may be skipped with a warning. The demos still work, but query performance and lexical ranking quality may be lower.

## Retrieval Modes Explained

SuperOptiX currently supports four SurrealDB retrieval modes.

| Mode | What happens | Best use case |
|---|---|---|
| `vector` | semantic similarity over the embedding field | standard RAG |
| `hybrid` | weighted blend of vector similarity and lexical score | user questions where exact terms matter |
| `graph` | vector seed search first, then graph expansion through `RELATE` edges | entity and capability discovery |
| `multi` | hybrid retrieval first, then graph expansion | mixed semantic, lexical, and relationship-heavy retrieval |

Technical behavior:

- `graph_depth` is clamped to `1..3`
- `graph_relations` must be a list of lowercase relation names
- `hybrid_alpha` is clamped to `0.0..1.0`
- `embedding_mode` is either `client` or `server`

Operationally, each mode works like this:

### `vector`

SuperOptiX generates a query embedding and ranks records by cosine similarity against `embedding`.

### `hybrid`

SuperOptiX combines:

- vector similarity from the embedding field
- lexical relevance from the full-text index on `content`

`hybrid_alpha` controls the balance:

- `1.0` means strongly semantic
- `0.0` means strongly lexical
- `0.7` is the current practical default for the demos

### `graph`

Graph mode is a two-step retrieval process:

1. run vector retrieval to find the best seed records
2. follow `RELATE` edges from those seed record IDs using the configured relation names and depth

This is why GraphRAG only works fully when:

- graph seed data was created with `--graph`
- the SurrealDB server supports the required graph traversal behavior

### `multi`

Multi mode starts with hybrid retrieval, then expands the result set through graph traversal. It is the broadest retrieval mode and is useful when the question mixes keywords, semantics, and relationships.

## Capability Gating And Fallbacks

SuperOptiX does not assume every SurrealDB server supports every newer feature.

At runtime it probes the connected server and adjusts behavior safely.

Current probes cover:

- graph traversal parser support for `RELATE`-style traversal
- vector similarity support
- full-text helper support
- `fn::embed` availability for server-side embeddings
- `LIVE SELECT` support based on connection type

Important fallback rules:

- if graph support is missing, `graph` mode falls back to `vector`
- if graph support is missing in `multi`, the graph expansion part is skipped
- if `fn::embed` is unavailable, `embedding_mode: server` falls back to client-side embeddings
- live subscriptions require `ws://` or `wss://`; embedded URLs are rejected clearly

## Time Needed

- First run: about 10-20 minutes
- Later runs: 2-5 minutes

## Before You Start

You need:

- Python environment with `superoptix`
- Docker installed
- terminal access
- optional for cloud models: API keys for Gemini, Anthropic, or OpenAI

## Terminal Layout

Using separate terminals makes this much easier to follow.

Use this exact layout:

- Terminal A: Ollama server
- Terminal B: SurrealDB server
- Terminal C: seed commands, pull, compile, and run commands

Do not close Terminal A or Terminal B while you are testing.

## Success Checklist

- [ ] `pip install "superoptix[surrealdb]"` completed
- [ ] `ollama pull qwen3.5:9b` completed
- [ ] `ollama serve` is running
- [ ] SurrealDB Docker process is running on port `8000`
- [ ] seed command prints `SurrealDB seed complete`
- [ ] `super init memory-demo` completed
- [ ] you are inside the `memory-demo` directory
- [ ] RAG run returns `NEON-FOX-742`
- [ ] run ends with `Validation Status: PASSED`
- [ ] graph seed prints `Edges created:` greater than `0`
- [ ] GraphRAG run answers from connected graph data without fallback

## Quick Start

This is the fastest path to a successful first run.

Goal of this section:

- prove that SuperOptiX can retrieve from SurrealDB
- verify the seeded token `NEON-FOX-742` is coming from retrieval, not guesswork

If you want the framework tabs after your first successful run, jump here:

- [SurrealDB Across Frameworks](#surrealdb-across-frameworks)

### 1) Install

Run this in Terminal C:

With `uv`:

```bash
uv pip install "superoptix[turboagents]"
ollama pull qwen3.5:9b
```

Or with `pip`:

```bash
pip install "superoptix[turboagents]"
ollama pull qwen3.5:9b
```

If you want the older native-only SurrealDB path, `superoptix[surrealdb]` still
works. The TurboAgents integration path uses the new extra because it pulls in
`turboagents[rag]` as well.

What this does:

- installs SuperOptiX with SurrealDB support
- downloads the local Ollama model used by the local DSPy path

Do not move on until both commands finish.

### 2) Start services

Start the model server first.

Terminal A:

```bash
ollama serve
```

Leave this terminal open.

Then start SurrealDB.

Terminal B:

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Leave this terminal open too.

What this does:

- starts a SurrealDB server
- exposes it on `ws://localhost:8000`
- uses username `root` and password `secret`

If Docker says port `8000` is already in use, jump to `Docker And Connection Notes` and use the alternate port example there.

### 3) Seed demo data

Go back to Terminal C.

Terminal C:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
```

This command:

- reads the packaged seed dataset
- generates embeddings
- writes rows into `rag_documents`

Exact output to look for:

- `SurrealDB seed complete`
- `Inserted: 8`

Behavior to verify:

- the command exits without an exception
- the seed completes against the SurrealDB instance you started in Terminal B

Do not continue if you do not see the exact output lines above.

### 4) Create a SuperOptiX project

Before pulling any agent, create a SuperOptiX project directory.

Still in Terminal C, run:

```bash
super init memory-demo
cd memory-demo
```

What this does:

- creates a valid SuperOptiX project
- gives the CLI a working directory for pulled agents, compiled pipelines, and runtime files

Behavior to verify:

- the `memory-demo` directory exists
- you are now running commands from inside `memory-demo`

### 5) Pull, compile, and run RAG

Still in Terminal C, run these exactly in order:

```bash
super agent pull rag_surrealdb_openai_demo
super agent compile rag_surrealdb_openai_demo --framework openai
super agent run rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"
```

What each command does:

- `pull` downloads the demo agent definition into your workspace
- `compile` generates the framework-specific runnable pipeline
- `run` executes the agent with SurrealDB retrieval enabled

Exact output to look for:

- `RAG retrieval enabled`
- `Validation Status: PASSED`

Behavior to verify:

- output mentions `NEON-FOX-742`

If the run completes but the answer does not mention `NEON-FOX-742`, treat that as a failed retrieval test and fix the seed or connection before moving on.

At this point the basic SurrealDB RAG path is working.

## GraphRAG Quick Start

Goal of this section:

- prove the agent can retrieve not only by similarity, but also by graph relations created with `RELATE`

### 1) Seed graph data

In Terminal C, run:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

This command:

- loads the graph seed dataset
- creates deterministic graph-oriented records
- attempts to create indexes
- creates `RELATE` edges when supported by the server

Exact output to look for:

- `GraphRAG seeding:`
- `Nodes created:`
- `Edges created:`

Important:

- `Edges created:` should be greater than `0` for real graph traversal support.
- `--graph` replaces previous rows from the same graph seed source.
- If you want graph docs and the normal token docs together, run this afterwards:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --append
```

### 2) Pull, compile, and run GraphRAG

Still in Terminal C, run:

```bash
super agent pull graphrag_surrealdb_openai_demo
super agent compile graphrag_surrealdb_openai_demo --framework openai
super agent run graphrag_surrealdb_openai_demo --framework openai --goal "What capabilities does SurrealDB provide?"
```

Behavior to verify:

- no fallback warning about `RELATE`
- answer includes SurrealDB capabilities from graph-connected docs

If you see a message saying GraphRAG is falling back to vector mode, stop here and fix the graph seeding first. Do not assume graph retrieval is active just because the run returned an answer.

## Run With Gemini

Use this path if you want a cloud model instead of the local Ollama model.

Set your API key:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Run standard RAG:

```bash
super agent run rag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
```

Run GraphRAG:

```bash
super agent run graphrag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
```

## Docker And Connection Notes

SuperOptiX demos use authenticated SurrealDB server mode in Docker.

Default Docker command:

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Default connection settings:

```yaml
vector_store:
  url: ws://localhost:8000
  namespace: superoptix
  database: knowledge
  username: root
  password: secret
  skip_signin: false
  table_name: rag_documents
  vector_field: embedding
  content_field: content
  metadata_field: metadata
```

If port `8000` is already used, map another port:

```bash
docker run --rm -p 18000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Then use:

- `ws://localhost:18000`

Important URL rule:

- use the base WebSocket URL only
- do not add `/rpc`

## Framework Demo IDs

Use these IDs with `pull`, `compile`, and `run`.

| Framework | RAG demo id | GraphRAG demo id |
|---|---|---|
| DSPy | `rag_surrealdb_dspy_demo` | `graphrag_surrealdb_dspy_demo` |
| OpenAI | `rag_surrealdb_openai_demo` | `graphrag_surrealdb_openai_demo` |
| Claude SDK | `rag_surrealdb_claude_sdk_demo` | `graphrag_surrealdb_claude_sdk_demo` |
| Microsoft | `rag_surrealdb_microsoft_demo` | `graphrag_surrealdb_microsoft_demo` |
| PydanticAI | `rag_surrealdb_pydanticai_demo` | `graphrag_surrealdb_pydanticai_demo` |
| CrewAI | `rag_surrealdb_crewai_demo` | `graphrag_surrealdb_crewai_demo` |
| Google ADK | `rag_surrealdb_adk_demo` | `graphrag_surrealdb_adk_demo` |
| DeepAgents | `rag_surrealdb_deepagents_demo` | `graphrag_surrealdb_deepagents_demo` |

## Install Framework Extras

Install only the framework you want to test:

```bash
pip install -U "superoptix[frameworks-dspy]"
pip install -U "superoptix[frameworks-openai]"
pip install -U "superoptix[frameworks-claude-sdk]"
pip install -U "superoptix[frameworks-microsoft]"
pip install -U "superoptix[frameworks-pydantic-ai]"
pip install -U "superoptix[frameworks-google]"
pip install -U "superoptix[frameworks-deepagents]"
```

Install most supported frameworks at once:

```bash
pip install -U "superoptix[frameworks]"
```

If you install SuperOptiX with `uv tool`, use:

```bash
uv tool install superoptix --with "superoptix[frameworks-dspy]"
uv tool install superoptix --with "superoptix[frameworks-openai]"
uv tool install superoptix --with "superoptix[frameworks-claude-sdk]"
uv tool install superoptix --with "superoptix[frameworks-microsoft]"
uv tool install superoptix --with "superoptix[frameworks-pydantic-ai]"
uv tool install superoptix --with "superoptix[frameworks-google]"
uv tool install superoptix --with "superoptix[frameworks-deepagents]"
```

Notes:

- use `frameworks-google`, not `framework-google`
- use `frameworks-pydantic-ai`, not `frameworks-pydanticai`
- `frameworks-microsoft` should install a compatible prerelease Microsoft SDK build; if `ChatAgent` import errors still appear, run `pip install -U --pre agent-framework azure-identity` and then recompile the Microsoft pipeline.
- CrewAI is not bundled in `frameworks` because of dependency conflicts with DSPy

## SurrealDB Across Frameworks

This section demonstrates the same SurrealDB backend across every supported framework.

The companion repository for these generated framework demos and trace files is:

- https://github.com/SuperagenticAI/SurrealOptiX

Use the same shared setup for all tabs:

- start Ollama in Terminal A if you want local runs
- start SurrealDB in Terminal B
- run the standard seed command once
- run the graph seed command once before GraphRAG tests

Shared setup commands:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

Use the same two questions everywhere:

- basic RAG question: `What is NEON-FOX-742?`
- GraphRAG question: `What capabilities does SurrealDB provide?`

What should stay the same across frameworks:

- the same SurrealDB backend
- the same seed data
- the same retrieval behavior
- the same validation expectation

For the framework demos below, the runtime examples use Google Gemini via:

- `--cloud --provider google-genai --model gemini-2.5-flash`

Gemini prerequisite:

```bash
export GOOGLE_API_KEY="your-google-api-key"
# or: export GEMINI_API_KEY="your-google-api-key"
```

Important retrieval note:

- if a framework run completes successfully but answers with "the provided context does not contain information about `NEON-FOX-742`", the framework is working but retrieval is not grounded in the seeded demo data yet
- in that case, re-run `python -m superoptix.agents.demo.setup_surrealdb_seed`
- then verify the agent is querying the expected SurrealDB settings: `ws://localhost:8000`, namespace `superoptix`, database `knowledge`, table `rag_documents`

=== "🔬 DSPy"
    Install:

    ```bash
    pip install -U "superoptix[frameworks-dspy]"
    ```

    Current local status:

    - the DSPy SurrealDB path is implemented but not part of the current passing local validation matrix
    - the known blocker is the local LiteLLM and Ollama path for `qwen3.5:9b`, which currently fails with `invalid model name`
    - use the OpenAI Agents or Pydantic AI tabs below for the currently validated local route

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_dspy_demo
    super agent compile rag_surrealdb_dspy_demo --framework dspy
    super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_dspy_demo
    super agent compile graphrag_surrealdb_dspy_demo --framework dspy
    super agent run graphrag_surrealdb_dspy_demo --framework dspy --goal "What capabilities does SurrealDB provide?"
    ```

=== "🤖 OpenAI"
    Note:

    - install with `pip install -U "superoptix[frameworks-openai]"`
    - for the OpenAI Agents SDK demo, recompile with the Gemini cloud flags before running
    - if the run log still shows `model=litellm/ollama/qwen3.5:9b`, the pipeline is still using an older Ollama-compiled spec

    Install:

    ```bash
    pip install -U "superoptix[frameworks-openai]"
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_openai_demo
    super agent compile rag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash
    super agent run rag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_openai_demo
    super agent compile graphrag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash
    super agent run graphrag_surrealdb_openai_demo --framework openai --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer includes SurrealDB capabilities from related records
    - both runs complete successfully

=== "🧠 Claude SDK"
    Install:

    ```bash
    pip install -U "superoptix[frameworks-claude-sdk]"
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_claude_sdk_demo
    super agent compile rag_surrealdb_claude_sdk_demo --framework claude-sdk
    super agent run rag_surrealdb_claude_sdk_demo --framework claude-sdk --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_claude_sdk_demo
    super agent compile graphrag_surrealdb_claude_sdk_demo --framework claude-sdk
    super agent run graphrag_surrealdb_claude_sdk_demo --framework claude-sdk --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer reflects graph-connected SurrealDB capabilities
    - both runs complete successfully

=== "🏢 Microsoft"
    Note:

    - `pip install -U --force-reinstall "superoptix[frameworks-microsoft]"` is the safest upgrade path for Microsoft demos
    - if the run still fails with `cannot import name 'ChatAgent' from 'agent_framework'`, your generated pipeline is still using the older Microsoft SDK API or your env still has an older `agent-framework` build
    - when using Gemini here, set `GOOGLE_API_KEY` or `GEMINI_API_KEY`; do not set only `OPENAI_API_KEY`
    - if the run fails with `Agent.__init__() missing 1 required positional argument: 'client'`, your generated Microsoft pipeline is stale from an older SuperOptiX release
    - fix the env with `pip install -U --pre agent-framework azure-identity`
    - then delete the generated Microsoft pipeline files and recompile before rerunning

    Install:

    ```bash
    pip install -U --force-reinstall "superoptix[frameworks-microsoft]"
    ```

    Basic RAG:

    ```bash
    export GOOGLE_API_KEY="your-google-api-key"
    # or: export GEMINI_API_KEY="your-google-api-key"

    rm -f surrealoptix/agents/rag_surrealdb_microsoft_demo/pipelines/rag_surrealdb_microsoft_demo_microsoft_pipeline.py
    rm -f surrealoptix/agents/rag_surrealdb_microsoft_demo/pipelines/rag_surrealdb_microsoft_demo_microsoft_pipeline_compiled_spec.json

    super agent pull rag_surrealdb_microsoft_demo
    super agent compile rag_surrealdb_microsoft_demo --framework microsoft --cloud --provider google-genai --model gemini-2.5-flash
    super agent run rag_surrealdb_microsoft_demo --framework microsoft --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    export GOOGLE_API_KEY="your-google-api-key"
    # or: export GEMINI_API_KEY="your-google-api-key"

    rm -f surrealoptix/agents/graphrag_surrealdb_microsoft_demo/pipelines/graphrag_surrealdb_microsoft_demo_microsoft_pipeline.py
    rm -f surrealoptix/agents/graphrag_surrealdb_microsoft_demo/pipelines/graphrag_surrealdb_microsoft_demo_microsoft_pipeline_compiled_spec.json

    super agent pull graphrag_surrealdb_microsoft_demo
    super agent compile graphrag_surrealdb_microsoft_demo --framework microsoft --cloud --provider google-genai --model gemini-2.5-flash
    super agent run graphrag_surrealdb_microsoft_demo --framework microsoft --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer uses the same SurrealDB graph data
    - both runs complete successfully

=== "🐍 PydanticAI"
    Note:

    - install with `pip install -U "superoptix[frameworks-pydantic-ai]"`
    - if your installed `superoptix` incorrectly asks for `PYDANTIC_AI_GATEWAY_API_KEY` while using Gemini, force direct mode for now:

    ```bash
    super agent run graphrag_surrealdb_pydanticai_demo --framework pydantic-ai --cloud --direct --provider google-genai --model gemini-2.5-flash --gateway-key-env "" --goal "What capabilities does SurrealDB provide?"
    ```

    - direct Gemini mode should use `GOOGLE_API_KEY` or `GEMINI_API_KEY`, not `PYDANTIC_AI_GATEWAY_API_KEY`

    Install:

    ```bash
    pip install -U "superoptix[frameworks-pydantic-ai]"
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_pydanticai_demo
    super agent compile rag_surrealdb_pydanticai_demo --framework pydantic-ai
    super agent run rag_surrealdb_pydanticai_demo --framework pydantic-ai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_pydanticai_demo
    super agent compile graphrag_surrealdb_pydanticai_demo --framework pydantic-ai
    super agent run graphrag_surrealdb_pydanticai_demo --framework pydantic-ai --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer reflects graph-expanded retrieval
    - both runs complete successfully

=== "👥 CrewAI"
    Note:

    - CrewAI is not bundled in `superoptix[frameworks]` because it conflicts with DSPy in the same environment
    - install CrewAI in a separate environment if you also need DSPy

    Install:

    ```bash
    pip install -U superoptix
    pip install -U crewai==1.2.0
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_crewai_demo
    super agent compile rag_surrealdb_crewai_demo --framework crewai
    super agent run rag_surrealdb_crewai_demo --framework crewai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_crewai_demo
    super agent compile graphrag_surrealdb_crewai_demo --framework crewai
    super agent run graphrag_surrealdb_crewai_demo --framework crewai --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer reflects the seeded SurrealDB graph
    - both runs complete successfully

=== "🔮 Google ADK"
    Install:

    ```bash
    pip install -U "superoptix[frameworks-google]"
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_adk_demo
    super agent compile rag_surrealdb_adk_demo --framework google-adk
    super agent run rag_surrealdb_adk_demo --framework google-adk --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_adk_demo
    super agent compile graphrag_surrealdb_adk_demo --framework google-adk
    super agent run graphrag_surrealdb_adk_demo --framework google-adk --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer reflects graph-connected SurrealDB capabilities
    - both runs complete successfully

=== "🌊 DeepAgents"
    Install:

    ```bash
    pip install -U "superoptix[frameworks-deepagents]"
    ```

    Basic RAG:

    ```bash
    super agent pull rag_surrealdb_deepagents_demo
    super agent compile rag_surrealdb_deepagents_demo --framework deepagents
    super agent run rag_surrealdb_deepagents_demo --framework deepagents --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
    ```

    GraphRAG:

    ```bash
    super agent pull graphrag_surrealdb_deepagents_demo
    super agent compile graphrag_surrealdb_deepagents_demo --framework deepagents
    super agent run graphrag_surrealdb_deepagents_demo --framework deepagents --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
    ```

    Verify:

    - basic RAG answer mentions `NEON-FOX-742`
    - GraphRAG answer reflects graph-expanded retrieval
    - both runs complete successfully

## One Command Pattern For Any Framework

1. Pull:

```bash
super agent pull <demo_id>
```

2. Compile:

```bash
super agent compile <demo_id> --framework <framework_name>
```

3. Run:

```bash
super agent run <demo_id> --framework <framework_name> --cloud --provider google-genai --model gemini-2.5-flash --goal "your question"
```

## How To Run Each Feature

### Feature: Vector RAG (`surrealdb-vector-rag`)

```bash
super agent pull rag_surrealdb_openai_demo
super agent compile rag_surrealdb_openai_demo --framework openai
super agent run rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"
```

### Feature: Hybrid RAG (`surrealdb-hybrid-rag`)

Use any `rag_surrealdb_*_demo` playbook and set:

```yaml
rag:
  config:
    retrieval_mode: hybrid
    hybrid_alpha: 0.7
```

Then compile and run as normal.

### Feature: GraphRAG (`surrealdb-graphrag`)

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
super agent pull graphrag_surrealdb_openai_demo
super agent compile graphrag_surrealdb_openai_demo --framework openai
super agent run graphrag_surrealdb_openai_demo --framework openai --goal "What capabilities does SurrealDB provide?"
```

### Feature: Multi Retrieval (`surrealdb-multi-rag`)

Use a playbook with:

```yaml
rag:
  config:
    retrieval_mode: multi
    graph_depth: 2
    graph_relations:
      - integrates_with
      - provides
      - supports
      - enables
```

### Feature: Temporal Memory (`surrealdb-temporal-memory`)

```bash
super agent pull temporal_memory_surrealdb_demo
super agent compile temporal_memory_surrealdb_demo --framework openai
super agent run temporal_memory_surrealdb_demo --framework openai --goal "Remember that I prefer dark mode."
```

### Feature: Server-side Embeddings (`surrealdb-server-embeddings`)

Enable in playbook:

```yaml
rag:
  config:
    embedding_mode: server
```

Behavior:

- if `fn::embed` is available in SurrealDB, server embeddings are used
- if unavailable, SuperOptiX falls back to client embeddings automatically

### Feature: Live Memory Utility (`surrealdb-live-memory`)

Python usage:

```python
from superoptix.memory import LiveMemorySubscriber

# Requires SurrealDB backend using ws:// or wss://
# subscribe(table, callback) gives real-time memory updates
```

This is a standalone utility and is not auto-wired into every runtime path.

### Feature: Read-only MCP Tool (`surrealdb-mcp-readonly`)

Use built-in tool config:

```yaml
tools:
  built_in_tools:
    - name: surrealdb_query
      config:
        url: ws://localhost:8000
        namespace: superoptix
        database: knowledge
        username: root
        password: secret
```

Safety controls:

- read-only statement allowlist: `SELECT`, `INFO`, `RETURN`
- row limit injection when missing
- query timeout protection

### Feature: Capability Gating (`surrealdb-capability-gating`)

SuperOptiX probes SurrealDB features at runtime and degrades safely when needed.

Examples:

- graph mode falls back to vector or hybrid when `RELATE` is unavailable
- server embedding mode falls back to client embedding when `fn::embed` is unavailable

## Configuration Reference

This is the smallest SurrealDB RAG configuration that works:

```yaml
rag:
  enabled: true
  retriever_type: turboagents-surrealdb
  config:
    top_k: 5
    retrieval_mode: vector
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
    url: ws://localhost:8000
    namespace: superoptix
    database: knowledge
    username: root
    password: secret
    skip_signin: false
    table_name: rag_documents
    vector_field: embedding
    content_field: content
    metadata_field: metadata
```

### RAG Runtime Options

| Key | Type | Meaning | Notes |
|---|---|---|---|
| `rag.enabled` | bool | enables retrieval | must be `true` |
| `rag.retriever_type` | string | selects backend | use `turboagents-surrealdb` |
| `rag.config.top_k` | int | max retrieved rows | typical demo value is `5` |
| `rag.config.retrieval_mode` | string | retrieval strategy | `vector`, `hybrid`, `graph`, `multi` |
| `rag.config.hybrid_alpha` | float | semantic vs lexical weight | valid range `0.0..1.0` |
| `rag.config.graph_depth` | int | graph traversal depth | clamped to `1..3` |
| `rag.config.graph_relations` | list[str] | allowed relation names to follow | lowercase relation names such as `integrates_with` |
| `rag.config.embedding_mode` | string | where query embeddings are computed | `client` or `server` |

### Vector Store Options

| Key | Type | Meaning | Notes |
|---|---|---|---|
| `url` | string | SurrealDB connection URL | `ws://localhost:8000` for server mode |
| `namespace` | string | SurrealDB namespace | demo default is `superoptix` |
| `database` | string | SurrealDB database | demo default is `knowledge` |
| `username` | string | SurrealDB username | ignored when `skip_signin: true` |
| `password` | string | SurrealDB password | ignored when `skip_signin: true` |
| `skip_signin` | bool | skips explicit signin | useful for embedded transports like `memory://` or `surrealkv://` |
| `table_name` | string | document table | demo default is `rag_documents` |
| `vector_field` | string | embedding field | demo default is `embedding` |
| `content_field` | string | text field used in prompts and lexical search | demo default is `content` |
| `metadata_field` | string | metadata field | demo default is `metadata` |
| `embedding_model` | string | client-side embedding model | demo default is `sentence-transformers/all-MiniLM-L6-v2` |

### Memory Options For SurrealDBBackend

If you want agent memory in SurrealDB as well as RAG, the memory backend can point to the same server.

```yaml
memory:
  enabled: true
  backend:
    type: surrealdb
    config:
      url: ws://localhost:8000
      namespace: superoptix
      database: agents
      username: root
      password: secret
      table_name: superoptix_memory
  temporal:
    enabled: true
    max_versions_per_key: 50
```

Memory-specific notes:

- the primary table stores the latest value for each key
- temporal history is appended to a companion table named `<table_name>_versions`
- `retrieve()` keeps latest-value semantics
- `history()` and `retrieve_at()` read from the versions table when temporal mode is enabled

### MCP Tool Configuration

The `surrealdb_query` built-in tool is intended for read-only querying.

```yaml
tools:
  built_in_tools:
    - name: surrealdb_query
      config:
        url: ws://localhost:8000
        namespace: superoptix
        database: knowledge
        username: root
        password: secret
```

Runtime protection built into the tool:

- only `SELECT`, `INFO`, and `RETURN` statements are allowed
- a row limit is injected when the query does not specify one
- the call is time-bounded to avoid hanging queries

## Full Technical Example

This example shows one SurrealDB deployment backing:

- RAG
- GraphRAG
- temporal memory
- the read-only MCP tool

```yaml
spec:
  target_framework: dspy

  language_model:
    location: cloud
    provider: google-genai
    model: gemini-2.5-flash

  memory:
    enabled: true
    backend:
      type: surrealdb
      config:
        url: ws://localhost:8000
        namespace: superoptix
        database: agents
        username: root
        password: secret
        table_name: superoptix_memory
    temporal:
      enabled: true
      max_versions_per_key: 50

  rag:
    enabled: true
    retriever_type: turboagents-surrealdb
    config:
      top_k: 5
      retrieval_mode: multi
      hybrid_alpha: 0.7
      graph_depth: 2
      graph_relations:
        - integrates_with
        - provides
        - supports
        - enables
      embedding_mode: client
    vector_store:
      url: ws://localhost:8000
      namespace: superoptix
      database: knowledge
      username: root
      password: secret
      skip_signin: false
      table_name: rag_documents
      vector_field: embedding
      content_field: content
      metadata_field: metadata
      embedding_model: sentence-transformers/all-MiniLM-L6-v2

  tools:
    built_in_tools:
      - name: surrealdb_query
        config:
          url: ws://localhost:8000
          namespace: superoptix
          database: knowledge
          username: root
          password: secret
```

## Operational Notes

### Connection Modes

SurrealDB can be used in more than one way inside SuperOptiX:

| Mode | Typical URL | Best use |
|---|---|---|
| local server | `ws://localhost:8000` | demos, Docker, live queries |
| remote server | `wss://...` | shared or hosted deployments |
| embedded memory | `memory` or `memory://` | quick local experiments |
| local file store | `surrealkv://./path/to/file` | local persistent development runs |

General guidance:

- use `ws://` or `wss://` when you need live subscriptions
- use embedded transports for simple local experiments
- `skip_signin` is usually `true` for embedded modes and `false` for server modes

### Seeding Behavior

The seeding script does more than just insert rows.

Standard seed mode:

- loads JSONL documents
- generates embeddings with the configured sentence-transformer model
- inserts rows into `rag_documents`
- optionally deletes previous rows from the same seed source first

Graph seed mode:

- validates relationship targets before writing anything
- creates deterministic entity record IDs
- attempts to define indexes
- creates `RELATE` edges when the server supports them

### Indexing Strategy

For serious usage, the SurrealDB table should have:

- a vector index for embedding search
- a lexical index for hybrid retrieval
- stable identifiers for graph-oriented records

The demo seeder attempts to create these automatically, but production deployments should define and verify them explicitly as part of environment setup.

### Performance Expectations

Practical trade-offs by mode:

- `vector` is the cheapest and simplest
- `hybrid` is usually a better default when exact tokens matter
- `graph` is more expressive but depends on good relations and graph-capable server support
- `multi` is the broadest mode and may retrieve the richest context, but it is also the most expensive

### Framework Behavior

SuperOptiX does not implement separate SurrealDB logic per framework.

Instead:

- framework adapters compile agent code
- the shared runtime handles SurrealDB retrieval and memory
- that means behavior stays aligned across frameworks
- demo playbooks differ mostly in framework syntax, not SurrealDB semantics

## Most Common Problems And Fixes

### Problem: `Connection refused`

Meaning: SurrealDB is not running.

Fix:

```bash
docker ps --filter name=surrealdb-demo
```

If nothing is listed, start SurrealDB again.

### Problem: `did not receive a valid HTTP response`

Meaning: wrong SurrealDB URL.

Fix:

- use `ws://localhost:8000`
- do not use `/rpc` in the URL

### Problem: Graph warning `falling back from 'graph' to 'vector' mode`

Meaning: graph edges were not available or the running SurrealDB server does not support the required graph behavior.

Fix:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

Then confirm `Edges created:` is greater than `0`.

### Problem: `model is required` with Ollama

Meaning: wrong model string was passed.

Fix:

```bash
super agent run rag_surrealdb_dspy_demo --framework dspy --local --provider ollama --model qwen3.5:9b --goal "What is NEON-FOX-742?"
```

### Problem: Gemini says `API_KEY_INVALID` or `API Key not found`

Meaning: the key is missing or invalid.

Fix:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Then run again.

### Problem: Auth error

Meaning: Docker credentials and playbook credentials do not match.

Fix:

- make sure Docker uses `--user root --pass secret`
- make sure the playbook uses the same username and password

### Problem: `embeddings.position_ids | UNEXPECTED`

Meaning: model loading report. Usually informational only.

If the run still completes, ignore it.

## Quick Verification

### Verify basic RAG

Exact output to look for:

- `Validation Status: ✅ PASSED`

Behavior to verify:

- the answer contains `NEON-FOX-742`

### Verify GraphRAG really works

Run:

```bash
python - <<'PY'
from surrealdb import Surreal

with Surreal("ws://localhost:8000") as db:
    db.signin({"username": "root", "password": "secret"})
    db.use("superoptix", "knowledge")
    print(db.query("SELECT count() AS c FROM integrates_with WHERE source='superoptix_seed';"))
    print(db.query("SELECT content FROM rag_documents:superoptix->integrates_with->rag_documents;"))
PY
```

Behavior to verify:

- the count is non-zero
- the traversal query returns rows

If both conditions are true, GraphRAG data is active.

## Related

- [RAG Guide](../../guides/rag.md)
- [Memory Guide](../../guides/memory.md)
