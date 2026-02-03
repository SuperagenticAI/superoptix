# RAG Optimization Tutorial

Learn how to optimize Retrieval-Augmented Generation (RAG) systems using SuperOptiX's advanced techniques and GEPA optimization.

## Overview

This tutorial covers:
- Setting up RAG systems with multiple vector databases
- Optimizing retrieval parameters
- Improving context relevance with GEPA
- Performance monitoring and evaluation

## Prerequisites

### Install SuperOptiX

```bash
pip install superoptix
```

**For vector database support:**
```bash
pip install superoptix[vectordb]
```

**Includes:**
- SuperOptiX core with GEPA 0.0.17
- GenericRAGAdapter for RAG optimization
- All vector databases (ChromaDB, LanceDB, Weaviate, Qdrant, Milvus)

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)
- Basic understanding of RAG concepts

## Step 1: Initialize RAG Project

```bash
# Create new project
super init rag_optimization_project
cd rag_optimization_project

# Pull RAG demo agent
super agent pull rag_chroma_demo
```

## Step 2: Configure Vector Database

Choose your vector database:

=== "ChromaDB"
    ```yaml
    # agents/rag_chroma_demo.yaml
    spec:
      rag:
        enabled: true
        backend: chromadb
        config:
          collection_name: "superoptix_docs"
          persist_directory: "./chroma_db"
          embedding_model: "all-MiniLM-L6-v2"
          chunk_size: 512
          chunk_overlap: 50
          top_k: 5
    ```

=== "LanceDB"
    ```yaml
    spec:
      rag:
        enabled: true
        backend: lancedb
        config:
          table_name: "documents"
          uri: "./lancedb"
          embedding_model: "all-MiniLM-L6-v2"
          chunk_size: 512
          chunk_overlap: 50
          top_k: 5
    ```

=== "Weaviate"
    ```yaml
    spec:
      rag:
        enabled: true
        backend: weaviate
        config:
          url: "http://localhost:8080"
          class_name: "Document"
          embedding_model: "all-MiniLM-L6-v2"
          chunk_size: 512
          chunk_overlap: 50
          top_k: 5
    ```

=== "Qdrant"
    ```yaml
    spec:
      rag:
        enabled: true
        backend: qdrant
        config:
          url: "http://localhost:6333"
          collection_name: "documents"
          embedding_model: "all-MiniLM-L6-v2"
          chunk_size: 512
          chunk_overlap: 50
          top_k: 5
    ```

=== "Milvus"
    ```yaml
    spec:
      rag:
        enabled: true
        backend: milvus
        config:
          host: "localhost"
          port: 19530
          collection_name: "documents"
          embedding_model: "all-MiniLM-L6-v2"
          chunk_size: 512
          chunk_overlap: 50
          top_k: 5
    ```

## Step 3: Prepare Your Documents

```bash
# Create documents directory
mkdir -p documents

# Add your documents
cp /path/to/your/docs/*.pdf documents/
cp /path/to/your/docs/*.txt documents/
cp /path/to/your/docs/*.md documents/

# Or use sample documents
echo "SuperOptiX is a full-stack agentic AI optimization framework." > documents/intro.txt
echo "GEPA is the universal optimizer that works across all frameworks." > documents/gepa.txt
echo "RAG systems improve AI responses with relevant context." > documents/rag.txt
```

## Step 4: Compile and Test RAG Agent

```bash
# Compile the RAG agent
super agent compile rag_chroma_demo

# Test with sample query
super agent run rag_chroma_demo --goal "What is SuperOptiX?"
```

Expected output:
```
Response: SuperOptiX is a full-stack agentic AI optimization framework that provides comprehensive tools for building, optimizing, and deploying AI agents across multiple frameworks.
```

## Step 5: Evaluate RAG Performance

```bash
# Run evaluation
super agent evaluate rag_chroma_demo
```

This will test:
- Retrieval accuracy
- Response relevance
- Context utilization
- Response quality

## Step 6: Optimize RAG Parameters

### 6.1 Chunk Size Optimization

```yaml
# Test different chunk sizes
spec:
  rag:
    config:
      chunk_size: 256    # Smaller chunks for precise retrieval
      chunk_overlap: 25
      top_k: 5
```

```bash
super agent compile rag_chroma_demo
super agent evaluate rag_chroma_demo
```

### 6.2 Top-K Optimization

```yaml
# Test different top_k values
spec:
  rag:
    config:
      chunk_size: 512
      chunk_overlap: 50
      top_k: 3    # Fewer results for focused context
```

```bash
super agent compile rag_chroma_demo
super agent evaluate rag_chroma_demo
```

### 6.3 Embedding Model Optimization

