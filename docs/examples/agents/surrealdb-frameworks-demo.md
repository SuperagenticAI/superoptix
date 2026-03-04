# SurrealDB + SuperOptiX Framework Guide

This guide is written for beginners.

If you can copy and paste terminal commands, you can run this.

## What You Will Do

You will run an AI agent that:

- stores knowledge in SurrealDB
- retrieves that knowledge during a question
- works in multiple frameworks (DSPy, OpenAI SDK, Claude SDK, Microsoft, PydanticAI, CrewAI, Google ADK, DeepAgents)

## SurrealDB Feature Coverage (Tagged)

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

## Time Needed

- First run: about 10-20 minutes
- Later runs: 2-5 minutes

## Before You Start

You need:

- Python environment with `superoptix`
- Docker installed
- Terminal access
- Optional for cloud models: API keys (Gemini/Anthropic/OpenAI)

## Step 1: Install Dependencies

Run:

```bash
pip install "superoptix[surrealdb]"
```

If you want local model runs (recommended for first test), also run:

```bash
super model install llama3.1:8b
```

## Step 2: Start Required Services

### 2A) Start Ollama (local model service)

```bash
ollama serve
```

Keep this terminal open.

### 2B) Start SurrealDB

Open a new terminal and run:

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Keep this terminal open too.

## Step 3: Seed Demo Data (No Source Code Needed)

In a third terminal, run:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
```

Expected success output includes:

- `SurrealDB seed complete`
- `Inserted: 8`

### Optional: Seed GraphRAG Data

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

Expected success output includes:

- `GraphRAG seeding:`
- `Nodes created:`
- `Edges created:` (should be greater than 0)

Important note:

- `--graph` replaces previous seed rows from the same source.
- If you want both graph docs and token docs together, run this after `--graph`:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --append
```

## Step 4: First Successful Run (DSPy + Local)

Run exactly:

```bash
super agent pull rag_surrealdb_dspy_demo
super agent compile rag_surrealdb_dspy_demo --framework dspy
super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
```

Expected success signs:

- `🔍 RAG retrieval enabled (runner-managed).`
- output mentions `NEON-FOX-742`
- `Validation Status: ✅ PASSED`

## Step 5: Run GraphRAG (DSPy)

Run:

```bash
super agent pull graphrag_surrealdb_dspy_demo
super agent compile graphrag_surrealdb_dspy_demo --framework dspy
super agent run graphrag_surrealdb_dspy_demo --framework dspy --goal "What capabilities does SurrealDB provide?"
```

Expected success signs:

- No fallback warning about RELATE
- answer includes SurrealDB capabilities from graph-connected docs
- `Validation Status: ✅ PASSED`

## Optional: Run with Gemini 2.5 Flash

Set your key:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Run RAG with Gemini:

```bash
super agent run rag_surrealdb_dspy_demo --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
```

Run GraphRAG with Gemini:

```bash
super agent run graphrag_surrealdb_dspy_demo --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
```

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

## How To Run Each Feature

### Feature: Vector RAG (`surrealdb-vector-rag`)

```bash
super agent pull rag_surrealdb_dspy_demo
super agent compile rag_surrealdb_dspy_demo --framework dspy
super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
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
super agent pull graphrag_surrealdb_dspy_demo
super agent compile graphrag_surrealdb_dspy_demo --framework dspy
super agent run graphrag_surrealdb_dspy_demo --framework dspy --goal "What capabilities does SurrealDB provide?"
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

- If `fn::embed` is available in SurrealDB, server embeddings are used.
- If unavailable, SuperOptiX falls back to client embeddings automatically.

### Feature: Live Memory Utility (`surrealdb-live-memory`)

Python usage:

```python
from superoptix.memory import LiveMemorySubscriber

# Requires SurrealDB backend using ws:// or wss://
# subscribe(table, callback) gives real-time memory updates
```

Note: this is provided as a standalone utility and is not auto-wired into every runtime path.

### Feature: Read-only MCP Tool (`surrealdb-mcp-readonly`)

Use built-in tool:

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

- read-only statement allowlist (`SELECT`, `INFO`, `RETURN`)
- row limit injection when missing
- query timeout protection

### Feature: Capability Gating (`surrealdb-capability-gating`)

SuperOptiX probes SurrealDB features at runtime and degrades safely when needed.

Examples:

- Graph mode falls back to vector/hybrid when RELATE is unavailable.
- Server embedding mode falls back to client embedding when `fn::embed` is unavailable.

## One-Command Pattern for Any Framework

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
super agent run <demo_id> --framework <framework_name> --goal "your question"
```

## Most Common Problems and Fixes

### Problem: `Connection refused`

Meaning: SurrealDB is not running.

Fix:

```bash
docker ps --filter name=surrealdb-demo
```

If nothing is listed, start SurrealDB again (Step 2B).

### Problem: `did not receive a valid HTTP response`

Meaning: wrong SurrealDB URL.

Fix:

- use `ws://localhost:8000`
- do not use `/rpc` in URL

### Problem: Graph warning `falling back from 'graph' to 'vector' mode`

Meaning: graph edges were not available or parser compatibility issue.

Fix:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

Confirm `Edges created:` is greater than `0`.

### Problem: `Ollama_chatException - {"error":"model is required"}`

Meaning: wrong model string passed.

Fix: use this exact format:

```bash
super agent run rag_surrealdb_dspy_demo --framework dspy --local --provider ollama --model llama3.1:8b --goal "What is NEON-FOX-742?"
```

### Problem: Gemini says `API_KEY_INVALID` or `API Key not found`

Meaning: key missing or wrong.

Fix:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Then run again.

### Problem: You see `embeddings.position_ids | UNEXPECTED`

Meaning: model loading report. Usually safe.

If seeding/run still completes, ignore it.

## Quick Verification (Graph Really Works)

Run:

```bash
python - <<'PY'
from surrealdb import Surreal

with Surreal("ws://localhost:8000") as db:
    db.signin({"username":"root","password":"secret"})
    db.use("superoptix","knowledge")
    print(db.query("SELECT count() AS c FROM integrates_with WHERE source='superoptix_seed';"))
    print(db.query("SELECT content FROM rag_documents:superoptix->integrates_with->rag_documents;"))
PY
```

If count is non-zero and traversal returns rows, GraphRAG data is active.

## Related Pages

- [SurrealDB Demo](surrealdb-demo.md)
- [SurrealDB Docker Demo](surrealdb-docker-demo.md)
- [RAG Guide](../../guides/rag.md)
