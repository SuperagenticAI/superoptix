# 🕵️‍♂️ Agent Discovery Guide

Agent discovery in SuperOptiX is all about **creating and exploring agent playbooks**-the heart of context engineering for your agents.

---

## 🧠 What is Agent Discovery?

Agent discovery means:
- Defining the **context, goals, and capabilities** your agent needs
- Engineering all relevant context, memory, tools, and RAG settings **in the playbook**
- Using the **SuperSpec DSL** to declaratively specify your agent's behavior, persona, and requirements

---

## 📒 The Agent Playbook (SuperSpec DSL)

- Every agent in SuperOptiX is defined by a **playbook** written in the SuperSpec DSL
- The playbook is where you do all your **context engineering**: persona, memory, tools, RAG, tasks, and more
- Playbooks are human-readable, versionable, and easy to modify

---

## 🛠️ Three Ways to Discover & Create Agent Playbooks

### 🏪 **Browse Prebuilt Agents & Tools (Marketplace)**

Discover ready-to-use agents and tools from the SuperOptiX marketplace.

#### Browse All Available Agents
```bash
super market browse agents
```

<details>
<summary>📋 Example Output</summary>

```
🤖 Marketplace: Agents
══════════════════════════════════════════════════

📊 Available Industries (22):
 • Agriculture Food     • Consulting         • Demo            
 • Education            • Energy Utilities   • Finance         
 • Gaming Sports        • Government Public  • Healthcare      
 • Hospitality Tourism  • Huggingface Demo   • Human Resources 
 • Legal                • Manufacturing      • Marketing       
 • Media Entertainment  • Mlx Demo           • Real Estate     
 • Retail               • Software           • Testing         
 • Transportation                                              

                                                             📋 Available Pre-built Agents                                                             
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Industry            ┃ Name                                ┃ ID                             ┃ Level   ┃ Type        ┃ Playbook Ref                   ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Software            │ Developer Assistant                 │ developer                      │ oracles │ Supervised  │ developer                      │
│ Software            │ DevOps Engineer Assistant           │ devops_engineer                │ oracles │ Supervised  │ devops_engineer                │
│ Software            │ Lightweight Developer Assistant     │ lightweight-developer          │ oracles │ Autonomous  │ lightweight_developer          │
│ Software            │ Performance Engineer Assistant      │ performance_engineer           │ oracles │ Supervised  │ performance_engineer           │
│ Software            │ Product Owner Assistant             │ product_owner                  │ oracles │ Supervised  │ product_owner                  │
│ Software            │ QA Engineer Assistant               │ qa_engineer                    │ oracles │ Supervised  │ qa_engineer                    │
│ Software            │ Scrum Master Assistant              │ scrum_master                   │ oracles │ Supervised  │ scrum_master                   │
│ Software            │ Security Engineer Assistant         │ security_engineer              │ oracles │ Supervised  │ security_engineer              │
│ Software            │ System Architect Assistant          │ system_architect               │ oracles │ Supervised  │ system_architect               │
│ Software            │ Technical Writer Assistant          │ technical_writer               │ oracles │ Supervised  │ technical_writer               │
└─────────────────────┴─────────────────────────────────────┴────────────────────────────────┴─────────┴─────────────┴────────────────────────────────┘

Found 119 pre-built agent(s)

🚀 Next Steps:
   super agent pull <playbook_ref>           - Add an agent to your project
   super agent list --pre-built --industry <name> - Filter by industry
   super agent design                        - Create a custom agent

💡 Example: super agent pull developer
```

</details>

#### Browse Available Tools
```bash
super market browse tools
```

<details>
<summary>🛠️ Example Output</summary>

