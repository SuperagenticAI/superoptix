# 🧠 Memory Systems Guide

SuperOptiX provides a **universal memory management system** that works across all 6 major agent frameworks, giving agents sophisticated state management and persistence capabilities.

**🌟 Key Achievement**: Same memory system works across DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, and DeepAgents!

## Overview

The memory system consists of four main components working together, **regardless of framework**:

### 1. Memory Backends
Provides flexible storage options:
- **FileBackend**: JSON/pickle file-based storage with TTL support
- **SQLiteBackend**: Relational database storage with automatic cleanup
- **RedisBackend**: High-performance in-memory storage (optional)

Key Features:
- Automatic TTL (time-to-live) management
- Thread-safe operations
- Pluggable architecture for easy extension
- Support for both JSON and binary serialization

### 2. Short-Term Memory
Manages temporary, session-based information:
- **LRU Cache**: Automatic eviction of least recently used items
- **Conversation History**: Tracks dialogue between user and agent
- **Working Memory**: Temporary context for current tasks
- **Retention Policies**: LRU, FIFO, or priority-based eviction

Use Cases:
- Recent conversation context
- Temporary task state
- User preferences for current session
- Quick access to frequently used information

### 3. Long-Term Memory
Persistent knowledge storage with semantic search:
- **Knowledge Categories**: Organized storage (facts, procedures, experiences, etc.)
- **Semantic Search**: Optional sentence-transformer embeddings for similarity search
- **Tagging System**: Flexible categorization and retrieval
- **Importance Scoring**: Weighted relevance for better retrieval

Use Cases:
- Learned facts and procedures
- User preferences and patterns
- Domain knowledge
- Historical insights and patterns

### 4. Episodic Memory
Tracks experiences and temporal sequences:
- **Episode Management**: Start, track, and end interaction episodes
- **Event Logging**: Detailed event tracking within episodes
- **Pattern Analysis**: Identify trends and patterns across episodes
- **Timeline Reconstruction**: Chronological view of agent activities

Use Cases:
- Interaction tracking
- Performance analysis
- Learning from past experiences
- Debugging and monitoring

### 5. Context Manager
Manages hierarchical context across different scopes:
- **Context Scopes**: Global, session, task, and local contexts
- **Context Stack**: Hierarchical context management
- **Automatic Persistence**: Context saved across sessions
- **Context Merging**: Intelligent combination of multiple context layers
- **Multi-Framework**: Works across all 6 frameworks

Scopes:
- **Global**: Persistent agent characteristics and learned patterns
- **Session**: Current session data and preferences
- **Task**: Specific task context and state
- **Local**: Temporary, function-specific context

## 🔧 Multi-Framework Memory Support

### **Universal Memory Configuration**

Memory works the same way across all frameworks! Just add the `memory` section to your playbook:

=== "🔬 DSPy"
    ```yaml
    spec:
      target_framework: dspy
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

=== "🤖 OpenAI SDK"
    ```yaml
    spec:
      target_framework: openai
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

=== "👥 CrewAI"
    ```yaml
    spec:
      target_framework: crewai
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

=== "🔮 Google ADK"
    ```yaml
    spec:
      target_framework: google-adk
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

=== "🏢 Microsoft"
    ```yaml
    spec:
      target_framework: microsoft
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

=== "🌊 DeepAgents"
    ```yaml
    spec:
      target_framework: deepagents
      memory:
        enabled: true
        backend: sqlite
        short_term:
          max_size: 100
          retention_policy: lru
        long_term:
          enabled: true
          semantic_search: true
    ```

### **Universal Workflow**

```bash
# Same workflow for ALL frameworks!
super agent compile <agent_name>  # Memory automatically configured
super agent evaluate <agent_name>  # Test with memory persistence
super agent optimize <agent_name> --auto medium  # GEPA optimizes memory-enhanced agents
super agent run <agent_name>  # Use with memory persistence
```

### **Memory + GEPA Optimization**

Memory-enhanced agents can be optimized with GEPA:

```yaml
spec:
  target_framework: openai  # Works with ANY framework!
  memory:
    enabled: true
    backend: sqlite
    long_term:
      enabled: true
      semantic_search: true
  optimization:
    optimizer:
      name: GEPA  # Optimize memory-enhanced agents!
      params:
        auto: medium
