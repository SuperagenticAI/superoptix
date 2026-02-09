# Milvus RAG Demo 🏗️

A comprehensive demonstration of SuperOptiX's RAG capabilities using **Milvus** vector database for enterprise-grade similarity search and scalable knowledge retrieval.

## Overview

This demo showcases how to integrate **Milvus** - a cloud-native vector database - with SuperOptiX's RAG system to create intelligent agents capable of retrieving and synthesizing information from massive knowledge bases with enterprise-level scalability.

## This demo demonstrates:

🏗️ **Milvus Vector Database Integration** - Enterprise-grade connection to Milvus for scalable vector storage

🌐 **Cloud-Native Architecture** - Distributed vector search with horizontal scaling capabilities

📈 **Massive Scale Operations** - Handle millions of vectors with high performance

🔍 **Advanced Indexing** - Multiple indexing strategies for different use cases

🔄 **RAG Pipeline Integration** - Complete retrieval-augmented generation workflow

## Prerequisites

### Install SuperOptiX
```bash
pip install superoptix
```

### Install Milvus Dependencies
```bash
pip install pymilvus
```

### Set Up Milvus Server
```bash
# Using Docker Compose (recommended)
wget https://github.com/milvus-io/milvus/releases/download/v2.5.12/milvus-standalone-docker-compose.yml
docker-compose up -d
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
super agent pull rag_milvus_demo
```

### Compile the Agent
```bash
super agent compile rag_milvus_demo
```

### Run the Demo
```bash
super agent run rag_milvus_demo --goal "What are the key features of Milvus and how does it work with SuperOptiX?"
```

## Key Configuration Points:

🔧 **Vector Database Setup** - Configured to connect to Milvus at `localhost:19530`

📊 **Collection Management** - Uses `superoptix_knowledge` collection for document storage

🎯 **Embedding Model** - Leverages `sentence-transformers/all-MiniLM-L6-v2` for vector generation

⚙️ **Search Parameters** - Optimized with `top_k: 5` and `similarity_threshold: 0.7`

## Playbook Configuration

The demo uses a specialized playbook with Milvus-specific configurations:

```yaml
rag:
  enabled: true
  retriever_type: milvus
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    host: localhost
    port: 19530
    collection_name: superoptix_knowledge
```

## Customization

### Modify Milvus Connection
```yaml
vector_store:
  host: your-milvus-host
  port: 19530
  collection_name: YourCustomCollection
  user: your-username  # If using authentication
  password: your-password
```

### Adjust Search Parameters
```yaml
config:
  top_k: 10  # Retrieve more documents
  similarity_threshold: 0.8  # Higher similarity threshold
  chunk_size: 1024  # Larger chunks
```

### Configure Collection Schema
```yaml
vector_store:
  schema:
    fields:
      - name: id
        dtype: INT64
        is_primary: true
      - name: content
        dtype: VARCHAR
        max_length: 65535
      - name: embedding
        dtype: FLOAT_VECTOR
        dim: 384
```

## Troubleshooting

### Connection Issues
- **Error**: "Connection refused"
  - **Solution**: Ensure Milvus server is running on port 19530
  - **Check**: `curl http://localhost:9091/healthz`

### Collection Issues
- **Error**: "Collection not found"
  - **Solution**: Create collection manually or check collection name
  - **Check**: Use Milvus CLI or Python client to list collections

### Performance Issues
- **Slow queries**: Optimize index parameters or reduce `top_k`
- **Memory issues**: Adjust `chunk_size` and `chunk_overlap`

## Use Cases

🏢 **Enterprise Search** - Large-scale corporate knowledge management

🔬 **Scientific Research** - Massive dataset analysis and discovery

📱 **Recommendation Systems** - High-throughput content recommendation

🎯 **E-commerce** - Product search and recommendation engines

## 📚 Related Documentation

- [SuperOptiX RAG Guide](../guides/rag)
- [RAG Integration Guide](../guides/rag) - Vector database setup and configuration
- [Model Management](../guides/model-management.md)

---

**Ready to scale your vector search with Milvus?** 🚀

Start with this demo to understand how Milvus's enterprise-grade capabilities can power your AI applications with massive-scale knowledge retrieval and similarity search. 