# 💎 SuperSpec - Universal Agent Specification

<div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, var(--md-primary-fg-color--light) 0%, var(--md-accent-fg-color--light) 25%, var(--md-primary-fg-color--lighter) 50%, var(--md-accent-fg-color--lighter) 75%, var(--md-primary-fg-color--lightest) 100%); border-radius: var(--border-radius); color: var(--md-default-fg-color); border: 2px solid var(--md-primary-fg-color--light);">
    <h2 style="color: var(--md-default-fg-color);">💎 SuperSpec - Universal Agent Specification</h2>
    <p style="font-size: 1.2rem; margin-bottom: 2rem; color: var(--md-default-fg-color);">
        <strong>SuperSpec is our declarative DSL that works across all 6 major agent frameworks.</strong><br>
        Think of it as "Kubernetes for AI agents" - you describe what you want, choose your framework, and SuperOptiX builds the entire pipeline.
    </p>
    
    <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <div style="background: rgba(255, 255, 255, 0.1); padding: 0.75rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <span style="font-size: 1.2rem;">📝</span> <strong>Declarative Agent Specs</strong>
        </div>
        <div style="background: rgba(255, 255, 255, 0.1); padding: 0.75rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <span style="font-size: 1.2rem;">🔧</span> <strong>Multi-Framework Support</strong>
        </div>
        <div style="background: rgba(255, 255, 255, 0.1); padding: 0.75rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <span style="font-size: 1.2rem;">🧪</span> <strong>BDD-Style Testing</strong>
        </div>
        <div style="background: rgba(255, 255, 255, 0.1); padding: 0.75rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <span style="font-size: 1.2rem;">⚙️</span> <strong>GEPA Optimization</strong>
        </div>
    </div>
</div>

## 🎯 **What is SuperSpec?**

**SuperSpec** (pronounced `/suː.pər spɛk/`) is the **universal specification language** for AI agents across all major frameworks. It's designed to provide the **just-right context** to agents so they perform better - not too much, not too little, but striking the perfect balance.

**🌟 Key Achievement**: One specification format works across DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, and DeepAgents!

### **Core Philosophy: Framework Freedom**

SuperSpec enables you to:
- **Choose Your Framework**: Select from 6 major frameworks based on your needs
- **Keep Your Workflow**: Same compile → evaluate → optimize → run cycle
- **Optimize Universally**: GEPA works across all frameworks
- **Version Control Everything**: Git-based agent management

```mermaid
graph LR
    A[SuperSpec YAML] --> B[Choose Framework]
    B --> C[Compile to Native Code]
    C --> D[GEPA Optimization]
    D --> E[Production Deployment]
    
    style A fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#a855f7,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    style D fill:#d97706,stroke:#f59e0b,stroke-width:2px,color:#ffffff
    style E fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
```

### **Context Engineering**

Context engineering is the systematic approach to designing dynamic systems that deliver precisely the right information and tools in the optimal format, enabling LLMs to successfully accomplish their intended tasks. **When agents fail to perform reliably, the root cause is almost always insufficient or poorly structured context, unclear instructions, or missing tools that haven't been properly communicated to the model.**

### **Agent Engineering**

Agent engineering represents the next evolution of AI engineering. Rather than developing systems with static, hardcoded logic, engineers now design autonomous, goal-driven entities capable of using tools, accessing memory, engaging in reflective reasoning, and operating within safety constraints.

## 🏗️ **SuperSpec Design Principles**

### **1. Declarative & Strongly Typed**
SuperSpec is **declarative** and **strongly typed** to ensure strong contracts between context and LLM output. This contract then converts into **DSPy Signatures** which validate the output even further.

### **2. Kubernetes-Inspired**
Like Kubernetes DSL for declaring pods, deployments, and services, SuperSpec provides a **Kubernetes-style declarative specification** for AI agents:

```yaml
# Kubernetes-style declarative approach
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: my-agent
  namespace: production
spec:
  # Declare what you want, not how to get it
```

### **3. Version Controllable**
SuperSpec specifications are **totally version controllable** and context can be versioned, enabling:
- **Git-based agent management**
- **Rollback capabilities**
- **A/B testing of agent configurations**
- **Team collaboration on agent development**

## 📋 **SuperSpec Structure Overview**

### **Top-Level Fields**

```yaml
apiVersion: agent/v1                    # REQUIRED - Schema version
kind: AgentSpec                        # REQUIRED - Object type
metadata:                              # REQUIRED - Agent identity
spec:                                  # REQUIRED - Agent specification
  target_framework: string             # REQUIRED - Framework choice (dspy, openai, crewai, google-adk, microsoft, deepagents)
  language_model:                      # REQUIRED - LLM configuration
  persona:                             # OPTIONAL - Agent personality
  tasks:                               # REQUIRED - Agent capabilities (framework-specific)
  agentflow:                           # OPTIONAL - Execution flow
  tools:                               # OPTIONAL - Tool integration
  memory:                              # OPTIONAL - Memory systems
  rag:                                 # OPTIONAL - Knowledge retrieval
  evaluation:                          # OPTIONAL - Quality metrics
  feature_specifications:              # REQUIRED - BDD scenarios (universal)
  optimization:                        # OPTIONAL - GEPA optimization (universal)
```

## 🔧 **Multi-Framework Support**

### **Choosing Your Framework**

SuperSpec supports 6 major agent frameworks. Select based on your needs:

=== "🔬 DSPy"
    ```yaml
    spec:
      target_framework: dspy  # Pure DSPy mode
      language_model:
        provider: ollama
        model: llama3.1:8b
    ```
    **Best For**: Complex reasoning, 10+ optimizable variables

=== "🤖 OpenAI SDK"
    ```yaml
    spec:
      target_framework: openai  # OpenAI Agents SDK
      language_model:
        provider: ollama
        model: gpt-oss:20b
    ```
    **Best For**: Simple & fast, works with Ollama

=== "👥 CrewAI"
    ```yaml
    spec:
      target_framework: crewai  # Multi-agent collaboration
      language_model:
        provider: ollama
        model: llama3.1:8b
    ```
    **Best For**: Multi-agent teams, role-based agents

=== "🔮 Google ADK"
    ```yaml
    spec:
      target_framework: google-adk  # Gemini native
      language_model:
        provider: google
        model: gemini-2.0-flash
    ```
    **Best For**: Gemini 2.0, free tier available

=== "🏢 Microsoft"
    ```yaml
    spec:
      target_framework: microsoft  # Enterprise Azure
      language_model:
        provider: ollama
        model: gpt-oss:20b
    ```
    **Best For**: Enterprise Azure integration

=== "🌊 DeepAgents"
    ```yaml
    spec:
      target_framework: deepagents  # Complex planning
      language_model:
        provider: ollama
        model: llama3.1:8b
    ```
    **Best For**: LangGraph planning, advanced reasoning

### **Framework Comparison**

| Framework | Variables | Local Models | Best For |
|-----------|-----------|--------------|----------|
| **DSPy** | 10+ | Ollama | Complex reasoning, research |
| **OpenAI SDK** | 1 | Ollama | Simple & fast |
| **CrewAI** | 5 | Ollama | Multi-agent teams |
| **Google ADK** | 1 | Cloud only | Gemini native, free tier |
| **Microsoft** | 1 | Ollama | Enterprise Azure |
| **DeepAgents** | 1 | Ollama | Complex planning |

