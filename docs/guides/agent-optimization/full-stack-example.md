# Full-Stack Optimization: Complete Example

## Overview

This guide shows how **all 6 optimization layers** work together in a real production agent. We'll use a **Code Review Agent** as our example because it demonstrates every optimization layer naturally.

**What You'll See**:
- How each layer contributes to the final result
- The compound effect of multi-layer optimization
- Before/after comparisons at each layer
- Complete end-to-end workflow

---

## The Use Case: Code Review Agent

### Agent Purpose

Analyze code for security vulnerabilities, performance issues, and code quality problems, providing actionable recommendations with code examples.

### Why This Example?

Code review requires ALL optimization layers:
- **Prompts**: How to structure comprehensive reviews
- **RAG**: When to search security/performance documentation
- **Tools**: Which analysis tools to use (complexity, security scanning)
- **Memory**: Recall similar past findings
- **Protocols**: Use MCP for advanced file operations
- **Datasets**: Learn from 100 real GitHub code reviews

---

## The Agent Configuration

### Full Playbook Structure

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Code Review Assistant
  level: genies

spec:
  # Language Model
  language_model:
    provider: ollama
    model: qwen3.5:9b
  
  # Layer 1: Prompts (always optimized)
  persona:
    role: Senior Software Engineer & Security Reviewer
    goal: Provide thorough, actionable code reviews
    traits: [detail-oriented, security-conscious, constructive]
  
  # Layer 2: RAG (knowledge retrieval)
  rag:
    enabled: true
    knowledge_base:
      - ./knowledge/security/*.md
      - ./knowledge/performance/*.md
      - ./knowledge/best_practices/*.md
    top_k: 5
  
  # Layer 3: Tools (analysis capabilities)
  tools:
    enabled: true
    specific_tools:
      - complexity_calculator
      - security_scanner
      - performance_analyzer
  
  # Layer 4: Memory (context from past reviews)
  memory:
    enabled: true
    enable_context_optimization: true
    max_context_tokens: 2000
  
  # Layer 5: Protocols (MCP for advanced ops)
  # (Can be added if needed)
  
  # Layer 6: Datasets (learn from real reviews)
  datasets:
    - name: github_reviews
      source: ./data/real_code_reviews.csv
      limit: 100
  
  # GEPA optimizes ALL layers
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium
```

---

## The Test Input: Complex Real-World Code

```python
# Production authentication code with multiple issues
password = "admin123"  # Issue 1: Hardcoded credential

def authenticate_user(username):
    # Issue 2: SQL injection via string concatenation
    query = "SELECT * FROM users WHERE username='" + username + "'"
    result = db.execute(query)
    
    # Issue 3: High cyclomatic complexity (nested conditionals)
    if result:
        if result['password'] == password:  # Issue 4: Plaintext password
            if result['active']:
                if result['verified']:
                    if result['subscription'] == 'premium':
                        return True
    return False
```

**Issues Present**:
1. Hardcoded password (CRITICAL)
2. SQL injection (CRITICAL)
3. Plaintext password comparison (CRITICAL)
4. High cyclomatic complexity (MEDIUM)

---

## Baseline Performance (Before Optimization)

### Initial Agent Behavior

```bash
super agent compile code_review_assistant
super agent evaluate code_review_assistant
```

**Result**:
```
Testing 8 RSpec-style BDD scenarios:

SQL Injection Detection: FAIL
   Expected: Specific vulnerability with solution
   Got: "Check your SQL queries"

Hardcoded Credentials: FAIL
   Expected: Identify hardcoded secret with env var solution
   Got: Generic "use better practices"

Complexity Analysis: PASS
   (Agent happened to mention complexity)

Security Comprehensive: FAIL
   Expected: All 3 security issues identified
   Got: Only 1 issue found

Overall: 1/8 PASS (12.5%)
```

**Agent Output** (Baseline):
```
"Your code has some security issues and could be improved."
```

**Problems**:
- Extremely vague
- No specific issues identified
- No solutions provided
- Not actionable
- No tool usage
- No knowledge retrieval
- No past context referenced

---

## Layer-by-Layer Optimization

### Step 1: Run GEPA Optimization

```bash
super agent optimize code_review_assistant --auto medium --fresh
```

**What Happens**: GEPA optimizes all 6 layers simultaneously

---

### Layer 1: Prompt Optimization in Action

**GEPA Reflection (Iteration 3)**:
```
"Agent gave vague 'security issues' response. Need specific vulnerability 
 identification. Optimize persona to include security expertise and goal 
 to include 'specific findings with severity classification'."
```

**Prompt Evolution**:

**Before**:
```yaml
persona:
  role: Code Reviewer
  goal: Find code issues
```

**After GEPA**:
```yaml
persona:
  role: Senior Software Engineer & Security Reviewer with expertise in 
       OWASP Top 10, secure coding, and performance optimization
  goal: Identify specific security vulnerabilities, performance bottlenecks, 
       and code quality issues with severity classification and executable 
       solutions
```

**Result**: Agent now knows to be specific and provide solutions

---

### Layer 2: RAG Optimization in Action

**GEPA Reflection (Iteration 5)**:
```
"Agent should search security documentation BEFORE analyzing SQL queries.
 Pattern: String concatenation in SQL context → Retrieve sql_injection.md"
```

**RAG Strategy Evolution**:

**Before**:
```
Query: Generic "code review"
Retrieved: random_doc.md, naming_conventions.md, testing.md
Relevance: 25% (wrong topics)
```

**After GEPA**:
```
Learned Strategy:
- Detect: String concatenation + SQL keywords
- Query: "SQL injection prevention parameterized queries OWASP"
- Retrieved: sql_injection.md, database_security.md, owasp_a03.md
- Relevance: 95% (perfect match)
```

**Result**: Agent retrieves exact security docs needed

---

### Layer 3: Tool Optimization in Action

**GEPA Reflection (Iteration 7)**:
```
"Agent should use complexity_calculator for nested conditions.
 Pattern: >3 nested if statements → Use complexity_calculator
 Then cite threshold violation in review."
```

**Tool Usage Evolution**:

**Before**:
```
Tools Available: complexity_calculator, security_scanner
Tools Used: None
Result: No metrics, vague assessment
```

**After GEPA**:
```
Learned Strategy:
1. Detect nested conditionals → Use complexity_calculator
2. Detect string concatenation in SQL → Use security_scanner
3. Combine results for comprehensive review

Tools Used:
- complexity_calculator → Returns: complexity = 5
- security_scanner → Returns: [SQL injection, hardcoded secret]
```

**Result**: Metric-driven, tool-backed findings

---

### Layer 4: Memory Optimization in Action

**GEPA Reflection (Iteration 9)**:
```
"Agent should reference similar past SQL injection findings.
 Memory optimization should prioritize high-importance security memories."
```

**Memory Selection Evolution**:

**Before**:
```
Memories: Last 10 reviews chronologically
Relevance: 30% (mostly irrelevant)
```

**After GEPA**:
```
Learned Strategy:
Query: "SQL injection"
Selected Memories:
- Memory #47: Previous SQL injection in auth code (0.95 similarity)
- Memory #23: Parameterized query pattern used before (0.88 similarity)
- Memory #61: Team security standard (0.82 similarity, high importance)

Result: Highly relevant past context
```

**Result**: Agent says "Similar to previous finding #47. Use parameterized queries as recommended before."

---

### Layer 5: Protocol Optimization in Action

**GEPA Reflection (Iteration 11)**:
```
"For simple code snippets, use built-in tools (faster).
 For file system operations, use MCP when recursive or complex."
```

**Protocol Strategy Evolution**:

**Before**:
```
Always initialize MCP → Slow startup (500ms overhead)
```

**After GEPA**:
```
Learned Strategy:
- Single code snippet → Use built-in tools (fast)
- Directory analysis → Use MCP filesystem (powerful)
- Git context needed → Use MCP github (required)

Current query: Single code snippet
Tool: built-in security_scanner (50ms vs. 500ms)
```

**Result**: Optimal tool source selection

---

### Layer 6: Dataset Learning in Action

**GEPA Learning from 100 Real Reviews**:

```
Pattern Extraction:
- 85% of expert reviews cite OWASP standards
- 90% provide executable code solutions
- 75% include attack examples for critical issues
- 95% classify severity based on exploitability
- 80% prioritize security over code quality

Agent Learns:
→ Always cite OWASP for web security
→ Provide code solutions with imports
→ Show attack vector for CRITICAL issues
→ Classify: CRITICAL > HIGH > MEDIUM > LOW
→ Prioritize security in recommendations
```

**Result**: Agent review style matches expert reviews

---

## Final Optimized Performance

### Re-Evaluation After Optimization

```bash
super agent evaluate code_review_assistant  # automatically loads optimized weights
```

**Result**:
```
Testing 8 RSpec-style BDD scenarios:

SQL Injection Detection: PASS
   ✓ Identified SQL injection with specific attack example
   ✓ Provided parameterized query solution
   ✓ Cited OWASP Top 10 #1

Hardcoded Credentials: PASS
   ✓ Found hardcoded password
   ✓ Recommended environment variables
   ✓ Cited CWE-798

Complexity Analysis: PASS
   ✓ Used complexity_calculator tool
   ✓ Reported complexity 5/4 threshold
   ✓ Suggested early returns pattern

Security Comprehensive: PASS
   ✓ Found all 3 security issues
   ✓ Prioritized by severity
   ✓ Cited OWASP standards

Performance Issues: PASS
Memory Reference: PASS
Multi-Issue Handling: PASS
Professional Format: PASS

Overall: 8/8 PASS (100%)
Improvement: +87.5% (12.5% → 100%)
```

---

## Complete Optimized Agent Output

### Live Query Result

```bash
super agent run code_review_assistant --code "[authentication code above]"
```

**Complete Agent Response** (All Layers Working Together):

```
═══════════════════════════════════════════════════════════════════════════
SECURITY CODE REVIEW RESULTS
═══════════════════════════════════════════════════════════════════════════

OVERALL SEVERITY: 🔴 CRITICAL

📋 CRITICAL ISSUES (Fix Before Deployment):

1. Hardcoded Database Credential (Line 2)
   ─────────────────────────────────────────────────────────────────────
   Code: password = "admin123"
   
   🎯 Issue [Tool: security_scanner]:
   Sensitive credential stored directly in source code
   
   ⚠️  Risk:
   - Credential exposed if code repository accessed
   - Security breach if code deployed to production
   - Violates security compliance standards
   
   Solution:
   ```python
   import os
   password = os.environ.get('DB_PASSWORD')
   if not password:
       raise ValueError("DB_PASSWORD environment variable not set")
   ```
   
   📚 Reference [Retrieved from: knowledge/security/hardcoded_secrets.md]:
   - OWASP ASVS 2.7.1: Credentials must not be hardcoded
   - CWE-798: Use of Hard-coded Credentials
   - Similar to: Previous finding #61 (resolved with env vars)

2. SQL Injection Vulnerability (Line 5)
   ─────────────────────────────────────────────────────────────────────
   Code: query = "SELECT * FROM users WHERE username='" + username + "'"
   
   🎯 Issue [Tool: security_scanner]:
   User input concatenated directly into SQL query
   
   ⚠️  Attack Example:
   Input: username = "admin' OR '1'='1"
   Result: SELECT * FROM users WHERE username='admin' OR '1'='1'
   Impact: Returns ALL users, authentication bypass
   
   Solution:
   ```python
   def authenticate_user(username):
       query = "SELECT * FROM users WHERE username = ?"
       result = db.execute(query, (username,))
   ```
   
   📚 Reference [Retrieved from: knowledge/security/sql_injection.md]:
   - OWASP Top 10 2024: #1 Injection
   - CWE-89: SQL Injection
   - Parameterized queries prevent all injection attacks
   - Similar to: Previous finding #47 (parameterized queries recommended)

3. Plaintext Password Comparison (Line 7)
   ─────────────────────────────────────────────────────────────────────
   Code: if result['password'] == password
   
   🎯 Issue [Tool: security_scanner]:
   Direct password comparison without hashing
   
   ⚠️  Risk:
   - Passwords stored in plaintext in database
   - Timing attack vulnerability (password length leak)
   - Complete compromise if database breached
   
   Solution:
   ```python
   import bcrypt
   
   # When storing password:
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   
   # When verifying:
   if bcrypt.checkpw(password.encode(), result['password_hash']):
       return True
   ```
   
   📚 Reference [Retrieved from: knowledge/security/password_hashing.md]:
   - OWASP ASVS 2.4.1: Passwords must be hashed with bcrypt/Argon2
   - Use constant-time comparison to prevent timing attacks

═══════════════════════════════════════════════════════════════════════════

📊 MEDIUM PRIORITY ISSUES:

4. High Cyclomatic Complexity (Lines 7-12)
   ─────────────────────────────────────────────────────────────────────
   Function: authenticate_user()
   
   🎯 Metrics [Tool: complexity_calculator]:
   - Cyclomatic Complexity: 5
   - Recommended Threshold: 4
   - Nesting Depth: 5 levels
   
   ⚠️  Impact:
   - Hard to test (2^5 = 32 test cases needed)
   - Difficult to maintain
   - Error-prone modifications
   
   Solution (Early Returns Pattern):
   ```python
   def authenticate_user(username):
       query = "SELECT * FROM users WHERE username = ?"
       result = db.execute(query, (username,))
       
       if not result:
           return False
       if not bcrypt.checkpw(password.encode(), result['password_hash']):
           return False
       if not result['active']:
           return False
       if not result['verified']:
           return False
       if result['subscription'] != 'premium':
           return False
       
       return True
   ```
   
   📚 Reference [Retrieved from: knowledge/best_practices/code_smells.md]:
   - Clean Code: Cyclomatic complexity should be <4
   - Early returns reduce nesting and improve readability
   - Similar to: Issue #23 (refactored using early returns)

═══════════════════════════════════════════════════════════════════════════

📊 ANALYSIS METRICS:

Lines Analyzed: 13
Issues Found: 4
  - CRITICAL: 3
  - HIGH: 0
  - MEDIUM: 1
  - LOW: 0

Tool Usage:
  - security_scanner: 3 findings
  - complexity_calculator: 1 finding

Knowledge Retrieved:
  - security/sql_injection.md (0.94 relevance)
  - security/hardcoded_secrets.md (0.91 relevance)
  - security/password_hashing.md (0.89 relevance)
  - best_practices/code_smells.md (0.87 relevance)

Memory References:
  - Issue #47: SQL injection (similar pattern)
  - Issue #61: Hardcoded credentials (team standard)
  - Issue #23: Complexity refactoring (same solution)

Analysis Time: 2.8 seconds

═══════════════════════════════════════════════════════════════════════════

🎯 RECOMMENDATIONS (Priority Order):

IMMEDIATE (Deploy Blockers):
1. Fix SQL injection (Line 5) - CRITICAL security risk
2. Remove hardcoded password (Line 2) - CRITICAL exposure
3. Implement password hashing (Line 7) - CRITICAL crypto failure

BEFORE NEXT RELEASE:
4. Refactor complexity (Lines 7-12) - Maintainability

STANDARDS COMPLIANCE CHECK:
OWASP Top 10 #1: Injection - VIOLATED
OWASP ASVS 2.4.1: Password Hashing - VIOLATED
OWASP ASVS 2.7.1: Hardcoded Credentials - VIOLATED
⚠️  Clean Code: Complexity Threshold - EXCEEDED

RISK LEVEL: 🔴 DEPLOY BLOCKED (3 critical security issues)

═══════════════════════════════════════════════════════════════════════════

📚 REFERENCES & RESOURCES:

Security:
- OWASP Top 10 2024: https://owasp.org/Top10
- SQL Injection Prevention: [Local: knowledge/security/sql_injection.md]
- Password Security: [Local: knowledge/security/password_hashing.md]

Code Quality:
- Clean Code (Martin): Chapter 3 (Functions)
- Cyclomatic Complexity: https://en.wikipedia.org/wiki/Cyclomatic_complexity

Team Standards:
- Previous similar findings: #23, #47, #61
- Security review checklist: ./docs/security_checklist.md

═══════════════════════════════════════════════════════════════════════════
```

---

## Layer-by-Layer Breakdown

### How Each Layer Contributed

**1. Prompts** 💬:
- Learned to structure reviews: Severity → Findings → Solutions → References
- Learned to quantify impact: "2^5 = 32 test cases needed"
- Learned to prioritize: CRITICAL before MEDIUM

**2. RAG** 🔍:
- Searched security docs when detecting SQL concatenation
- Retrieved 4 highly relevant docs (>0.87 similarity)
- Integrated citations naturally: "[Retrieved from: sql_injection.md]"

**3. Tools** 🛠️:
- Used security_scanner for vulnerability detection
- Used complexity_calculator for metrics
- Combined tool outputs: "3 security + 1 complexity findings"

**4. Memory** 🧠:
- Recalled similar past findings (#23, #47, #61)
- Referenced team standards and previous solutions
- Selected only relevant memories (3/50 selected)

**5. Protocols** 🔌:
- Used built-in tools (code snippet analysis, no MCP needed)
- Would use MCP for directory scanning or Git context

**6. Datasets** 📊:
- Learned professional phrasing from 100 real reviews
- Learned to provide attack examples (from dataset)
- Learned severity classification (CRITICAL for exploitable)
- Learned to cite standards (90% of dataset cites OWASP)

---

## Optimization Metrics

### Performance Improvement

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Overall Accuracy</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">12.5%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">100%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+87.5%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Security Detection</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">33% (1/3)</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">100% (3/3)</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+67%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>RAG Relevance</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">25%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+70%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Tool Usage Accuracy</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">0%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">100%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+100%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Memory Relevance</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+60%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Response Actionability</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">20%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+75%</strong></td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>Token Efficiency</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">5,000 tokens</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">2,000 tokens</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">-60%</strong></td>
	</tr>
</table>

---

## The Compound Effect

### Single-Layer vs. Full-Stack

**Optimizing ONLY Prompts**:
```
Result: Better instructions, but...
- Still retrieves wrong knowledge docs
- Still doesn't use tools correctly
- Still includes irrelevant memories
- Still uses generic phrasing

Final Accuracy: ~45%
```

**Optimizing ALL Layers**:
```
Result: Better instructions AND
- Retrieves perfect security docs
- Uses tools strategically
- Recalls relevant past findings
- Uses expert-level phrasing from dataset

Final Accuracy: 100%
```

**Key Insight**: Each layer multiplies the effect of others. This is why full-stack optimization produces 2-3x better results than prompt-only optimization.

---

## Complete Workflow

### End-to-End Optimization Process

```bash
# Initialize project
super init code_review_project
cd code_review_project

# Create knowledge base
mkdir -p knowledge/security knowledge/performance knowledge/best_practices
# ... add your documentation files

# Prepare dataset (optional but recommended)
# Download or create real code review examples
cp your_real_reviews.csv data/code_reviews.csv

# Create agent playbook
cat > agents/code_reviewer/playbook.yaml << 'EOF'
spec:
  persona:
    role: Code Reviewer
    goal: Find issues in code
  
  rag:
    enabled: true
    knowledge_base: [./knowledge/**/*.md]
  
  tools:
    enabled: true
    specific_tools: [complexity_calculator, security_scanner]
  
  memory:
    enabled: true
    enable_context_optimization: true
  
  datasets:
    - source: ./data/code_reviews.csv
      limit: 100
  
  optimization:
    optimizer: {name: GEPA, params: {auto: medium}}
