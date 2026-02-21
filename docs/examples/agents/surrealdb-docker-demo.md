# SurrealDB Docker RAG Demo

Run SuperOptiX RAG with SurrealDB in Docker using authenticated WebSocket mode.

## 1) Install dependencies

```bash
pip install "superoptix[surrealdb]"
```

## 2) Start SurrealDB in Docker

```bash
docker run --rm -p 8000:8000 --name surrealdb-demo surrealdb/surrealdb:latest \
  start --log info --user root --pass secret memory
```

## 3) Start model backend

```bash
super model install llama3.1:8b
ollama serve
```

## 4) Pull, compile, run Docker demo agent

```bash
super agent pull rag_surrealdb_docker_demo
super agent compile rag_surrealdb_docker_demo
super agent run rag_surrealdb_docker_demo --goal "Explain SurrealDB hybrid retrieval in SuperOptiX"
```

## Playbook settings used

```yaml
rag:
  enabled: true
  retriever_type: surrealdb
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

- If you see auth errors, ensure Docker command credentials match playbook credentials.
- If port conflict occurs, free `8000` or map to another port and update playbook URL.
- If answer is generic, table may have no data yet; ingest documents first.
- Use base server URL (`ws://localhost:8000`), not `.../rpc` (SDK appends `/rpc` internally).

## Related

- [SurrealDB Embedded Demo](surrealdb-demo.md)
- [RAG Guide](../../guides/rag.md)
