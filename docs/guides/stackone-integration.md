# StackOne Integration Guide

SuperOptiX serves as the **Universal Bridge** for [StackOne](https://stackone.com), allowing you to use their unified SaaS API tools with **any** major agent framework (DSPy, Pydantic AI, CrewAI, Google Vertex, Microsoft Semantic Kernel) while adding powerful capabilities like **GEPA optimization** and **pre-built benchmarks**.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Universal Bridge** | Use StackOne tools in DSPy, Pydantic AI, CrewAI, Google Vertex, and Semantic Kernel. |
| **GEPA Optimization** | Automatically rewrite tool descriptions to fix LLM errors. |
| **Vertical Benchmarks** | Pre-built evaluation suites for HRIS, ATS, and CRM tasks. |
| **Type Safety** | Full Pydantic model generation for strict validation. |

---

## 📦 Installation

Install both SuperOptiX and the StackOne SDK:

```bash
pip install superoptix stackone-ai
```

For Claude Agent SDK integration:

```bash
pip install superoptix stackone-ai claude-agent-sdk
```

---

## 🌉 The Universal Bridge

The `StackOneBridge` adapter allows you to convert StackOne tools into the native format of your chosen framework.

### 1. DSPy Integration

Perfect for programmable agents and optimization.

```python
from stackone_ai import StackOneToolSet
from superoptix.adapters import StackOneBridge
import dspy

# 1. Fetch Tools
tools = StackOneToolSet().fetch_tools(include_tools=["hris_*"])

# 2. Bridge to DSPy
dspy_tools = StackOneBridge(tools).to_dspy()

# 3. Use in Agent
agent = dspy.ReAct("query -> answer", tools=dspy_tools)
```

### 2. Pydantic AI Integration (Type-Safe)

Generates strictly typed Pydantic models for every tool, ensuring the agent follows the schema exactly.

```python
from pydantic_ai import Agent

# 1. Bridge to Pydantic AI
pai_tools = StackOneBridge(tools).to_pydantic_ai()

# 2. Use in Agent (Type-safe!)
agent = Agent('openai:gpt-4o', tools=pai_tools)
```

### 3. CrewAI Integration

Perfect for multi-agent workflows with role-based agents. Supports both sync and async tools.

```python
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# 1. Bridge to CrewAI (Sync)
crewai_tools = StackOneBridge(tools).to_crewai()

# Or for async workflows:
# crewai_async_tools = StackOneBridge(tools).to_crewai_async()

# 2. Create Agent with StackOne tools
hr_agent = Agent(
    role="HR Assistant",
    goal="Help with HR queries using HRIS tools",
    backstory="You are an HR specialist with access to employee management systems.",
    llm=LLM(model="gpt-4o-mini"),
    tools=crewai_tools,
)

# 3. Create Task and Crew
task = Task(
    description="List all employees in engineering",
    expected_output="Employee list with names and roles",
    agent=hr_agent,
)

crew = Crew(agents=[hr_agent], tasks=[task], process=Process.sequential)

# 4. Run
result = crew.kickoff()
```

### 4. Google Vertex AI (Gemini)

Converts tools to Google's specific `FunctionDeclaration` format.

```python
import google.generativeai as genai

# 1. Bridge to Google ADK
google_tools = StackOneBridge(tools).to_google_adk()

# 2. Initialize Gemini
model = genai.GenerativeModel('gemini-1.5-pro', tools=[google_tools])
```

### 5. Microsoft Semantic Kernel

Converts tools into Semantic Kernel Plugins/Functions.

```python
import semantic_kernel as sk

# 1. Bridge to Semantic Kernel
sk_functions = StackOneBridge(tools).to_semantic_kernel()

# 2. Register as Plugin
kernel = sk.Kernel()
for func in sk_functions:
    kernel.add_function(plugin_name="StackOne", function=func)
```

### 6. Claude Agent SDK (In-Process MCP)

Uses StackOne tools as Claude SDK MCP tools with no subprocess server required.

```python
from stackone_ai import StackOneToolSet
from claude_agent_sdk import ClaudeAgentOptions, query
from superoptix.adapters import StackOneBridge

toolset = StackOneToolSet()
tools = toolset.fetch_tools(
    include_tools=["hris_list_employees", "hris_get_employee"],
    account_ids=["your_stackone_account_id"],
)

bridge = StackOneBridge(tools)
mcp_server, tool_names = bridge.to_claude_sdk()

options = ClaudeAgentOptions(
    system_prompt="You are an HR assistant. Use StackOne tools for factual answers.",
    mcp_servers={"stackone": mcp_server},
    allowed_tools=tool_names,
    model="claude-sonnet-4-5",
)

async for message in query(prompt="List all employees in engineering", options=options):
    pass
```

Model examples (Anthropic docs):
- `claude-opus-4-5`
- `claude-sonnet-4-5`
- `claude-haiku-4-5`

Runtime setup:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

For large toolsets with discovery mode:

```python
mcp_server, tool_names = StackOneBridge(tools).to_discovery_tools(framework="claude_sdk")
```

See full guide: `docs/guides/stackone-claude-sdk.md`

---

## 🔍 Dynamic Tool Discovery (Discovery Mode)

StackOne provides 100+ tools. Loading them all into an LLM's context window is expensive and confusing. **Discovery Mode** provides the agent with just two "meta-tools" to navigate the entire ecosystem at runtime.

### How it Works
1.  The agent receives `tool_search` and `tool_execute`.
2.  The agent searches for a capability (e.g., "how to find employees").
3.  The agent receives the specific tool name from the index and executes it.

### Usage

```python
# 1. Fetch a large set of tools (e.g., everything)
all_tools = toolset.fetch_tools(account_ids=["acc_123"])

# 2. Get Discovery Tools for your framework
# Supported: 'dspy', 'pydantic_ai', 'crewai', 'google', 'semantic_kernel'
discovery_tools = StackOneBridge(all_tools).to_discovery_tools(framework="dspy")

# For CrewAI:
# discovery_tools = StackOneBridge(all_tools).to_discovery_tools(framework="crewai")

# 3. Equip the agent (Only 2 tools injected!)
agent = dspy.ReAct("question -> answer", tools=discovery_tools)
```

---

## 🧬 GEPA Optimization

Is the LLM struggling to use a specific HRIS tool? Use **GEPA** to automatically rewrite the tool's description based on real failure data.

```python
from superoptix.benchmarks.stackone import HRISBenchmark

# 1. Load Benchmark Data
dataset = HRISBenchmark().get_dataset()

# 2. Run Optimization
# This uses the 'StackOneOptimizableComponent' to mutate tool descriptions
optimized_tools = bridge.optimize(
    dataset=dataset,
    metric=my_accuracy_metric,
    max_iterations=5
)

# 3. Result: Tools now have "LLM-optimized" descriptions
print(optimized_tools[0].description)
```

---

## 📊 Evaluation Benchmarks

SuperOptiX includes pre-built benchmarks for StackOne's core verticals. Use these to prove your agent works before deploying.

### Available Benchmarks
*   **`HRISBenchmark`**: Employee retrieval, employment details, team structure.
*   **`ATSBenchmark`**: Job search, candidate profiles, application tracking.
*   **`CRMBenchmark`**: Account management, opportunity lists, contact lookup.

### Usage

```python
from superoptix.benchmarks.stackone import ATSBenchmark

benchmark = ATSBenchmark()
dataset = benchmark.get_dataset()

for case in dataset:
    print(f"Testing: {case['input']}")
    # ... run your agent ...
    score = benchmark.evaluate_tool_call(tool_name, tool_args, expected=case)
```

---

## 📄 Production Blueprints

Don't want to code? Use our pre-built YAML blueprints to deploy optimized agents instantly.

| Agent ID | Description |
| :--- | :--- |
| `stackone_hris_agent` | HR Specialist for employee management |
| `stackone_ats_agent` | Recruitment assistant for hiring workflows |
| `stackone_crm_agent` | Sales assistant for CRM operations |

**Run directly from CLI:**

```bash
# Pull the blueprint
super agent pull stackone_hris_agent

# Run the agent
super agent run stackone_hris_agent --input "Find employee ID 123"
```
