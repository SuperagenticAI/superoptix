# StackOne Integration Guide

SuperOptiX serves as the **Universal Bridge** for [StackOne](https://stackone.com), allowing you to use their unified SaaS API tools with major frameworks (DSPy, Pydantic AI, CrewAI, Google ADK, OpenAI SDK, DeepAgents) while adding optimization and evaluation workflows.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Universal Bridge** | Use StackOne tools in DSPy, Pydantic AI, CrewAI, Google ADK, OpenAI SDK, and DeepAgents. |
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

## Current CLI Workflow (Recommended)

Use one StackOne playbook and compile it into any framework:

```bash
export STACKONE_API_KEY="..."
export STACKONE_ACCOUNT_IDS="acc_123"
super agent pull stackone-calendly
```

```bash
# DSPy
super agent compile stackone-calendly --framework dspy
super agent run stackone-calendly --framework dspy --goal "What is my Calendly username?"

# Pydantic AI
super agent compile stackone-calendly --framework pydantic-ai --cloud --provider google-genai --model gemini-2.5-flash
super agent run stackone-calendly --framework pydantic-ai --direct --cloud --provider google-genai --model gemini-2.5-flash --goal "What is my Calendly username?"

# OpenAI SDK
super agent compile stackone-calendly --framework openai --cloud --provider google-genai --model gemini-2.5-flash
super agent run stackone-calendly --framework openai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is my Calendly username?"

# Claude Agent SDK
super agent compile stackone-calendly --framework claude-sdk
super agent run stackone-calendly --framework claude-sdk --goal "What is my Calendly username?"

# CrewAI
super agent compile stackone-calendly --framework crewai --cloud --provider google-genai --model gemini-2.5-flash
super agent run stackone-calendly --framework crewai --cloud --provider google-genai --model gemini-2.5-flash --goal "What is my Calendly username?"
```

For Claude-specific setup details, see [StackOne + Claude Agent SDK](stackone-claude-sdk.md).

---

## 🌉 The Universal Bridge

The `StackOneBridge` adapter allows you to convert StackOne tools into the native format of your chosen framework.

### DSPy Integration

Perfect for programmable agents and optimization.

```python
from stackone_ai import StackOneToolSet
from superoptix.adapters import StackOneBridge
import dspy

# Fetch Tools
tools = StackOneToolSet().fetch_tools(actions=["hris_*"])

# Bridge to DSPy
dspy_tools = StackOneBridge(tools).to_dspy()

# Use in Agent
agent = dspy.ReAct("query -> answer", tools=dspy_tools)
```

### DSPy via SuperSpec (No DSPy Coding)

Use the connector through SuperSpec and let SuperOptiX wire DSPy tools automatically:

```yaml
spec:
  target_framework: dspy
  dspy:
    module: react
    tools:
      mode: stackone_discovery
      trace:
        enabled: true   # optional: transient live tool logs
      stackone:
        enabled: true
        api_key_env: STACKONE_API_KEY
        account_ids_env: STACKONE_ACCOUNT_IDS
        providers: ["bamboohr"]
        actions: ["hris_*"]
```

Then run:

```bash
export STACKONE_API_KEY="..."
export STACKONE_ACCOUNT_IDS="acc_123"
super agent pull stackone-calendly
super agent compile stackone-calendly --framework dspy
super agent run stackone-calendly --framework dspy --goal "List meetings and highlight conflicts"
```

Calendly-focused demo:

```bash
export STACKONE_API_KEY="..."
export STACKONE_ACCOUNT_IDS="acc_123"
super agent pull stackone-calendly
super agent compile stackone-calendly --framework dspy
super agent run stackone-calendly --framework dspy --goal "Show my meetings for next week and any conflicts"
```

You can also enable live transient thinking logs from the shell:

```bash
export SUPEROPTIX_DSPY_THINKING_LOGS=1
```

### Pydantic AI Integration (Type-Safe)

Generates strictly typed Pydantic models for every tool, ensuring the agent follows the schema exactly.

```python
from pydantic_ai import Agent

# Bridge to Pydantic AI
pai_tools = StackOneBridge(tools).to_pydantic_ai()

# Use in Agent (Type-safe!)
agent = Agent('openai:gpt-4o', tools=pai_tools)
```

### CrewAI Integration

Perfect for multi-agent workflows with role-based agents. Supports both sync and async tools.

```python
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# Bridge to CrewAI (Sync)
crewai_tools = StackOneBridge(tools).to_crewai()

# Or for async workflows:
# crewai_async_tools = StackOneBridge(tools).to_crewai_async()

# Create Agent with StackOne tools
hr_agent = Agent(
    role="HR Assistant",
    goal="Help with HR queries using HRIS tools",
    backstory="You are an HR specialist with access to employee management systems.",
    llm=LLM(model="gpt-4o-mini"),
    tools=crewai_tools,
)

# Create Task and Crew
task = Task(
    description="List all employees in engineering",
    expected_output="Employee list with names and roles",
    agent=hr_agent,
)

crew = Crew(agents=[hr_agent], tasks=[task], process=Process.sequential)

# Run
result = crew.kickoff()
```

### Google ADK / Gemini

Converts tools to Google's specific `FunctionDeclaration` format.

```python
import google.generativeai as genai

# Bridge to Google ADK
google_tools = StackOneBridge(tools).to_google_adk()

# Initialize Gemini
model = genai.GenerativeModel('gemini-1.5-pro', tools=[google_tools])
```

### Microsoft Semantic Kernel

Converts tools into Semantic Kernel Plugins/Functions.

```python
import semantic_kernel as sk

# Bridge to Semantic Kernel
sk_functions = StackOneBridge(tools).to_semantic_kernel()

# Register as Plugin
kernel = sk.Kernel()
for func in sk_functions:
    kernel.add_function(plugin_name="StackOne", function=func)
```

### Claude Agent SDK (In-Process MCP)

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
# Fetch a large set of tools (e.g., everything)
all_tools = toolset.fetch_tools(account_ids=["acc_123"])

# Get Discovery Tools for your framework
# Supported: 'dspy', 'pydantic_ai', 'crewai', 'google', 'semantic_kernel'
discovery_tools = StackOneBridge(all_tools).to_discovery_tools(framework="dspy")

# For CrewAI:
# discovery_tools = StackOneBridge(all_tools).to_discovery_tools(framework="crewai")

# Equip the agent (Only 2 tools injected!)
agent = dspy.ReAct("question -> answer", tools=discovery_tools)
```

---

## 🧬 GEPA Optimization

Is the LLM struggling to use a specific HRIS tool? Use **GEPA** to automatically rewrite the tool's description based on real failure data.

```python
from superoptix.benchmarks.stackone import HRISBenchmark

# Load Benchmark Data
dataset = HRISBenchmark().get_dataset()

# Run Optimization
# This uses the 'StackOneOptimizableComponent' to mutate tool descriptions
optimized_tools = bridge.optimize(
    dataset=dataset,
    metric=my_accuracy_metric,
    max_iterations=5
)

# Result: Tools now have "LLM-optimized" descriptions
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

## 📄 Deployment Blueprints

Don't want to code? Use our pre-built YAML blueprints to deploy optimized agents instantly.

| Agent ID | Description |
| :--- | :--- |
| `stackone-calendly` | Calendly scheduling and identity queries via StackOne |

**Run directly from CLI:**

```bash
# Pull the blueprint
super agent pull stackone-calendly

# Compile for a framework (examples)
super agent compile stackone-calendly --framework dspy
super agent compile stackone-calendly --framework pydantic-ai --cloud --provider google-genai --model gemini-2.5-flash

# Run the agent
super agent run stackone-calendly --framework dspy --goal "What is my Calendly username?"
super agent run stackone-calendly --framework pydantic-ai --direct --cloud --provider google-genai --model gemini-2.5-flash --goal "What is my Calendly username?"
```
