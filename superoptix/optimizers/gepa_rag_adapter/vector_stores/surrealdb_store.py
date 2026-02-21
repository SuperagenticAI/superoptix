# Copyright (c) 2025 Lakshya A Agrawal and the GEPA contributors
# https://github.com/gepa-ai/gepa

from typing import Any

from ..vector_store_interface import VectorStoreInterface


class SurrealDBVectorStore(VectorStoreInterface):
    """
    SurrealDB implementation of the VectorStoreInterface.

    This store uses SurrealQL vector similarity functions for retrieval.
    SurrealDB server setup, authentication, and record ingestion are expected to be
    handled by the caller.
    """

    def __init__(
        self,
        client,
        table_name: str,
        embedding_function=None,
        content_field: str = "content",
        vector_field: str = "embedding",
        metadata_field: str = "metadata",
    ):
        import importlib.util
        import re

        if importlib.util.find_spec("surrealdb") is None:
            raise ImportError(
                "SurrealDB client is required for SurrealDBVectorStore. Install with: pip install litellm surrealdb"
            )

        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            raise ValueError(
                "Invalid table name. Use letters, numbers, and underscores only."
            )

        self.client = client
        self.table_name = table_name
        self.embedding_function = embedding_function
        self.content_field = content_field
        self.vector_field = vector_field
        self.metadata_field = metadata_field

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search using text query by embedding it first."""
        if self.embedding_function is None:
            raise ValueError("No embedding function provided for similarity search")

        query_vector = self.embedding_function(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()

        return self.vector_search(query_vector, k=k, filters=filters)

    def vector_search(
        self,
        query_vector: list[float],
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search using a pre-computed query embedding vector."""
        where_clause, params = self._build_where_clause(filters)
        params["query_vector"] = query_vector
        params["limit"] = int(k)

        query = f"""
        SELECT *,
               vector::similarity::cosine({self.vector_field}, $query_vector) AS score
        FROM {self.table_name}
        WHERE {self.vector_field} != NONE{where_clause}
        ORDER BY score DESC
        LIMIT $limit;
        """
        rows = self._execute_query(query, params)
        return self._format_results(rows)

    def get_collection_info(self) -> dict[str, Any]:
        """Get metadata and basic statistics for the SurrealDB table."""
        count_query = f"SELECT count() AS count FROM {self.table_name} GROUP ALL;"
        dim_query = f"""
        SELECT array::len({self.vector_field}) AS dimension
        FROM {self.table_name}
        WHERE {self.vector_field} != NONE
        LIMIT 1;
        """

        count_rows = self._execute_query(count_query, {})
        dim_rows = self._execute_query(dim_query, {})

        document_count = 0
        dimension = 0

        if count_rows and isinstance(count_rows[0], dict):
            raw_count = count_rows[0].get("count", 0)
            if isinstance(raw_count, int | float):
                document_count = int(raw_count)

        if dim_rows and isinstance(dim_rows[0], dict):
            raw_dim = dim_rows[0].get("dimension", 0)
            if isinstance(raw_dim, int | float):
                dimension = int(raw_dim)

        return {
            "name": self.table_name,
            "document_count": document_count,
            "dimension": dimension,
            "vector_store_type": "surrealdb",
        }

    def supports_hybrid_search(self) -> bool:
        """SurrealDB supports hybrid retrieval with combined scoring."""
        return True

    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Hybrid search combining vector similarity and lexical matching.

        Uses:
        - vector::similarity::cosine() for semantic relevance
        - search::score() for full-text relevance
        """
        if self.embedding_function is None:
            return self.similarity_search(query, k=k, filters=filters)

        query_vector = self.embedding_function(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()

        where_clause, params = self._build_where_clause(filters)
        params["query"] = query
        params["query_vector"] = query_vector
        params["alpha"] = float(alpha)
        params["beta"] = float(1.0 - alpha)
        params["limit"] = int(k)

        query_sql = f"""
        SELECT *,
               vector::similarity::cosine({self.vector_field}, $query_vector) AS vector_score,
               search::score() AS lexical_score,
               (($alpha * vector::similarity::cosine({self.vector_field}, $query_vector))
                 + ($beta * search::score())) AS score
        FROM {self.table_name}
        WHERE {self.vector_field} != NONE AND {self.content_field} @0@ $query{where_clause}
        ORDER BY score DESC
        LIMIT $limit;
        """

        rows = self._execute_query(query_sql, params)
        return self._format_results(rows)

    def _build_where_clause(
        self, filters: dict[str, Any] | None
    ) -> tuple[str, dict[str, Any]]:
        """Build safe WHERE fragments and parameter mapping."""
        import re

        if not filters:
            return "", {}

        clauses: list[str] = []
        params: dict[str, Any] = {}
        idx = 0

        for key, value in filters.items():
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                continue

            param_name = f"f_{idx}"
            if isinstance(value, dict):
                for op, op_value in value.items():
                    op_param_name = f"{param_name}_{op.strip('$')}"
                    if op in {"$eq", "eq"}:
                        clauses.append(f"{key} = ${op_param_name}")
                    elif op in {"$ne", "ne"}:
                        clauses.append(f"{key} != ${op_param_name}")
                    elif op in {"$gt", "gt"}:
                        clauses.append(f"{key} > ${op_param_name}")
                    elif op in {"$gte", "gte"}:
                        clauses.append(f"{key} >= ${op_param_name}")
                    elif op in {"$lt", "lt"}:
                        clauses.append(f"{key} < ${op_param_name}")
                    elif op in {"$lte", "lte"}:
                        clauses.append(f"{key} <= ${op_param_name}")
                    else:
                        continue
                    params[op_param_name] = op_value
            else:
                clauses.append(f"{key} = ${param_name}")
                params[param_name] = value

            idx += 1

        if not clauses:
            return "", params
        return f" AND {' AND '.join(clauses)}", params

    def _execute_query(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Execute query and normalize results from query/query_raw methods.
        """
        # query_raw usually returns {"result": [{"result": [...]}]}
        if hasattr(self.client, "query_raw"):
            raw = self.client.query_raw(query, params)
            if isinstance(raw, dict):
                result = raw.get("result", [])
                if result and isinstance(result, list) and isinstance(result[0], dict):
                    rows = result[0].get("result", [])
                    if isinstance(rows, list):
                        return rows

        # query usually returns the first statement result directly
        if hasattr(self.client, "query"):
            raw = self.client.query(query, params)
            if isinstance(raw, list):
                return [row for row in raw if isinstance(row, dict)]
            if isinstance(raw, dict):
                return [raw]

        return []

    def _format_results(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert SurrealDB records into the standardized adapter output format."""
        documents: list[dict[str, Any]] = []

        for row in rows:
            content = str(row.get(self.content_field, ""))
            metadata = row.get(self.metadata_field, {})
            if not isinstance(metadata, dict):
                metadata = {"metadata": metadata}

            row_id = row.get("id")
            if row_id is not None:
                metadata["doc_id"] = str(row_id)

            score = row.get("score", 0.0)
            if isinstance(score, int | float):
                score_value = float(score)
            else:
                score_value = 0.0

            documents.append(
                {
                    "content": content,
                    "metadata": metadata,
                    "score": score_value,
                }
            )

        return documents
