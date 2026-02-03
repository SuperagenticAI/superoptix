# 🤖 OpenAI Agents SDK Integration

**SuperOptiX now supports OpenAI Agents SDK - a lightweight, provider-agnostic framework that works PERFECTLY with Ollama!**

✅ **Works great with FREE Ollama (No API Keys Needed!)**

> **Hands-on demo:** Clone the MIT-licensed companion repo [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) to try the OpenAI Agents SDK with SuperOptiX Lite right away. The Code Reviewer example in that project mirrors this guide step by step.

---

## 🎯 What is OpenAI Agents SDK?

OpenAI Agents SDK is a lightweight yet powerful framework for building multi-agent workflows. Key features:

- 🌐 **Provider-Agnostic**: Works with OpenAI, Ollama, and 100+ LLMs
- 🔄 **Multi-Agent**: Built-in handoffs for agent collaboration
- 🛡️ **Guardrails**: Input/output validation
- 💾 **Sessions**: Automatic conversation history
- 📊 **Tracing**: Built-in execution tracking
- ✅ **Works with Ollama!**: Unlike DeepAgents, no function-calling limitations

Perfect for simple to moderate complexity tasks with local models!

---

## 📦 Installation

```bash
pip install superoptix[frameworks-openai]
```

**Includes:**
- openai-agents 0.4.1
- openai SDK (latest)
- SuperOptiX core with GEPA 0.0.17

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)

---

## 🚀 Quick Start

### 1. Pull the Demo Agent

```bash
cd your_project
super agent pull assistant_openai
```

### 2. Configure Model

**✅ Uses Ollama by Default!** (FREE, no API keys needed!)

The `assistant_openai` agent now defaults to Ollama `llama3.1:8b`:

```yaml
language_model:
  location: local
  provider: ollama
  model: ollama:llama3.1:8b  # Fast and efficient model
  temperature: 0.7
  api_base: http://localhost:11434
```

**Just install Ollama and run:**
```bash
brew install ollama  # macOS
ollama pull llama3.1:8b
super agent run assistant_openai --goal "Hello!"
```

**Also Works With Cloud Models** (requires API key):
```yaml
# OpenAI GPT-4
language_model:
  location: cloud
  provider: openai
  model: openai:gpt-4o
  # Set: export OPENAI_API_KEY="sk-..."
  
# Anthropic Claude
language_model:
  location: cloud
  provider: anthropic
  model: anthropic:claude-sonnet-4-20250514
  # Set: export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run the Workflow

```bash
# Compile
super agent compile assistant_openai --framework openai

# Evaluate
super agent evaluate assistant_openai

# Optimize with GEPA
super agent optimize assistant_openai --auto medium --framework openai --reflection-lm ollama:llama3.1:8b

# Run
super agent run assistant_openai --goal "What is Python?"
```

---

## 🌩️ Simplified Cloud/Local Model Switching

The [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) companion repo includes simplified scripts for easy switching between local and cloud models:

### Local Models (FREE)
```bash
python demo_local.py        # Run demo with Ollama
python optimize_local.py    # GEPA optimization with Ollama
```

### Cloud Models (OpenAI, Anthropic, Google)
```bash
# Set API key (choose one)
export OPENAI_API_KEY=sk-...        # Uses gpt-5
export ANTHROPIC_API_KEY=sk-ant-... # Uses claude-sonnet-4.5
export GOOGLE_API_KEY=...           # Uses gemini-pro-2.5

# Run cloud scripts (auto-detects provider)
python demo_cloud.py        # Demo with cloud models
python optimize_cloud.py    # GEPA optimization with cloud models
```

**Features:**
- ✅ Auto-detects cloud provider from API key
- ✅ Uses latest models (gpt-5, claude-sonnet-4.5, gemini-pro-2.5)
- ✅ Separate scripts for local vs cloud (no complex switching)
- ✅ Includes cost warnings (optimization uses APIs)
- ✅ .env file support for API keys

See the [repo README](https://github.com/SuperagenticAI/superoptix-lite-openai) for complete documentation.

---

## 📋 Creating Your Own OpenAI SDK Playbook

### Basic Structure

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: My Assistant
  id: my_assistant
  namespace: custom
  version: 1.0.0
  level: genies

spec:
  target_framework: openai
  
  language_model:
    location: local
    provider: ollama
    model: ollama:gpt-oss:20b
    api_base: http://localhost:11434
  
  input_fields:
    - name: query
      type: str
      required: true
  
  output_fields:
    - name: response
      type: str
      required: true
  
  persona:
    role: Helpful AI Assistant
    goal: Provide clear and helpful responses
    traits:
      - helpful
      - concise
  
  reasoning:
    method: direct
    steps:
      - Understand the question
      - Provide clear answer
  
  # BDD Scenarios
  feature_specifications:
    scenarios:
      - name: Test scenario
        input:
          query: "Hello!"
        expected_output:
          response: "Greeting"
          expected_keywords:
            - hello
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: response_accuracy
        auto: medium
```

