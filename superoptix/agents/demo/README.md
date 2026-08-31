# 🎯 Demo Agents

**Showcase agents demonstrating SuperOptiX's capabilities across different frameworks and use cases.**

---

## 📋 Available Demo Agents

### Code Review Assistant
**Framework:** DSPy  
**Features:** RAG, Tools, Datasets, Memory  
**ID:** `code_review_assistant`  
**Use Case:** Code review with security focus

```bash
super agent pull code_review_assistant
```

**Highlights:**
- 🔍 RAG-powered knowledge retrieval
- 🛠️ File system tools
- 📊 Real code review dataset
- 💾 Memory optimization (GEPA-optimized context selection)
- ⭐ **Perfect for ODSC demo!**

---

### Research Agent (DeepAgents)
**Framework:** DeepAgents (LangGraph)  
**Features:** Planning, Filesystem, Subagents  
**ID:** `research_agent_deepagents`  
**Use Case:** Multi-step research with planning

```bash
super agent pull research_agent_deepagents
```

**Highlights:**
- 📋 Built-in planning tool (`write_todos`)
- 📁 Filesystem for context management
- 👥 Subagent spawning capability
- 🧠 Demonstrates multi-framework GEPA optimization
- ⚠️ **Requires function-calling model** (Claude/GPT-4, not Ollama)

---

### Customer Support with Memory
**Framework:** DSPy  
**Features:** Memory Optimization  
**ID:** `customer_support_with_memory`  
**Use Case:** Context-aware support with optimized memory selection

```bash
super agent pull customer_support_with_memory
```

**Highlights:**
- 💾 Short-term and long-term memory
- 🎯 GEPA-optimized context window management
- 📊 Memory ranking by relevance, importance, recency
- 🗜️ Memory summarization to fit token budget

---

### Protocol-First Agent
**Framework:** DSPy + Agenspy  
**Features:** MCP Protocol Support  
**ID:** `protocol_first_agent`  
**Use Case:** Protocol-first agent with automatic tool discovery

```bash
super agent pull protocol_first_agent
```

**Highlights:**
- 🔌 MCP (Model Context Protocol) integration
- 🔍 Automatic tool discovery
- 🎯 Protocol-first design
- 🛠️ Dynamic tool loading

---

### DSPy Automation Demo
**Framework:** DSPy  
**Features:** SuperSpec DSPy Automation (Modules, Adapters, Tools, GEPA config)  
**ID:** `dspy-demo`  
**Use Case:** Learn and test no-code DSPy automation from YAML

```bash
super agent pull dspy-demo
```

**Highlights:**
- 🧩 `dspy.module` + `dspy.module_params`
- 🎛️ Global adapter + per-module adapter overrides
- 🛠️ Builtin tools wiring from SuperSpec
- ⚙️ GEPA settings for `--optimize` flow

---

### Arize Phoenix Trace Demo
**Framework:** DSPy  
**Features:** Phoenix tracing, OpenInference auto-instrumentation, minimal structured output  
**ID:** `arize-phoenix-demo`  
**Use Case:** Generate a clean Arize Phoenix trace from a single DSPy run

```bash
super agent pull arize-phoenix-demo
```

**Highlights:**
- 🔭 Minimal DSPy playbook focused on trace generation
- 🔌 Built-in Phoenix config (`spec.phoenix`) with local collector default
- 🧪 Useful for demos where you only need to see traces, not eval or optimization
- 📥 Pull with `super agent pull arize-phoenix-demo`

---

### Pydantic Gateway Demo
**Framework:** Pydantic AI  
**Features:** Gateway runtime mode (`language_model.runtime_mode: gateway`)  
**ID:** `pydantic-gateway-demo`  
**Use Case:** Validate gateway-routed model calls with minimal Pydantic-native pipeline output

```bash
super agent pull pydantic-gateway-demo
```

