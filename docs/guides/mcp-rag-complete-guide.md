# MCP RAG Optimization - Complete Guide

**Model Context Protocol + RAG + GEPA Optimization**

Learn how to build and optimize RAG agents with MCP protocol support.

---

## Table of Contents

1. [Overview](#overview)
2. [What is MCP?](#what-is-mcp)
3. [RAG Basics](#rag-basics)
4. [MCP + RAG Integration](#mcp--rag-integration)
5. [GEPA Optimization for RAG](#gepa-optimization-for-rag)
6. [Practical Examples](#practical-examples)
7. [Advanced Configurations](#advanced-configurations)
8. [Best Practices](#best-practices)

---

## Overview

SuperOptiX combines three powerful technologies:

- **MCP (Model Context Protocol)**: Standard protocol for connecting AI models to external context
- **RAG (Retrieval-Augmented Generation)**: Knowledge retrieval to enhance responses
- **GEPA Optimization**: Automatic optimization of retrieval and generation

**Why This Matters:**
- ✅ Connect to any knowledge source (files, databases, APIs)
- ✅ Retrieve relevant context automatically
- ✅ Optimize retrieval queries and generation prompts
- ✅ Build production-ready RAG agents

---

## What is MCP?

### Model Context Protocol

MCP is an open protocol for connecting AI models to external data sources:

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│   AI Model   │ ←──MCP──│  MCP Server  │ ←──────│  Data Source │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
```

### Supported MCP Servers

SuperOptiX works with all MCP servers:

| Server | Purpose | Source |
|--------|---------|--------|
| **filesystem** | Read/write local files | `@modelcontextprotocol/server-filesystem` |
| **git** | Access Git repositories | `@modelcontextprotocol/server-git` |
| **postgres** | Query PostgreSQL databases | `@modelcontextprotocol/server-postgres` |
| **sqlite** | Query SQLite databases | `@modelcontextprotocol/server-sqlite` |
| **slack** | Access Slack messages | `@modelcontextprotocol/server-slack` |
| **github** | Access GitHub data | `@modelcontextprotocol/server-github` |
| **google-drive** | Access Google Drive | `@modelcontextprotocol/server-google-drive` |

---

## RAG Basics

### What is RAG?

**Retrieval-Augmented Generation** enhances AI responses with relevant knowledge:

```
User Query → [Retrieve Docs] → [Generate with Context] → Response
```

### RAG Components in SuperOptiX

1. **Vector Store**: ChromaDB, LanceDB, Weaviate, Qdrant, Milvus
2. **Embeddings**: OpenAI, HuggingFace, local models
3. **Retrieval**: Semantic search, hybrid search
4. **Generation**: Any LLM with retrieved context

---

## MCP + RAG Integration

### How MCP Enhances RAG

```yaml
spec:
  target_framework: dspy
  
  # Traditional RAG (vector database)
  rag:
    enabled: true
    vector_store: chromadb
    collection_name: docs
    top_k: 5
  
  # MCP Enhancement (live data sources)
  mcp:
    enabled: true
    servers:
      # File system access
      - name: filesystem
        command: npx
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
      
      # Git repository access
      - name: git
        command: npx
        args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
      
      # Database access
      - name: postgres
        command: npx
        args: ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
```

### Benefits

- ✅ **Live data**: Always fresh, no re-indexing
- ✅ **Multiple sources**: Combine vector DB + files + databases
- ✅ **Protocol standard**: Works with any MCP server
- ✅ **Tool integration**: MCP provides tools automatically

---

## GEPA Optimization for RAG

### What GEPA Optimizes

When you use GEPA with RAG agents, it optimizes:

1. **Retrieval Queries**: How to search the knowledge base
2. **Context Selection**: Which documents to use
3. **Generation Prompts**: How to use retrieved context
4. **Answer Synthesis**: How to combine multiple sources

### Example Optimization

**Before GEPA:**
```
Query: "What is the return policy?"
Retrieval: Generic search for "return policy"
Result: Finds wrong section, poor answer
```

**After GEPA:**
```
Query: "What is the return policy?"
Optimized Retrieval: "customer return policy refund procedure"
Result: Finds exact policy, perfect answer
```

---

## Practical Examples

### Example 1: Documentation RAG with MCP

**Use Case**: Build a Q&A agent for your documentation

#### Step 1: Create Playbook

```yaml
# docs_qa_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: docs_qa_agent
  id: docs_qa
spec:
  target_framework: dspy
  
  language_model:
    provider: ollama
    model: llama3.1:8b
  
  persona:
    role: Documentation Assistant
    goal: Answer questions about the documentation
    backstory: |
      You are an expert at finding and explaining documentation.
      You provide accurate, well-sourced answers.
  
  # RAG Configuration
  rag:
    enabled: true
    vector_store: chromadb
    collection_name: documentation
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
  
  # MCP Configuration
  mcp:
    enabled: true
    servers:
      # Access documentation files
      - name: docs_filesystem
        command: npx
        args:
          - "-y"
          - "@modelcontextprotocol/server-filesystem"
          - "/path/to/docs"
      
      # Access git history for recent changes
      - name: docs_git
        command: npx
        args:
          - "-y"
          - "@modelcontextprotocol/server-git"
          - "--repository"
          - "/path/to/docs/repo"
  
  # BDD Scenarios for evaluation
  feature_specifications:
    scenarios:
      - name: Basic documentation query
        input:
          query: "How do I install SuperOptiX?"
        expected_output:
          answer: "pip install superoptix"
          expected_keywords:
            - pip
            - install
            - superoptix
      
      - name: Complex workflow query
        input:
          query: "What is the workflow for optimizing an agent?"
        expected_output:
          answer: "compile, evaluate, optimize, evaluate"
          expected_keywords:
            - compile
            - evaluate
            - optimize
      
      - name: API reference query
        input:
          query: "What parameters does super agent optimize accept?"
        expected_output:
          answer: "auto, optimizer, iterations"
          expected_keywords:
            - auto
            - optimizer
            - iterations
```

#### Step 2: Prepare Knowledge Base

```bash
# Index your documentation
super agent rag index docs_qa \
  --directory /path/to/docs \
  --pattern "**/*.md"

# Verify indexing
super agent rag info docs_qa
```

#### Step 3: Compile and Test

```bash
# Compile
super agent compile docs_qa

# Test without optimization
super agent evaluate docs_qa
# Example result: 60% accuracy

# Optimize with GEPA
super agent optimize docs_qa --auto medium

# Test after optimization
super agent evaluate docs_qa  # automatically loads optimized weights
# Example result: 85% accuracy (+25%)
```

#### Step 4: Run

```bash
# Interactive mode
super agent run docs_qa

# Single query
super agent run docs_qa --input "How do I optimize an agent?"
```

---

### Example 2: Code Repository Q&A

**Use Case**: Answer questions about your codebase

```yaml
# code_qa_playbook.yaml
spec:
  target_framework: dspy
  
  persona:
    role: Code Expert
    goal: Answer questions about the codebase
  
  rag:
    enabled: true
    vector_store: lancedb
    embedding_model: openai:text-embedding-3-small
    top_k: 10
  
  mcp:
    enabled: true
    servers:
      # File system for code files
      - name: codebase
        command: npx
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/code"]
      
      # Git for history and blame
      - name: git_history
        command: npx
        args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/code"]
  
  feature_specifications:
    scenarios:
      - name: Find function implementation
        input:
          query: "How is the compile function implemented?"
        expected_output:
          answer: "Located in cli/compile.py"
          expected_keywords:
            - compile
            - implementation
            - function
```

**Usage:**

```bash
# Index codebase
super agent rag index code_qa \
  --directory /path/to/code \
  --pattern "**/*.py" \
  --exclude "**/__pycache__/**,**/node_modules/**"

# Optimize
super agent optimize code_qa --auto medium

# Query
super agent run code_qa --input "Where is GEPA optimizer defined?"
```

---

### Example 3: Customer Support with Multiple Sources

**Use Case**: Support agent with access to docs, tickets, and knowledge base

```yaml
# support_agent_playbook.yaml
spec:
  target_framework: crewai
  
  persona:
    role: Customer Support Agent
    goal: Resolve customer issues efficiently
    backstory: |
      Expert support agent with access to all customer data and documentation.
  
  rag:
    enabled: true
    vector_store: qdrant
    top_k: 8
  
  mcp:
    enabled: true
    servers:
      # Documentation
      - name: docs
        command: npx
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
      
      # Customer database
      - name: customer_db
        command: npx
        args: ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/customers"]
      
      # Slack for team discussions
      - name: team_slack
        command: npx
        args: ["-y", "@modelcontextprotocol/server-slack"]
        env:
          SLACK_BOT_TOKEN: "xoxb-your-token"
  
  feature_specifications:
    scenarios:
      - name: Product question
        input:
          query: "Customer asks about feature X"
        expected_output:
          answer: "Feature X is available in Pro plan"
      
      - name: Issue resolution
        input:
          query: "Customer reports bug with Y"
        expected_output:
          answer: "Known issue, workaround is Z"
```

**Workflow:**

```bash
# Index all sources
super agent rag index support_agent --directory /path/to/docs
super agent rag index support_agent --source postgresql://localhost/customers

# Optimize for best responses
super agent optimize support_agent --auto intensive

# Run in production
super agent run support_agent
```

---

## Advanced Configurations

### Hybrid Search (Vector + Keyword)

```yaml
rag:
  enabled: true
  vector_store: weaviate
  search_type: hybrid  # Vector + keyword search
  alpha: 0.75  # 0.0 = pure keyword, 1.0 = pure vector
  top_k: 5
```

### Re-ranking

```yaml
rag:
  enabled: true
  vector_store: chromadb
  top_k: 20  # Retrieve more candidates
  rerank:
    enabled: true
    model: cross-encoder/ms-marco-MiniLM-L-6-v2
    top_n: 5  # Final count after reranking
```

### Multi-Vector Store

```yaml
rag:
  enabled: true
  stores:
    # Primary: Fast, general purpose
    - name: primary
      vector_store: chromadb
      collection_name: general
      top_k: 5
    
    # Secondary: Specialized, high-quality
    - name: specialized
      vector_store: qdrant
      collection_name: expert
      top_k: 3
```

### MCP with Environment Variables

```yaml
mcp:
  enabled: true
  servers:
    - name: postgres
      command: npx
      args: ["-y", "@modelcontextprotocol/server-postgres"]
      env:
        DATABASE_URL: "${POSTGRES_URL}"
        DATABASE_USER: "${POSTGRES_USER}"
        DATABASE_PASSWORD: "${POSTGRES_PASSWORD}"
```

---

## Best Practices

### 1. Start with Good Data

```bash
# Clean your documents
# Remove duplicates
# Use consistent formatting
# Split long documents

# Index incrementally
super agent rag index my_agent --directory ./docs/batch1
super agent rag index my_agent --directory ./docs/batch2 --append
```

### 2. Tune Retrieval Parameters

```yaml
rag:
  top_k: 5  # Start with 5, adjust based on results
  chunk_size: 512  # Balance between context and precision
  chunk_overlap: 50  # 10% of chunk_size
```

### 3. Use GEPA to Optimize

```bash
# Let GEPA find the best retrieval strategy
super agent optimize my_agent --auto medium

# GEPA will optimize:
# - How to formulate queries
# - Which chunks to use
# - How to combine retrieved context
```

### 4. Monitor and Iterate

```bash
# Evaluate regularly
super agent evaluate my_agent

# Check retrieval quality
super agent rag test my_agent --goal "test question"

# Re-index when data changes
super agent rag reindex my_agent
```

### 5. Combine Multiple Sources

```yaml
# Best practice: Vector DB + MCP
rag:
  enabled: true
  vector_store: chromadb  # For static docs
mcp:
  enabled: true
  servers:
    - name: live_data  # For dynamic data
      command: npx
      args: ["-y", "@modelcontextprotocol/server-postgres", "..."]
```

---

## Troubleshooting

### Issue: Poor Retrieval Quality

**Solutions:**
```bash
# 1. Check indexing
super agent rag info my_agent

# 2. Test retrieval
super agent rag test my_agent --goal "your query"

# 3. Adjust parameters
# In playbook:
rag:
  top_k: 10  # Increase
  chunk_size: 256  # Decrease for more precise

# 4. Re-index with better chunking
super agent rag reindex my_agent
```

### Issue: MCP Server Not Starting

**Solutions:**
```bash
# Check npx is installed
npx --version

# Test MCP server manually
npx -y @modelcontextprotocol/server-filesystem /path

# Check logs
super agent run my_agent --verbose
```

### Issue: Slow Performance

**Solutions:**
```yaml
# Use faster vector store
rag:
  vector_store: lancedb  # Fast
  # vs chromadb (slower but feature-rich)

# Cache embeddings
rag:
  cache_embeddings: true

# Reduce top_k
rag:
  top_k: 3  # Fewer retrievals
```

---

## CLI Commands Reference

```bash
# RAG Commands
super agent rag index <agent> --directory <path>
super agent rag reindex <agent>
super agent rag info <agent>
super agent rag test <agent> --goal "test"
super agent rag clear <agent>

# MCP Commands
super agent mcp list <agent>
super agent mcp test <agent> --server <name>
super agent mcp logs <agent>

# Combined Workflow
super agent compile <agent>
super agent rag index <agent> --directory ./docs
super agent evaluate <agent>
super agent optimize <agent> --auto medium
super agent evaluate <agent>  # automatically loads optimized weights
super agent run <agent>
```

---

## Real-World Examples

### Example: SuperOptiX Documentation Assistant

```bash
# 1. Clone repo
git clone https://github.com/SuperagenticAI/SuperOptiX
cd SuperOptiX

# 2. Pull demo agent
super agent pull docs_qa_agent

# 3. Index documentation
super agent rag index docs_qa_agent --directory ./docs

# 4. Configure MCP for live docs
# Edit: agents/docs_qa_agent/playbook/docs_qa_agent_playbook.yaml
# Add MCP filesystem server pointing to ./docs

# 5. Compile
super agent compile docs_qa_agent

# 6. Optimize
super agent optimize docs_qa_agent --auto medium

# 7. Run
super agent run docs_qa_agent

# Ask: "How do I optimize an agent with GEPA?"
```

---

## Next Steps

1. **Try the examples**: Start with documentation Q&A
2. **Read MCP docs**: https://modelcontextprotocol.io
3. **Explore vector stores**: [RAG Guide](rag.md)
4. **Optimize with GEPA**: [GEPA Guide](gepa-optimization.md)

### Related Guides

- [RAG Guide](rag.md)
- [GEPA Optimization](gepa-optimization.md)
- [Protocol-First Agents](protocol-first-agents.md)
- [Tool Development](tool-development.md)

---

**Status**: Complete MCP + RAG Guide ✅  
**MCP Servers**: All major servers documented ✅  
**Examples**: Practical workflows included ✅  
**GEPA Integration**: Optimization covered ✅

