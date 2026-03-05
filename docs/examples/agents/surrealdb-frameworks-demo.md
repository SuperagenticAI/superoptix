# SurrealDB

This is the single SurrealDB guide for SuperOptiX.

It combines the earlier beginner demo, Docker demo, and framework guide into one page so you can find everything in one place.

## What This Guide Covers

You will learn how to:

- start SurrealDB
- seed demo data
- run standard RAG
- run GraphRAG
- run the same SurrealDB-backed behavior across multiple frameworks
- understand which SurrealDB features are already integrated in SuperOptiX

This guide is written for beginners. If you can copy and paste terminal commands, you can run it.

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

## Time Needed

- First run: about 10-20 minutes
- Later runs: 2-5 minutes

## Before You Start

You need:

- Python environment with `superoptix`
- Docker installed
- terminal access
- optional for cloud models: API keys for Gemini, Anthropic, or OpenAI

## Quick Start

This is the fastest path to a successful first run.

### 1) Install

```bash
pip install "superoptix[surrealdb]"
ollama pull llama3.1:8b
```

### 2) Start services

Terminal A:

```bash
ollama serve
```

Terminal B:

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Keep both terminals open.

### 3) Seed demo data

Terminal C:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
```

Expected success output includes:

- `SurrealDB seed complete`
- `Inserted: 8`

### 4) Pull, compile, and run RAG

```bash
super agent pull rag_surrealdb_dspy_demo
super agent compile rag_surrealdb_dspy_demo --framework dspy
super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
```

Expected success signs:

- `RAG retrieval enabled`
- output mentions `NEON-FOX-742`
- `Validation Status: ✅ PASSED`

## GraphRAG Quick Start

### 1) Seed graph data

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

Expected success output includes:

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

```bash
super agent pull graphrag_surrealdb_dspy_demo
super agent compile graphrag_surrealdb_dspy_demo --framework dspy
super agent run graphrag_surrealdb_dspy_demo --framework dspy --goal "What capabilities does SurrealDB provide?"
```

Expected success signs:

- no fallback warning about `RELATE`
- answer includes SurrealDB capabilities from graph-connected docs
- `Validation Status: ✅ PASSED`

## Run With Gemini

Set your API key:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Run standard RAG:

```bash
super agent run rag_surrealdb_dspy_demo --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
```

Run GraphRAG:

```bash
super agent run graphrag_surrealdb_dspy_demo --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "What capabilities does SurrealDB provide?"
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
super agent run <demo_id> --framework <framework_name> --goal "your question"
```

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

## Minimal Config Reference

```yaml
rag:
  enabled: true
  retriever_type: surrealdb
  config:
    top_k: 5
    retrieval_mode: vector
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
super agent run rag_surrealdb_dspy_demo --framework dspy --local --provider ollama --model llama3.1:8b --goal "What is NEON-FOX-742?"
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

Success means:

- the answer contains `NEON-FOX-742`
- the run ends with `Validation Status: ✅ PASSED`

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

If the count is non-zero and traversal returns rows, GraphRAG data is active.

## Related

- [RAG Guide](../../guides/rag.md)
- [Memory Guide](../../guides/memory.md)