---

## 🔄 Complete Workflow

### Step 1: Initialize

```bash
super init my_project
cd my_project
```

### Step 2: Create/Pull Agent

```bash
# Pull demo agent
super agent pull assistant_openai

# Or create custom playbook in:
# agents/my_agent/playbook/my_agent_playbook.yaml
```

### Step 3: Compile

```bash
super agent compile assistant_openai --framework openai
```

**What happens:**
- Reads SuperSpec YAML playbook
- Generates Python code using `openai_pipeline.py.jinja2`
- Creates `BaseComponent` wrapper for GEPA
- Initializes OpenAI Agent with Ollama model
- Creates evaluation and optimization methods

**Output:** `agents/assistant_openai/pipelines/assistant_openai_openai_pipeline.py`

### Step 4: Evaluate

```bash
super agent evaluate assistant_openai
```

**Expected Results:**
```
🔍 Evaluating assistant_openai...
Testing 4 BDD scenarios:

✅ OpenAI Agents SDK initialized with Ollama: gpt-oss:20b
✅ Simple greeting: PASS
✅ Question answering: PASS
✅ Explanation request: PASS
✅ Math question: PASS

Overall: 4/4 PASS (100.0%)
```

**Note**: Results depend on your model, hardware, and BDD scenario complexity. The agent loads optimized instructions automatically if available.

### Step 5: Optimize

```bash
super agent optimize assistant_openai --auto medium --framework openai --reflection-lm ollama:llama3.1:8b
```

**What GEPA optimizes:**
- **`instructions`**: The agent's system prompt

GEPA will test variations to find the best instructions!

**Note:** Requires `--reflection-lm` parameter for Universal GEPA optimization

### Step 6: Re-evaluate

```bash
super agent evaluate assistant_openai
```

See if GEPA improved the pass rate!

### Step 7: Run

```bash
super agent run assistant_openai --goal "Explain quantum computing"
```

---

## 🔧 How It Works

### BaseComponent Wrapper

```python
class AssistantOpenAiComponent(BaseComponent):
    def __init__(self, instructions=None, model_config=None, ...):
        super().__init__(
            name="assistant_openai",
            variable=instructions,  # GEPA optimizes this!
            variable_type="instructions",
            framework="openai",
            ...
        )
    
    def _initialize_model(self):
        # Detect Ollama vs OpenAI
        if model_str.startswith("ollama:"):
            self._model = OpenAIChatCompletionsModel(
                model="gpt-oss:20b",
                openai_client=AsyncOpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama",
                ),
            )
    
    def _initialize_agent(self):
        self._agent = Agent(
            name="Assistant",
            instructions=self.variable,  # GEPA optimizes!
            tools=self._tools,
            model=self._model,
        )
    
    def forward(self, **inputs):
        result = Runner.run_sync(self._agent, input=query)
        return {"response": result.final_output}
    
    def update(self, new_variable):
        # GEPA calls this during optimization
        self.variable = new_variable
        self._agent = None  # Reinitialize with new instructions
```

### Pipeline Class

```python
class AssistantOpenAiPipeline:
    def __init__(self, playbook_path=None):
        # Load playbook and BDD scenarios
        self.component = create_assistant_open_ai_agent(model_config=...)
        self.test_scenarios = self._load_bdd_scenarios()
    
    def run(self, **inputs):
        return self.component.forward(**inputs)
    
    def evaluate(self):
        # Run all BDD scenarios
        for scenario in self.test_scenarios:
            result = self.run(**scenario["input"])
            # Evaluate against expected output
    
    def optimize_with_gepa(self, auto="medium"):
        # Universal GEPA optimization
        optimizer = UniversalGEPA(...)
        result = optimizer.compile(
            component=self.component,
            trainset=trainset,
            valset=valset
        )
    
    def run_bdd_test_suite(self):
        # CLI compatibility
        return self.evaluate()
```