```

## Key Features

### 1. Multi-Backend Support
- File-based storage for simplicity
- SQLite for structured data and queries
- Redis for high-performance scenarios
- Easy to extend with new backends

### 2. Semantic Search
- Optional sentence-transformer integration
- Similarity-based knowledge retrieval
- Automatic embedding generation
- Fallback to keyword search

### 3. Automatic Context Management
- Hierarchical context scopes
- Intelligent context merging
- Automatic persistence
- TTL-based expiration

### 4. Interaction Tracking
- Episode-based interaction management
- Detailed event logging
- Pattern recognition
- Performance analytics

### 5. Learning Capabilities
- Insight extraction from interactions
- Pattern recognition and storage
- Feedback integration
- Continuous improvement

### 6. Production Ready
- Thread-safe operations
- Automatic cleanup and maintenance
- Comprehensive error handling
- Memory usage monitoring

## Usage Examples

### Basic Memory Operations
```python
from superoptix.memory import AgentMemory

memory = AgentMemory("assistant_agent")

# Store knowledge
memory.remember(
    "DSPy is a framework for programming with foundation models",
    memory_type="long",
    category="frameworks",
    tags=["dspy", "llm", "programming"]
)

# Recall relevant information
results = memory.recall("DSPy programming", limit=5)
for result in results:
    print(f"[{result['similarity']:.2f}] {result['content']}")
```

### Interaction Tracking
```python
# Start tracking an interaction
episode_id = memory.start_interaction({
    "user_id": "user123",
    "session_type": "technical_help"
})

# Add events during the interaction
memory.add_interaction_event("question_asked", "User asked about Python decorators")
memory.add_interaction_event("answer_provided", "Provided explanation with examples")
memory.add_interaction_event("feedback_received", "User found answer helpful")

# End the interaction with results
memory.end_interaction({
    "success": True,
    "satisfaction_score": 0.9,
    "resolution_time": 120
})
```

### Learning from Feedback
```python
# Learn insights from user interactions
insights = [
    "Users prefer code examples over theoretical explanations",
    "Step-by-step tutorials are highly effective",
    "Visual diagrams enhance understanding"
]

patterns = {
    "effective_teaching_methods": ["examples", "step-by-step", "visual"],
    "user_preferences": {"format": "practical", "detail_level": "medium"}
}

memory.learn_from_interaction(insights, patterns)
```

### Memory Analytics
```python
# Get comprehensive memory statistics
summary = memory.get_memory_summary()
print(f"Total interactions: {summary['interaction_count']}")
print(f"Knowledge items: {summary['long_term_memory']['total_items']}")
print(f"Active episodes: {summary['episodic_memory']['active_episodes']}")

# Cleanup expired data
cleanup_stats = memory.cleanup_memory()
print(f"Cleaned up {cleanup_stats['expired_short_term']} expired items")
```

## Configuration

### Basic Memory Control

#### Disable Memory Completely
```yaml
agent_capabilities:
  memory:
    enabled: false  # No memory system at all
```

#### Enable Memory with Defaults
```yaml
agent_capabilities:
  memory:
    enabled: true  # Uses SQLite backend with standard settings
```

### Backend Configuration

#### SQLite Backend (Default)
```yaml
memory:
  backend:
    type: sqlite
    config:
      db_path: ".superoptix/agent_memory.db"
```

#### File Backend
```yaml
memory:
  backend:
    type: file
    config:
      storage_path: ".superoptix/memory"
```

#### Redis Backend (High Performance)
```yaml
memory:
  backend:
    type: redis
    config:
      host: "localhost"
      port: 6379
      db: 0
      password: "optional_password"
      prefix: "agent_name:"
```

### Memory Component Configuration

#### Short-term Memory
```yaml
memory:
  short_term:
    enabled: true
    capacity: 100                    # Max items
    retention_policy: lru            # lru|fifo|priority
    max_conversation_length: 50      # Conversation history
    default_ttl: 3600               # 1 hour TTL
```

#### Long-term Memory
```yaml
memory:
  long_term:
    enabled: true
    enable_embeddings: true          # Semantic search
    embedding_model: "all-MiniLM-L6-v2"
    search:
      default_limit: 10
      min_similarity_threshold: 0.3
```

#### Episodic Memory
```yaml
memory:
  episodic:
    enabled: true
    auto_start_episodes: true
    episode_boundary: interaction    # time|task|manual|interaction
    max_episode_duration: 3600      # 1 hour
```

### Common Use Case Configurations

#### Development Agent (Full Memory)
```yaml
memory:
  enabled: true
  backend:
    type: sqlite
  short_term:
    capacity: 200
    max_conversation_length: 100
  long_term:
    enable_embeddings: true
    categories:
      - name: "code_patterns"
      - name: "best_practices"
      - name: "user_preferences"
  episodic:
    pattern_analysis:
      enabled: true
