# Tool Optimization

## What is Tool Optimization?

Tool optimization is the process of improving an agent's **tool selection**, **invocation order**, and **output combination** strategies. While traditional approaches hardcode which tools to use, GEPA learns dynamic, context-aware tool usage patterns.

**Key Insight**: Having tools isn't enough. The agent must learn WHICH tools to use for WHICH scenarios, in WHAT order, and HOW to combine their outputs for comprehensive results.

---

## The Tool Optimization Problem

### Without Optimization

**Scenario**: Agent reviewing code with high complexity

```
1. Agent receives nested conditional code
2. Agent has complexity_calculator tool available
3. Agent doesn't use it (doesn't know when to use tools)
4. Agent says: "Your code might be complex"
```

**Problem**: Tool available but not used, vague response

### With GEPA Optimization

**Scenario**: Same code review

```
1. Agent receives nested conditional code
2. GEPA-learned strategy: "Use complexity_calculator for nested conditions"
3. Agent uses tool: complexity_calculator(code)
4. Tool returns: complexity = 8
5. Agent says: "High complexity detected (8/4 threshold). Refactor to reduce nesting."
```

**Solution**: Correct tool used, specific metric provided, actionable feedback

---

## What GEPA Optimizes in Tool Usage

### 1. Tool Selection (Which Tools to Use)

**What It Is**: Learning which tool(s) to use for each scenario

**What GEPA Learns**:
- Pattern → Tool mapping
- When to use specific tools
- When to use multiple tools
- When to skip tools

**Example Configuration**:

```yaml
spec:
  tools:
    enabled: true
    specific_tools:
      - complexity_calculator    # Calculates cyclomatic complexity
      - security_scanner         # Detects vulnerabilities
      - performance_analyzer     # Identifies performance issues
      - code_smell_detector      # Finds code smells
```

**Before Optimization**:
```
Strategy: Random tool selection or no tool usage
Result: Tools used incorrectly or not at all
```

**After GEPA Optimization**:
```
Learned Strategies:
- "Use complexity_calculator when seeing nested if/for/while (>3 levels)"
- "Use security_scanner when detecting string concatenation in SQL/HTML"
- "Use performance_analyzer for loops with nested loops"
- "Use code_smell_detector for duplicated code patterns"
```

**Impact**: 0% → 100% correct tool selection

---

### 2. Tool Invocation Order (Orchestration)

**What It Is**: Learning the optimal sequence of tool calls

**What GEPA Learns**:
- Which tools to call first
- Dependencies between tools
- Parallel vs. sequential execution
- When to stop tool chain

**Before Optimization**:
```
Random order:
1. code_smell_detector (finds duplication)
2. complexity_calculator (finds complexity: 8)
3. security_scanner (finds SQL injection)
```

**After GEPA Optimization**:
```
Learned Priority Order:
1. security_scanner FIRST (critical issues)
   → Finds: SQL injection (CRITICAL)
2. complexity_calculator SECOND (maintainability)
   → Finds: Complexity 8 (MEDIUM)
3. code_smell_detector THIRD (code quality)
   → Finds: DRY violation (LOW)

Result: Prioritized by severity automatically
```

**Impact**: Logical ordering, priority-based findings

---

### 3. Output Combination (Multi-Tool Integration)

**What It Is**: Learning how to combine outputs from multiple tools

**What GEPA Learns**:
- How to merge tool results
- How to resolve conflicts
- How to synthesize comprehensive findings
- Citation format for tool outputs

**Example Scenario**: Code with multiple issues

**Before Optimization**:
```
Tool 1: complexity_calculator → "Complexity: 8"
Tool 2: security_scanner → "Potential injection"

Agent Response: "Complexity is 8. Potential injection found."
[Disconnected findings, no synthesis]
```

**After GEPA Optimization**:
```
Tool 1: complexity_calculator → "Complexity: 8"
Tool 2: security_scanner → "SQL injection detected"

Agent Response:
"Multiple issues detected:

1. SQL Injection (CRITICAL) [Tool: security_scanner]
   Line: query = 'SELECT...'
   Impact: Security breach possible
   
2. High Complexity (MEDIUM) [Tool: complexity_calculator]
   Complexity: 8/4 threshold
   Impact: Hard to maintain and test

RECOMMENDATION: Fix SQL injection first (security), then refactor (maintainability)"
```

