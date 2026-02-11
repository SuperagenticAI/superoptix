# 💬 Super CLI - Conversational Interface (Beta)

**AI-Powered Command-Line Interface for SuperOptiX**

Experience a new way to interact with SuperOptiX through natural language and intelligent automation.

---

## 🎯 Overview

**Super CLI** is SuperOptiX's conversational interface that combines:

- **Natural Language Understanding** - Talk to SuperOptiX naturally
- **Intelligent Command Generation** - AI translates your intent to commands
- **MCP Client Integration** - Built-in Model Context Protocol support
- **Model Flexibility** - Switch between Ollama, OpenAI, Anthropic models
- **Beautiful UI** - Engaging animations and visual feedback

!!! info "Beta Feature"
    Super CLI is currently in **beta**. We're actively improving the experience based on user feedback!

---

## 🚀 Getting Started

### Launch Super CLI

```bash
# Just type 'super' with no arguments
super
```

**You'll see:**
```
✨ Welcome to Super CLI [BETA] ✨

┌─────────────────────────────────────┐
│  Super CLI                          │
│  The Official SuperOptiX CLI        │
│  Using: ollama (gpt-oss:120b)       │
└─────────────────────────────────────┘

┌──────── 💡 Quick Start ─────────────┐
│ Essential Commands:                 │
│   /help     Full command reference  │
│   /ask      Ask questions           │
│   /model    List models             │
│   /mcp      MCP server status       │
│   /exit     Exit CLI                │
│                                     │
│ Natural Language:                   │
│   "Build a developer agent"         │
│   "Evaluate my agent"               │
│   "Optimize with GEPA"              │
└─────────────────────────────────────┘

┌─ 💬 Message ─────────────────────────────────────────┐
│ ▶ _
└──────────────────────────────────────────────────────┘
```

---

## 💬 Natural Language Mode

### Just Type What You Want

Super CLI understands natural language and translates it to the right commands.

**Examples:**

```bash
# Build an agent
SuperOptiX › build a developer agent

✨ Let me cook...
  ✓ Understood: build (developer)
🔧 Preparing the perfect command...
  ✓ Generated 1 command(s)
🚀 Launching your request...
Agent created successfully!
```

```bash
# Evaluate an agent
SuperOptiX › evaluate my customer support agent

🤔 Analyzing your request...
  ✓ Understood: evaluate (customer_support)
⚙️ Tuning parameters...
  ✓ Generated 1 command(s)
⚡ Running the command...
Evaluation complete!
```

```bash
# Optimize with GEPA
SuperOptiX › optimize the code review agent with GEPA

💡 Got an idea...
  ✓ Understood: optimize (code_review)
🗺️ Charting the course...
  ✓ Generated 1 command(s)
🧠 AI at work...
Optimization complete!
```

### Supported Intents

| What You Say | What It Does |
|--------------|--------------|
| "build/create a <name> agent" | Generates agent with SuperSpec |
| "compile <name>" | Compiles agent playbook to pipeline |
| "evaluate/test <name>" | Runs BDD evaluation |
| "optimize <name>" | Optimizes agent with GEPA |
| "run <name> with <goal>" | Executes agent with goal |
| "list agents" | Shows available agents |
| "show config" | Displays configuration |

---

## 🔧 Slash Commands

### Core Commands

```bash
# Get help
SuperOptiX › /help

# Ask questions about SuperOptiX
SuperOptiX › /ask how does GEPA optimization work?

# List available models
SuperOptiX › /model list

# Switch models
SuperOptiX › /model set gpt-4o-mini

# Show configuration
SuperOptiX › /config

# Exit
SuperOptiX › /exit
```

### Agent Management

```bash
# List marketplace agents
SuperOptiX › /agents

# List compiled playbooks in current project
SuperOptiX › /playbooks
```

### MCP Commands

```bash
# Check MCP server status
SuperOptiX › /mcp status

# List MCP servers
SuperOptiX › /mcp list

# Show available MCP tools
SuperOptiX › /mcp tools

# Add MCP server
SuperOptiX › /mcp add

# Enable/disable server
SuperOptiX › /mcp enable <server_name>
SuperOptiX › /mcp disable <server_name>
```

### Utility Commands

```bash
# Show conversation history
SuperOptiX › /history

# Clear screen
SuperOptiX › /clear
```

---

## 🤖 Model Management

### Built-in Support for Multiple Providers

**Local Models (Ollama):**
- `llama3.2:1b`, `llama3.2:3b`
- `gpt-oss:20b`, `gpt-oss:120b`
- `qwen2.5-coder:7b`
- Any Ollama model

