# Weaviate RAG Demo 🗄️

A comprehensive demonstration of SuperOptiX's RAG capabilities using **Weaviate** vector database for advanced semantic search and knowledge retrieval.

## Overview

This demo showcases how to integrate **Weaviate** - a powerful vector database - with SuperOptiX's RAG system to create intelligent agents capable of retrieving and synthesizing information from large knowledge bases.

## This demo demonstrates:

🔍 **Weaviate Vector Database Integration** - Seamless connection to Weaviate for high-performance vector storage

🧠 **Advanced Semantic Search** - Intelligent retrieval using Weaviate's sophisticated similarity algorithms

📚 **Knowledge Base Management** - Efficient document storage, indexing, and retrieval workflows

⚡ **Real-time Query Processing** - Fast response times with Weaviate's optimized search capabilities

🔄 **RAG Pipeline Integration** - Complete retrieval-augmented generation workflow

## Prerequisites

### Install SuperOptiX
```bash
pip install superoptix
```

### Install Weaviate Dependencies
```bash
pip install weaviate-client
```

### Set Up Weaviate Server
```bash
# Using Docker (recommended)
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-transformers' \
  -e TRANSFORMERS_INFERENCE_API='http://t2v-transformers:8080' \
  semitechnologies/weaviate:1.22.4
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
super agent pull rag_weaviate_demo
```

### Compile the Agent
```bash
super agent compile rag_weaviate_demo
```

### Run the Demo
```bash
super agent run rag_weaviate_demo --goal "What is the SuperOptiX framework and its key features?"
```

## Key Configuration Points:

🔧 **Vector Database Setup** - Configured to connect to Weaviate at `http://localhost:8080`

📊 **Collection Management** - Uses `SuperOptiXKnowledge` class for document storage

🎯 **Embedding Model** - Leverages `sentence-transformers/all-MiniLM-L6-v2` for vector generation

⚙️ **Search Parameters** - Optimized with `top_k: 5` and `similarity_threshold: 0.7`

## Playbook Configuration

The demo uses a specialized playbook with Weaviate-specific configurations:

```yaml
rag:
  enabled: true
  retriever_type: weaviate
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    url: http://localhost:8080
    class_name: SuperOptiXKnowledge
```

## Customization

### Modify Weaviate Connection
```yaml
vector_store:
  url: http://your-weaviate-server:8080
  class_name: YourCustomClass
  auth_token: your-auth-token  # If using authentication
```

### Adjust Search Parameters
```yaml
config:
  top_k: 10  # Retrieve more documents
  similarity_threshold: 0.8  # Higher similarity threshold
  chunk_size: 1024  # Larger chunks
```

### Add Custom Schema
```yaml
vector_store:
  schema:
    properties:
      - name: content
        dataType: text
      - name: metadata
        dataType: object
```

## Troubleshooting

### Connection Issues
- **Error**: "Connection refused"
  - **Solution**: Ensure Weaviate server is running on port 8080
  - **Check**: `curl http://localhost:8080/v1/.well-known/ready`

### Client Version Issues
- **Error**: "Client.__init__() takes 1 positional argument but 2 were given"
  - **Solution**: Update to Weaviate client v4: `pip install weaviate-client>=4.0.0`

### Performance Issues
- **Slow queries**: Reduce `top_k` or increase `similarity_threshold`
- **Memory issues**: Adjust `chunk_size` and `chunk_overlap`

## Use Cases

🎓 **Academic Research** - Large-scale document analysis and citation retrieval

🏢 **Enterprise Search** - Corporate knowledge base with semantic understanding

📰 **Content Management** - Intelligent article and document organization

🔬 **Scientific Literature** - Research paper discovery and analysis

## Related Resources

- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [SuperOptiX RAG Guide](../guides/rag.md)
- [RAG Integration Guide](../guides/rag.md) - Vector database setup and configuration
- [Model Management](../guides/model-management.md)

---

**Ready to explore the power of Weaviate with SuperOptiX?** 🚀

Start with this demo to understand how vector databases can enhance your AI applications with intelligent knowledge retrieval and semantic search capabilities. 