---

## 📊 OpenAI SDK vs Other Frameworks

| Feature | DSPy | DeepAgents | OpenAI SDK |
|---------|------|------------|------------|
| **Ollama Support** | ✅ Full | ❌ Blocked | ✅ Perfect |
| **Baseline Performance** | Good | N/A | Excellent |
| **API Complexity** | Medium | High | Low |
| **Planning** | Manual | Built-in | Manual |
| **Multi-Agent** | Manual | Subagents | Handoffs |
| **GEPA Optimization** | All signatures | system_prompt | instructions |
| **Best For** | Prompt optimization | Complex planning | Simple tasks |

### When to Use OpenAI SDK

✅ **Perfect for:**
- Simple to moderate complexity tasks
- Local development with Ollama
- Quick prototyping
- Clean, minimal agent design
- When you want high baseline performance

❌ **Not ideal for:**
- Complex multi-step planning (use DeepAgents)
- Maximum prompt optimization (use DSPy)
- Need filesystem context management (use DeepAgents)

---

## 🎓 Example Use Cases

### Question Answering Agent

```yaml
persona:
  role: Knowledge Expert
  goal: Answer questions accurately and concisely

feature_specifications:
  scenarios:
    - name: Python question
      input:
        query: "What is Python?"
      expected_output:
        expected_keywords:
          - Python
          - programming
          - language
```

### Customer Support Agent

```yaml
persona:
  role: Customer Support Specialist
  goal: Help customers with their issues professionally

tools:
  specific_tools:
    - check_order_status
    - process_refund
    - escalate_to_human
```

### Code Explainer

```yaml
persona:
  role: Senior Software Engineer
  goal: Explain code concepts clearly to beginners

reasoning:
  steps:
    - Analyze the code or concept
    - Break down complex ideas
    - Provide clear explanations with examples
```

---

## ⚙️ Advanced Features

### Tools Support

```yaml
tools:
  enabled: true
  specific_tools:
    - name: search_database
      description: Search knowledge base
    - name: send_email
      description: Send email to user
```

Implement in generated pipeline:

```python
@function_tool
def search_database(query: str) -> str:
    """Search the knowledge base."""
    return f"Results for: {query}"

tools = [search_database]
```

### Multi-Agent Handoffs

```yaml
handoffs:
  - name: specialist_agent
    description: Hand off complex technical questions
    instructions: You are a technical specialist
```

### Guardrails

```yaml
guardrails:
  input:
    - type: content_filter
      params:
        block_harmful: true
  output:
    - type: pii_detector
      params:
        redact: true
```

---

## 🐛 Troubleshooting

### Agent Not Responding

**Symptom:** Agent returns empty response

**Checklist:**
1. ✅ Ollama running? (`curl http://localhost:11434/api/tags`)
2. ✅ Model downloaded? (`ollama list`)
3. ✅ Correct model string? (`ollama:gpt-oss:20b`)

### Low Pass Rate

**Symptom:** Scenarios failing

**Solutions:**
1. Check BDD scenario keywords are realistic
2. Lower threshold to 0.4 or 0.5
3. Run GEPA optimization to improve instructions
4. Try different model (llama3.1:70b or gpt-oss:120b for more capability)

### Import Error

**Symptom:** `ModuleNotFoundError: No module named 'agents'`

**Solution:**
```bash
pip install openai-agents
```

---

## 🎯 GEPA Optimization

### What Gets Optimized

OpenAI Agents SDK has one main optimizable variable:
- **`instructions`**: The agent's system prompt

### How GEPA Optimizes OpenAI SDK Agents

GEPA optimizes the **instructions** field by:

1. **Analyzing BDD test scenarios** to understand success criteria
2. **Generating variations** of the instructions prompt
3. **Testing each variation** against your evaluation scenarios
4. **Selecting the best performer** based on pass rate

**Example transformation:**

```yaml
# Original (from playbook)
persona:
  role: Helpful AI Assistant
  goal: Provide clear responses

→ instructions = "Helpful AI Assistant\nGoal: Provide clear responses"
```

```yaml
# After GEPA optimization
→ instructions = "You are a Helpful AI Assistant.

When answering questions:
1. Read the question carefully
2. Provide accurate, factual information
3. Use clear, simple language
4. Be concise but complete

Goal: Provide clear, helpful responses that directly address the user's query."
```

