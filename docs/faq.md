# ❓ Frequently Asked Questions

## 🚀 **Framework Overview**

### How is SuperOptiX different from other agent frameworks?

SuperOptiX is a **full-stack, all-in-one** agent framework that provides:

- **🎯 Evaluation-First Approach** - Built-in BDD/TDD methodology with executable specifications
- **⚡ Optimization-First Design** - Advanced DSPy optimization with production-ready techniques
- **🎭 Multi-Agent Orchestration** - Sophisticated coordination patterns (pipeline, broadcast, conditional, parallel)
- **🧠 Advanced Memory Systems** - Multi-layered memory with episodic, semantic, and working memory
- **🔧 Complete Tool Ecosystem** - 50+ built-in tools across 17 industry categories
- **📊 Production Observability** - Comprehensive tracing, debugging, and monitoring
- **🔄 CI/CD Integration** - Built-in quality gates and automated testing workflows

Unlike other frameworks that focus on single components, SuperOptiX provides a complete ecosystem for building, testing, optimizing, and deploying production-ready AI agents.

### Is SuperOptiX just a DSPy wrapper?

**No, SuperOptiX is "Agentic DSPy" - an evolution beyond DSPy.** While SuperOptiX harnesses the full power of DSPy's optimization principles, it transforms them into a production-ready agentic AI platform:

- **🧬 Advanced Agentic Modules** - Custom modules for multi-agent coordination, protocol support (MCP, A2A), and memory-optimized interactions
- **🏗️ Application-Layer Abstractions** - SuperSpec DSL for declarative agent building at the application layer
- **🎯 BDD Testing Framework** - Behavior-driven specifications and executable tests for agent validation
- **🎭 Multi-Tier Architecture** - Progressive complexity from Oracles to Sovereigns
- **🔄 Production-Ready Features** - Memory management, observability, and deployment automation
- **🔧 Modular Optimization** - DSPy as primary adapter with framework-agnostic design for future optimization frameworks

**SuperOptiX treats DSPy as the optimization engine while providing the complete agentic ecosystem around it.**

### What's the relationship between SuperOptiX and DSPy?

SuperOptiX and DSPy have a **symbiotic relationship** where each framework amplifies the other's strengths:

**🚀 DSPy's Core Strengths:**
- Only framework with systematic optimization
- Iterative optimization principles (perfect for TDD/BDD)
- Assertions and evaluations for validation
- Signature generation and module composition

**🧬 SuperOptiX's Agentic Evolution:**
- **Advanced Custom Modules** for agentic scenarios beyond standard DSPy
- **Automatic Pipeline Generation** from high-level SuperSpec specifications  
- **Protocol Support** for MCP, A2A, and emerging agentic standards
- **Application-Layer DSL** that compiles to optimized DSPy implementations

**💡 Key Insight:** DSPy provides the optimization foundation; SuperOptiX provides the agentic architecture, production tooling, and developer experience.

### Why did SuperOptiX choose DSPy over other frameworks?

DSPy is the **only framework that systematically optimizes** language model programs, making it uniquely suited for building reliable agentic systems:

**🔬 Scientific Approach:**
- **Optimization-First Philosophy** - Treats prompt engineering as a systematic optimization problem
- **Evaluation-Driven Development** - Built-in assertions and metrics for validation
- **Composable Architecture** - Modules that can be optimized individually and collectively

**🧪 Perfect for Agentic TDD/BDD:**
- **Iterative Refinement** - Aligns with test-driven development principles
- **Behavioral Validation** - Assertions that ensure agent behavior meets specifications
- **Systematic Testing** - Framework for comprehensive agent evaluation

**🚀 Production Readiness:**
- **Transparent Optimization** - Clear visibility into optimization process
- **Reproducible Results** - Deterministic optimization with version control
- **Scalable Architecture** - Designed for complex, multi-component systems

**SuperOptiX recognizes that DSPy's approach is fundamentally different from other frameworks - it's built for systematic optimization rather than ad-hoc prompt engineering.**

### Can SuperOptiX work with other optimization frameworks?

**Yes, SuperOptiX is designed with a modular optimization architecture:**

**🔧 Current Implementation:**
- **DSPy as Primary Adapter** - Leverages DSPy's proven optimization capabilities
- **Comprehensive Integration** - Full DSPy feature support with agentic extensions