```

#### Customer Service Agent (Conversation Focus)
```yaml
memory:
  enabled: true
  short_term:
    capacity: 150
    max_conversation_length: 200
  long_term:
    categories:
      - name: "customer_preferences"
      - name: "common_issues"
  security:
    pii_detection: true
```

#### Simple Task Agent (No Memory)
```yaml
memory:
  enabled: false
```

#### High-Performance Agent (Redis)
```yaml
memory:
  enabled: true
  backend:
    type: redis
    config:
      host: "redis-cluster.example.com"
      port: 6379
  performance:
    cache_embeddings: true
    batch_operations: true
    connection_pooling: true
```

## Best Practices

### 1. Memory Configuration by Use Case

- **Development Agents**: Enable all memory types with longer retention
- **Customer Service**: Focus on conversation history and user preferences  
- **Data Analysis**: Emphasize pattern recognition and episodic learning
- **Simple Tasks**: Disable memory for lightweight operation

### 2. Performance Optimization

- Use Redis backend for high-throughput scenarios
- Enable embedding caching for semantic search heavy workloads
- Configure appropriate retention policies to manage storage
- Use batch operations for bulk memory updates

### 3. Security Considerations

- Enable PII detection for customer-facing agents
- Use encryption for sensitive data
- Configure appropriate retention policies for compliance
- Enable audit logging for regulated environments

### 4. Memory Design
- Use short-term memory for session-specific data
- Use long-term memory for persistent knowledge
- Use episodic memory for interaction tracking
- Use context for hierarchical state management

### 5. Data Management
- Validate data before storage
- Use appropriate categories and tags
- Implement data versioning
- Regular backup of memory data

## Troubleshooting

### Common Issues

#### Memory Not Working
```python
# Check if memory is enabled
memory = AgentMemory("test_agent")
print(f"Memory enabled: {memory.is_enabled()}")

# Check backend status
print(f"Backend status: {memory.get_backend_status()}")
```

#### Performance Issues
```python
# Monitor memory usage
stats = memory.get_memory_stats()
print(f"Memory usage: {stats['usage_percent']}%")
print(f"Items in memory: {stats['total_items']}")

# Clean up if needed
memory.cleanup()
```

#### Data Persistence Issues
```python
# Check if data is being saved
memory.remember("test data", memory_type="long")
memory.save_memory_state()

# Verify data persistence
results = memory.recall("test data")
print(f"Found {len(results)} results")
```

#### Poor Search Results
- Adjust similarity thresholds
- Verify embedding model is loaded
- Check if fallback to keyword search is working

#### Memory Conflicts
- Ensure separate retrieval contexts
- Configure different similarity thresholds
- Use distinct embedding models if needed

### Debug Commands

```python
# Check memory status
agent.memory.get_memory_summary()

# Export memory state for debugging
agent.memory.save_memory_state()

# Clear specific memory types
agent.memory.short_term.clear()
agent.memory.long_term.clear()

# Enable verbose logging
agent_config = {
    "memory": {
        "debug": {
            "verbose_logging": True,
            "trace_memory_operations": True
        }
    }
}
```

## Performance Considerations

### Memory Usage
- Short-term memory: ~1MB per 1000 items
- Long-term memory: Depends on content size and embeddings
- Context management: Minimal overhead
- Episodic memory: ~10KB per episode

### Optimization Tips
1. **Use appropriate TTL values** for short-term memory
2. **Enable embeddings only when needed** for semantic search
3. **Regular cleanup** to prevent memory bloat
4. **Choose appropriate backend** for your use case
5. **Monitor memory statistics** for optimization opportunities

## Quick Commands

### Check Memory Status
```python
agent.memory.get_memory_summary()
```

### Clear Memory
```python
agent.memory.clear_all_memory()
```

### Manual Memory Operations
```python
# Store knowledge
agent.memory.remember("Important fact", memory_type="long", category="facts")

# Recall information
results = agent.memory.recall("search query", memory_type="all")

# Start interaction tracking
episode_id = agent.memory.start_interaction({"user": "john_doe"})
```

## 📚 Related Documentation

- [Agent Development Guide](agent-development.md) - Complete agent development workflow
- [RAG Guide](rag.md) - Knowledge retrieval systems
- [Quick Start Guide](../quick-start.md) - Getting started with SuperOptiX 