**Impact**: Synthesized, prioritized findings vs. disconnected results

---

### 4. Error Handling and Fallbacks

**What It Is**: Learning how to handle tool failures gracefully

**What GEPA Learns**:
- What to do when tool fails
- Fallback strategies
- Error message interpretation
- Alternative tool selection

**Before Optimization**:
```
Tool fails → Agent gives up
"Unable to analyze code."
```

**After GEPA Optimization**:
```
Learned Strategies:
- Tool fails → Try alternative tool
- All tools fail → Use pattern matching from training data
- Partial failure → Continue with available results

Response: "Complexity tool unavailable. Based on pattern analysis: 
           Function has 6 nested conditions, likely high complexity. 
           Recommend refactoring."
```

**Impact**: Robust performance even when tools fail

---

## Before/After Comparison

### Scenario: Performance Code Review

**Input Code**:
```python
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates
```

**Before Tool Optimization**:
```
Tool Usage: None (agent doesn't know to use performance_analyzer)

Agent Response:
"This code could be more efficient."
```
- Vague
- No metrics
- No solution

**After GEPA Tool Optimization**:
```
Tool Usage:
1. performance_analyzer(code)
   → Detects: Nested loops, O(n²) complexity
   
2. complexity_calculator(code)
   → Returns: Cyclomatic complexity = 4

Learned Strategy: "Use both tools for loop analysis"

Agent Response:
"Performance Issue Detected

Complexity Analysis [Tool: complexity_calculator]:
- Cyclomatic Complexity: 4
- Nested loops detected

Performance Analysis [Tool: performance_analyzer]:
- Time Complexity: O(n²)
- Space Complexity: O(n)
- Issue: Nested iteration over same list

Impact: For 1000 items, 1,000,000 iterations

Optimized Solution (O(n)):
```python
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

Performance Improvement: O(n²) → O(n) (1000x faster for large lists)"
```

**Improvement**: From vague → Specific metrics + Executable solution

---

## How GEPA Learns Tool Strategies

### The Optimization Process

1. **Analysis Phase**
   ```
   GEPA Observes:
   - Agent saw nested loops but didn't use performance_analyzer
   - Agent gave vague "could be better" response
   - RSpec-style BDD scenario expected O(n²) mention and solution
   - Scenario FAILED
   ```

2. **Reflection Phase**
   ```
   GEPA Reflection:
   "The agent should use performance_analyzer when detecting nested loops.
    The tool would have identified O(n²) complexity and suggested O(n) solution.
    Need to learn: nested loops → performance_analyzer"
   ```

3. **Mutation Phase**
   ```
   GEPA Tests:
   - Strategy 1: "Always use performance_analyzer"
   - Strategy 2: "Use performance_analyzer when detecting loops"
   - Strategy 3: "Use performance_analyzer for nested loops only"
   ```

4. **Evaluation Phase**
   ```
   Results:
   - Strategy 1: 50% (too many false positives)
   - Strategy 2: 75% (good but misses single loops)
   - Strategy 3: 95% (precise!) ← Winner!
   ```

5. **Selection Phase**
   ```
   GEPA Keeps: Strategy 3
   Next: Learn to combine with complexity_calculator
   ```

**Result**: Learned precise tool selection patterns

---

## Best Practices

### 1. Provide Diverse Tool Categories

```yaml
tools:
  categories:
    - code_analysis    # Static analysis tools
    - security         # Security scanning tools
    - utilities        # General utilities
  specific_tools:
    - complexity_calculator
    - security_scanner
    - performance_analyzer
```

GEPA learns which category for which scenario.

### 2. Define Tool Purposes in RSpec-Style BDD

```yaml
feature_specifications:
  scenarios:
    - name: complexity_detection
      description: Agent should use complexity_calculator for nested code
      input:
        code: [Nested conditionals]
      expected_output:
        review: Must include "complexity: 8" (from tool)
```

GEPA learns: This scenario requires complexity_calculator.

### 3. Show Tool Usage in Datasets

```csv
code,review
"[nested loops]","Performance: O(n²) [Tool: performance_analyzer]"
"[SQL concat]","SQL Injection [Tool: security_scanner]"
```

GEPA learns tool patterns from real examples.

### 4. Enable Tool Reflection

```yaml
tools:
  max_iterations: 5    # Allow multi-step tool usage
  timeout: 30          # Per-tool timeout