GEPA typically expands the instructions to be more explicit and structured, which can improve agent behavior consistency.

---

## 📈 Performance Characteristics

### Baseline Performance

**Task:** General question answering
**Model:** Ollama gpt-oss:20b
**Framework:** OpenAI Agents SDK

OpenAI SDK typically achieves good baseline performance with local Ollama models. Results will vary based on:
- Your hardware capabilities (RAM, CPU/GPU)
- Model size and quality (8b vs 20b vs 120b)
- BDD scenario complexity
- Temperature and other model parameters

### Framework Comparison

**OpenAI SDK strengths:**
- Clean, simple API makes agents easier to understand
- Works seamlessly with Ollama (no function-calling limitations)
- Good baseline performance out of the box

**DSPy strengths:**
- More optimization targets (all signatures, not just instructions)
- Better for focused, well-defined tasks
- Greater improvement potential through optimization

**DeepAgents limitations:**
- Requires cloud models (Claude/GPT-4) due to LangChain function-calling requirements
- Cannot be tested with Ollama

---

## 🏗️ Architecture

```
SuperSpec YAML Playbook
        ↓
    Compiler (AgentCompiler)
        ↓
OpenAI Pipeline Template (openai_pipeline.py.jinja2)
        ↓
Generated Python Pipeline
        ├─ AssistantOpenAIComponent (BaseComponent wrapper)
        │   ├─ _initialize_model() → OpenAIChatCompletionsModel (Ollama)
        │   ├─ _initialize_agent() → Agent(instructions, tools, model)
        │   └─ forward() → Runner.run_sync()
        └─ AssistantOpenAIPipeline
            ├─ run()
            ├─ evaluate()
            ├─ optimize_with_gepa() ← Universal GEPA
            └─ run_bdd_test_suite()
```

---

## 🔄 Model Configuration

### Ollama (Local) - RECOMMENDED ⭐

```yaml
language_model:
  location: local
  provider: ollama
  model: ollama:gpt-oss:20b
  temperature: 0.7
  max_tokens: 2000
  api_base: http://localhost:11434
```

**Advantages:**
- ✅ Free inference
- ✅ Privacy (data stays local)
- ✅ Fast development iteration
- ✅ Good baseline performance

**Supported Ollama Models:**
- `ollama:llama3.1:8b` (default, fast and efficient)
- `ollama:gpt-oss:120b` (most capable, larger model)
- `ollama:gpt-oss:20b` (faster alternative)
- `ollama:qwen3:8b` (alternative)

### OpenAI (Cloud)

```yaml
language_model:
  provider: openai
  model: gpt-4.1
  temperature: 0.7
```

Set API key: `export OPENAI_API_KEY=your_key`

---

## 🎓 Comparison with Other Frameworks

### OpenAI SDK Advantages
- ✅ **Ollama compatibility** (unlike DeepAgents)
- ✅ **Good baseline performance**
- ✅ **Simple, clean API**
- ✅ **Built-in tracing and sessions**
- ✅ **Fast compilation and execution**

### DSPy Advantages
- ✅ **Maximum optimization** (all signatures)
- ✅ **More optimization targets**
- ✅ **Better for focused tasks**

### DeepAgents Advantages
- ✅ **Built-in planning** (write_todos)
- ✅ **Filesystem context** management
- ✅ **Subagent spawning**
- ❌ **Requires Claude/GPT-4** (no Ollama)

### Use Them Together!

```bash
# Simple tasks → OpenAI SDK (Ollama)
super agent compile assistant --framework openai

# Complex research → DeepAgents (Claude)
super agent compile researcher --framework deepagents

# Maximum optimization → DSPy (Ollama)
super agent compile analyzer --framework dspy
```

---

## 🛠️ Advanced Configuration

### With Tools

```yaml
spec:
  tools:
    enabled: true
    specific_tools:
      - name: get_weather
        description: Get weather for a city
      - name: send_email
        description: Send email to user
```

Then implement in code or use built-in tools.

### With Handoffs (Multi-Agent)

```yaml
spec:
  handoffs:
    - name: technical_specialist
      description: Handles technical questions
      instructions: You are a technical expert
    
    - name: billing_specialist
      description: Handles billing issues
      instructions: You handle billing and payments
```

### With Guardrails