**Cloud Models (OpenAI):**
- `gpt-4o`, `gpt-4o-mini`
- `gpt-3.5-turbo`

**Cloud Models (Anthropic):**
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`

### List Available Models

```bash
SuperOptiX › /model list
```

**Output:**
```
🤖 Available Models

Local Models (Ollama):
  • llama3.2:1b           Fast, lightweight
  • gpt-oss:120b         Powerful reasoning
  • qwen2.5-coder:7b     Code specialist

Cloud Models (OpenAI):
  • gpt-4o-mini          Cost-effective, fast
  • gpt-4o               Most capable

Cloud Models (Anthropic):
  • claude-3-5-sonnet    Best for complex tasks
```

### Switch Models

```bash
# Switch to local model
SuperOptiX › /model set gpt-oss:120b

# Switch to cloud model
SuperOptiX › /model set gpt-4o-mini
```

**Notes:**
- Model used for CLI conversation only
- Agents use their playbook-specified models
- No interference between CLI and agent models

---

## 🔧 MCP Client Features

### What is MCP?

**Model Context Protocol** - Industry standard for connecting AI models to external tools and data sources.

SuperOptiX Super CLI acts as an **MCP client**, allowing you to:
- Connect to MCP servers (filesystem, databases, APIs)
- Use MCP tools for knowledge access
- Manage server configurations
- Monitor server status

### Check MCP Status

```bash
SuperOptiX › /mcp status
```

**Output:**
```
🔧 MCP Client Status

Status: Ready 
Active Servers:
  • filesystem - Local file access
    Status: Connected     Tools: 3 available

Available Tools:
  • read_file(path) - Read file contents
  • write_file(path, content) - Write to file
  • list_directory(path) - List files in directory
```

### Manage MCP Servers

```bash
# List configured servers
SuperOptiX › /mcp list

# Add a server
SuperOptiX › /mcp add
# Interactive wizard will guide you

# Enable/disable server
SuperOptiX › /mcp enable filesystem
SuperOptiX › /mcp disable database
```

### MCP Tools

```bash
# List available tools
SuperOptiX › /mcp tools

# Tools are automatically used by Super CLI when relevant
# For example, when you ask about code, it can read files via MCP
```

---

## 🎨 Visual Features

### Engaging Animations

**58+ Rotating Messages** keep the experience fresh:

**Thinking Phase:**
- "✨ Let me cook..."
- "🧠 Neurons firing..."
- "💫 Channeling the AI spirits..."
- "🔮 Figuring this out..."
- And 26+ more!

**Preparing Phase:**
- "🔧 Preparing the perfect command..."
- "🗺️ Charting the course..."
- "🎯 Aiming for perfection..."
- And 5+ more!

**Executing Phase:**
- "🚀 Launching your request..."
- "🔥 Executing with style..."
- "⚡ Zapping it into existence..."
- And 17+ more!

### Progressive Status

```
✨ Let me cook...

  ✓ Understood: build (developer)

🔧 Preparing the perfect command...

  ✓ Generated 1 command(s)

🚀 Launching your request...

Success!
```

**Smooth, continuous animations until each step completes!**

---

## ⚙️ Configuration

### First-Time Setup

**Super CLI runs a setup wizard on first launch:**

```bash
super
```

**You'll configure:**
1. **Model Provider** - Ollama (local) or OpenAI/Anthropic (cloud)
2. **Default Model** - Which model to use for conversations
3. **API Keys** - For cloud providers (optional)

**Wizard saves to:** `~/.superoptix_config.json`

### View Configuration

```bash
SuperOptiX › /config
```

**Shows:**
- Current model provider
- Active model
- API key status (masked)
- MCP server status

### Change Model

```bash
# Switch model anytime
SuperOptiX › /model set gpt-4o-mini

Switched to: gpt-4o-mini
   Provider: openai
```

---

## 🧠 Knowledge Base

### Ask About SuperOptiX

Super CLI has built-in knowledge about SuperOptiX features:

```bash
SuperOptiX › /ask how does GEPA optimization work?
```

**Gets answers from:**
1. **Curated Knowledge** - Pre-built Q&A (12 topics)
2. **Documentation** - Direct access to docs/ files
3. **MCP Tools** - Filesystem access for examples and code

**Topics covered:**
- Memory optimization
- RAG setup
- Tool integration
- GEPA algorithm
- SuperSpec DSL
- Agent tiers
- Compilation process
- Evaluation methods
- Optimization levels
- CLI commands
- Fresh flag usage
- Multi-agent orchestration

---

## 🎯 Use Cases

### Quick Prototyping

```bash
SuperOptiX › build a customer support agent for e-commerce

