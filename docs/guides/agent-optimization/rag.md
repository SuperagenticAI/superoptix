# RAG Optimization

## What is RAG Optimization?

RAG (Retrieval-Augmented Generation) optimization is the process of improving **when**, **which**, and **how** an agent retrieves knowledge from its knowledge base. While traditional RAG uses fixed retrieval strategies, GEPA learns dynamic, context-aware retrieval patterns.

**Key Insight**: It's not enough to have a knowledge base. The agent must learn WHEN to search it, WHICH documents to retrieve, and HOW to integrate that knowledge into its response.

---

## The RAG Optimization Problem

### Without Optimization

**Scenario**: Agent reviewing code for SQL injection

```
1. Agent receives code with SQL injection
2. Agent retrieves random documents from knowledge base
3. Agent might get: "Python naming conventions.md" (irrelevant)
4. Agent gives vague response: "Check your code"
```

**Problem**: Wrong documents retrieved, no actionable solution

### With GEPA Optimization

**Scenario**: Same code review

```
1. Agent receives code with SQL injection
2. GEPA-learned strategy: "Search security docs for SQL patterns"
3. Agent retrieves: "sql_injection.md" (highly relevant)
4. Agent gives specific response: "SQL injection detected. Use parameterized queries: query = 'SELECT * WHERE id = ?'"
```

**Solution**: Right documents at right time, actionable solution

---

## What GEPA Optimizes in RAG

### 1. Retrieval Strategy (When to Search)

**What It Is**: Learning when to query the knowledge base

**What GEPA Learns**:
- Which scenarios require knowledge retrieval
- When to search before analysis vs. after
- When to skip retrieval (already have knowledge)

**Example Configuration**:

```yaml
spec:
  rag:
    enabled: true
    vector_database: chromadb
    collection: code_review_knowledge
    knowledge_base:
      - ./knowledge/security/*.md
      - ./knowledge/python/*.md
      - ./knowledge/performance/*.md
```

**Before Optimization**:
```
Strategy: Always search all knowledge sources for every query
Result: Slow, often irrelevant docs retrieved
```

**After GEPA Optimization**:
```
Learned Strategies:
- "Search security/*.md when code contains string concatenation in SQL"
- "Search performance/*.md when detecting loops or recursion"
- "Search python/*.md for naming and style issues"
- "Skip search for simple syntax errors"
```

**Impact**: 3x faster, 85% relevance vs. 30% relevance

---

### 2. Document Selection (Which to Retrieve)

**What It Is**: Choosing the most relevant documents from the knowledge base

**What GEPA Learns**:
- Query formulation for semantic search
- Relevance threshold tuning
- Number of documents to retrieve (top_k)

**Configuration**:

```yaml
rag:
  top_k: 5
  similarity_threshold: 0.7
```

**Before Optimization**:
```
Query: Generic "code review"
Retrieved: Random 5 docs, low relevance
```

**After GEPA Optimization**:
```
Learned Query Strategies:
- For SQL code: "SQL injection prevention parameterized queries OWASP"
- For loops: "performance optimization time complexity O(n)"
- For naming: "Python naming conventions PEP 8"

Retrieved: Top 5 highly relevant docs (>0.85 similarity)
```

**Impact**: Precision increased from 40% → 90%

---

### 3. Context Integration (How to Use)

**What It Is**: Incorporating retrieved knowledge into agent responses

**What GEPA Learns**:
- How to cite retrieved documents
- How to combine multiple sources
- When to quote vs. paraphrase
- How to attribute knowledge

**Before Optimization**:
```
Response: "This is a security issue."
[Retrieved doc not cited or used effectively]
```

**After GEPA Optimization**:
```
Response: "SQL Injection Vulnerability (CRITICAL)

According to OWASP Top 10 2024 [Retrieved from: security/sql_injection.md]:
'Injection attacks occur when untrusted data is sent to an interpreter as 
part of a command or query.'

Solution (from best practices):
```python
query = "SELECT * FROM users WHERE name = ?"
db.execute(query, (username,))
```

Reference: OWASP Top 10 #1, CWE-89"
```

**Impact**: Clear attribution, professional citations, actionable solutions

---

### 4. Relevance Scoring

**What It Is**: Filtering and ranking retrieved documents

**What GEPA Learns**:
- Optimal similarity thresholds
- Re-ranking strategies
- Filtering irrelevant results

**Configuration**:

```yaml
rag:
  similarity_threshold: 0.7
  rerank: true
```

**Before Optimization**:
```
Retrieved 5 docs with similarities: [0.71, 0.68, 0.65, 0.64, 0.62]
Used all 5 (including low-relevance ones)
```

**After GEPA Optimization**:
```
Learned Threshold: 0.75 for security queries, 0.65 for general
Retrieved 5 docs, filtered to top 2 with >0.85 similarity
Re-ranked by: recency + domain match + keyword overlap
```