**🚀 Future-Ready Design:**
- **Framework Agnostic** - Ready to integrate other optimization frameworks as they emerge
- **Adapter Pattern** - Clean interfaces for adding new optimization backends
- **User Choice** - Multiple optimization strategies for different use cases
- **Custom Implementations** - Support for specialized optimization layers

**💡 Philosophy:** DSPy is currently the gold standard for optimization, but SuperOptiX is prepared to evolve as the optimization landscape develops.

## 💰 **Licensing & Tiers**

### Is SuperOptiX open source?
Yes! SuperOptiX is open source under the MIT License. We welcome contributions from the community.

- **🎭 Oracle Tier** - Basic Q&A and simple evaluation capabilities
- **🧞 Genie Tier** - Tools, RAG, memory, and streaming features
- **🎭 Basic Orchestration** - Simple multi-agent coordination
- **🛠️ Core Tools** - Essential tools for development and prototyping
- **📊 Basic Observability** - Tracing and debugging capabilities

**⚠️ Important:** The OSS version is designed for **demos and prototypes**. It's not recommended for production use unless you have significant expertise in AI system deployment and optimization.

## 🔧 **Installation & Dependencies**

### I'm getting dependency conflicts when installing CrewAI with SuperOptiX. What's happening?

This is a **known dependency conflict** between CrewAI and DSPy due to incompatible `json-repair` version requirements:

**🔍 The Problem:**
- **DSPy 3.0.0** requires `json-repair>=0.30.0`
- **CrewAI 0.157.0** requires `json-repair==0.25.2` (exact version)

**The Solution:**
Install CrewAI manually after installing SuperOptiX with DSPy support:

```bash
# Install SuperOptiX with DSPy support (this gets compatible json-repair)
pip install "superoptix[optimas]"

# Install CrewAI without dependencies to avoid conflicts
pip install crewai==0.157.0 --no-deps

# Ensure compatible json-repair version
pip install "json-repair>=0.30.0"
```

**💡 Why This Works:**
- The `--no-deps` flag prevents pip from trying to resolve conflicting dependencies
- We manually install the version of `json-repair` that satisfies both packages
- Both packages work together at runtime despite metadata conflicts

**📚 Alternative:**
If you only need CrewAI functionality, you can install SuperOptiX without DSPy support and then add CrewAI normally.

### How can I access higher tiers (Protocols and beyond)?

Higher tiers require **enterprise licensing** from Superagentic AI:

- **🎯 Protocols Tier** - Advanced features, parallel execution, and production optimizations
- **🚀 Enterprise Features** - Protocol integrations (MCP, A2A), advanced orchestration, and custom deployments
- **🔧 Custom Solutions** - Tailored packages based on specific use cases and requirements

**📞 Contact:** There's no set pricing as it varies by use case. Contact Superagentic AI for a tailored package based on your specific needs and requirements.

## 🎓 **Learning & Usage**

### Do I need to know DSPy to use SuperOptiX?

**Not necessarily, but it helps:**

- **🛡️ SuperOptiX handles DSPy complexity** - The framework abstracts most DSPy internals
- **🚀 You can start immediately** - Basic agents work out-of-the-box with minimal DSPy knowledge
- **🎯 DSPy knowledge = Full control** - Understanding DSPy helps you create production-worthy pipelines
- **📚 Learning path** - Start with SuperOptiX basics, then learn DSPy for advanced customization

**💡 Recommendation:** Start with SuperOptiX's high-level APIs, then learn DSPy as you need more control over optimization and pipeline design.

## ⚡ **Optimization & Performance**

### What optimization strategies does SuperOptiX support?

SuperOptiX provides multiple optimization strategies:

- **🎯 BootstrapFewShot** - Automatic few-shot learning with bootstrapped demonstrations
- **🔄 ReAct** - Reasoning and acting optimization for tool-using agents
- **📊 Multi-Metric Optimization** - Optimize for multiple metrics simultaneously
- **🎭 Tier-Specific Optimization** - Different strategies for Oracles, Genies, and Protocols tiers
- **🛠️ Tool-Aware Optimization** - Optimization that considers tool usage patterns



### Can I optimize agents for specific use cases?

