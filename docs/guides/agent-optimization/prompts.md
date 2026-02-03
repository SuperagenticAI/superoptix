# Prompt Optimization

## What is Prompt Optimization?

Prompt optimization is the process of improving an agent's core instructions, persona definition, reasoning patterns, and response formatting to produce better outputs. This is the **foundation layer** of agent optimization.

**Key Insight**: GEPA doesn't just tweak prompt text. It learns **strategies** for how to structure instructions, when to use reasoning, and how to format responses for maximum clarity and effectiveness.

---

## What GEPA Optimizes in Prompts

### 1. Persona and Role Definition

**What It Is**: The agent's identity, role, and behavioral guidelines

**What GEPA Learns**:
- Role clarity and specificity
- Goal articulation
- Communication style
- Domain expertise framing

**Example Configuration**:

```yaml
spec:
  persona:
    role: Senior Software Engineer & Security Reviewer
    goal: Provide thorough, actionable code reviews
    traits:
      - detail-oriented
      - security-conscious
      - constructive
```

**Before Optimization**:
```
role: Code Reviewer
goal: Review code
```

**After GEPA Optimization**:
```
role: Senior Software Engineer & Security Reviewer
goal: Provide thorough, actionable code reviews that improve security, 
     performance, and maintainability with specific solutions
traits: [detail-oriented, security-conscious, constructive, pragmatic]
```

**Impact**: More focused, professional reviews with clear authority

---

### 2. Task Instructions

**What It Is**: Core instructions for each agent task

**What GEPA Learns**:
- Instruction clarity
- Step specification
- Output requirements
- Success criteria

**Example**:

```yaml
tasks:
  - name: review_code
    instruction: |
      Analyze the code for:
      1. Security vulnerabilities (SQL injection, XSS, hardcoded secrets)
      2. Performance issues (O(n²) complexity, inefficient loops)
      3. Code quality (cyclomatic complexity, duplication, naming)
      
      For each issue:
      - Identify the specific line/pattern
      - Explain why it's problematic
      - Provide a concrete solution with code example
      - Cite relevant documentation or standards
```

**Before Optimization**:
```
instruction: Review the code and find problems
```

**After GEPA Optimization**:
```
instruction: |
  Analyze code systematically:
  1. Security: Check for OWASP Top 10 vulnerabilities
  2. Performance: Identify O(n²) or worse complexity
  3. Quality: Calculate cyclomatic complexity (threshold: 4)
  
  For each finding:
  - Specify exact line and pattern
  - Explain impact (security risk, performance cost, etc.)
  - Provide executable solution with code
  - Reference standards (OWASP, PEP 8, etc.)
```

**Impact**: Structured, comprehensive reviews vs. vague suggestions

---

### 3. Reasoning Patterns

**What It Is**: Chain-of-thought, step-by-step thinking process

**What GEPA Learns**:
- When to use chain-of-thought
- How many reasoning steps
- Depth of analysis
- Thinking structure

**Example**:

```yaml
reasoning:
  style: chain_of_thought
  steps:
    - Scan code for security patterns
    - Calculate complexity metrics
    - Check against best practices
    - Prioritize findings by severity
    - Formulate actionable recommendations
```

**Before Optimization**:
```
Agent thinks implicitly, inconsistent analysis
```

**After GEPA Optimization**:
```
Agent follows explicit reasoning steps:
1. Scan for security patterns (SQL concatenation, hardcoded secrets)
2. Run complexity analysis (cyclomatic complexity, nesting depth)
3. Check best practices (naming, error handling, DRY)
4. Prioritize by severity (critical > high > medium > low)
5. Generate solutions with code examples
```

**Impact**: Consistent, thorough analysis every time

---

### 4. Response Formatting

**What It Is**: How the agent structures its output

**What GEPA Learns**:
- Response organization
- Level of detail
- Code example formatting
- Citation style

**Example Output Structure**:

```yaml
output_fields:
  - name: review
    type: str
    description: Comprehensive code review with structured findings
  - name: severity
    type: str
    description: Overall severity (critical, high, medium, low)
  - name: recommendations
    type: list
    description: Prioritized action items
```

**Before Optimization**:
```
"Your code has some issues. Check for SQL injection and complexity."
```

