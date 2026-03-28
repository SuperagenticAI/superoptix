# RAG Chroma Demo Agent

This demo uses the `turboagents-chroma` retriever path inside SuperOptiX. Chroma stays the local collection backend, while TurboAgents adds compressed retrieval and reranking on top.

## What This Demo Shows

- TurboAgents-backed Chroma retrieval in the normal SuperOptiX RAG flow
- persisted local Chroma collections
- sentence-transformer embeddings with TurboAgents reranking
- the playbook settings needed for a TurboAgents-backed Chroma path

## Setup

Install the local model used by the demo:

```bash
super model install qwen3.5:9b
ollama serve
```

Pull, compile, and run the demo:

```bash
uv pip install "superoptix[turboagents]"
super agent pull rag_chroma_demo
super agent compile rag_chroma_demo
super agent run rag_chroma_demo --goal "What is the SuperOptiX framework?"
```

## Playbook Configuration

```yaml
language_model:
  location: local
  provider: ollama
  model: qwen3.5:9b
  api_base: http://localhost:11434
  temperature: 0.7
  max_tokens: 2048

rag:
  enabled: true
  retriever_type: turboagents-chroma
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    collection_name: rag_demo_knowledge
    persist_directory: ./.superoptix/turboagents-chroma
```

Important points:

- `retriever_type: turboagents-chroma` selects the TurboAgents path
- `embedding_dimension: 64` matches a supported TurboAgents compressed dimension
- Chroma handles candidate persistence and search
- TurboAgents reranks the candidate set before context is injected into the model

## Validation Status

Current local validation for this path is narrower than LanceDB and SurrealDB. What is validated today is:

- focused SuperOptiX tests for the TurboAgents vector-store and RAG mixin paths
- direct `RAGMixin` smoke using the real TurboAgents Chroma adapter
- local alignment on `chromadb 1.5.5` in both TurboAgents and SuperOptiX

This means the Chroma integration is implemented and exercised locally, but this page does not claim a recorded end-to-end demo transcript yet.

## Retrieval Stack

The runtime stack is:

- `sentence-transformers` creates document and query embeddings
- Chroma stores and retrieves the candidate set
- TurboAgents reranks those candidates using compressed retrieval
- SuperOptiX injects the selected context into the compiled framework runtime

## Troubleshooting

Common checks:

```bash
curl http://localhost:11434/api/tags
super agent inspect rag_chroma_demo
```

If you need a clean local Chroma collection, remove the persisted demo directory and rerun the demo.

## Related Resources

- [TurboAgents Integration Guide](../../guides/turboagents-integration.md)
- [RAG LanceDB Demo](rag-lancedb-demo.md)
- [SurrealDB Frameworks Guide](surrealdb-frameworks-demo.md)
