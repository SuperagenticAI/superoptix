# Protocol Optimization (MCP)

## What is Protocol Optimization?

Protocol optimization is the process of improving how agents use **standardized communication protocols** like MCP (Model Context Protocol) for tool interaction. GEPA learns optimal protocol invocation patterns, tool selection within protocols, and error handling strategies.

**Key Insight**: Protocols like MCP provide powerful tool ecosystems, but agents must learn WHEN to use protocol tools vs. built-in tools, HOW to structure protocol calls, and HOW to handle protocol-specific errors.

---

## What is MCP?

**MCP (Model Context Protocol)** is an open protocol for connecting AI models with external tools and data sources. It standardizes how agents discover, invoke, and interact with tools.

**MCP Benefits**:
- Standardized tool interface
- Automatic tool discovery
- Rich tool ecosystems
- Cross-platform compatibility

**SuperOptiX + MCP**: GEPA optimizes how agents use MCP tools for maximum effectiveness.

---

## The Protocol Optimization Problem

### Without Optimization

**Scenario**: Agent with both built-in and MCP tools

```
1. Agent has: built-in calculator + MCP math_tools
2. Query: "Calculate 2^10"
3. Agent: Doesn't know which to use
4. Agent: Uses wrong tool or no tool
```

**Problem**: Tool confusion, suboptimal usage

### With GEPA Optimization

**Scenario**: Same tools, same query

```
1. Agent has: built-in calculator + MCP math_tools
2. GEPA-learned strategy: "Use MCP math_tools for advanced math, built-in for simple"
3. Query: "Calculate 2^10"
4. Agent: Uses built-in calculator (simpler, faster)
5. Agent: Returns 1024
```

**Solution**: Optimal tool selection based on query complexity

---

## What GEPA Optimizes in MCP

### Protocol Tool Selection

**What It Is**: Learning when to use MCP tools vs. built-in tools

**What GEPA Learns**:
- Complexity thresholds (simple → built-in, complex → MCP)
- Capability mapping (which tool for which task)
- Performance tradeoffs (latency vs. capability)

**Example Configuration**:

```yaml
spec:
  tools:
    enabled: true
    protocol: mcp
    mcp_servers:
      - name: filesystem
        command: uvx mcp-server-filesystem
      - name: github
        command: uvx mcp-server-github
    
    # Built-in tools also available
    categories:
      - utilities
```

**Before Optimization**:
```
Strategy: Always prefer MCP tools (slower, more overhead)
Result: Simple tasks take longer than needed
```

**After GEPA Optimization**:
```
Learned Strategies:
- "Simple file read → Use built-in file_reader (fast)"
- "Git operations → Use MCP github server (required)"
- "Complex filesystem ops → Use MCP filesystem server (powerful)"
- "Calculations → Use built-in calculator unless advanced math needed"
```

**Impact**: 3x faster for simple tasks, same power for complex tasks

---

### Protocol Invocation Patterns

**What It Is**: Learning how to structure and sequence protocol calls

**What GEPA Learns**:
- Call structure optimization
- Parameter selection
- Error recovery patterns
- Result caching strategies

**Before Optimization**:
```
MCP Call: Generic parameters, no error handling

Result: Failures on edge cases, no retry logic
```

**After GEPA Optimization**:
```
Learned Patterns:
1. Validate inputs before MCP call
2. Use specific parameters based on context
3. Implement retry logic for transient failures
4. Cache results for repeated queries
5. Fall back to built-in tools if MCP unavailable
```

**Impact**: 90% error recovery rate, robust performance

---

### Multi-Protocol Orchestration

**What It Is**: Learning to coordinate multiple MCP servers

**What GEPA Learns**:
- Which server for which task
- Cross-server workflows
- Result aggregation from multiple protocols

**Example**: Code review with MCP

**Before Optimization**:
```
Agent: Uses only one MCP server, misses context
Result: Incomplete analysis
```

**After GEPA Optimization**:
```
Learned Orchestration:
1. MCP filesystem → Read code file
2. MCP github → Get commit history and PR comments
3. Built-in security_scanner → Analyze code
4. Synthesize: File content + Git context + Security analysis

Result: Comprehensive review with version control context
```

