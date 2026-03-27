# 🚀 RAG LanceDB Demo Agent

This demo now uses the `turboagents-lancedb` retriever path inside SuperOptiX.

The RAG LanceDB Demo Agent showcases **high-performance RAG** capabilities with LanceDB vector database in SuperOptiX. This demo focuses specifically on how to configure and use RAG with LanceDB for scalable, production-ready knowledge retrieval.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🚀 **High-Performance RAG**: How to configure RAG with LanceDB in SuperOptiX
- 📈 **Scalable Knowledge Retrieval**: Production-ready vector database
- ⚡ **Fast Semantic Search**: Optimized retrieval performance
- ⚙️ **Playbook Configuration**: How to set up RAG with LanceDB in agent playbooks

## 🚀 **Setup RAG with LanceDB**

### **1. Install Ollama Model**

```bash
# Install the Ollama model used in this demo
super model install llama3.2:8b
```

### **2. Start Ollama Server**

```bash
# Start Ollama server (runs on port 11434 by default)
ollama serve
```

### **3. Pull and Run the Demo**

```bash
# Install the TurboAgents-backed RAG path
uv pip install "superoptix[turboagents]"

# Pull the RAG LanceDB demo agent
super agent pull rag_lancedb_demo

# Compile the agent
super agent compile rag_lancedb_demo

# Run the agent
super agent run rag_lancedb_demo --goal "What is the SuperOptiX framework?"
```

## 🔧 **RAG Configuration in Playbook**

The RAG LanceDB demo showcases how to configure RAG with LanceDB in the agent playbook:

### **Language Model Configuration**
```yaml
language_model:
  location: local
  provider: ollama
  model: llama3.2:8b
  api_base: http://localhost:11434
  temperature: 0.7
  max_tokens: 2048
```

### **RAG Configuration**
```yaml
rag:
  enabled: true
  retriever_type: turboagents-lancedb
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    embedding_dimension: 64
    bits: 3.5
    rerank_top: 16
    table_name: lancedb_demo_table
    uri: ./data/lancedb
```

**Key RAG Configuration Points**:

- **`enabled: true`**: Enables RAG functionality
- 🗄️ **`retriever_type: turboagents-lancedb`**: Uses TurboAgents over LanceDB as the retrieval path
- 🔝 **`top_k: 5`**: Retrieves top 5 most similar documents
- 📄 **`chunk_size: 512`**: Document chunk size for processing
- 🔗 **`chunk_overlap: 50`**: Overlap between chunks for context
- 🎯 **`similarity_threshold: 0.7`**: Minimum similarity score for retrieval
- 🧠 **`embedding_model`**: Sentence transformers for embeddings
- 📐 **`embedding_dimension: 64`**: TurboAgents-compatible compressed dimension
- 🪶 **`bits: 3.5`**: Current default compression setting for the demo
- 🧮 **`rerank_top: 16`**: Candidate pool reranked by TurboAgents before final selection
- 📋 **`table_name`**: LanceDB table name
- 💾 **`uri`**: LanceDB storage directory

## 🧩 Why This Uses TurboAgents

This SuperOptiX demo now exercises the real TurboAgents integration path instead
of only the native LanceDB path.

That means:

- LanceDB still stores and serves the candidate set
- SuperOptiX selects the `turboagents-lancedb` retriever
- TurboAgents handles compressed retrieval and reranking inside the SuperOptiX RAG flow

This gives you a concrete integration story to compare against the older native
retriever behavior.



## 🚀 **LanceDB: Enterprise-Grade RAG**

LanceDB is built for production environments where performance and scalability matter. It's the vector database of choice for serious applications:

- **⚡ Lightning Fast**: Optimized for high-speed semantic search across millions of documents
- **📈 Enterprise Scale**: Handles massive document collections with ease
- **🏢 Production Ready**: Built with enterprise-grade reliability and consistency
- **☁️ Cloud Native**: Seamlessly works with cloud storage and distributed systems
- **🔄 ACID Compliant**: Guarantees data consistency and transaction safety
- **📋 Version Control**: Track changes and maintain document history

## 🔧 **Customizing RAG Configuration**

### **Adjust Retrieval Settings**
Edit `agents/rag_lancedb_demo/playbook/rag_lancedb_demo_playbook.yaml`:

```yaml
rag:
  config:
    top_k: 10  # Retrieve more documents
    chunk_size: 1024  # Larger chunks
    similarity_threshold: 0.8  # Higher similarity threshold
```

### **Change Vector Database**
```yaml
rag:
  retriever_type: chroma  # Use ChromaDB instead
  vector_store:
    collection_name: chromadb_demo_collection
    persist_directory: ./data/chromadb
```

### **Use Different Embedding Model**
```yaml
rag:
  vector_store:
    embedding_model: sentence-transformers/all-mpnet-base-v2  # Different embeddings
```

## 🚨 **Troubleshooting RAG**

### **Common Issues**

1. **Ollama Server Not Running**
   ```bash
   # Check if Ollama server is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama server
   ollama serve
   ```

2. **LanceDB Issues**
   ```bash
   # Check RAG configuration
   super agent inspect rag_lancedb_demo
   
   # Clear LanceDB data if needed
   rm -rf ./data/lancedb
   ```

3. **RAG Not Working**
   ```bash
   # Check RAG configuration
   super agent inspect rag_lancedb_demo
   
   # Verify knowledge base is populated
   ```

### **Getting Help**
```bash
# Check agent status
super agent inspect rag_lancedb_demo

# View agent logs
super agent logs rag_lancedb_demo

# Get RAG help
super agent --help
```

## 📚 Related Documentation

- [RAG Guide](../guides/rag) - Complete RAG setup and usage
- [RAG Integration Guide](../guides/rag) - LanceDB configuration and setup
- [Agent Development](../guides/agent-development.md) - Building custom agents

## 🔗 Next Steps

1. **Try Other RAG Backends**: Explore [RAG ChromaDB](rag-chroma-demo) for development 
