# Explicit DSPy Agents

**Category**: Explicit Code Generation Examples
**Purpose**: Reference agents demonstrating transparent DSPy code generation
**Status**: ✅ Production-ready marketplace agents
**Model**: All use Ollama local models (llama3.2:1b)

---

## 🎯 Purpose

These agents demonstrate SuperOptiX's **explicit DSPy code generation** approach:
- ✅ **No mixins** - All logic inline and visible
- ✅ **Pure DSPy** - Standard patterns (ChainOfThought, ReAct, Retrieve)
- ✅ **Full transparency** - Complete code visibility
- ✅ **Local-first** - Run entirely on your machine with Ollama
- ✅ **Zero vendor lock-in** - Own and modify all generated code

---

## 📚 Available Agents

| Agent | Tier | Pattern | Features | Use Case |
|-------|------|---------|----------|----------|
| **qa_bot** | Oracles | CoT | Q&A, Evaluation, GEPA | Simple question answering |
| **rag_assistant** | Genies | CoT + RAG | ChromaDB, Retrieval, GEPA | Knowledge-enhanced responses |
| **mcp_agent** | Genies | ReAct | Tools, Calculator, DateTime | Task automation with tools |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2:1b

# For RAG assistant, install vector DB
pip install chromadb sentence-transformers
```

### Pull an Agent

```bash
# Initialize SuperOptiX project (if not already done)
super init my_project
cd my_project

# Pull any of these agents
super agent pull qa_bot
super agent pull rag_assistant
super agent pull mcp_agent
```

### Compile Agent

```bash
# Generate explicit DSPy pipeline (no mixins!)
super agent compile qa_bot --explicit

# This creates:
# agents/qa_bot/pipelines/qa_bot_pipeline.py (pure DSPy code)
```

### Run Agent

```bash
# Run the agent
super agent run qa_bot

# Or run directly with Python
cd agents/qa_bot/pipelines/
python qa_bot_pipeline.py
```

---

## 🎨 What Makes These "Explicit"?

### Traditional Mixin Approach ❌

```python
from superoptix.core.pipeline_utils import TracingMixin, BDDTestMixin

class MyAgent(TracingMixin, BDDTestMixin):
    def __init__(self):
        super().__init__()
        self.setup_tracing(...)  # ❓ Hidden in mixin
```

### Explicit Approach ✅

```python
# Just dspy and yaml - that's it!
import dspy
import yaml

class MyAgentPipeline:
    def __init__(self):
        # All model setup visible
        self.lm = dspy.LM(model="llama3.2:1b", temperature=0.7)
        dspy.configure(lm=self.lm)

        # All scenario loading visible
        self.test_scenarios = self._load_bdd_scenarios()

    def _load_bdd_scenarios(self):
        # All logic right here - no magic!
        scenarios = []
        # ... explicit loading code ...
        return scenarios
```

---

## 📋 Agent Details

### 1. QA Bot (qa_bot)

**Type**: Simple Q&A
**Tier**: Oracles
**Pattern**: Chain of Thought
**Lines**: ~610 lines of explicit DSPy code

**Features**:
- Basic question answering
- Chain of Thought reasoning
- BDD test scenarios
- GEPA optimization ready

**Example**:
```python
from qa_bot_pipeline import QaBotPipeline

pipeline = QaBotPipeline(playbook_path="playbook/qa_bot_playbook.yaml")
response = pipeline.run("What is Python?")
```

**Use Cases**:
- Customer support Q&A
- FAQ bots
- General information assistants
- Educational tutors

---

### 2. RAG Assistant (rag_assistant)

**Type**: Retrieval-Augmented Generation
**Tier**: Genies
**Pattern**: Chain of Thought + RAG
**Lines**: ~775 lines of explicit DSPy code

**Features**:
- Document retrieval from ChromaDB
- Context-enhanced responses
- Explicit RAG setup (all visible!)
- Knowledge base integration

**Example**:
```python
from rag_assistant_pipeline import RagAssistantPipeline

pipeline = RagAssistantPipeline(playbook_path="playbook/rag_assistant_playbook.yaml")
response = pipeline.run("What is DSPy?")
# Uses retrieved docs to answer
```

**Use Cases**:
- Documentation assistants
- Knowledge base search
- Technical Q&A with context
- Research paper analysis

---

### 3. MCP Agent (mcp_agent)

**Type**: Tool-Using Agent
**Tier**: Genies
**Pattern**: ReAct (Reasoning + Acting)
**Lines**: ~759 lines of explicit DSPy code

**Features**:
- ReAct pattern for tool use
- Calculator, DateTime, WebSearch tools
- Explicit tool registry (all visible!)
- Multi-step reasoning

**Example**:
```python
from mcp_agent_pipeline import McpAgentPipeline

