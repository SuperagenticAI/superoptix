# Dataset-Driven Optimization

## What is Dataset-Driven Optimization?

Dataset-driven optimization is the process of training agents on **large-scale, real-world examples** (100s to 1000s) instead of just a handful of manual RSpec-style BDD scenarios. GEPA learns patterns, edge cases, and domain-specific knowledge from actual data.

**Key Insight**: While RSpec-style BDD scenarios define expected behavior, large datasets teach the agent **how real-world problems actually look** and **how experts actually solve them**.

---

## The Dataset Optimization Problem

### Without Datasets (Manual Scenarios Only)

**Scenario**: Training code review agent

```
Training Data: 5-10 manual RSpec-style BDD scenarios
Coverage: Limited patterns, idealized examples
Result: Agent works on test cases but fails on real code
```

**Problems**:
- Limited pattern exposure
- Idealized examples don't match real-world complexity
- Edge cases not covered
- Manual scenario creation is time-consuming

### With Dataset-Driven Optimization

**Scenario**: Same code review agent

```
Training Data: 
- 10 RSpec-style BDD scenarios (expected behavior)
- 100 real GitHub code reviews (real-world examples)

Coverage: Diverse patterns, real complexity, edge cases
Result: Agent handles real-world code variations
```

**Solution**: Broader pattern recognition, robust to edge cases, production-ready

---

## What GEPA Learns from Datasets

### 1. Real-World Patterns

**What It Is**: Learning how real issues actually manifest in code

**What GEPA Learns**:
- Common vulnerability patterns
- Typical code smell variations
- Industry-specific conventions
- Edge case handling

**Example**: SQL Injection Patterns

**Manual RSpec-Style BDD Scenario** (Idealized):
```yaml
scenarios:
  - name: sql_injection
    input:
      code: 'query = "SELECT * FROM users WHERE id = " + user_id'
    expected_output:
      review: "SQL injection detected"
```

**Dataset Examples** (Real-World):
```csv
code,review
"query = f'SELECT * FROM t WHERE x = {val}'","SQL injection via f-string"
"sql = 'DELETE FROM items WHERE ' + condition","SQL injection in DELETE"
"db.execute('UPDATE users SET name = ' + name)","SQL injection in UPDATE"
"cursor.execute(query % (user_input,))","SQL injection via % formatting"
```

**What GEPA Learns**:
- SQL injection appears in SELECT, DELETE, UPDATE, INSERT
- Multiple string formatting methods (concat, f-string, % formatting)
- Variables named differently (query, sql, cmd)
- Real code uses diverse patterns

**Impact**: Recognizes SQL injection in ANY form, not just idealized examples

---

### 2. Expert Solution Phrasing

**What It Is**: Learning how domain experts actually write recommendations

**What GEPA Learns from Real Reviews**:
- Professional terminology
- Actionable solution format
- Appropriate severity levels
- Citation styles

**Example**: Learning from Real GitHub Code Reviews

**Dataset Examples**:
```csv
code,review
"[complexity 8]","Cyclomatic complexity (8) exceeds maintainability threshold (4). Recommend refactoring with early returns pattern. See: Clean Code, Chapter 3."
"[hardcoded key]","CRITICAL: Hardcoded API key detected (line 23). Never commit secrets. Use environment variables: os.environ.get('API_KEY'). Reference: OWASP ASVS 2.7.1"
"[O(n²) loop]","Performance: Nested loops create O(n²) complexity. For 10k items, that's 100M iterations. Optimize to O(n) using set lookup. Benchmark: 1000x faster."
```

**What GEPA Learns**:
- Quantify impact: "8 exceeds 4", "100M iterations", "1000x faster"
- Provide specific solutions: "Use environment variables", "set lookup"
- Cite standards: "Clean Code Chapter 3", "OWASP ASVS 2.7.1"
- Use severity markers: "CRITICAL:", "Performance:", "Maintainability:"

**Impact**: Professional, detailed reviews vs. generic "this is bad" responses

---

### 3. Edge Case Handling

**What It Is**: Learning to handle unusual or complex scenarios

**What GEPA Learns from Dataset**:
- Rare vulnerability patterns
- Complex code structures
- Multiple simultaneous issues
- Language-specific idioms

**Example**: Complex Security Patterns

