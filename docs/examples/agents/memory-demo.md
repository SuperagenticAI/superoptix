# 🧠 Memory Demo Agent

The Memory Demo Agent showcases **multi-layered memory system** capabilities in SuperOptiX. This demo focuses specifically on how to configure and use memory systems for context retention and knowledge persistence.

## 🎯 **What This Demo Shows**

This demo demonstrates:

- 🧠 **Memory Integration**: How to configure memory systems in SuperOptiX agents
- 🏗️ **Multi-Layered Memory**: Short-term, long-term, and episodic memory
- 💭 **Context Retention**: How agents remember and use past information
- ⚙️ **Playbook Configuration**: How to set up memory in agent playbooks

## 🚀 **Setup Memory Demo**

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
# Pull the Memory demo agent
super agent pull memory_demo

# Compile the agent
super agent compile memory_demo

# Run the agent
super agent run memory_demo --goal "What memory systems are available and how do they work?"
```

## 🔧 **Memory Configuration in Playbook**

The Memory demo showcases how to configure memory systems in the agent playbook:

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

### **Memory Configuration**
```yaml
memory:
  enabled: true
  short_term:
    enabled: true
    max_tokens: 1000
    storage_type: in_memory
  long_term:
    enabled: true
    storage_type: local
    max_entries: 100
    persistence_path: ./data/memory/long_term
  episodic:
    enabled: true
    max_episodes: 50
    storage_type: local
    persistence_path: ./data/memory/episodic
```

**Key Memory Configuration Points**:

- **`enabled: true`**: Enables memory functionality
- ⚡ **`short_term`**: Immediate context retention (1000 tokens)
- 💾 **`long_term`**: Persistent knowledge storage (100 entries)
- 📚 **`episodic`**: Conversation episode memory (50 episodes)
- 🗄️ **`storage_type`**: Local file storage for persistence
- 📁 **`persistence_path`**: Local storage directories



## 🧠 **Memory: Your AI's Brain**

Memory systems give your AI agent the ability to learn, remember, and build relationships over time. It's like giving your AI a brain that grows smarter with each interaction:

### **🏗️ Three-Layer Memory Architecture**
- **⚡ Short-term Memory**: Holds the current conversation context (like your working memory)
- **💾 Long-term Memory**: Stores important facts and knowledge permanently (like your long-term memory)
- **📚 Episodic Memory**: Remembers past conversations and experiences (like your episodic memory)

### **🎯 Key Benefits**
- **🔄 Context Continuity**: Maintains conversation flow across multiple interactions
- **📈 Learning Over Time**: Builds knowledge and improves responses with experience
- **👤 Personalization**: Remembers user preferences and adapts accordingly
- **🔗 Relationship Building**: Creates meaningful, ongoing relationships with users

## 🔧 **Customizing Memory Configuration**

### **Adjust Memory Settings**
Edit `agents/memory_demo/playbook/memory_demo_playbook.yaml`:

```yaml
memory:
  short_term:
    max_tokens: 2000  # More context
  long_term:
    max_entries: 200  # More persistent storage
  episodic:
    max_episodes: 100  # More episodes
```

### **Change Storage Type**
```yaml
memory:
  long_term:
    storage_type: database  # Use database instead of local files
    connection_string: "sqlite:///memory.db"
```

### **Disable Memory Types**
```yaml
memory:
  short_term:
    enabled: false  # Disable short-term memory
  long_term:
    enabled: true
  episodic:
    enabled: true
```

## 🚨 **Troubleshooting Memory**

### **Common Issues**

1. **Ollama Server Not Running**
   ```bash
   # Check if Ollama server is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama server
   ollama serve
   ```

2. **Memory Not Working**
   ```bash
   # Check memory configuration
   super agent inspect memory_demo
   
   # Verify memory is enabled
   ```

3. **Memory Storage Issues**
   ```bash
   # Check memory storage directories
   ls -la ./data/memory/
   
   # Clear memory data if needed
   rm -rf ./data/memory/
   ```

### **Getting Help**
```bash
# Check agent status
super agent inspect memory_demo

# View agent logs
super agent logs memory_demo

# Get memory help
super agent --help
```

## 📚 Related Documentation

- [Agent Development](../guides/agent-development.md) - Building custom agents
