# SurrealDB RAG Demo

A demonstration of SuperOptiX RAG capabilities using **SurrealDB** for vector and hybrid retrieval workflows.

## Overview

This demo shows how to connect SuperOptiX RAG to SurrealDB and use:

- Vector similarity retrieval via SurrealQL vector functions
- Metadata-aware filtering for targeted retrieval
- Hybrid retrieval design (semantic + lexical scoring)

## Prerequisites

### Install SuperOptiX + SurrealDB extra
```bash
pip install "superoptix[surrealdb]"
```

### Option A: No Docker (embedded, in-memory, ephemeral)
```yaml
vector_store:
  url: memory
  namespace: test
  database: test
  username: root
  password: root
  skip_signin: true
```

### Option B: No Docker (embedded, persistent local file)
```yaml
vector_store:
  url: surrealkv://./.superoptix/surreal.db
  namespace: test
  database: test
  username: root
  password: root
  skip_signin: true
```

### Option C: Start SurrealDB with Docker
```bash
docker run --rm -p 8000:8000 surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

### Install and serve model
```bash
super model install llama3.1:8b
ollama serve
```

## Quick Start

### Pull the demo
```bash
super agent pull rag_surrealdb_demo
```

### Compile
```bash
super agent compile rag_surrealdb_demo
```

### Seed demo knowledge once
```bash
python superoptix/agents/demo/setup_surrealdb_seed.py
```

### Run
```bash
super agent run rag_surrealdb_demo --goal "How can SurrealDB improve RAG workflows in SuperOptiX?"
```

## Playbook Configuration

```yaml
rag:
  enabled: true
  retriever_type: surrealdb
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
    retrieval_mode: vector  # or "hybrid"
    hybrid_alpha: 0.7
    telemetry: true
    index_check: true
vector_store:
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  url: surrealkv://./.superoptix/surreal.db
  namespace: test
  database: test
  username: root
  password: root
  skip_signin: true
  table_name: rag_documents
  vector_field: embedding
  content_field: content
  metadata_field: metadata
```

## Workflow Integration Ideas

- Use SurrealDB as a unified operational + vector layer for agent memory and retrieval.
- Store graph links between documents and entities, then combine relation hops with vector retrieval.
- Use SurrealQL filtering to scope retrieval by tenant, document type, or freshness window.
- Use hybrid retrieval when exact terms matter alongside semantic similarity.
- Set `rag.config.retrieval_mode: hybrid` to combine lexical and vector ranking.
- Keep `rag.config.telemetry: true` for retrieval latency/hit/score observability.
- `memory` is connection-scoped and ephemeral; for repeated runs use `surrealkv://...`.
- Set `skip_signin: false` when using authenticated `ws://` / `http://` SurrealDB servers.

## Related

- [RAG Guide](../../guides/rag.md)
- [Qdrant Demo](qdrant-demo.md)
- [Milvus Demo](milvus-demo.md)