```yaml
# Test different embedding models
spec:
  rag:
    config:
      embedding_model: "sentence-transformers/all-mpnet-base-v2"  # Better quality
      chunk_size: 512
      chunk_overlap: 50
      top_k: 5
```

## Step 7: GEPA Optimization for RAG

Optimize the RAG system using GEPA:

```bash
# Optimize with GEPA
super agent optimize rag_chroma_demo --auto medium

# Evaluate optimized version
super agent evaluate rag_chroma_demo  # automatically loads optimized weights
```

GEPA will optimize:
- Retrieval parameters
- Context selection
- Response generation
- Relevance scoring

## Step 8: Advanced RAG Techniques

### 8.1 Hybrid Search

```yaml
spec:
  rag:
    config:
      search_type: "hybrid"  # Combines semantic + keyword search
      semantic_weight: 0.7
      keyword_weight: 0.3
      chunk_size: 512
      top_k: 5
```

### 8.2 Query Expansion

```yaml
spec:
  rag:
    config:
      query_expansion: true
      expansion_model: "gpt-3.5-turbo"
      max_expansions: 3
      chunk_size: 512
      top_k: 5
```

### 8.3 Context Re-ranking

```yaml
spec:
  rag:
    config:
      rerank: true
      rerank_model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
      rerank_top_k: 10
      final_top_k: 5
```

## Step 9: Performance Monitoring

### 9.1 Set Up Observability

```bash
# Enable MLFlow tracking
super agent compile rag_chroma_demo --observability mlflow

# Enable LangFuse tracing
super agent compile rag_chroma_demo --observability langfuse
```

### 9.2 Monitor Metrics

```bash
# Run with monitoring
super agent run rag_chroma_demo --goal "What is GEPA?" --monitor

# View metrics
super observe metrics rag_chroma_demo
```

Key metrics to monitor:
- **Retrieval Accuracy**: How relevant are retrieved chunks?
- **Response Quality**: How good are the generated responses?
- **Latency**: How fast is the RAG system?
- **Token Usage**: How many tokens are consumed?

## Step 10: Production Deployment

### 10.1 Optimize for Production

```bash
# Final optimization
super agent optimize rag_chroma_demo --auto intensive

# Build production version
super agent compile rag_chroma_demo --production
```

### 10.2 Deploy with Orchestra

```bash
# Create orchestra for RAG system
super orchestra create rag_orchestra

# Add RAG agent to orchestra
super orchestra add-agent rag_chroma_demo

# Run orchestra
super orchestra run rag_orchestra
```

## Best Practices

### Document Preparation
- **Clean your documents**: Remove headers, footers, and irrelevant content
- **Consistent formatting**: Use consistent structure across documents
- **Metadata inclusion**: Add relevant metadata to documents

### Chunking Strategy
- **Optimal chunk size**: 256-512 tokens for most use cases
- **Overlap**: 10-20% overlap between chunks
- **Semantic boundaries**: Split at sentence or paragraph boundaries

### Retrieval Optimization
- **Top-K tuning**: Start with 5-10, adjust based on performance
- **Embedding models**: Use domain-specific models when available
- **Hybrid search**: Combine semantic and keyword search for better results

### Evaluation Metrics
- **Relevance**: How relevant are retrieved chunks?
- **Accuracy**: How accurate are the responses?
- **Completeness**: Do responses cover all aspects of the query?
- **Consistency**: Are responses consistent across similar queries?

## Troubleshooting

### Common Issues

**Low Retrieval Accuracy**
```bash
# Try different chunk sizes
super agent compile rag_chroma_demo --chunk-size 256

# Try different embedding models
super agent compile rag_chroma_demo --embedding-model "all-mpnet-base-v2"
```

**Slow Performance**
```bash
# Reduce top_k
super agent compile rag_chroma_demo --top-k 3

# Use faster embedding model
super agent compile rag_chroma_demo --embedding-model "all-MiniLM-L6-v2"
```

**Irrelevant Context**
```bash
# Enable query expansion
super agent compile rag_chroma_demo --goal-expansion

# Use hybrid search
super agent compile rag_chroma_demo --search-type hybrid
```

## Next Steps

- [MCP Optimization Tutorial](mcp-optimization.md)
- [Memory Optimization Guide](../guides/memory-context-optimization.md)
- [Advanced RAG Techniques](../guides/rag.md)
- [Observability Setup](../guides/observability.md)

## Resources

- [RAG Best Practices](https://docs.superoptix.ai/guides/rag)
- [Vector Database Comparison](../guides/multi-framework.md)
- [GEPA Optimization Guide](../guides/gepa-optimization.md)
- [Community Discord](https://Documentation: https://superagenticai.github.io/superoptix-ai/)