### **Learning Path: Beginner to Advanced**

| Level | Focus | Key Concepts |
|-------|-------|--------------|
| **🟢 Beginner** | Basic Structure | `metadata`, `language_model`, `persona`, `tasks` |
| **🟡 Intermediate** | Execution Flow | `agentflow`, `evaluation`, `feature_specifications` |
| **🔴 Advanced** | Advanced Features | `tools`, `memory`, `rag`, `optimization` |

## 🎯 **Beginner Level: Core Components**

### **Metadata Section**

The `metadata` section defines the agent's identity and basic properties.

#### **Required Fields**

```yaml
metadata:
  name: string                         # REQUIRED - Human-readable name
  id: string                           # REQUIRED - Unique identifier
  version: string                      # REQUIRED - Agent version (e.g., "1.0.0")
```

#### **Optional Fields**

```yaml
metadata:
  namespace: string                    # OPTIONAL - Logical grouping (e.g., "software", "finance")
  agent_type: Autonomous|Supervised|Interactive|Reactive|Deliberative|Hybrid  # OPTIONAL
  level: oracles|genies  # OPTIONAL - Capability tier (available: oracles, genies only)
  description: string                  # OPTIONAL - Brief description
  tags: [string]                       # OPTIONAL - Categorization tags
```

#### **Example**

```yaml
metadata:
  name: Developer Assistant
  id: developer
  namespace: software
  version: "1.0.0"
  agent_type: Supervised
  level: oracles
  description: An agent that helps write clean, efficient, and maintainable code.
  tags: ["development", "coding", "software"]
```

### **Language Model Configuration**

The `language_model` section configures the underlying LLM that powers your agent.

#### **Required Fields**

```yaml
spec:
  language_model:
    location: local|self-hosted|cloud  # REQUIRED - Model hosting location
    provider: string                   # REQUIRED - Model provider
    model: string                      # REQUIRED - Specific model identifier
```

#### **Location-Specific Providers**

| Location | Supported Providers |
|----------|-------------------|
| **local** | `ollama`, `vllm`, `sg_lang`, `mlx`, `lm_studio`, `custom` |
| **self-hosted** | `custom` |
| **cloud** | `openai`, `anthropic`, `google`, `azure`, `mistral`, `cohere`, `groq`, `deepseek` |

#### **Optional Configuration**

```yaml
spec:
  language_model:
    # Model behavior
    temperature: float                  # OPTIONAL (default: 0.0) - Randomness control
    max_tokens: int                     # OPTIONAL (default: 4000) - Max output length
    top_p: float                        # OPTIONAL (default: 1.0) - Nucleus sampling
    
    # API configuration (for local/cloud)
    api_base: string                    # OPTIONAL - API endpoint (e.g., "http://localhost:11434")
    api_key: string                     # OPTIONAL - API key (or use environment variables)
    
    # Model capabilities
    modalities: [text|image|audio|video] # OPTIONAL (default: [text])
```

#### **Examples**

##### **Oracles Tier (Local)**
```yaml
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.2:1b
    api_base: http://localhost:11434
    temperature: 0.0
    max_tokens: 2048
```

##### **Genies Tier (Local)**
```yaml
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
    temperature: 0.7
    max_tokens: 2048
```

##### **Cloud Provider**
```yaml
spec:
  language_model:
    location: cloud
    provider: openai
    model: o3-mini
    temperature: 1.0
    max_tokens: 20000
```

### **Persona Configuration**

The `persona` section defines the agent's personality, role, and behavioral characteristics.

#### **Required Fields**

```yaml
spec:
  persona:
    role: string                        # REQUIRED - Agent's role (e.g., "Software Developer")
```

#### **Optional Fields**

```yaml
spec:
  persona:
    name: string                        # OPTIONAL - Agent's name (e.g., "DevBot")
    goal: string                        # OPTIONAL - Primary objective
    traits: [string]                    # OPTIONAL - Personality characteristics
    expertise_areas: [string]           # OPTIONAL - Knowledge domains
    communication_preferences:          # OPTIONAL
      style: formal|casual|technical|conversational  # OPTIONAL (default: formal)
      tone: professional|friendly|authoritative|supportive  # OPTIONAL (default: professional)
      verbosity: concise|detailed|adaptive  # OPTIONAL (default: concise)
```

#### **Example**

```yaml
spec:
  persona:
    name: DevBot
    role: Software Developer
    goal: Write clean, efficient, and maintainable code
    traits:
    - analytical
    - detail-oriented
    - problem-solver
    expertise_areas:
    - software development
    - code review
    - debugging
    communication_preferences:
      style: technical
      tone: professional
      verbosity: detailed
```

### **Tasks Configuration**

The `tasks` section defines the agent's capabilities and what it can do.

#### **Required Structure**

```yaml
spec:
  tasks:                                # REQUIRED (minimum 1 task)
    - name: string                      # REQUIRED - Unique task name
      description: string               # REQUIRED - What the task achieves
      instruction: string               # REQUIRED - Core LLM instruction
      inputs:                           # REQUIRED (minimum 1 input)
        - name: string                  # REQUIRED - Input field name
          type: str|int|bool|float|list[str]|dict[str,Any]  # REQUIRED - Data type
          description: string           # REQUIRED - Field description
          required: bool                # REQUIRED - Whether mandatory
      outputs:                          # REQUIRED (minimum 1 output)
        - name: string                  # REQUIRED - Output field name
          type: str|int|bool|float|list[str]|dict[str,Any]  # REQUIRED - Data type
          description: string           # REQUIRED - Field description
```

#### **Input/Output Types**

| Type | Description | Example |
|------|-------------|---------|
| `str` | String text | `"Hello world"` |
| `int` | Integer number | `42` |
| `bool` | Boolean value | `true` |
| `float` | Decimal number | `3.14` |
| `list[str]` | List of strings | `["item1", "item2"]` |
| `dict[str,Any]` | Dictionary/object | `{"key": "value"}` |

#### **Example**

```yaml
spec:
  tasks:
  - name: implement_feature
    description: Implement software features based on requirements
    instruction: You are a Software Developer. Your goal is to write clean, efficient, and maintainable code. Implement the feature based on the provided requirement.
    inputs:
    - name: feature_requirement
      type: str
      description: A detailed description of the feature to implement.
      required: true
    outputs:
    - name: implementation
      type: str
      description: The code implementation of the feature.
```

## 🔄 **Intermediate Level: Execution Flow**

### **AgentFlow Configuration**

The `agentflow` section defines the sequence of steps the agent takes to complete tasks.

#### **Required Structure**

```yaml
spec:
  agentflow:                            # OPTIONAL - Execution flow
    - name: string                      # REQUIRED - Step name
      type: Generate|Think|ActWithTools|Search|Code|Compare|MultiHopSearch|Route  # REQUIRED
      task: string                      # REQUIRED - Task name to execute
      depends_on: [string]              # OPTIONAL - Dependencies
```

#### **Step Types**

