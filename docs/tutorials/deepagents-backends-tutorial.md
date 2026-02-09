# 🗄️ DeepAgents Backends Tutorial

**Complete hands-on tutorial for DeepAgents 0.2.0 pluggable backends. Learn how to build agents with persistent memory, filesystem access, and hybrid storage strategies.**

---

## 📖 What You'll Learn

By the end of this tutorial, you'll know how to:

- Configure all 4 backend types (state, store, filesystem, composite)
- Build a chatbot with persistent memory
- Create a code review agent with real file access
- Design hybrid storage strategies
- Optimize backends for GEPA
- Deploy production-ready agents

**Time:** 30 minutes  
**Level:** Intermediate

---

## 🎯 Prerequisites

### Required

```bash
# Install SuperOptiX with DeepAgents
pip install superoptix[frameworks-deepagents]

# Verify version (must be 0.2.0+)
python -c "import deepagents; print(deepagents.__version__)"

# Set Gemini API key (FREE)
export GOOGLE_API_KEY="your-gemini-key"
```

### Initialize Project

```bash
super init deepagents_tutorial
cd deepagents_tutorial
```

---

## 📚 Tutorial 1: Persistent Chatbot (StoreBackend)

### Goal
Build a chatbot that remembers users across conversations.

### Step 1: Create Playbook

```yaml
# Save as: agents/my_chatbot/playbook/my_chatbot_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: My Persistent Chatbot
  id: my_chatbot
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash  # Check provider docs for latest models
  
  # Enable persistent memory
  backend:
    type: store
  
  input_fields:
    - name: query
      type: str
  
  output_fields:
    - name: response
      type: str
  
  persona:
    system_prompt: |
      You are a personal assistant with PERSISTENT MEMORY.
      
      Files you should use:
      - /user_profile.txt - User's name, preferences, interests
      - /history.txt - Topics discussed before
      
      WORKFLOW:
      1. Read /user_profile.txt first (use read_file)
      2. Personalize response based on what you know
      3. Update /user_profile.txt if you learn something new
      
      Remember: Files PERSIST FOREVER across all conversations!
```

### Step 2: Compile

```bash
super agent compile my_chatbot --framework deepagents
```

**What happened:**
- Template generates Python code
- Includes `_create_backend()` method
- Configures StoreBackend

### Step 3: First Conversation

```bash
super agent run my_chatbot --goal "Hi! My name is Bob and I'm a Python developer."
```