**Highlights:**
- 🌐 Gateway runtime config in SuperSpec (`runtime_mode` + `gateway` block)
- 🔐 API key via env var (`PYDANTIC_AI_GATEWAY_API_KEY`)
- 🧱 Minimal generated Pydantic pipeline (`Agent(...)`, `run(...)`)

---

## 🚀 Quick Start with Any Demo Agent

### 1. Pull Agent
```bash
super agent pull <agent_id>
```

### 2. Compile
```bash
super agent compile <agent_id>
# Or with specific framework:
super agent compile research_agent_deepagents --framework deepagents
```

### 3. Evaluate
```bash
super agent evaluate <agent_id>
```

### 4. Optimize
```bash
super agent optimize <agent_id> --auto medium
```

### 5. Run
```bash
super agent run <agent_id> --goal "your goal here"
```

---

## 🎯 Use Cases by Agent

| Agent | Best For | Model | Framework |
|-------|----------|-------|-----------|
| **code_review_assistant** | Software teams, code quality | Ollama ✅ | DSPy |
| **research_agent_deepagents** | Research, planning, complex tasks | Claude/GPT-4 | DeepAgents |
| **customer_support_with_memory** | Support, context retention | Ollama ✅ | DSPy |
| **protocol_first_agent** | Tool integration, MCP servers | Ollama ✅ | DSPy |

---

## 💡 Which Demo to Try First?

**For ODSC Demo:** → `code_review_assistant`
- Complete feature showcase (RAG, Tools, Datasets, Memory)
- Works with local Ollama models
- Real-world use case
- Measurable results

**For Multi-Framework:** → `research_agent_deepagents`
- Shows SuperOptiX works with non-DSPy frameworks
- Demonstrates Universal GEPA
- Advanced planning and subagents
- Needs Claude/GPT-4

**For Memory Features:** → `customer_support_with_memory`
- GEPA-optimized context window
- Memory ranking and summarization
- Production-ready memory system

**For Protocol-First:** → `protocol_first_agent`
- MCP integration
- Automatic tool discovery
- Modern agent architecture

---

## 🎓 Learning Path

1. **Start Simple**: `code_review_assistant` (DSPy, all features, Ollama)
2. **Add Complexity**: `customer_support_with_memory` (memory optimization)
3. **Explore Multi-Framework**: `research_agent_deepagents` (DeepAgents)
4. **Go Protocol-First**: `protocol_first_agent` (MCP)

---

## 🔧 Customization

All demo agents are fully customizable:

1. **Pull agent**: `super agent pull <agent_id>`
2. **Edit playbook**: `agents/<agent_id>/playbook/<agent_id>_playbook.yaml`
3. **Recompile**: `super agent compile <agent_id>`
4. **Test changes**: `super agent evaluate <agent_id>`

---

## 📊 Framework Comparison

SuperOptiX supports multiple frameworks through the same workflow:

```bash
# DSPy agent (default)
super agent compile my_agent

# DeepAgents agent
super agent compile my_agent --framework deepagents

# CrewAI agent (coming soon)
super agent compile my_agent --framework crewai

# All use the SAME evaluate/optimize/run commands!
```

---

## 🎉 What Makes These Special?

1. **Production-Ready**: Real datasets, knowledge bases, complete BDD scenarios
2. **GEPA-Optimized**: All agents benefit from Universal GEPA optimization
3. **Multi-Framework**: Demonstrates SuperOptiX works with any framework
4. **Well-Documented**: Each has comprehensive README and demo scripts
5. **Easy to Customize**: YAML-based configuration, no code needed

---

## 📈 Results You Can Expect

### Code Review Assistant
- **Baseline**: ~40% pass rate
- **After GEPA**: ~60-70% pass rate
- **With Memory**: Better context retention

### Sentiment Analyzer
- **Baseline**: 37.5% pass rate
- **After GEPA**: 50-60% pass rate

### Research Agent (DeepAgents)
- **Baseline**: Varies by task complexity
- **After GEPA**: 20-40% improvement in structured outputs

---

*Want to contribute your own demo agent? Check our [CONTRIBUTING.md](/CONTRIBUTING.md)!*