| Type | Description | Use Case |
|------|-------------|----------|
| `Generate` | Generate content using LLM | Text generation, code writing |
| `Think` | Reasoning and analysis | Problem solving, decision making |
| `ActWithTools` | Use tools and APIs | External integrations |
| `Search` | Information retrieval | Knowledge lookup |
| `Code` | Code generation and execution | Software development |
| `Compare` | Compare multiple options | Evaluation and selection |
| `MultiHopSearch` | Multi-step information gathering | Complex research |
| `Route` | Route to different steps | Conditional logic |

#### **Example**

```yaml
spec:
  agentflow:
  - name: analyze_request
    type: Think
    task: implement_feature
  - name: generate_code
    type: Generate
    task: implement_feature
    depends_on: ["analyze_request"]
```

### **Evaluation Configuration**

The `evaluation` section defines quality metrics and validation criteria.

#### **Built-in Metrics**

```yaml
spec:
  evaluation:
    builtin_metrics:                    # OPTIONAL - Quality metrics
      - name: answer_exact_match|answer_passage_match|semantic_f1|rouge_l|bleu|meteor|answer_correctness|faithfulness|context_relevance
        threshold: float                # OPTIONAL (default: 0.7) - Quality threshold
        weight: float                   # OPTIONAL (default: 1.0) - Metric weight
```

#### **Available Metrics**

| Metric | Description | Use Case |
|--------|-------------|----------|
| `answer_exact_match` | Exact text matching | Factual accuracy |
| `answer_passage_match` | Passage-level matching | Content relevance |
| `semantic_f1` | Semantic similarity | Meaning accuracy |
| `rouge_l` | ROUGE-L score | Text generation quality |
| `bleu` | BLEU score | Translation quality |
| `meteor` | METEOR score | Text similarity |
| `answer_correctness` | Overall correctness | General quality |
| `faithfulness` | Faithfulness to source | Information accuracy |
| `context_relevance` | Context relevance | RAG quality |

#### **Example**

```yaml
spec:
  evaluation:
    builtin_metrics:
    - name: answer_exact_match
      threshold: 1.0
    - name: answer_correctness
      threshold: 0.8
      weight: 2.0
```

### **Feature Specifications (BDD Scenarios)**

The `feature_specifications` section defines BDD scenarios for agent testing and optimization.

#### **Structure**

```yaml
spec:
  feature_specifications:               # OPTIONAL - BDD scenarios
    scenarios:                          # OPTIONAL
      - name: string                    # REQUIRED - Scenario name
        description: string             # REQUIRED - Scenario description
        input: {}                       # REQUIRED - Input data
        expected_output: {}             # REQUIRED - Expected output
        validation_criteria: [string]   # OPTIONAL - Validation hints
```

#### **Example**

```yaml
spec:
  feature_specifications:
    scenarios:
    - name: basic_question_answering
      description: The agent should answer basic questions accurately.
      input:
        question: "What is artificial intelligence and how does it work?"
      expected_output:
        answer: "Should include comprehensive explanation of AI concepts"
    - name: creative_content_generation
      description: The agent should generate creative content effectively.
      input:
        question: "Write a short story about a robot learning to paint"
      expected_output:
        answer: "Should include a creative and engaging story"
```

## 🚀 **Advanced Level: Advanced Features**

### **Tools Configuration (Genies Tier)**

The `tools` section enables tool integration for Genies tier agents.

#### **Basic Configuration**

```yaml
spec:
  tools:
    enabled: bool                       # REQUIRED - Enable tool integration
    categories: [string]                # OPTIONAL - Tool categories to include
    specific_tools: [string]            # OPTIONAL - Specific tools to include
```

#### **Available Tool Categories**

| Category | Description | Examples |
|----------|-------------|----------|
| `core` | Essential tools | calculator, file_reader, text_analyzer |
| `development` | Software development | code_formatter, debugger, linter |
| `utilities` | General utilities | date_time, json_processor, data_processor |
| `finance` | Financial tools | financial_calculator, investment_analyzer |
| `healthcare` | Healthcare tools | health_assessment, medical_analyzer |
| `education` | Educational tools | educational_content, quiz_generator |
| `legal` | Legal tools | legal_analyzer, contract_reviewer |
| `marketing` | Marketing tools | marketing_analyzer, campaign_planner |
| `real_estate` | Real estate tools | property_analyzer, market_researcher |
| `retail` | Retail tools | inventory_manager, sales_analyzer |
| `transportation` | Transportation tools | route_optimizer, fleet_manager |
| `energy` | Energy tools | energy_calculator, efficiency_analyzer |
| `agriculture` | Agriculture tools | crop_advisor, weather_analyzer |
| `human_resources` | HR tools | hr_analyzer, recruitment_assistant |
| `hospitality` | Hospitality tools | hospitality_manager, booking_optimizer |
| `manufacturing` | Manufacturing tools | production_planner, quality_inspector |
| `gaming_sports` | Gaming/Sports tools | game_analyzer, performance_tracker |
| `media_entertainment` | Media tools | content_analyzer, trend_predictor |
| `government_public` | Government tools | policy_analyzer, compliance_checker |
| `consulting` | Consulting tools | business_consultant, strategy_advisor |

#### **Example**

```yaml
spec:
  tools:
    enabled: true
    categories:
    - core
    - development
    - utilities
    specific_tools:
    - calculator
    - file_reader
    - text_analyzer
    - web_search
    - date_time
    - code_formatter
```

### **Memory Configuration (Genies Tier)**

The `memory` section configures memory systems for Genies tier agents.

#### **Basic Configuration**

```yaml
spec:
  memory:
    enabled: bool                       # REQUIRED - Enable memory system
    short_term:                         # OPTIONAL - Working memory
      enabled: bool                     # OPTIONAL (default: true)
      max_tokens: int                   # OPTIONAL - Maximum tokens
    long_term:                          # OPTIONAL - Persistent knowledge
      enabled: bool                     # OPTIONAL (default: true)
      storage_type: local               # OPTIONAL - Storage backend
      max_entries: int                  # OPTIONAL - Maximum entries
    episodic:                           # OPTIONAL - Experience tracking
      enabled: bool                     # OPTIONAL (default: true)
      max_episodes: int                 # OPTIONAL - Maximum episodes
```

#### **Example**

```yaml
spec:
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1000
    long_term:
      enabled: true
      storage_type: local
      max_entries: 100
    episodic:
      enabled: true
      max_episodes: 50
```

### **RAG Configuration (Genies Tier)**

The `rag` section configures Retrieval-Augmented Generation for knowledge retrieval.

#### **Basic Configuration**

```yaml
spec:
  rag:
    enabled: bool                       # REQUIRED - Enable RAG
    retriever_type: chroma|qdrant|weaviate|milvus|lancedb  # REQUIRED - Vector store
    config:                             # OPTIONAL - Retrieval configuration
      top_k: int                        # OPTIONAL (default: 5) - Number of results
      chunk_size: int                   # OPTIONAL (default: 512) - Text chunk size
      chunk_overlap: int                # OPTIONAL (default: 50) - Chunk overlap
    vector_store:                       # OPTIONAL - Vector store configuration
      embedding_model: string           # OPTIONAL - Embedding model
      collection_name: string           # OPTIONAL - Collection name
```

