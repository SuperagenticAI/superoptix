# 🚀 SuperOptiX Examples

Welcome to the SuperOptiX Examples section! These demos showcase specific technologies and capabilities within the SuperOptiX framework. Each demo focuses on a particular technology or feature, providing hands-on experience with different aspects of the framework.

## 🎯 **Demo Overview**

The examples are organized into three main categories:

### **🤖 Model Backend Demos**
Learn how to configure and use different local model backends:

- **[🍎 MLX Demo](agents/mlx-demo)** - Apple Silicon optimization with MLX models
- **[🦙 Ollama Demo](agents/ollama-demo)** - Easy local model management with Ollama
- **[🤗 HuggingFace Demo](agents/huggingface-demo)** - Advanced NLP with HuggingFace models
- **[🎮 LM Studio Demo](agents/lmstudio-demo)** - GUI-based model management with LM Studio

### **🔍 RAG Technology Demos**
Explore Retrieval-Augmented Generation capabilities:

- **[🔍 RAG ChromaDB Demo](agents/rag-chroma-demo)** - RAG with ChromaDB vector database
- **[🚀 RAG LanceDB Demo](agents/rag-lancedb-demo)** - High-performance RAG with LanceDB
- **[🗄️ Weaviate Demo](agents/weaviate-demo)** - Advanced semantic search with Weaviate
- **[🎯 Qdrant Demo](agents/qdrant-demo)** - Lightning-fast vector search with Qdrant
- **[🏗️ Milvus Demo](agents/milvus-demo)** - Enterprise-scale vector database with Milvus

### **🛠️ Framework Feature Demos**
Discover core framework capabilities:

- **[🛠️ Tools Demo](agents/tools-demo)** - Comprehensive tool integration across 20+ categories
- **[🧠 Memory Demo](agents/memory-demo)** - Multi-layered memory system (short-term, long-term, episodic)
- **[📊 Observability Demo](agents/observability-demo)** - Monitoring, tracing, and debugging capabilities

### **🔌 Observability Integrations**
Integrate with external observability platforms:

- **[🧪 MLFlow Integration](agents/mlflow-integration)** - Experiment tracking and model monitoring
- **[🔍 LangFuse Integration](agents/langfuse-integration)** - LLM observability and performance tracking

## 🎯 **Technology Focus Matrix**

| Demo | Primary Technology | Key Features | Use Case |
|------|-------------------|--------------|----------|
| **MLX** | Apple Silicon Models | Native performance, 4-bit quantization | Apple Silicon development |
| **Ollama** | Easy Model Management | Simple setup, cross-platform | Quick local model usage |
| **HuggingFace** | Advanced NLP | Transformer models, custom models | NLP research and development |
| **LM Studio** | GUI Model Management | Visual interface, Windows-friendly | Desktop model management |
| **RAG ChromaDB** | Knowledge Retrieval | Semantic search, document retrieval | Knowledge base queries |
| **RAG LanceDB** | High-Performance RAG | Scalable, production-ready | Large-scale deployments |
| **Weaviate** | Advanced Semantic Search | Sophisticated similarity algorithms | Academic research, enterprise search |
| **Qdrant** | Lightning-Fast Search | Optimized performance, high throughput | Industrial applications, real-time systems |
| **Milvus** | Enterprise-Scale RAG | Cloud-native, distributed architecture | Massive-scale deployments, enterprise search |
| **Tools** | Tool Integration | 20+ categories, specialized tools | Enhanced agent capabilities |
| **Memory** | Context Retention | Multi-layered, persistent storage | Conversational AI |
| **Observability** | Monitoring & Debugging | Tracing, metrics, dashboard | Production monitoring |
| **MLFlow** | Experiment Tracking | Model monitoring, metrics, artifacts | ML lifecycle management |
| **LangFuse** | LLM Observability | Token tracking, cost monitoring, feedback | LLM application monitoring |

## 🚀 **Getting Started**

### **Prerequisites**

1. **Install SuperOptiX**
   ```bash
   pip install superoptix
   ```

2. **Choose Your Demo**
   - Start with **Ollama** for easiest setup
   - Use **MLX** if you have Apple Silicon
   - Try **RAG** for knowledge retrieval
   - Explore **Tools** for enhanced capabilities

### **Quick Start Pattern**

Each demo follows this pattern:

```bash
# Install model
super model install <model_name>

# Start server (if needed)
super model server <backend> <model_name>

# Pull and run demo
super agent pull <demo_name>
super agent compile <demo_name>
super agent run <demo_name> --goal "Your question here"
```

## 🎯 **Learning Path**

### **Beginner Path**
1. **Ollama Demo** - Learn basic model setup
2. **Tools Demo** - Explore tool integration
3. **Memory Demo** - Understand context retention

### **Intermediate Path**
1. **MLX Demo** - Apple Silicon optimization
2. **RAG ChromaDB Demo** - Knowledge retrieval
3. **Observability Demo** - Monitoring and debugging

### **Advanced Path**
1. **HuggingFace Demo** - Advanced NLP capabilities
2. **LM Studio Demo** - GUI model management
3. **RAG LanceDB Demo** - Production-scale RAG
4. **MLFlow Integration** - Experiment tracking and monitoring
5. **LangFuse Integration** - LLM observability and cost tracking

## 🔧 **Customization Guide**

Each demo serves as a template for building custom agents:

### **Model Backend Customization**
- Change models in `language_model.model`
- Adjust performance settings (temperature, max_tokens)
- Configure different backends (mlx, ollama, huggingface, lmstudio)

### **RAG Customization**
- Modify retrieval settings (top_k, chunk_size)
- Change vector databases (chroma, lancedb, weaviate, qdrant, milvus)
- Adjust embedding models

### **Framework Feature Customization**
- Enable/disable specific tools
- Configure memory settings
- Adjust observability levels
- Integrate external observability platforms (MLFlow, LangFuse)

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Model Not Found**
   ```bash
   # Check available models
   super model list --backend <backend>
   
   # Install required model
   super model install <model_name>
   ```

2. **Server Not Running**
   ```bash
   # Check server status
   curl http://localhost:<port>/health
   
   # Start server
   super model server <backend> <model_name>
   ```

3. **Demo Not Working**
   ```bash
   # Check agent status
   super agent inspect <demo_name>
   
   # View logs
   super agent logs <demo_name>
   ```

### **Getting Help**
```bash
# General help
super --help

# Model help
super model --help

# Agent help
super agent --help
```

## 📚 **Related Resources**

- **[Quick Start Guide](../quick-start.md)** - Get up and running quickly
- **[LLM Setup Guide](../llm-setup.md)** - Complete model setup instructions
- **[Agent Development](../guides/agent-development.md)** - Build custom agents
- **[Tool Development](../guides/tool-development.md)** - Create custom tools
- **[RAG Guide](../guides/rag.md)** - RAG implementation guide
- **[Memory Guide](../guides/memory.md)** - Memory system guide
- **[Observability Guide](../guides/observability.md)** - Monitoring and debugging
- **[MLFlow Integration](agents/mlflow-integration.md)** - MLFlow integration guide
- **[LangFuse Integration](agents/langfuse-integration.md)** - LangFuse integration guide

## 🎉 **Next Steps**

After exploring the demos:

1. **Build Custom Agents** - Use demos as templates for your specific use cases
2. **Combine Technologies** - Mix and match different technologies
3. **Scale to Production** - Deploy optimized agents for production use
4. **Contribute** - Share your custom agents and tools with the community

---

**Ready to explore SuperOptiX capabilities? Choose a demo and start building! 🚀** 