EOF

# Compile
super agent compile code_reviewer
# → Generates pipeline with all layers enabled

# Baseline evaluation
super agent evaluate code_reviewer
# → Shows baseline: 12.5% accuracy

# Optimize ALL layers
super agent optimize code_reviewer --auto medium --fresh
# → GEPA optimizes: prompts + RAG + tools + memory + dataset learning
# → Takes 10-15 minutes
# → Shows progress for each layer

# Re-evaluate
super agent evaluate code_reviewer  # automatically loads optimized weights
# → Shows improvement: 100% accuracy (+87.5%)

# Test on real code
super agent run code_reviewer --code "$(cat suspicious_code.py)"
# → Professional, comprehensive security audit

# Deploy
super agent run code_reviewer --interactive
# → Production-ready code review agent!
```

---

## What Makes This Production-Ready?

### Quality Indicators

**1. Comprehensive Coverage** - Detects all vulnerability types (SQL, XSS, secrets, etc.)
- Analyzes performance and code quality
- Handles edge cases and complex patterns

**2. Actionable Output** - Specific issue identification
- Executable code solutions
- Clear priority ordering
- Standards compliance

**3. Professional Quality** - Expert-level phrasing (learned from dataset)
- Proper citations (OWASP, CWE, Clean Code)
- Severity classification
- Risk assessment

**4. Efficient Operation** - Strategic knowledge retrieval (95% relevance)
- Correct tool usage (100% accuracy)
- Optimized memory selection (60% fewer tokens)
- Fast response time (<3 seconds)

**5. Robust Performance** - Handles unseen code variations (dataset generalization)
- References past findings (memory consistency)
- Graceful error handling (tool/protocol failures)

---

## Applying to Your Agents

### Step 1: Identify Your Layers

Which layers does your agent need?

```yaml
Customer Support:
  - Prompts: (response quality)
  - RAG: (product knowledge)
  - Tools: ⚠️ (maybe ticketing system)
  - Memory: (conversation history)
  - Protocols: (not needed)
  - Datasets: (real support tickets)

