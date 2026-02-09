# 🐍 Pydantic AI MCP Demo

**Step-by-step guide to using MCP (Model Context Protocol) with Pydantic AI in SuperOptiX.**

This demo shows how to:
1. Set up a simple MCP server
2. Configure MCP in your playbook
3. Compile and run a Pydantic AI agent with MCP tools
4. Optimize MCP tool descriptions with GEPA

**Tested and Working with `llama3.1:8b` on local Ollama!** 🎉

---

## Prerequisites

```bash
# Install SuperOptiX with Pydantic AI
pip install superoptix[frameworks-pydantic-ai]

# Install MCP SDK (included with pydantic-ai, but ensure it's there)
pip install mcp

# Node.js (for filesystem MCP server)
node --version  # Should be 18+
npx --version   # Required for running MCP servers

# Ollama (for local model inference)
ollama pull llama3.1:8b
```

---

## Quick Start: Pull the MCP Demo Agent

The fastest way to try MCP with Pydantic AI:

```bash
# Initialize project
super init swe
cd swe

# Pull the pre-configured MCP demo agent
super agent pull pydantic-mcp

# Compile with Pydantic AI framework
super agent compile pydantic-mcp --framework pydantic-ai

# Test it!
super agent run pydantic-mcp --goal "List all files in /private/tmp"
```

**Expected Output:**
```
Using model: llama3.1:8b
🛠️  Initialized MCP stdio server: filesystem
Initialized 1 MCP server(s)
🚀 Running agent with input: List all files in /tmp
Model response received

┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Aspect   ┃ Value                                        ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Response │ The files in the /private/tmp directory are: │
│          │ * node-compile-cache (directory)             │
│          │ * test.txt (file)                            │
│          │ * ... more files ...                         │
└──────────┴──────────────────────────────────────────────┘
```

---

## Demo: Filesystem MCP Server (Step by Step)

### Step 1: Initialize Project

```bash
# Create a new project
super init swe
cd swe
```

### Step 2: Pull the MCP Demo Agent

```bash
super agent pull pydantic-mcp
```

This creates:
```
swe/agents/pydantic-mcp/
├── playbook/
│   └── pydantic_mcp_playbook.yaml  # MCP configuration included!
└── pipelines/
    └── (generated after compile)
```

> **Important:** The playbook filename should use underscores (`pydantic_mcp_playbook.yaml`), not hyphens. The generated pipeline expects this naming convention.

### Step 3: Review the MCP Configuration

The `pydantic_mcp_playbook.yaml` includes:

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b  # Works great with 8b models!
    api_base: http://localhost:11434
  
  # MCP Integration
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: npx
          args:
            - "-y"
            - "@modelcontextprotocol/server-filesystem"
            - "/private/tmp"  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: fs_  # Tools become: fs_read_file, fs_write_file, etc.
```

### Step 4: Compile with Pydantic AI

```bash
super agent compile pydantic-mcp --framework pydantic-ai
```

**Expected output:**
```
🔨 Compiling agent 'pydantic-mcp'...
🚀 Compiling with PYDANTIC-AI framework...
Successfully compiled with PYDANTIC-AI framework
🎉 COMPILATION SUCCESSFUL! Pipeline Generated
```

### Step 5: Test MCP Operations

Create a test file first:
```bash
echo "Hello from MCP test file!" > /private/tmp/test.txt
```

**Test 1: List Files**
```bash
super agent run pydantic-mcp --goal "List all files in /private/tmp"
```

**Test 2: Read a File**
```bash
super agent run pydantic-mcp --goal "Read the file at /private/tmp/test.txt"
```

**Expected output:**
```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Aspect   ┃ Value                                                             ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Response │ The contents of the file at /private/tmp/test.txt have been read          │
│          │ successfully. The output is:                                      │
│          │                                                                   │
│          │ "Hello from MCP test file!"                                       │
└──────────┴───────────────────────────────────────────────────────────────────┘
```

**Test 3: Write a File**
```bash
super agent run pydantic-mcp --goal "Create a file /private/tmp/mcp_demo.txt with content: MCP demo successful!"
```

**Verify:**
```bash
cat /private/tmp/mcp_demo.txt
# Output: MCP demo successful!
```

---

## MCP Tools Available

With the filesystem MCP server, your agent has access to these tools:

| Tool | Description |
|------|-------------|
| `fs__list_directory` | List files and directories |
| `fs__read_text_file` | Read text file contents |
| `fs__write_text_file` | Write/create text files |
| `fs__create_directory` | Create new directories |
| `fs__move_file` | Move/rename files |

> **Note:** Tool names have double underscore (`__`) between prefix and name due to how Pydantic AI processes the MCP server tools.

---

## Custom Agent with MCP (Manual Setup)

If you want to add MCP to your own agent:

### Step 1: Create or Edit Your Playbook

Add the `mcp` section to any playbook:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: My MCP Agent
  id: my_mcp_agent
  
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  
  input_fields:
    - name: query
      type: string
      description: User's request
  
  output_fields:
    - name: response
      type: string
      description: Agent's response
  
  persona:
    role: File Operations Assistant
    goal: Help users with file system operations using MCP tools
    backstory: You are an assistant with filesystem access through MCP.
  
  # Add MCP Configuration
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: npx
          args:
            - "-y"
            - "@modelcontextprotocol/server-filesystem"
            - "/private/tmp"  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: fs_
```

