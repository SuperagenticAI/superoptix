# Protocol-First Agents in SuperOptiX

## 🚀 Introduction

SuperOptiX supports two approaches for building agents:

1. **Tool-First (Traditional)**: Manually load and configure tools
2. **Protocol-First (New!)**: Automatic tool discovery via protocols

This guide covers the **protocol-first approach**, powered by vendored Agenspy components.

---

## 🎯 What is Protocol-First?

Protocol-first agents treat communication protocols (like MCP) as first-class primitives. Instead of manually loading tools, agents connect to protocol servers and **automatically discover** available tools.

### Traditional Tool-First
```python
# Manual tool loading
tools = [calculator, search, github_api]
agent = MyAgent(tools=tools)
```

### Protocol-First
```python
# Automatic tool discovery
agent = MyAgent(mcp_servers=['mcp://localhost:8080'])
# Tools discovered automatically!
```

---

## ✨ Key Benefits

### Zero Configuration
- No manual tool loading
- No tool registry management
- Tools appear automatically when servers add them

### Dynamic Discovery
- New tools available instantly
- No agent recompilation needed
- Protocol handles versioning

### Protocol-Level Optimization
- GEPA can optimize at protocol level
- Session management built-in
- Future-ready for Agent2Agent protocol

### Better Maintainability
- Less code to maintain
- No tool version conflicts
- Protocol handles compatibility

---

## 📋 Quick Start

### Step 1: Create a Protocol-First Playbook

Add two fields to your playbook's `spec` section:

```yaml
apiVersion: agent/v1
kind: AgentSpec

metadata:
  name: "My Protocol Agent"
  id: "my_protocol_agent"
  version: "1.0.0"
  level: "genies"  # Protocol-first requires genies tier

spec:
  # NEW: Enable protocol-first mode
  tool_backend: "agenspy"
  
  # NEW: List MCP server URIs
  mcp_servers:
    - "mcp://localhost:8080/math"
    - "mcp://localhost:8080/github"
  
  # Rest of your spec...
  language_model:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
  
  persona:
    role: "Research Assistant"
    goal: "Help with research and analysis"
```

### Step 2: Compile the Agent

```bash
super agent compile my_protocol_agent
```

**Output:**
```
🤖 Generating Protocol-First Genies-Tier pipeline (Agenspy - Automatic tool discovery via MCP)...
🔌 Protocol-First Approach: Automatic tool discovery from MCP servers
🤖 Agenspy Integration: Vendored protocol-first components
🛠️  Auto Tool Discovery: No manual tool loading or registration
🎯 Key Differentiator: Protocol-level optimization + session management
📡 MCP Servers: 2 configured (mcp://localhost:8080/math, mcp://localhost:8080/github)
Successfully generated Genies-tier pipeline (protocol-first/agenspy)
```

### Step 3: Run the Agent

```bash
super agent run my_protocol_agent --goal "Calculate 25 * 17 and search GitHub for SuperOptiX"
```

**Behind the Scenes:**
1. Agent connects to MCP servers
2. Tools discovered automatically (calculator, github_search, etc.)
3. Agent uses ReAct with protocol-discovered tools
4. Results include protocol metadata

---

## 🔧 Configuration Options

### Playbook Schema

```yaml
spec:
  # Required: Choose backend
  tool_backend: "agenspy"  # or "dspy" for tool-first
  
  # Required for protocol-first: MCP servers
  mcp_servers:
    - "mcp://localhost:8080/math"
    - "mcp://localhost:8080/github"
    - "mcp://localhost:8080/code"
  
  # Optional: Protocol settings in config section
config:
  protocol_timeout: 30
  auto_reconnect: true
  max_tool_retries: 3
  cache_protocol_capabilities: true
```

### Auto-Detection

If you provide `mcp_servers` but omit `tool_backend`, SuperOptiX automatically uses protocol-first:

```yaml
spec:
  # tool_backend auto-detected as "agenspy"
  mcp_servers:
    - "mcp://localhost:8080/math"
```

---

## 🎓 Complete Example

See `examples/protocol_agent_basic.yaml` for a full example:

```yaml
apiVersion: agent/v1
kind: AgentSpec

metadata:
  name: "GitHub Research Assistant"
  id: "github_research_assistant"
  level: "genies"

spec:
  tool_backend: "agenspy"
  
  mcp_servers:
    - "mcp://localhost:8080/github"
    - "mcp://localhost:8080/code"
  
  language_model:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
  
  persona:
    role: "GitHub analyst"
    goal: "Analyze repositories and code"
  
  reasoning:
    method: "react"
    max_iterations: 5
  
  input_fields:
    - name: "query"
      description: "Research query"
  
  output_fields:
    - name: "analysis"
      description: "Analysis results"
```

---

## 🔍 How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│ Protocol-First Agent (ProtocolAgent)   │
│                                         │
│ ┌────────────────────────────────────┐ │
│ │ DSPy ReAct Module                  │ │
│ │ (with protocol-discovered tools)   │ │
│ └────────────────────────────────────┘ │
│                                         │
│ ┌────────────────────────────────────┐ │
│ │ Protocol Registry                  │ │
│ │  • MCP Client 1 (math)             │ │
│ │  • MCP Client 2 (github)           │ │
│ │  • MCP Client 3 (code)             │ │
│ └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│ MCP Servers                             │
│  • mcp://localhost:8080/math            │
│  • mcp://localhost:8080/github          │
│  • mcp://localhost:8080/code            │
└─────────────────────────────────────────┘
```

### Execution Flow

1. **Initialization**
   - Agent connects to MCP servers
   - Tools discovered automatically
   - Protocol registry tracks connections

2. **Query Processing**
   - User provides query
   - ReAct decides which tools to use
   - Tools execute via protocol sessions

3. **Tool Execution**
   - Tool call routed to appropriate MCP server
   - Server executes and returns result
   - Result formatted for agent

4. **Response Generation**
   - Agent synthesizes tool outputs
   - Final response returned
   - Protocol metadata included

---

## 🎯 Best Practices

### MCP Server URIs
```yaml
# Good: Descriptive server names
mcp_servers:
  - "mcp://localhost:8080/math"
  - "mcp://localhost:8080/github"

# Avoid: Generic names
mcp_servers:
  - "mcp://localhost:8080"
```

### Tier Selection
```yaml
# Protocol-first requires genies tier
metadata:
  level: "genies"

spec:
  tool_backend: "agenspy"
```

### Reasoning Method
```yaml
# Use ReAct for tool-using agents
reasoning:
  method: "react"
  max_iterations: 5
```

### Error Handling
```yaml
# Configure retries and timeouts
config:
  protocol_timeout: 30
  max_tool_retries: 3
  auto_reconnect: true
```

---

## 🔄 Migration Guide

### From Tool-First to Protocol-First

**Before (Tool-First)**:
```yaml
spec:
  tools:
    enabled: true
    categories:
      - "core"
      - "finance"
    specific_tools:
      - "calculator"
      - "web_search"
```

**After (Protocol-First)**:
```yaml
spec:
  tool_backend: "agenspy"
  mcp_servers:
    - "mcp://localhost:8080/math"
    - "mcp://localhost:8080/web"
```

**Key Changes**:
1. Replace `tools` section with `mcp_servers`
2. Add `tool_backend: "agenspy"`
3. Ensure `level: "genies"`
4. Recompile agent

---

## 🐛 Troubleshooting

### Agent Not Using Protocol-First

**Problem**: Agent compiled as tool-first despite configuration

**Solution**: Check that:
- `tool_backend: "agenspy"` is set OR
- `mcp_servers` list is not empty
- Agent is genies tier (`level: "genies"`)

### No Tools Discovered

**Problem**: Agent reports 0 tools discovered

**Solution**:
- Verify MCP servers are running
- Check server URIs are correct
- Check network connectivity
- Review logs for connection errors

### Protocol Connection Failed

**Problem**: "Failed to connect to MCP server"

**Solution**:
- Verify server URI format: `mcp://host:port/path`
- Check server is running and accessible
- Increase timeout: `config.protocol_timeout: 60`
- Enable auto-reconnect: `config.auto_reconnect: true`