#### **Supported Vector Stores**

| Retriever Type | Description | Use Case |
|----------------|-------------|----------|
| `chroma` | ChromaDB vector store | Local development, small datasets |
| `qdrant` | Qdrant vector database | Production, scalable deployments |
| `weaviate` | Weaviate vector database | Enterprise, rich metadata |
| `milvus` | Milvus vector database | High-performance, large-scale |
| `lancedb` | LanceDB vector database | Fast, embedded vector storage |

#### **Example**

```yaml
spec:
  rag:
    enabled: true
    retriever_type: chroma
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: agent_knowledge
```

### **Optimization Configuration**

The `optimization` section configures advanced DSPy-based performance improvement using state-of-the-art optimizers.

#### **Complete Configuration Schema**

```yaml
spec:
  optimization:
    enabled: true                       # OPTIONAL (default: false)
    optimizer:
      name: GEPA|SIMBA|MIPROv2|BootstrapFewShot|BetterTogether|COPRO|KNNFewShot|LabeledFewShot
      params:
        # Common parameters for all optimizers
        metric: string                  # REQUIRED - Evaluation metric
        timeout: 300                    # OPTIONAL - Timeout in seconds
        verbose: false                  # OPTIONAL - Enable detailed logs
        
        # GEPA-specific parameters
        auto: minimal|light|medium|heavy            # GEPA budget control
        reflection_lm: string                       # Reflection model name
        reflection_minibatch_size: 3                # Reflection batch size
        skip_perfect_score: true                    # Skip if perfect
        add_format_failure_as_feedback: true       # Include format errors
        
        # SIMBA-specific parameters  
        bsize: 8                                    # SIMBA batch size
        num_candidates: 5                           # Number of candidates
        max_steps: 10                               # Maximum steps
        
        # BootstrapFewShot parameters
        max_bootstrapped_demos: 8                   # Bootstrap examples
        max_labeled_demos: 16                       # Labeled examples
        max_rounds: 2                               # Optimization rounds
        max_errors: 3                               # Error tolerance
        
        # MIPROv2 parameters
        init_temperature: 1.2                      # Initial temperature
        
    evaluation:
      enabled: true                               # Enable evaluation
      metrics: ["answer_exact_match"]             # Additional metrics
      test_split: 0.2                            # Test data fraction
      cross_validation:
        enabled: false                            # Enable CV
        folds: 5                                  # CV folds
        
    hardware_optimization:
      target_tier: lightweight|standard|production # Hardware tier
      memory_limit_gb: 16                         # Memory limit
      parallel_optimization: false               # Enable parallel
      max_workers: 2                             # Parallel workers
```

#### **DSPy Optimizers**

SuperSpec now supports all major DSPy optimizers with universal tier compatibility:

| Optimizer | Description | Strengths | Time Estimate |
|-----------|-------------|-----------|---------------|
| **🧠 GEPA** | Genetic-Pareto | Complex reasoning, math, reflective optimization | 3-30 min |
| **⚡ SIMBA** | Stochastic Introspective Mini-Batch Ascent | Fast optimization, general tasks | 1-3 min |
| **📝 MIPROv2** | Multi-step Instruction Prompt Optimization | Creative writing, sophisticated prompts | 2-15 min |
| **🔄 BootstrapFewShot** | Bootstrap few-shot examples | Quick optimization, small datasets | 30-60 sec |
| **🤝 BetterTogether** | Ensemble few-shot approach | Document analysis, balanced accuracy | 1-5 min |
| **🤖 COPRO** | Collaborative Prompt Optimization | Legal analysis, structured tasks | 2-8 min |
| **🔍 KNNFewShot** | K-nearest neighbor few-shot learning | Similarity-based, recommendations | 1-2 min |
| **🏷️ LabeledFewShot** | Traditional labeled few-shot | Translation, classification | 30-90 sec |

#### **Quick Start Examples**

**GEPA for Mathematical Reasoning:**
```yaml
  optimization:
    enabled: true
    optimizer:
      name: GEPA
      params:
        metric: advanced_math_feedback
        auto: light
        reflection_lm: qwen3:8b
        reflection_minibatch_size: 3
```

**SIMBA for Fast Optimization:**
```yaml
  optimization:
    enabled: true
    optimizer:
      name: SIMBA
      params:
        metric: answer_exact_match
        bsize: 8
        num_candidates: 5
```

**BootstrapFewShot for Quick Testing:**
```yaml
  optimization:
    enabled: true
    optimizer:
      name: BootstrapFewShot
      params:
        metric: answer_exact_match
        max_bootstrapped_demos: 4
```

#### **Advanced Feedback Metrics**

SuperSpec provides specialized metrics for domain-specific optimization:

| Metric | Use Case | Description |
|--------|----------|-------------|
| `advanced_math_feedback` | Mathematics | Step-by-step reasoning validation |
| `multi_component_enterprise_feedback` | Business | Multi-aspect document analysis |
| `vulnerability_detection_feedback` | Security | Security analysis with remediation |
| `privacy_preservation_feedback` | Privacy | Data privacy compliance |
| `medical_accuracy_feedback` | Healthcare | Medical safety validation |
| `legal_analysis_feedback` | Legal | Legal compliance verification |

#### **Hardware Tier Configuration**

Optimize for different hardware capabilities:

```yaml
  optimization:
    hardware_optimization:
      target_tier: lightweight    # 8GB+ RAM, 2-3 min optimization
      # OR
      target_tier: standard      # 16GB+ RAM, 5-8 min optimization  
      # OR
      target_tier: production    # 32GB+ RAM, 15-30 min optimization
```

#### **Legacy Support**

For backward compatibility, the old optimization format is still supported:

```yaml
  optimization: few_shot_bootstrapping  # Legacy format - automatically converted
```

## 🎯 **Context Engineering Deep Dive**

### **Memory Systems**

SuperSpec provides a comprehensive multi-layer memory system:

```yaml
context:
  memory:
    enabled: true
    systems:
      short_term:
        enabled: true
        type: "conversation_buffer"
        max_tokens: 4000
        
      long_term:
        enabled: true
        type: "vector_database"
        provider: "pinecone"
        collection: "agent_memory"
        
      episodic:
        enabled: true
        type: "event_store"
        persistence: "redis"
        ttl: "30d"
```

#### **Memory Types**

| Type | Purpose | Persistence | Use Case |
|------|---------|-------------|----------|
| **Short-term** | Conversation context | Session | Current interaction |
| **Long-term** | Domain knowledge | Permanent | Factual information |
| **Episodic** | Interaction history | Configurable | Learning patterns |

### **Knowledge Integration**

Seamless integration with multiple knowledge sources:

```yaml
context:
  knowledge:
    sources:
      - name: "company_docs"
        type: "document_store"
        path: "./knowledge/company/"
        embedding_model: "text-embedding-ada-002"
        
      - name: "market_data"
        type: "api_integration"
        provider: "alpha_vantage"
        update_frequency: "1h"
        
      - name: "regulatory_framework"
        type: "structured_data"
        format: "json"
        source: "regulatory_api"
    
    retrieval:
      strategy: "hybrid"
      reranking: true
      max_results: 10
```

