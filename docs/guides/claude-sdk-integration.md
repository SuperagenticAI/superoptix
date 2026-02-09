# Claude Agent SDK Integration Guide

SuperOptiX provides first-class support for Claude Agent SDK, enabling GEPA-optimizable agents powered by Anthropic's Claude with in-process MCP tool support.

RLM support is experimental. Unified sandbox support is coming soon.

---

## Key Features

| Feature | Description |
| :--- | :--- |
| **GEPA Optimization** | Optimize system prompts automatically for better performance |
| **In-Process MCP Tools** | Convert StackOne tools to Claude SDK MCP servers |
| **Async-First** | Full async/await support for high-performance applications |
| **Bidirectional Sessions** | Interactive multi-turn conversations with ClaudeSDKClient |
| **Hook System** | Pre/Post tool use hooks for control and security |

---

## Installation

```bash
pip install superoptix claude-agent-sdk
```

For StackOne integration:
```bash
pip install superoptix claude-agent-sdk stackone-ai
```

---

## Quick Start

### Create a Playbook

```yaml
# agents/my_claude_agent_playbook.yaml
metadata:
  name: my_claude_agent
  version: "1.0.0"
  description: "Claude SDK powered agent"

spec:
  persona:
    role: "You are a helpful coding assistant"
    goal: "Help users write better code"
    instructions: "Be concise and provide working examples"

  language_model:
    provider: anthropic
    model: claude-sonnet-4-5

  input_fields:
    - name: question
      type: string

  output_fields:
    - name: answer
      type: string
```

### Compile and Run

```bash
# Pull or create the agent project structure first
super agent pull my_claude_agent

# Compile to Claude SDK
super agent compile my_claude_agent --framework claude-sdk

# Run the agent
super agent run my_claude_agent --framework claude-sdk --goal "Explain async/await in Python"
```

### Use Programmatically

```python
import asyncio
from my_claude_agent_claude_sdk_pipeline import MyClaudeAgentPipeline

async def main():
    pipeline = MyClaudeAgentPipeline()
    result = await pipeline.run(query="Explain async/await in Python")
    print(result["answer"])

asyncio.run(main())
```

---

## Using StackOne Tools

The SuperOptiX StackOneBridge converts StackOne tools to Claude SDK's in-process MCP server format.

### Basic Integration

```python
from stackone_ai import StackOneToolSet
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, query
from superoptix.adapters import StackOneBridge

# Fetch StackOne tools
toolset = StackOneToolSet()
tools = toolset.fetch_tools(
    include_tools=["hris_get_employee", "hris_list_employees"],
    account_ids=["your_account_id"]
)

# Convert to Claude SDK MCP server
bridge = StackOneBridge(tools)
mcp_server, tool_names = bridge.to_claude_sdk()

# Create Claude Agent with tools
options = ClaudeAgentOptions(
    system_prompt="You are an HR assistant with HRIS access.",
    mcp_servers={"stackone": mcp_server},
    allowed_tools=tool_names,
    model="claude-sonnet-4-5",
)

# Execute query
async for message in query(prompt="Find employee John Doe", options=options):
    # Process messages
    pass
```

### Interactive Session

```python
async with ClaudeSDKClient(options=options) as client:
    # First query
    await client.query("How many employees do we have?")
    async for msg in client.receive_response():
        # Process response
        pass

    # Follow-up (uses conversation context)
    await client.query("Who is in engineering?")
    async for msg in client.receive_response():
        pass
```

### Dynamic Tool Discovery

For large tool sets, use discovery tools:

```python
# Get all tools
tools = toolset.fetch_tools(include_tools=["hris_*", "ats_*", "crm_*"])

# Create discovery meta-tools
bridge = StackOneBridge(tools)
mcp_server, tool_names = bridge.to_discovery_tools(framework="claude_sdk")

# Agent can now search for and execute tools dynamically
options = ClaudeAgentOptions(
    system_prompt="Use tool_search to find tools, then tool_execute to run them.",
    mcp_servers={"stackone": mcp_server},
    allowed_tools=tool_names,
)
```

---

## GEPA Optimization

The `system_prompt` is the optimizable variable for Claude SDK agents:

```python
from superoptix.adapters import FrameworkRegistry
from superoptix.optimizers.universal_gepa import UniversalGEPA

# Create component from playbook
component = FrameworkRegistry.create_component("claude-sdk", playbook)

# The system_prompt is accessible as component.variable
print(f"Current prompt: {component.variable}")

# Optimize with GEPA
optimizer = UniversalGEPA(metric=my_accuracy_metric, auto="medium")
result = optimizer.optimize(component, trainset=training_data)

print(f"Optimized prompt: {result.optimized_variable}")
print(f"Improvement: {result.improvement}%")
```

---

## MCP Server Configuration

### External MCP Servers (stdio)

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@anthropic/claude-mcp-filesystem", "/path/to/dir"]
```

### HTTP/SSE MCP Servers

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: my_api
        type: http
        config:
          url: "http://localhost:8080/mcp"
          headers:
            Authorization: "Bearer ${API_KEY}"
```

---

## API Reference

### ClaudeAgentSDKFrameworkAdapter

```python
from superoptix.adapters import FrameworkRegistry

# Get adapter
adapter = FrameworkRegistry.get_adapter("claude-sdk")

# Compile playbook
output_path = adapter.compile_from_playbook(playbook, "output.py")

# Create component for GEPA
component = adapter.create_component(playbook)

# Get optimizable variable
prompt = adapter.get_optimizable_variable(playbook)
```

### StackOneBridge.to_claude_sdk()

```python
mcp_server, tool_names = bridge.to_claude_sdk()
```

**Returns:**
- `mcp_server`: `McpSdkServerConfig` for use with `ClaudeAgentOptions.mcp_servers`
- `tool_names`: List of tool names in format `mcp__stackone__{tool_name}`

---

## Best Practices

1. **Use async/await**: Claude SDK is async-first; use `asyncio.run()` for sync contexts

2. **Tool naming**: Claude SDK MCP tools follow `mcp__{server}__{tool}` convention

3. **System prompt optimization**: Keep prompts focused; let GEPA refine them

4. **Error handling**: Use `ResultMessage.is_error` to detect failures

5. **Cost tracking**: Check `ResultMessage.total_cost_usd` for usage monitoring

---

## Troubleshooting

### Claude Agent SDK not installed

```
ImportError: claude-agent-sdk is not installed
```

**Solution:** `pip install claude-agent-sdk`

### CLI not found

```
CLINotFoundError: Claude Code CLI not found
```

**Solution:** The Claude Agent SDK requires the Claude Code CLI. Install it or ensure it's in your PATH.

### MCP server connection failed

```
MCPConnectionError: Failed to connect to MCP server
```

**Solution:** Check server configuration, ensure the command/URL is correct, and verify the server is running.

---

## Examples

See the complete example at:
```
examples/integrations/stackone_claude_sdk_example.py
```

This includes:
- Basic StackOne + Claude SDK integration
- Interactive sessions with ClaudeSDKClient
- Dynamic tool discovery
