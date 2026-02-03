# 🧠 DeepAgents Framework Integration

**SuperOptiX now supports DeepAgents 0.2.0 - a LangGraph-based "agent harness" for building sophisticated, long-running agents with planning, pluggable backends, and subagent spawning!**

!!! tip "🚀 New to DeepAgents? Start with the Complete Tutorial!"
    **[👉 Complete End-to-End Workflow Tutorial](../tutorials/deepagents-complete-workflow.md)**
    
    Learn how to build, run, evaluate, and optimize DeepAgents from scratch in 30 minutes:
    
    - ✅ Step-by-step with real expected outputs
    - ✅ Works with FREE Gemini API
    - ✅ Persistent memory, real file access, hybrid storage
    - ✅ GEPA optimization guide
    - ✅ Production deployment guide

---

## 🎯 What is DeepAgents?

DeepAgents is LangChain's premier framework for creating **"deep agents"** - sophisticated agents that go beyond simple tool-calling loops. As [LangChain states](https://blog.langchain.com/doubling-down-on-deepagents/), deep agents are "able to do complex, open ended tasks over longer time horizons."

### Core Capabilities

- 📋 **Planning Tools**: Break down complex tasks with `write_todos`
- 📁 **Filesystem Access**: `read_file`, `write_file`, `ls`, `edit_file`, `grep_search`, `glob_search`
- 👥 **Subagent Spawning**: Delegate specialized tasks to focused subagents
- 🗄️ **Pluggable Backends** (NEW 0.2.0): Choose where files are stored
- ⚡ **Auto-Optimization** (NEW 0.2.0): Large result eviction, conversation summarization
- 🔧 **Error Recovery** (NEW 0.2.0): Automatic tool call repair

### NEW in 0.2.0: Pluggable Backends

The biggest addition is the **backend abstraction** that lets you choose where agent files are stored:

| Backend | Persistence | Use Case |
|---------|-------------|----------|
| **StateBackend** | Thread only | Scratch space (default) |
| **StoreBackend** | Forever | Long-term memory, chatbots |
| **FilesystemBackend** | Forever | Real project files, code analysis |
| **CompositeBackend** | Mixed | Hybrid strategies (best of all) |

**Perfect for:** Complex research, code generation, chatbots, multi-step workflows, and production systems.

**Read more:** [LangChain Blog - Doubling Down on DeepAgents](https://blog.langchain.com/doubling-down-on-deepagents/)

---

## 📦 Installation

```bash
# Install SuperOptiX with DeepAgents support
pip install superoptix[frameworks-deepagents]

# REQUIRED: Install Gemini integration (or your preferred LLM provider)
pip install langchain-google-genai  # For Gemini
# pip install langchain-anthropic   # For Claude
# pip install langchain-openai      # For GPT-4
```

**Includes:**
- **deepagents 0.2.0+** with pluggable backends
- SuperOptiX core with GEPA
- LangChain integration (provider-specific packages need to be installed separately)
- LangChain, LangGraph integration

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)
- API keys for function-calling models (Gemini, Claude, or GPT-4)

**New in 0.2.0:**
- ✨ Pluggable backend abstraction
- 💾 Persistent memory support
- 📁 Real filesystem access
- ⚡ Auto-optimization features

---

## 🚀 Quick Start

### Option A: Using Gemini (FREE & Recommended for Testing) ⭐

**Why Gemini?** Free tier, fast, excellent function-calling support!

```bash
# 1. Get FREE API key from https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY="your-gemini-api-key"

# 2. Pull demo agent (already configured for Gemini!)
super agent pull research_agent_deepagents

# 3. Run the full workflow
super agent compile research_agent_deepagents --framework deepagents
super agent run research_agent_deepagents --goal "What is LangGraph?"
super agent evaluate research_agent_deepagents
super agent optimize research_agent_deepagents --auto medium --framework deepagents --reflection-lm ollama:llama3.1:8b

# ✅ Done! Agent optimized with local Ollama
```

**📖 Detailed Gemini Guide**: See `DEEPAGENTS_GEMINI_TEST.md` in repo root

---

### Option B: Using Claude or GPT-4