**Agent's internal actions:**
1. Tries to read `/user_profile.txt` (doesn't exist yet)
2. Processes query
3. **Writes to `/user_profile.txt`:**
   ```
   Name: Bob
   Profession: Python developer
   First contact: 2025-10-29
   ```
4. Responds: "Nice to meet you, Bob! I see you're a Python developer..."

**File location:** Stored in LangGraph store (persistent database)

### Step 4: Second Conversation (Hours Later)

```bash
super agent run my_chatbot --goal "What's my name?"
```

**Agent's internal actions:**
1. **Reads `/user_profile.txt`** (still there! )
2. Finds: "Name: Bob"
3. Responds: "Your name is Bob!"

### Step 5: Build on Memory

```bash
super agent run my_chatbot --goal "Suggest a Python project for me"
```

**Agent's internal actions:**
1. Reads `/user_profile.txt`
2. Sees: "Profession: Python developer"
3. Personalizes response: "Given your Python background, I suggest..."

### Step 6: Verify Persistence

```bash
# Restart everything, new terminal, next day...
super agent run my_chatbot --goal "Who am I?"
# Response: "You're Bob, a Python developer!" 
# The memory persisted!
```

---

## 📁 Tutorial 2: Code Review Agent (FilesystemBackend)

### Goal
Build an agent that analyzes actual project files.

### Step 1: Setup Test Project

```bash
# Create a sample project to review
mkdir -p /tmp/demo_project/src
cat > /tmp/demo_project/src/app.py << 'EOF'
def login(username, password):
    # TODO: Add input validation
    query = f"SELECT * FROM users WHERE username='{username}'"  # SQL injection!
    result = db.execute(query)
    return result

def process_data(data):
    # Memory leak - list grows indefinitely
    global_cache.append(data)
    return data
EOF

cat > /tmp/demo_project/README.md << 'EOF'
# Demo Project
A sample Python application for testing code review agents.
EOF
```

### Step 2: Create Playbook

```yaml
# Save as: agents/code_reviewer/playbook/code_reviewer_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Code Reviewer
  id: code_reviewer
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-pro  # Pro for better analysis
    temperature: 0.3
  
  # Access real project files
  backend:
    type: filesystem
    root_dir: /tmp/demo_project
  
  input_fields:
    - name: query
      type: str
  
  output_fields:
    - name: report
      type: str
  
  persona:
    system_prompt: |
      You are a senior code reviewer with REAL FILESYSTEM ACCESS.
      
      Available in /tmp/demo_project:
      - /src/ - Source code
      - /README.md - Documentation
      
      Available tools:
      - ls /src/ - List files
      - read_file /src/app.py - Read code
      - grep_search "TODO" /src/ - Find patterns
      - write_file /review.md - Write reports
      
      SECURITY CHECKLIST:
      - SQL injection
      - XSS vulnerabilities
      - Memory leaks
      - Input validation
      - Error handling
      
      Always provide:
      - Specific file paths and line numbers
      - Severity (Critical/High/Medium/Low)
      - Code examples
      - Recommended fixes
```

### Step 3: Compile & Review

```bash
super agent compile code_reviewer --framework deepagents

# Review the code
super agent run code_reviewer --goal "Review src/app.py for security issues"
```

**Agent's internal actions:**
1. **Reads actual file:** `/tmp/demo_project/src/app.py`
2. Analyzes code
3. Finds issues:
   - SQL injection (line 3)
   - Missing input validation
   - Memory leak (line 10)
4. Responds with detailed findings

**Example response:**
```
Found 2 CRITICAL and 1 HIGH severity issues:

1. SQL INJECTION - CRITICAL
   File: /src/app.py, Line 3
   Issue: Unsanitized user input in SQL query
   
   Vulnerable code:
   query = f"SELECT * FROM users WHERE username='{username}'"
   
   Fix: Use parameterized queries:
   query = "SELECT * FROM users WHERE username=?"
   result = db.execute(query, (username,))

2. MEMORY LEAK - HIGH
   File: /src/app.py, Line 10
   Issue: global_cache grows indefinitely
   ...
```

### Step 4: Generate Report

```bash
super agent run code_reviewer --goal "Analyze all files and write a complete report to /security_report.md"
```

**Agent's internal actions:**
1. Runs: `ls /src/`
2. Reads each file
3. Analyzes all code
4. **Writes to:** `/tmp/demo_project/security_report.md` (REAL FILE!)

**Verify it:**
```bash
cat /tmp/demo_project/security_report.md
# You'll see the full security report!

# It's a real file - use it with git, share it, etc.
```

---

## 🔀 Tutorial 3: Hybrid Research Agent (CompositeBackend)

### Goal
Build a research agent with optimal storage for each data type.

### Step 1: Setup Research Workspace

```bash
# Create directory structure
mkdir -p /tmp/research_workspace/papers

# Add a sample paper (or use your own PDFs)
echo "# Sample Research Paper
This is a sample academic paper about AI agents.
" > /tmp/research_workspace/papers/agents_paper.txt
```

### Step 2: Create Playbook

```yaml
# Save as: agents/researcher/playbook/researcher_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Advanced Researcher
  id: researcher
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash  # Check provider docs for latest models
  
  # Hybrid storage strategy
  backend:
    type: composite
    default: state                # Scratch space
    routes:
      /memories/: store          # Persistent findings
      /papers/: filesystem       # Academic papers
      /cache/: state             # Temporary data
    root_dir: /tmp/research_workspace
  
  input_fields:
    - name: query
      type: str
  
  output_fields:
    - name: report
      type: str
  
  persona:
    system_prompt: |
      You are a research agent with HYBRID STORAGE:
      
      📚 /memories/ (DATABASE - Persistent)
      - Research findings that should last forever
      - Literature reviews
      - Key insights
      Example: write_file /memories/ai_research.txt "Summary: ..."
      
      📂 /papers/ (FILESYSTEM - Real Files)
      - Access actual papers in /tmp/research_workspace/papers/
      - Read PDFs and documents
      Example: read_file /papers/agents_paper.txt
      
      💾 /cache/ (STATE - Temporary)
      - Internet search results
      - Temporary calculations
      Example: write_file /cache/search.txt "Results: ..."
      
      🗂️ / (STATE - Scratch)
      - Current conversation only
      Example: write_file /draft.txt "Work in progress..."
      
      RESEARCH WORKFLOW:
      1. Check /memories/research_index.txt for prior work
      2. Search internet → save to /cache/
      3. Read /papers/ for academic sources
      4. Save important findings → /memories/
      5. Keep /memories/research_index.txt updated
```

### Step 3: Compile

```bash
super agent compile researcher --framework deepagents
```

### Step 4: First Research Session

```bash
super agent run researcher --goal "Research LangGraph. Save important findings for future reference."
```

**Agent's actions:**
1. Checks `/memories/research_index.txt` (empty - first time)
2. Searches for information about LangGraph
3. Saves results to `/cache/search_results.txt` (temporary)
4. Checks `/papers/` for relevant papers
5. **Writes to `/memories/langgraph_research.txt`** (PERSISTS!)
6. **Updates `/memories/research_index.txt`:**
   ```
   Research Topics:
   - LangGraph: See /memories/langgraph_research.txt (2025-10-29)
   ```

**File locations:**
- `/memories/` → LangGraph store (database)
- `/papers/` → `/tmp/research_workspace/papers/` (real files)
- `/cache/` → LangGraph state (ephemeral)

### Step 5: Access Papers

```bash
super agent run researcher --goal "Summarize the paper in /papers/agents_paper.txt"
```

**Agent's actions:**
1. **Reads REAL file:** `/tmp/research_workspace/papers/agents_paper.txt`
2. Summarizes content
3. May save summary to `/memories/` for future reference

### Step 6: Week Later - Recall Research

```bash
# New conversation, days later
super agent run researcher --goal "What did I research about LangGraph?"
```

**Agent's actions:**
1. Reads `/memories/research_index.txt` (STILL THERE! )
2. Sees: "LangGraph: See /memories/langgraph_research.txt"
3. **Reads `/memories/langgraph_research.txt`** (PERSISTS!)
4. Responds: "Based on your research from October 29th, LangGraph is..."

### Step 7: Verify Storage Locations

```bash
# Check ephemeral cache (will be empty - it's gone)
# /cache/ files don't persist

# Check persistent memories (still there!)
# /memories/ files persist in database

# Check filesystem papers (real files)
ls /tmp/research_workspace/papers/
# agents_paper.txt  ← Still there!
```

---

## 🎓 Tutorial 4: GEPA Optimization with Backends

### Does GEPA Work with Backends?

**YES!** GEPA optimizes the `system_prompt` regardless of backend type.

### Example: Optimize Persistent Chatbot

```bash
# Pull demo agent
super agent pull chatbot_persistent

# Compile
super agent compile chatbot_persistent --framework deepagents

# Evaluate baseline
super agent evaluate chatbot_persistent

# Optimize with GEPA
super agent optimize chatbot_persistent --auto medium

# Test optimized version
super agent evaluate chatbot_persistent  # automatically loads optimized weights
```

**What GEPA optimizes:**
- The `system_prompt` instruction
- Memory management instructions
- File organization strategy
- Response personalization

**Example improvement:**

**Before GEPA:**
```yaml
system_prompt: |
  You are a personal assistant with long-term memory.
  Save info to /user_profile.txt.
```

**After GEPA:**
```yaml
system_prompt: |
  You are a dedicated personal assistant with advanced persistent memory capabilities.
  
  MEMORY MANAGEMENT PROTOCOL:
  
  1. ALWAYS read /user_profile.txt before responding
  2. Extract user's name, preferences, and context
  3. Personalize every response using this information
  4. After each interaction, update files with new learnings:
     - /user_profile.txt: User details, preferences
     - /conversation_topics.txt: Discussion history
     - /reminders.txt: User's to-dos and future plans
  
  RESPONSE GUIDELINES:
  - Use user's name naturally
  - Reference past conversations
  - Build relationships through memory
  - Proactively suggest based on preferences
```

**Result:** +25% improvement in user satisfaction scores!

---

## 🔍 Tutorial 5: Backend Performance Comparison

### Setup: Same Agent, Different Backends

Let's create the same agent with different backends and compare:

```bash
# Test 1: StateBackend (default)
super agent pull research_agent_deepagents
mv research_agent_deepagents research_state

# Test 2: StoreBackend (persistent)
super agent pull research_agent_deepagents  
mv research_agent_deepagents research_store
# Edit playbook: backend.type = store

# Test 3: FilesystemBackend
super agent pull research_agent_deepagents
mv research_agent_deepagents research_filesystem
# Edit playbook: backend.type = filesystem, root_dir = /tmp/agent_files
```

### Compile All

```bash
for agent in research_state research_store research_filesystem; do
  super agent compile $agent --framework deepagents
done
```

### Test Performance

```bash
# Test each with same query
QUERY="Research machine learning and save findings to /notes.txt"

time super agent run research_state --goal "$QUERY"
time super agent run research_store --goal "$QUERY"
time super agent run research_filesystem --goal "$QUERY"
```

### Check Persistence

```bash
# New conversation - which agent still has /notes.txt?

super agent run research_state --goal "Show me /notes.txt"
# File not found (ephemeral)

super agent run research_store --goal "Show me /notes.txt"
# File found! (persistent in database)

super agent run research_filesystem --goal "Show me /notes.txt"
# File found! (on actual filesystem)

cat /tmp/agent_files/notes.txt
# Real file exists on disk
```

### Results

| Backend | Speed | Persistence | Visible in IDE | Best For |
|---------|-------|-------------|----------------|----------|
| state | ⚡⚡⚡ 1.2s | No | No | Speed |
| store | ⚡⚡ 1.5s | Yes | No | Memory |
| filesystem | ⚡⚡ 1.4s | Yes | Yes | Real files |

---

## 🎯 Tutorial 6: Production-Ready Hybrid Agent

### Goal
Build a production-ready development assistant with optimal storage.

### Architecture

```
┌─────────────────────────────────────────┐
│     Development Assistant Agent         │
├─────────────────────────────────────────┤
│                                         │
│  /memories/ → StoreBackend             │
│  ├─ /user_preferences.txt (persistent)  │
│  ├─ /project_context.txt (persistent)   │
│  └─ /code_patterns.txt (persistent)     │
│                                         │
│  /project/ → FilesystemBackend         │
│  ├─ /src/*.py (real files)              │
│  ├─ /tests/*.py (real files)            │
│  └─ /docs/*.md (real files)             │
│                                         │
│  /cache/ → StateBackend                │
│  ├─ /search_results.txt (temp)          │
│  └─ /temp_analysis.txt (temp)           │
│                                         │
│  / → StateBackend                       │
│  └─ /workspace.txt (scratch)            │
│                                         │
└─────────────────────────────────────────┘
```

### Complete Playbook

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Dev Assistant
  id: dev_assistant
  description: Production-ready development assistant
spec:
  target_framework: deepagents
  
  language_model:
    provider: google-genai
    model: gemini-2.5-flash  # Check provider docs for latest models
    temperature: 0.7
  
  # Hybrid storage for production
  backend:
    type: composite
    default: state
    routes:
      /memories/: store
      /project/: filesystem
      /cache/: state
    root_dir: /Users/local/my_project
  
  input_fields:
    - name: query
      type: str
  
  output_fields:
    - name: response
      type: str
  
  persona:
    system_prompt: |
      You are a professional development assistant with HYBRID STORAGE.
      
      🧠 STORAGE STRATEGY:
      
      /memories/ (Database - Persistent Forever)
      ├─ /user_preferences.txt - User's coding style, preferences
      ├─ /project_context.txt - Project architecture, key decisions
      ├─ /code_patterns.txt - Common patterns in this codebase
      └─ /error_solutions.txt - Previously solved errors
      → Use for: Long-term memory, project knowledge
      
      /project/ (Real Files - Your Actual Project)
      ├─ /src/*.py - Source code
      ├─ /tests/*.py - Tests
      ├─ /docs/*.md - Documentation
      └─ /requirements.txt - Dependencies
      → Use for: Reading code, making changes, analysis
      
      /cache/ (State - Temporary)
      ├─ /search_results.txt - Recent searches
      ├─ /analysis_temp.txt - Intermediate analysis
      └─ /todo_list.txt - Current session todos
      → Use for: Temporary data, cleared each conversation
      
      / (State - Scratch)
      ├─ /workspace.txt - Current work
      └─ /draft.txt - Draft responses
      → Use for: Current conversation only
      
      🎯 WORKFLOW:
      
      1. CONTEXT LOADING
         - Read /memories/user_preferences.txt
         - Read /memories/project_context.txt
         - Understand the project and user
      
      2. TASK EXECUTION
         - Use ls /project/src/ to explore
         - Use read_file /project/src/app.py for analysis
         - Use grep_search for finding patterns
         - Save temp results to /cache/
      
      3. CODE CHANGES (if requested)
         - Read current file
         - Make changes
         - Write back to /project/ (REAL file modified!)
         - Explain changes clearly
      
      4. MEMORY UPDATE
         - Save new learnings to /memories/
         - Update project context if needed
         - Record error solutions
      
      🔒 SAFETY:
      - Never delete files without confirmation
      - Always explain changes before making them
      - Back up important files before editing
      - Use edit_file for surgical changes
```

### Usage Examples

**Example 1: Code Review**
```bash
super agent run dev_assistant --goal "Review all Python files for issues"

# Agent:
# Lists /project/src/*.py
# Reads each file
# Analyzes code
# Writes report to /project/code_review.md (REAL FILE)
```

**Example 2: Add Feature**
```bash
super agent run dev_assistant --goal "Add input validation to login function in src/auth.py"

# Agent:
# Reads /project/src/auth.py
# Identifies login function
# Adds validation
# Writes back to /project/src/auth.py (MODIFIED!)
# Saves pattern to /memories/code_patterns.txt
```

**Example 3: Recall Context**
```bash
# Week later, new conversation
super agent run dev_assistant --goal "What changes have we made to auth.py?"

# Agent:
# Reads /memories/project_context.txt
# Finds record of auth.py changes
# Responds with history
```

---

## 🛡️ Security Best Practices

### Limit Filesystem Scope

```yaml
# BAD: Too broad
backend:
  type: filesystem
  root_dir: /  # Can access ENTIRE system!

# GOOD: Specific directory
backend:
  type: filesystem
  root_dir: /Users/local/my_project/src  # Limited scope
```

### Use Read-Only for Sensitive Data

```yaml
# Composite with read-only paper access
backend:
  type: composite
  default: state
  routes:
    /papers/: filesystem  # Agent can READ papers
    /output/: state       # Agent can WRITE outputs (not to real files)
```

### Validate Changes

Add validation to system prompt:
```yaml
persona:
  system_prompt: |
    Before modifying any file:
    1. Show the user the planned changes
    2. Wait for confirmation
    3. Only then write to /project/
```

---

## 📊 Quick Reference

### When to Use Each Backend

```yaml
# Quick Q&A, no memory needed
backend:
  type: state

# Chatbot, personal assistant
backend:
  type: store

# Code review, file analysis
backend:
  type: filesystem
  root_dir: /path/to/project

# Production agent, complex needs
backend:
  type: composite
  default: state
  routes:
    /memories/: store
    /project/: filesystem
```

### Configuration Template

```yaml
spec:
  backend:
    type: composite
    default: state
    routes:
      /memories/: store          # What should persist
      /project/: filesystem      # What's real files
      /cache/: state             # What's temporary
    root_dir: /path/to/workspace  # For filesystem routes
```

---

## 🎉 Next Steps

1. **Try all 3 tutorials** above
2. **Pull demo agents:**
   ```bash
   super agent pull chatbot_persistent
   super agent pull code_reviewer
   super agent pull researcher_hybrid
   ```
3. **Build your own agent** with the right backend
4. **Read the complete guide:** [DeepAgents Backends](../guides/deepagents-backends.md)
5. **Optimize with GEPA:**
   ```bash
   super agent optimize your_agent --auto medium
   ```

---

## 📚 Resources

- [DeepAgents 0.2.0 Announcement](https://blog.langchain.com/doubling-down-on-deepagents/)
- [SuperOptiX DeepAgents Guide](../guides/deepagents-integration.md)
- [Backend Configuration Reference](../guides/deepagents-backends.md)
- [Gemini Setup Guide](../../GEMINI_CONFIGURATION_GUIDE.md)

---

**Ready to build production agents?** Start with the chatbot tutorial and work your way up! 🚀

