# TurboAgents Integration

`superoptix` can use `turboagents` as both a GEPA vector-store backend and a shared RAG retriever backend.

This is the current reference integration for TurboAgents. The package stays framework-agnostic, but SuperOptiX is where the full compile, run, and demo validation path exists today.

## What You Get

SuperOptiX exposes these TurboAgents-backed vector stores through the GEPA adapter layer:

- `TurboChromaVectorStore`
- `TurboFAISSVectorStore`
- `TurboLanceDBVectorStore`
- `TurboSurrealDBVectorStore`

SuperOptiX also accepts these retriever types in the main RAG config:

- `turboagents-chroma`
- `turboagents-faiss`
- `turboagents-lancedb`
- `turboagents-surrealdb`

## Install

If you are working from a SuperOptiX source checkout, use `uv` extras:

```bash
uv sync --extra turboagents
```

Add framework extras when you want to validate those runtime paths too:

```bash
uv sync --extra turboagents --extra frameworks-openai --extra frameworks-pydantic-ai
uv sync --extra turboagents --extra frameworks-dspy
```

If you are using the published package instead of a source checkout:

```bash
uv pip install "superoptix[turboagents]"
```

## Runnable Example

A minimal local FAISS-based example is included at `examples/turboagents_gepa_rag.py`.

Run it with:

```bash
uv run python examples/turboagents_gepa_rag.py
```

What it demonstrates:

- creating a `TurboFAISSVectorStore`
- adding documents and embeddings
- executing a SuperOptiX `RAGPipeline`
- using TurboAgents reranking under the SuperOptiX interface

## Validation Matrix

The current local validation state is:

| Surface | Status | Notes |
| --- | --- | --- |
| `turboagents-chroma` | Passed | Focused tests plus direct `RAGMixin` smoke on `chromadb 1.5.5` |
| `turboagents-lancedb` | Passed | End-to-end `rag_lancedb_demo` run returned the seeded `LANCE-TURBO-314` token |
| `turboagents-surrealdb` + OpenAI Agents | Passed | End-to-end local run returned the seeded `NEON-FOX-742` token |
| `turboagents-surrealdb` + Pydantic AI | Passed | End-to-end local run returned the seeded `NEON-FOX-742` token |
| `turboagents-surrealdb` + DSPy | Blocked | Local LiteLLM and Ollama compatibility issue for `qwen3.5:9b`; retrieval path itself is not the blocker |
| LiteLLM dependency security | Hardened | SuperOptiX excludes compromised `1.82.7` and `1.82.8`; current resolved local version is `1.81.6` |

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

### Chroma

```python
from superoptix.optimizers.gepa_rag_adapter import TurboChromaVectorStore

vector_store = TurboChromaVectorStore(
    path="./data/turboagents-chroma",
    collection_name="documents",
    dim=64,
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

## Playbook Usage

Use one of the TurboAgents retriever types directly in the RAG block.

### Chroma

```yaml
rag:
  enabled: true
  retriever_type: turboagents-chroma
  config:
    top_k: 5
  vector_store:
    persist_directory: ./.superoptix/turboagents-chroma
    collection_name: documents
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
    seed: 0
```

### FAISS

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

### LanceDB

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

Validate the local LanceDB demo path with:

```bash
uv run python superoptix/agents/demo/setup_lancedb_seed.py
super agent run rag_lancedb_demo --goal "What is LANCE-TURBO-314?"
```

### SurrealDB

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

Validate the local SurrealDB demo path with:

```bash
uv run python superoptix/agents/demo/setup_surrealdb_seed.py
super agent run rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"
super agent run rag_surrealdb_pydanticai_demo --framework pydantic-ai --goal "What is NEON-FOX-742?"
```

The seed helper now understands `turboagents-surrealdb` directly and writes TurboAgents-compatible payloads. It also trims or pads sentence-transformer embeddings to the configured TurboAgents dimension so the seeded data matches runtime behavior.

## Current Limits

Current limits:

- metadata filtering is not implemented yet for these wrappers
- the SurrealDB GEPA wrapper uses a sync boundary around the async TurboAgents adapter, so it is aimed at synchronous GEPA flows first
- dimensions must match the current TurboAgents quantization surface, such as `64`, `128`, or `256`
- the DSPy SurrealDB path still needs a clean local Ollama and LiteLLM fix before it can join the validated matrix

## Security Note

SuperOptiX excludes LiteLLM `1.82.7` and `1.82.8` after the March 2026 PyPI compromise advisory. The current local resolved version used in validation is `1.81.6`.