```
🛠️ Marketplace: Tools
══════════════════════════════════════════════════
📂 Available Categories (3):
 • Core (6)  • Development (9)  • Data (1) 

                                                              🛠️ Available Tools                                                              
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                ┃ Category    ┃ Description                                           ┃ Industry   ┃ Tags                             ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ web_search          │ Core        │ Search the web for information using various searc... │ General    │ search, web, research            │
│ calculator          │ Core        │ Perform safe mathematical calculations and express... │ General    │ math, calculation, arithmetic    │
│ file_reader         │ Core        │ Read and process text files with safety restrictio... │ General    │ file, text, io                   │
│ datetime            │ Core        │ Get current time and format dates between differen... │ General    │ time, date, formatting           │
│ text_analyzer       │ Core        │ Analyze text for statistics, readability, and basi... │ General    │ text, analysis, nlp              │
│ json_processor      │ Core        │ Parse JSON and extract specific fields using dot n... │ General    │ json, parsing, data              │
│ code_formatter      │ Development │ Format code with basic syntax highlighting and str... │ Technology │ code, formatting, development    │
│ data_processor      │ Data        │ Process and analyze CSV data with various operatio... │ General    │ data, csv, analysis              │
│ git_analyzer        │ Development │ Analyze Git commit messages for best practices and... │ Technology │ git, version-control, commits    │
│ api_tester          │ Development │ Validate and analyze API responses for structure a... │ Technology │ api, testing, validation         │
│ database_query      │ Development │ Validate SQL queries for syntax and security issue... │ Technology │ sql, database, security          │
│ version_checker     │ Development │ Compare semantic versions and determine relationsh... │ Technology │ versioning, semver, comparison   │
│ dependency_analyzer │ Development │ Analyze package dependencies for security and upda... │ Technology │ dependencies, security, packages │
│ code_reviewer       │ Development │ Perform automated code review and quality analysis    │ Technology │ code-review, quality, analysis   │
│ test_coverage       │ Development │ Analyze test coverage reports and provide recommen... │ Technology │ testing, coverage, quality       │
│ docker_helper       │ Development │ Validate Dockerfiles for best practices and optimi... │ Technology │ docker, containers, devops       │
└─────────────────────┴─────────────┴───────────────────────────────────────────────────────┴────────────┴──────────────────────────────────┘

Found 16 tool(s)
```

</details>

#### Search for Specific Agents
```bash
super market search "Software"
```

<details>
<summary>🔍 Example Output</summary>

```
🔍 Marketplace Search: 'Software'
════════════════════════════════════════════════════════════
Found 10 result(s)

🤖 Agents
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                            ┃ Industry ┃ Type       ┃ Install                                               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ System Architect Assistant      │ Software │ Supervised │ super marketplace install agent system_architect      │
│ Product Owner Assistant         │ Software │ Supervised │ super marketplace install agent product_owner         │
│ Lightweight Developer Assistant │ Software │ Autonomous │ super marketplace install agent lightweight_developer │
│ Developer Assistant             │ Software │ Supervised │ super marketplace install agent developer             │
│ Scrum Master Assistant          │ Software │ Supervised │ super marketplace install agent scrum_master          │
└─────────────────────────────────┴──────────┴────────────┴───────────────────────────────────────────────────────┘
... and 5 more agents
```

</details>

**Benefits:**

- ⚡ **Fastest setup** - Get started in minutes

- 🛡️ **Battle-tested** - Pre-optimized and evaluated

- 📦 **No coding required** - Ready to use immediately

- 🔄 **Actively maintained** - Regular updates and improvements

### 📜 **Create Agents Using SuperSpec (CLI)**

Generate custom agent playbooks using the declarative SuperSpec DSL.

```bash
super spec generate <tier> <agent_name> [--rag]
```

**Examples:**
```bash
# Create a Genies-tier developer agent with RAG
super spec generate genies developer --rag

# Create an Oracles-tier research agent
super spec generate oracles research

# Create a basic Genies-tier agent
super spec generate genies assistant
```

<details>
<summary>📋 Example Output</summary>

