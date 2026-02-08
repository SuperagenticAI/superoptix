# ⚙️ SuperSpec Configuration

<div style="text-align: center; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, var(--md-primary-fg-color--light) 0%, var(--md-accent-fg-color--light) 50%, var(--md-primary-fg-color--lighter) 100%); border-radius: var(--border-radius); color: var(--md-default-fg-color); border: 2px solid var(--md-primary-fg-color--light);">
    <h2 style="color: var(--md-default-fg-color);">⚙️ SuperSpec Configuration</h2>
    <p style="font-size: 1.1rem; margin-bottom: 1rem; color: var(--md-default-fg-color);">
        <strong>Complete configuration reference for SuperSpec DSL</strong><br>
        Based on the actual SuperOptiX library implementation
    </p>
</div>

## 📋 **Overview**

SuperSpec configuration covers all aspects of agent specification, from basic metadata to advanced features like memory, tools, and RAG. This page provides detailed configuration options based on the actual library implementation.

## 🎯 **Configuration Sections**

### **1. Metadata Configuration**

The `metadata` section defines the agent's identity and basic properties.

```yaml
metadata:
  name: string                    # REQUIRED - Human-readable agent name
  id: string                      # REQUIRED - Unique identifier (a-z, 0-9, -, _)
  version: string                 # REQUIRED - Semantic versioning (e.g., "1.0.0")
  namespace: string               # OPTIONAL - Logical grouping namespace
  level: oracles|genies          # OPTIONAL - Agent tier level (default: oracles)
  stage: alpha|beta|stable       # OPTIONAL - Development stage (default: alpha)
  agent_type: Autonomous|Supervised|Interactive|Reactive|Deliberative|Hybrid  # OPTIONAL
  description: string             # OPTIONAL - Brief agent description
  tags: [string]                  # OPTIONAL - Categorization tags
  created_at: string              # OPTIONAL - ISO timestamp of creation
  updated_at: string              # OPTIONAL - ISO timestamp of last update
```

#### **Valid Namespaces**

```python
VALID_NAMESPACES = [
    "software", "education", "healthcare", "finance", "marketing",
    "legal", "consulting", "retail", "manufacturing", "transportation", 
    "agriculture_food", "energy_utilities", "gaming_sports",
    "government_public", "hospitality_tourism", "human_resources",
    "media_entertainment", "real_estate", "testing"
]
```

#### **Valid Agent Types**

```python
VALID_AGENT_TYPES = [
    "Autonomous", "Supervised", "Interactive", "Reactive", "Deliberative", "Hybrid"
]
```

### **2. Language Model Configuration**

The `language_model` section configures the underlying LLM.

```yaml
spec:
  language_model:
    location: local|self-hosted|cloud  # REQUIRED - Model hosting location
    provider: string                   # REQUIRED - Model provider
    model: string                      # REQUIRED - Specific model identifier
    model_type: chat|text|completion  # OPTIONAL - Model endpoint type (default: chat)
    temperature: float                 # OPTIONAL - Randomness control (0.0-2.0, default: 0.0)
    max_tokens: int                    # OPTIONAL - Max output length (1-100000, default: 4000)
    top_p: float                       # OPTIONAL - Nucleus sampling (0.0-1.0, default: 1.0)
    frequency_penalty: float           # OPTIONAL - Frequency penalty (-2.0-2.0, default: 0.0)
    presence_penalty: float            # OPTIONAL - Presence penalty (-2.0-2.0, default: 0.0)
    cache: bool                        # OPTIONAL - Enable LLM call caching (default: true)
    cache_in_memory: bool              # OPTIONAL - Cache in memory vs disk (default: true)
    num_retries: int                   # OPTIONAL - API failure retry attempts (0-10, default: 3)
    modalities: [text|image|audio|video]  # OPTIONAL - Supported modalities (default: [text])
    api_key: string                    # OPTIONAL - API key for cloud providers
    api_base: string                   # OPTIONAL - Custom API base URL
    api_version: string                # OPTIONAL - API version (Azure)
```

#### **Valid Providers by Location**

| Location | Supported Providers |
|----------|-------------------|
| **local** | `ollama`, `vllm`, `sglang`, `mlx`, `lm_studio` |
| **self-hosted** | `custom` |
| **cloud** | `openai`, `anthropic`, `google`, `azure`, `mistral`, `cohere`, `groq`, `deepseek` |

### **3. Persona Configuration**

The `persona` section defines the agent's personality and behavior.

```yaml
spec:
  persona:
    name: string                        # OPTIONAL - Agent's name
    role: string                        # REQUIRED - Agent's role
    goal: string                        # OPTIONAL - Primary objective
    traits: [string]                    # OPTIONAL - Personality characteristics
    expertise_areas: [string]           # OPTIONAL - Knowledge domains
    communication_preferences:          # OPTIONAL
      style: formal|casual|technical|conversational  # OPTIONAL (default: formal)
      tone: professional|friendly|authoritative|supportive  # OPTIONAL (default: professional)
      verbosity: concise|detailed|adaptive  # OPTIONAL (default: concise)
```

### **4. Tasks Configuration**

