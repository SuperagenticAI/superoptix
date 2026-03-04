# SurrealDB RAG Demo (Beginner Friendly)

This is the easiest SurrealDB demo to start with.

You will run one agent that reads knowledge from SurrealDB and answers with grounded context.

## What You Get

- SurrealDB-backed retrieval
- token grounding check (`NEON-FOX-742`)
- simple run path using DSPy framework

## Step-by-Step

### 1) Install

```bash
pip install "superoptix[surrealdb]"
super model install llama3.1:8b
```

### 2) Start services

Terminal A:

```bash
ollama serve
```

Terminal B:

```bash
docker run --rm -p 8000:8000 surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

### 3) Seed demo data

Terminal C:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
```

Expected:

- `SurrealDB seed complete`
- `Inserted: 8`

### 4) Pull + compile + run

```bash
super agent pull rag_surrealdb_dspy_demo
super agent compile rag_surrealdb_dspy_demo --framework dspy
super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
```

Expected:

- `🔍 RAG retrieval enabled (runner-managed).`
- response mentions `NEON-FOX-742`
- `Validation Status: ✅ PASSED`

## Optional: Run with Gemini

Set key:

```bash
export GEMINI_API_KEY=your_key_here
# or
export GOOGLE_API_KEY=your_key_here
```

Run:

```bash
super agent run rag_surrealdb_dspy_demo --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "What is NEON-FOX-742?"
```

## Minimal Config Reference

```yaml
rag:
  enabled: true
  retriever_type: surrealdb
  config:
    top_k: 5
    retrieval_mode: vector   # or hybrid
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

## Troubleshooting

### `Connection refused`

SurrealDB is not running. Start Docker command again.

### `model is required` with Ollama

Use model as `llama3.1:8b` (not `ollama:llama3.1:8b`).

### `API Key not found` for Gemini

Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) before run.

### `embeddings.position_ids | UNEXPECTED`

Usually informational only. Ignore if run succeeds.

## Next Step

If this worked, continue with GraphRAG:

- [SurrealDB Framework Guide](surrealdb-frameworks-demo.md)
