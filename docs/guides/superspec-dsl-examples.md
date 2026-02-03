# 📙 SuperSpec DSL Examples

<div align="center">
  <img src="../logo.png" alt="SuperOptiX Logo" width="150" style="margin-bottom: 10px;"/>
  <h2 style="margin-top: 10px; margin-bottom: 10px;">SuperSpec DSL Examples</h2>
  <p style="margin-top: 10px; margin-bottom: 20px;"><strong>Real-world agent examples across all 6 frameworks</strong></p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="../superspec/" style="background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📝 SuperSpec Overview</a>
  <a href="../superspec-dsl-reference/" style="background: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📗 DSL Reference</a>
  <a href="../superspec-agent-building/" style="background: #FF9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🏗️ Agent Building</a>
  <a href="../superspec-configuration/" style="background: #9C27B0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚙️ Configuration</a>
</div>

---

## 📚 Framework Examples

Each example shows the same agent specification adapted for different frameworks.

### Example 1: Simple AI Assistant

=== "🔬 DSPy"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: assistant
      id: assistant_dspy
      namespace: demo
      version: 1.0.0
      level: oracles
    
    spec:
      target_framework: dspy
      
      language_model:
        provider: ollama
        model: llama3
        api_base: http://localhost:11434
      
      persona:
        role: Helpful AI Assistant
        goal: Provide accurate, helpful responses to user queries
        backstory: |
          You are a helpful AI assistant.
        reasoning:
          steps:
            - Understand the user's question
            - Formulate a clear response
      
      input_fields:
        - name: query
          type: str
          description: User's question
      
      output_fields:
        - name: response
          type: str
          description: Assistant's response
      
      feature_specifications:
        scenarios:
          - name: Greeting
            input:
              query: "Hello"
            expected_output:
              response: "greeting"
              expected_keywords:
                - hello
                - assistant
      
      optimization:
        optimizer:
          name: GEPA
          params:
            metric: answer_exact_match
            auto: medium
    ```

=== "🤖 OpenAI SDK"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: assistant_openai
      id: assistant_openai
      namespace: demo
      version: 1.0.0
      level: oracles
    
    spec:
      target_framework: openai
      
      language_model:
        provider: ollama
        model: llama3
        api_base: http://localhost:11434
      
      persona:
        instructions: |
          You are a helpful AI assistant that provides accurate,
          clear, and concise responses to user queries.
          
          Your approach:
          1. Understand the user's question
          2. Provide a clear, helpful response
          3. Be friendly and professional
      
      input_fields:
        - name: query
          type: str
          description: User's question
      
      output_fields:
        - name: response
          type: str
          description: Assistant's response
      
      feature_specifications:
        scenarios:
          - name: Greeting
            input:
              query: "Hello"
            expected_output:
              response: "greeting"
              expected_keywords:
                - hello
                - assistant
    ```

=== "👥 CrewAI"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: researcher_crew
      id: researcher_crew
      namespace: demo
      version: 1.0.0
      level: genies
    
    spec:
      target_framework: crewai
      
      language_model:
        provider: ollama
        model: llama3
        api_base: http://localhost:11434
      
      persona:
        role: AI Research Assistant
        goal: Conduct thorough research and provide accurate insights
        backstory: |
          You are an experienced research assistant with expertise in
          gathering and analyzing information from multiple sources.
      
      tasks:
        - name: research_task
          description: |
            Research the given topic thoroughly, gathering information
            from all available sources.
          expected_output: |
            A comprehensive research summary with key findings and insights.
      
      input_fields:
        - name: query
          type: str
          description: Research topic or question
      
      output_fields:
        - name: response
          type: str
          description: Research findings
      
      feature_specifications:
        scenarios:
          - name: Research query
            input:
              query: "What is quantum computing?"
            expected_output:
              response: "quantum computing"
              expected_keywords:
                - quantum
                - computing
    ```

=== "🔮 Google ADK"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: assistant_adk
      id: assistant_adk
      namespace: demo
      version: 1.0.0
      level: oracles
    
    spec:
      target_framework: google-adk
      
      language_model:
        provider: google
        model: gemini-2.0-flash
        api_key: ${GOOGLE_API_KEY}
      
      persona:
        instructions: |
          You are a helpful AI assistant powered by Google's Gemini.
          Provide accurate, informative responses.
          
          Your approach:
          1. Understand the user's question
          2. Formulate a clear response
          3. Provide helpful insights
      
      input_fields:
        - name: query
          type: str
          description: User's question
      
      output_fields:
        - name: response
          type: str
          description: Assistant's response
      
      feature_specifications:
        scenarios:
          - name: Greeting
            input:
              query: "Hello"
            expected_output:
              response: "greeting"
    ```