#### **Knowledge Sources**

| Type | Description | Example |
|------|-------------|---------|
| **Document Store** | Local file system | Company documents |
| **API Integration** | External APIs | Market data |
| **Structured Data** | Databases | Regulatory info |
| **Vector Database** | Embeddings | Semantic search |

### **Tool Orchestration**

Structured integration of external tools and APIs:

```yaml
context:
  tools:
    enabled: true
    categories:
      data_analysis:
        - name: "pandas"
          version: "2.0.0"
          capabilities: ["data_manipulation", "statistics"]
          
        - name: "matplotlib"
          version: "3.7.0"
          capabilities: ["visualization"]
          
      external_apis:
        - name: "financial_data_api"
          endpoint: "https://api.financial.com"
          authentication: "api_key"
          rate_limit: "1000/hour"
```

## 🔧 **Agent Engineering Deep Dive**

### **Tier-based Architecture**

SuperSpec supports all five tiers with tier-specific configurations. **Note**: Higher-level configurations for protocols, SuperAgents, and Sovereigns tiers are not included in the current version.

#### **Oracle Tier (Basic)**

```yaml
metadata:
  tier: oracle
  
spec:
  capabilities:
    chain_of_thought: true
    template_responses: true
  
  tasks:
    - name: "answer_question"
```

#### **Genie Tier (Intermediate)**

```yaml
metadata:
  tier: genie
  
spec:
  context:
    memory: true
    tools: true
    retrieval: true
  
  reasoning: "react"
  optimization: "mipro"
```

### **Task Definitions**

Define agent capabilities through declarative task specifications:

```yaml
tasks:
  - name: "analyze_financial_data"
    description: "Perform comprehensive financial data analysis"
    inputs:
      - "data_source"
      - "analysis_type"
      - "time_period"
    outputs:
      - "analysis_report"
      - "visualizations"
      - "recommendations"
    validation:
      required_inputs: ["data_source"]
      output_format: "json"
```

### **AgentFlow**

Define the execution flow of your agent:

```yaml
agentflow:
  - name: "data_collection"
    type: "tool_call"
    depends_on: []
    
  - name: "data_processing"
    type: "task_execution"
    depends_on: ["data_collection"]
    
  - name: "analysis_generation"
    type: "llm_reasoning"
    depends_on: ["data_processing"]
    
  - name: "insight_synthesis"
    type: "task_execution"
    depends_on: ["analysis_generation"]
```

## 🎭 **Multi-Agent Orchestration**

### **Orchestra Specification**

Define multi-agent workflows:

```yaml
apiVersion: orchestra/v1
kind: Orchestra
metadata:
  name: research-team
  tier: genie
  
spec:
  agents:
    - name: "researcher"
      role: "information_gathering"
      tier: "genie"
      
    - name: "analyst"
      role: "data_analysis"
      tier: "genie"
      
    - name: "writer"
      role: "report_generation"
      tier: "oracle"
  
  workflow:
    - name: "research_phase"
      agents: ["researcher"]
      type: "parallel"
      
    - name: "analysis_phase"
      agents: ["analyst"]
      depends_on: ["research_phase"]
      
    - name: "writing_phase"
      agents: ["writer"]
      depends_on: ["analysis_phase"]
```

## 🧪 **BDD Integration**

### **Feature Specifications**

Define expected behaviors using BDD scenarios in the `feature_specifications` section:

```yaml
feature_specifications:
  scenarios:
  - name: "financial_analysis_accuracy"
    description: "The agent should provide accurate financial analysis"
    input:
      data_source: "sample_financial_data.csv"
      analysis_type: "trend_analysis"
      time_period: "Q1 2024"
    expected_output:
      analysis_report: "Should include comprehensive financial analysis with insights"
      visualizations: "Should provide relevant charts and graphs"
      recommendations: "Should offer actionable financial recommendations"
      
  - name: "tool_usage_efficiency"
    description: "The agent should use tools efficiently for data processing"
    input:
      data_analysis_request: "Analyze this dataset and create visualizations"
    expected_output:
      processed_data: "Should demonstrate efficient use of pandas and matplotlib"
      analysis_quality: "Should provide accurate statistical analysis"
```

### **Scenario Structure**

Each scenario in `feature_specifications` follows this structure:

```yaml
feature_specifications:
  scenarios:
  - name: string                    # REQUIRED - Unique scenario name
    description: string             # REQUIRED - What the scenario tests
    input: {}                       # REQUIRED - Input data matching task inputs
    expected_output: {}             # REQUIRED - Expected outputs matching task outputs
    validation_criteria: [string]   # OPTIONAL - Additional validation hints
```

### **Evaluation Configuration**

```yaml
evaluation:
  builtin_metrics:
  - name: answer_exact_match
    threshold: 0.8
  - name: answer_correctness
    threshold: 0.9
    weight: 2.0
    
  optimization:
    strategy: few_shot_bootstrapping
    metric: answer_correctness
    metric_threshold: 0.8
```

## 🎯 **Tier-Specific Configurations**

!!! note "Tier Availability"
    
    **Current Version**: This guide covers **Oracles** and **Genies** tiers only. Higher-level configurations for **Sage**, **SuperAgents**, and **Sovereigns** tiers (including advanced protocols, multi-agent orchestration, and enterprise features) are not included in the current version.

### **Oracles Tier (Basic)**

Oracles tier agents focus on fundamental capabilities:

```yaml
metadata:
  level: oracles

spec:
  # Basic LLM configuration
  language_model:
    location: local
    provider: ollama
    model: llama3.2:1b
    
  # Simple persona
  persona:
    role: "Assistant"
    goal: "Help with basic tasks"
    
  # Single task
  tasks:
  - name: answer_question
    instruction: "Answer questions clearly and accurately"
    inputs:
    - name: question
      type: str
      description: "The question to answer"
      required: true
    outputs:
    - name: answer
      type: str
      description: "The answer to the question"
      
  # Simple flow
  agentflow:
  - name: generate_answer
    type: Generate
    task: answer_question
    
  # Basic evaluation
  evaluation:
    builtin_metrics:
    - name: answer_exact_match
      threshold: 1.0
```

### **Genies Tier (Advanced)**

Genies tier agents include advanced techniques:

```yaml
metadata:
  level: genies

spec:
  # Advanced LLM configuration
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    temperature: 0.7
    max_tokens: 2048
    
  # Rich persona
  persona:
    name: "AdvancedBot"
    role: "Advanced Assistant"
    goal: "Provide comprehensive assistance with tools and memory"
    traits:
    - helpful
    - knowledgeable
    - precise
    
  # Multiple tasks
  tasks:
  - name: creative_writing
    instruction: "Generate creative content"
    inputs:
    - name: writing_request
      type: str
      description: "Creative writing request"
      required: true
    outputs:
    - name: creative_content
      type: str
      description: "Creative content"
      
  # Complex flow
  agentflow:
  - name: analyze_request
    type: Think
    task: creative_writing
  - name: generate_content
    type: Generate
    task: creative_writing
    depends_on: ["analyze_request"]
    
  # Advanced techniques
  tools:
    enabled: true
    categories:
    - core
    - utilities
    
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1000
    long_term:
      enabled: true
      storage_type: local
      max_entries: 100
      
  rag:
    enabled: true
    retriever_type: chroma
    config:
      top_k: 5
      chunk_size: 512
      
  # Comprehensive evaluation
  evaluation:
    builtin_metrics:
    - name: response_quality
      threshold: 0.8
    - name: creativity_score
      threshold: 0.7
```