The `tasks` section defines the agent's capabilities.

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
      schema:                           # OPTIONAL - Task schema configuration
        style: chain_of_thought|direct|structured  # OPTIONAL
        reasoning_traces: bool          # OPTIONAL
      reasoning_steps: [string]         # OPTIONAL - Reasoning step definitions
      training_examples: [dict]         # OPTIONAL - Training examples
      assertions: [dict]                # OPTIONAL - Task assertions
```

### **5. AgentFlow Configuration**

The `agentflow` section defines the execution flow.

```yaml
spec:
  agentflow:                            # OPTIONAL - Execution flow
    - name: string                      # REQUIRED - Step name
      type: string                      # REQUIRED - Step type
      task: string                      # REQUIRED - Task name to execute
      depends_on: [string]              # OPTIONAL - Dependencies
      config: dict                      # OPTIONAL - Step configuration
      retry_policy: dict                # OPTIONAL - Retry policy
```

#### **Valid AgentFlow Types by Tier**

| Tier | Allowed Types |
|------|---------------|
| **oracles** | `Generate`, `Think`, `Compare`, `Route` |
| **genies** | `Generate`, `Think`, `ActWithTools`, `Search`, `Compare`, `Route` |

### **6. Memory Configuration (Genies Only)**

The `memory` section configures memory systems for Genies tier agents.

```yaml
spec:
  memory:
    enabled: bool                       # REQUIRED - Enable memory system
    short_term:                         # OPTIONAL - Working memory
      enabled: bool                     # OPTIONAL (default: true)
      max_tokens: int                   # OPTIONAL - Maximum tokens
      window_size: int                  # OPTIONAL - Conversation window size
    long_term:                          # OPTIONAL - Persistent knowledge
      enabled: bool                     # OPTIONAL (default: true)
      storage_type: local               # OPTIONAL - Storage backend
      max_entries: int                  # OPTIONAL - Maximum entries
      persistence: bool                 # OPTIONAL - Enable persistence
    episodic:                           # OPTIONAL - Experience tracking
      enabled: bool                     # OPTIONAL (default: true)
      max_episodes: int                 # OPTIONAL - Maximum episodes
      episode_retention: int            # OPTIONAL - Episode retention days
    context_manager:                    # OPTIONAL - Context management
      enabled: bool                     # OPTIONAL (default: true)
      max_context_length: int           # OPTIONAL - Maximum context length
      context_strategy: sliding_window  # OPTIONAL - Context strategy
```

#### **Valid Memory Backends**

```python
VALID_MEMORY_BACKENDS = ["file", "sqlite", "redis"]
```

### **7. Tools Configuration (Genies Only)**

The `tools` section enables tool integration for Genies tier agents.

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

### **8. RAG Configuration (Genies Only)**

The `retrieval` section configures Retrieval-Augmented Generation.

```yaml
spec:
  retrieval:
    enabled: bool                       # REQUIRED - Enable RAG
    retriever_type: string              # REQUIRED - Vector store type
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

### **9. Evaluation Configuration**

The `evaluation` section defines quality metrics and validation criteria.

```yaml
spec:
  evaluation:
    builtin_metrics:                    # OPTIONAL - Quality metrics
      - name: string                    # REQUIRED - Metric name
        threshold: float                # OPTIONAL (default: 0.7) - Quality threshold
        weight: float                   # OPTIONAL (default: 1.0) - Metric weight
```

#### **Available Built-in Metrics**

```python
VALID_BUILTIN_METRICS = [
    "answer_exact_match", "answer_passage_match", "semantic_f1", 
    "rouge_l", "bleu", "meteor", "answer_correctness", 
    "faithfulness", "context_relevance"
]
```

### **10. Feature Specifications (BDD Scenarios)**

The `feature_specifications` section defines BDD scenarios for testing.

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

### **11. Optimization Configuration**

The `optimization` section configures DSPy-based performance improvement.

```yaml
spec:
  optimization:
    strategy: string                    # OPTIONAL - Optimization strategy
    metric: string                      # REQUIRED - Metric to optimize for
    metric_threshold: float             # OPTIONAL - Quality threshold
    few_shot_bootstrapping_config:      # OPTIONAL - Bootstrap configuration
      max_bootstrapped_demos: int       # OPTIONAL (default: 4) - Max demos
      max_rounds: int                   # OPTIONAL (default: 1) - Optimization rounds
```

#### **Available Optimization Strategies**

```python
VALID_OPTIMIZATION_STRATEGIES = ["few_shot_bootstrapping"]  # Current version only
```

### **12. Runtime Configuration**

The `runtime` section configures runtime behavior.

```yaml
spec:
  runtime:
    caching:                            # OPTIONAL - Caching configuration
      enabled: bool                     # OPTIONAL (default: true)
      backend: memory|disk|redis        # OPTIONAL - Cache backend
      ttl: int                          # OPTIONAL - Time to live in seconds
    monitoring:                         # OPTIONAL - Monitoring configuration
      log_level: debug|info|warn|error  # OPTIONAL - Log level
      metrics_collection: bool          # OPTIONAL - Enable metrics collection
```

