# RAG LanceDB Demo Agent

This demo uses the `turboagents-lancedb` retriever path inside SuperOptiX. LanceDB remains the persisted candidate store, while TurboAgents adds compressed retrieval and reranking in the shared RAG flow.

## What This Demo Shows

- TurboAgents-backed LanceDB retrieval in the normal SuperOptiX demo flow
- persisted local LanceDB tables that reopen in a fresh process
- seeded validation data for a concrete retrieval check
- playbook settings for `turboagents-lancedb`

## Setup

Install the local model and start Ollama:

```bash
super model install qwen3.5:9b
ollama serve
```

Pull, compile, seed, and run the demo:

```bash
uv pip install "superoptix[turboagents]"
super agent pull rag_lancedb_demo
super agent compile rag_lancedb_demo
uv run python superoptix/agents/demo/setup_lancedb_seed.py
super agent run rag_lancedb_demo --goal "What is LANCE-TURBO-314?"
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
  retriever_type: turboagents-lancedb
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
    rerank_top: 16
    table_name: lancedb_demo_table
    uri: ./data/lancedb
```

## Why This Uses TurboAgents

This demo now exercises the real TurboAgents integration path instead of only the native LanceDB retriever.

That means:

- LanceDB stores and searches the candidate set
- SuperOptiX selects `turboagents-lancedb` from the normal RAG config surface
- TurboAgents reranks that candidate set inside the shared RAG runtime

## Validated Result

This demo is validated end to end locally. The observed run:

```bash
super agent run rag_lancedb_demo --goal "What is LANCE-TURBO-314?"
```

returned a grounded answer identifying `LANCE-TURBO-314` as the seeded validation token for the TurboAgents-backed LanceDB demo path.

This validation matters because it proves more than unit tests:

- the playbook compiles through the normal SuperOptiX CLI
- the persisted LanceDB table reopens in a fresh process
- the shared RAG runtime can query the TurboAgents-backed store during a real demo run

## Troubleshooting

Common checks:

```bash
curl http://localhost:11434/api/tags
super agent inspect rag_lancedb_demo
uv run python superoptix/agents/demo/setup_lancedb_seed.py
```

## Related Resources

- [TurboAgents Integration Guide](../../guides/turboagents-integration.md)
- [RAG Chroma Demo](rag-chroma-demo.md)
- [SurrealDB Frameworks Guide](surrealdb-frameworks-demo.md)