DeepAgents requires function-calling models. To switch providers, pull the same demo agent and update the model in the generated playbook if needed. Refer to provider docs for the latest model names:

- **Gemini:** https://ai.google.dev/models
- **Claude:** https://docs.anthropic.com/en/docs/models-overview
- **OpenAI:** https://platform.openai.com/docs/models

Note: Ollama models are not supported by DeepAgents today (LangChain limitation). Use the DSPy framework for Ollama.

### Set API Key

```bash
# For Gemini (FREE)
export GOOGLE_API_KEY=your_key

# For Claude
export ANTHROPIC_API_KEY=your_key

# For OpenAI
export OPENAI_API_KEY=your_key
```

### 4. Run the Complete Workflow (Pulled Agent)

```bash
# Compile (generate DeepAgents pipeline code)
super agent compile research_agent_deepagents --framework deepagents

# Run agent
super agent run research_agent_deepagents --goal "What is LangGraph?"

# Evaluate (run BDD scenarios)
super agent evaluate research_agent_deepagents

# Optimize with GEPA (optimize system prompt)
super agent optimize research_agent_deepagents \
  --framework deepagents \
  --auto medium \
  --reflection-lm google-genai:gemini-2.5-pro

# Test optimized version
super agent evaluate research_agent_deepagents  # automatically loads optimized weights
```

**Expected Results:**
- Baseline performance → After GEPA: Significant improvement (results vary by hardware and model)
- Cost: $0.00 with FREE Gemini tier
- Time: 5-10 minutes

!!! success "📖 Want Detailed Step-by-Step Guide?"
    **[👉 Complete End-to-End Workflow Tutorial](../tutorials/deepagents-complete-workflow.md)**
    
    This comprehensive tutorial shows you:
    - ✅ What to expect at each step (real outputs!)
    - ✅ How to configure all 3 backend types
    - ✅ GEPA optimization walkthrough with examples
    - ✅ Production deployment guide

---

## 🗄️ Backend Configuration (NEW in 0.2.0)

### What Are Backends?

DeepAgents 0.2.0 introduces a **pluggable backend abstraction** that lets you choose where agent files are stored. This transforms DeepAgents from a toy framework into a **production-ready agent harness**.