**After GEPA Optimization**:
```
SEVERITY: CRITICAL

FINDINGS:

1. SQL Injection Vulnerability (CRITICAL)
   Line: query = "SELECT * FROM users WHERE name = '" + username + "'"
   Issue: User input concatenated directly into SQL query
   Solution:
   ```python
   query = "SELECT * FROM users WHERE name = ?"
   result = db.execute(query, (username,))
   ```
   Reference: OWASP Top 10 #1

2. High Cyclomatic Complexity (MEDIUM)
   Function: login()
   Complexity: 8 (threshold: 4)
   Issue: Too many nested conditions
   Solution: Use early returns
   ```python
   if not result: return False
   if not result['active']: return False
   return True
   ```

RECOMMENDATIONS:
1. Fix SQL injection immediately (security risk)
2. Refactor login() to reduce complexity (maintainability)
```

**Impact**: Actionable, professional reviews vs. vague suggestions

---

## Before/After Comparison

### Scenario: Code Review Request

**Input Code**:
```python
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
```

**Before Prompt Optimization**:
```
"Your code might have security issues. Consider using better practices."
```
- Vague
- No specific issue identified
- No solution provided
- Not actionable

**After GEPA Prompt Optimization**:
```
SEVERITY: CRITICAL

FINDING: SQL Injection Vulnerability

Line: query = "SELECT * FROM users WHERE name = '" + username + "'"

Issue: User input (username) is concatenated directly into SQL query without 
       sanitization, allowing attackers to inject malicious SQL code.

Attack Example:
  username = "admin' OR '1'='1"
  → Returns all users, bypassing authentication

Solution:
```python
def get_user(username):
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (username,))
```

Why This Works:
- Parameterized queries prevent SQL injection
- Database driver handles escaping automatically
- Industry standard (OWASP recommendation)

Reference: OWASP Top 10 2024 - Injection Attacks (#1)
```
- Specific issue identified
- Attack scenario explained
- Executable solution provided
- Standards cited

**Improvement**: From 0% helpful → 100% actionable

---

## How GEPA Learns Prompt Strategies

### The Optimization Process

1. **Analysis Phase**
   - GEPA evaluates agent responses
   - Identifies vague or incomplete reviews
   - Notes missing elements (severity, solutions, citations)

2. **Reflection Phase**
   ```
   GEPA Reflection:
   "The agent identified 'security issue' but didn't specify SQL injection.
    It didn't provide a code solution or cite OWASP standards.
    Need more specific instructions for security findings."
   ```

3. **Mutation Phase**
   - Generates improved prompt variations
   - Tests: "Always specify exact vulnerability type (SQL injection, XSS, etc.)"
   - Tests: "Provide executable code solutions"
   - Tests: "Cite security standards (OWASP, CWE)"

4. **Selection Phase**
   - Evaluates each variation
   - Selects best-performing prompts
   - Keeps improvements, discards regressions

5. **Iteration**
   - Repeats process
   - Compounds improvements
   - Converges on optimal prompts

**Result**: Learned prompt strategies, not just text tweaks

---

## Best Practices

### 1. Start with Clear Base Prompts

```yaml
# Good starting point
persona:
  role: [Specific role with expertise level]
  goal: [Clear, measurable objective]
  traits: [Relevant characteristics]

tasks:
  - instruction: [Step-by-step process, not vague request]
```

### 2. Define Expected Output Format

```yaml
output_fields:
  - name: finding
    description: Specific issue identified
  - name: severity
    description: Impact level
  - name: solution
    description: Executable fix with code
```

GEPA will learn to match this structure consistently.

### 3. Provide RSpec-Style BDD Scenarios

```yaml
feature_specifications:
  scenarios:
    - name: security_detection
      description: Agent should detect and explain security issues
      input:
        code: [Code with SQL injection]
      expected_output:
        review: Must mention "SQL injection" and "parameterized queries"
        severity: critical
```

GEPA optimizes prompts to match these specifications.

### 4. Use Datasets for Real-World Patterns

```yaml
datasets:
  - source: ./data/real_reviews.csv
    limit: 100
```

GEPA learns effective phrasing from real examples.

---

## Common Patterns GEPA Learns

### Pattern 1: Specificity Over Generality

**Before**: "Check for issues"  
**After**: "Check for: SQL injection, XSS, hardcoded secrets, complexity > 4"

### Pattern 2: Actionability

**Before**: "This could be better"  
**After**: "Replace X with Y. Here's the code: [executable solution]"

### Pattern 3: Citations

**Before**: "This is bad practice"  
**After**: "Violates SOLID principles (reference: Clean Code, Chapter 3)"