=== "🏢 Microsoft"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: assistant_microsoft
      id: assistant_microsoft
      namespace: demo
      version: 1.0.0
      level: oracles
    
    spec:
      target_framework: microsoft
      
      language_model:
        provider: ollama
        model: gpt-oss:20b
        api_base: http://localhost:11434
      
      persona:
        instructions: |
          You are a helpful AI assistant.
          Provide accurate, clear responses.
          
          Your approach:
          1. Understand the question
          2. Gather relevant information
          3. Formulate a clear response
      
      input_fields:
        - name: query
          type: str
          description: User's question
      
      output_fields:
        - name: response
          type: str
          description: Assistant's response
      
      feature_specifications:
        scenarios:
          - name: Greeting
            input:
              query: "Hello"
            expected_output:
              response: "greeting"
    ```

=== "🌊 DeepAgents"

    ```yaml
    apiVersion: agent/v1
    kind: AgentSpec
    metadata:
      name: research_agent_deepagents
      id: research_agent_deepagents
      namespace: demo
      version: 1.0.0
      level: genies
    
    spec:
      target_framework: deepagents
      
      language_model:
        provider: ollama
        model: llama3
        api_base: http://localhost:11434
      
      persona:
        instructions: |
          You are an AI research agent.
          Conduct thorough research and provide insights.
      
      input_fields:
        - name: query
          type: str
          description: Research query
      
      output_fields:
        - name: response
          type: str
          description: Research findings
      
      feature_specifications:
        scenarios:
          - name: Research
            input:
              query: "Explain AI optimization"
            expected_output:
              response: "optimization"
    ```

---

## 🧞 Example 2: Agent with Tools & RAG

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: genie_with_tools
  id: genie_with_tools
  namespace: demo
  version: 1.0.0
  level: genies
  description: Agent with web search and RAG capabilities

spec:
  target_framework: dspy  # Works with any framework!
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
  
  persona:
    role: Information Retrieval Specialist
    goal: Find and synthesize information from multiple sources
    backstory: |
      You are an expert at finding relevant information and
      presenting it in a clear, actionable format.
    reasoning:
      steps:
        - Understand the information need
        - Search relevant sources (web + knowledge base)
        - Synthesize findings
        - Present clear recommendations
  
  input_fields:
    - name: query
      type: str
      description: Information request
  
  output_fields:
    - name: response
      type: str
      description: Synthesized information
    - name: sources
      type: list
      description: List of sources used
  
  tools:
    - name: web_search
      type: builtin
      enabled: true
      config:
        max_results: 5
    
    - name: calculator
      type: builtin
      enabled: true
  
  rag:
    enabled: true
    vector_db:
      type: chromadb
      collection_name: knowledge_base
      persist_directory: ./data/chroma
    config:
      top_k: 5
      chunk_size: 512
  
  memory:
    enabled: true
    backend: sqlite
    short_term:
      max_size: 100
    long_term:
      enabled: true
      semantic_search: true
  
  feature_specifications:
    scenarios:
      - name: Web search query
        input:
          query: "Latest developments in AI"
        expected_output:
          response: "AI developments"
          expected_keywords:
            - AI
            - developments
            - recent
      
      - name: Calculation query
        input:
          query: "What is 15% of 200?"
        expected_output:
          response: "30"
          expected_keywords:
            - "30"
            - percent
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: medium
        reflection_lm: qwen3:8b
```

---

## 🔌 Example 3: MCP Protocol Agent

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: mcp_protocol_agent
  id: mcp_protocol_agent
  namespace: protocols
  version: 1.0.0
  level: genies
  description: Agent using Model Context Protocol for tool discovery