**Source:** [LangChain Blog - Doubling Down on DeepAgents](https://blog.langchain.com/doubling-down-on-deepagents/)

### Quick Comparison

| Backend | When to Use | Example |
|---------|-------------|---------|
| **StateBackend** | Temporary scratch space | Draft generation, Q&A |
| **StoreBackend** | Persistent chatbots | Customer support, personal assistants |
| **FilesystemBackend** | Real file access | Code review, project analysis |
| **CompositeBackend** | Complex agents | Research assistant, dev tools |

---

### Example 1: Persistent Chatbot (StoreBackend)

Use the prebuilt agent and run it (persistent memory out of the box):
```bash
# First conversation
super agent run chatbot_persistent --goal "Hi! I'm Sarah and I love gardening."
# Agent saves: "Name: Sarah, Interest: gardening" to /user_profile.txt

# Days later, new conversation
super agent run chatbot_persistent --goal "What's my name?"
# Agent reads /user_profile.txt → "Your name is Sarah!"

# Weeks later
super agent run chatbot_persistent --goal "What do I like?"
# Agent reads /user_profile.txt → "You love gardening!"
```

**Why It Works:** StoreBackend persists files in a database. They survive across:
- ✅ Different conversations
- ✅ Different days
- ✅ Server restarts
- ✅ All threads

---

### Example 2: Code Review Agent (FilesystemBackend)

Pull and run against real files (set `root_dir` in the playbook after pulling):
```bash
# Review a specific file
super agent run code_reviewer --goal "Review src/auth.py for security issues"
# Agent reads ACTUAL file: /Users/local/my_project/src/auth.py
# Response: "Found 3 security issues in src/auth.py..."

# Analyze entire project
super agent run code_reviewer --goal "Analyze all Python files and write report to /review.md"
# Agent:
# 1. Runs: ls /src/
# 2. Reads each .py file
# 3. Writes to: /Users/local/my_project/review.md (REAL FILE!)

# You can see the report in your IDE immediately!
cat /Users/local/my_project/review.md
```

**Why It Works:** FilesystemBackend gives agent real filesystem access.
Changes are immediately visible in your IDE, terminal, git, etc.

**⚠️ Security:** Agent can modify actual files! Use with trusted agents only.

---

### Example 3: Research Agent (CompositeBackend)

Pull and run the hybrid storage demo (edit `root_dir` after pulling):
```bash
# Setup: Create papers directory
mkdir -p /Users/local/research/papers

# First research session
super agent run researcher_hybrid --goal "Research transformer architectures and save findings"

# Agent workflow:
# 1. Checks /memories/research_index.txt (empty first time)
# 2. Searches internet → saves to /cache/search_results.txt
# 3. Checks /papers/ for PDFs (if any exist)
# 4. Writes to /memories/transformer_research.txt (PERSISTS!)
# 5. Updates /memories/research_index.txt

# Week later, follow-up
super agent run researcher_hybrid --goal "What did I learn about transformers?"

# Agent workflow:
# 1. Reads /memories/transformer_research.txt (STILL THERE from last week!)
# 2. Response: "Based on your previous research from [date]..."
# 3. Can build upon previous knowledge!

# Access specific paper
super agent run researcher_hybrid --goal "Summarize the paper in /papers/attention.pdf"
# Reads actual file: /Users/local/research/papers/attention.pdf
```

**Why It Works:** Each storage type is optimized:
- `/memories/` = Persistent (store)
- `/papers/` = Real files (filesystem)
- `/cache/` = Fast & temporary (state)

---

### Backend Configuration Matrix

High-level guidance on which backend to pick:

| Configuration | /memories/ | /papers/ | /cache/ | / | Best For |
|---------------|------------|----------|---------|---|----------|
| **Default** | state | state | state | state | Simple agents |
| **Persistent** | store | store | store | store | Chatbots |
| **Local Files** | filesystem | filesystem | filesystem | filesystem | Code tools |
| **Hybrid ⭐** | store | filesystem | state | state | Production |

---

## 📚 Demo Agents with Backends

SuperOptiX includes 3 demo agents showcasing different backends:

### 1. Basic Research Agent (StateBackend)

```bash
super agent pull research_agent_deepagents
# Uses default StateBackend (ephemeral)
# Good for: Single-session research
```

### 2. Persistent Chatbot (StoreBackend)

```bash
super agent pull chatbot_persistent
# Uses StoreBackend for memory
# Good for: Multi-session conversations
```

### 3. Code Reviewer (FilesystemBackend)

```bash
super agent pull code_reviewer
# Uses FilesystemBackend for real files
# Good for: Project analysis
```

### 4. Advanced Researcher (CompositeBackend)

```bash
super agent pull researcher_hybrid
# Uses CompositeBackend for hybrid storage
# Good for: Complex production agents
```

**Try them all:**
```bash
# Set API key
export GOOGLE_API_KEY="your-key"

# Pull and test each one
for agent in research_agent_deepagents chatbot_persistent code_reviewer researcher_hybrid; do
  super agent pull $agent
  super agent compile $agent --framework deepagents
  super agent run $agent --goal "Test query"
done
```

!!! info "📖 Detailed Tutorials for Each Agent"
    Each demo agent has step-by-step tutorials:
    
    - **[Complete Workflow](../tutorials/deepagents-complete-workflow.md)** - All agents explained
    - **[Backend Tutorial](../tutorials/deepagents-backends-tutorial.md)** - Hands-on with each backend type
    
    See real examples, expected outputs, and production patterns!

---

## 📋 Complete Backend Configuration Reference

### Backend Type: state (Default)

**Storage:** LangGraph state (ephemeral)  
**Persistence:** Current conversation only  
**Best For:** Temporary scratch space

Pull the appropriate demo agent and inspect its playbook for backend configuration. No need to copy YAML from docs.

**Characteristics:**
- ⚡⚡⚡ Very fast (in-memory)
- ✅ Checkpointed within thread
- ❌ Lost when conversation ends
- ❌ Not shared across threads

**Use Cases:**
- Simple Q&A agents
- Temporary calculations
- Draft generation
- Single-session tasks

---

### Backend Type: store (Persistent)

**Storage:** LangGraph store (persistent database)  
**Persistence:** Forever, across all conversations  
**Best For:** Chatbots, learning agents

Pull `chatbot_persistent` to see a persistent store-backed setup.

**Characteristics:**
- ⚡⚡ Fast (database)
- ✅ Persistent across all threads
- ✅ Shared between conversations
- ✅ Survives restarts

**Use Cases:**
- Chatbots with memory
- Personal assistants
- Learning agents
- Knowledge accumulation

**Example Agent:**
```bash
super agent pull chatbot_persistent
super agent compile chatbot_persistent --framework deepagents
export GOOGLE_API_KEY="your-key"
super agent run chatbot_persistent --goal "Hi! My name is Alice."
# Later...
super agent run chatbot_persistent --goal "What's my name?"
# Response: "Your name is Alice!" ✅
```

---

### Backend Type: filesystem

**Storage:** Actual local filesystem  
**Persistence:** Real files on disk  
**Best For:** Code analysis, file editing

After pulling `code_reviewer`, set `backend.root_dir` in its playbook to your project path.

**Characteristics:**
- ⚡⚡ Fast (filesystem speed)
- ✅ Real files on disk
- ✅ Changes immediately visible
- ⚠️  Security: Can modify actual files!

**Use Cases:**
- Code review agents
- Documentation generators
- File refactoring
- Project analysis

**Example Agent:**
```bash
super agent pull code_reviewer
# Edit playbook to set your root_dir
super agent compile code_reviewer --framework deepagents
export GOOGLE_API_KEY="your-key"
super agent run code_reviewer --goal "Review src/app.py"
# Reads actual file from your project!
```

**⚠️ Security Warning:**
- Agent can read ANY file in `root_dir`
- Agent can MODIFY or DELETE files
- Use a limited `root_dir` scope
- Don't point to system directories (/, /etc, etc.)
- Consider read-only permissions for sensitive projects

---

### Backend Type: composite (Hybrid)

**Storage:** Routes different paths to different backends  
**Persistence:** Mixed strategies  
**Best For:** Production agents with complex needs

Pull `researcher_hybrid` to explore hybrid storage. Edit paths in the playbook to match your environment.

**Characteristics:**
- ✅ Best of all worlds
- ✅ Optimized for each data type
- ✅ Maximum flexibility
- 🔧 Requires thoughtful configuration

**Use Cases:**
- Development assistants
- Complex research agents
- Multi-domain agents
- Production systems

**Example Agent:**
```bash
super agent pull researcher_hybrid
# Edit playbook to set your root_dir
super agent compile researcher_hybrid --framework deepagents
export GOOGLE_API_KEY="your-key"
super agent run researcher_hybrid --goal "Research AI and save findings"

# Files go to optimal locations:
# /memories/research_findings.txt → Database (persists)
# /papers/reference.pdf → Real filesystem (your files)
# /cache/search.txt → Ephemeral (fast)
# /draft.txt → Scratch space (fast)
```

---

### Backend Configuration in Playbooks

**Complete Syntax:**

```yaml
spec:
  backend:
    # Backend type (required)
    type: state | store | filesystem | composite
    
    # For filesystem backend (required if type=filesystem)
    root_dir: /path/to/directory
    
    # For composite backend only
    default: state | store | filesystem  # Default backend
    routes:                              # Path routing
      /path1/: store
      /path2/: filesystem
      /path3/: state
```

**Examples:**

```yaml
# Simple: State (default)
backend:
  type: state

# Simple: Store (persistent)
backend:
  type: store

# Simple: Filesystem (real files)
backend:
  type: filesystem
  root_dir: /Users/local/my_project

# Advanced: Composite (hybrid)
backend:
  type: composite
  default: state
  routes:
    /memories/: store
    /project/: filesystem
  root_dir: /Users/local/workspace
```

---

## 📋 Creating Your Own DeepAgents Playbook

### Basic Structure

Start from a pulled demo agent and modify its playbook to fit your needs instead of copying YAML from docs.

---

## 🔄 Complete Workflow

### Step 1: Initialize Project

```bash
super init my_project
cd my_project
```

### Step 2: Create or Pull Agent

```bash
# Option A: Pull prebuilt agent
super agent pull research_agent_deepagents

# Option B: Create custom playbook
# (Create your_agent_playbook.yaml in agents/your_agent/playbook/)
```

### Step 3: Compile

```bash
super agent compile research_agent_deepagents --framework deepagents
```

**What happens:**
- Reads playbook YAML
- Generates Python pipeline using `deepagents_pipeline.py.jinja2` template
- Creates `BaseComponent` wrapper for GEPA optimization
- Adds BDD test loading
- Creates evaluation methods

**Output:** `agents/research_agent_deepagents/pipelines/research_agent_deepagents_deepagents_pipeline.py`

### Step 4: Evaluate

```bash
super agent evaluate research_agent_deepagents
```

**What happens:**
- Loads compiled pipeline
- Initializes DeepAgents agent
- Runs BDD scenarios from playbook
- Tests against expected outputs
- Shows pass/fail rate

**Example Output:**
```
✅ Simple research query: PASS
✅ Technical comparison: PASS
❌ Complex research: FAIL

Overall: 2/3 PASS (66.7%)
```

### Step 5: Optimize with GEPA

```bash
super agent optimize research_agent_deepagents --auto medium --framework deepagents --reflection-lm ollama:llama3.1:8b
```

**What happens:**
- Universal GEPA optimizer analyzes agent performance
- Optimizes the `system_prompt` (the optimizable variable)
- Runs multiple iterations with different prompts
- Selects best performing version
- Saves optimized weights

**Key Innovation:** GEPA optimizes DeepAgents agents even though they're not DSPy!

### Step 6: Re-evaluate

```bash
super agent evaluate research_agent_deepagents
```

**What happens:**
- Loads optimized system prompt
- Re-runs BDD scenarios
- Shows improvement

**Expected:** Higher pass rate after optimization!

### Step 7: Run

```bash
super agent run research_agent_deepagents --goal "Research AI trends in 2025"
```

---

## 🔧 How It Works Under the Hood

When you run `super agent compile research_agent_deepagents --framework deepagents`, SuperOptiX generates a pipeline class that includes:

High-level: SuperOptiX compiles your playbook into an executable DeepAgents pipeline and wires it to the standard run/evaluate/optimize workflow.

**Key Points:**
- ✅ Your playbook YAML controls all agent configuration
- ✅ BDD scenarios define what success looks like
- ✅ GEPA optimization is automatic - just run `super agent optimize`
- ✅ The same workflow works across all frameworks (DSPy, CrewAI, etc.)

---

## 📊 DeepAgents vs DSPy

| Feature | DeepAgents | DSPy |
|---------|-----------|------|
| **Framework** | LangGraph | DSPy |
| **Strength** | Complex multi-step tasks | Prompt optimization |
| **Planning** | Built-in `write_todos` | Manual implementation |
| **Filesystem** | Built-in tools | Manual implementation |
| **Subagents** | Native support | Manual composition |
| **SuperOptiX Support** | ✅ Full workflow | ✅ Full workflow |
| **GEPA Optimization** | ✅ system_prompt | ✅ All signatures |
| **Model Requirements** | Function-calling only | Any LLM |
| **Ollama Support** | ⚠️ Blocked (LangChain issue) | ✅ Full support |

**When to use DeepAgents:**
- Complex research tasks
- Multi-step workflows requiring planning
- Need filesystem for context management
- Want subagent delegation

**When to use DSPy:**
- Need Ollama/local model support
- Focus on prompt optimization
- Simpler task structures
- Want maximum flexibility

---

## 🎓 Example Use Cases

### Research Agent
Use the `research_agent_deepagents` demo as a starting point and adapt.

### Code Assistant
Use the `code_reviewer` demo for file-based analysis tasks.

### Data Analyst
Use the `researcher_hybrid` demo for hybrid storage and multi-step analysis.

---

## ⚙️ Advanced Configuration

### Custom Subagents
Start from a pulled agent and extend its playbook with subagents as needed.

### Custom Tools
Extend the pulled agent's `tools` list for your use case; no need to copy YAML from docs.

---

## 🐛 Troubleshooting

### NotImplementedError in bind_tools()

**Symptom:**
```
NotImplementedError
  at langchain_core.language_models.chat_models.py line 1491
```

**Cause:** Using Ollama model with DeepAgents

**Solution:** Use function-calling capable models:
```yaml
language_model:
  provider: anthropic
  model: anthropic:claude-sonnet-4-20250514
```

### Agent Initialization Failed

**Symptom:** "Failed to initialize DeepAgents"

**Checklist:**
1. ✅ API key set? (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
2. ✅ Model string correct? (e.g., `anthropic:claude-sonnet-4-20250514`)
3. ✅ LangChain dependencies installed? (`pip install langchain langchain-anthropic`)

### No BDD Specifications Found

**Symptom:** "❌ No BDD specifications found!"

**Solution:** Add scenarios to playbook:
```yaml
feature_specifications:
  scenarios:
    - name: Basic test
      input:
        query: "Test query"
      expected_output:
        report: "Expected result"
```

Then recompile:
```bash
super agent compile your_agent --framework deepagents
```

---

## 🎯 GEPA Optimization Details

### What Gets Optimized

DeepAgents agents have one optimizable variable:
- **`system_prompt`**: The main instruction to the agent

GEPA automatically:
1. Analyzes agent performance on BDD scenarios
2. Generates variations of the system prompt
3. Tests each variation
4. Selects the best performing prompt
5. Saves optimized version

### Optimization Example

**Before (Baseline):**
```
System Prompt: "You are an expert researcher."
Pass Rate: Baseline performance (varies by hardware/model)
```

**After GEPA Optimization:**
```
System Prompt: "You are an expert researcher. When answering questions:
1. Use write_todos to plan your research steps
2. Save findings to research_notes.md
3. Synthesize information before responding
..."
Pass Rate: Improved (results vary by hardware/model)
```

---

## 🏗️ Architecture

```
SuperSpec YAML Playbook
        ↓
    Compiler (AgentCompiler)
        ↓
DeepAgents Pipeline Template (deepagents_pipeline.py.jinja2)
        ↓
Generated Python Pipeline
        ├─ ResearchAgentDeepAgentsComponent (BaseComponent wrapper)
        │   └─ create_deep_agent() ← Real DeepAgents implementation
        └─ ResearchAgentDeepAgentsPipeline
            ├─ run()
            ├─ evaluate()
            ├─ optimize_with_gepa() ← Universal GEPA
            └─ run_bdd_test_suite()
```

---

## 📚 Additional Resources

- **DeepAgents Docs**: https://github.com/langchain-ai/deepagents
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **SuperOptiX Multi-Framework Guide**: `/docs/guides/multi-framework.md`
- **Universal GEPA**: `/docs/guides/universal-gepa.md`

---

## 💡 Tips & Best Practices

### 1. Use Detailed System Prompts
DeepAgents shine with detailed instructions:
```yaml
persona:
  role: Expert Researcher
  goal: |
    Conduct thorough research on AI topics, producing
    comprehensive, well-sourced reports
  backstory: |
    You have 10+ years of experience in AI research
```

### 2. Leverage Planning
Always include `write_todos` in tools:
```yaml
reasoning:
  steps:
    - Break down research into subtasks using write_todos
    - Execute each subtask systematically
```

### 3. Use Filesystem for Context
For long outputs, instruct agent to save to files:
```yaml
constraints:
  - Save research findings to research_notes.md
  - Keep main context clean
```

### 4. Start Simple, Then Optimize
1. Get baseline working (compile + evaluate)
2. Run optimization (GEPA improves the prompt)
3. Iterate on scenarios based on failures

---

## 🎓 Comparison with Other Frameworks

### DeepAgents + SuperOptiX Advantages
- ✅ Built-in planning and filesystem
- ✅ GEPA optimization works
- ✅ Standard SuperOptiX workflow
- ✅ Full LangGraph features (streaming, checkpointing, etc.)

### DSPy + SuperOptiX Advantages
- ✅ Works with Ollama (no function-calling requirement)
- ✅ More optimization targets (all signatures, not just system_prompt)
- ✅ Better for simple, focused tasks
- ✅ Native to SuperOptiX

### Use Both!
SuperOptiX lets you:
- Use **DSPy** for simple tasks with Ollama
- Use **DeepAgents** for complex tasks with Claude/GPT-4
- **Optimize both** with the same workflow!

---

## 🚀 Next Steps

Quick start with demos:

```bash
super agent pull research_agent_deepagents && super agent compile research_agent_deepagents --framework deepagents
super agent evaluate research_agent_deepagents
```

---

## ❓ FAQ

**Q: Why can't I use Ollama with DeepAgents?**  
A: LangChain's ChatOllama doesn't implement `bind_tools()` yet. This is a LangChain limitation, not SuperOptiX or DeepAgents. We're tracking the issue.

**Q: Can I use local models at all?**  
A: Yes! Use DSPy agents which work perfectly with Ollama. The workflow is identical.

**Q: Does GEPA really optimize DeepAgents?**  
A: Yes! Universal GEPA optimizes the `system_prompt` through the BaseComponent interface. It's framework-agnostic.

**Q: Can I mix DSPy and DeepAgents agents?**  
A: Absolutely! Create orchestrations that use both. Each agent uses the best framework for its task.

**Q: What about other frameworks?**  
A: Coming soon! We're extending the same pattern to CrewAI, Microsoft, OpenAI SDK, and Google ADK.

---

## 🎉 Success Stories

**What Users Are Building:**
- Complex research agents with multi-step planning
- Code assistants with filesystem access
- Data analysis agents with specialized subagents
- All optimized with GEPA for better performance!

**The SuperOptiX Advantage:**
"Finally, one workflow to rule them all - whether you use DSPy, DeepAgents, or any other framework!"

---

## 📚 Additional Resources

### 🎯 Start Here (Recommended)

- 🚀 **[Complete End-to-End Workflow](../tutorials/deepagents-complete-workflow.md)** ⭐ **NEW!**
  - Step-by-step tutorial with real examples
  - From zero to production-ready agent in 30 minutes
  - Includes evaluation, optimization, and deployment
  - All using FREE Gemini API!

### Backend Configuration (NEW in 0.2.0)

- 📖 **[Backend Reference Guide](deepagents-backends.md)** - Complete configuration reference
- 🎓 **[Backends Tutorial](../tutorials/deepagents-backends-tutorial.md)** - 6 hands-on tutorials  
- 📝 **[Integration Summary](../../DEEPAGENTS_0.2.0_COMPLETE.md)** - What's new and how to use

### Model Configuration

- 🔧 **[Gemini Configuration Guide](../../GEMINI_CONFIGURATION_GUIDE.md)** - Gemini 2.5 setup
- 🧪 **[Gemini Testing Guide](../../DEEPAGENTS_GEMINI_TEST.md)** - Complete testing workflow

### Technical Details

- 🔍 **[Technical Analysis](../../DEEPAGENTS_ANALYSIS.md)** - Why Ollama doesn't work
- 🐛 **[Fixes Summary](../../DEEPAGENTS_FIXES_SUMMARY.md)** - Bug fixes applied
- 🚀 **[Integration Plan](../../DEEPAGENTS_0.2.0_INTEGRATION.md)** - Implementation details

### Demo Agents

Pull these to see backends in action:
```bash
super agent pull research_agent_deepagents  # StateBackend (default)
super agent pull chatbot_persistent         # StoreBackend (persistent)
super agent pull code_reviewer              # FilesystemBackend (real files)
super agent pull researcher_hybrid          # CompositeBackend (hybrid)
```

### External Resources

- [DeepAgents 0.2.0 Announcement](https://blog.langchain.com/doubling-down-on-deepagents/) - LangChain blog post
- [DeepAgents GitHub](https://github.com/langchain-ai/deepagents) - Source repository
- [LangChain Docs](https://python.langchain.com/) - LangChain documentation

---

*Need help? Check our [Documentation](https://superagenticai.github.io/superoptix/) or email us at [hello@super-agentic.ai](mailto:hello@super-agentic.ai)!*


