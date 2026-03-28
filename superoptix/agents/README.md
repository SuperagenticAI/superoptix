# SuperOptiX Agent Marketplace

**Location**: `/superoptix/agents/` (Production marketplace agents)
**Purpose**: Domain-specific, production-ready agent playbooks
**Count**: 151+ agents across 25+ domains
**Access**: `super agent pull <agent_name>`

> **Note**: These are **marketplace agents** for production use. For learning examples, see `/examples/explicit_dspy_agents/`

---

## 📁 Directory Structure

This directory contains production-ready agent playbooks organized by domain:

```
superoptix/agents/
├── agriculture_food/        # Agriculture and food industry agents
├── consulting/              # Business consulting agents
├── demo/                    # Quick demo agents
├── dspy_optimizers/         # DSPy optimizer demonstration agents
├── education/               # Educational and tutoring agents
├── explicit_agents/         # ⭐ Explicit DSPy agents (no mixins, pure DSPy code)
├── energy_utilities/        # Energy and utilities sector agents
├── finance/                 # Financial analysis and trading agents
├── gaming_sports/           # Gaming and sports analytics agents
├── government_public/       # Government and public sector agents
├── healthcare/              # Medical and healthcare agents
├── hospitality_tourism/     # Hospitality and tourism agents
├── human_resources/         # HR and recruitment agents
├── legal/                   # Legal research and compliance agents
├── manufacturing/           # Manufacturing and industrial agents
├── marketing/               # Marketing and advertising agents
├── media_entertainment/     # Media and entertainment agents
├── real_estate/             # Real estate and property agents
├── retail/                  # Retail and e-commerce agents
├── security/                # Cybersecurity and security agents
├── software/                # Software development agents
├── testing/                 # Testing and QA agents
└── transportation/          # Transportation and logistics agents
```

---

## 🚀 How to Use Marketplace Agents

### 1. Browse Available Agents

```bash
# List all agents
super market browse

# Search for specific domain
super market search finance

# Search by capability
super market search "financial analysis"
```

### 2. Pull an Agent

```bash
# Pull agent playbook to your project
super agent pull financial_analyst

# This creates:
# your_project/
# └── agents/
#     └── financial_analyst/
#         └── playbook/
#             └── financial_analyst_playbook.yaml
```

### 3. Compile Agent

```bash
# Generate DSPy pipeline from playbook
super agent compile financial_analyst

# This creates:
# your_project/
# └── agents/
#     └── financial_analyst/
#         ├── playbook/
#         │   └── financial_analyst_playbook.yaml
#         └── pipelines/
#             └── financial_analyst_pipeline.py
```

### 4. Run Agent

```bash
# Run the compiled agent
super agent run financial_analyst
```

---

## 📊 Domain Categories

