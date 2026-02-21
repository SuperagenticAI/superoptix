# 🌌 SurrealDB Framework Guide

This page explains how to run SurrealDB RAG in SuperOptiX across DSPy, PydanticAI, CrewAI, and Google ADK.

## Quick start for beginners

Follow these steps in order.

### 1. Install dependencies

```bash
pip install "superoptix[surrealdb]"
super model install llama3.1:8b
```

### 2. Start Ollama

```bash
ollama serve
```

### 3. Start SurrealDB (Docker)

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

### 4. Run one demo first (DSPy)

```bash
super agent pull rag_surrealdb_demo
super agent compile rag_surrealdb_demo
super agent run rag_surrealdb_demo --goal "What is NEON-FOX-742?"
```

### 5. Confirm it is working

Look for this line in logs:

```text
🔍 RAG retrieval enabled (runner-managed).
```

## Framework support matrix

| Framework | SurrealDB RAG | Status | Notes |
|---|---|---|---|
| DSPy | Yes | Stable | Best first demo for new users |
| PydanticAI | Yes | Stable | Same RAG config |
| CrewAI | Yes | Stable | Same RAG config, prompt style may need tuning |
| Google ADK | Yes | Stable | Works with cloud model runtime |
| DeepAgents | Shared RAG engine | Expected | Use same `rag` block and validate playbook behavior |

## Core shared RAG config

Use this in playbooks for all frameworks.

```yaml
rag:
  enabled: true
  retriever_type: surrealdb
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.65
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
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

## SurrealDB deployment options

### Option A: In-memory embedded mode (no Docker)

```yaml
vector_store:
  url: memory
  namespace: test
  database: test
  username: root
  password: root
  skip_signin: true
```

### Option B: Embedded persistent file (no Docker)

```yaml
vector_store:
  url: surrealkv://./.superoptix/surreal.db
  namespace: test
  database: test
  username: root
  password: root
  skip_signin: true
```

### Option C: Docker server mode

```yaml
vector_store:
  url: ws://localhost:8000
  namespace: superoptix
  database: knowledge
  username: root
  password: secret
  skip_signin: false
```

## Framework run commands

### DSPy

```bash
super agent pull rag_surrealdb_demo
super agent compile rag_surrealdb_demo
super agent run rag_surrealdb_demo --goal "What is NEON-FOX-742?"
```

### PydanticAI

```bash
super agent pull rag_surrealdb_pydanticai_demo
super agent compile rag_surrealdb_pydanticai_demo --framework pydantic-ai
super agent run rag_surrealdb_pydanticai_demo --goal "What is NEON-FOX-742?"
```

### CrewAI

```bash
super agent pull rag_surrealdb_crewai_demo
super agent compile rag_surrealdb_crewai_demo --framework crewai
super agent run rag_surrealdb_crewai_demo --goal "What is NEON-FOX-742?"
```

### Google ADK

Fish shell:

```fish
set -x GOOGLE_API_KEY your_key_here
```

```bash
super agent pull rag_surrealdb_adk_demo
super agent compile rag_surrealdb_adk_demo --framework google-adk --cloud --provider google --model gemini-2.5-flash
super agent run rag_surrealdb_adk_demo --framework google-adk --cloud --provider google --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
```

## How retrieval works across frameworks

1. The framework pipeline starts.
2. SuperOptiX checks `rag.enabled` and `retriever_type: surrealdb`.
3. SurrealDB retrieves context.
4. Retrieved context is injected into the prompt.
5. The model returns a final answer.

## Troubleshooting

### `Connection refused`

Cause: SurrealDB is not reachable.

Fix:

```bash
docker ps --filter name=surrealdb-demo
```

If Docker maps a different host port, update `vector_store.url` to that port.
Example: `ws://localhost:18000`.

### `did not receive a valid HTTP response`

Cause: invalid URL.

Fix: use base URL only, no `/rpc`.
Correct: `ws://localhost:8000`

### Authentication failed

Cause: credentials mismatch.

Fix: `--user` and `--pass` in Docker must match `username` and `password` in playbook.

### Generic answer even though run passed

Cause: model style, not retrieval wiring.

Fix:

- Confirm log contains `🔍 RAG retrieval enabled (runner-managed).`
- Confirm prompt shows retrieved context.
- Tighten task/persona instruction to enforce final-answer-only output.

### First run downloads embeddings

`sentence-transformers/all-MiniLM-L6-v2` is fetched from HuggingFace on first run and then cached.

## Validation checklist

- SurrealDB container is running.
- `vector_store.url` matches running port.
- Logs show `🔍 RAG retrieval enabled (runner-managed).`
- No SurrealDB connection or auth error.
- Output contains facts from retrieved context.

## Related

- [SurrealDB Embedded Demo](surrealdb-demo.md)
- [SurrealDB Docker Demo](surrealdb-docker-demo.md)
- [RAG Guide](../../guides/rag.md)