## 🚀 **Best Practices**

### **1. Start Simple**

Begin with Oracle tier for simple use cases:

```yaml
# Simple FAQ bot
apiVersion: agent/v1
kind: Agent
metadata:
  name: faq-bot
  tier: oracle
spec:
  tasks:
    - name: "answer_faq"
      template: "Answer this FAQ: {question}"
```

### **2. Progressive Enhancement**

Upgrade to Genie when you need tools and memory:

```yaml
# Enhanced customer service
apiVersion: agent/v1
kind: Agent
metadata:
  name: customer-service
  tier: genie
spec:
  context:
    memory: true
    tools: true
    retrieval: true
  tasks:
    - name: "handle_inquiry"
      description: "Handle customer inquiries"
```

### **3. Production Considerations**

For Protocol tier and above (commercial version):

```yaml
# Production-ready agent
apiVersion: agent/v1
kind: Agent
metadata:
  name: production-agent
  tier: protocol
spec:
  context:
    memory: true
    tools: true
    protocols: ["mcp", "a2a"]
  monitoring:
    tracing: true
    observability: true
    alerting: true
```

### **4. Validation and Testing**

Always include BDD feature specifications:

```yaml
feature_specifications:
  scenarios:
  - name: "core_functionality"
    description: "The agent should perform core tasks correctly"
    input:
      question: "What is the capital of France?"
    expected_output:
      answer: "Should provide accurate information about Paris"
```

## 🔧 **Development Workflow**

### **1. Create SuperSpec Playbook**

```bash
# Generate a new agent specification
super spec generate genies my-agent \
  --namespace my-domain \
  --tools \
  --memory \
  --rag

# Or create manually
vim agents/my-agent/playbook/my-agent_playbook.yaml
```

### **2. Validate Specification**

```bash
# Validate the SuperSpec specification
super spec validate my-agent_playbook.yaml
```

### **3. Compile Agent**

```bash
# Compile SuperSpec to executable pipeline
super agent compile my-agent
```

### **4. Test and Optimize**

```bash
# Run BDD evaluation
super agent evaluate my-agent

# Optimize performance
super agent optimize my-agent

# Re-evaluate
super agent evaluate my-agent
```

### **5. Deploy**

```bash
# Run the agent
super agent run my-agent --goal "Your task here"
```

## 🎯 **Best Practices**

### **DO's**

1. **Start Simple**: Begin with basic Oracles tier configuration
2. **Use Descriptive Names**: Make task and field names self-documenting
3. **Validate Early**: Use `super spec validate` to catch errors
4. **Version Control**: Commit SuperSpec files to Git for tracking
5. **Test Thoroughly**: Write comprehensive BDD scenarios
6. **Optimize Iteratively**: Use evaluation results to guide optimization

### **DON'Ts**

1. **Don't Over-Configure**: Start with minimal configuration
2. **Don't Skip Validation**: Always validate before compilation
3. **Don't Ignore Evaluation**: Use BDD scenarios for quality assurance
4. **Don't Hardcode Secrets**: Use environment variables for API keys
5. **Don't Mix Tiers**: Stick to tier-appropriate features

## 🎉 **Conclusion**

SuperSpec provides a **declarative, strongly-typed specification language** for AI agents that:

- 🎯 **Strikes the right balance** of context for optimal performance
- 🔄 **Integrates seamlessly** with DSPy for validation and optimization
- 📋 **Follows Kubernetes patterns** for declarative configuration
- 🧪 **Supports BDD scenarios** for comprehensive testing
- 🚀 **Enables version control** and team collaboration

Start using SuperSpec today to build **reliable, maintainable, and performant AI agents**!

---

💡 **Pro Tip**: Begin with Oracles tier configurations to understand the basics, then graduate to Genies tier for advanced techniques like tools, memory, and RAG. Always validate your SuperSpec specifications before compilation!

!!! info "Advanced Tiers"
    
    For **Sage**, **SuperAgents**, and **Sovereigns** tiers with advanced protocols, multi-agent orchestration, and enterprise features, please refer to the commercial version of SuperOptiX. 

## 🔧 **DSL Examples**

### **Basic Oracles Tier Agent**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Simple Assistant
  id: simple-assistant
  namespace: software
  version: "1.0.0"
  level: oracles
  stage: alpha
  agent_type: Autonomous
  description: A basic assistant for simple tasks
  tags: ["software", "oracles", "basic"]
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.2:1b
    api_base: http://localhost:11434
    temperature: 0.0
    max_tokens: 2048
    cache: true
  persona:
    name: SimpleBot
    role: Assistant
    goal: Provide helpful assistance for basic tasks
    traits:
    - helpful
    - concise
    - accurate
    communication_preferences:
      style: professional
      tone: friendly
      verbosity: concise
  tasks:
  - name: answer_question
    description: Answer user questions clearly and accurately
    instruction: You are a helpful assistant. Answer the user's question clearly and accurately.
    inputs:
    - name: question
      type: str
      description: The question to answer
      required: true
    outputs:
    - name: answer
      type: str
      description: The answer to the question
  agentflow:
  - name: generate_answer
    type: Think
    task: answer_question
    config:
      reasoning_depth: 2
  evaluation:
    builtin_metrics:
    - name: answer_correctness
      threshold: 0.8
  optimization:
    strategy: few_shot_bootstrapping
    metric: answer_correctness
    few_shot_bootstrapping_config:
      max_bootstrapped_demos: 4
      max_rounds: 1
  feature_specifications:
    scenarios:
    - name: basic_question_answering
      description: The agent should answer basic questions accurately
      input:
        question: "What is the capital of France?"
      expected_output:
        answer: "Should provide accurate information about Paris"
    - name: factual_inquiry
      description: The agent should handle factual inquiries
      input:
        question: "How many planets are in our solar system?"
      expected_output:
        answer: "Should provide accurate count of planets"