spec:
  target_framework: dspy
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
  
  persona:
    role: MCP-Enabled Assistant
    goal: Use MCP tools to access file systems and repositories
    backstory: |
      You are an assistant that can access files and repositories
      through the Model Context Protocol.
  
  input_fields:
    - name: query
      type: str
      description: User's request
  
  output_fields:
    - name: response
      type: str
      description: Response with file/repo information
  
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args:
            - "-y"
            - "@modelcontextprotocol/server-filesystem"
            - "/path/to/docs"
        
        - name: git
          command: npx
          args:
            - "-y"
            - "@modelcontextprotocol/server-git"
            - "--repository"
            - "/path/to/repo"
    config:
      top_k: 5
  
  feature_specifications:
    scenarios:
      - name: File access query
        input:
          query: "What files are in the docs folder?"
        expected_output:
          response: "file list"
          expected_keywords:
            - files
            - docs
  
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium
```

---

## 📊 Example 4: Multi-Agent Crew

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: content_creator_crew
  id: content_creator_crew
  namespace: demo
  version: 1.0.0
  level: genies
  description: CrewAI multi-agent content creation system

spec:
  target_framework: crewai
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
  
  persona:
    role: Content Creator
    goal: Create engaging, well-researched content
    backstory: |
      You are an experienced content creator who specializes in
      creating engaging, informative content.
  
  tasks:
    - name: content_creation
      description: |
        Create high-quality content on the given topic.
        Research the topic, outline key points, and write engaging content.
      expected_output: |
        A well-structured article with introduction, body, and conclusion.
        Include key insights and actionable takeaways.
  
  input_fields:
    - name: topic
      type: str
      description: Content topic
    - name: target_audience
      type: str
      description: Target audience description
  
  output_fields:
    - name: response
      type: str
      description: Created content
  
  tools:
    - name: web_search
      type: builtin
      enabled: true
  
  feature_specifications:
    scenarios:
      - name: Content creation
        input:
          topic: "Future of AI"
          target_audience: "Tech enthusiasts"
        expected_output:
          response: "AI future content"
          expected_keywords:
            - AI
            - future
            - technology
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: medium
```

---

## 🧠 Example 5: Agent with Memory Optimization

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: memory_optimized_agent
  id: memory_optimized_agent
  namespace: demo
  version: 1.0.0
  level: genies
  description: Agent with GEPA-optimized memory selection

spec:
  target_framework: dspy
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
  
  persona:
    role: Conversational AI with Memory
    goal: Maintain context across conversations
    backstory: |
      You are a conversational AI that remembers previous
      interactions and provides contextual responses.
  
  input_fields:
    - name: query
      type: str
      description: User's message
  
  output_fields:
    - name: response
      type: str
      description: Contextual response
  
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
    optimization:
      enabled: true  # GEPA-based memory selection
      max_context_tokens: 2000
      relevance_threshold: 0.7
  
  feature_specifications:
    scenarios:
      - name: Context recall
        input:
          query: "What did we discuss earlier?"
        expected_output:
          response: "previous discussion"
          expected_keywords:
            - discussed
            - earlier
  
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium
```

---

## 🔍 Example 6: RAG-Optimized Research Agent

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: rag_research_agent
  id: rag_research_agent
  namespace: research
  version: 1.0.0
  level: genies
  description: Research agent with optimized RAG retrieval

spec:
  target_framework: dspy
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
  
  persona:
    role: Research Analyst
    goal: Provide well-researched, evidence-based answers
    backstory: |
      You are a research analyst who excels at finding and
      synthesizing information from knowledge bases.
  
  input_fields:
    - name: research_question
      type: str
      description: Research question
  
  output_fields:
    - name: response
      type: str
      description: Research findings
    - name: citations
      type: list
      description: List of source citations
  
  rag:
    enabled: true
    vector_db:
      type: lancedb  # or chromadb, weaviate, qdrant, milvus
      uri: ./data/lancedb
      table_name: research_docs
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
      reranking: true
    optimization:
      enabled: true  # GEPA-based RAG optimization
      query_expansion: true
      context_compression: true
  
  tools:
    - name: web_search
      type: builtin
      enabled: true
  
  feature_specifications:
    scenarios:
      - name: Research with citations
        input:
          research_question: "What are the benefits of RAG?"
        expected_output:
          response: "RAG benefits"
          expected_keywords:
            - RAG
            - retrieval
            - benefits
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: intensive  # Use intensive for research agents
        reflection_lm: qwen3:8b
        skip_perfect_score: true
```

---

## 🎼 Example 7: Multi-Agent Orchestra

```yaml
apiVersion: orchestra/v1
kind: OrchestraSpec
metadata:
  name: research_orchestra
  id: research_orchestra
  version: 1.0.0
  description: Multi-agent research orchestra

spec:
  agents:
    - agent_id: researcher
      role: lead
    - agent_id: analyst
      role: support
    - agent_id: writer
      role: support
  
  workflow:
    mode: sequential
    steps:
      - agent: researcher
        task: gather_information
      - agent: analyst
        task: analyze_data
      - agent: writer
        task: write_report
  
  coordination:
    strategy: hierarchical
    communication: shared_memory
```

---

## 🔬 Framework-Specific Features

### DSPy-Specific Configuration

```yaml
spec:
  target_framework: dspy
  dspy:
    signature_type: ChainOfThought  # Predict, ChainOfThought, ReAct
    max_retries: 3
    include_demos: true
```

### CrewAI-Specific Configuration

```yaml
spec:
  target_framework: crewai
  crewai:
    verbose: true
    process: sequential  # or hierarchical
    manager_llm: llama3
```