✨ Working on it...
Agent created successfully!

SuperOptiX › compile it

🔧 Assembling the pieces...
Compiled!

SuperOptiX › evaluate the agent

🚀 Launching evaluation...
Evaluation complete!
Score: 85%
```

### Iterative Optimization

```bash
SuperOptiX › optimize customer_support with GEPA at high level

🧠 AI at work...
Optimization complete!
Best score: 92%

SuperOptiX › evaluate it again

⚡ Running the command...
Evaluation complete!
Score: 92% (improved 7%!)
```

### Multi-Agent Workflows

```bash
SuperOptiX › create a software development team

💡 Got an idea...
Created developer, qa_engineer, devops_engineer

SuperOptiX › compile all of them

🔨 Building it now...
All agents compiled!

SuperOptiX › create an orchestra for them

🎵 Orchestrating the plan...
Orchestra created!
```

---

## 📖 Command Reference

### Natural Language

| Command Pattern | Example | What It Does |
|----------------|---------|--------------|
| `build/create <name>` | "build a developer agent" | Generate agent with SuperSpec |
| `compile <name>` | "compile developer" | Compile playbook to pipeline |
| `evaluate <name>` | "evaluate my agent" | Run BDD tests |
| `optimize <name>` | "optimize with GEPA" | GEPA optimization |
| `run <name> with <goal>` | "run developer with goal X" | Execute agent |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Full command reference with examples |
| `/ask <question>` | Ask about SuperOptiX features |
| `/model list` | List available models |
| `/model set <name>` | Switch to different model |
| `/config` | Show current configuration |
| `/agents` | List marketplace agent templates |
| `/playbooks` | List compiled playbooks (requires project) |
| `/mcp status` | Check MCP server status |
| `/mcp list` | List MCP servers |
| `/mcp tools` | Show available MCP tools |
| `/history` | Show conversation history |
| `/clear` | Clear screen |
| `/exit` or `/quit` | Exit Super CLI |

---

## 🔒 Security & Privacy

### Local-First by Default

**Super CLI prioritizes local models:**
- Uses Ollama by default (runs on your machine)
- No data sent to cloud unless you choose cloud models
- MCP servers run locally
- All data stays on your machine

### Cloud Models (Optional)

**If you choose OpenAI or Anthropic:**
- Your conversations go to their APIs
- You control the API keys
- Keys stored locally in `~/.superoptix_config.json`
- You can delete anytime

### MCP Security

**MCP servers have controlled access:**
- Filesystem server: Read/write permissions you grant
- Each server can be enabled/disabled
- Full audit trail of tool usage
- You control what data is accessible

---

## 🎨 Visual Features

### Animations

**Continuous feedback during processing:**
- Thinking animations while parsing intent
- Preparing animations while generating commands
- Executing animations while running commands
- Smooth transitions between steps

**58+ rotating messages:**
- "✨ Let me cook..."
- "🧠 Neurons firing..."
- "🔥 Warming up the engines..."
- Different every time for engagement!

### Clean Output

**Focus on results, not technical details:**
- Success indicators
- Clear error messages
- 📊 Relevant information only
- No command clutter

---

## ⚙️ Advanced Features

### Conversation Context

**Super CLI remembers your session:**
- Recent interactions
- Current agent you're working on
- Project state

**Example:**
```bash
SuperOptiX › build a developer agent
Created!

SuperOptiX › compile it
# Knows "it" refers to developer agent
Compiled!