### Step 2: Save with Correct Filename

Save as `my_mcp_agent_playbook.yaml` (using underscores).

> **Important:** The playbook filename should match the pattern `{agent_id}_playbook.yaml` using underscores.

---

## Demo: Python-Based MCP Server (No Node.js Required!)

If you don't have Node.js, you can create a simple Python MCP server:

### Create Simple Calculator MCP Server

Create `simple_calculator_server.py`:

```python
#!/usr/bin/env python3
"""Simple calculator MCP server for demo."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

if __name__ == "__main__":
    mcp.run()
```

Make it executable:
```bash
chmod +x simple_calculator_server.py
```

### Configure in Playbook

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: calculator
        type: stdio
        config:
          command: "python3"
          args: ["simple_calculator_server.py"]
        tool_prefix: "calc_"
```

Now the agent has access to `calc_add`, `calc_multiply`, `calc_subtract` tools!

---

## Demo: MCP Tool Optimization

### Step 1: Enable Tool Optimization

Edit your playbook to enable MCP tool description optimization:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        tool_prefix: "fs_"  # Runtime prefix (optional)
    
    # Enable tool optimization
    optimization:
      optimize_tool_descriptions: true
      # IMPORTANT: Use actual MCP server tool names (WITHOUT prefix)
      # The optimizer queries the server directly
      tool_names: ["read_file", "write_file", "list_directory"]
```

> **Important:** The `tool_names` must match the actual MCP server tool names, **not** the prefixed names. The optimizer queries the MCP server directly, which returns unprefixed tool names like `read_file`, `write_file`, `list_directory`.

### Step 2: Add BDD Scenarios for Tool Usage

Add scenarios that use MCP tools:

```yaml
feature_specifications:
  scenarios:
    - name: read_file_scenario
      input:
        feature_requirement: Read the file /tmp/config.json and tell me what database host it specifies
      expected_output:
        implementation: read_file fs_read_file /tmp/config.json database host config
```

### Step 3: Optimize

> ⚠️ **IMPORTANT: Resource & Cost Warning**
> 
> **Optimization is resource-intensive and makes many LLM API calls:**
> - Requires **high-end GPU** or cloud GPU access
> - Makes **many LLM API calls** (20-100+ depending on settings)
> - Can incur **significant costs** with cloud models (GPT-4, Claude)
> - **RECOMMENDED:** Use local `ollama/llama3.1:8b` to avoid API charges
> 
> **MCP optimization runs TWO phases**, effectively doubling resource usage.

**Quick Test (Super Light - ~1-2 minutes, ~20 API calls):**
```bash
# Use local Ollama for free optimization
super agent optimize developer \
  --framework pydantic-ai \
  --max-metric-calls 20 \
  --reflection-lm ollama/llama3.1:8b
```

> **Note:** Use `--max-metric-calls 20` instead of `--max-full-evals 1` for more precise control over total evaluations.

**Recommended (Light Mode - ~5-10 minutes, ~50-100 API calls):**
```bash
# Use local Ollama (free) instead of cloud models (costly)
super agent optimize developer \
  --framework pydantic-ai \
  --auto light \
  --reflection-lm ollama/llama3.1:8b
```

