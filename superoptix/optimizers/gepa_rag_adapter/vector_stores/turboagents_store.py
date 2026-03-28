# Copyright (c) 2025 Lakshya A Agrawal and the GEPA contributors
# https://github.com/gepa-ai/gepa

from __future__ import annotations

import asyncio
import importlib.util
from typing import Any

import numpy as np

from ..vector_store_interface import VectorStoreInterface


def _turboagents_available() -> bool:
    return importlib.util.find_spec("turboagents") is not None


def _coerce_metadata(value: Any, *, fallback_id: str | None = None) -> tuple[str, dict[str, Any]]:
    if isinstance(value, dict):
        content = str(value.get("content") or value.get("text") or "")
        metadata = dict(value.get("metadata", value))
    else:
        content = "" if value is None else str(value)
        metadata = {"value": value}

    if fallback_id is not None:
        metadata.setdefault("doc_id", fallback_id)
    return content, metadata


class _TurboAgentsBaseStore(VectorStoreInterface):
    def __init__(self, *, embedding_function=None, rerank_top: int | None = None):
        if not _turboagents_available():
            raise ImportError(
                "turboagents is required for TurboAgents-backed vector stores. "
                "Install with: pip install 'turboagents[rag]'"
            )
        self.embedding_function = embedding_function
        self.rerank_top = rerank_top
        self._doc_count = 0

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if self.embedding_function is None:
            raise ValueError("No embedding function provided for similarity search")
        query_vector = self.embedding_function(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()
        return self.vector_search(list(query_vector), k=k, filters=filters)

    def _format_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        for result in results:
            index = result.get("index")
            content, metadata = _coerce_metadata(
                result.get("metadata"), fallback_id=str(index) if index is not None else None
            )
            formatted.append(
                {
                    "content": content,
                    "metadata": metadata,
                    "score": float(result.get("score", 0.0)),
                }
            )
        return formatted

    def get_collection_info(self) -> dict[str, Any]:
        return {
            "name": getattr(self, "name", "turboagents"),
            "document_count": self._doc_count,
            "dimension": getattr(self, "dim", 0),
            "vector_store_type": getattr(self, "vector_store_type", "turboagents"),
        }


class TurboChromaVectorStore(_TurboAgentsBaseStore):
    """SuperOptiX GEPA wrapper over turboagents TurboChroma."""

    vector_store_type = "turboagents-chroma"

    def __init__(
        self,
        *,
        path: str | None,
        collection_name: str,
        dim: int,
        bits: float = 3.5,
        seed: int = 0,
        embedding_function=None,
        rerank_top: int | None = None,
        metric: str = "cosine",
    ):
        super().__init__(embedding_function=embedding_function, rerank_top=rerank_top)
        from turboagents.rag import TurboChroma

        self.dim = dim
        self.name = collection_name
        self._collection_ready = False
        self._store = TurboChroma(
            path=path,
            collection_name=collection_name,
            dim=dim,
            bits=bits,
            seed=seed,
            metric=metric,
        )
        self._collection_name = collection_name

    def add_documents(
        self,
        documents: list[dict[str, Any]],
        embeddings: list[list[float]],
        ids: list[str] | None = None,
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        resolved_ids = ids or [f"doc_{self._doc_count + i}" for i in range(len(documents))]
        metadata = []
        for doc_id, doc in zip(resolved_ids, documents, strict=False):
            content, doc_metadata = _coerce_metadata(doc, fallback_id=doc_id)
            doc_metadata.setdefault("content", content)
            metadata.append(doc_metadata)
        if not self._collection_ready:
            self._store.create_collection(self._collection_name)
            self._collection_ready = True
        self._store.add(np.asarray(embeddings, dtype=np.float32), metadata=metadata)
        self._doc_count += len(documents)
        return resolved_ids

    def vector_search(
        self,
        query_vector: list[float],
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if filters:
            raise NotImplementedError("TurboChromaVectorStore does not support metadata filtering yet")
        results = self._store.search(
            np.asarray(query_vector, dtype=np.float32),
            k=k,
            rerank_top=self.rerank_top,
        )
        return self._format_results(results)


class TurboFAISSVectorStore(_TurboAgentsBaseStore):
    """SuperOptiX GEPA wrapper over turboagents TurboFAISS."""

    vector_store_type = "turboagents-faiss"

    def __init__(
        self,
        *,
        dim: int,
        bits: float = 3.5,
        seed: int = 0,
        embedding_function=None,
        rerank_top: int | None = None,
    ):
        super().__init__(embedding_function=embedding_function, rerank_top=rerank_top)
        from turboagents.rag import TurboFAISS

        self.dim = dim
        self.name = "turboagents_faiss"
        self._store = TurboFAISS(dim=dim, bits=bits, seed=seed)

    def add_documents(
        self,
        documents: list[dict[str, Any]],
        embeddings: list[list[float]],
        ids: list[str] | None = None,
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        resolved_ids = ids or [f"doc_{self._doc_count + i}" for i in range(len(documents))]
        metadata = []
        for doc_id, doc in zip(resolved_ids, documents, strict=False):
            content, doc_metadata = _coerce_metadata(doc, fallback_id=doc_id)
            doc_metadata.setdefault("content", content)
            metadata.append(doc_metadata)
        self._store.add(np.asarray(embeddings, dtype=np.float32), metadata=metadata)
        self._doc_count += len(documents)
        return resolved_ids

    def vector_search(
        self,
        query_vector: list[float],
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if filters:
            raise NotImplementedError("TurboFAISSVectorStore does not support metadata filtering yet")
        results = self._store.search(
            np.asarray(query_vector, dtype=np.float32),
            k=k,
            rerank_top=self.rerank_top,
        )
        return self._format_results(results)


class TurboLanceDBVectorStore(_TurboAgentsBaseStore):
    """SuperOptiX GEPA wrapper over turboagents TurboLanceDB."""

    vector_store_type = "turboagents-lancedb"

    def __init__(
        self,
        *,
        uri: str,
        table_name: str,
        dim: int,
        bits: float = 3.5,
        seed: int = 0,
        embedding_function=None,
        rerank_top: int | None = None,
        metric: str = "dot",
    ):
        super().__init__(embedding_function=embedding_function, rerank_top=rerank_top)
        from turboagents.rag import TurboLanceDB

        self.dim = dim
        self.name = table_name
        self._table_ready = False
        self._store = TurboLanceDB(
            uri,
            dim=dim,
            bits=bits,
            seed=seed,
            metric=metric,
        )
        self._table_name = table_name

    def add_documents(
        self,
        documents: list[dict[str, Any]],
        embeddings: list[list[float]],
        ids: list[str] | None = None,
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        resolved_ids = ids or [f"doc_{self._doc_count + i}" for i in range(len(documents))]
        metadata = []
        for doc_id, doc in zip(resolved_ids, documents, strict=False):
            content, doc_metadata = _coerce_metadata(doc, fallback_id=doc_id)
            doc_metadata.setdefault("content", content)
            metadata.append(doc_metadata)
        embedding_array = np.asarray(embeddings, dtype=np.float32)
        if not self._table_ready:
            self._store.create_table(self._table_name, embedding_array, metadata=metadata)
            self._table_ready = True
        else:
            self._store.add(embedding_array, metadata=metadata)
        self._doc_count += len(documents)
        return resolved_ids

    def vector_search(
        self,
        query_vector: list[float],
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if filters:
            raise NotImplementedError("TurboLanceDBVectorStore does not support metadata filtering yet")
        results = self._store.search(
            np.asarray(query_vector, dtype=np.float32),
            k=k,
            rerank_top=self.rerank_top,
        )
        return self._format_results(results)


class TurboSurrealDBVectorStore(_TurboAgentsBaseStore):
    """SuperOptiX GEPA wrapper over turboagents TurboSurrealDB."""

    vector_store_type = "turboagents-surrealdb"

    def __init__(
        self,
        *,
        url: str,
        namespace: str,
        database: str,
        table_name: str,
        dim: int,
        bits: float = 3.5,
        seed: int = 0,
        embedding_function=None,
        rerank_top: int | None = None,
        metric: str = "COSINE",
        auth: dict[str, Any] | None = None,
    ):
        super().__init__(embedding_function=embedding_function, rerank_top=rerank_top)
        from turboagents.rag import TurboSurrealDB

        self.dim = dim
        self.name = table_name
        self._collection_ready = False
        self._store = TurboSurrealDB(
            url=url,
            namespace=namespace,
            database=database,
            dim=dim,
            bits=bits,
            seed=seed,
            metric=metric,
            auth=auth,
        )
        self._table_name = table_name

    @staticmethod
    def _run(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        raise RuntimeError(
            "TurboSurrealDBVectorStore cannot run inside an active event loop. "
            "Use the async turboagents adapter directly for async workflows."
        )

    def add_documents(
        self,
        documents: list[dict[str, Any]],
        embeddings: list[list[float]],
        ids: list[str] | None = None,
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        resolved_ids = ids or [f"doc_{self._doc_count + i}" for i in range(len(documents))]
        metadata = []
        for doc_id, doc in zip(resolved_ids, documents, strict=False):
            content, doc_metadata = _coerce_metadata(doc, fallback_id=doc_id)
            doc_metadata.setdefault("content", content)
            metadata.append(doc_metadata)
        if not self._collection_ready:
            self._run(self._store.create_collection(self._table_name))
            self._collection_ready = True
        self._run(self._store.add(np.asarray(embeddings, dtype=np.float32), metadata=metadata))
        self._doc_count += len(documents)
        return resolved_ids

    def vector_search(
        self,
        query_vector: list[float],
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if filters:
            raise NotImplementedError("TurboSurrealDBVectorStore does not support metadata filtering yet")
        results = self._run(
            self._store.search(
                np.asarray(query_vector, dtype=np.float32),
                k=k,
                rerank_top=self.rerank_top,
            )
        )
        return self._format_results(results)