### OpenAI SDK-Specific Configuration

```yaml
spec:
  target_framework: openai
  openai:
    parallel_tool_calls: true
    response_format: text  # or json_object
```

---

## 📈 Advanced: Custom Metrics

Define custom evaluation metrics for domain-specific optimization.

```yaml
spec:
  evaluation:
    custom_metrics:
      - name: factual_accuracy
        type: llm_judge
        prompt: |
          Rate the factual accuracy of the response on a scale of 0-100.
          Consider: correctness, precision, completeness.
        judge_model: gpt-4o-mini
      
      - name: response_length
        type: python
        function: len
        target: response
        expected_range: [50, 200]
```

---

## 🔧 Complete Real-World Example

Here's a production-ready agent with all features:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: production_agent
  id: production_agent
  namespace: production
  version: 2.1.0
  level: genies
  stage: stable
  description: Production-ready agent with all features
  tags:
    - production
    - rag
    - mcp
    - memory
  created_at: "2025-01-15T10:00:00Z"
  updated_at: "2025-01-20T14:30:00Z"

spec:
  target_framework: dspy
  
  language_model:
    provider: ollama
    model: llama3
    api_base: http://localhost:11434
    temperature: 0.7
    max_tokens: 2000
  
  persona:
    role: Production AI Assistant
    goal: Provide accurate, helpful responses with citations
    backstory: |
      You are a production-grade AI assistant with access to
      extensive knowledge bases, tools, and memory systems.
    reasoning:
      steps:
        - Understand user intent
        - Search knowledge base (RAG)
        - Use tools when needed
        - Recall relevant memories
        - Formulate comprehensive response
        - Provide citations
  
  input_fields:
    - name: query
      type: str
      description: User's question or request
      required: true
    - name: context
      type: str
      description: Additional context
      required: false
  
  output_fields:
    - name: response
      type: str
      description: Agent's response
    - name: sources
      type: list
      description: Citation sources
    - name: confidence
      type: float
      description: Confidence score
  
  tools:
    - name: web_search
      type: builtin
      enabled: true
      config:
        max_results: 5
        search_engine: duckduckgo
    
    - name: calculator
      type: builtin
      enabled: true
    
    - name: custom_api
      type: custom
      function: tools.custom_api.call_api
      config:
        endpoint: https://api.example.com
        timeout: 30
  
  rag:
    enabled: true
    vector_db:
      type: chromadb
      collection_name: production_docs
      persist_directory: ./data/chroma
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "./docs"]
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "."]
    config:
      top_k: 5
      chunk_size: 512
      chunk_overlap: 50
      reranking: true
    optimization:
      enabled: true
      query_expansion: true
      context_compression: true
  
  memory:
    enabled: true
    backend: sqlite
    database_path: ./data/memory.db
    short_term:
      max_size: 100
      retention_policy: lru
    long_term:
      enabled: true
      semantic_search: true
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
    optimization:
      enabled: true
      max_context_tokens: 2000
      relevance_threshold: 0.7
  
  guardrails:
    enabled: true
    max_retries: 3
    timeout: 60
    content_filters:
      - no_pii
      - no_toxic_content
  
  feature_specifications:
    scenarios:
      - name: Knowledge base query
        input:
          query: "What is our refund policy?"
        expected_output:
          response: "refund policy"
          expected_keywords:
            - refund
            - policy
      
      - name: Calculation with tools
        input:
          query: "Calculate compound interest for $1000 at 5% for 3 years"
        expected_output:
          response: "compound interest"
          expected_keywords:
            - interest
            - calculation
      
      - name: Web search query
        input:
          query: "Latest news on AI regulation"
        expected_output:
          response: "AI regulation news"
          expected_keywords:
            - AI
            - regulation
            - news
  
  evaluation:
    custom_metrics:
      - name: citation_quality
        type: llm_judge
        judge_model: gpt-4o-mini
      - name: response_relevance
        type: embedding_similarity
        threshold: 0.8
  
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: intensive
        reflection_lm: qwen3:8b
        reflection_minibatch_size: 3
        skip_perfect_score: true
        add_format_failure_as_feedback: true
```

---

## 🚀 Next Steps

<div align="center" style="margin: 30px 0;">
  <a href="../superspec-dsl-reference/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📗 DSL Reference</a>
  <a href="../superspec-agent-building/" style="background: #2196F3; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🏗️ Build Your Agent</a>
  <a href="../../quick-start/" style="background: #FF9800; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 Quick Start</a>
  <a href="../multi-framework/" style="background: #9C27B0; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🔬 Framework Guide</a>
</div>

