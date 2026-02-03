# 📗 SuperSpec DSL Reference

<div align="center">
  <img src="../logo.png" alt="SuperOptiX Logo" width="150" style="margin-bottom: 10px;"/>
  <h2 style="margin-top: 10px; margin-bottom: 10px;">SuperSpec DSL Complete Reference</h2>
  <p style="margin-top: 10px; margin-bottom: 20px;"><strong>Universal agent specification language for all 6 frameworks</strong></p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="../superspec/" style="background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📝 SuperSpec Overview</a>
  <a href="../superspec-agent-building/" style="background: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🏗️ Agent Building</a>
  <a href="../superspec-dsl-examples/" style="background: #FF9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📙 DSL Examples</a>
  <a href="../superspec-configuration/" style="background: #9C27B0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚙️ Configuration</a>
</div>

---

## 📋 Complete SuperSpec Schema

### Top-Level Structure

```yaml
apiVersion: agent/v1                    # REQUIRED - Schema version
kind: AgentSpec                        # REQUIRED - Object type
metadata:                              # REQUIRED - Agent identity
spec:                                  # REQUIRED - Agent specification
```

---

## 🏷️ Metadata Section

The `metadata` section defines the agent's identity and basic properties.

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 25%;">Field</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 15%;">Required</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 20%;">Type</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 40%;">Description</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>name</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">✅ Yes</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">string</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Human-readable agent name</td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>id</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">✅ Yes</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">string</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Unique identifier (a-z, 0-9, -, _)</td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>version</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">✅ Yes</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">string</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Semantic versioning (e.g., "1.0.0")</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>namespace</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Optional</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">string</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Logical grouping namespace</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>level</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Optional</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">oracles | genies</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Agent tier level (default: oracles)</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>description</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Optional</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">string</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Brief agent description</td>
  </tr>
</table>

### Example Metadata

```yaml
metadata:
  name: sentiment_analyzer
  id: sentiment_analyzer
  namespace: testing
  version: 1.0.0
  level: oracles
  description: Analyzes sentiment of text input
  tags:
    - nlp
    - sentiment-analysis
    - text-processing
```

---

## 🎯 Spec Section

The `spec` section contains all agent configuration.

### Required Fields

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 30%;">Field</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 70%;">Description</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>target_framework</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Framework choice: <code>dspy</code>, <code>openai</code>, <code>crewai</code>, <code>google-adk</code>, <code>microsoft</code>, <code>deepagents</code></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>language_model</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">LLM configuration (provider, model, API settings)</td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>input_fields</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">List of input field specifications</td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>output_fields</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">List of output field specifications</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>feature_specifications</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">BDD scenarios for evaluation (universal across all frameworks)</td>
  </tr>
</table>

---

## 🤖 Language Model Configuration

Configure your LLM for any provider.

### Ollama (Local, Recommended)

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
    temperature: 0.7
    max_tokens: 1000
```

### OpenAI

```yaml
spec:
  language_model:
    provider: openai
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
    max_tokens: 1000
```

### Google Gemini

```yaml
spec:
  language_model:
    provider: google
    model: gemini-2.0-flash
    api_key: ${GOOGLE_API_KEY}
    temperature: 0.7
```

### Azure OpenAI

```yaml
spec:
  language_model:
    provider: azure
    model: gpt-4
    api_key: ${AZURE_OPENAI_API_KEY}
    api_base: ${AZURE_OPENAI_ENDPOINT}
    api_version: "2024-02-15-preview"
```

### MLX (Apple Silicon)

```yaml
spec:
  language_model:
    provider: mlx
    model: mlx-community/Llama-3-8B-Instruct-4bit
    temperature: 0.7
```

---

## 👤 Persona Configuration

Define your agent's personality and approach.

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 30%;">Field</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3); width: 70%;">Description</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>role</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Agent's role (e.g., "AI Research Assistant")</td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>goal</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Agent's primary objective</td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>backstory</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Agent's background context (multi-line supported)</td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>instructions</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Direct instructions for the agent (OpenAI SDK, Google ADK, Microsoft style)</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>reasoning.steps</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">List of reasoning steps the agent should follow</td>
  </tr>
</table>

### Example Persona (DSPy/CrewAI Style)

```yaml
spec:
  persona:
    role: AI Research Assistant
    goal: Help researchers find and analyze academic papers
    backstory: |
      You are an experienced research assistant with expertise in
      literature review and academic analysis. You help researchers
      discover relevant papers and extract key insights.
    reasoning:
      steps:
        - Understand the research question
        - Search for relevant papers
        - Analyze key findings
        - Summarize insights
```

### Example Persona (OpenAI SDK/Google ADK/Microsoft Style)

```yaml
spec:
  persona:
    instructions: |
      You are a helpful AI assistant that provides accurate,
      well-researched responses to user queries.
      
      Your approach:
      1. Understand the user's question
      2. Gather relevant information
      3. Formulate a clear response
      4. Provide helpful insights
```

---

## 📥 Input & Output Fields

Define the agent's interface with strongly typed fields.

### Input Fields

```yaml
spec:
  input_fields:
    - name: query
      type: str
      description: User's question or request
      required: true
    
    - name: context
      type: str
      description: Additional context for the query
      required: false
      default: ""
```

### Output Fields

```yaml
spec:
  output_fields:
    - name: response
      type: str
      description: Agent's response to the query
    
    - name: confidence
      type: float
      description: Confidence score (0.0-1.0)
      default: 0.0
