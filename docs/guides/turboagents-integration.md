# TurboAgents Integration

`superoptix` can now use `turboagents` as a real GEPA vector-store backend.

This integration now covers two paths:

- `turboagents`-backed GEPA vector stores through `VectorStoreInterface`
- main SuperOptiX `rag_mixin` retriever types for FAISS, LanceDB, and SurrealDB

## What You Get

SuperOptiX now exposes these `turboagents`-backed vector stores:

- `TurboFAISSVectorStore`
- `TurboLanceDBVectorStore`
- `TurboSurrealDBVectorStore`

These wrap the corresponding `turboagents` retrieval adapters and make them
usable inside the SuperOptiX GEPA RAG pipeline.

SuperOptiX also accepts these retriever types in the main RAG config:

- `turboagents-faiss`
- `turboagents-lancedb`
- `turboagents-surrealdb`

## Install

Install the dedicated extra:

```bash
pip install "superoptix[turboagents]"
```

Or install the broader vector DB extra:

```bash
pip install "superoptix[vectordb]"
```

## Runnable Example

A minimal local FAISS-based example is included at:

- `examples/turboagents_gepa_rag.py`

Run it with:

```bash
python examples/turboagents_gepa_rag.py
```

What it demonstrates:

- creating a `TurboFAISSVectorStore`
- adding documents and embeddings
- executing a SuperOptiX `RAGPipeline`
- using `turboagents` reranking under the SuperOptiX interface

## Programmatic Usage

### FAISS

```python
from superoptix.optimizers.gepa_rag_adapter import RAGPipeline, TurboFAISSVectorStore

vector_store = TurboFAISSVectorStore(
    dim=128,
    bits=3.5,
    seed=0,
    embedding_function=embed,
    rerank_top=16,
)
```

### LanceDB

```python
from superoptix.optimizers.gepa_rag_adapter import TurboLanceDBVectorStore

vector_store = TurboLanceDBVectorStore(
    uri="./data/turboagents-lancedb",
    table_name="documents",
    dim=128,
    bits=3.5,
    seed=0,
    embedding_function=embed,
    rerank_top=16,
)
```

### SurrealDB

```python
from superoptix.optimizers.gepa_rag_adapter import TurboSurrealDBVectorStore

vector_store = TurboSurrealDBVectorStore(
    url="ws://localhost:8000/rpc",
    namespace="test",
    database="test",
    table_name="documents",
    dim=128,
    bits=3.5,
    seed=0,
    embedding_function=embed,
    rerank_top=16,
)
```

## Playbook / RAG Config Usage

Use one of the new retriever types directly in the RAG block:

```yaml
rag:
  enabled: true
  retriever_type: turboagents-faiss
  config:
    top_k: 5
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
    seed: 0
```

For LanceDB:

```yaml
rag:
  enabled: true
  retriever_type: turboagents-lancedb
  config:
    top_k: 5
  vector_store:
    uri: ./.superoptix/turboagents-lancedb
    table_name: documents
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
```

For SurrealDB:

```yaml
rag:
  enabled: true
  retriever_type: turboagents-surrealdb
  config:
    top_k: 5
  vector_store:
    url: ws://localhost:8000/rpc
    namespace: test
    database: test
    table_name: documents
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
```

## Current Limits

Current limits:

- metadata filtering is not implemented yet for these wrappers
- the SurrealDB GEPA wrapper uses the sync boundary around the async `turboagents` adapter, so it is aimed at synchronous GEPA flows first
- dimensions must match the current TurboAgents quantization surface, such as `64`, `128`, or `256`
- sentence-transformer embeddings are trimmed or zero-padded to the configured TurboAgents dimension

## Recommended Next Step

After validating the GEPA path, the next integration step is:

1. wire one or more demo playbooks to the new retriever types
2. compare native SuperOptiX retrieval with the `turboagents`-backed path on the same workload
3. decide whether to promote one backend as the default integration story