### Business & Finance
- **finance/** - Financial analysts, traders, advisors
- **consulting/** - Business consultants, strategy advisors
- **marketing/** - Marketing strategists, content creators
- **real_estate/** - Property analysts, real estate advisors

### Healthcare & Wellness
- **healthcare/** - Medical assistants, diagnosis helpers, patient care
- **hospitality_tourism/** - Travel planners, hotel management

### Technology & Engineering
- **software/** - Developers, code reviewers, DevOps
- **security/** - Security analysts, penetration testers
- **manufacturing/** - Industrial automation, quality control
- **energy_utilities/** - Energy management, utility optimization

### Education & Government
- **education/** - Tutors, course creators, learning assistants
- **government_public/** - Public service, policy analysis
- **human_resources/** - Recruitment, employee management

### Creative & Media
- **media_entertainment/** - Content creators, script writers
- **gaming_sports/** - Game designers, sports analysts

### Other Domains
- **legal/** - Legal research, contract analysis, compliance
- **agriculture_food/** - Farming optimization, food safety
- **retail/** - E-commerce, inventory management
- **transportation/** - Logistics, route optimization

---

## 🎯 Agent Types

### By Tier (Capability Level)

| Tier | Complexity | Features | Example Use Cases |
|------|------------|----------|-------------------|
| **Oracles** | Simple | CoT, Basic reasoning | Q&A, Information retrieval |
| **Genies** | Intermediate | CoT + RAG or Tools | Document analysis, Task automation |
| **Protocols** | Advanced | Multi-step workflows | Complex analysis, Decision support |
| **Superagents** | Expert | Multi-agent systems | Enterprise workflows |
| **Sovereigns** | Ultimate | Autonomous systems | Full system orchestration |

### By Pattern

- **Chain of Thought (CoT)** - Step-by-step reasoning
- **RAG (Retrieval-Augmented Generation)** - Knowledge-enhanced
- **ReAct (Reasoning + Acting)** - Tool-using agents
- **Multi-agent** - Collaborative agent systems

---

## 🔍 Finding the Right Agent

### By Use Case

**Need financial analysis?**
```bash
super market search finance
# → financial_analyst, investment_advisor, risk_analyst
```

**Need code help?**
```bash
super market search software
# → developer, code_reviewer, bug_analyzer
```

**Need document processing?**
```bash
super market search "document analysis"
# → legal_researcher, contract_analyzer, content_extractor
```

**Need customer support?**
```bash
super market search "customer support"
# → support_agent, chatbot, complaint_handler
```

---

## 💡 Customization

All marketplace agents are **fully customizable**:

1. **Pull agent** - Get the playbook
2. **Modify playbook** - Adjust to your needs
   - Change model configuration
   - Add/remove tools
   - Modify prompts and instructions
   - Add domain-specific knowledge
3. **Recompile** - Generate updated pipeline
4. **Deploy** - Run in your environment

---

## 🆚 Marketplace vs Examples

| Aspect | Marketplace (`/superoptix/agents/`) | Examples (`/examples/`) |
|--------|-------------------------------------|-------------------------|
| **Purpose** | Production use | Learning/tutorials |
| **Count** | 151+ agents | 3 examples |
| **Organization** | By domain | By complexity |
| **Documentation** | Usage-focused | Tutorial-style |
| **Updates** | Continuous | Stable |
| **Use When** | Building real apps | Learning framework |

---

## 📚 Special Categories

### `/dspy_optimizers/`
Demonstration agents showing different DSPy optimizers:
- **GEPA** - Genetic-Pareto
- **SIMBA** - Stochastic Introspective Mini-Batch Ascent
- **MIPROv2** - Multi-step Instruction Prompt Optimization
- **BootstrapFewShot** - Basic few-shot learning
- And more...

**Use these to**: Learn about different optimization strategies

### `/explicit_agents/` ⭐
**Special category**: Agents demonstrating **explicit DSPy code generation** (no mixins!)
- **qa_bot** - Simple Q&A with Chain of Thought
- **rag_assistant** - RAG with ChromaDB integration
- **mcp_agent** - ReAct with tool usage

**Use these to**:
- Learn pure DSPy patterns
- See transparent code generation
- Understand SuperOptiX without vendor lock-in
- Run locally with Ollama (qwen3.5:2b)

**Why explicit?**:
- ✅ All logic inline and visible
- ✅ No mixin imports
- ✅ Standard DSPy patterns only
- ✅ Zero vendor lock-in
- ✅ Perfect for DSPy users

[Read more →](/superoptix/agents/explicit_agents/README.md)

### `/demo/`
Quick demo agents for rapid prototyping and testing

### `/testing/`
Agents specifically designed for testing and QA workflows

---

## 🔄 Workflow

```
Browse Marketplace → Pull Agent → Customize → Compile → Deploy
       ↓                ↓            ↓           ↓         ↓
  super market    super agent    Edit YAML   Generate   Production
     search          pull        playbook    Pipeline
```

---

## 🎓 Getting Started

### For Beginners
1. **Start with examples**: `/examples/explicit_dspy_agents/`
2. **Learn the basics**: Q&A Bot → RAG Assistant → MCP Agent
3. **Then explore marketplace**: Find domain-specific agents

### For Production
1. **Search marketplace**: Find agent matching your domain
2. **Pull and customize**: Adjust to your specific needs
3. **Compile and test**: Generate pipeline and validate
4. **Deploy**: Run in your environment

---

## 📖 Documentation

- [SuperSpec Format](../../docs/superspec.md) - Playbook configuration
- [Explicit DSPy Examples](../../examples/explicit_dspy_agents/) - Tutorial examples
- [CLI Reference](../../docs/cli.md) - Command-line usage
- [Tier System](../../docs/tiers.md) - Capability levels

---

## 🤝 Contributing Agents

Want to add your agent to the marketplace?

1. Create agent playbook following SuperSpec format
2. Test thoroughly with evaluation metrics
3. Document use cases and capabilities
4. Submit PR to appropriate domain directory

---

**Marketplace = Production | Examples = Learning**

**151+ Agents | 25+ Domains | Production-Ready**