**Yes, absolutely:**

- **🎯 Custom Evaluation Metrics** - Define domain-specific evaluation criteria
- **📊 BDD Scenarios** - Create executable specifications for your use case
- **🛠️ Tool Integration** - Optimize for specific tool usage patterns
- **🧠 Memory Optimization** - Tune memory systems for your data patterns
- **📈 Performance Profiling** - Identify and optimize bottlenecks

## 🧪 **Evaluation & Testing**

### How does SuperOptiX's evaluation system work?

The evaluation system provides:

- **🎯 BDD/TDD Approach** - Executable specifications as test cases
- **📊 Multiple Metrics** - Semantic F1, exact match, reasoning quality, tool efficiency
- **🔄 Continuous Evaluation** - Automated testing in CI/CD pipelines
- **📈 Quality Gates** - Pass/fail thresholds for automated deployment
- **🎭 Scenario Testing** - Complex multi-step scenario validation

### What evaluation metrics are available?

SuperOptiX includes:

- **🎯 Semantic F1** - Semantic similarity scoring
- **Exact Match** - Precise answer matching
- **🧠 Reasoning Quality** - Assessment of reasoning process
- **🛠️ Tool Usage Efficiency** - Evaluation of tool selection and usage
- **📊 Response Time** - Performance and latency metrics
- **💰 Cost Metrics** - Token usage and cost tracking
- **🎭 Custom Metrics** - Domain-specific evaluation criteria

### How do I set up automated testing?

The framework provides:

- **🔄 CI/CD Integration** - GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **📊 Quality Gates** - Automated pass/fail thresholds
- **🎯 BDD Scenarios** - Executable specifications as tests
- **📈 Performance Monitoring** - Continuous performance tracking
- **🚀 Automated Deployment** - Deploy only when tests pass



## 🧠 **Memory Systems**

### What types of memory does SuperOptiX support?

The framework provides three memory layers:

- **📝 Episodic Memory** - Conversation history and interaction episodes
- **🧠 Semantic Memory** - Persistent knowledge and relationships
- **⚡ Working Memory** - Temporary session information

### What storage backends are available?

SuperOptiX supports multiple backends:

- **🗄️ SQLite** - Lightweight, file-based storage (default)
- **🔴 Redis** - High-performance, in-memory storage
- **📁 File** - Simple file-based storage with JSON/YAML formats

### How does memory integration work?

Memory integration provides:

- **🎯 Context Retrieval** - Automatic relevant context for responses
- **📊 Memory Statistics** - Usage tracking and analytics
- **🔄 Automatic Cleanup** - Retention policies and cleanup
- **🧠 Semantic Search** - Find relevant memories by content
- **⚡ Working Memory** - Temporary data with TTL support

## 🛠️ **Tools & Integrations**

### What tools are included in SuperOptiX?

The framework includes **50+ tools** across **17 categories**:

- **🔧 Core Tools** - Web search, calculator, file operations, date/time
- **💻 Development** - Git, API testing, database queries, code review
- **💰 Finance** - Currency conversion, tax calculation, loan analysis
- **🏥 Healthcare** - BMI calculator, medical lookups, drug interactions
- **📈 Marketing** - SEO analysis, email validation, social metrics
- **⚖️ Legal** - Legal lookups, contract analysis, case search
- **🎓 Education** - Grade calculation, study scheduling, quiz generation

### Can I create custom tools?

**Absolutely:**

- **🔧 BaseTool Class** - Inherit from BaseTool for custom tools
- **🛠️ Factory Pattern** - Use tool factories for easy creation
- **📊 Schema Validation** - Automatic parameter validation
- **🎯 Category Organization** - Organize tools by industry/function
- **🔄 Registry System** - Automatic tool discovery and registration

### How do I integrate external APIs?

SuperOptiX provides:

- **🔑 API Key Management** - Secure API key handling
- **🔄 Retry Logic** - Automatic retry with exponential backoff
- **📊 Rate Limiting** - Built-in rate limit handling
- **🛡️ Error Handling** - Graceful error handling and fallbacks
- **📈 Monitoring** - API usage tracking and metrics









---

**💡 Need more help?** Check out our [documentation](index.md), [guides](guides/index.md), or [contact support](mailto:support@superagentic.ai). 