from __future__ import annotations

from pathlib import Path

import yaml

from superoptix.agents.demo.setup_surrealdb_seed import (
    load_seed_documents,
    load_surreal_vector_store,
)


def test_load_seed_documents_parses_jsonl(tmp_path: Path):
    dataset = tmp_path / "seed.jsonl"
    dataset.write_text(
        "\n".join(
            [
                '{"id":"a1","content":"hello","metadata":{"topic":"x"}}',
                '{"content":"world"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    docs = load_seed_documents(dataset)

    assert len(docs) == 2
    assert docs[0]["id"] == "a1"
    assert docs[0]["content"] == "hello"
    assert docs[0]["metadata"]["topic"] == "x"
    assert docs[0]["metadata"]["source"] == "superoptix_surreal_seed_v1"
    assert docs[1]["id"] == "seed-002"
    assert docs[1]["metadata"]["seed_id"] == "seed-002"


def test_load_surreal_vector_store_defaults_skip_signin_for_embedded(tmp_path: Path):
    playbook = {
        "spec": {
            "rag": {
                "retriever_type": "surrealdb",
                "vector_store": {
                    "url": "surrealkv://./.superoptix/surreal.db",
                    "namespace": "test",
                    "database": "test",
                },
            }
        }
    }
    playbook_path = tmp_path / "pb.yaml"
    playbook_path.write_text(yaml.safe_dump(playbook), encoding="utf-8")

    cfg = load_surreal_vector_store(playbook_path)

    assert cfg["url"] == "surrealkv://./.superoptix/surreal.db"
    assert cfg["skip_signin"] is True
    assert cfg["table_name"] == "rag_documents"
    assert cfg["vector_field"] == "embedding"
    assert cfg["content_field"] == "content"
    assert cfg["metadata_field"] == "metadata"


def test_load_surreal_vector_store_normalizes_rpc_url(tmp_path: Path):
    playbook = {
        "spec": {
            "rag": {
                "retriever_type": "surrealdb",
                "vector_store": {
                    "url": "ws://localhost:8000/rpc",
                    "namespace": "superoptix",
                    "database": "knowledge",
                    "skip_signin": False,
                },
            }
        }
    }
    playbook_path = tmp_path / "pb_rpc.yaml"
    playbook_path.write_text(yaml.safe_dump(playbook), encoding="utf-8")

    cfg = load_surreal_vector_store(playbook_path)
    assert cfg["url"] == "ws://localhost:8000"
    assert cfg["skip_signin"] is False
