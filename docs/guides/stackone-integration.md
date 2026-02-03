# StackOne Integration Guide

SuperOptiX provides deep integration with [StackOne](https://stackone.com), enabling unified SaaS API tools with **any** major agent framework while adding powerful capabilities like **GEPA optimization**, **feedback collection**, and **pre-built benchmarks**.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **No-Code YAML Config** | Configure StackOne tools in agent playbooks - no code required |
| **Universal Bridge** | Use StackOne tools in DSPy, Pydantic AI, Google Vertex, Semantic Kernel, OpenAI, LangChain |
| **GEPA Optimization** | Automatically rewrite tool descriptions to fix LLM errors |
| **Vertical Benchmarks** | Pre-built evaluation suites for HRIS, ATS, and CRM tasks |
| **Feedback Collection** | Collect user feedback on tool performance |
| **Implicit Feedback** | LangSmith integration for behavioral feedback tracking |
| **Hybrid Search** | BM25 + TF-IDF index for intelligent tool discovery |
| **File Upload** | Automatic detection and handling of file uploads |
| **MCP Discovery** | Runtime tool fetch via Model Context Protocol |

---

## 📦 Installation

```bash
pip install superoptix
pip install 'stackone-ai[mcp]'
```

---

## 🎯 No-Code Usage (CLI + YAML)

Use StackOne tools **without writing any code** - only CLI commands and YAML configuration.

### Step 1: Initialize Your Project

```bash
super init my_hr_project
cd my_hr_project
```

This creates:
- `.super` file (project marker)
- `.env` file for API keys
- `my_hr_project/agents/` directory for agent playbooks

### Step 2: Configure StackOne API Key

Edit the `.env` file:

```env
# .env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# StackOne Configuration
STACKONE_API_KEY=your_stackone_api_key
STACKONE_ACCOUNT_ID=your_account_id
```

### Step 3: Pull Pre-Built StackOne Agent

```bash
# Browse available StackOne agents
super market browse agents --industry stackone

# Pull a pre-built StackOne agent
super agent pull stackone_hris_agent
```

Available pre-built agents:

| Agent | Command | Description |
|-------|---------|-------------|
| HRIS Agent | `super agent pull stackone_hris_agent` | Employee management |
| ATS Agent | `super agent pull stackone_ats_agent` | Recruitment workflows |
| CRM Agent | `super agent pull stackone_crm_agent` | Sales operations |

### Step 4: Or Create Your Own Agent

Create a YAML playbook in your project's agents directory:

```yaml
# hr_assistant_playbook.yaml

name: HR Assistant
id: hr_assistant
version: 1.0.0
description: HR assistant using StackOne HRIS integration
framework: dspy
tier: genies  # Tool-using tier

model:
  provider: openai
  name: gpt-5.2
  temperature: 0.0

instructions: |
  You are an HR specialist with access to the company HRIS.
  Help users with employee information and HR tasks.

# StackOne Tool Configuration
tools:
  - source: stackone              # ← Use StackOne as tool source
    category: hris                # ← Which StackOne vertical
    account_id: ${STACKONE_ACCOUNT_ID}
    filter:                       # ← Glob patterns for tool selection
      - hris_*                    # Include all HRIS tools
      - "!hris_delete_*"          # Exclude delete operations

optimization:
  optimizer: GEPA
  metric: tool_accuracy
  auto: medium

dataset:
  benchmark: stackone.HRISBenchmark
  min_score: 0.9
```

### Step 5: Compile and Run

```bash
# Compile the agent
super agent compile hr_assistant

# Run interactively
super agent chat hr_assistant

# Or run with a query
super agent run hr_assistant --query "List all employees in Engineering"
```

---

## 📊 Observability (LogFire & MLflow)

StackOne agents in SuperOptiX support comprehensive observability and experiment tracking through native integrations with **LogFire** and **MLflow**.

### 🔥 LogFire Integration
LogFire provides deep tracing for Pydantic AI agents, allowing you to monitor every LLM call and tool invocation.

1. **Install LogFire support:**
   ```bash
   pip install "superoptix[logfire]"
   ```

2. **Enable in Playbook:**
   Add the following to your `spec:` section:
   ```yaml
   spec:
     logfire:
       enabled: true  # Auto-detects if LogFire is authenticated
   ```

3. **Authenticate:**
   ```bash
   logfire auth
   ```

### 🧪 MLflow Integration
MLflow tracks metrics, parameters, and artifacts for your agent runs, making it easy to compare performance across different versions.

1. **Enable in Playbook:**
   Add the following to your `spec:` section:
   ```yaml
   spec:
     observability:
       enabled: true
       backends:
         - mlflow
       mlflow:
         experiment_name: "stackone_hris_agent"
         tracking_uri: "http://localhost:5000"
         log_artifacts: true
   ```

2. **Start MLflow Server:**
   ```bash
   mlflow server --port 5000
   ```

---

## 📋 YAML Configuration Reference

### Tool Source Options

```yaml
tools:
  # Option 1: All tools from a category
  - source: stackone
    category: hris
    
  # Option 2: Specific tools with filters
  - source: stackone
    category: ats
    filter:
      - ats_list_jobs
      - ats_get_candidate
      - ats_create_application
      
  # Option 3: Glob patterns with exclusions
  - source: stackone
    category: crm
    filter:
      - crm_*           # All CRM tools
      - "!crm_delete_*" # Except delete operations
      
  # Option 4: Multiple accounts
  - source: stackone
    category: hris
    account_ids:
      - acc_123
      - acc_456
      
  # Option 5: Provider-specific tools
  - source: stackone
    providers:
      - hibob
      - bamboohr
```

### Available Categories

| Category | Description | Example Tools |
|----------|-------------|---------------|
| `hris` | Human Resources | `hris_list_employees`, `hris_get_team` |
| `ats` | Applicant Tracking | `ats_list_jobs`, `ats_create_application` |
| `crm` | Customer Relations | `crm_list_accounts`, `crm_get_contact` |
| `lms` | Learning Management | `lms_list_courses`, `lms_get_enrollment` |
| `iam` | Identity & Access | `iam_list_users`, `iam_get_role` |
| `documents` | Document Management | `documents_upload`, `documents_list` |
| `marketing` | Marketing Automation | `marketing_list_campaigns` |

### Feedback Configuration

```yaml
tools:
  - source: stackone
    category: hris
    feedback:
      enabled: true           # Enable tool_feedback
      ask_permission: true    # Always ask user before sending
```

### Implicit Feedback (LangSmith)

```yaml
tools:
  - source: stackone
    category: hris
    implicit_feedback:
      enabled: true
      project: my-project
      tags:
        - production
        - hr-assistant
```

### Complete Example Playbook

```yaml
# complete_hr_agent_playbook.yaml

name: Complete HR Assistant
id: complete_hr_assistant
version: 1.0.0
description: Full-featured HR assistant with StackOne integration
framework: dspy
tier: genies

model:
  provider: openai
  name: gpt-5.2
  temperature: 0.0

instructions: |
  You are an expert HR Specialist with access to the company's HRIS system.
  
  RESPONSIBILITIES:
  - Look up employee information when asked
  - Help with team structure queries
  - Assist with employment details
  
  GUIDELINES:
  - Always verify employee ID before sharing sensitive data
  - If information cannot be found, explain what you searched for
  - Be concise but thorough in your responses

tools:
  - source: stackone
    category: hris
    account_id: ${STACKONE_ACCOUNT_ID}
    filter:
      - hris_get_employee
      - hris_list_employees
      - hris_get_employment
      - hris_list_employments
      - hris_get_team
      - hris_list_teams
    feedback:
      enabled: true
      ask_permission: true

optimization:
  optimizer: GEPA
  metric: hris_accuracy
  auto: medium

dataset:
  benchmark: stackone.HRISBenchmark
  min_score: 0.9

guardrails:
  - type: pii_protection
    level: strict
```

---

## 🌉 Programmatic Usage (Python API)

For developers who need programmatic access.

### Basic Usage

```python
from superoptix.adapters import StackOneToolSetWrapper, StackOneBridge

# Initialize toolset
toolset = StackOneToolSetWrapper()  # Uses STACKONE_API_KEY env var

# Fetch HRIS tools with glob patterns
tools = toolset.fetch_tools(
    actions=["hris_*", "!hris_delete_*"],
    account_ids=["your-account-id"]
)

# Convert to your framework
bridge = toolset.to_bridge()
dspy_tools = bridge.to_dspy()
openai_tools = bridge.to_openai()
```

### Framework Conversion

```python
from superoptix.adapters import StackOneBridge

bridge = StackOneBridge(tools)

# Convert to different frameworks
dspy_tools = bridge.to_dspy()              # DSPy Tool objects
pydantic_tools = bridge.to_pydantic_ai()   # Pydantic AI Tools
openai_tools = bridge.to_openai()          # OpenAI function calling
langchain_tools = bridge.to_langchain()    # LangChain Tools
google_tools = bridge.to_google_adk()      # Google ADK format
sk_functions = bridge.to_semantic_kernel() # Semantic Kernel Functions
```

### DSPy Integration

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

### Pydantic AI Integration (Type-Safe)

```python
from pydantic_ai import Agent

# Bridge to Pydantic AI (generates typed models)
pai_tools = StackOneBridge(tools).to_pydantic_ai()

# Use in Agent
agent = Agent('openai:gpt-5.2', tools=pai_tools)
```

### Google Vertex AI (Gemini)

```python
import google.generativeai as genai

# Bridge to Google ADK
google_tools = StackOneBridge(tools).to_google_adk()

# Initialize Gemini
model = genai.GenerativeModel('gemini-1.5-pro', tools=[google_tools])
```

### Microsoft Semantic Kernel

```python
import semantic_kernel as sk

# Bridge to Semantic Kernel
sk_functions = StackOneBridge(tools).to_semantic_kernel()

# Register as Plugin
kernel = sk.Kernel()
for func in sk_functions:
    kernel.add_function(plugin_name="StackOne", function=func)
```

---

## 🔍 Dynamic Tool Discovery

StackOne provides 100+ tools. **Discovery Mode** provides the agent with just two "meta-tools" to navigate the entire ecosystem at runtime.

### How it Works
1. The agent receives `tool_search` and `tool_execute`
2. The agent searches for a capability (e.g., "how to find employees")
3. The agent receives the specific tool name and executes it

### Usage

```python
# Fetch all tools
all_tools = toolset.fetch_tools(account_ids=["acc_123"])

# Get Discovery Tools (only 2 tools injected!)
discovery_tools = StackOneBridge(all_tools).to_discovery_tools(framework="dspy")

# Use in agent
agent = dspy.ReAct("question -> answer", tools=discovery_tools)
```

### Hybrid Search Index

```python
from superoptix.adapters import ToolIndex

# Create hybrid search index
index = ToolIndex(tools, hybrid_alpha=0.2)

# Search with natural language
results = index.search("manage employee time off", limit=5)

for result in results:
    print(f"{result.name}: {result.score:.3f}")
```

---

## 🧬 GEPA Optimization

Automatically rewrite tool descriptions based on failure data:

```python
from superoptix.benchmarks.stackone import HRISBenchmark

# Load Benchmark Data
dataset = HRISBenchmark().get_dataset()

# Run Optimization
optimized_tools = bridge.optimize(
    dataset=dataset,
    metric=my_accuracy_metric,
    max_iterations=5
)

# Result: Tools now have "LLM-optimized" descriptions
print(optimized_tools[0].description)
```

---

## 📊 Feedback Collection

### Explicit Feedback

```python
from superoptix.adapters import StackOneFeedbackTool

feedback_tool = StackOneFeedbackTool()

# Submit feedback (always ask user permission first!)
result = feedback_tool.execute(
    feedback="The HRIS tools are working great!",
    account_id="acc_123456",
    tool_names=["hris_list_employees", "hris_get_employee"]
)
```

### Implicit Feedback (LangSmith)

```python
from superoptix.adapters import configure_implicit_feedback

configure_implicit_feedback(
    api_key="your-langsmith-key",
    project_name="stackone-agents",
    default_tags=["production"],
)

# Feedback is automatically tracked
# Detects: refinement patterns, tool suitability, usage patterns
```

---

## 📊 Evaluation Benchmarks

Pre-built benchmarks for StackOne's core verticals:

| Benchmark | Description |
|-----------|-------------|
| `HRISBenchmark` | Employee retrieval, employment details, team structure |
| `ATSBenchmark` | Job search, candidate profiles, application tracking |
| `CRMBenchmark` | Account management, opportunity lists, contact lookup |

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

## 🔧 Environment Variables

| Variable | Description |
|----------|-------------|
| `STACKONE_API_KEY` | StackOne API key |
| `STACKONE_ACCOUNT_ID` | Default account ID |
| `LANGSMITH_API_KEY` | LangSmith API key for implicit feedback |
| `STACKONE_IMPLICIT_FEEDBACK_ENABLED` | Enable/disable implicit feedback |
| `STACKONE_IMPLICIT_FEEDBACK_PROJECT` | LangSmith project name |
| `STACKONE_IMPLICIT_FEEDBACK_TAGS` | Comma-separated tags |

---

## 📚 API Reference

### StackOneToolSetWrapper

```python
class StackOneToolSetWrapper:
    def __init__(api_key=None, account_id=None, base_url="https://api.stackone.com")
    def set_accounts(account_ids: List[str]) -> Self
    def fetch_tools(account_ids=None, providers=None, actions=None) -> List[StackOneTool]
    def get_tool(name: str) -> Optional[StackOneTool]
    def to_bridge(tools=None) -> StackOneBridge
    def create_tool_index(tools=None) -> ToolIndex
    def get_feedback_tool() -> StackOneFeedbackTool
```

### StackOneBridge

```python
class StackOneBridge:
    def __init__(stackone_tools: List[StackOneTool])
    def optimize(dataset, metric, reflection_lm="gpt-5.2", max_iterations=5)
    def to_dspy() -> List[DSPyTool]
    def to_pydantic_ai() -> List[PydanticAITool]
    def to_openai() -> List[Dict]
    def to_langchain() -> List[LangChainTool]
    def to_google_adk() -> List[Dict]
    def to_semantic_kernel() -> List[KernelFunction]
    def to_discovery_tools(framework="dspy") -> List
```

### ToolIndex

```python
class ToolIndex:
    DEFAULT_HYBRID_ALPHA = 0.2
    def __init__(tools: List[StackOneTool], hybrid_alpha=None)
    def search(query: str, limit=5, min_score=0.0) -> List[ToolSearchResult]
```

---

## 🔗 See Also

- [StackOne AI SDK Documentation](https://github.com/StackOneHQ/stackone-ai-python)
- [SuperOptiX GEPA Optimization](./gepa-optimization.md)
- [Agent Optimization Guide](./agent-optimization/tools.md)