```

---

## Common Tool Patterns GEPA Learns

### Pattern 1: Conditional Tool Usage

**Before**: Use tools randomly  
**After**: "Use complexity_calculator only for functions >5 lines with conditionals"

### Pattern 2: Tool Chaining

**Before**: Use one tool in isolation  
**After**: "Run security_scanner → If findings, use vulnerability_db for severity → Cite from knowledge base"

### Pattern 3: Tool Result Validation

**Before**: Trust tool output blindly  
**After**: "If complexity_calculator returns unexpected value, verify with manual pattern check"

### Pattern 4: Multi-Tool Synthesis

**Before**: Report each tool result separately  
**After**: "Combine security_scanner + complexity_calculator + code_smell_detector for comprehensive review"

---

## Metrics and Results

### What Gets Measured

- **Tool Selection Accuracy**: % of scenarios where correct tools used
- **Tool Usage Rate**: % of scenarios where tools should be used and are
- **Output Synthesis Quality**: % of multi-tool outputs properly combined
- **Error Handling**: % of tool failures handled gracefully

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Tool Selection Accuracy</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">25%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>100%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+75%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Tool Usage Rate</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+65%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Multi-Tool Synthesis</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">20%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+65%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Error Handling</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">0%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+90%</td>
	</tr>
</table>

---

## Quick Start

### Enable Tool Optimization

```yaml
spec:
  # Tool configuration
  tools:
    enabled: true
    categories:
      - code_analysis
      - security
    specific_tools:
      - complexity_calculator
      - security_scanner
  
  # GEPA automatically optimizes tool usage
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

GEPA will learn optimal tool selection strategies!

---

## Advanced: Tool-Specific Configuration

### Fine-Tune Tool Behavior

```yaml
tools:
  enabled: true
  max_iterations: 5        # Allow multi-step tool usage
  timeout: 30              # Per-tool timeout
  retry_on_failure: true   # Retry failed tools
  
  # Tool categories
  categories:
    - code_analysis
    - security
    - utilities
  
  # Specific tools with configs
  specific_tools:
    - name: complexity_calculator
      params:
        threshold: 4
    - name: security_scanner
      params:
        rules: ["sql-injection", "xss", "secrets"]
```

GEPA learns optimal parameters through optimization.

---

## Common Tool Strategies GEPA Learns

### Strategy 1: Pattern-Based Selection

**Before**: Use all tools for everything  
**After**: "Use security_scanner only when code contains: string concatenation, user input, DB queries, file operations"

### Strategy 2: Progressive Tool Usage

**Before**: Use all tools upfront  
**After**: "Start with security_scanner. If issues found, then use vulnerability_db for details. If no security issues, check complexity_calculator"

### Strategy 3: Tool Result Interpretation

**Before**: Report tool output verbatim  
**After**: "Complexity: 8 → Explain: 'This exceeds threshold of 4, making code hard to test. Recommend refactoring.'"

### Strategy 4: Multi-Tool Combination

**Before**: Report each tool separately  
**After**: "Combine security_scanner + complexity_calculator → Comprehensive review: 'Code has CRITICAL security issue (priority 1) and MEDIUM complexity issue (priority 2)'"

---

## Integration with Other Layers

Tool optimization amplifies other optimizations:

**Tools + Prompts**:
```
Optimized Prompt: "Use complexity_calculator for nested conditions"
Optimized Tool: Correctly identifies nested conditions → Calls tool
→ Agent provides metric-driven feedback
```

**Tools + RAG**:
```
Optimized RAG: Retrieves complexity best practices doc
Optimized Tool: Calculates actual complexity = 8
→ Agent says: "Your complexity (8) exceeds recommended (4) per Clean Code guidelines"
```

**Tools + Memory**:
```
Optimized Memory: Recalls "Previous similar code had complexity 7, we refactored"
Optimized Tool: Calculates current complexity = 8
→ Agent says: "Similar to issue #47 (complexity 7). Recommend same refactoring approach"
```

---

## Real-World Example

### Use Case: Comprehensive Code Analysis

**Available Tools**:
- `complexity_calculator` - Cyclomatic complexity
- `security_scanner` - Vulnerability detection
- `performance_analyzer` - Performance patterns
- `code_smell_detector` - Code quality issues

