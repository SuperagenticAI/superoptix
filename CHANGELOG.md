# 📋 Changelog

All notable changes to SuperOptiX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0b17] - 2025-08-18

### 🔧 Fixed
- **Agent Naming Consistency**: Fixed inconsistent agent IDs (hyphens vs underscores) across all GEPA agents
  - Standardized all agent IDs to use underscores to match filename convention
  - Fixed: `advanced_math_gepa`, `enterprise_extractor_gepa`, `medical_assistant_gepa`, `contract_analyzer_gepa`, `privacy_delegate_gepa`, `data_science_gepa`, `security_analyzer_gepa`, `gepa_demo`
- **Genies Tier Optimization Bug**: Fixed `input_field` variable scope error in DSPy Genies pipeline template
  - Resolved "name 'input_field' is not defined" error during optimization
  - Added proper variable scoping in train() and evaluate() methods
  - Genies tier agents now optimize successfully with BootstrapFewShot, SIMBA, and BetterTogether optimizers

### 📚 Documentation
- **Comprehensive GEPA Documentation**: Added detailed documentation for all 8 GEPA agents across multiple domains
  - Mathematics: `advanced_math_gepa`, `data_science_gepa`
  - Healthcare: `medical_assistant_gepa`
  - Legal: `contract_analyzer_gepa`
  - Enterprise: `enterprise_extractor_gepa`
  - Security: `security_analyzer_gepa`, `privacy_delegate_gepa`
  - Demo: `gepa_demo`
- **DSPy Optimizers Quick Start Guide**: Added comprehensive quick start commands for all 8 DSPy optimizers
  - Complete workflows (pull, compile, optimize, test) for each optimizer
  - Domain-specific examples and use cases
  - Performance comparisons and best practices
- **GEPA Limitations Documentation**: Added critical guidance about GEPA compatibility
  - Clear warning that GEPA doesn't work with tool-calling agents (Genies tier+)
  - Detailed explanation of why (complex output formats, tool call parsing issues)
  - Alternative optimizer recommendations for each tier
  - Agent tier compatibility table

### 🚀 Enhanced
- **Ready-to-Run Commands**: All documentation now includes copy-paste commands with proper timeouts
- **Agent Discovery**: Complete tables of all available agents organized by domain and optimizer
- **Practical Examples**: Real-world goals and use cases for every agent type

## [0.1.0b16] - 2025-01-07

### 🚀 Added
- **🍎 Apple Silicon GPT-OSS Support**: MLX-LM v0.26.3 now provides native Apple Silicon support for GPT-OSS models
  - **No More Mixed Precision Issues**: MLX-LM handles MXFP4 quantization properly on Apple Silicon
  - **Native Performance**: GPT-OSS models now run natively without CPU fallback
  - **Multiple Backend Options**: Users can choose between MLX (native) and Ollama (performance)
