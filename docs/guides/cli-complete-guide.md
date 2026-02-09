# Complete CLI Usage Guide

**SuperOptiX CLI: Your Complete Command Reference**

Master the `super` CLI for building, optimizing, and deploying AI agents.

---

## Table of Contents

1. [Installation](#installation)
2. [Project Management](#project-management)
3. [Agent Commands](#agent-commands)
4. [Optimization Commands](#optimization-commands)
5. [Dataset Commands](#dataset-commands)
6. [Model Management](#model-management)
7. [Orchestra Commands](#orchestra-commands)
8. [Marketplace Commands](#marketplace-commands)
9. [Observability Commands](#observability-commands)
10. [Advanced Usage](#advanced-usage)

---

## Installation

### Quick Install (Recommended)

```bash
# Using uv (fastest)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install superoptix

# Verify installation
super --version
super --help
```

### Alternative Install (pip)

```bash
pip install superoptix
```

### Get Documentation

```bash
# Open comprehensive docs
super docs

# Show help for any command
super <command> --help
super agent compile --help
```

---

## Project Management

### `super init` - Initialize Project

```bash
# Create new project
super init my_project
cd my_project

# What gets created:
# my_project/
# ├── .super              # Project marker
# ├── agents/             # Agent playbooks
# ├── guardrails/         # Safety rules
# ├── memory/             # Memory modules
# ├── protocols/          # Communication protocols
# ├── teams/              # Multi-agent teams
# ├── evals/              # Evaluation results
# ├── knowledge/          # Knowledge bases
# ├── optimizers/         # Optimization data
# ├── servers/            # Server code
# └── tools/              # Custom tools
```

---

## Agent Commands

### `super agent list` - List Agents

```bash
# List all agents in current project
super agent list

# List pre-built demo agents
super agent list --pre-built

# List agents in specific directory
super agent list --directory ./agents/custom
```

### `super agent pull` - Download Demo Agents

```bash
# Pull demo agent from marketplace
super agent pull sentiment_analyzer      # DSPy demo
super agent pull assistant_openai        # OpenAI SDK demo
super agent pull researcher_crew         # CrewAI demo
super agent pull assistant_adk           # Google ADK demo
super agent pull assistant_microsoft     # Microsoft demo
super agent pull research_agent_deepagents  # DeepAgents demo

# Pull to specific directory
super agent pull sentiment_analyzer --output ./agents/demos/

# List available agents
super market browse agents
```

### `super agent compile` - Compile Agent

```bash
# Compile with default framework (DSPy)
super agent compile my_agent

# Compile with specific framework
super agent compile my_agent --framework dspy
super agent compile my_agent --framework openai
super agent compile my_agent --framework crewai
super agent compile my_agent --framework google-adk
super agent compile my_agent --framework microsoft
super agent compile my_agent --framework deepagents

# Compile with output path
super agent compile my_agent --output ./pipelines/

# Compile with verbose output
super agent compile my_agent --verbose

# Compile multiple agents
super agent compile agent1 agent2 agent3
```

### `super agent evaluate` - Evaluate Agent

```bash
# Evaluate agent (baseline)
super agent evaluate my_agent

# Evaluate optimized version
super agent evaluate my_agent  # automatically loads optimized weights

# Evaluate with specific dataset
super agent evaluate my_agent --dataset ./data/test.csv

# Evaluate with verbose output
super agent evaluate my_agent --verbose

# Save evaluation report
super agent evaluate my_agent --save-report results.json

# Evaluate with specific scenarios
super agent evaluate my_agent --scenarios "scenario1,scenario2"

# Evaluate in CI/CD pipeline
super agent evaluate my_agent --format json --exit-code
```

### `super agent optimize` - Optimize Agent

```bash
# Optimize with auto settings (recommended)
super agent optimize my_agent --auto light      # Quick (5 min)
super agent optimize my_agent --auto medium     # Balanced (15 min) ⭐ Recommended
super agent optimize my_agent --auto intensive  # Thorough (30+ min)

# Optimize with custom settings
super agent optimize my_agent \
  --optimizer GEPA \
  --iterations 10 \
  --metric answer_exact_match

# Optimize with specific LLM for reflection
super agent optimize my_agent \
  --auto medium \
  --reflection-lm qwen3:8b

# Fresh optimization (discard previous)
super agent optimize my_agent --auto medium --fresh

# Continue from previous optimization
super agent optimize my_agent --auto medium --resume

# Optimize with minibatch
super agent optimize my_agent \
  --auto medium \
  --minibatch-size 5

# Skip scenarios with perfect scores
super agent optimize my_agent \
  --auto medium \
  --skip-perfect-score
```

### `super agent run` - Run Agent

```bash
# Run agent interactively
super agent run my_agent

# Run with specific input
super agent run my_agent --goal "Analyze this text"

# Run with input from file
super agent run my_agent --goal "$(cat ./input.txt)"

# Run optimized version
super agent run my_agent  # automatically loads optimized weights

# Run with specific framework
super agent run my_agent --framework openai

# Run in batch mode
super agent run my_agent --batch ./inputs.jsonl

# Run with output to file
super agent run my_agent --goal "text" --output results.json
```

### `super agent design` - Design Agent (Studio)

```bash
# Launch Studio UI for agent design
super agent design

# Design options
super agent design --mode visual     # Visual builder
super agent design --mode code       # Code editor
super agent design                   # Default interactive mode

# Design in specific mode
super agent design --mode visual     # Visual builder
super agent design --mode code       # Code editor
```

---

## Optimization Commands

### `super spec generate` - Generate Agent from SuperSpec

```bash
# Generate agent from natural language description
super spec generate my_agent "Create a sentiment analyzer"

# Generate with template
super spec generate my_agent --template sentiment_analysis

# Generate with RAG
super spec generate my_agent "Q&A agent" --rag

# Generate with defaults
super spec generate my_agent "Research agent"

# Interactive generation
super spec generate
```

---

## Dataset Commands

### `super agent dataset` - Dataset Management

```bash
# Preview dataset
super agent dataset preview my_agent --limit 10

# Validate dataset configuration
super agent dataset validate my_agent

# Get dataset info
super agent dataset info my_agent

# Convert dataset format
super agent dataset convert \
  --input ./data/train.csv \
  --output ./data/train.jsonl \
  --format jsonl

# Split dataset
super agent dataset split \
  --input ./data/all.csv \
  --train ./data/train.csv \
  --test ./data/test.csv \
  --ratio 0.8

# Merge datasets
super agent dataset merge \
  --inputs data1.csv data2.csv data3.csv \
  --output combined.csv
```

---

## Model Management

### `super model` - Model Commands

```bash
# List installed models
super model list

# List all available models
super model list --all

# Install model
super model install llama3.1:8b
super model install llama3.1:8b --backend ollama

# Install with specific backend
super model install llama3.1:8b --backend mlx       # Apple Silicon
super model install llama3.1:8b --backend huggingface
super model install llama3.1:8b --backend lmstudio

# Get model info
super model info llama3.1:8b

# Start model server
super model server --port 11434
super model serve --backend ollama

# Remove model
super model remove llama3.1:8b
```

---

## Orchestra Commands

### `super orchestra` - Multi-Agent Orchestration

```bash
# Create orchestra
super orchestra create my_orchestra

# List orchestras
super orchestra list

# Run orchestra
super orchestra run my_orchestra

# Run with specific input
super orchestra run my_orchestra --goal "Complex task"

# Evaluate orchestra
super orchestra evaluate my_orchestra

# Optimize orchestra
super orchestra optimize my_orchestra --auto medium
```

---

## Marketplace Commands

### `super market` - Marketplace Operations

```bash
# Browse agents
super market browse agents

# Browse tools
super market browse tools

# Search marketplace
super market search "sentiment analysis"
super market search "RAG"

# Get agent details
super market info sentiment_analyzer

# Install agent from marketplace
super market install agent sentiment_analyzer

# Install tool from marketplace
super market install tool web_scraper

# List installed marketplace items
super market list --installed
```

---

## Observability Commands

### `super observe` - Observability

```bash
# Start observability dashboard
super observe

# View specific agent runs
super observe my_agent

# View with specific backend
super observe --backend mlflow
super observe --backend langfuse

# Export metrics
super observe export --format json --output metrics.json

# View logs
super observe logs my_agent

# View performance metrics
super observe metrics my_agent --window 7d
```

---

## Advanced Usage

### Chaining Commands

```bash
# Complete workflow in one go
super agent pull sentiment_analyzer && \
super agent compile sentiment_analyzer && \
super agent evaluate sentiment_analyzer && \
super agent optimize sentiment_analyzer --auto medium && \
super agent evaluate sentiment_analyzer && \
super agent run sentiment_analyzer
```

### Using Environment Variables

```bash
# Set model configuration
export SUPER_MODEL_PROVIDER=ollama
export SUPER_MODEL_NAME=llama3.1:8b
export SUPER_API_BASE=http://localhost:11434

# Set optimization settings
export SUPER_OPTIMIZER=GEPA
export SUPER_AUTO_MODE=medium

# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"

# Run with environment config
super agent optimize my_agent
```

### Batch Processing

```bash
# Process multiple agents
for agent in agent1 agent2 agent3; do
  super agent compile $agent
  super agent evaluate $agent
  super agent optimize $agent --auto medium
done

# Process with parallel execution
parallel super agent optimize {} --auto medium ::: agent1 agent2 agent3
```

### CI/CD Integration

```bash
# In your CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
name: Agent Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install SuperOptiX
        run: pip install superoptix
      
      - name: Compile Agent
        run: super agent compile my_agent
      
      - name: Evaluate Agent
        run: super agent evaluate my_agent --format json --exit-code
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: results.json
```

### Debugging

```bash
# Enable verbose output
super agent compile my_agent --verbose
super agent evaluate my_agent --verbose --debug

# Check logs
super observe logs my_agent --tail 100

# Dry run (show what would happen)
super agent compile my_agent --dry-run

# Show execution plan
super agent run my_agent --explain
```

---

## Common Workflows

### Workflow 1: Quick Start (New Agent)

```bash
# Initialize project
super init my_project && cd my_project

# Pull demo agent
super agent pull sentiment_analyzer

# Compile
super agent compile sentiment_analyzer

# Evaluate baseline
super agent evaluate sentiment_analyzer

# Optimize
super agent optimize sentiment_analyzer --auto medium

# Evaluate optimized
super agent evaluate sentiment_analyzer  # automatically loads optimized weights

# Run
super agent run sentiment_analyzer
```

### Workflow 2: Custom Agent Development

```bash
# Generate from description
super spec generate my_agent "Analyze customer reviews"

# Edit playbook (manual)
vim agents/my_agent/playbook/my_agent_playbook.yaml

# Compile and test
super agent compile my_agent
super agent evaluate my_agent

# Optimize
super agent optimize my_agent --auto medium

# Deploy
super agent run my_agent
```

### Workflow 3: Multi-Framework Comparison

```bash
# Compare same agent across frameworks
for fw in dspy openai crewai; do
  echo "Testing $fw..."
  super agent compile my_agent --framework $fw
  super agent evaluate my_agent
done
```

### Workflow 4: Dataset Import & Training

```bash
# Prepare dataset
cat > data/train.csv << EOF
text,label
"Great product!",positive
"Poor quality",negative
EOF

# Configure in playbook
# (add datasets: section)

# Preview
super agent dataset preview my_agent

# Compile with dataset
super agent compile my_agent

# Train with large dataset
super agent optimize my_agent --auto medium
```

---

## Configuration Files

### Global Config: `~/.superoptix/config.yaml`

```yaml
# Default settings
default_framework: dspy
default_optimizer: GEPA
auto_mode: medium

# Model settings
model:
  provider: ollama
  default_model: llama3.1:8b
  api_base: http://localhost:11434

# Optimization settings
optimization:
  default_iterations: 5
  minibatch_size: 3
  skip_perfect_score: true

# Observability
observability:
  backend: mlflow
  tracking_uri: http://localhost:5000
```

### Project Config: `.super/config.yaml`

```yaml
# Project-specific settings
project_name: my_project
default_agent: sentiment_analyzer

# Override global settings
default_framework: crewai
auto_mode: intensive
```

---

## Tips & Tricks

### Tip 1: Use Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias sac='super agent compile'
alias sae='super agent evaluate'
alias sao='super agent optimize'
alias sar='super agent run'

# Use them
sac my_agent && sae my_agent && sao my_agent --auto medium
```

### Tip 2: Quick Optimization Test

```bash
# Test optimization quickly
super agent optimize my_agent --auto light --limit 3
```

### Tip 3: Watch for Changes

```bash
# Auto-recompile on file changes
watch -n 2 'super agent compile my_agent'

# Or use entr
ls agents/my_agent/*.yaml | entr super agent compile my_agent
```

### Tip 4: Export Results

```bash
# Save evaluation results for comparison
super agent evaluate my_agent --save-report baseline.json
super agent optimize my_agent --auto medium
super agent evaluate my_agent --save-report optimized.json  # automatically loads optimized weights

# Compare
diff baseline.json optimized.json
```

---

## Troubleshooting

### Command Not Found

```bash
# Check installation
which super
uv pip list | grep superoptix

# Reinstall
uv pip install --upgrade superoptix
```

### Permission Denied

```bash
# Run with proper permissions
chmod +x $(which super)

# Or use full path
python -m superoptix.cli.main
```

### API Rate Limits

```bash
# Use local models
export SUPER_MODEL_PROVIDER=ollama

# Reduce optimization intensity
super agent optimize my_agent --auto light
```

---

## Getting Help

```bash
# General help
super --help

# Command-specific help
super agent --help
super agent compile --help
super agent optimize --help

# Show version
super --version
super -v

# Check documentation
super docs
```

---

## Next Steps

- [Multi-Framework Guide](multi-framework.md)
- [GEPA Optimization](gepa-optimization.md)
- [Dataset Import](dataset-import.md)
- [SuperSpec DSL](superspec.md)

---

**Status**: Complete CLI Reference **Commands**: All major commands documented **Examples**: Practical workflows included 