```

---

## 🎯 Tasks Configuration (CrewAI/DeepAgents)

Define tasks for multi-agent or complex workflow frameworks.

```yaml
spec:
  tasks:
    - name: research_task
      description: |
        Research the given topic and gather relevant information
        from multiple sources.
      expected_output: |
        A comprehensive summary with key findings, citations,
        and recommendations for further reading.
      agent: researcher  # Optional: assign to specific agent
```

---

## 🔌 Tools Configuration

Add tools for your agent to use.

### Built-in Tools

```yaml
spec:
  tools:
    - name: web_search
      type: builtin
      enabled: true
      config:
        max_results: 5
        
    - name: calculator
      type: builtin
      enabled: true
```

### Custom Tools

```yaml
spec:
  tools:
    - name: custom_api
      type: custom
      function: my_module.my_function
      description: Calls custom API endpoint
      parameters:
        endpoint: https://api.example.com
        api_key: ${API_KEY}
```

---

## 🧠 Memory Configuration

Configure short-term and long-term memory.

```yaml
spec:
  memory:
    enabled: true
    backend: sqlite
    short_term:
      max_size: 100
      retention_policy: lru
    long_term:
      enabled: true
      semantic_search: true
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
```

---

## 📚 RAG Configuration

Enable Retrieval-Augmented Generation.

### Vector Database RAG

```yaml
spec:
  rag:
    enabled: true
    vector_db:
      type: chromadb
      collection_name: my_knowledge
      persist_directory: ./data/chroma
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
```

### MCP Protocol RAG

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
    config:
      top_k: 5
```

---

## ✅ Feature Specifications (BDD Scenarios)

Define behavior-driven test scenarios (universal across all frameworks).

```yaml
spec:
  feature_specifications:
    scenarios:
      - name: Simple greeting
        input:
          query: "Hello, how are you?"
        expected_output:
          response: "I am doing well"
          expected_keywords:
            - hello
            - well
            - assistant
      
      - name: Domain-specific query
        input:
          query: "What is quantum entanglement?"
        expected_output:
          response: "quantum entanglement explanation"
          expected_keywords:
            - quantum
            - entanglement
            - particles
```

---

## 🧬 Optimization Configuration

Configure GEPA optimizer (universal across all frameworks).

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: medium                    # light, medium, intensive
        reflection_lm: qwen3:8b
        reflection_minibatch_size: 3
        skip_perfect_score: true
        add_format_failure_as_feedback: true
```

### Optimization Modes

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Mode</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Iterations</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Time</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Best For</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">light</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">3-5</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">5-10 min</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Quick testing, rapid prototyping</td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">medium</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">10-15</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">15-30 min</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Production agents, balanced quality/speed</td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">intensive</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">20-30</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30-60 min</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Critical agents, maximum performance</td>
  </tr>
</table>

---

## 🔧 Framework-Specific Sections

### DSPy-Specific

```yaml
spec:
  target_framework: dspy
  dspy:
    signature_type: ChainOfThought  # or Predict, ReAct
    max_retries: 3
```

### CrewAI-Specific

```yaml
spec:
  target_framework: crewai
  tasks:
    - name: research
      description: Conduct research on the topic
      expected_output: Detailed research summary
```

### OpenAI SDK-Specific

```yaml
spec:
  target_framework: openai
  persona:
    instructions: |
      You are a helpful assistant that provides accurate responses.
```

---

## 📊 Complete Example: Multi-Framework Agent

Here's a complete SuperSpec that can be compiled to ANY framework:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: research_assistant
  id: research_assistant
  namespace: research
  version: 1.0.0
  level: genies
  description: AI research assistant that helps find and analyze information

spec:
  target_framework: dspy  # Change to: openai, crewai, google-adk, microsoft, deepagents
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
    temperature: 0.7
  
  persona:
    role: AI Research Assistant
    goal: Help users find and analyze relevant information
    backstory: |
      You are an experienced research assistant with expertise in
      information retrieval and analysis.
    reasoning:
      steps:
        - Understand the research question
        - Search for relevant information
        - Analyze and synthesize findings
        - Present clear, actionable insights
  
  input_fields:
    - name: query
      type: str
      description: Research question or topic
  
  output_fields:
    - name: response
      type: str
      description: Research findings and analysis
  
  tools:
    - name: web_search
      type: builtin
      enabled: true
  
  rag:
    enabled: true
    vector_db:
      type: chromadb
      collection_name: research_docs
    config:
      top_k: 5
  
  memory:
    enabled: true
    short_term:
      max_size: 50
  
  feature_specifications:
    scenarios:
      - name: Basic research query
        input:
          query: "What is machine learning?"
        expected_output:
          response: "machine learning explanation"
          expected_keywords:
            - machine learning
            - algorithms
            - data
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: medium
```

---

## 🎯 Field Type Reference

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Type</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Python Type</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Description</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>str</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>str</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Text string</td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>int</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>int</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Integer number</td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>float</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>float</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Floating point number</td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>bool</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>bool</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Boolean (true/false)</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>list</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><code>List</code></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Array of items</td>
  </tr>
</table>

---

## 🚀 Next Steps

<div align="center" style="margin: 30px 0;">
  <a href="../superspec-dsl-examples/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📙 See DSL Examples</a>
  <a href="../superspec-agent-building/" style="background: #2196F3; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🏗️ Build Your Agent</a>
  <a href="../superspec-configuration/" style="background: #FF9800; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚙️ Full Configuration</a>
  <a href="../../quick-start/" style="background: #9C27B0; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 Quick Start</a>
</div>