**Impact**: Higher quality context, less noise

---

## Before/After Comparison

### Scenario: Security Code Review

**Input Code**:
```python
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
```

**Before RAG Optimization**:
```
RAG Behavior:
- Query: "code review"
- Retrieved: naming_conventions.md, file_organization.md, testing.md
- Relevance: Low (wrong topic)

Agent Response:
"This code could be improved. Consider better practices."
```

**After GEPA RAG Optimization**:
```
RAG Behavior:
- Learned Strategy: "Detect SQL pattern → Search security docs"
- Query: "SQL injection prevention parameterized queries"
- Retrieved: sql_injection.md, database_security.md
- Relevance: High (>0.90 similarity)

Agent Response:
"SQL Injection Vulnerability (CRITICAL)

Issue: String concatenation in SQL query allows injection attacks.

According to OWASP Top 10 [Retrieved from: sql_injection.md]:
This is the #1 web security risk in 2024.

Solution:
```python
def get_user(username):
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (username,))
```

Why: Parameterized queries prevent injection by treating user input as data, not code.

Reference: OWASP A03:2021 - Injection"
```

**Improvement**: From irrelevant docs → Precise security knowledge

---

## How GEPA Learns RAG Strategies

### The Optimization Process

1. **Analysis Phase**
   ```
   GEPA Observes:
   - Agent retrieved "naming_conventions.md" for SQL injection code
   - Document wasn't relevant to security issue
   - Agent gave vague response without specific solution
   ```

2. **Reflection Phase**
   ```
   GEPA Reflection:
   "The agent should search security documentation BEFORE analyzing 
    SQL queries. String concatenation in SQL context is a security 
    pattern that requires security knowledge retrieval."
   ```

3. **Mutation Phase**
   ```
   GEPA Tests:
   - Strategy 1: "Always search security docs for any SQL code"
   - Strategy 2: "Search security docs when detecting string concatenation in SQL"
   - Strategy 3: "Search security docs after finding potential injection"
   ```

4. **Evaluation Phase**
   ```
   Results:
   - Strategy 1: 70% (too broad, slow)
   - Strategy 2: 95% (precise, fast) ← Winner!
   - Strategy 3: 60% (too late, misses context)
   ```

5. **Selection Phase**
   ```
   GEPA Keeps: Strategy 2
   Next Iteration: Build on this strategy for other patterns
   ```

**Result**: Learned when and what to retrieve for maximum relevance

---

## Best Practices

### 1. Organize Knowledge Base by Topic

```yaml
rag:
  knowledge_base:
    - ./knowledge/security/*.md      # Security topics
    - ./knowledge/performance/*.md   # Performance topics
    - ./knowledge/best_practices/*.md # General practices
```

GEPA learns which directory to search for which scenario.

### 2. Use Descriptive Document Names

```
✅ Good:
- sql_injection_prevention.md
- xss_mitigation.md
- password_hashing_best_practices.md

❌ Bad:
- doc1.md
- security.md
- notes.md
```

### 3. Structure Documents Consistently

```markdown
# SQL Injection Prevention

## What is SQL Injection?
[Clear explanation]

## How to Prevent
[Specific solutions with code]

## References
[OWASP, CWE links]
```

Consistent structure helps GEPA learn effective retrieval patterns.

### 4. Combine with RSpec-Style BDD Scenarios

```yaml
feature_specifications:
  scenarios:
    - name: sql_injection_detection
      description: Agent should use security docs for SQL analysis
      input:
        code: [SQL injection code]
      expected_output:
        review: Must mention "SQL injection" and cite "OWASP"
```

GEPA optimizes RAG to pass these scenarios.

---

## Metrics and Results

### What Gets Measured

- **Retrieval Precision**: % of retrieved docs that are relevant
- **Retrieval Recall**: % of relevant docs that are retrieved
- **Response Relevance**: % of responses using retrieved knowledge
- **Citation Accuracy**: % of citations that are correct

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Retrieval Precision</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Response Relevance</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">40%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+50%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Citation Accuracy</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">25%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>95%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+70%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Retrieval Speed</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">2.5s</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>0.8s</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">3x faster</td>
	</tr>
</table>

---

## Quick Start

### Enable RAG Optimization