**Dataset Includes**:
```python
# Edge Case 1: SQL injection in WHERE clause builder
def build_query(filters):
    where = " AND ".join([f"{k} = '{v}'" for k, v in filters.items()])
    return f"SELECT * FROM table WHERE {where}"

# Edge Case 2: Second-order SQL injection
def log_query(query):
    log = f"INSERT INTO logs VALUES ('{query}')"  # Injection here!
    db.execute(log)

# Edge Case 3: Blind SQL injection via time delay
def check_user(username):
    query = f"SELECT IF(username='{username}', SLEEP(5), 0)"
```

**What GEPA Learns**:
- SQL injection isn't just in obvious SELECT statements
- Can occur in logging, error handling, query builders
- Can be second-order (stored then executed)
- Various attack vectors (WHERE, INSERT, time-based)

**Impact**: Detects vulnerabilities in unusual contexts

---

### 4. Domain-Specific Knowledge

**What It Is**: Learning industry standards, best practices, conventions

**What GEPA Learns from Dataset**:
- Industry terminology
- Standard references (OWASP, CWE, PEP)
- Severity classification
- Remediation priorities

**Example**: Security Domain Dataset

```csv
vulnerability,severity,standard_reference
"SQL Injection",CRITICAL,"OWASP Top 10 #1, CWE-89"
"XSS",CRITICAL,"OWASP Top 10 #3, CWE-79"
"Hardcoded Secrets",CRITICAL,"OWASP ASVS 2.7.1, CWE-798"
"High Complexity",MEDIUM,"Clean Code, Cyclomatic Complexity"
"Missing Error Handling",MEDIUM,"PEP 8, Exception Handling"
```

**What GEPA Learns**:
- Map each issue to severity level
- Cite appropriate standards
- Use industry-standard terminology

**Impact**: Professional, standards-compliant reviews

---

## Before/After Comparison

### Scenario: Training on Real GitHub Code Reviews

**Training Data**:
- **Without Dataset**: 5 manual RSpec-style BDD scenarios
- **With Dataset**: 5 RSpec-style BDD scenarios + 100 real GitHub reviews

**Input Code**:
```python
# Complex real-world code
class UserManager:
    def __init__(self):
        self.db_password = "admin123"  # Issue 1: Hardcoded
    
    def get_user(self, user_id):
        # Issue 2: SQL injection via f-string
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.execute(query)
    
    def verify_login(self, username, password):
        # Issue 3: Timing attack vulnerability
        user = self.get_user(username)
        if user and user.password == password:  # Issue 4: Plaintext comparison
            return True
        return False
```

**Before Dataset Optimization** (5 scenarios only):
```
Agent Review:
"Security issues detected:
- Line 6: SQL injection
- Line 12: Password issue

Please fix these problems."
```
- Vague
- Missed 2 issues (hardcoded secret, timing attack)
- No specific solutions
- No severity classification
- No standards cited

**After Dataset Optimization** (5 scenarios + 100 real reviews):
```
Agent Review:
"Security Audit Results

CRITICAL Issues (Fix Immediately):

1. Hardcoded Database Credential (Line 4)
   Code: self.db_password = "admin123"
   Risk: Database compromise if code exposed
   Solution:
   ```python
   self.db_password = os.environ.get('DB_PASSWORD')
   ```
   Reference: OWASP ASVS 2.7.1, CWE-798

2. SQL Injection via F-String (Line 8)
   Code: f'SELECT * FROM users WHERE id = {user_id}'
   Risk: Database takeover possible
   Attack: user_id = '1 OR 1=1'
   Solution:
   ```python
   query = 'SELECT * FROM users WHERE id = ?'
   self.db.execute(query, (user_id,))
   ```
   Reference: OWASP Top 10 #1, CWE-89

3. Timing Attack Vulnerability (Line 13)
   Code: if user and user.password == password
   Risk: Password length leakage via timing
   Solution: Use constant-time comparison
   Reference: CWE-208

4. Plaintext Password Storage (Line 13)
   Code: Direct password comparison
   Risk: Passwords must be hashed
   Solution:
   ```python
   import bcrypt
   if bcrypt.checkpw(password.encode(), user.password_hash):
   ```
   Reference: OWASP ASVS 2.4.1

Severity Distribution:
- CRITICAL: 4 issues
- HIGH: 0
- MEDIUM: 0

Priority: Address all CRITICAL issues before deployment

Standards Compliance:
- OWASP Top 10: 2 violations
- OWASP ASVS: 2 violations
- CWE: 4 weaknesses

Recommended Next Steps:
1. Immediate: Fix SQL injection + hardcoded password
2. Before deployment: Add password hashing + timing-safe comparison
3. Security audit: Review all authentication code"
```