```

### **Advanced Genies Tier Agent**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Advanced Data Analyst
  id: advanced-data-analyst
  namespace: finance
  version: "1.0.0"
  level: genies
  stage: alpha
  agent_type: Autonomous
  description: Advanced data analysis agent with tools and memory
  tags: ["finance", "genies", "data-analysis", "advanced"]
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
    temperature: 0.7
    max_tokens: 2048
    cache: true
  persona:
    name: DataBot
    role: Data Analyst
    goal: Perform comprehensive data analysis and provide insights
    traits:
    - analytical
    - detail-oriented
    - precise
    - helpful
    expertise_areas:
    - data analysis
    - statistical modeling
    - financial analysis
    - visualization
    communication_preferences:
      style: technical
      tone: professional
      verbosity: detailed
  tasks:
  - name: analyze_data
    description: Perform comprehensive data analysis
    instruction: You are a Data Analyst. Analyze the provided data and generate insights, visualizations, and recommendations.
    inputs:
    - name: data_source
      type: str
      description: Source of data to analyze (file path, URL, or data description)
      required: true
    - name: analysis_type
      type: str
      description: Type of analysis to perform (descriptive, predictive, exploratory)
      required: true
    - name: time_period
      type: str
      description: Time period for analysis
      required: false
    outputs:
    - name: analysis_report
      type: str
      description: Comprehensive analysis report
    - name: visualizations
      type: list[str]
      description: Generated data visualizations
    - name: recommendations
      type: str
      description: Actionable recommendations based on analysis
  - name: create_visualization
    description: Create data visualizations
    instruction: Create appropriate visualizations for the given data and analysis requirements.
    inputs:
    - name: data
      type: dict[str,Any]
      description: Data to visualize
      required: true
    - name: chart_type
      type: str
      description: Type of chart to create
      required: true
    outputs:
    - name: visualization
      type: str
      description: Generated visualization
  agentflow:
  - name: load_data
    type: ActWithTools
    task: analyze_data
  - name: perform_analysis
    type: Think
    task: analyze_data
    depends_on: ["load_data"]
  - name: generate_visualizations
    type: Generate
    task: create_visualization
    depends_on: ["perform_analysis"]
  - name: synthesize_results
    type: Generate
    task: analyze_data
    depends_on: ["generate_visualizations"]
  react_config:
    max_iters: 5
    max_tool_calls: 3
    tool_selection_strategy: automatic
    reasoning_style: step_by_step
    error_handling: retry
    enable_tracing: true
  tools:
    enabled: true
    categories:
    - core
    - development
    - utilities
    specific_tools:
    - calculator
    - file_reader
    - text_analyzer
    - web_search
    - date_time
    - code_formatter
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 2000
    long_term:
      enabled: true
      storage_type: local
      max_entries: 500
    episodic:
      enabled: true
      max_episodes: 100
  retrieval:
    enabled: true
    retriever_type: chroma
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
    vector_store:
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      collection_name: data_analysis_knowledge
  evaluation:
    builtin_metrics:
    - name: answer_correctness
      threshold: 0.8
    - name: analysis_quality
      threshold: 0.7
    - name: visualization_quality
      threshold: 0.6
  feature_specifications:
    scenarios:
    - name: financial_data_analysis
      description: The agent should analyze financial data effectively
      input:
        data_source: "sample_financial_data.csv"
        analysis_type: "descriptive"
        time_period: "Q1 2024"
      expected_output:
        analysis_report: "Should include comprehensive financial analysis"
        visualizations: "Should provide relevant charts and graphs"
        recommendations: "Should offer actionable financial recommendations"
    - name: statistical_analysis
      description: The agent should perform statistical analysis
      input:
        data_source: "sales_data.json"
        analysis_type: "predictive"
      expected_output:
        analysis_report: "Should include statistical insights and predictions"
        recommendations: "Should provide data-driven recommendations"
  optimization:
    strategy: few_shot_bootstrapping
    metric: analysis_quality
    metric_threshold: 0.7
    few_shot_bootstrapping_config:
      max_bootstrapped_demos: 4
      max_rounds: 1
```

### **Healthcare Agent Example**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Healthcare Assistant
  id: healthcare-assistant
  namespace: healthcare
  version: "1.0.0"
  level: genies
  stage: alpha
  agent_type: Supervised
  description: Healthcare assistant for patient information and medical guidance
  tags: ["healthcare", "genies", "medical", "patient-care"]
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
    temperature: 0.3
    max_tokens: 2048
  persona:
    name: HealthBot
    role: Healthcare Assistant
    goal: Provide accurate healthcare information and patient support
    traits:
    - knowledgeable
    - empathetic
    - precise
    - professional
    expertise_areas:
    - general health
    - medical terminology
    - patient care
    - health education
    communication_preferences:
      style: professional
      tone: supportive
      verbosity: detailed
  tasks:
  - name: health_assessment
    description: Assess health information and provide guidance
    instruction: You are a Healthcare Assistant. Assess the provided health information and provide appropriate guidance while maintaining patient privacy and safety.
    inputs:
    - name: health_query
      type: str
      description: Health-related question or concern
      required: true
    - name: patient_context
      type: dict[str,Any]
      description: Relevant patient context (age, symptoms, etc.)
      required: false
    outputs:
    - name: health_guidance
      type: str
      description: Appropriate health guidance and recommendations
    - name: urgency_level
      type: str
      description: Assessment of urgency (low, medium, high, emergency)
    - name: next_steps
      type: list[str]
      description: Recommended next steps
  agentflow:
  - name: assess_query
    type: Think
    task: health_assessment
  - name: provide_guidance
    type: Generate
    task: health_assessment
    depends_on: ["assess_query"]
  tools:
    enabled: true
    categories:
    - core
    - healthcare
    specific_tools:
    - calculator
    - text_analyzer
    - date_time
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1000
    long_term:
      enabled: true
      storage_type: local
      max_entries: 100
  evaluation:
    builtin_metrics:
    - name: answer_correctness
      threshold: 0.9
    - name: safety_compliance
      threshold: 1.0
  feature_specifications:
    scenarios:
    - name: general_health_inquiry
      description: The agent should handle general health inquiries appropriately
      input:
        health_query: "What are the symptoms of a common cold?"
      expected_output:
        health_guidance: "Should provide accurate information about cold symptoms"
        urgency_level: "low"
        next_steps: "Should suggest appropriate self-care measures"
    - name: emergency_assessment
      description: The agent should identify emergency situations
      input:
        health_query: "I'm experiencing chest pain and shortness of breath"
      expected_output:
        urgency_level: "emergency"
        next_steps: "Should recommend immediate medical attention"
```

### **Education Agent Example**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Educational Tutor
  id: educational-tutor
  namespace: education
  version: "1.0.0"
  level: genies
  stage: alpha
  agent_type: Interactive
  description: Interactive educational tutor for various subjects
  tags: ["education", "genies", "tutoring", "interactive"]
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
    temperature: 0.7
    max_tokens: 2048
  persona:
    name: TutorBot
    role: Educational Tutor
    goal: Provide engaging and effective educational support
    traits:
    - patient
    - encouraging
    - knowledgeable
    - adaptive
    expertise_areas:
    - mathematics
    - science
    - language arts
    - history
    - problem solving
    communication_preferences:
      style: conversational
      tone: encouraging
      verbosity: adaptive
  tasks:
  - name: teach_concept
    description: Teach a specific concept or topic
    instruction: You are an Educational Tutor. Teach the requested concept in an engaging and understandable way, adapting to the student's level.
    inputs:
    - name: subject
      type: str
      description: Subject area (math, science, history, etc.)
      required: true
    - name: topic
      type: str
      description: Specific topic to teach
      required: true
    - name: student_level
      type: str
      description: Student's current level (beginner, intermediate, advanced)
      required: true
    outputs:
    - name: explanation
      type: str
      description: Clear explanation of the concept
    - name: examples
      type: list[str]
      description: Relevant examples and practice problems
    - name: assessment
      type: str
      description: Assessment of student understanding
  - name: answer_question
    description: Answer student questions
    instruction: Answer the student's question clearly and helpfully, providing additional context when needed.
    inputs:
    - name: question
      type: str
      description: Student's question
      required: true
    outputs:
    - name: answer
      type: str
      description: Clear and helpful answer
  agentflow:
  - name: assess_student_needs
    type: Think
    task: teach_concept
  - name: provide_explanation
    type: Generate
    task: teach_concept
    depends_on: ["assess_student_needs"]
  - name: create_examples
    type: Generate
    task: teach_concept
    depends_on: ["provide_explanation"]
  tools:
    enabled: true
    categories:
    - core
    - education
    - utilities
    specific_tools:
    - calculator
    - text_analyzer
    - date_time
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1500
    long_term:
      enabled: true
      storage_type: local
      max_entries: 200
  evaluation:
    builtin_metrics:
    - name: explanation_clarity
      threshold: 0.8
    - name: educational_value
      threshold: 0.8
  feature_specifications:
    scenarios:
    - name: math_teaching
      description: The agent should teach mathematical concepts effectively
      input:
        subject: "mathematics"
        topic: "fractions"
        student_level: "beginner"
      expected_output:
        explanation: "Should provide clear explanation of fractions"
        examples: "Should include relevant practice problems"
    - name: science_explanation
      description: The agent should explain scientific concepts
      input:
        subject: "science"
        topic: "photosynthesis"
        student_level: "intermediate"
      expected_output:
        explanation: "Should explain photosynthesis clearly"
        examples: "Should provide real-world examples"
```