```
📁 Using SuperOptiX project structure: demo_agent_discovery/agents/developer/playbook/developer_playbook.yaml
Generated genies agent playbook: /Users/super/agentic/SuperOptiX/demo_agent_discovery/agents/developer/playbook/developer_playbook.yaml
📋 Agent: Developer (Tier: genies)
🏷️  Namespace: software
⚡ Features: memory, tools, agentflow
```

</details>

**Benefits:**

- 🎯 **Full control** - Customize every aspect of your agent

- 📝 **Declarative** - SuperSpec DSL makes agent design transparent

- 🔧 **Optimization-ready** - Built-in DSPy optimization support

- 🏗️ **Production-ready** - Enterprise-grade quality and structure

### 🎨 **Create Agents Using Studio (UI)**

Use the visual SuperOptiX Agent Design Studio for interactive agent creation.

```bash
super agent design <agent_name>
```

**Examples:**
```bash
# Launch UI for Oracles-tier research agent
super agent design research

# Launch UI for Genies-tier developer agent
super agent design developer
```

<details>
<summary>🎨 Example Output</summary>

```
╭────────────────────────────────────────────────────────────────────── 🎨 Agent Design Studio ───────────────────────────────────────────────────────────────────────╮
│ 🚀 super Agent Designer                                                                                                                                             │
│                                                                                                                                                                     │
│ Agent: RESEARCH                                                                                                                                                     │
│ Tier: Oracles                                                                                                                                                       │
│ └── UI: http://localhost:8501                                                                                                                                       │
│                                                                                                                                                                     │
│ Starting designer... Use Ctrl+C to stop when done.                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Waiting for designer UI to launch...
Designer UI is ready!
🌐 Visit: http://localhost:8501

Designer is running. Press Ctrl+C here to stop the server.
```

</details>

**Benefits:**

- 🖱️ **Visual design** - Drag-and-drop interface

- 🔄 **Real-time preview** - See changes instantly

- 🎯 **Interactive** - Guided agent creation process

- 📱 **User-friendly** - No CLI knowledge required

**Note:** The UI is still evolving and may not be as fast or robust as the CLI approach.

---

## 🎯 **The Playbook: Your Agent's Foundation**

**No matter which method you choose, you'll end up with a playbook that needs context engineering.**

### 🚀 **Fastest Path: Marketplace Template + Hand Editing**

1. **Grab a template** from the marketplace that's close to your needs
2. **Edit by hand** to add your custom requirements and context
3. **Use SuperSpec DSL** to configure all the powerful features you need

### 🔧 **SuperSpec: Configure Everything**

Your playbook can include:

- 🧠 **Memory systems** - Short-term, long-term, and episodic memory

- 🛠️ **Tool integration** - Web search, file operations, code analysis

- 📚 **RAG capabilities** - Document ingestion and retrieval

- 🎭 **Persona definition** - Agent personality and behavior

- 📋 **Task specifications** - What your agent should do

- 🔒 **Safety constraints** - What your agent should NOT do

---

## 🌟 Why Agent Discovery Matters

- 🔍 **Context Engineering** - All agent intelligence starts with a well-crafted playbook

- 🧩 **Composable** - Playbooks can be reused, versioned, and shared

- 🏪 **Marketplace** - Instantly discover and adapt pre-built agents

- 📝 **Declarative** - SuperSpec DSL makes agent design transparent and auditable

- 🚀 **Customizable** - Modify any aspect of your agent's context, tools, or memory

---

## 🚫 What This Page Does NOT Cover

- This guide is **only about discovering and creating agent playbooks**
- For running, evaluating, compiling, or optimizing agents, see the other guides and tutorials

---

## 🎯 Next Steps

- Explore the marketplace for playbooks
- Use `super spec generate ...` to create your own
- Try the UI studio for visual design
- Edit and version your playbooks as your needs evolve

Agent discovery is the foundation of every great agentic system-start with a strong playbook, and everything else gets easier! 🚀 