**Impact**: Multi-dimensional analysis vs. single-source review

---

### Error Handling and Fallbacks

**What It Is**: Learning how to handle protocol failures

**What GEPA Learns**:
- When to retry
- When to fall back to alternatives
- How to communicate errors
- Graceful degradation

**Before Optimization**:
```
MCP server down → Agent fails completely
Response: "Error: Unable to process request"
```

**After GEPA Optimization**:
```
Learned Fallback Strategy:
1. Try MCP tool
2. If timeout → Retry once
3. If still failing → Fall back to built-in tool
4. If no fallback → Explain limitation gracefully

Response: "MCP server temporarily unavailable. Using built-in tools for analysis. 
           Results may be less comprehensive but still actionable."
```

**Impact**: Graceful degradation vs. complete failure

---

## Before/After Comparison

### Scenario: File Analysis with MCP

**Setup**:
- Built-in tool: `file_reader` (simple, fast)
- MCP tool: `mcp-server-filesystem` (advanced, slower)

**Query**: "Read config.json and check for hardcoded secrets"

**Before Protocol Optimization**:
```
Tool Selection: Always MCP (overkill for simple read)
Steps:
1. Initialize MCP connection (300ms)
2. Discover tools (200ms)
3. Read file via MCP (150ms)
4. Analyze (agent processing)
Total: 650ms + analysis

Result: Correct but slow
```

**After GEPA Protocol Optimization**:
```
GEPA-Learned Strategy: "Simple file read → Use built-in (faster)"

Tool Selection: built-in file_reader
Steps:
1. Read file (50ms)
2. Analyze (agent processing)
Total: 50ms + analysis

Result: Same correctness, 13x faster

BUT, if query was: "Read all JSON files in directory recursively"
GEPA learns: "Complex filesystem ops → Use MCP (more powerful)"
Tool Selection: mcp-server-filesystem
```

**Impact**: Optimal tool choice based on task complexity

---

## How GEPA Learns Protocol Strategies

### The Optimization Process

1. **Analysis Phase**
   ```
   GEPA Observes:
   - Agent used MCP for simple file read
   - Operation took 650ms (slow)
   - Built-in tool could have done it in 50ms
   - RSpec-style BDD scenario passed but performance poor
   ```

2. **Reflection Phase**
   ```
   GEPA Reflection:
   "MCP overhead (500ms) not justified for simple file read.
    Built-in file_reader could handle this faster.
    Learn pattern: Simple reads → built-in, Complex ops → MCP"
   ```

3. **Mutation Phase**
   ```
   GEPA Tests:
   - Strategy 1: "Always use built-in" (fails on complex ops)
   - Strategy 2: "Always use MCP" (slow on simple ops)
   - Strategy 3: "Built-in for single file, MCP for directory/recursive"
   ```

4. **Evaluation Phase**
   ```
   Results:
   - Strategy 1: 60% (fast but limited)
   - Strategy 2: 70% (powerful but slow)
   - Strategy 3: 95% (optimal!) ← Winner!
   ```

5. **Selection Phase**
   ```
   GEPA Keeps: Strategy 3 (complexity-based selection)
   Generalizes: Pattern applies to other tool types
   ```

**Result**: Learned when to use protocol tools vs. built-in tools

---

## Best Practices

### Configure Both MCP and Built-in Tools

```yaml
tools:
  enabled: true
  protocol: mcp
  
  # MCP servers
  mcp_servers:
    - name: filesystem
      command: uvx mcp-server-filesystem
    - name: github  
      command: uvx mcp-server-github
  
  # Built-in tools as fallbacks
  categories:
    - utilities
    - code_analysis
```

GEPA learns when to use each type.

### Define Protocol-Aware RSpec-Style BDD Scenarios

```yaml
feature_specifications:
  scenarios:
    - name: git_operations
      description: Agent should use MCP github server for Git ops
      input:
        task: "Get latest commit message"
      expected_output:
        result: Must use MCP github tool (not built-in)
```

### Enable Error Recovery

```yaml
tools:
  retry_on_failure: true
  fallback_to_builtin: true
  timeout: 30
```

GEPA optimizes retry and fallback strategies.

### Monitor Protocol Performance