### **Finance Agent Example**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Financial Advisor
  id: financial-advisor
  namespace: finance
  version: "1.0.0"
  level: genies
  stage: alpha
  agent_type: Supervised
  description: Financial advisor for investment and financial planning
  tags: ["finance", "genies", "investment", "planning"]
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
    temperature: 0.5
    max_tokens: 2048
  persona:
    name: FinanceBot
    role: Financial Advisor
    goal: Provide sound financial advice and investment guidance
    traits:
    - analytical
    - conservative
    - trustworthy
    - knowledgeable
    expertise_areas:
    - investment planning
    - risk assessment
    - financial analysis
    - retirement planning
    communication_preferences:
      style: professional
      tone: authoritative
      verbosity: detailed
  tasks:
  - name: financial_analysis
    description: Analyze financial data and provide insights
    instruction: You are a Financial Advisor. Analyze the provided financial information and provide sound advice and recommendations.
    inputs:
    - name: financial_data
      type: dict[str,Any]
      description: Financial data to analyze
      required: true
    - name: analysis_type
      type: str
      description: Type of analysis (investment, retirement, budgeting)
      required: true
    outputs:
    - name: analysis_report
      type: str
      description: Comprehensive financial analysis
    - name: recommendations
      type: list[str]
      description: Financial recommendations
    - name: risk_assessment
      type: str
      description: Risk assessment and considerations
  agentflow:
  - name: analyze_data
    type: Think
    task: financial_analysis
  - name: generate_recommendations
    type: Generate
    task: financial_analysis
    depends_on: ["analyze_data"]
  tools:
    enabled: true
    categories:
    - core
    - finance
    - utilities
    specific_tools:
    - calculator
    - financial_calculator
    - text_analyzer
    - date_time
  memory:
    enabled: true
    short_term:
      enabled: true
      max_tokens: 1000
    long_term:
      enabled: true
      storage_type: local
      max_entries: 100
  evaluation:
    builtin_metrics:
    - name: advice_quality
      threshold: 0.8
    - name: risk_awareness
      threshold: 0.9
  feature_specifications:
    scenarios:
    - name: investment_analysis
      description: The agent should provide sound investment advice
      input:
        financial_data: {"income": 75000, "savings": 50000, "age": 35}
        analysis_type: "investment"
      expected_output:
        analysis_report: "Should provide comprehensive investment analysis"
        recommendations: "Should suggest appropriate investment strategies"
        risk_assessment: "Should include risk considerations"
```

## 🎯 **Configuration Examples**

### **Memory Configuration**

```yaml
memory:
  enabled: true
  short_term:
    enabled: true
    max_tokens: 2000
    window_size: 10
  long_term:
    enabled: true
    storage_type: local
    max_entries: 500
    persistence: true
  episodic:
    enabled: true
    max_episodes: 100
    episode_retention: 30
  context_manager:
    enabled: true
    max_context_length: 4000
    context_strategy: sliding_window
```

### **Tool Configuration**

```yaml
tools:
  enabled: true
  categories:
  - core
  - development
  - utilities
  - finance
  specific_tools:
  - calculator
  - file_reader
  - text_analyzer
  - web_search
  - date_time
  - code_formatter
  - financial_calculator
```

### **RAG Configuration**

```yaml
retrieval:
  enabled: true
  retriever_type: chroma
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50
  vector_store:
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    collection_name: agent_knowledge
```

### **Evaluation Configuration**

```yaml
evaluation:
  builtin_metrics:
  - name: answer_correctness
    threshold: 0.8
    weight: 2.0
  - name: response_quality
    threshold: 0.7
  - name: safety_compliance
    threshold: 1.0
    weight: 3.0
```

### **Optimization Configuration**

```yaml
optimization:
  strategy: few_shot_bootstrapping
  metric: answer_correctness
  metric_threshold: 0.8
  few_shot_bootstrapping_config:
    max_bootstrapped_demos: 4
    max_rounds: 1
```

## 🚀 **Best Practices for Examples**

### **1. Use Descriptive Names and IDs**

```yaml
metadata:
  name: "Customer Support Specialist"  # Clear, descriptive name
  id: "customer-support-specialist"    # URL-friendly identifier
  description: "Handles customer inquiries and provides support"
```

### **2. Define Clear Task Instructions**

```yaml
tasks:
- name: handle_inquiry
  instruction: |
    You are a Customer Support Specialist. Your goal is to help customers 
    resolve their issues efficiently and professionally. Always be polite, 
    patient, and solution-oriented.
```

### **3. Use Appropriate AgentFlow**

```yaml
agentflow:
- name: understand_issue
  type: Think
  task: handle_inquiry
- name: provide_solution
  type: Generate
  task: handle_inquiry
  depends_on: ["understand_issue"]
```

### **4. Include Comprehensive BDD Scenarios**

```yaml
feature_specifications:
  scenarios:
  - name: basic_inquiry_handling
    description: The agent should handle basic customer inquiries
    input:
      inquiry: "I can't log into my account"
    expected_output:
      response: "Should provide helpful troubleshooting steps"
  - name: complex_issue_resolution
    description: The agent should handle complex issues
    input:
      inquiry: "My order was delivered to the wrong address"
    expected_output:
      response: "Should provide escalation and resolution steps"
```

### **5. Configure Tier-Appropriate Features**

```yaml
# For Oracles tier - keep it simple
metadata:
  level: oracles
spec:
  # No memory, tools, or RAG configuration
  tasks: [...]

# For Genies tier - use advanced features
metadata:
  level: genies
spec:
  memory:
    enabled: true
  tools:
    enabled: true
  retrieval:
    enabled: true
```

---

💡 **Pro Tip**: Use the `super spec generate` command to create templates based on these examples, then customize them for your specific use case! 