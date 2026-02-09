# 🔍 RAG ChromaDB Demo Agent

The RAG ChromaDB Demo Agent showcases **Retrieval-Augmented Generation** capabilities with ChromaDB vector database in SuperOptiX. This demo focuses specifically on how to configure and use RAG with ChromaDB for knowledge retrieval and context-aware responses.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🔍 **RAG Integration**: How to configure RAG with ChromaDB in SuperOptiX
- 📚 **Knowledge Retrieval**: Semantic search and document retrieval
- 🧠 **Context-Aware Responses**: Responses based on retrieved knowledge
- ⚙️ **Playbook Configuration**: How to set up RAG in agent playbooks

## 🚀 **Setup RAG with ChromaDB**

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
# Pull the RAG ChromaDB demo agent
super agent pull rag_chroma_demo

# Compile the agent
super agent compile rag_chroma_demo

# Run the agent
super agent run rag_chroma_demo --goal "What is the SuperOptiX framework?"
```

## 🔧 **RAG Configuration in Playbook**

The RAG ChromaDB demo showcases how to configure RAG in the agent playbook:

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
  retriever_type: chroma
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
    similarity_threshold: 0.7
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    collection_name: rag_demo_knowledge
    persist_directory: ./data/chromadb
```

**Key RAG Configuration Points**:

- **`enabled: true`**: Enables RAG functionality
- 🗄️ **`retriever_type: chroma`**: Uses ChromaDB as vector database
- 🔝 **`top_k: 5`**: Retrieves top 5 most similar documents
- 📄 **`chunk_size: 512`**: Document chunk size for processing
- 🔗 **`chunk_overlap: 50`**: Overlap between chunks for context
- 🎯 **`similarity_threshold: 0.7`**: Minimum similarity score for retrieval
- 🧠 **`embedding_model`**: Sentence transformers for embeddings
- 📁 **`collection_name`**: ChromaDB collection name
- 💾 **`persist_directory`**: Local storage directory



## 🔍 **RAG: Your AI's Memory Bank**

Retrieval-Augmented Generation (RAG) gives your AI agent the ability to access and use specific knowledge. Think of it as giving your AI a personal library:

- **🧠 Semantic Understanding**: Finds relevant information based on meaning, not just keywords
- **📚 Knowledge Base**: Access to your own documents, databases, and information sources
- **🎯 Precise Answers**: Generates responses based on actual retrieved content
- **📖 Source Citations**: Always provides references to where information came from
- **🔄 Real-time Updates**: Can access the latest information as it becomes available

## 🔧 **Customizing RAG Configuration**

### **Adjust Retrieval Settings**
Edit `agents/rag_chroma_demo/playbook/rag_chroma_demo_playbook.yaml`:

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
  retriever_type: lancedb  # Use LanceDB instead
  vector_store:
    table_name: lancedb_demo_table
    database_path: ./data/lancedb
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

2. **ChromaDB Issues**
   ```bash
   # Check RAG configuration
   super agent inspect rag_chroma_demo
   
   # Clear ChromaDB data if needed
   rm -rf ./data/chromadb
   ```

3. **RAG Not Working**
   ```bash
   # Check RAG configuration
   super agent inspect rag_chroma_demo
   
   # Verify knowledge base is populated
   ```

### **Getting Help**
```bash
# Check agent status
super agent inspect rag_chroma_demo

# View agent logs
super agent logs rag_chroma_demo

# Get RAG help
super agent --help
```

## 📚 **Related Resources**

- [RAG Guide](../guides/rag.md) - Complete RAG setup and usage
- [RAG Integration Guide](../guides/rag.md) - ChromaDB configuration and setup
- [Agent Development](../guides/agent-development.md) - Building custom agents

## 🎉 **Next Steps**

After exploring the RAG ChromaDB demo:

1. **Try Other RAG Backends**: Explore [RAG LanceDB](rag-lancedb-demo.md) for production use
2. **Customize**: Modify the playbook for your specific knowledge base
3. **Build Your Own**: Use this as a template for your custom RAG agent

---

**Ready to explore knowledge retrieval? Start with the RAG ChromaDB demo! 🚀** 
**Ready to explore knowledge retrieval? Start with the RAG ChromaDB demo! 🚀** 