SuperOptiX › evaluate
# Knows which agent to evaluate
Evaluated!
```

### Hybrid Knowledge Access

**Super CLI uses multiple knowledge sources:**

1. **Curated Q&A** - Pre-built answers for common questions
2. **Documentation Access** - Reads from docs/ directory
3. **MCP Tools** - Filesystem access for examples and code

**Combines all three for comprehensive answers!**

### Model Isolation

**Important:** Super CLI's model is separate from agent models!

- **CLI model:** Used for conversation and intent parsing
- **Agent models:** Specified in playbooks, used during execution

**No interference:** Changing CLI model doesn't affect your agents!

---

## 🚀 Best Practices

### Choose the Right Model

**For CLI Conversation:**
- **Local (Ollama):** `gpt-oss:120b` - Great balance of speed and capability
- **Cloud (OpenAI):** `gpt-4o-mini` - Fast and cost-effective
- **Cloud (Anthropic):** `claude-3-5-sonnet` - Best for complex reasoning

**For Agents:**
- Configure in playbook YAML
- Can use different model than CLI
- Independent of CLI model choice

### Use Natural Language

**Good:**
- "build a developer agent"
- "evaluate my agent"
- "optimize with GEPA at high level"

**Also works (slash commands):**
- "/agents" - Quick reference
- "/help" - Full documentation
- "/ask <question>" - Specific questions

### Leverage MCP

**Enable filesystem server:**
```bash
SuperOptiX › /mcp status
SuperOptiX › /mcp enable filesystem
```

**Now Super CLI can:**
- Read your code files
- Access examples
- Provide context-aware answers

---

## 🔧 Troubleshooting

### CLI Won't Start

**Check installation:**
```bash
uv pip show superoptix | grep Version
# Should show: Version: 0.1.2 or higher
```

**Reinstall if needed:**
```bash
uv pip install --upgrade superoptix
```

### Model Not Found

**For Ollama models:**
```bash
# List available
ollama list

# Pull model if needed
ollama pull gpt-oss:120b
```

**For cloud models:**
```bash
# Set API key
export OPENAI_API_KEY=your-key
# Or configure in setup wizard
```

### MCP Server Not Working

**Check server status:**
```bash
SuperOptiX › /mcp status
```

**Restart server:**
```bash
SuperOptiX › /mcp disable filesystem
SuperOptiX › /mcp enable filesystem
```

---

## 📊 Comparison: Traditional CLI vs Super CLI

| Feature | Traditional CLI | Super CLI |
|---------|----------------|-----------|
| **Syntax** | Exact commands required | Natural language |
| **Examples** | `super spec generate genies dev --namespace software` | "build a developer agent" |
| **Learning Curve** | Medium (learn commands) | Low (just talk) |
| **Flexibility** | Fixed syntax | Understands variations |
| **Feedback** | Text output | Animated, visual |
| **Model Support** | Agent models only | CLI + Agent models |
| **MCP** | Manual integration | Built-in client |
| **Knowledge** | External docs | Built-in Q&A + docs |

**Both available - use what fits your workflow!**

---

## 🎯 Common Workflows

### Build → Compile → Evaluate → Optimize

```bash
SuperOptiX › build a developer agent
Created!

SuperOptiX › compile it
Compiled!

SuperOptiX › evaluate the agent
Evaluated! Score: 78%

SuperOptiX › optimize with GEPA
Optimized! Score: 91%

SuperOptiX › evaluate again
Evaluated! Score: 91%
```

### Agent Discovery

```bash
SuperOptiX › /agents
📦 Available Agents

🔹 Software Development
  • developer, qa_engineer, devops_engineer

🔹 Customer Support
  • customer_support, sales_agent

SuperOptiX › /ask tell me about the developer agent
📚 The developer agent...
```

### MCP Integration

```bash
SuperOptiX › /mcp status
🔧 MCP Client Ready 
SuperOptiX › /ask show me an example of RAG optimization
📚 Reading from docs/guides/rag.md...
(Uses MCP filesystem access)
```

---

## 🔮 Future Enhancements

### Coming Soon

- 🎯 Multi-turn conversations (context across sessions)
- 🧠 Learning from your patterns
- 🔌 More MCP server integrations
- 🌐 Remote MCP server support
- 📊 Visual dashboards in terminal
- 🎨 Customizable themes
- 🗣️ Voice input support

### Feedback Welcome!

Super CLI is in beta - we want your input!

- 💬 Join our Discord: [SuperagenticAI](https://discord.gg/superagentic)
- 🐛 Report issues: [GitHub Issues](https://github.com/SuperagenticAI/superoptix/issues)
- 💡 Feature requests: [Discussions](https://github.com/SuperagenticAI/superoptix/discussions)

---

## 📖 Related Documentation

- [CLI Complete Guide](cli-complete-guide.md) - Traditional CLI reference
- [MCP Tools Guide](mcp-tools.md) - MCP integration details
- [GEPA Optimization](gepa-optimization.md) - Optimization strategies
- [Agent Development](../tutorials/first-agent.md) - Building agents

---

## ✨ Summary

**Super CLI brings conversational AI to your terminal:**

- 💬 Natural language - just talk
- 🤖 Model flexibility - local or cloud
- 🔧 MCP client - built-in tool access
- 🎨 Beautiful UI - engaging animations
- 📚 Knowledge access - built-in docs
- 🚀 Production ready - stable and tested

**Experience the future of AI development tools!**

```bash
super  # Launch and explore!
```