pipeline = McpAgentPipeline(playbook_path="playbook/mcp_agent_playbook.yaml")
response = pipeline.run("What is 25 * 48 + 17?")
# Uses calculator tool
```

**Use Cases**:
- Task automation
- Mathematical computations
- Information retrieval with search
- Multi-tool workflows

---

## 🔧 Local Ollama Setup

All agents are configured to run locally with Ollama:

```yaml
# In playbook:
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.2:1b        # Fast, lightweight
    temperature: 0.7
    max_tokens: 2000-3000
    api_base: http://localhost:11434
```

**Why llama3.2:1b?**
- ✅ Fast responses (~2-3 sec on MacBook)
- ✅ Low memory usage (~2GB RAM)
- ✅ Good enough for demos
- ✅ Free and local

**Want better quality?** Change model in playbook:
```yaml
model: llama3.1:8b    # Better quality
model: llama3.1:70b   # Best quality (needs more RAM)
```

---

## 💡 Customization

### Change Model

Edit playbook:
```yaml
spec:
  language_model:
    model: llama3.1:8b  # Upgrade to larger model
```

### Add Tools (MCP Agent)

Edit playbook:
```yaml
spec:
  tools:
    specific_tools:
      - calculator
      - date_time
      - my_custom_tool  # Add your tool
```

Then in generated code, add tool to registry:
```python
tool_registry = {
    "my_custom_tool": {
        "name": "my_custom_tool",
        "desc": "Does something custom",
        "func": lambda x: custom_logic(x),
        ...
    }
}
```

### Modify RAG (RAG Assistant)

Edit playbook:
```yaml
spec:
  rag:
    top_k: 10              # More context
    chunk_size: 1000       # Larger chunks
    collection: my_docs    # Custom collection
```

---

## 🎓 Learning Path

1. **Start with qa_bot**
   - Learn basic DSPy patterns
   - Understand explicit code generation
   - See ChainOfThought in action

2. **Move to rag_assistant**
   - Add document retrieval
   - Work with vector databases
   - Context-enhanced generation

3. **Master mcp_agent**
   - ReAct pattern for tools
   - Multi-step reasoning
   - Build practical agents

---

## 🆚 vs Other Marketplace Agents

| Aspect | Explicit Agents | Other Marketplace |
|--------|----------------|-------------------|
| **Code Style** | Explicit (no mixins) | May use mixins |
| **Purpose** | Reference/learning | Production use |
| **Transparency** | 100% visible | Varies |
| **Model** | Ollama local | Varies |
| **Customization** | Encouraged | Template-based |
| **Lock-in** | Zero | Minimal |

---

## 📖 Documentation

- **Main Examples Guide**: `/examples/explicit_dspy_agents/README.md`
- **Complete Summary**: `EXPLICIT_DSPY_COMPLETE_SUMMARY.md`
- **Template Details**: `EXPLICIT_DSPY_TEMPLATE_SUMMARY.md`
- **CLI Usage**: Run `super agent --help`

---

## 🔄 Workflow

```
Pull Agent → Compile (Explicit) → Review Code → Customize → Run
     ↓              ↓                  ↓            ↓         ↓
super agent   Pure DSPy code    Understand    Modify     Production
   pull         generated         logic       as needed
```

---

## 🎯 Key Benefits

### For DSPy Users
- ✅ See familiar DSPy patterns
- ✅ No learning curve
- ✅ Copy code anywhere
- ✅ Full control

### For Learners
- ✅ All logic visible
- ✅ Easy to understand
- ✅ Modify and experiment
- ✅ Progressive complexity

### For Production
- ✅ Battle-tested patterns
- ✅ Local-first (Ollama)
- ✅ GEPA optimization
- ✅ Complete ownership

---

## 🚀 Next Steps

1. **Pull an agent**: `super agent pull qa_bot`
2. **Compile it**: `super agent compile qa_bot --explicit`
3. **Read the code**: Review generated pipeline
4. **Run it**: `super agent run qa_bot`
5. **Customize**: Modify and make it yours!

---

## 🤝 Contributing

Want to add more explicit agents? Follow this pattern:
1. Create playbook with `language_model.provider: ollama`
2. Use standard DSPy patterns (CoT, ReAct, Retrieve)
3. Include comprehensive BDD scenarios
4. Document customization points
5. Test with local Ollama models

---

**Explicit = Transparent | Local = Free | DSPy = Standard**

**No Mixins. No Lock-in. Just DSPy.**
