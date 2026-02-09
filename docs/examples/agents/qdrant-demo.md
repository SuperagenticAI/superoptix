# Qdrant RAG Demo 🎯

A comprehensive demonstration of SuperOptiX's RAG capabilities using **Qdrant** vector database for high-performance similarity search and intelligent knowledge retrieval.

## Overview

This demo showcases how to integrate **Qdrant** - a blazingly fast vector database - with SuperOptiX's RAG system to create intelligent agents capable of retrieving and synthesizing information from large knowledge bases with exceptional performance.

## This demo demonstrates:

⚡ **Qdrant Vector Database Integration** - Lightning-fast connection to Qdrant for high-performance vector storage

🎯 **Precision Similarity Search** - Intelligent retrieval using Qdrant's optimized similarity algorithms

📊 **Collection Management** - Efficient document storage, indexing, and retrieval workflows

🚀 **Ultra-fast Query Processing** - Exceptional response times with Qdrant's performance optimizations

🔄 **RAG Pipeline Integration** - Complete retrieval-augmented generation workflow

## Prerequisites

### Install SuperOptiX
```bash
pip install superoptix
```

### Install Qdrant Dependencies
```bash
pip install qdrant-client
```

### Set Up Qdrant Server
```bash
# Using Docker (recommended)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

### Install and Serve Model
```bash
# Install a model (if not already installed)
super model install llama3.1:8b

# Start Ollama server (if using Ollama backend)
ollama serve
```

## Quick Start

### Pull the Demo Agent
```bash
super agent pull rag_qdrant_demo
```

### Compile the Agent
```bash
super agent compile rag_qdrant_demo
```

### Run the Demo
```bash
super agent run rag_qdrant_demo --goal "What are the key features of Qdrant and how does it work with SuperOptiX?"
```

## Key Configuration Points:

🔧 **Vector Database Setup** - Configured to connect to Qdrant at `http://localhost:6333`

📊 **Collection Management** - Uses `superoptix_knowledge` collection for document storage

🎯 **Embedding Model** - Leverages `sentence-transformers/all-MiniLM-L6-v2` for vector generation

⚙️ **Search Parameters** - Optimized with `top_k: 5` and `similarity_threshold: 0.7`

## Playbook Configuration

The demo uses a specialized playbook with Qdrant-specific configurations:

```yaml
rag:
  enabled: true
  retriever_type: qdrant
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    url: http://localhost:6333
    collection_name: superoptix_knowledge
```

## Customization

### Modify Qdrant Connection
```yaml
vector_store:
  url: http://your-qdrant-server:6333
  collection_name: YourCustomCollection
  api_key: your-api-key  # If using authentication
```

### Adjust Search Parameters
```yaml
config:
  top_k: 10  # Retrieve more documents
  similarity_threshold: 0.8  # Higher similarity threshold
  chunk_size: 1024  # Larger chunks
```

### Configure Collection Settings
```yaml
vector_store:
  collection_config:
    vectors:
      size: 384  # Vector dimension
      distance: Cosine  # Distance metric
    optimizers_config:
      memmap_threshold: 20000
```

## Troubleshooting

### Connection Issues
- **Error**: "Connection refused"
  - **Solution**: Ensure Qdrant server is running on port 6333
  - **Check**: `curl http://localhost:6333/collections`

### Collection Issues
- **Error**: "Collection not found"
  - **Solution**: Create collection manually or check collection name
  - **Check**: `curl http://localhost:6333/collections/superoptix_knowledge`

### Performance Issues
- **Slow queries**: Optimize collection settings or reduce `top_k`
- **Memory issues**: Adjust `chunk_size` and `chunk_overlap`

## Use Cases

🏭 **Industrial Applications** - High-throughput document processing and retrieval

🎮 **Gaming & Entertainment** - Real-time content recommendation systems

🏥 **Healthcare** - Medical document analysis and patient information retrieval

💰 **Financial Services** - Risk assessment and regulatory compliance document search

## 📚 Related Documentation

- [SuperOptiX RAG Guide](../guides/rag)
- [RAG Integration Guide](../guides/rag) - Vector database setup and configuration
- [Model Management](../guides/model-management.md)

---

**Ready to experience lightning-fast vector search with Qdrant?** ⚡

Start with this demo to understand how Qdrant's performance optimizations can supercharge your AI applications with blazingly fast knowledge retrieval and similarity search capabilities. 