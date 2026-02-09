# 🔍 RAG (Retrieval-Augmented Generation) Guide

SuperOptiX provides **universal RAG support** across all 6 major agent frameworks, with powerful MCP (Model Context Protocol) integration for advanced knowledge retrieval.

**🌟 Key Achievement**: RAG works seamlessly across DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, and DeepAgents!

## Overview

RAG enhances AI agents by providing them with access to external knowledge sources. Instead of relying solely on pre-trained knowledge, agents can retrieve relevant information from documents, databases, or other sources to provide more accurate and up-to-date responses.

### **Multi-Framework RAG**

RAG in SuperOptiX works consistently across all frameworks:
- **🔧 Framework Agnostic**: Same RAG configuration works for all frameworks
- **📊 MCP Integration**: Advanced Model Context Protocol support
- **⚡ Multiple Vector DBs**: ChromaDB, LanceDB, Weaviate, Qdrant, Milvus
- **🎯 Universal Optimization**: GEPA can optimize RAG-enhanced agents
- **🔄 Consistent API**: Same configuration format across frameworks

## 🚀 Quick Start

### **Universal RAG Configuration**

RAG works the same way across all frameworks! Just add the `rag` section to your playbook:

=== "🔬 DSPy"
    ```yaml
    spec:
      target_framework: dspy
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

=== "🤖 OpenAI SDK"
    ```yaml
    spec:
      target_framework: openai
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

=== "👥 CrewAI"
    ```yaml
    spec:
      target_framework: crewai
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

=== "🔮 Google ADK"
    ```yaml
    spec:
      target_framework: google-adk
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

=== "🏢 Microsoft"
    ```yaml
    spec:
      target_framework: microsoft
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

=== "🌊 DeepAgents"
    ```yaml
    spec:
      target_framework: deepagents
      rag:
        enabled: true
        retriever_type: chroma
        config:
          top_k: 5
          chunk_size: 512
    ```

### **Universal Workflow**

```bash
# Same workflow for ALL frameworks!
super agent compile <agent_name>  # RAG automatically configured
super agent evaluate <agent_name>  # Test with knowledge retrieval
super agent optimize <agent_name> --auto medium  # GEPA optimizes RAG-enhanced agents
super agent run <agent_name>  # Use with RAG-enhanced responses
```

## RAG Configuration

RAG is configured through the playbook YAML file. Here's the structure:

```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma  # or vector_database: chroma
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: knowledge_base
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | true | Enable/disable RAG |
| `retriever_type` | string | - | Vector database type |
| `top_k` | int | 5 | Number of documents to retrieve |
| `chunk_size` | int | 512 | Document chunk size |
| `chunk_overlap` | int | 50 | Overlap between chunks |
| `embedding_model` | string | all-MiniLM-L6-v2 | Sentence transformer model |

## 🔌 MCP (Model Context Protocol) Integration

SuperOptiX supports **MCP (Model Context Protocol)** for advanced RAG capabilities and tool integration.

### **What is MCP?**

MCP (Model Context Protocol) is a universal protocol for connecting AI agents to external data sources, tools, and knowledge bases. It provides:
- **Standardized Connections**: Connect to any MCP server
- **Advanced RAG**: Enhanced knowledge retrieval
- **Tool Integration**: Seamless tool discovery and execution
- **Multi-Framework Support**: Works across all frameworks

### **MCP Configuration**

```yaml
spec:
  target_framework: dspy  # Works with any framework
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
    config:
      top_k: 5
      chunk_size: 512
```

### **MCP Benefits**

- **Universal Protocol**: Works across all frameworks
- **Rich Integrations**: Connect to filesystems, databases, APIs, Git repos
- **Tool Discovery**: Automatic tool detection and execution
- **Enhanced RAG**: Better context retrieval with MCP servers
- **GEPA Optimization**: Optimize MCP-enhanced agents with GEPA

### **Example: MCP + RAG + Multi-Framework**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: mcp_enhanced_agent
spec:
  target_framework: openai  # Works with ANY framework!
  language_model:
    provider: ollama
    model: gpt-oss:20b
  rag:
    enabled: true
    retriever_type: chroma
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "./docs"]
  optimization:
    optimizer:
      name: GEPA  # Optimize MCP-enhanced agents!
      params:
        auto: medium
```

**Learn More**: See our [MCP Protocol Guide](protocol-first-agents.md) for detailed MCP integration examples.

---

## 📦 Supported Vector Databases

### ChromaDB (Recommended for Local Development)

ChromaDB is the default and recommended option for local development. It's lightweight, requires no external dependencies, and automatically downloads embedding models.

#### Configuration

```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: my_knowledge_base
```

#### Example Usage

```python
from agile.agents.qa.pipelines.qa_pipeline import QaPipeline

# Initialize with ChromaDB
pipeline = QaPipeline()

# Add documents
documents = [
    {
        'content': 'ChromaDB is a lightweight vector database for AI applications.',
        'metadata': {'source': 'chroma_docs', 'version': '1.0'}
    }
]

pipeline.add_documents(documents)

# Query
result = await pipeline.forward("What is ChromaDB?")
print(result['response'])
```

### LanceDB

LanceDB is a modern vector database built on Apache Arrow, offering high performance and easy integration.

#### Configuration

```yaml
spec:
  rag:
    enabled: true
    retriever_type: lancedb
    config:
      top_k: 5
      chunk_size: 512
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      table_name: knowledge_table
      database_path: ./data/lancedb
```

#### Example Usage

```python
from agile.agents.qa.pipelines.qa_pipeline import QaPipeline

# Initialize with LanceDB
pipeline = QaPipeline()

