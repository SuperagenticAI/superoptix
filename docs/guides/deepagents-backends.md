# 🗄️ DeepAgents Backend Configuration Guide

**Complete guide to DeepAgents 0.2.0 pluggable backends for persistent memory, filesystem access, and advanced storage strategies.**

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Backend Types](#backend-types)
4. [Complete Examples](#complete-examples)
5. [Advanced Patterns](#advanced-patterns)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

### What's New in DeepAgents 0.2.0?

DeepAgents 0.2.0 introduces a **pluggable backend abstraction** that transforms how agents store and access files. Instead of being limited to ephemeral virtual filesystems, you can now:

**Persist memory** across conversations (StoreBackend)  
**Access real files** on your local filesystem (FilesystemBackend)  
**Hybrid strategies** with different storage for different paths (CompositeBackend)  
**Custom backends** for databases, S3, remote VMs, etc.

**Source:** [LangChain Blog - Doubling Down on DeepAgents](https://blog.langchain.com/doubling-down-on-deepagents/)

### Why Backends Matter

**Before 0.2.0:**
```
Agent writes to /notes.txt → Stored in LangGraph state
New conversation starts → /notes.txt is gone ```

**After 0.2.0:**
```
Agent writes to /memories/notes.txt → Stored in persistent database
New conversation starts → /memories/notes.txt still there! ```

---

## 🚀 Quick Start

### Basic Setup (Default Behavior)

If you don't specify a backend, DeepAgents uses `StateBackend` (ephemeral, same as 0.1.0):

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Basic Research Agent
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
  
  # No backend config = uses StateBackend (default)
```

### Enable Persistent Memory

Add just 2 lines to enable persistent memory:

```yaml
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
  
  # Enable persistent storage
  backend:
    type: store  # ✨ That's it!
```

Now everything the agent writes persists across conversations!

---

## 📦 Backend Types

### StateBackend (Default)

**Storage:** LangGraph state (ephemeral, per-thread)  
**Persistence:** Within conversation only  
**Best For:** Temporary scratch space, single-conversation agents

**Configuration:**
```yaml
backend:
  type: state
```

**Behavior:**
- Fast (in-memory)
- Checkpointed within thread
- Lost when thread ends
- Not shared across threads

**Use Cases:**
- Simple Q&A agents
- Temporary calculations
- Draft generation
- Single-session tasks

---

### StoreBackend (Persistent)

**Storage:** LangGraph store (persistent database)  
**Persistence:** Across all conversations  
**Best For:** Long-term memory, learning agents, chatbots

**Configuration:**
```yaml
backend:
  type: store
```

**Behavior:**
- Persistent across threads
- Shared between conversations
- Survives restarts
- ⚡ Slightly slower (database)

**Use Cases:**
- Chatbots with memory
- Research assistants that learn
- Agents that build knowledge over time
- Multi-session projects

---

### FilesystemBackend (Local Files)

**Storage:** Actual local filesystem  
**Persistence:** Real files on disk  
**Best For:** Code analysis, file editing, project work

**Configuration:**
```yaml
backend:
  type: filesystem
  root_dir: /Users/local/my_project
```

**Behavior:**
- Access real project files
- Changes immediately visible
- Works with other tools (git, IDE, etc.)
- ⚠️  Security: Agent can modify actual files!

**Use Cases:**
- Code review agents
- Documentation generators
- File refactoring
- Project analysis

---

### CompositeBackend (Hybrid)

**Storage:** Route different paths to different backends  
**Persistence:** Mixed strategies  
**Best For:** Complex agents with different storage needs

**Configuration:**
```yaml
backend:
  type: composite
  default: state              # Default for unspecified paths
  routes:
    /memories/: store         # Persistent memories
    /project/: filesystem     # Real project files
    /cache/: state            # Temporary files
```

**Behavior:**
- Best of all worlds
- Optimized for each data type
- Flexible and powerful
- 🔧 Requires more configuration

**Use Cases:**
- Development assistants
- Complex research agents
- Multi-domain agents
- Production systems

---

## 📚 Complete Examples

### Example 1: Persistent Chatbot

**Scenario:** Build a chatbot that remembers user preferences and previous conversations.

**Playbook:**
```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Persistent Chatbot
  description: Chatbot with long-term memory
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
    temperature: 0.7
  
  # Persistent memory across all conversations
  backend:
    type: store
  
  persona:
    role: Personal AI Assistant
    goal: Help users and remember their preferences over time
    system_prompt: |
      You are a personal AI assistant with long-term memory.
      
      IMPORTANT: Save important information to these files:
      - /user_profile.txt - User's name, preferences, interests
      - /conversation_history.txt - Key topics from past conversations
      - /reminders.txt - User's reminders and to-dos
      
      Before responding, ALWAYS:
      1. Check /user_profile.txt to personalize your response
      2. Check /conversation_history.txt for context
      3. Update files with new information learned
```

**Usage:**
```bash
# First conversation
super agent run persistent_chatbot --goal "Hi! My name is Alice and I love Python."

# Agent writes to /user_profile.txt:
# Name: Alice
# Interests: Python programming

# Days later, new conversation
super agent run persistent_chatbot --goal "What's my name?"

# Agent reads /user_profile.txt
# Response: "Your name is Alice! And I remember you love Python programming."
```

**Why It Works:**
- `StoreBackend` persists files across all threads
- Agent can read previous data
- Builds knowledge over time

---

### Example 2: Code Review Agent

**Scenario:** Agent analyzes actual project files and suggests improvements.

**Playbook:**
```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Code Review Agent
  description: Analyzes real project files
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-pro  # Pro for better analysis
    temperature: 0.3
  
  # Access real project files
  backend:
    type: filesystem
    root_dir: /Users/local/my_project
  
  persona:
    role: Senior Code Reviewer
    goal: Analyze code for bugs, security issues, and best practices
    system_prompt: |
      You are a senior code reviewer with access to the project files.
      
      Available in your filesystem:
      - /src/ - Source code
      - /tests/ - Test files
      - /README.md - Project documentation
      - /requirements.txt - Dependencies
      
      When reviewing:
      1. Read the relevant files using ls and read_file
      2. Analyze for:
         - Security vulnerabilities
         - Performance issues
         - Code style violations
         - Missing tests
      3. Provide specific, actionable feedback
      4. If appropriate, suggest or make improvements
```

**Usage:**
```bash
# Analyze a specific file
super agent run code_review_agent --goal "Review src/auth.py for security issues"

# Agent reads actual file from disk:
# - /src/auth.py
# Response: "Found 3 security concerns in src/auth.py..."

# Analyze entire codebase
super agent run code_review_agent --goal "Analyze the entire codebase and write a report to /code_review_report.md"

# Agent:
# Lists files with ls /src/
# Reads each file
# Writes report to actual file: /Users/local/my_project/code_review_report.md
```

**Why It Works:**
- `FilesystemBackend` gives access to real files
- Changes are immediately visible in IDE
- Can be used with git, etc.

**⚠️ Security Note:** Agent can modify actual files! Use carefully.

---

### Example 3: Research Agent with Hybrid Storage

**Scenario:** Advanced research assistant that uses optimal storage for each data type.

**Playbook:**
```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Advanced Research Agent
  description: Hybrid storage for optimal performance
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
    temperature: 0.7
  
  # Hybrid storage strategy
  backend:
    type: composite
    default: state                # Scratch space for current conversation
    routes:
      /memories/: store          # Long-term research knowledge
      /papers/: filesystem       # Access to local paper PDFs
      /cache/: state             # Temporary internet search results
  
  persona:
    role: AI Research Assistant
    goal: Conduct thorough research and build long-term knowledge
    system_prompt: |
      You are an AI research assistant with advanced storage capabilities.
      
      STORAGE GUIDELINES:
      
      📁 /memories/ (Persistent Database)
      - Save important research findings
      - Store literature reviews
      - Keep track of research topics explored
      - Build cumulative knowledge over time
      
      📂 /papers/ (Local Filesystem)
      - Access PDF papers in /Users/local/research/papers/
      - Read abstracts and summaries
      - Reference actual academic papers
      
      💾 /cache/ (Temporary)
      - Store internet search results
      - Keep intermediate calculations
      - Temporary notes (cleared each conversation)
      
      🗂️ / (Scratch Space)
      - Current conversation context
      - Draft responses
      - Work in progress
      
      WORKFLOW:
      1. Check /memories/ for previous research on topic
      2. Search for new information
      3. Save results to /cache/ temporarily
      4. If information is important, save to /memories/
      5. Access /papers/ for academic sources
```

**Advanced Configuration (in Python):**
```python
# For more control, configure in playbook
backend:
  type: composite
  default: state
  routes:
    /memories/: store
    /papers/: filesystem
    /cache/: state
  
  # Root dir for filesystem backend
  root_dir: /Users/local/research
```

**Usage:**
```bash
export GOOGLE_API_KEY="your-key"

# First research session
super agent run advanced_research_agent --goal "Research transformer architectures. Save key findings."

# Agent workflow:
# Checks /memories/transformer_research.txt (not found)
# Searches for information
# Saves results to /cache/search_results.txt
# Writes summary to /memories/transformer_research.txt (persisted!)
# May read from /papers/attention_is_all_you_need.pdf

# Week later, follow-up research
super agent run advanced_research_agent --goal "What did I learn about transformers?"

# Agent workflow:
# Reads /memories/transformer_research.txt (found - from last week!)
# Response: "Based on your previous research, transformers..."
# Can build upon previous knowledge

# Analyze specific paper
super agent run advanced_research_agent --goal "Summarize the paper in /papers/bert.pdf"

# Agent reads actual file from /Users/local/research/papers/bert.pdf
```

**Why It Works:**
- `/memories/` persists across weeks (StoreBackend)
- `/papers/` accesses real PDFs (FilesystemBackend)
- `/cache/` is fast and ephemeral (StateBackend)
- `/` is conversation-scoped (StateBackend)

---

## 🎓 Advanced Patterns

### Pattern 1: Learning Agent

**Goal:** Agent that improves over time by learning from interactions.

```yaml
backend:
  type: store

persona:
  system_prompt: |
    You are a learning assistant. After each interaction:
    
    1. Read /knowledge/learned_facts.txt
    2. Add new facts you learned
    3. Write back to /knowledge/learned_facts.txt
    
    Over time, your knowledge will grow!
```

**Result:** Agent builds cumulative knowledge base.

---

### Pattern 2: Project-Aware Agent

**Goal:** Agent that understands your entire project structure.

```yaml
backend:
  type: composite
  default: state
  routes:
    /project/: filesystem
  
  root_dir: /Users/local/my_app

persona:
  system_prompt: |
    You have access to the entire project in /project/.
    
    Key files:
    - /project/src/ - Source code
    - /project/tests/ - Tests
    - /project/docs/ - Documentation
    
    You can read and modify these files directly!
```

**Result:** Agent sees actual project, can make real changes.

---

### Pattern 3: Multi-Session Research

**Goal:** Research project that spans multiple days.

```yaml
backend:
  type: composite
  default: state
  routes:
    /research/: store
    /output/: filesystem
  
  root_dir: /Users/local/research_output

persona:
  system_prompt: |
    You are conducting a long-term research project.
    
    /research/ - Persistent research notes (cross-session)
    /output/ - Final reports written to disk
    / - Current session workspace
    
    At the end of each session, summarize findings to /research/session_N_summary.txt
```

**Result:** Research builds across sessions, final reports saved to disk.

---

### Pattern 4: Secure Sandbox

**Goal:** Agent can work freely but can't access sensitive files.

```yaml
backend:
  type: filesystem
  root_dir: /tmp/agent_sandbox  # Isolated directory

persona:
  system_prompt: |
    You can create and modify files freely.
    All files are in a secure sandbox.
```

**Result:** Agent has filesystem access but can't touch important files.

---

## 🔧 Configuration Reference

### Complete Playbook Schema

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Example Agent
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
  
  # Backend configuration (NEW in 0.2.0)
  backend:
    type: state | store | filesystem | composite
    
    # For filesystem backend only:
    root_dir: /path/to/directory
    
    # For composite backend only:
    default: state | store | filesystem
    routes:
      /path1/: store
      /path2/: filesystem
      /path3/: state
```

### Backend Type Matrix

| Backend | Persistence | Speed | Shared | Use Case |
|---------|-------------|-------|--------|----------|
| **state** | Thread only | ⚡⚡⚡ Very Fast | No | Scratch space |
| **store** | Forever | ⚡⚡ Fast | Yes | Long-term memory |
| **filesystem** | Forever | ⚡⚡ Fast | Yes | Real files |
| **composite** | Mixed | ⚡⚡ Fast | Mixed | Best of all |

---

## 🚨 Troubleshooting

### Issue 1: "Backend import failed"

**Error:**
```
⚠️  Backend import failed: No module named 'superoptix.vendor.deepagents.backends'
```

**Solution:**
```bash
# Update SuperOptiX
cd /Users/local/superagentic/SuperOptiX
pip install -e .

# Verify backends are available
python -c "from superoptix.vendor.deepagents.backends import state; print('Backends available')"
```

---

### Issue 2: Files not persisting

**Problem:** Files disappear between conversations

**Check:**
```yaml
# Make sure you're using store, not state
backend:
  type: store  # NOT state!
```

---

### Issue 3: Can't access local files

**Error:**
```
FileNotFoundError: /Users/local/project/file.txt
```

**Solution:**
```yaml
backend:
  type: filesystem
  root_dir: /Users/local/project  # Must specify root!
```

---

### Issue 4: Permission denied

**Error:**
```
PermissionError: /etc/password
```

**Cause:** FilesystemBackend respects OS permissions

**Solution:**
- Use appropriate `root_dir`
- Check file permissions
- Don't point to system directories

---

## 📊 Performance Tips

### Choose the Right Backend

```yaml
# Fast scratch space
backend:
  type: state

# Persistent but slightly slower
backend:
  type: store

# Real files (filesystem speed)
backend:
  type: filesystem
```

### Use Composite for Optimal Performance

```yaml
# Optimize for each data type
backend:
  type: composite
  default: state           # Fast default
  routes:
    /memories/: store     # Only what needs persistence
    /big_files/: filesystem  # Offload large files
```

### Limit Filesystem Scope

```yaml
# Good: Specific directory
backend:
  type: filesystem
  root_dir: /Users/local/project/src

# Bad: Entire filesystem
backend:
  type: filesystem
  root_dir: /
```

---

## 🎯 Best Practices

### Do

1. **Use StateBackend** for temporary, single-conversation agents
2. **Use StoreBackend** for chatbots and learning agents
3. **Use FilesystemBackend** with specific `root_dir`
4. **Use CompositeBackend** for complex production agents
5. **Document storage strategy** in system prompt
6. **Test with small `root_dir`** first

### Don't

1. **Don't use FilesystemBackend on root** (`/`)
2. **Don't store sensitive data** without encryption
3. **Don't assume infinite storage** in StoreBackend
4. **Don't mix backends** without CompositeBackend
5. **Don't give write access** to critical files
6. **Don't forget to backup** persistent data

---

## 🚀 Migration Guide

### From 0.1.0 to 0.2.0

**No breaking changes!** Old playbooks work as-is.

**To add persistence:**

```yaml
# Old (still works)
spec:
  target_framework: deepagents
  language_model:
    model: gemini-2.5-flash

# New (with persistence)
spec:
  target_framework: deepagents
  language_model:
    model: gemini-2.5-flash
  backend:
    type: store  # Add this!
```

**Steps:**
1. Add `backend` section to playbook
2. Recompile: `super agent compile my_agent --framework deepagents`
3. Test: `super agent run my_agent --goal "test"`
4. Verify persistence works

---

## 📚 Resources

- [DeepAgents 0.2.0 Announcement](https://blog.langchain.com/doubling-down-on-deepagents/)
- [DeepAgents GitHub](https://github.com/langchain-ai/deepagents)
- [SuperOptiX DeepAgents Integration Guide](deepagents-integration.md)
- [Gemini Configuration Guide](../../GEMINI_CONFIGURATION_GUIDE.md)

---

## 💡 Next Steps

1. **Try the examples** above
2. **Experiment with different backends**
3. **Build a persistent chatbot**
4. **Create a code analysis agent**
5. **Design your hybrid storage strategy**

---

**Questions?** Check our [FAQ](../faq.md) or [Troubleshooting Guide](../troubleshooting.md)

**Ready to build?** Start with the [DeepAgents Quick Start](deepagents-integration.md)!