**Input Code**:
```python
password = "admin123"  # Hardcoded secret

def login(user):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE username='" + user + "'"
    result = db.execute(query)
    
    # High complexity (nested conditionals)
    if result:
        if result['password'] == password:
            if result['active']:
                if result['verified']:
                    return True
    return False
```

**Before Tool Optimization**:
```
Tool Usage: None (doesn't know which tools to use)

Response: "Your code has some issues."
```

**After GEPA Tool Optimization**:
```
Learned Multi-Tool Strategy:

Step 1: security_scanner
→ Detects: Hardcoded password, SQL injection, plaintext password check

Step 2: complexity_calculator  
→ Calculates: Cyclomatic complexity = 5

Step 3: Synthesis
→ Prioritizes: Security (CRITICAL) before complexity (MEDIUM)

Agent Response:
"Multiple Critical Issues Detected

1. Hardcoded Credentials (CRITICAL) [Tool: security_scanner]
   Line: password = 'admin123'
   Risk: Security breach if code exposed
   
2. SQL Injection (CRITICAL) [Tool: security_scanner]
   Line: query = 'SELECT...' + user + '...'
   Risk: Database compromise possible
   
3. Plaintext Password Comparison (CRITICAL) [Tool: security_scanner]
   Line: result['password'] == password
   Risk: Passwords should be hashed
   
4. High Cyclomatic Complexity (MEDIUM) [Tool: complexity_calculator]
   Complexity: 5/4 threshold
   Issue: Nested conditionals reduce maintainability

PRIORITY:
1. Fix security issues immediately (3 CRITICAL)
2. Refactor complexity after security fixed"
```

**Improvement**: From no tool usage → Strategic multi-tool orchestration

---

## How GEPA Learns Tool Strategies

### Example: Learning to Use complexity_calculator

**Iteration 1**:
```
Scenario: Code with nested conditionals
Agent: Doesn't use complexity_calculator
Result: FAIL (expected "complexity: 5" in output)

GEPA Reflection:
"Agent failed to use complexity_calculator for nested conditionals.
 Tool is available but not invoked. Need to learn pattern."
```

**Iteration 2**:
```
Modified Prompt: "For code with if/else statements, use complexity_calculator"
Agent: Uses tool for ALL if statements (even simple ones)
Result: PARTIAL (too broad, slow)

GEPA Reflection:
"Tool usage too aggressive. Should only use for nested (>3 levels)"
```

**Iteration 3**:
```
Refined Prompt: "Use complexity_calculator when detecting >3 nested conditionals"
Agent: Uses tool selectively for complex code only
Result: PASS (100% accuracy)

GEPA: Strategy learned! Keep this pattern.
```

**Result**: Learned precise tool invocation pattern through reflection

---

## Troubleshooting

### Issue: Tools Not Being Used

**Symptoms**: Agent has tools but doesn't call them

**Solutions**:
1. Add RSpec-style BDD scenarios requiring tool outputs
2. Include tool usage examples in datasets
3. Increase optimization iterations
4. Check tool registration is working

### Issue: Wrong Tools Used

**Symptoms**: Agent uses inappropriate tools for scenarios

**Solutions**:
1. Add more specific RSpec-style BDD scenarios
2. Increase training examples showing correct tool usage
3. Use tool categories to group related tools
4. Add tool descriptions to help GEPA understand purpose

### Issue: Tool Outputs Not Integrated

**Symptoms**: Tool called but output not used in response

**Solutions**:
1. Require tool outputs in expected_output of RSpec-style BDD scenarios
2. Optimize prompts to include "cite tool results"
3. Add examples showing proper tool citation

---

## Related Guides

- [💬 Prompt Optimization](prompts.md) - Optimize instructions
- [🔍 RAG Optimization](rag.md) - Optimize knowledge retrieval
- [🧠 Memory Optimization](memory.md) - Optimize context
- [🔌 Protocol Optimization](protocols.md) - Optimize MCP usage
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers
- [Tool Development Guide](../tool-development.md) - Create custom tools
- [MCP Optimization Tutorial](../../tutorials/mcp-optimization.md) - Advanced tool protocols

---

**Next**: Learn how GEPA optimizes [memory and context selection →](memory.md)

