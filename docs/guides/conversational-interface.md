# Conversational Interface

## 🎯 Overview

SuperOptiX features a conversational interface that makes it easy to interact with the framework through natural language and slash commands.

**Just type:**

```bash
super
```

That's it! No need for `super chat` or other subcommands.

---

## 🚀 Getting Started

### First Run

The first time you run `super`, you'll go through a quick setup:

```bash
$ super

🎉 Welcome to SuperOptiX!

First time setup - this will take about 30 seconds.

Step 1/2: Choose AI Model Provider

1. 🏠 Ollama (Local - FREE, Private, Offline)
2. ☁️  OpenAI (Cloud - Paid)
3. ☁️  Anthropic (Cloud - Paid)

Choose [1-3]: 1
```

**We recommend Ollama** for:
- ✅ Privacy (data stays local)
- ✅ No API costs (free)
- ✅ Offline capability

### After Setup

Once configured, just type `super` to enter conversational mode:

```bash
$ super

Welcome to SuperOptiX!
Using: ollama (llama3.1:8b)

Type /help for slash commands or just tell me what to do.

SuperOptiX> _
```

---

## 🎮 Slash Commands

Slash commands provide quick access to SuperOptiX features:

### Configuration & Models

```bash
/model                    # Show current model
/model list              # List all available models
/model set <model>       # Switch model
/config                  # Show configuration
/config show             # Show all settings
/config set <k> <v>      # Set configuration value
```

### Help & Documentation

```bash
/help                    # Show all commands
/ask <question>         # Ask about SuperOptiX
/help <topic>           # Topic-specific help
/docs <topic>           # Open documentation
/examples               # Show example workflows
```

### Project & Agents

```bash
/status                 # Show project status
/agents                 # List all agents
/playbooks              # List all playbooks
/templates              # Show available templates
```

### Conversation

```bash
/clear                  # Clear screen
/history                # Show conversation history (coming soon)
/exit, /quit            # Exit conversational mode
```

---

## 💬 Example Session

```bash
$ super

Welcome to SuperOptiX!
Using: ollama (llama3.1:8b)

SuperOptiX> /help

[Shows all slash commands]

SuperOptiX> /model list

Available AI Models

🏠 LOCAL MODELS (via Ollama):
✅ llama3.1:8b (current)
✅ qwen2.5:14b

☁️  CLOUD MODELS:
OpenAI: gpt-4o, gpt-4o-mini
Anthropic: claude-3.5-sonnet

SuperOptiX> /ask How do I add memory?

💡 How do I add memory to my agent?

To add memory to your agent, update your playbook's spec:

```yaml
spec:
  memory:
    enabled: true
    enable_context_optimization: true
    max_context_tokens: 2000
```

SuperOptiX> /agents

Agents

Found 2 agent(s):

  • code_reviewer
    ✅ Compiled
  • customer_support
    ⚠️  Not compiled

SuperOptiX> /playbooks

Available Playbooks

📦 Library Templates (5):
  • genie_playbook [memory, tools, rag]
    General-purpose intelligent agent...
  • security_agent_playbook [tools, rag]
    Code security review agent...

📁 Your Project (2):
  • code_reviewer_playbook [memory, tools]
  • customer_support_playbook [memory, rag]

SuperOptiX> /exit

👋 Goodbye! Happy building with SuperOptiX!
```

---

## 🔧 Model Management

### Viewing Models

```bash
SuperOptiX> /model

Current Model Configuration

• Provider: ollama
• Model: llama3.1:8b
• API Base: http://localhost:11434
• Status: ✅ Connected
```

### Switching Models

```bash
# Switch to different Ollama model
SuperOptiX> /model set qwen2.5:14b

✅ Switched to: qwen2.5:14b

# Switch to OpenAI (requires API key)
SuperOptiX> /model set gpt-4o

⚠️  OPENAI_API_KEY not set
Set it with: /config set OPENAI_API_KEY sk-...
```

### Listing All Models

```bash
SuperOptiX> /model list

Available AI Models

🏠 LOCAL MODELS (via Ollama):

Installed:
  ✅ llama3.1:8b (current)
  ✅ qwen2.5:14b

Available to install:
  • deepseek-coder:33b (19GB) - Best for coding
  • mistral:7b (4.1GB) - Fast alternative

Install: ollama pull <model>

─────────────────────────────────────

☁️  CLOUD MODELS:

OpenAI (Requires OPENAI_API_KEY):
  • gpt-4o - Best overall
  • gpt-4o-mini - Fast and affordable

Anthropic (Requires ANTHROPIC_API_KEY):
  • claude-3.5-sonnet - Best for coding
  • claude-3.5-haiku - Fast and affordable

Set API key: /config set OPENAI_API_KEY sk-...
```