**Learned from 100 Real Reviews**:
- Caught all 4 issues (100% vs. 50%)
- Specific attack examples
- Executable solutions
- Severity classification
- Standards compliance check
- Actionable priority order

**Improvement**: From incomplete → Comprehensive professional audit

---

## How GEPA Learns from Datasets

### The Optimization Process

1. **Dataset Loading**
   ```
   Loading: 100 GitHub code reviews
   Format: CSV with (code, review, severity, tags)
   ```

2. **Pattern Extraction**
   ```
   GEPA Analyzes Dataset:
   - 30% of reviews mention "SQL injection" with "parameterized" solution
   - 25% mention "hardcoded" with "environment variables" solution
   - 40% cite "OWASP" standards
   - 80% provide code examples in solutions
   - Reviews average 200 words with structured format
   ```

3. **Reflection Phase**
   ```
   GEPA Reflection:
   "Real expert reviews always:
    1. Identify specific vulnerability type (not generic 'security issue')
    2. Provide executable code solution (not just 'fix it')
    3. Cite standards (OWASP, CWE)
    4. Classify severity (CRITICAL, HIGH, MEDIUM)
    
    Agent should learn these patterns."
   ```

4. **Strategy Generation**
   ```
   GEPA Creates Instructions:
   "For security issues:
    - Specify exact vulnerability (SQL injection, XSS, etc.)
    - Provide code solution with imports and context
    - Cite relevant OWASP/CWE reference
    - Classify severity based on exploitability
    - Structure: Issue → Risk → Solution → Reference"
   ```

5. **Validation**
   ```
   Test on held-out dataset:
   - Agent now matches expert review format
   - 90% of responses include code solutions
   - 85% cite appropriate standards
   - Severity classification 95% accurate
   ```

**Result**: Agent learns professional review style from real experts

---

## Best Practices

### 1. Combine RSpec-Style BDD Scenarios + Datasets

```yaml
spec:
  # RSpec-style BDD for expected behavior (10 scenarios)
  feature_specifications:
    scenarios:
      - name: sql_injection_detection
        input: {code: "[SQL injection]"}
        expected_output: {review: "SQL injection detected"}
  
  # Dataset for real-world patterns (100+ examples)
  datasets:
    - name: github_reviews
      source: ./data/real_reviews.csv
      limit: 100
```

**Why**: RSpec-style BDD defines expectations, datasets teach real-world execution

### 2. Use Diverse, High-Quality Datasets

```yaml
datasets:
  # Real code reviews from GitHub
  - name: github_reviews
    source: ./data/github_code_reviews.csv
    limit: 100
  
  # Security-specific examples
  - name: security_dataset
    source: huggingface:code_security_vulnerabilities
    format: huggingface
    limit: 500
  
  # Performance optimization examples
  - name: performance_dataset
    source: ./data/performance_reviews.csv
    limit: 50
```

### 3. Balance Dataset Size

```yaml
# Development (fast iteration)
datasets:
  - limit: 20  # Small for quick optimization

# Production (best quality)
datasets:
  - limit: 500  # Large for comprehensive learning
```

### 4. Ensure Dataset Quality

**Good Dataset**:
- Diverse examples
- Expert-quality annotations
- Consistent format
- Real-world complexity

**Bad Dataset**:
- Repetitive examples
- Low-quality annotations
- Inconsistent format
- Artificial simplicity

---

## Dataset Formats Supported

### CSV (Most Common)

```yaml
datasets:
  - name: code_reviews
    source: ./data/reviews.csv
    format: csv
    mapping:
      input: code
      output: review
```

### HuggingFace (100,000+ Datasets)

```yaml
datasets:
  - name: security_dataset
    source: huggingface:code_security
    format: huggingface
    mapping:
      input: code_snippet
      output: vulnerability_report
    limit: 1000
```

### JSON/JSONL

```yaml
datasets:
  - name: reviews
    source: ./data/reviews.jsonl
    format: jsonl
    mapping:
      input: code
      output: expert_review
```

See [Dataset Import Guide](../dataset-import.md) for complete details.

---

## Scaling Benefits

### Small Dataset (10 examples)

**Training Time**: 2-3 minutes  
**Pattern Coverage**: 30%  
**Accuracy**: 60%  
**Best For**: Quick prototypes

