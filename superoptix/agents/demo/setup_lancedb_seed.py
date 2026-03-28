#!/usr/bin/env python3
"""
Seed LanceDB demo documents for SuperOptiX RAG examples.

Minimal usage:
  python superoptix/agents/demo/setup_lancedb_seed.py

By default this uses:
  - playbook: superoptix/agents/demo/rag_lancedb_demo_playbook.yaml
  - dataset:  superoptix/agents/demo/lancedb_seed_dataset.jsonl
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from superoptix.core.rag_mixin import RAGMixin


class _Harness(RAGMixin):
    pass


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_seed_documents(dataset_path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
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
            metadata.setdefault("source", "superoptix_lancedb_seed_v1")
            documents.append({"id": doc_id, "content": content, "metadata": metadata})
    if not documents:
        raise ValueError(f"No seed documents found in {dataset_path}")
    return documents


def load_playbook_spec(playbook_path: Path) -> dict[str, Any]:
    with playbook_path.open("r", encoding="utf-8") as handle:
        playbook = yaml.safe_load(handle) or {}
    spec = playbook.get("spec", {}) or {}
    rag = spec.get("rag", {}) or {}
    retriever_type = str(rag.get("retriever_type", "")).strip().lower()
    if retriever_type not in {"lancedb", "turboagents-lancedb"}:
        raise ValueError(
            f"Playbook {playbook_path} is not configured with retriever_type: "
            "lancedb or turboagents-lancedb"
        )
    return spec


def parse_args() -> argparse.Namespace:
    default_playbook = _script_dir() / "rag_lancedb_demo_playbook.yaml"
    default_dataset = _script_dir() / "lancedb_seed_dataset.jsonl"

    parser = argparse.ArgumentParser(
        description="Seed LanceDB documents for SuperOptiX RAG demos."
    )
    parser.add_argument(
        "--playbook",
        type=Path,
        default=default_playbook,
        help=f"Path to a LanceDB demo playbook (default: {default_playbook})",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset,
        help=f"Path to JSONL seed dataset (default: {default_dataset})",
    )
    return parser.parse_args()


def _reset_local_lancedb_store(uri: str) -> None:
    parsed = urlparse(uri)
    if parsed.scheme and parsed.scheme not in {"file"}:
        return
    target = Path(parsed.path if parsed.scheme == "file" else uri).expanduser()
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    if target.exists():
        shutil.rmtree(target)


def main() -> int:
    args = parse_args()
    playbook_path = args.playbook.expanduser().resolve()
    dataset_path = args.dataset.expanduser().resolve()

    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found: {playbook_path}")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    spec = load_playbook_spec(playbook_path)
    documents = load_seed_documents(dataset_path)

    harness = _Harness()
    vector_store = (spec.get("rag", {}) or {}).get("vector_store", {}) or {}
    uri = str(
        vector_store.get("uri", vector_store.get("database_path", "./data/lancedb"))
    )
    _reset_local_lancedb_store(uri)
    if not harness.setup_rag(spec):
        raise RuntimeError(f"Failed to set up RAG for {playbook_path}")
    if not harness.add_documents(documents):
        raise RuntimeError(f"Failed to seed LanceDB documents for {playbook_path}")

    print("LanceDB seed complete")
    print(f"   Playbook: {playbook_path}")
    print(f"   Dataset:  {dataset_path}")
    print(
        f"   URI:      {vector_store.get('uri', vector_store.get('database_path', './data/lancedb'))}"
    )
    print(f"   Table:    {vector_store.get('table_name', 'documents')}")
    print(f"   Inserted: {len(documents)}")
    print("")
    print("Try:")
    print('  super agent run rag_lancedb_demo --goal "What is LANCE-TURBO-314?"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