### Pattern 4: Structured Output

**Before**: Freeform text response  
**After**: Severity → Findings → Solutions → References

---

## Metrics and Results

### What Gets Measured

- **Specificity**: % of responses with specific issue identification
- **Actionability**: % of responses with executable solutions
- **Citation Rate**: % of responses with references
- **Format Compliance**: % matching expected output structure

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Response Specificity</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+60%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Actionable Solutions</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">20%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+65%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Citation Rate</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">10%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>75%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+65%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Format Compliance</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">40%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
</table>

---

## Quick Start

### Enable Prompt Optimization

Prompts are automatically optimized when you run GEPA:

```bash
# 1. Create agent with good base prompts
super spec generate code_reviewer --template genie

# 2. Compile
super agent compile code_reviewer

# 3. Evaluate baseline
super agent evaluate code_reviewer

# 4. Optimize prompts (and other enabled layers)
super agent optimize code_reviewer --auto medium

# 5. See improvement
super agent evaluate code_reviewer  # automatically loads optimized weights
```

GEPA automatically optimizes all prompts in your playbook!

---

## Advanced: Prompt-Specific Tuning

### Control What GEPA Optimizes

```yaml
optimization:
  optimizer:
    name: GEPA
    params:
      # Focus on prompts
      variables_to_optimize:
        - persona.role
        - persona.goal
        - tasks[*].instruction
```

### Optimization Intensity

```yaml
optimization:
  optimizer:
    params:
      auto: light      # Quick prompt tweaks (3-5 iterations)
      auto: medium     # Balanced optimization (10-15 iterations)
      auto: intensive  # Thorough exploration (20-30 iterations)
```

---

## Common Prompt Improvements

### Improvement 1: Adding Specificity

**Before**: "Analyze the code"  
**After**: "Analyze code for: (1) Security vulnerabilities per OWASP Top 10, (2) Performance issues with O(n) or worse complexity, (3) Code quality issues with cyclomatic complexity > 4"

### Improvement 2: Adding Structure

**Before**: "Provide feedback"  
**After**: "Structure review as: Severity → Findings (line number, issue, impact) → Solutions (code example) → References (standards)"

### Improvement 3: Adding Examples

**Before**: "Suggest improvements"  
**After**: "Suggest improvements with before/after code examples showing exact changes needed"

### Improvement 4: Adding Context

**Before**: "Review code quality"  
**After**: "Review code quality considering: project type, team size, production criticality, industry standards"

---

## Integration with Other Layers

Prompt optimization works best when combined with other layers:

**Prompt + RAG**:
```
Prompt: "Search security documentation before analyzing SQL queries"
→ Combines optimized instructions with optimized retrieval
```

**Prompt + Tools**:
```
Prompt: "Use complexity_calculator for nested conditions exceeding 3 levels"
→ Combines optimized instructions with optimized tool selection
```

**Prompt + Memory**:
```
Prompt: "Reference similar past findings when identifying patterns"
→ Combines optimized instructions with optimized memory retrieval
```

---

## Troubleshooting

### Issue: Prompts Not Improving

**Symptoms**: Optimization runs but prompts stay similar

**Solutions**:
1. Check RSpec-style BDD scenarios are specific enough
2. Ensure datasets have diverse examples
3. Increase iterations: `--auto intensive`
4. Add reflection_lm: `--reflection-lm llama3.1:8b`

### Issue: Prompts Too Long

**Symptoms**: Optimized prompts exceed token limits

**Solutions**:
1. Set max_tokens constraint in optimization config
2. Use summarization in optimization params
3. Focus on key instructions, not exhaustive lists

### Issue: Inconsistent Format

**Symptoms**: Agent responses vary in structure

**Solutions**:
1. Define strict output_fields schema
2. Add format examples in RSpec-style BDD scenarios
3. Use structured output in task configuration

---

## Related Guides

- [🔍 RAG Optimization](rag.md) - Optimize knowledge retrieval
- [🛠️ Tool Optimization](tools.md) - Optimize tool selection
- [🧠 Memory Optimization](memory.md) - Optimize context selection
- [📊 Dataset-Driven Optimization](datasets.md) - Train on large-scale data
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers together
- [GEPA Optimizer Guide](../gepa-optimization.md) - Technical details
- [SuperSpec DSL](../superspec.md) - Playbook configuration

---

**Next**: Learn how GEPA optimizes [RAG retrieval strategies →](rag.md)