```yaml
spec:
  guardrails:
    input_guardrails:
      - type: content_safety
        params:
          block_harmful: true
    
    output_guardrails:
      - type: pii_filter
        params:
          redact_emails: true
          redact_phones: true
```

---

## 📊 Framework Trade-offs

### Model Support Comparison

| Framework | Local Models (Ollama) | Cloud Models | Optimization Targets |
|-----------|----------------------|--------------|---------------------|
| **OpenAI SDK** | ✅ Full support | ✅ Yes | Instructions only |
| **DSPy** | ✅ Full support | ✅ Yes | Multiple signatures |
| **DeepAgents** | ❌ Limited* | ✅ Yes | System prompt |

*DeepAgents has LangChain function-calling limitations with local models

### Cost & Development Speed

| Framework | Development Complexity | Ollama Cost | Cloud Cost |
|-----------|----------------------|-------------|------------|
| **OpenAI SDK** | Low (simple API) | Free | Variable |
| **DSPy** | Medium (more concepts) | Free | Variable |
| **DeepAgents** | High (planning graphs) | N/A | Variable |

**Note:** Actual performance depends on your specific use case, model choice, and BDD scenarios. Always evaluate with your own data.

---

## 🎯 Real-World Examples

### Customer Support Bot

```yaml
metadata:
  name: Support Bot
  id: support_bot

spec:
  persona:
    role: Customer Support Specialist
    goal: Resolve customer issues efficiently
    traits:
      - patient
      - empathetic
      - solution-focused
  
  tools:
    specific_tools:
      - check_order_status
      - process_refund
      - escalate_ticket
```

### Code Helper

```yaml
metadata:
  name: Code Helper
  id: code_helper

spec:
  persona:
    role: Senior Developer
    goal: Help developers with code questions
    communication_preferences:
      style: technical
      verbosity: detailed
```

### Content Writer

```yaml
metadata:
  name: Content Writer
  id: content_writer

spec:
  persona:
    role: Professional Content Writer
    goal: Create engaging, high-quality content
    traits:
      - creative
      - detail-oriented
```

---

## 🔬 Under the Hood

### Ollama Integration

The template automatically detects Ollama and configures correctly:

```python
if model_str.startswith("ollama:"):
    model_name = model_str.replace("ollama:", "")
    api_base = config.get("api_base", "http://localhost:11434")
    
    self._model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(
            base_url=f"{api_base}/v1",
            api_key="ollama",
        ),
    )
```

This is based on the official OpenAI Agents SDK example for Ollama!

### Agent Execution Flow

1. User input received
2. Component's `forward()` called
3. Agent initialized (lazy, cached)
4. `Runner.run_sync(agent, input)` executed
5. OpenAI Agent processes with Ollama
6. `result.final_output` returned
7. Mapped to output fields

---

## 🎯 The SuperOptiX Multi-Framework Advantage

### One Playbook, Multiple Frameworks

SuperOptiX allows you to write your agent specification once and compile to any supported framework:

```bash
# Same playbook, different frameworks
super agent compile my_agent --framework dspy
super agent compile my_agent --framework openai
super agent compile my_agent --framework deepagents

# GEPA optimization works across all frameworks
super agent optimize my_agent --auto medium
```

### When to Use Each Framework

**Choose OpenAI SDK when:**
- You want simple, straightforward agent design
- You're using Ollama for local development
- You need fast prototyping and iteration
- Your use case is simple to moderate complexity

**Choose DSPy when:**
- You need maximum optimization flexibility
- You want to optimize multiple components (signatures)
- You have well-defined, focused tasks
- You want proven optimization improvements

**Choose DeepAgents when:**
- You need complex planning capabilities
- You're using cloud models (Claude/GPT-4)
- You need filesystem context management
- Your task requires sophisticated multi-step reasoning

---

## 💡 Tips & Best Practices

### 1. Start with OpenAI SDK for Prototyping
- Fast compilation
- Simple design
- Works with Ollama
- High baseline performance

### 2. Use Clear Instructions
```yaml
persona:
  role: Expert Assistant
  goal: Specific, measurable goal
  # Be specific about what the agent should do
```

### 3. Realistic BDD Scenarios
```yaml
scenarios:
  - name: Specific test case
    input:
      query: "Concrete question"
    expected_output:
      expected_keywords:
        - keyword1
        - keyword2
```

### 4. Iterate and Optimize
1. Get baseline working
2. Add more scenarios
3. Run GEPA optimization
4. Deploy best version