### Medium Dataset (100 examples)

**Training Time**: 10-15 minutes  
**Pattern Coverage**: 80%  
**Accuracy**: 85%  
**Best For**: Production agents

### Large Dataset (1000+ examples)

**Training Time**: 60-90 minutes  
**Pattern Coverage**: 95%  
**Accuracy**: 92%  
**Best For**: Mission-critical agents

**Recommendation**: Start with 100 examples for best balance.

---

## Before/After Comparison

### Scenario: Security Code Review Training

**Agent Task**: Detect security vulnerabilities in code

**Training Approach 1: Manual RSpec-Style BDD Only**

```yaml
feature_specifications:
  scenarios:
    - name: sql_injection
      input: {code: 'query = "SELECT * WHERE id = " + user_id'}
      expected_output: {finding: "SQL injection"}
    
    - name: xss_vulnerability
      input: {code: 'html = "<div>" + user_input + "</div>"'}
      expected_output: {finding: "XSS vulnerability"}
    
    # ... 8 more idealized scenarios
```

**Coverage**: 10 patterns (idealized)

**Test on Real Code**:
```python
# Real-world complex code
async def search_products(filters: dict):
    where_clauses = []
    for field, value in filters.items():
        where_clauses.append(f"{field} = '{value}'")  # SQL injection!
    query = "SELECT * FROM products WHERE " + " AND ".join(where_clauses)
    return await db.fetch(query)
```

**Agent Result (RSpec-Style BDD Only)**:
```
"Potential SQL issue detected."
```
- Vague
- Didn't recognize f-string SQL injection in loop
- No specific solution
- Pass Rate: 40%

---

**Training Approach 2: RSpec-Style BDD + Dataset**

```yaml
feature_specifications:
  scenarios: [Same 10 scenarios as above]

datasets:
  - name: github_security_reviews
    source: ./data/real_security_reviews.csv
    limit: 100
```

**Dataset Examples Include**:
```csv
code,review,severity
"f'{col} = {val}'","SQL injection via f-string formatting",CRITICAL
"' AND '.join(clauses)","SQL injection in dynamic WHERE builder",CRITICAL
"async def query(sql)","Async SQL execution requires parameterization",HIGH
```

**Coverage**: 10 RSpec-style BDD patterns + 100 real-world variations

**Test on Same Real Code**:

**Agent Result (RSpec-Style BDD + Dataset)**:
```
"CRITICAL: SQL Injection in Dynamic Query Builder

Issue: F-string formatting in WHERE clause construction (Line 4)
Code: where_clauses.append(f"{field} = '{value}'")

Attack Vector:
  filters = {'id': "1' OR '1'='1"}
  → Query: SELECT * FROM products WHERE id = '1' OR '1'='1'
  → Returns ALL products (authentication bypass)

Root Cause: User-controlled 'filters' dict values inserted into SQL without sanitization

Solution (Parameterized Queries):
```python
async def search_products(filters: dict):
    placeholders = []
    values = []
    for field, value in filters.items():
        placeholders.append(f"{field} = ?")
        values.append(value)
    query = "SELECT * FROM products WHERE " + " AND ".join(placeholders)
    return await db.fetch(query, *values)
```

Why This Works:
- Parameterized queries separate SQL logic from data
- Database driver handles escaping automatically
- Prevents all SQL injection attacks

Additional Recommendation:
- Validate field names against whitelist (prevent column injection)
- Add input sanitization for defense-in-depth

Reference: OWASP Top 10 #1 (2024), CWE-89
Severity: CRITICAL (exploitable remote code execution)"
```

**Learned from Dataset**:
- Recognized f-string SQL injection in loop context
- Identified attack vector with example
- Provided async-compatible solution
- Added field validation recommendation
- Cited multiple standards

**Improvement**: 40% → 95% pass rate, professional-quality reviews

---

## How GEPA Learns from Datasets

### The Dataset Optimization Process

1. **Dataset Analysis**
   ```
   GEPA Analyzes 100 Real Reviews:
   
   Patterns Discovered:
   - 85% of security reviews cite OWASP or CWE
   - 90% provide executable code solutions
   - 75% include attack examples
   - 95% classify severity
   - 80% mention multiple related issues
   ```