```yaml
spec:
  # RAG configuration
  rag:
    enabled: true
    vector_database: chromadb
    knowledge_base:
      - ./knowledge/**/*.md
    top_k: 5
  
  # GEPA automatically optimizes RAG strategies
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

GEPA will learn optimal retrieval strategies!

---

## Advanced: RAG-Specific Configuration

### Fine-Tune Retrieval Parameters

```yaml
rag:
  # Semantic search config
  top_k: 5                    # Number of docs to retrieve
  similarity_threshold: 0.7   # Minimum similarity score
  rerank: true                # Re-rank results
  
  # Document processing
  chunk_size: 512             # Tokens per chunk
  chunk_overlap: 50           # Overlap between chunks
  
  # Embedding model
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
```

GEPA learns optimal values for these parameters through optimization.

---

## Common RAG Strategies GEPA Learns

### Strategy 1: Topic-Aware Retrieval

**Before**: Search all knowledge indiscriminately  
**After**: "Search security/*.md for SQL/XSS patterns, performance/*.md for loops/recursion"

### Strategy 2: Pre-emptive Retrieval

**Before**: Retrieve after analysis (too late)  
**After**: "Search BEFORE analyzing SQL queries to have security context"

### Strategy 3: Contextual Queries

**Before**: Generic query "code review"  
**After**: Specific query "SQL injection prevention parameterized queries OWASP"

### Strategy 4: Multi-Source Combination

**Before**: Use only top result  
**After**: "Combine security doc + code example doc + OWASP reference for comprehensive answer"

---

## Integration with Other Layers

RAG optimization amplifies other layer optimizations:

**RAG + Prompts**:
```
Optimized Prompt: "Search security docs for SQL patterns"
Optimized RAG: Retrieves sql_injection.md with 0.95 similarity
→ Agent has perfect context for security analysis
```

**RAG + Tools**:
```
Optimized RAG: Retrieves complexity best practices
Optimized Tools: Uses complexity_calculator
→ Agent cites doc: "Per Clean Code guidelines, complexity should be <4"
→ Then shows: "Your code: 8 (calculated)"
```

**RAG + Memory**:
```
Optimized Memory: "Similar SQL injection found in previous review"
Optimized RAG: Retrieves same security doc used before
→ Consistent, high-quality security recommendations
```

---

## Real-World Example

### Use Case: Security Code Review

**Knowledge Base Structure**:
```
knowledge/
├── security/
│   ├── sql_injection.md          (OWASP Top 10 #1)
│   ├── xss_prevention.md          (OWASP Top 10 #3)
│   ├── hardcoded_secrets.md       (Security best practice)
│   └── password_hashing.md        (Cryptography)
├── performance/
│   ├── time_complexity.md         (Big O notation)
│   └── optimization_patterns.md   (Performance tips)
└── best_practices/
    └── solid_principles.md        (Clean code)
```

**Input**: Code with SQL injection

**Before RAG Optimization**:
```
Retrieved:
1. solid_principles.md (similarity: 0.68) - Wrong topic
2. optimization_patterns.md (similarity: 0.65) - Wrong topic
3. time_complexity.md (similarity: 0.63) - Wrong topic

Response: "Your code needs improvement."
```

**After GEPA RAG Optimization**:
```
Learned Strategy: "SQL string concatenation → security domain"

Retrieved:
1. sql_injection.md (similarity: 0.94) - Perfect!
2. hardcoded_secrets.md (similarity: 0.87) - Relevant!
3. password_hashing.md (similarity: 0.82) - Related!

Response: "SQL Injection Vulnerability (CRITICAL)

Issue: User input concatenated into SQL query (OWASP Top 10 #1)
[Retrieved from: security/sql_injection.md]

Attack Example: username = \"admin' OR '1'='1\"
→ Returns all users, bypasses authentication

Solution (from OWASP guidelines):
```python
query = "SELECT * FROM users WHERE name = ?"
result = db.execute(query, (username,))
```

Reference: OWASP A03:2021 - Injection, CWE-89"
```

**Impact**: 0% helpful → 100% actionable with professional citations

---

## Troubleshooting

### Issue: Low Retrieval Relevance

**Symptoms**: Agent retrieves wrong documents

**Solutions**:
1. Add more RSpec-style BDD scenarios showing expected retrieval
2. Increase `top_k` to give GEPA more options
3. Improve document organization by topic
4. Use more specific document titles

### Issue: Slow Retrieval

**Symptoms**: RAG queries take too long

**Solutions**:
1. GEPA learns to skip retrieval when not needed
2. Reduce `top_k` (GEPA finds optimal value)
3. Use smaller embedding model
4. Enable caching for repeated queries

### Issue: Documents Not Used in Response

**Symptoms**: Docs retrieved but not cited

**Solutions**:
1. Add citation requirements to RSpec-style BDD scenarios
2. Optimize prompts to include "cite sources"
3. Add examples showing proper citation format

---

## Related Guides

- [💬 Prompt Optimization](prompts.md) - Optimize instructions
- [🛠️ Tool Optimization](tools.md) - Optimize tool usage
- [🧠 Memory Optimization](memory.md) - Optimize context
- [📊 Dataset-Driven Optimization](datasets.md) - Train on data
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers
- [RAG Configuration Guide](../rag.md) - RAG setup details
- [MCP + RAG Complete Guide](../mcp-rag-complete-guide.md) - Advanced RAG

---

**Next**: Learn how GEPA optimizes [tool selection and usage →](tools.md)

