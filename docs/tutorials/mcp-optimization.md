# MCP Optimization Tutorial

Learn how to optimize Model Context Protocol (MCP) systems using SuperOptiX's advanced MCP integration and GEPA optimization.

## Overview

This tutorial covers:
- Setting up MCP servers and clients
- Optimizing MCP tool integration
- Protocol-First vs Tool-First approaches
- Advanced MCP optimization techniques

## Prerequisites

### Install SuperOptiX with MCP Support

```bash
pip install superoptix[mcp]
```

**Includes:**
- SuperOptiX core with GEPA 0.0.17
- MCP SDK 1.19.0 for tool optimization
- MCP adapter (vendored from GEPA PR #105)

**Additional Requirements:**
- Python 3.11+
- Git (for DSPy dependency)
- Node.js 18+ (for MCP servers)
- Basic understanding of MCP concepts

## Step 1: Initialize MCP Project

```bash
# Create new project
super init mcp_optimization_project
cd mcp_optimization_project

# Pull MCP demo agent
super agent pull mcp_demo
```

## Step 2: Install MCP Servers

```bash
# Install MCP servers (Node.js required)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sqlite
```

**Note:** MCP SDK 1.19.0 is already installed if you used `superoptix[mcp]` above.

## Step 3: Configure MCP Servers

### 3.1 Filesystem Server

```yaml
# agents/mcp_demo.yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
          env:
            MCP_FILESYSTEM_ROOT: "/path/to/docs"
```

### 3.2 Git Server

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
          env:
            MCP_GIT_REPO: "/path/to/repo"
```

### 3.3 SQLite Server

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: sqlite
          command: npx
          args: ["-y", "@modelcontextprotocol/server-sqlite", "--db", "/path/to/database.db"]
          env:
            MCP_SQLITE_DB: "/path/to/database.db"
```

## Step 4: Protocol-First Approach

### 4.1 Automatic Tool Discovery

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      protocol_first: true
      auto_discovery: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
```

### 4.2 Tool Registration

```bash
# Compile with MCP
super agent compile mcp_demo

# Test automatic tool discovery
super agent run mcp_demo --goal "List all available tools"
```

Expected output:
```
Available Tools:
- filesystem.read_file: Read file contents
- filesystem.write_file: Write file contents
- filesystem.list_directory: List directory contents
- git.get_commits: Get commit history
- git.get_diff: Get file differences
- sqlite.query: Execute SQL queries
```

## Step 5: Tool-First Approach

### 5.1 Manual Tool Configuration

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      protocol_first: false
      tools:
        - name: read_file
          description: "Read contents of a file"
          parameters:
            path:
              type: string
              description: "Path to the file"
        - name: write_file
          description: "Write contents to a file"
          parameters:
            path:
              type: string
              description: "Path to the file"
            content:
              type: string
              description: "Content to write"
        - name: list_directory
          description: "List contents of a directory"
          parameters:
            path:
              type: string
              description: "Path to the directory"
```

### 5.2 Custom Tool Implementation

```python
# tools/mcp_custom_tools.py
from typing import Dict, Any
import os

class MCPCustomTools:
    def __init__(self):
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_directory": self.list_directory,
        }
    
    def read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def list_directory(self, path: str) -> list:
        """List directory contents."""
        try:
            return os.listdir(path)
        except Exception as e:
            return [f"Error listing directory: {e}"]
```

## Step 6: MCP Optimization with GEPA

### 6.1 Tool Selection Optimization

```bash
# Optimize tool selection
super agent optimize mcp_demo --auto medium

# Evaluate optimized version
super agent evaluate mcp_demo  # automatically loads optimized weights
```

GEPA will optimize:
- Tool selection based on query context
- Parameter optimization for tools
- Tool chaining strategies
- Context utilization

### 6.2 Protocol Optimization

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      optimization:
        tool_selection: "contextual"  # Context-aware tool selection
        parameter_tuning: true        # Optimize tool parameters
        tool_chaining: true           # Enable tool chaining
        context_window: 8192         # Optimize context window
```

## Step 7: Advanced MCP Techniques

### 7.1 Multi-Server Coordination

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/docs"]
        - name: git
          command: npx
          args: ["-y", "@modelcontextprotocol/server-git", "--repository", "/repo"]
        - name: sqlite
          command: npx
          args: ["-y", "@modelcontextprotocol/server-sqlite", "--db", "/data.db"]
      coordination:
        enabled: true
        strategy: "sequential"  # sequential, parallel, hybrid
        timeout: 30
```

### 7.2 Tool Chaining

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      tool_chaining:
        enabled: true
        max_chain_length: 5
        strategies:
          - "filesystem -> git -> sqlite"
          - "git -> filesystem -> sqlite"
          - "sqlite -> filesystem -> git"
```

### 7.3 Context Optimization

```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      context_optimization:
        enabled: true
        max_context_length: 8192
        context_compression: true
        relevance_threshold: 0.7
        dynamic_context: true
```

## Step 8: MCP Performance Monitoring

### 8.1 Set Up Observability

```bash
# Enable MCP-specific monitoring
super agent compile mcp_demo --observability mcp

# Enable detailed tracing
super agent compile mcp_demo --tracing detailed
```

### 8.2 Monitor MCP Metrics

```bash
# Run with MCP monitoring
super agent run mcp_demo --goal "Analyze the codebase" --monitor

# View MCP-specific metrics
super observe mcp-metrics mcp_demo
```

Key MCP metrics to monitor:
- **Tool Selection Accuracy**: How well are tools selected?
- **Tool Execution Time**: How fast are tools executed?
- **Context Utilization**: How well is context used?
- **Protocol Efficiency**: How efficient is the MCP protocol?

## Step 9: Production MCP Deployment

### 9.1 Optimize for Production

```bash
# Final MCP optimization
super agent optimize mcp_demo --auto intensive

# Build production version
super agent compile mcp_demo --production
```

### 9.2 Deploy MCP Orchestra

```bash
# Create MCP orchestra
super orchestra create mcp_orchestra

# Add MCP agent to orchestra
super orchestra add-agent mcp_demo

# Configure MCP servers for orchestra
super orchestra configure mcp_orchestra --mcp-servers

# Run MCP orchestra
super orchestra run mcp_orchestra
```

## Step 10: MCP Best Practices

### 10.1 Server Configuration

**Resource Management**
```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      servers:
        - name: filesystem
          command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/docs"]
          resources:
            memory_limit: "512MB"
            cpu_limit: "0.5"
            timeout: 30
```

**Security Configuration**
```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      security:
        enabled: true
        allowed_paths: ["/docs", "/data"]
        blocked_paths: ["/system", "/root"]
        authentication: true
        encryption: true
```

### 10.2 Tool Design

**Tool Naming**
- Use descriptive, action-oriented names
- Follow consistent naming conventions
- Include version numbers for breaking changes

**Parameter Design**
- Use clear, descriptive parameter names
- Provide comprehensive parameter descriptions
- Include examples in descriptions
- Validate parameter types and ranges

**Error Handling**
- Provide meaningful error messages
- Include error codes for programmatic handling
- Log errors for debugging
- Graceful degradation when possible

### 10.3 Performance Optimization

**Tool Caching**
```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      caching:
        enabled: true
        cache_ttl: 3600  # 1 hour
        cache_size: 1000
        cache_strategy: "lru"
```

**Connection Pooling**
```yaml
spec:
  rag:
    enabled: true
    mcp:
      enabled: true
      connection_pooling:
        enabled: true
        max_connections: 10
        connection_timeout: 30
        keep_alive: true
```

## Troubleshooting

### Common MCP Issues

**Server Connection Failures**
```bash
# Check server status
super mcp status

# Restart MCP servers
super mcp restart

# Check server logs
super mcp logs
```

**Tool Discovery Issues**
```bash
# Force tool discovery
super agent compile mcp_demo --force-discovery

# Check available tools
super mcp list-tools
```

**Performance Issues**
```bash
# Optimize MCP configuration
super agent optimize mcp_demo --mcp-optimization

# Check MCP metrics
super observe mcp-metrics mcp_demo
```

## Next Steps

- [RAG Optimization Tutorial](rag-optimization.md)
- [Memory Optimization Guide](../guides/memory-context-optimization.md)
- [Advanced MCP Techniques](../guides/protocol-first-agents.md)
- [Observability Setup](../guides/observability.md)

## Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Development](../guides/protocol-first-agents.md)
- [GEPA Optimization Guide](../guides/gepa-optimization.md)
- [Community Discord](https://Documentation: https://superagenticai.github.io/superoptix-ai/)