**What happens:**
1. **Phase 1**: GEPA optimizes MCP tool descriptions (e.g., how `read_file` is described)
2. **Phase 2**: GEPA optimizes agent instructions

**Results saved to:**
- `swe/agents/developer/optimized/developer_mcp_tool_descriptions.json`
- `swe/agents/developer/optimized/developer_pydantic_ai_optimized.json`

---

## Complete Example Playbook

Here's a complete playbook with MCP enabled:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Developer Assistant with MCP
  id: developer_mcp
  namespace: software
  version: 1.0.0
  level: genies

spec:
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  
  input_fields:
    - name: feature_requirement
      type: str
      description: Feature to implement
  
  output_fields:
    - name: implementation
      type: str
      description: Code implementation
  
  persona:
    role: Software Developer
    goal: Write clean, efficient code with file system access
  
  # MCP Configuration
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS
        tool_prefix: "fs_"  # Runtime prefix (tools become fs__read_file at runtime)
    
    # Tool optimization - use actual MCP server tool names (WITHOUT prefix)
    optimization:
      optimize_tool_descriptions: true
      tool_names: ["read_file", "write_file", "list_directory"]
  
  feature_specifications:
    scenarios:
      - name: read_config_file
        input:
          feature_requirement: Read /private/tmp/config.json and extract the database URL
        expected_output:
          implementation: read_file config.json database URL extract
  
  optimization:
    optimizer:
      name: GEPA
      params:
        reflection_lm: ollama/llama3.1:8b  # Use forward slash for LiteLLM
        auto: light
```

---

## Testing the Demo

### Compile

```bash
super agent compile developer_mcp --framework pydantic-ai
```

**Verify MCP initialization:**
- Look for: `🛠️  Initialized MCP stdio server: filesystem`
- Look for: `Initialized 1 MCP server(s)`

### Run with File Operations

```bash
# Create a test file first
echo '{"db_host": "localhost", "db_port": 5432}' > /private/tmp/config.json

# Run agent
super agent run developer_mcp \
  --goal "Read /private/tmp/config.json and tell me what database port is configured"
```

**Expected behavior:**
- Agent uses `fs_read_file` tool
- Reads the file
- Returns the database port

### Evaluate

```bash
super agent evaluate developer_mcp
```

### Optimize (if enabled)

> ⚠️ **Resource Warning:** MCP tool optimization runs **two phases** (tools + instructions), effectively doubling resource usage. Only run if you have adequate GPU/compute resources.

**Quick Test (Super Light - ~1-2 minutes, ~20 API calls):**
```bash
# RECOMMENDED: Use local Ollama to avoid API costs
super agent optimize developer_mcp \
  --framework pydantic-ai \
  --max-metric-calls 20 \
  --reflection-lm ollama/llama3.1:8b
```

> **Note:** `--max-metric-calls 20` provides more precise control than `--max-full-evals 1`.
> 
> **Cost Tip:** Local Ollama models are free. Cloud models (GPT-4, Claude) will incur charges (~$0.50-10+ per optimization run).

**Recommended (Light Mode - ~5-10 minutes, ~50-100 API calls):**
```bash
# Use local Ollama (free) instead of cloud models (costly)
super agent optimize developer_mcp \
  --framework pydantic-ai \
  --auto light \
  --reflection-lm ollama/llama3.1:8b  # Use forward slash for LiteLLM
