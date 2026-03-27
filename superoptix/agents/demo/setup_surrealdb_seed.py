#!/usr/bin/env python3
"""
Seed SurrealDB demo documents for SuperOptiX RAG examples.

Minimal usage:
  python superoptix/agents/demo/setup_surrealdb_seed.py

Graph-enabled seeding (creates entity nodes + RELATE edges):
  python superoptix/agents/demo/setup_surrealdb_seed.py --graph

By default this uses:
  - playbook: superoptix/agents/demo/rag_surrealdb_openai_demo_playbook.yaml
  - dataset:  superoptix/agents/demo/surrealdb_seed_dataset.jsonl

Use --playbook to target any SurrealDB demo playbook.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _normalize_surrealdb_url(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme in {"ws", "wss", "http", "https"} and parsed.path.rstrip("/") == "/rpc":
        return f"{scheme}://{parsed.netloc}"
    return url


def _default_skip_signin(url: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    return scheme in {"memory", "mem", "file", "surrealkv"} or url == "memory"


def load_seed_documents(dataset_path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            text = raw.strip()
            if not text:
                continue
            row = json.loads(text)
            content = str(row.get("content", "")).strip()
            if not content:
                raise ValueError(
                    f"Dataset row {line_no} is missing non-empty 'content'."
                )
            metadata = row.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {"value": metadata}
            doc_id = str(row.get("id", f"seed-{line_no:03d}")).strip()
            metadata.setdefault("seed_id", doc_id)
            metadata.setdefault("source", "superoptix_surreal_seed_v1")
            docs.append({"id": doc_id, "content": content, "metadata": metadata})
    if not docs:
        raise ValueError(f"No seed documents found in {dataset_path}")
    return docs


def load_graph_seed_documents(dataset_path: Path) -> list[dict[str, Any]]:
    """Load graph seed documents with relationships from JSONL.

    Each document must have metadata.entity_id for deterministic record IDs.
    Relationships reference other entity_ids via the 'target' field.
    """
    docs: list[dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            text = raw.strip()
            if not text:
                continue
            row = json.loads(text)
            content = str(row.get("content", "")).strip()
            if not content:
                raise ValueError(
                    f"Graph dataset row {line_no} is missing non-empty 'content'."
                )
            metadata = row.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {"value": metadata}
            entity_id = metadata.get("entity_id")
            if not entity_id:
                raise ValueError(
                    f"Graph dataset row {line_no} is missing metadata.entity_id."
                )
            # Sanitize entity_id: lowercase, alphanumeric + underscores only
            sanitized = re.sub(r"[^a-z0-9_]", "_", str(entity_id).lower())
            metadata["entity_id"] = sanitized
            metadata.setdefault("source", "superoptix_surreal_seed_v1")
            relationships = row.get("relationships", [])
            if not isinstance(relationships, list):
                relationships = []
            docs.append(
                {
                    "id": sanitized,
                    "content": content,
                    "metadata": metadata,
                    "relationships": relationships,
                }
            )
    if not docs:
        raise ValueError(f"No graph seed documents found in {dataset_path}")
    return docs


def _validate_graph_dataset(documents: list[dict[str, Any]]) -> None:
    """Validate that all relationship targets reference valid entity_ids."""
    entity_ids = {doc["id"] for doc in documents}
    for doc in documents:
        for rel in doc.get("relationships", []):
            target = re.sub(r"[^a-z0-9_]", "_", str(rel.get("target", "")).lower())
            if target not in entity_ids:
                raise ValueError(
                    f"Entity '{doc['id']}' has relationship targeting '{target}' "
                    f"which is not a valid entity_id in the dataset. "
                    f"Valid IDs: {sorted(entity_ids)}"
                )
            rel_type = str(rel.get("type", "")).strip()
            if not rel_type or not re.match(r"^[a-z_][a-z0-9_]*$", rel_type):
                raise ValueError(
                    f"Entity '{doc['id']}' has invalid relationship type '{rel_type}'. "
                    f"Must be lowercase alphanumeric with underscores."
                )


def _define_indexes(
    db: Any,
    table_name: str,
    vector_field: str,
    content_field: str,
    embedding_dim: int = 384,
) -> None:
    """Define HNSW vector, full-text, and entity_id indexes."""
    index_stmts = [
        f"DEFINE INDEX IF NOT EXISTS idx_rag_embedding ON {table_name} "
        f"FIELDS {vector_field} HNSW DIMENSION {embedding_dim} DIST COSINE;",
        f"DEFINE INDEX IF NOT EXISTS idx_rag_content_ft ON {table_name} "
        f"FIELDS {content_field} SEARCH ANALYZER ascii BM25;",
        f"DEFINE INDEX IF NOT EXISTS idx_rag_entity_id ON {table_name} "
        f"FIELDS metadata.entity_id;",
    ]
    for stmt in index_stmts:
        try:
            db.query(stmt)
        except Exception as e:
            # Index creation may fail on older SurrealDB versions — non-fatal
            print(f"   Warning: Index creation skipped: {e}")


def _seed_graph_nodes(
    db: Any,
    documents: list[dict[str, Any]],
    table_name: str,
    vector_field: str,
    content_field: str,
    metadata_field: str,
    model: Any,
) -> int:
    """Create entity records with deterministic record IDs."""
    inserted = 0
    for doc in documents:
        entity_id = doc["id"]
        embedding = model.encode(doc["content"]).tolist()
        payload = {
            content_field: doc["content"],
            vector_field: embedding,
            metadata_field: doc["metadata"],
        }
        # Use deterministic record ID: table_name:entity_id
        db.query(
            f"CREATE {table_name}:{entity_id} CONTENT $payload;",
            {"payload": payload},
        )
        inserted += 1
    return inserted


def _seed_graph_relations(
    db: Any,
    documents: list[dict[str, Any]],
    table_name: str,
) -> int:
    """Create RELATE edges between entity records."""
    created = 0
    for doc in documents:
        source_id = doc["id"]
        for rel in doc.get("relationships", []):
            target = re.sub(r"[^a-z0-9_]", "_", str(rel["target"]).lower())
            rel_type = str(rel["type"]).strip()
            try:
                db.query(
                    f"RELATE {table_name}:{source_id}->{rel_type}->{table_name}:{target} "
                    f"CONTENT {{ created_at: time::now(), source: 'superoptix_seed' }};",
                )
                created += 1
            except Exception as e:
                print(
                    f"   Warning: RELATE {source_id}->{rel_type}->{target} failed: {e}"
                )
    return created


def seed_surrealdb_graph(
    *,
    vector_store: dict[str, Any],
    documents: list[dict[str, Any]],
    replace_existing: bool = True,
) -> dict[str, int]:
    """Seed graph-enabled documents with entity nodes and RELATE edges.

    Returns dict with 'nodes' and 'edges' counts.
    """
    try:
        from sentence_transformers import SentenceTransformer
        from surrealdb import Surreal
    except ImportError as exc:
        raise ImportError(
            "Required packages missing. Install with: pip install surrealdb sentence-transformers"
        ) from exc

    from superoptix.utils.surrealdb_features import SurrealDBFeatureDetector

    url = str(vector_store["url"])
    namespace = str(vector_store["namespace"])
    database = str(vector_store["database"])
    username = str(vector_store["username"])
    password = str(vector_store["password"])
    skip_signin = bool(vector_store.get("skip_signin", False))
    table_name = str(vector_store["table_name"])
    vector_field = str(vector_store["vector_field"])
    content_field = str(vector_store["content_field"])
    metadata_field = str(vector_store["metadata_field"])
    embedding_model = str(vector_store["embedding_model"])

    model = SentenceTransformer(embedding_model)

    with Surreal(url) as db:
        if not skip_signin:
            db.signin({"username": username, "password": password})
        db.use(namespace, database)

        # Capability gate: check if RELATE is supported
        detector = SurrealDBFeatureDetector(db)
        if not detector.has("relate"):
            print("   Warning: SurrealDB server does not support RELATE.")
            print("   Graph edges will be skipped. Seeding nodes only (flat mode).")

        # Define indexes (best-effort)
        _define_indexes(db, table_name, vector_field, content_field)

        # Clean existing graph seed docs
        if replace_existing:
            db.query(
                f"DELETE {table_name} WHERE {metadata_field}.source = $source;",
                {"source": "superoptix_surreal_seed_v1"},
            )
            # Also clean edge tables for known relation types
            rel_types = set()
            for doc in documents:
                for rel in doc.get("relationships", []):
                    rel_types.add(str(rel["type"]).strip())
            for rt in rel_types:
                try:
                    db.query(f"DELETE {rt} WHERE source = 'superoptix_seed';")
                except Exception:
                    pass  # Edge table may not exist yet

        # Rollout order: indexes (done above) -> nodes -> edges
        nodes = _seed_graph_nodes(
            db,
            documents,
            table_name,
            vector_field,
            content_field,
            metadata_field,
            model,
        )
        edges = 0
        if detector.has("relate"):
            edges = _seed_graph_relations(db, documents, table_name)
        else:
            print("   Skipping RELATE edges (not supported by server).")

    return {"nodes": nodes, "edges": edges}


def load_surreal_vector_store(playbook_path: Path) -> dict[str, Any]:
    with playbook_path.open("r", encoding="utf-8") as handle:
        playbook = yaml.safe_load(handle) or {}
    spec = playbook.get("spec", {}) or {}
    rag = spec.get("rag", {}) or {}
    retriever_type = str(rag.get("retriever_type", "")).strip().lower()
    if retriever_type not in {"surrealdb", "turboagents-surrealdb"}:
        raise ValueError(
            f"Playbook {playbook_path} is not configured with retriever_type: surrealdb or turboagents-surrealdb"
        )
    vector_store = dict(rag.get("vector_store", {}) or {})
    if not vector_store:
        raise ValueError(f"Playbook {playbook_path} is missing spec.rag.vector_store")

    url = _normalize_surrealdb_url(str(vector_store.get("url", "ws://localhost:8000")))
    vector_store["url"] = url
    if "skip_signin" not in vector_store:
        vector_store["skip_signin"] = _default_skip_signin(url)
    vector_store.setdefault("namespace", "test")
    vector_store.setdefault("database", "test")
    vector_store.setdefault("username", "root")
    vector_store.setdefault("password", "root")
    vector_store.setdefault("table_name", "rag_documents")
    vector_store.setdefault("vector_field", "embedding")
    vector_store.setdefault("content_field", "content")
    vector_store.setdefault("metadata_field", "metadata")
    vector_store.setdefault("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
    return vector_store


def seed_surrealdb_documents(
    *,
    vector_store: dict[str, Any],
    documents: list[dict[str, Any]],
    replace_existing_seed_docs: bool = True,
) -> int:
    try:
        from sentence_transformers import SentenceTransformer
        from surrealdb import Surreal
    except ImportError as exc:
        raise ImportError(
            "Required packages missing. Install with: pip install surrealdb sentence-transformers"
        ) from exc

    url = str(vector_store["url"])
    namespace = str(vector_store["namespace"])
    database = str(vector_store["database"])
    username = str(vector_store["username"])
    password = str(vector_store["password"])
    skip_signin = bool(vector_store.get("skip_signin", False))
    table_name = str(vector_store["table_name"])
    vector_field = str(vector_store["vector_field"])
    content_field = str(vector_store["content_field"])
    metadata_field = str(vector_store["metadata_field"])
    embedding_model = str(vector_store["embedding_model"])

    model = SentenceTransformer(embedding_model)
    inserted = 0

    with Surreal(url) as db:
        if not skip_signin:
            db.signin({"username": username, "password": password})
        db.use(namespace, database)

        if replace_existing_seed_docs:
            db.query(
                f"DELETE {table_name} WHERE {metadata_field}.source = $source;",
                {"source": "superoptix_surreal_seed_v1"},
            )

        for doc in documents:
            embedding = model.encode(doc["content"]).tolist()
            payload = {
                content_field: doc["content"],
                vector_field: embedding,
                metadata_field: doc["metadata"],
            }
            db.create(table_name, payload)
            inserted += 1

    return inserted


def parse_args() -> argparse.Namespace:
    default_playbook = _script_dir() / "rag_surrealdb_openai_demo_playbook.yaml"
    default_dataset = _script_dir() / "surrealdb_seed_dataset.jsonl"
    default_graph_dataset = _script_dir() / "surrealdb_graph_seed_dataset.jsonl"

    parser = argparse.ArgumentParser(
        description="Seed SurrealDB documents for SuperOptiX RAG demos."
    )
    parser.add_argument(
        "--playbook",
        type=Path,
        default=default_playbook,
        help=f"Path to a SurrealDB demo playbook (default: {default_playbook})",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset,
        help=f"Path to JSONL seed dataset (default: {default_dataset})",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append seed docs instead of replacing prior seed docs.",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Also seed graph entities with RELATE edges for GraphRAG.",
    )
    parser.add_argument(
        "--graph-dataset",
        type=Path,
        default=default_graph_dataset,
        help=f"Path to graph JSONL seed dataset (default: {default_graph_dataset})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    playbook_path = args.playbook.expanduser().resolve()
    dataset_path = args.dataset.expanduser().resolve()

    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found: {playbook_path}")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    vector_store = load_surreal_vector_store(playbook_path)
    documents = load_seed_documents(dataset_path)

    inserted = seed_surrealdb_documents(
        vector_store=vector_store,
        documents=documents,
        replace_existing_seed_docs=not args.append,
    )

    print("SurrealDB seed complete")
    print(f"   Playbook: {playbook_path}")
    print(f"   Dataset:  {dataset_path}")
    print(f"   URL:      {vector_store['url']}")
    print(f"   Table:    {vector_store['table_name']}")
    print(f"   Inserted: {inserted}")

    # Graph seeding (optional)
    if args.graph:
        graph_dataset_path = args.graph_dataset.expanduser().resolve()
        if not graph_dataset_path.exists():
            raise FileNotFoundError(f"Graph dataset not found: {graph_dataset_path}")

        graph_docs = load_graph_seed_documents(graph_dataset_path)
        _validate_graph_dataset(graph_docs)

        result = seed_surrealdb_graph(
            vector_store=vector_store,
            documents=graph_docs,
            replace_existing=not args.append,
        )
        print(f"\n   GraphRAG seeding:")
        print(f"   Graph dataset: {graph_dataset_path}")
        print(f"   Nodes created: {result['nodes']}")
        print(f"   Edges created: {result['edges']}")

    print("")
    print("Try:")
    print(
        '  super agent run rag_surrealdb_openai_demo --framework openai --goal "What is NEON-FOX-742?"'
    )
    if args.graph:
        print(
            '  super agent run graphrag_surrealdb_openai_demo --framework openai --goal "What capabilities does SurrealDB provide?"'
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
