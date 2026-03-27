"""Minimal SuperOptiX + TurboAgents GEPA RAG example."""

from __future__ import annotations

import math

from superoptix.optimizers.gepa_rag_adapter import RAGPipeline, TurboFAISSVectorStore


DIMENSION = 64


def simple_embedding(text: str) -> list[float]:
    buckets = [0.0] * DIMENSION
    for idx, token in enumerate(text.lower().split()):
        bucket = idx % DIMENSION
        buckets[bucket] += (sum(ord(ch) for ch in token) % 97) / 97.0

    norm = math.sqrt(sum(value * value for value in buckets)) or 1.0
    return [value / norm for value in buckets]


def fake_llm(messages: list[dict[str, str]]) -> str:
    user_prompt = messages[-1]["content"]
    if "Question:" in user_prompt and "Context:" in user_prompt:
        context = user_prompt.split("Context:", 1)[1]
        return context.strip().splitlines()[0]
    return "Unable to answer."


def main() -> None:
    vector_store = TurboFAISSVectorStore(
        dim=DIMENSION,
        bits=3.5,
        seed=0,
        embedding_function=simple_embedding,
        rerank_top=8,
    )

    documents = [
        {
            "content": "TurboAgents adds compressed retrieval and reranking under existing AI systems.",
            "metadata": {"source": "intro"},
        },
        {
            "content": "SuperOptiX can optimize RAG pipelines through the GEPA vector store interface.",
            "metadata": {"source": "gepa"},
        },
        {
            "content": "TurboAgents currently validates FAISS, LanceDB, pgvector, and SurrealDB style retrieval paths.",
            "metadata": {"source": "benchmarks"},
        },
    ]
    embeddings = [simple_embedding(doc["content"]) for doc in documents]
    vector_store.add_documents(documents, embeddings)

    pipeline = RAGPipeline(
        vector_store=vector_store,
        llm_client=fake_llm,
        embedding_function=simple_embedding,
    )

    result = pipeline.execute_rag(
        query="How does TurboAgents fit into SuperOptiX RAG?",
        prompts={
            "answer_generation": (
                "Answer using the provided context only.\n\n"
                "Question: {query}\n\nContext:\n{context}"
            )
        },
        config={"retrieval_strategy": "vector", "top_k": 2},
    )

    print("Retrieved documents:")
    for doc in result["retrieved_docs"]:
        print(f"- {doc['content']} ({doc['metadata'].get('source')})")

    print("\nGenerated answer:")
    print(result["generated_answer"])
    print("\nMetadata:")
    print(result["metadata"])


if __name__ == "__main__":
    main()