```yaml
observability:
  enabled: true
  track_tool_latency: true
  track_protocol_usage: true
```

Helps GEPA learn performance-optimal patterns.

---

## Common Protocol Strategies GEPA Learns

### Strategy 1: Complexity-Based Selection

**Before**: Random tool choice  
**After**: "Simple operations → built-in tools. Complex operations → MCP tools"

### Strategy 2: Capability-Aware Routing

**Before**: Try built-in first, fail, then MCP  
**After**: "Git operations always require MCP github server. Don't try built-in."

### Strategy 3: Performance Optimization

**Before**: Always initialize all MCP servers  
**After**: "Lazy-load MCP servers only when needed. Cache connections."

### Strategy 4: Graceful Degradation

**Before**: MCP fails → Agent fails  
**After**: "MCP unavailable → Use built-in tools with disclaimer about limitations"

---

## Metrics and Results

### What Gets Measured

- **Protocol Selection Accuracy**: % correct protocol choice
- **Latency**: Average tool execution time
- **Error Recovery Rate**: % of protocol failures recovered
- **Capability Utilization**: % of protocol features used effectively

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Protocol Selection Accuracy</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">40%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Average Latency</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">850ms</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>200ms</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">4x faster</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Error Recovery</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">10%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+80%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Feature Utilization</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
</table>

---

## Quick Start

### Enable Protocol Optimization

```yaml
spec:
  # MCP protocol configuration
  tools:
    enabled: true
    protocol: mcp
    mcp_servers:
      - name: filesystem
        command: uvx mcp-server-filesystem
  
  # GEPA automatically optimizes protocol usage
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium
```

```bash
super agent compile your_agent
super agent optimize your_agent --auto medium
```

GEPA will learn optimal MCP usage patterns!

---

## Advanced: MCP-Specific Configuration

### Multiple MCP Servers

```yaml
tools:
  protocol: mcp
  mcp_servers:
    - name: filesystem
      command: uvx mcp-server-filesystem
      capabilities: [read, write, list, search]
    
    - name: github
      command: uvx mcp-server-github
      env:
        GITHUB_TOKEN: ${GITHUB_TOKEN}
      capabilities: [repos, issues, prs]
    
    - name: database
      command: uvx mcp-server-postgres
      capabilities: [query, schema]
```

GEPA learns which server for which operation.

---

## What GEPA Optimizes

### Tool Source Selection (MCP vs. Built-in)

**What GEPA Learns**:
- When MCP tools provide value over built-in
- Performance tradeoffs
- Capability requirements

**Example**:

**Before Optimization**:
```
All tools → MCP (slow initialization for simple tasks)
```

**After GEPA Optimization**:
```
Learned Decision Tree:
- File exists check → built-in (1ms)
- Read single file → built-in (10ms)
- Read directory recursively → MCP filesystem (powerful)
- Git operations → MCP github (required)
- Database queries → MCP postgres (specialized)
```

**Impact**: Optimal tool source for each operation type

---

### Protocol Call Optimization

**What GEPA Learns**:
- Optimal parameter structuring
- Efficient call sequencing
- Connection reuse

**Before Optimization**:
```
Each call:
1. Initialize MCP connection
2. Discover tools
3. Call tool
4. Close connection
```

**After GEPA Optimization**:
```
Learned Pattern:
1. Initialize connection once
2. Cache tool discovery
3. Reuse connection for multiple calls
4. Close after session

Result: 5x faster for multi-call scenarios
```

---

### Error Handling Patterns

**What GEPA Learns**:
- MCP-specific error types
- Recovery strategies
- Fallback approaches

**Before Optimization**:
```
MCP server not responding → Agent fails
```

**After GEPA Optimization**:
```
Learned Error Handling:
1. Connection timeout → Retry with backoff
2. Tool not found → Check MCP server status
3. Server crashed → Fall back to built-in tools
4. Permission denied → Explain and suggest alternatives
```

**Impact**: Robust operation even with protocol issues

---

## Before/After Comparison

### Scenario: Code File Analysis

**Query**: "Analyze all Python files in src/ directory for security issues"

**Available Tools**:
- Built-in: `file_reader`, `security_scanner`
- MCP: `mcp-server-filesystem` (recursive read), `mcp-server-github` (git context)