---

## 📚 API Reference

### ProtocolAgent Class

```python
from superoptix.agent_bases import ProtocolAgent

class MyAgent(ProtocolAgent):
    def __init__(self, mcp_servers: List[str]):
        super().__init__(agent_id="my_agent")
        
        # Protocols added automatically
        # Tools discovered automatically
        
    def forward(self, query: str):
        # Execute with protocol tools
        return self.react(--goal query)
```

### Protocol Registry

```python
from superoptix.protocols import registry, ProtocolType

# Create protocol
protocol = registry.create_protocol(
    ProtocolType.MCP,
    server_url="mcp://localhost:8080/math"
)

# Connect
protocol.connect()

# Get capabilities
caps = protocol.get_capabilities()
print(f"Tools: {caps['tools']}")
```

### MCP Client

```python
from superoptix.protocols.mcp import MCPClient

# Create client
client = MCPClient(server_url="mcp://localhost:8080/math")

# Connect and discover tools
if client.connect():
    print(f"Connected! Tools: {list(client.available_tools.keys())}")
```

---

## 🚀 Advanced Usage

### Multiple MCP Servers

```yaml
spec:
  mcp_servers:
    - "mcp://localhost:8080/math"      # Math tools
    - "mcp://localhost:8080/github"    # GitHub API
    - "mcp://localhost:8080/code"      # Code analysis
    - "mcp://localhost:8080/web"       # Web search
```

### Protocol + RAG

```yaml
spec:
  tool_backend: "agenspy"
  mcp_servers:
    - "mcp://localhost:8080/github"
  
  rag:
    enabled: true
    collection: "github_docs"
    knowledge_base:
      - "docs/github_api.md"
    top_k: 5
```

### GEPA Optimization

Protocol-first agents are fully compatible with GEPA:

```bash
# Compile
super agent compile my_protocol_agent

# Evaluate
super agent evaluate my_protocol_agent

# Optimize with GEPA
super agent optimize my_protocol_agent

# Re-evaluate
super agent evaluate my_protocol_agent
```

---

## 🎓 FAQ

### Q: Do I need real MCP servers?
**A**: No! SuperOptiX includes mock MCP servers for development and testing.

### Q: Can I mix tool-first and protocol-first?
**A**: Not in the same agent. Choose one approach per agent. (Hybrid mode planned for v2.0)

### Q: Is protocol-first slower than tool-first?
**A**: No! Mock MCP has similar performance. Real MCP depends on server latency.

### Q: Does GEPA work with protocol-first?
**A**: Yes! Protocol-first agents are fully compatible with GEPA optimization.

### Q: Can I use custom protocols?
**A**: Currently only MCP is supported. Custom protocols planned for v2.0.

---

## 🔮 Future Enhancements

### Coming Soon
- RealMCPClient (background MCP servers)
- Additional mock tools
- Protocol-level GEPA optimization

### Roadmap
- Agent2Agent protocol support
- Hybrid mode (tool-first + protocol-first)
- Custom protocol implementations
- Protocol marketplace

---

## 🌟 Key Takeaways

1. **Protocol-first = Automatic tool discovery**
   - No manual tool loading
   - Tools update dynamically

2. **Two new fields in playbook**
   - `tool_backend: "agenspy"`
   - `mcp_servers: [...]`

3. **Fully backward compatible**
   - Tool-first still works
   - Choose per agent

4. **GEPA compatible**
   - Optimize protocol-first agents
   - Protocol-level optimization coming

5. **Key differentiator**
   - SuperOptiX is the only DSPy framework with protocol-first support

---

## 📖 Related Documentation

- [Examples: protocol_agent_basic.yaml](../../examples/protocol_agent_basic.yaml)
- [API Reference: Protocols](../reference/api/protocols.md)
- [SuperSpec DSL](../reference/api/superspec.md)
- [GEPA Optimization](./gepa-optimization.md)

---

**Questions or feedback?** Open an issue on GitHub or join our Discord!

**Want to contribute?** Check out our [Contributing Guide](../../CONTRIBUTING.md)

---

*Last Updated: 2025-10-20*
*Version: 1.0.0*