# Add documents
documents = [
    {
        'content': 'LanceDB provides fast vector search with Apache Arrow.',
        'metadata': {'source': 'lancedb_docs', 'category': 'database'}
    }
]

pipeline.add_documents(documents)

# Query
result = await pipeline.forward("What is LanceDB?")
print(result['response'])
```

### Weaviate

Weaviate is a vector database with a rich ecosystem and cloud offerings.

#### Configuration

```yaml
spec:
  rag:
    enabled: true
    retriever_type: weaviate
    config:
      top_k: 5
      chunk_size: 512
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: knowledge_collection
      weaviate_url: http://localhost:8080
      api_key: your_api_key  # Optional
```

#### Example Usage

```python
from agile.agents.qa.pipelines.qa_pipeline import QaPipeline

# Initialize with Weaviate
pipeline = QaPipeline()

# Add documents
documents = [
    {
        'content': 'Weaviate is a vector database with rich ecosystem.',
        'metadata': {'source': 'weaviate_docs', 'category': 'database'}
    }
]

pipeline.add_documents(documents)

# Query
result = await pipeline.forward("What is Weaviate?")
print(result['response'])
```

### Qdrant

Qdrant is a high-performance vector database with advanced filtering capabilities.

#### Configuration

```yaml
spec:
  rag:
    enabled: true
    retriever_type: qdrant
    config:
      top_k: 5
      chunk_size: 512
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: knowledge_collection
      qdrant_url: http://localhost:6333
      api_key: your_api_key  # Optional
```

### Milvus

Milvus is a scalable vector database designed for production use.

#### Configuration

```yaml
spec:
  rag:
    enabled: true
    retriever_type: milvus
    config:
      top_k: 5
      chunk_size: 512
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: knowledge_collection
      milvus_host: localhost
      milvus_port: 19530
```

## Document Ingestion

### Adding Documents

```python
# Single document
pipeline.add_document({
    'content': 'Your document content here.',
    'metadata': {
        'source': 'manual',
        'category': 'general',
        'date': '2024-01-01'
    }
})

# Multiple documents
documents = [
    {
        'content': 'First document content.',
        'metadata': {'source': 'file1', 'category': 'technical'}
    },
    {
        'content': 'Second document content.',
        'metadata': {'source': 'file2', 'category': 'business'}
    }
]
pipeline.add_documents(documents)
```

### Document Chunking

Documents are automatically chunked for better retrieval:

```yaml
spec:
  rag:
    config:
      chunk_size: 512      # Characters per chunk
      chunk_overlap: 50    # Overlap between chunks
      chunk_strategy: "recursive"  # recursive, fixed, semantic
```

## Advanced Configuration

### Custom Embedding Models

```yaml
spec:
  rag:
    vector_store:
      embedding_model: sentence-transformers/all-mpnet-base-v2  # Better quality
      # or
      embedding_model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  # Multilingual
```

### Retrieval Strategies

```yaml
spec:
  rag:
    config:
      top_k: 5
      similarity_threshold: 0.7
      rerank: true  # Enable re-ranking for better results
      hybrid_search: true  # Combine dense and sparse retrieval
```

### Filtering and Metadata

```python
# Query with metadata filters
result = await pipeline.forward(
    "What is DSPy?",
    filters={
        'category': 'framework',
        'source': 'docs'
    }
)
```

## RAG with Tools

RAG can be combined with tools for enhanced capabilities:

```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma
  tool_calling:
    enabled: true
    available_tools: ["web_search", "file_reader"]
```

## Best Practices

### Document Quality
- Use high-quality, relevant documents
- Ensure proper formatting and structure
- Include comprehensive metadata
- Regular updates and maintenance

### Chunking Strategy
- Choose appropriate chunk sizes (512-1024 characters)
- Use overlap to maintain context
- Consider semantic boundaries
- Test different strategies for your use case

### Embedding Models
- Use appropriate models for your domain
- Consider multilingual requirements
- Balance quality vs. performance
- Regular model updates

### Vector Database Selection
- **ChromaDB**: Development and prototyping
- **LanceDB**: High-performance local applications
- **Weaviate**: Rich ecosystem and cloud features
- **Qdrant**: Advanced filtering requirements
- **Milvus**: Large-scale production deployments

### Performance Optimization
- Monitor retrieval latency
- Optimize chunk sizes
- Use appropriate top_k values
- Implement caching strategies

## Troubleshooting

### Common Issues

#### RAG Not Working
```python
# Check RAG status
status = pipeline.get_rag_status()
print(f"RAG enabled: {status['enabled']}")
print(f"Documents loaded: {status['document_count']}")
```

#### Poor Retrieval Quality
```yaml
# Adjust configuration
spec:
  rag:
    config:
      top_k: 10  # Increase for more candidates
      similarity_threshold: 0.5  # Lower threshold
    vector_store:
      embedding_model: sentence-transformers/all-mpnet-base-v2  # Better model
```

#### Performance Issues
```yaml
# Optimize for performance
spec:
  rag:
    config:
      top_k: 3  # Reduce for faster retrieval
      chunk_size: 256  # Smaller chunks
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2  # Faster model
```

## Integration Examples

### RAG + Memory Integration
```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma
  memory:
    enabled: true
    long_term:
      enable_embeddings: true
```

### RAG + Optimization Integration
```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma
  optimization:
    enabled: true
    strategy: bootstrap_few_shot
```

## 📚 Related Documentation

- [Agent Development Guide](agent-development.md) - Complete agent development workflow
- [Memory Guide](memory.md) - Memory systems integration
- [Quick Start Guide](../quick-start.md) - Getting started with SuperOptiX 