- **🆕 GPT-OSS Model Support**: Added support for OpenAI's latest open-source models (GPT-OSS-20B and GPT-OSS-120B)
  - Apache 2.0 license for commercial use
  - Native MXFP4 quantization for efficient inference
  - Resources: [GPT-OSS-120B](https://huggingface.co/openai/gpt-oss-120b), [GPT-OSS-20B](https://huggingface.co/openai/gpt-oss-20b), [Ollama Library](https://ollama.com/library/gpt-oss)
- **MLX Model Evaluation**: Added `super model mlx evaluate` command for benchmarking MLX models using LM-Eval integration
- **MLX Model Fusion**: Added `super model mlx fuse` command for fusing finetuned adapters into base models
- **Backend-Specific Commands**: Reorganized model commands with `super model mlx`, `super model vllm`, `super model sglang` subcommands
- **Advanced MLX Features**: Support for evaluation tasks (mmlu, arc, hellaswag, etc.), fusion with dequantization, GGUF export, and HuggingFace upload
- **vLLM High-Performance Inference**: Added `super model vllm serve`, `super model vllm generate`, `super model vllm benchmark`, and `super model vllm quantize` commands for production-grade inference
- **vLLM Advanced Features**: Support for multi-GPU serving, streaming generation, performance benchmarking, and model quantization (AWQ, GPTQ, SqueezeLLM)
- **vLLM Optional Dependency**: Added vLLM as optional dependency with `pip install superoptix[vllm]` for Linux systems with NVIDIA GPUs
- **SGLang Streaming & Optimization**: Added `super model sglang serve`, `super model sglang generate`, `super model sglang optimize`, and `super model sglang benchmark` commands for streaming and optimization
- **SGLang Advanced Features**: Support for streaming generation, performance optimization (O0-O3), advanced batching, and real-time inference
- **SGLang Optional Dependency**: Added SGLang as optional dependency with `pip install superoptix[sglang]` for Linux systems with NVIDIA GPUs
- **MLX Experimental Features**: Added experimental `super model convert` and `super model quantize` commands for MLX model conversion and quantization (see `MLX_EXPERIMENTAL_FEATURES.md`)
- **Auto-installation**: Enhanced `super model run` with automatic model installation and backend detection

### 🔧 Updated
- **MLX Dependencies**: Updated to MLX-LM v0.26.3 for native GPT-OSS support on Apple Silicon
- **Model Management**: Enhanced MLX backend with better error handling and format validation
- **CLI Improvements**: Simplified UX by removing `--force` flags for cleaner commands

### 🐛 Fixed
- **Apple Silicon Compatibility**: Resolved mixed precision issues that prevented GPT-OSS models from running on Apple Silicon
- **HuggingFace Backend Limitations**: Documented that HuggingFace backend still has mixed precision issues on Apple Silicon

### 📚 Documentation
- **Apple Silicon Guide**: Updated documentation to reflect GPT-OSS support via MLX-LM and Ollama backends
- **Performance Comparison**: Added performance metrics comparing MLX-LM vs Ollama vs HuggingFace backends

## [Unreleased]

### 🚀 Added
- Initial foundation for agentic AI orchestration
- DSPy-native agent development framework
- Multi-tier orchestration system (Oracle → Sage → SuperAgent)
- BDD-driven agent testing and validation
- Memory systems with multi-layered architecture
- Comprehensive observability and tracing
- Enterprise-ready agent deployment patterns

### 🔄 Changed
- Established project structure and core modules
- Defined API contracts for agent development
- Set up development workflow and contribution guidelines

### 🐛 Fixed
- Bug fixes in development

### 🔒 Security
- Implemented secure agent execution sandboxing
- Added input validation and sanitization
- Established security best practices for agent development

## [0.1.0b11] - 2025-01-06

### 🚀 Added
- **Simplified Model Installation**: Completely redesigned model installation system for MLX and HuggingFace backends
- **Detailed Progress Display**: Added file-by-file download progress for large models with safetensors/bin files
- **Improved Model Detection**: Fixed model detection logic to properly identify installed models vs metadata-only downloads

### 🔧 Updated
- **MLX Backend**: Simplified installation using direct `snapshot_download` with single-threaded progress display
- **HuggingFace Backend**: Streamlined installation with detailed file-by-file progress for large models
- **CLI Integration**: Enhanced `super model install` command with proper model detection and progress display
- **Model Detection Logic**: Fixed detection to require actual model files (`.safetensors`, `.bin`) not just config files

### 🐛 Fixed
- **Model Installation Issues**: Resolved problems with large model downloads getting stuck at "Fetching files: 0%"
- **False Positive Detection**: Fixed issue where models with only metadata were incorrectly shown as "installed"
- **Progress Display**: Fixed missing detailed progress for individual model file downloads

### 📚 Documentation
- **Installation Guide**: Updated `SIMPLE_MODEL_INSTALLATION.md` with new simplified approach
- **Testing Scripts**: Added `test_simple_install.py` for validating model installation functionality

### 🔄 Changed
- **Installation Approach**: Removed complex validation and progress tracking in favor of simple, reliable downloads
- **Progress Display**: Switched from custom progress bars to standard HuggingFace Hub progress display
- **Error Handling**: Simplified error handling with clear, actionable error messages

### 🎯 Technical Details
- **Single-Threaded Downloads**: Uses `max_workers=1` to force detailed progress display for large models
- **Direct Download**: Uses `snapshot_download` without complex parameters for reliability
- **Proper Detection**: Checks for actual model files in snapshots directory, not just metadata

---

## [0.1.0] - 2024-12-XX

### 🎉 Initial Release

This is the first release of SuperOptiX - "The Kubernetes of Agentic AI"!

### 🚀 Added

#### 🏗️ Core Framework
- **DSPy-Native Architecture**: Built on DSPy 3.0 for self-improving agent programs
- **Agent Playbook System**: Declarative agent configuration with YAML
- **Multi-Agent Orchestration**: Sophisticated agent coordination and workflow management
- **Memory Systems**: Long-term, short-term, and episodic memory backends
- **Evaluation Framework**: Built-in testing and quality metrics for agents

#### 🛠️ CLI Tools
- `super init`: Initialize new agentic projects with full scaffolding
- `super agent create`: Generate agent templates and configurations
- `super compile`: Compile agents with DSPy optimization
- `super orchestra`: Multi-agent orchestration and deployment
- `super run`: Execute individual agents and agent workflows

#### 🎯 Agent Templates
- **Business & Consulting**: Strategy consultants, business analysts, change managers
- **Software Development**: Developers, QA engineers, DevOps, architects
- **Healthcare**: Medical assistants, health educators, mental health coaches
- **Education**: Tutors, instructors, study coaches across multiple subjects
- **Finance**: Financial advisors, budget analysts, investment researchers
- **Marketing**: Content creators, SEO specialists, campaign strategists
- **Legal**: Contract analyzers, compliance checkers, legal researchers
- **And many more!** (20+ industry categories)

#### 🧠 Memory & Context
- **Redis Backend**: Scalable memory storage for production deployments
- **Vector Memory**: Semantic memory search and retrieval
- **Context Management**: Intelligent context window optimization
- **Memory Persistence**: Long-term agent memory across sessions

#### 🔍 Observability & Debugging
- **Real-time Monitoring**: Agent performance and behavior tracking
- **Token Usage Analytics**: Cost and performance optimization
- **Debug Dashboard**: Visual debugging tools for agent development
- **Comprehensive Logging**: Detailed execution traces and metrics

#### 🧪 Testing & Quality
- **Agent BDD**: Behavior-driven development for agents
- **Automated Evaluation**: Quality metrics and regression testing
- **Performance Benchmarks**: Agent performance measurement tools
- **Safety Checks**: Built-in guardrails and safety validation

#### 🔌 Integrations
- **DSPy 3.0**: Full integration with latest DSPy features
- **MLFlow**: Experiment tracking and model management
- **FastAPI**: Production-ready API deployment
- **Streamlit**: Rapid UI development for agent interfaces

#### 📚 Documentation & Examples
- **Comprehensive Guides**: Step-by-step tutorials and documentation
- **Code Examples**: Real-world agent implementations
- **Best Practices**: Industry-standard development patterns
- **API Reference**: Complete API documentation

### 🎯 Key Features

- **🔥 Evaluation-First Development**: Every agent is testable and measurable
- **🚀 Auto-Optimization**: DSPy-powered prompt and pipeline optimization
- **🎼 Orchestration**: Kubernetes-style multi-agent coordination
- **🛡️ Production-Ready**: Enterprise-grade reliability and monitoring
- **🔧 Modular Design**: Swap components, models, and tools at runtime
- **📊 Rich Analytics**: Comprehensive performance and quality metrics

### �� Highlights

- **200+ Agent Templates**: Pre-built agents for every industry
- **DSPy 3.0 Integration**: Leverage the latest in self-improving programs
- **Enterprise Security**: Built-in security best practices and compliance
- **Cloud-Native**: Designed for modern cloud deployments
- **Developer Experience**: Intuitive CLI and comprehensive tooling

### 📦 Installation

```bash
pip install superoptix
```

### 🚀 Quick Start

```bash
# Create your first agentic system
super init my_agent_system
cd my_agent_system

# Create and run an agent
super agent create customer_service --template=support
super run customer_service "How can I help you today?"
```

### 🤝 Community

- **GitHub**: https://github.com/SuperagenticAI/superoptix
- **Documentation**: https://github.com/SuperagenticAI/superoptix/docs
- **Discussions**: https://github.com/SuperagenticAI/superoptix/discussions

---

## Release Notes Format

For each release, we document:

### 🚀 Added
New features and capabilities

### 🔄 Changed
Changes to existing functionality

### 🗑️ Deprecated
Features that will be removed in future versions

### 🐛 Fixed
Bug fixes and issue resolutions

### 🔒 Security
Security-related improvements and fixes

### ⚡ Performance
Performance improvements and optimizations

---

## Unreleased Features Preview

### 🔮 Coming Soon

#### v0.2.0 - "Agent Intelligence"
- **Advanced Reasoning**: Multi-step reasoning capabilities
- **Tool Integration**: Enhanced tool calling and API integration
- **Visual Agents**: Image and video processing capabilities
- **Agent Marketplace**: Community-driven agent sharing platform

#### v0.3.0 - "Enterprise Scale"
- **Kubernetes Deployment**: Native K8s orchestration
- **Enterprise SSO**: Advanced authentication and authorization
- **Audit Logging**: Comprehensive audit trails
- **SLA Monitoring**: Service level agreement tracking

#### v0.4.0 - "AI Evolution"
- **Self-Improving Agents**: Agents that evolve based on usage
- **Federated Learning**: Cross-agent knowledge sharing
- **Custom Models**: Support for fine-tuned and custom models
- **Agent Analytics**: Advanced analytics and insights

---

**🎯 Stay Updated**: Watch our repository and join our community to stay informed about the latest releases and features!

**🤝 Contribute**: Help us build the future of agentic AI by contributing to SuperOptiX! 