```

---

## Troubleshooting

### MCP Server Not Starting

**Error:** `Failed to initialize MCP server` or no "🛠️ Initialized MCP stdio server" message

**Solutions:**

1. **Check Node.js/npx:**
   ```bash
   which npx
   npx --version
   # Should be available
   ```

2. **Test the MCP server manually:**
   ```bash
   npx -y @modelcontextprotocol/server-filesystem /private/tmp
   # Should output: "Secure MCP Filesystem Server running on stdio"
   # Note: On macOS, use /private/tmp (or /tmp on Linux)
   ```

3. **Check playbook filename:**
   - Use underscores: `pydantic_mcp_playbook.yaml`    - Not hyphens: `pydantic-mcp_playbook.yaml` 
4. **Verify MCP config is correct:**
   ```yaml
   mcp:
     enabled: true  # Must be true!
     servers:
       - name: filesystem
         type: stdio
         config:
           command: npx  # Not "npx" with quotes
           args:
             - "-y"
             - "@modelcontextprotocol/server-filesystem"
             - "/private/tmp"  # Use /private/tmp on macOS (or /tmp on Linux)
   ```

### Tools Not Being Called

**Symptom:** Agent explains how to do something instead of using tools

**Solutions:**

1. **Verify MCP server initialized:**
   Look for these messages during run:
   ```
   🛠️  Initialized MCP stdio server: filesystem
   Initialized 1 MCP server(s)
   ```

2. **Use explicit paths:**
   ```bash
   # Instead of: "read test.txt"
   # Use: "Read the file at /private/tmp/test.txt" (on macOS)
   super agent run pydantic-mcp --goal "Read the file at /private/tmp/test.txt"
   ```

3. **Check allowed directories:**
   The filesystem server only allows access to specified directories:
   ```
   Client does not support MCP Roots, using allowed directories: [ '/private/tmp' ]
   ```
   Note: On macOS, `/tmp` is actually `/private/tmp`.

### Path Access Denied

**Error:** `Access denied - path outside allowed directories`

**Cause:** The model tried to access a file outside the allowed directory.

**Solution:** 
- **macOS:** Use `/private/tmp` in both MCP server config and file paths
- **Linux:** Use `/tmp` as normal
- Or modify the MCP server config to allow more directories:
  ```yaml
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/private/tmp"  # macOS
    # - "/tmp"        # Linux
    - "/home/user/projects"  # Add more allowed directories
  ```

### Model Returns JSON Instead of Content

**Symptom:** Response looks like `{"field": "value"}` instead of actual text

**Solution:** This was fixed in SuperOptiX 0.2.1. Update:
```bash
pip install --upgrade superoptix
```

The Pydantic AI template now uses plain text output mode, which works better with 8b models.

### MCP Tool Optimization Fails

**Error:** `None of the specified tools found. Available: ['read_file', 'write_file', ...]`

**Cause:** The `tool_names` in your playbook don't match the actual MCP server tool names.

**Solution:** Use actual MCP server tool names **without** the prefix:
```yaml
# Wrong - using prefixed names
tool_names: ["fs_read_file", "fs_write_file", "fs_list_files"]

# Correct - using actual server tool names
tool_names: ["read_file", "write_file", "list_directory"]
```

**Why?** The GEPA optimizer queries the MCP server directly, which returns unprefixed tool names. The `tool_prefix` only affects runtime naming in the agent.

### LiteLLM Provider Error

**Error:** `LLM Provider NOT provided. You passed model=ollama:llama3.1:8b`

**Solution:** Use forward slash instead of colon for the reflection LM:
```bash
# Wrong
--reflection-lm ollama:llama3.1:8b

# Correct
--reflection-lm ollama/llama3.1:8b
```

---

## Verified Working Examples

These commands were tested and work with `llama3.1:8b`:

```bash
# List directory contents (use /private/tmp on macOS, /tmp on Linux)
super agent run pydantic-mcp --goal "List all files in /private/tmp"
# Returns actual file list from filesystem

# Read a file
echo "Test content" > /private/tmp/test.txt
super agent run pydantic-mcp --goal "Read the file at /private/tmp/test.txt"
# Returns: "Test content"

# Write a file
super agent run pydantic-mcp --goal "Create a file /private/tmp/hello.txt with content: Hello World"
# Creates the file
cat /private/tmp/hello.txt  # Verify: "Hello World"
```

---

## What's Next?

- **Multiple MCP Servers**: Connect multiple servers for diverse tools
- **Remote Servers**: Use HTTP/SSE servers for remote tools
- **Custom Servers**: Build your own MCP servers in Python
- **Optimization**: Optimize tool descriptions with GEPA

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| MCP with Pydantic AI | Working | Full integration |
| Local 8b models | Working | `llama3.1:8b` tested |
| Filesystem operations | Working | Read, write, list |
| Plain text output | Working | No JSON metadata |
| Tool optimization | Working | GEPA support (use unprefixed tool names) |
| Instruction optimization | Working | Two-phase optimization |

---

## Related Documentation

- [Pydantic AI Integration Guide](pydantic-ai-integration.md)
- [MCP Protocol Guide](../guides/protocol-first-agents.md)
- [GEPA Optimization Guide](gepa-optimization.md)
- [Tool Optimization Guide](../guides/agent-optimization/tools.md)