Research Agent:
  - Prompts: (research methodology)
  - RAG: (academic papers)
  - Tools: (search, citations)
  - Memory: ⚠️ (maybe past searches)
  - Protocols: (MCP for data sources)
  - Datasets: (research examples)

Code Generator:
  - Prompts: (coding standards)
  - RAG: (API docs, patterns)
  - Tools: (syntax validators)
  - Memory: ⚠️ (maybe past code)
  - Protocols: ⚠️ (maybe MCP filesystem)
  - Datasets: (code examples)
```

### Step 2: Enable Your Layers

```yaml
spec:
  # Enable only what you need
  rag:
    enabled: true  # If you have knowledge base
  
  tools:
    enabled: true  # If you need tools
  
  memory:
    enabled: true  # If you need context
    enable_context_optimization: true
  
  datasets:
    - source: your_data.csv  # If you have examples
```

### Step 3: Optimize

```bash
super agent optimize your_agent --auto medium
```

GEPA automatically optimizes all enabled layers!

---

## Key Takeaways

### What You Learned

1. **Full-Stack > Prompts Only**: All 6 layers working together produces 2-3x better results
2. **Each Layer Compounds**: RAG finds better docs, tools provide better metrics, memory recalls better context
3. **GEPA Learns Strategies**: Not just what to do, but WHEN, WHICH, and HOW
4. **Datasets Amplify**: Real examples teach real-world patterns and expert-level quality
5. **Production-Ready**: 12% → 100% accuracy demonstrates deployment readiness

### The Full-Stack Advantage

| Optimization Approach | Accuracy | Quality | Production-Ready |
|----------------------|----------|---------|------------------|
| **Prompts Only** | 45% | Basic | No |
| **Prompts + RAG** | 65% | Better | ⚠️ Maybe |
| **Prompts + RAG + Tools** | 75% | Good | ⚠️ Close |
| **Full-Stack (All 6 Layers)** | 100% | Expert | Yes |

---

## Next Steps

### Explore Individual Layers

Deep-dive into specific layers:
- [💬 Prompt Optimization](prompts.md)
- [🔍 RAG Optimization](rag.md)
- [🛠️ Tool Optimization](tools.md)
- [🧠 Memory Optimization](memory.md)
- [🔌 Protocol Optimization](protocols.md)
- [📊 Dataset Optimization](datasets.md)

### Try the Workflow

```bash
# Create an agent with multiple layers
# Optimize with GEPA
# See the compound effect!
```

### Learn GEPA Internals

- [GEPA Optimizer Guide](../gepa-optimization.md)
- [GEPA + --fresh Flag](../gepa-optimization.md#using-the-fresh-flag)

### Scale with Datasets

- [Dataset Import Guide](../dataset-import.md)
- Browse HuggingFace: https://huggingface.co/datasets

---

**Related Guides:**

- [Agent Optimization Overview](overview.md)
- [GEPA Optimization](../gepa-optimization.md)
- [Memory Optimization](../memory-optimization.md)
- [Dataset Import](../dataset-import.md)
- [Tool Development](../tool-development.md)
- [RAG Configuration](../rag.md)
- [MCP Protocol](../protocol-first-agents.md)