**Before Protocol Optimization**:
```
Tool Selection: Random or all built-in
Steps:
1. Try file_reader on "src/" → Fails (not recursive)
2. Agent gives up
Response: "Unable to analyze directory"
```

**After GEPA Protocol Optimization**:
```
GEPA-Learned Strategy:

Step 1: Recognize "all files in directory" → Requires recursive read
Tool: MCP filesystem server

Step 2: Read all .py files recursively
Result: 15 Python files found

Step 3: For each file → Use built-in security_scanner (faster)
Results: 3 files with SQL injection, 2 with hardcoded secrets

Step 4: Use MCP github → Get git context
Result: Files with issues were recently modified

Agent Response:
"Security Analysis Complete

Analyzed: 15 Python files in src/ directory

Critical Issues Found:
1. auth.py (Line 45): SQL injection
   [Modified: 2 days ago by dev@team.com]
   
2. config.py (Line 12): Hardcoded API key
   [Modified: 1 week ago by admin@team.com]
   
3. database.py (Line 89): SQL injection
   [Modified: 3 days ago by dev@team.com]

Recommendation: Review recent commits for security practices

Files Analyzed: 15
Issues Found: 5
High Priority: 3
Scan Time: 2.3s"
```

**Improvement**: From directory analysis failure → Comprehensive security audit

---

## Common MCP Optimization Patterns

### Pattern 1: Lazy Loading

**Before**: Initialize all MCP servers at startup  
**After**: "Initialize MCP servers only when needed, cache for session"

### Pattern 2: Capability-Based Routing

**Before**: Try built-in first, then MCP  
**After**: "Check required capability first. If MCP-only (like Git), go direct to MCP"

### Pattern 3: Batch Operations

**Before**: One MCP call per item  
**After**: "Batch similar operations into single MCP call when possible"

### Pattern 4: Connection Pooling

**Before**: New connection per request  
**After**: "Reuse connections across requests, maintain connection pool"

---

## Integration with Other Layers

Protocol optimization works synergistically:

**Protocols + Prompts**:
```
Optimized Prompt: "For Git operations, use MCP github server"
Optimized Protocol: Correct MCP server selection
→ Agent efficiently handles Git workflows
```

**Protocols + RAG**:
```
Optimized Protocol: MCP github → Get PR comments
Optimized RAG: Retrieves review guidelines doc
→ Agent provides review consistent with team standards + Git context
```

**Protocols + Tools**:
```
Optimized Protocol: MCP filesystem → Read files
Optimized Tools: Built-in security_scanner → Analyze content
→ Best of both: MCP power + Built-in speed
```

---

## Troubleshooting

### Issue: MCP Tools Always Used (Performance Penalty)

**Symptoms**: Even simple operations use MCP

**Solutions**:
1. Add RSpec-style BDD scenarios showing when NOT to use MCP
2. Enable built-in tools as alternatives
3. Add latency metrics to optimization
4. Use `--fresh` flag to see optimization decisions

### Issue: MCP Connection Failures

**Symptoms**: Protocol tools fail frequently

**Solutions**:
1. Implement retry logic in tool configuration
2. Enable fallback to built-in tools
3. Add connection health checks
4. Optimize error handling through GEPA

### Issue: Inefficient MCP Usage

**Symptoms**: Multiple connections for same session

**Solutions**:
1. Enable connection pooling
2. Cache tool discovery results
3. Batch similar operations
4. GEPA learns these patterns automatically

---

## Related Guides

- [💬 Prompt Optimization](prompts.md) - Optimize instructions
- [🔍 RAG Optimization](rag.md) - Optimize retrieval
- [🛠️ Tool Optimization](tools.md) - Optimize tool selection
- [🧠 Memory Optimization](memory.md) - Optimize context
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers
- [MCP Protocol Guide](../protocol-first-agents.md) - MCP setup
- [MCP + RAG Guide](../mcp-rag-complete-guide.md) - Combined optimization
- [MCP Optimization Tutorial](../../tutorials/mcp-optimization.md) - Step-by-step

---

**Next**: Learn how GEPA leverages [large-scale datasets →](datasets.md)