---

## 🎓 Learning SuperOptiX

### Ask Questions

Use `/ask` to learn about SuperOptiX features:

```bash
SuperOptiX> /ask How do I add memory?
SuperOptiX> /ask What is GEPA?
SuperOptiX> /ask How do I add RAG?
SuperOptiX> /ask What is SuperSpec?
```

### View Examples

```bash
SuperOptiX> /examples

Example Workflows

1. Build and Optimize Agent:
   super spec generate genie code_reviewer
   super agent compile code_reviewer
   super agent optimize code_reviewer --auto medium

2. Quick Agent from Template:
   super agent pull developer
   super agent compile developer
   super agent run developer --goal "Build a CLI tool"
```

---

## 🔄 Backwards Compatibility

Traditional CLI commands still work:

```bash
# Traditional commands (no conversational mode)
$ super agent compile code_reviewer
$ super agent optimize code_reviewer --auto medium
$ super agent evaluate code_reviewer

# These bypass conversational mode and run directly
```

**When to use each:**

- **Conversational mode** (`super`): Interactive exploration, learning, quick tasks
- **Traditional CLI** (`super agent ...`): Scripts, CI/CD, automation

---

##  🔐 Configuration & Privacy

### Local Mode (Default)

- No authentication required
- All data stays on your machine
- Privacy-first

### Configuration Storage

```
~/.superoptix/
├── config.yaml          # Your model choice and settings
├── credentials.yaml     # API keys (encrypted)
└── history/            # Conversation history
```

### Changing Configuration

```bash
# View configuration
SuperOptiX> /config

# View detailed settings
SuperOptiX> /config show

# Set API keys
SuperOptiX> /config set OPENAI_API_KEY sk-...

# Reset configuration
SuperOptiX> /config reset
```

---

## 💡 Tips & Tricks

**1. Use /ask for Quick Help**
```bash
SuperOptiX> /ask memory
SuperOptiX> /ask RAG
SuperOptiX> /ask GEPA
```

**2. Discover Available Playbooks**
```bash
SuperOptiX> /playbooks
# Shows all library templates + your project playbooks
```

**3. Check Project Status**
```bash
SuperOptiX> /status
# Quick overview of your project
```

**4. Clear Screen**
```bash
SuperOptiX> /clear
# Clears conversation history
```

**5. Traditional CLI Still Works**
```bash
# Exit conversational mode
SuperOptiX> /exit

# Run traditional command
$ super agent compile code_reviewer

# Re-enter conversational mode
$ super
```

---

## 🚀 Coming Soon

**Natural Language Mode:**
```bash
SuperOptiX> Build a code review agent
SuperOptiX> Optimize my customer support agent
SuperOptiX> Show me optimization results
```

Currently in development! For now, use:
- Slash commands in conversational mode
- Traditional CLI for full functionality

---

## 🆘 Troubleshooting

### "Ollama not running"

**Solution:**
1. Install Ollama: https://ollama.com
2. Run: `ollama serve`
3. Install model: `ollama pull llama3.1:8b`

### "Not in a SuperOptiX project"

**Solution:**
```bash
# Exit conversational mode
SuperOptiX> /exit

# Initialize project
$ super init my_project
$ cd my_project

# Re-enter conversational mode
$ super
```

### "No agents found"

**Solution:**
```bash
SuperOptiX> /exit

# Create an agent
$ super spec generate genie code_reviewer

# Re-enter and check
$ super
SuperOptiX> /agents
```

---

## 📚 Learn More

- **Full documentation**: https://superoptix.ai
- **Getting started**: Run `super docs` for comprehensive guide
- **GitHub**: https://github.com/SuperagenticAI/superoptix

---

## ✨ Summary

**Just type `super`** - That's it!

- 🎮 Slash commands for quick access
- 💬 Ask questions with `/ask`
- 🔧 Manage models with `/model`
- 📋 Explore playbooks with `/playbooks`
- 🚀 Full backwards compatibility with traditional CLI

**Welcome to the future of SuperOptiX!** 🎉

