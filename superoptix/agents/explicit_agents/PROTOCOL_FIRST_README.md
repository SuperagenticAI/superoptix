# Protocol-First Agents in SuperOptiX

## 🚀 What's New

SuperOptiX now supports **protocol-first agents** using the Agenspy approach. This allows agents to automatically discover tools from MCP (Model Context Protocol) servers without manual tool configuration.

---

## 📋 Available Protocol-First Agents

### 1. `protocol_first_agent`
**Location**: `superoptix/agents/explicit_agents/protocol_first_agent_playbook.yaml`

**Description**: Demonstration agent showing automatic tool discovery from MCP servers

**Usage**:
```bash
# Pull the agent
super agent pull protocol_first_agent

# Compile
super agent compile protocol_first_agent

# Run
super agent run protocol_first_agent --goal "Search GitHub for AI agents"
```

### 2. `github_protocol_agent`
**Location**: `superoptix/agents/software/github_protocol_agent_playbook.yaml`

**Description**: GitHub repository analyst using protocol-first approach

**Usage**:
```bash
# Pull the agent
super agent pull github_protocol_agent

# Compile
super agent compile github_protocol_agent

# Run with observability
super agent run github_protocol_agent \
  --goal "Analyze SuperOptiX repository" \
  --observe mlflow
```

### 3. `protocol_demo`
**Location**: `superoptix/agents/demo/protocol_demo_playbook.yaml`

**Description**: Simple demo of protocol-first capabilities

**Usage**:
```bash
super agent pull protocol_demo
super agent compile protocol_demo
super agent run protocol_demo --goal "Show me your tools"
```

---

## 🔧 How Protocol-First Works

### Traditional Tool-First (MCP Agent)
```yaml
spec:
  tools:
    enabled: true
    categories: ["core"]
    specific_tools: ["calculator", "search"]
```
**Result**: Tools loaded manually

### Protocol-First (NEW!)
```yaml
spec:
  tool_backend: "agenspy"
  mcp_servers:
    - "mcp://localhost:8080/github"
```
**Result**: Tools discovered automatically!

---

## 🎯 Key Differences

| Feature | Tool-First | Protocol-First |
|---------|-----------|---------------|
| **Tool Loading** | Manual | Automatic |
| **Configuration** | List each tool | List MCP servers |
| **Discovery** | Static | Dynamic |
| **Updates** | Recompile needed | Automatic |
| **Template** | `dspy_pipeline_explicit.py.jinja2` | `dspy_pipeline_agenspy.py.jinja2` |

---

## 📚 Next Steps

1. **Pull an agent**:
   ```bash
   super agent pull protocol_first_agent
   ```

2. **Compile it**:
   ```bash
   super agent compile protocol_first_agent
   ```

3. **Run with observability**:
   ```bash
   super agent run protocol_first_agent \
     --goal "Test query" \
     --observe superoptix
   ```

4. **View dashboard**:
   ```bash
   super observe dashboard
   ```

---

## 🌟 Benefits

- ✅ **Zero Configuration**: No manual tool loading
- ✅ **Automatic Updates**: New tools appear instantly
- ✅ **Protocol-Level Optimization**: Future GEPA enhancements
- ✅ **Production Ready**: Real MCP client support

---

*For more information, see: [Protocol-First Agents Guide](../../../docs/guides/protocol-first-agents.md)*

