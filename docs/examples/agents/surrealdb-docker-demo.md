# SurrealDB Docker Demo (Simple Path)

Use this when you want SurrealDB in Docker with username/password auth.

## What This Page Covers

- start SurrealDB in Docker
- seed data
- run RAG demo
- run GraphRAG demo

## 1) Install

```bash
pip install "superoptix[surrealdb]"
super model install llama3.1:8b
```

## 2) Start services

Terminal A:

```bash
ollama serve
```

Terminal B:

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

## 3) Seed data

Terminal C:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed
```

For GraphRAG:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

## 4) Run RAG demo

```bash
super agent pull rag_surrealdb_dspy_demo
super agent compile rag_surrealdb_dspy_demo --framework dspy
super agent run rag_surrealdb_dspy_demo --framework dspy --goal "What is NEON-FOX-742?"
```

## 5) Run GraphRAG demo

```bash
super agent pull graphrag_surrealdb_dspy_demo
super agent compile graphrag_surrealdb_dspy_demo --framework dspy
super agent run graphrag_surrealdb_dspy_demo --framework dspy --goal "What capabilities does SurrealDB provide?"
```

## Docker Config Used

```yaml
vector_store:
  url: ws://localhost:8000
  namespace: superoptix
  database: knowledge
  username: root
  password: secret
  skip_signin: false
  table_name: rag_documents
```

## Troubleshooting

### Auth error

Make sure Docker `--user root --pass secret` matches playbook credentials.

### Port conflict

If `8000` is already used, map a different port and update playbook URL.

Example:

```bash
docker run --rm -p 18000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

Then use `ws://localhost:18000` in playbook.

### Graph falls back to vector mode

Run graph seed again and confirm edges are created:

```bash
python -m superoptix.agents.demo.setup_surrealdb_seed --graph
```

### `.../rpc` URL issue

Use base URL only. Correct format:

- `ws://localhost:8000`

## Related

- [SurrealDB Demo](surrealdb-demo.md)
- [SurrealDB Framework Guide](surrealdb-frameworks-demo.md)