### **13. DSPy Optimizer/Teleprompter Support**

SuperSpec now supports configuring any DSPy optimizer or teleprompter directly in your agent spec. This enables advanced optimization strategies, including GEPA, SIMBA, COPRO, KNNFewShot, BetterTogether, and more.

**How to use:**

Add an `optimizer` section under `spec.optimization`:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA  # or SIMBA, COPRO, KNNFewShot, BetterTogether, etc.
      params:
        metric: semantic_f1
        max_iters: 10
        feedback_fn: my_custom_feedback
    # ... other optimization config ...
```

- `name`: The DSPy optimizer/teleprompter class name (case-sensitive, e.g., GEPA, SIMBA, COPRO, KNNFewShot, BetterTogether, BootstrapFewShot, LabeledFewShot, etc.)
- `params`: Dictionary of parameters to pass to the optimizer/teleprompter constructor. Keys/values depend on the optimizer.

**Examples:**

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: semantic_f1
        max_iters: 10
        feedback_fn: my_custom_feedback
```

```yaml
spec:
  optimization:
    optimizer:
      name: KNNFewShot
      params:
        k: 8
        retriever: my_knn_retriever
```

```yaml
spec:
  optimization:
    optimizer:
      name: BetterTogether
      params:
        prompt_optimizer: BootstrapFewShot
        weight_optimizer: BootstrapFinetune
```

**How it works:**
- The pipeline generator will dynamically instantiate the specified optimizer/teleprompter with the provided parameters.
- All DSPy optimizers/teleprompters in your DSPy version are supported.
- If not specified, the default optimizer for the agent tier is used (LabeledFewShot for Oracles, BootstrapFewShot for Genies).

**See also:**
- [DSPy Optimizer Reference](https://github.com/stanford-oval/dspy/tree/main/dspy/teleprompt)
- [GEPA Optimizer](https://github.com/stanford-oval/gepa)

## 🎯 **Tier-Specific Configuration**

### **Oracles Tier Configuration**

```yaml
metadata:
  level: oracles

spec:
  # Basic LLM configuration
  language_model:
    location: local
    provider: ollama
    model: llama3.2:1b
    temperature: 0.0
    max_tokens: 2048
    
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
    type: Think
    task: answer_question
    
  # Basic evaluation
  evaluation:
    builtin_metrics:
    - name: answer_correctness
      threshold: 0.8
```

### **Genies Tier Configuration**

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
  - name: solve_problem
    instruction: "Solve complex problems using tools and reasoning"
    inputs:
    - name: problem
      type: str
      description: "Problem to solve"
      required: true
    outputs:
    - name: solution
      type: str
      description: "Problem solution"
      
  # Complex flow
  agentflow:
  - name: analyze_problem
    type: Think
    task: solve_problem
  - name: use_tools
    type: ActWithTools
    task: solve_problem
    depends_on: ["analyze_problem"]
  - name: synthesize_solution
    type: Generate
    task: solve_problem
    depends_on: ["use_tools"]
    
  # Advanced features
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
      
  retrieval:
    enabled: true
    retriever_type: chroma
    config:
      top_k: 5
      chunk_size: 512
      
  # Comprehensive evaluation
  evaluation:
    builtin_metrics:
    - name: solution_quality
      threshold: 0.8
    - name: tool_usage_efficiency
      threshold: 0.7
```

## 🚀 **Configuration Best Practices**

### **1. Use Proper Validation**

```bash
# Validate your configuration
super spec validate my-agent_playbook.yaml

# Check for tier-specific issues
super spec validate my-agent_playbook.yaml --verbose
```

### **2. Follow Tier Constraints**

```yaml
# Correct - Oracles tier without advanced features
metadata:
  level: oracles
spec:
  # No memory, tools, or RAG configuration
  tasks: [...]

# Correct - Genies tier with advanced features
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

### **3. Use Descriptive Configuration**

```yaml
metadata:
  name: "Financial Data Analyst"  # Clear, descriptive name
  description: "Specialized agent for financial data analysis and reporting"
  tags: ["finance", "data-analysis", "genies"]

persona:
  role: "Financial Data Analyst"
  goal: "Provide accurate financial analysis and insights"
  traits:
  - analytical
  - detail-oriented
  - precise
```

### **4. Configure Appropriate Metrics**

```yaml
evaluation:
  builtin_metrics:
  - name: answer_correctness
    threshold: 0.8
    weight: 2.0
  - name: analysis_quality
    threshold: 0.7
  - name: safety_compliance
    threshold: 1.0
    weight: 3.0
```

### **5. Use Comprehensive BDD Scenarios**

```yaml
feature_specifications:
  scenarios:
  - name: basic_functionality
    description: "The agent should perform basic tasks correctly"
    input:
      question: "What is the capital of France?"
    expected_output:
      answer: "Should provide accurate information about Paris"
  - name: advanced_functionality
    description: "The agent should handle complex scenarios"
    input:
      problem: "Analyze this financial dataset"
    expected_output:
      solution: "Should provide comprehensive analysis"
```

---

💡 **Pro Tip**: Use the `super spec schema` command to explore all available configuration options for each tier! 