2. **Reflection on Gaps**
   ```
   GEPA Reflection:
   "Current agent (trained on 10 RSpec-style BDD only):
    - Cites standards: 20% (vs. 85% in real reviews)
    - Provides code: 40% (vs. 90% in real reviews)
    - Shows attacks: 10% (vs. 75% in real reviews)
    
    Need to learn from real expert patterns."
   ```

3. **Strategy Learning**
   ```
   GEPA Extracts Strategies:
   - "Always cite OWASP for web security issues"
   - "Provide executable solution with imports"
   - "Show attack example for critical vulnerabilities"
   - "Classify severity based on exploitability"
   - "Mention related issues (defense-in-depth)"
   ```

4. **Validation on Test Set**
   ```
   Hold out 20 reviews for testing:
   
   Agent trained on dataset:
   - Cites standards: 80% ← Learned!
   - Provides code: 85% ← Learned!
   - Shows attacks: 70% ← Learned!
   - Severity correct: 90% ← Learned!
   ```

**Result**: Agent learned professional review style from real experts

---

## Combining Datasets with Other Layers

### Dataset + Prompts

```
Dataset teaches: How experts phrase recommendations
Prompts optimize: How to structure responses
Combined: Professional, well-structured reviews
```

### Dataset + RAG

```
Dataset teaches: Which knowledge to cite
RAG optimizes: When to retrieve which docs
Combined: Accurate citations of relevant standards
```

### Dataset + Tools

```
Dataset teaches: When experts use metrics (complexity, performance)
Tools optimize: Which tool for which metric
Combined: Metric-driven, quantified recommendations
```

### Dataset + Memory

```
Dataset teaches: How to reference similar past issues
Memory optimizes: Which past issues to recall
Combined: "Similar to issue #47" with consistent handling
```

---

## Metrics and Results

### What Gets Measured

- **Pattern Coverage**: % of real-world patterns recognized
- **Expert Alignment**: Similarity to expert reviews (style, content, format)
- **Edge Case Handling**: % of unusual scenarios handled correctly
- **Generalization**: Performance on unseen examples

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">RSpec-Style BDD Only (10)</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">RSpec-Style BDD + Dataset (100)</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Pattern Coverage</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Expert Alignment</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">40%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+50%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Edge Case Handling</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">25%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>80%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Generalization</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">50%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>88%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+38%</td>
	</tr>
</table>

---

## Quick Start

### Enable Dataset-Driven Optimization

```yaml
spec:
  # RSpec-style BDD scenarios (define expected behavior)
  feature_specifications:
    scenarios:
      - name: security_detection
        input: {code: "[vulnerable code]"}
        expected_output: {finding: "vulnerability type"}
  
  # Dataset (teach real-world patterns)
  datasets:
    - name: real_reviews
      source: ./data/expert_reviews.csv
      format: csv
      mapping:
        input: code
        output: review
      limit: 100
  
  # GEPA learns from both!
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

GEPA trains on both RSpec-style BDD and dataset examples!

---

## Troubleshooting

### Issue: Dataset Not Loading

**Symptoms**: "No dataset found" error

**Solutions**:
1. Check file path is correct
2. Verify format matches (csv, json, jsonl, parquet)
3. Check column mapping matches actual columns
4. See [Dataset Import Guide](../dataset-import.md)

### Issue: Low Quality After Dataset Training

**Symptoms**: No improvement despite large dataset

**Solutions**:
1. Validate dataset quality (are examples expert-level?)
2. Check mapping is correct (input/output fields match)
3. Ensure dataset diversity (not all same pattern)
4. Increase optimization iterations (`--auto intensive`)

### Issue: Agent Overfits to Dataset

**Symptoms**: Perfect on training data, poor on new examples

**Solutions**:
1. Add more diverse RSpec-style BDD scenarios
2. Use dataset shuffling (`shuffle: true`)
3. Split dataset (train/test)
4. Reduce dataset size if too repetitive

---

## Related Guides

- [💬 Prompt Optimization](prompts.md) - Optimize instructions
- [🔍 RAG Optimization](rag.md) - Optimize retrieval
- [🛠️ Tool Optimization](tools.md) - Optimize tools
- [🧠 Memory Optimization](memory.md) - Optimize context
- [🔌 Protocol Optimization](protocols.md) - Optimize protocols
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers
- [Dataset Import Guide](../dataset-import.md) - How to import datasets
- [RSpec-Style BDD Testing](../bdd.md) - BDD methodology

---

**Next**: See how all layers work together in the [Full-Stack Example →](full-stack-example.md)