---

## ❓ FAQ

**Q: Why use OpenAI SDK instead of DSPy?**
A: OpenAI SDK has a simpler, more straightforward API. It works well with Ollama out of the box. Choose DSPy when you need to optimize multiple components (signatures) or want maximum optimization flexibility.

**Q: Does it work with Ollama?**
A: Yes! OpenAI SDK has full Ollama support. Unlike DeepAgents (which has LangChain function-calling limitations), OpenAI SDK works seamlessly with local models.

**Q: Can I use cloud models?**
A: Yes! Configure your playbook with `provider: openai` and set the `OPENAI_API_KEY` environment variable. Supports OpenAI, Anthropic, and other providers.

**Q: Does GEPA optimize OpenAI SDK agents?**
A: Yes! Universal GEPA optimizes the `instructions` field. While OpenAI SDK has fewer optimization targets than DSPy (which optimizes all signatures), GEPA can still improve performance by refining the agent instructions.

**Q: Can I use tools with OpenAI SDK agents?**
A: Yes! Define tools in your playbook under `tools.specific_tools` and implement them using the `@function_tool` decorator in your pipeline code.

**Q: What about multi-agent workflows?**
A: OpenAI SDK supports multi-agent patterns through `handoffs`, where one agent can delegate to another. This is similar to CrewAI's crew concept but with a simpler API.

**Q: How does performance compare to other frameworks?**
A: Performance varies by use case, model, and hardware. OpenAI SDK typically has good baseline performance with Ollama. Run your own evaluations with `super agent evaluate` to measure performance for your specific use case.

---

## 📚 Additional Resources

- **OpenAI Agents SDK Docs**: https://openai.github.io/openai-agents-python/
- **Ollama Setup**: `/docs/llm-setup.md`
- **Multi-Framework Guide**: `/docs/guides/multi-framework.md`
- **Universal GEPA**: `/plan/MULTI_FRAMEWORK_GEPA_STRATEGY.md`
- **Hands-on Repo**: [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) — clone this MIT-licensed companion project to try the OpenAI Agents SDK with SuperOptiX Lite and follow our Code Reviewer tutorial step by step.

---

## 🌐 Multi-Framework Summary

**SuperOptiX supports 6 agent frameworks:**
1. ✅ DSPy (maximum optimization, Ollama compatible)
2. ✅ OpenAI SDK (simple API, excellent Ollama support)
3. ✅ CrewAI (multi-agent teams, role-based collaboration)
4. ✅ Google ADK (Gemini integration)
5. ✅ Microsoft (Azure OpenAI, enterprise)
6. ✅ DeepAgents (complex planning, Claude/GPT-4)

**All frameworks share:**
- Same SuperSpec YAML format
- Same CLI workflow (`compile`, `evaluate`, `optimize`, `run`)
- Same GEPA optimization engine
- Framework-specific strengths preserved

**Learn more:** See the [Multi-Framework Guide](multi-framework.md) for comprehensive comparisons and examples.

---

## 🚀 Getting Started

Ready to try OpenAI SDK with SuperOptiX?

```bash
# Pull the demo agent
super agent pull assistant_openai

# Start with Ollama (free, local)
super agent run assistant_openai --goal "Hello!"
```

---

## 📖 Next Steps

Want to build your own custom agent with native OpenAI SDK patterns and optimize it with GEPA?

### 🔧 [OpenAI SDK + GEPA Optimization Tutorial](../tutorials/openai-sdk-gepa-optimization.md)

This comprehensive step-by-step tutorial teaches you how to:

✅ Write agents using **official OpenAI Agents SDK patterns** (Agent, Runner, OpenAIChatCompletionsModel)
✅ Integrate your native SDK code with **SuperOptiX** for GEPA compatibility
✅ Define **BDD test scenarios** for measurable evaluation metrics
✅ Run **GEPA optimization** to automatically improve agent prompts
✅ Implement **automatic optimization loading** for production deployment

**Example project:** Code Reviewer Agent that detects security vulnerabilities
**Hands-on repo:** [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) — clone it to follow the tutorial with a fully wired SuperOptiX Lite playground.

**Time:** 30-45 minutes | **Difficulty:** Intermediate | **Prerequisites:** Python, Ollama, Git access to the repo above

👉 **[Start the tutorial now](../tutorials/openai-sdk-gepa-optimization.md)**


