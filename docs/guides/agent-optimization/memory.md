# Memory Optimization

## What is Memory Optimization?

Memory optimization is the process of improving **which memories** an agent includes in its context, **how it scores relevance**, and **how it manages token budgets**. While traditional approaches include all memories (leading to context overflow), GEPA learns intelligent, context-aware memory selection.

**Key Insight**: After 20+ interactions, an agent can't include all memories. GEPA learns which memories matter most for each query, balancing relevance, importance, and recency within token constraints.

---

## The Memory Optimization Problem

### Without Optimization

**Scenario**: Customer support agent after 30 interactions

```
1. Agent has 30 memories (15,000 tokens total)
2. Context limit: 2,000 tokens
3. Traditional approach: Include all → Context overflow
4. Agent: Error or truncated response
```

**Problem**: Too many memories, context overflow, poor performance

### With GEPA Optimization

**Scenario**: Same agent, same 30 memories

```
1. Agent has 30 memories (15,000 tokens total)
2. Context limit: 2,000 tokens
3. GEPA-learned strategy: Select 6 most relevant (1,800 tokens)
4. Agent: High-quality response with perfect context
```

**Solution**: Optimized selection, perfect fit, better performance

---

## What GEPA Optimizes in Memory

### Context Selection (Which Memories to Include)

**What It Is**: Learning which memories are relevant for each query

**What GEPA Learns**:
- Relevance scoring (semantic similarity to query)
- Importance weighting (critical vs. minor info)
- Recency balance (recent vs. older memories)
- Task-specific patterns

**Example Configuration**:

```yaml
spec:
  memory:
    enabled: true
    enable_context_optimization: true  # GEPA optimizes selection!
    max_context_tokens: 2000
    short_term_capacity: 100
```

**Before Optimization**:
```
Strategy: Include all recent memories chronologically
Result: 
- Context overflow (15,000 tokens > 2,000 limit)
- Irrelevant memories included
- Important older memories excluded
```

**After GEPA Optimization**:
```
Learned Strategy:
For security query:
  1. Search for memories matching "security", "SQL", "vulnerability"
  2. Prioritize: High importance memories (0.8-1.0)
  3. Include: Recent similar findings (last 7 days)
  4. Summarize: Older related memories
  5. Stop at: 1,800 tokens (buffer for response)

Result:
- 6 highly relevant memories selected
- Fits perfectly in 2,000 token budget
- Includes critical past findings
```

**Impact**: 60% fewer tokens, 55% higher relevance, better performance

---

### Relevance Scoring (How to Score Memories)

**What It Is**: Calculating how relevant each memory is to current query

**What GEPA Learns**:
- Semantic similarity weights
- Keyword matching importance
- Category matching
- Task-specific relevance

**Scoring Algorithm** (GEPA-Optimized):

```python
# Pseudocode showing what GEPA learns

def score_memory(memory, query, task_type):
    # GEPA learns optimal weights for each task type
    weights = get_task_weights(task_type)  # GEPA optimizes these!
    
    relevance = calculate_similarity(query, memory.content)
    importance = memory.importance
    recency = calculate_recency(memory.timestamp)
    
    # GEPA learns optimal combination
    final_score = (
        relevance * weights['relevance'] +      # GEPA learned: 0.5
        importance * weights['importance'] +    # GEPA learned: 0.3
        recency * weights['recency']            # GEPA learned: 0.2
    )
    
    return final_score
```

**Before Optimization**:
```
Weights: Equal (0.33, 0.33, 0.33)
Result: Recent but irrelevant memories rank high
```

**After GEPA Optimization**:
```
Learned Weights (Security Task):
- relevance: 0.6 (prioritize semantic match)
- importance: 0.3 (critical findings matter)
- recency: 0.1 (older security patterns still valid)

Learned Weights (Conversation Task):
- relevance: 0.4
- importance: 0.2
- recency: 0.4 (recent context matters more)
```

**Impact**: Task-specific scoring produces better context

---

### Token Budget Management

**What It Is**: Fitting memories within context window constraints

**What GEPA Learns**:
- How many memories to include
- When to summarize vs. include full memory
- Buffer allocation for response
- Compression strategies

**Before Optimization**:
```
Approach: Include memories until limit reached
Result:
- Memory 1: 500 tokens (full)
- Memory 2: 500 tokens (full)
- Memory 3: 500 tokens (full)
- Memory 4: 500 tokens (full)
- Total: 2,000 tokens (no buffer for response!)
```

**After GEPA Optimization**:
```
Learned Strategy:
- Reserve 200 tokens for response buffer
- Budget: 1,800 tokens for memories
- Strategy: Include top 3 full (450 tokens each)
- Summarize next 3 (150 tokens each)
- Total: 1,800 tokens (perfect fit!)
```

**Impact**: Better token allocation, room for quality responses

---

### Summarization Strategies

**What It Is**: Learning when and how to compress memories

**What GEPA Learns**:
- When to summarize (old, low-importance, large)
- How much to compress
- What information to preserve
- Summary format

**Before Optimization**:
```
Memory: "Customer John reported shipping issue with order #12345 on 
        Oct 15. He lives in California, ordered 3 items (laptop, mouse, 
        keyboard), paid $1,500, wants refund, mentioned he's traveling 
        next week..."
Length: 800 tokens
```

**After GEPA Optimization**:
```
Learned Summarization:
Summary: "Customer John: Order #12345 shipping issue, refund requested (Oct 15)"
Length: 50 tokens
Preserved: Customer name, order ID, issue type, request, date
Removed: Address, item details, payment (not relevant to current query)
```

**Impact**: 16x compression while preserving key info

---

## Before/After Comparison

### Scenario: Customer Support Query

**Agent Memory** (30 interactions, 15,000 tokens):
- Memories 1-5: Recent small talk (low importance)
- Memories 6-10: Previous product questions (medium importance)
- Memory 11: **Shipping issue with order #12345** (high importance)
- Memory 12: **Customer prefers email contact** (high importance)
- Memories 13-30: Various unrelated interactions

**Current Query**: "What happened with my shipping issue?"

**Before Memory Optimization**:
```
Selection: Last 10 memories chronologically (memories 21-30)
Included:
- Recent small talk about weather
- Question about product features
- Unrelated order status check
- More irrelevant recent context

Missing:
- Memory 11: Actual shipping issue details!
- Memory 12: Contact preference

Result: Agent says "I don't have information about shipping issues"
```

**After GEPA Memory Optimization**:
```
GEPA-Learned Selection Strategy:

1. Semantic Search: "shipping issue" matches Memory 11 (0.95 similarity)
2. Importance Filter: Memory 11 (0.9) and Memory 12 (0.8) ranked high
3. Recency Boost: Memory 11 is recent enough (5 days ago)
4. Token Allocation: Memory 11 (500 tokens) + Memory 12 (200 tokens) = 700 tokens

Selected Memories:
- Memory 11: Shipping issue with order #12345 (full text)
- Memory 12: Email contact preference (full text)
- Memory 28: Recent interaction (summarized, 100 tokens)
Total: 800 tokens (well under 2,000 limit)

Agent Response:
"I found information about your shipping issue.

Order #12345 Status:
- Reported: Oct 15
- Issue: Package delayed at distribution center
- Expected: Oct 25
- Tracking: Updated yesterday

I'll send detailed status to your email (your preferred contact method).

Would you like me to check current tracking status or escalate for faster delivery?"
```

**Improvement**: From "no information" → Complete, accurate response

---

## How GEPA Learns Memory Strategies

### The Optimization Process

1. **Analysis Phase**
   ```
   GEPA Observes:
   - Query about shipping issue
   - Agent selected recent irrelevant memories
   - Agent missed Memory 11 (actual shipping issue details)
   - Response was "I don't have that information" (FAIL)
   ```

2. **Reflection Phase**
   ```
   GEPA Reflection:
   "Agent failed because it selected recent memories chronologically 
    instead of semantically relevant memories. Query contained 'shipping 
    issue' which matches Memory 11 with 0.95 similarity. Need to prioritize 
    semantic relevance over recency for factual queries."
   ```

3. **Mutation Phase**
   ```
   GEPA Tests:
   - Strategy 1: Pure recency (chronological)
   - Strategy 2: Pure relevance (semantic)
   - Strategy 3: Balanced (0.6 relevance + 0.3 importance + 0.1 recency)
   ```

4. **Evaluation Phase**
   ```
   Results:
   - Strategy 1: 30% (misses key info)
   - Strategy 2: 70% (good but ignores recent context)
   - Strategy 3: 95% (balanced!) ← Winner!
   ```

5. **Selection Phase**
   ```
   GEPA Keeps: Strategy 3 (balanced approach)
   Fine-Tunes: Adjust weights per task type
   ```

**Result**: Learned task-specific memory selection strategies

---

## Best Practices

### Enable Context Optimization

```yaml
memory:
  enabled: true
  enable_context_optimization: true  # Critical!
  max_context_tokens: 2000
```

### Set Appropriate Token Budgets

```yaml
memory:
  max_context_tokens: 2000   # For general agents
  max_context_tokens: 4000   # For complex reasoning agents
  max_context_tokens: 1000   # For simple Q&A agents
```

### Use Memory Importance Levels

```python
# In code
memory.remember(
    content="Critical security finding: SQL injection",
    memory_type="long_term",
    importance=0.9  # High importance!
)

memory.remember(
    content="Small talk about weather",
    memory_type="short_term",
    importance=0.1  # Low importance
)
```

GEPA learns to prioritize high-importance memories.

### Define Memory-Aware RSpec-Style BDD Scenarios

```yaml
feature_specifications:
  scenarios:
    - name: memory_recall
      description: Agent should recall similar past issues
      given_memory:
        - content: "Previous SQL injection in authentication"
          importance: 0.9
      input:
        code: [SQL injection code]
      expected_output:
        review: Must mention "similar to previous finding"
```

---

## Common Memory Strategies GEPA Learns

### Strategy 1: Semantic Matching

**Before**: Chronological selection  
**After**: "For factual queries, prioritize memories with >0.80 semantic similarity"

### Strategy 2: Importance Weighting

**Before**: All memories equal weight  
**After**: "Always include high-importance memories (>0.8) regardless of age"

### Strategy 3: Task-Specific Balancing

**Before**: Same strategy for all tasks  
**After**: "Security queries: 60% relevance, 30% importance, 10% recency. Conversation: 40% relevance, 20% importance, 40% recency"

### Strategy 4: Dynamic Summarization

**Before**: Include full text or skip  
**After**: "Summarize memories >7 days old with <0.7 relevance to save tokens"

---

## Metrics and Results

### What Gets Measured

- **Selection Accuracy**: % of scenarios where right memories selected
- **Token Efficiency**: Average tokens used vs. budget
- **Relevance Score**: Average similarity of selected memories
- **Response Quality**: Agent performance with optimized context

### Typical Improvements

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
	<tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Metric</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Before</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After</td>
		<td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Token Usage</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">5,000 (overflow)</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>1,800</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">-64%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Memory Relevance</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">30%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+55%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Response Accuracy</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">45%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>90%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+45%</td>
	</tr>
	<tr>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Task Success Rate</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">50%</td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>85%</strong></td>
		<td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">+35%</td>
	</tr>
</table>

---

## Quick Start

### Enable Memory Optimization

```yaml
spec:
  # Memory configuration
  memory:
    enabled: true
    enable_context_optimization: true  # GEPA optimizes!
    max_context_tokens: 2000
    short_term_capacity: 100
  
  # GEPA automatically optimizes memory selection
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

GEPA will learn optimal memory selection strategies!

---

## Advanced: Memory-Specific Configuration

### Fine-Tune Memory Behavior

```yaml
memory:
  enabled: true
  enable_context_optimization: true
  
  # Token budget
  max_context_tokens: 2000
  
  # Capacity limits
  short_term_capacity: 100
  long_term_capacity: 1000
  
  # Embeddings for semantic search
  enable_embeddings: true
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  
  # Retention policy
  retention_policy: lru  # Least Recently Used
```

GEPA learns optimal configurations through optimization.

---

## Common Memory Strategies GEPA Learns

### Strategy 1: Task-Specific Weighting

**Before**: Same weights for all queries  
**After**:
- "Security queries: Prioritize high-importance memories (importance weight: 0.4)"
- "Conversation queries: Prioritize recent context (recency weight: 0.5)"
- "Knowledge queries: Prioritize semantic relevance (relevance weight: 0.6)"

### Strategy 2: Dynamic Summarization

**Before**: Include full memories or exclude them  
**After**: "Memories >7 days old: Summarize to 20% of original length if relevance <0.7"

### Strategy 3: Category-Aware Selection

**Before**: Ignore memory categories  
**After**: "For security query, prioritize memories with category='security_patterns'"

### Strategy 4: Similarity Clustering

**Before**: Select memories independently  
**After**: "If selecting memory about SQL injection, also include related memories about database security (cluster similar topics)"

---

## Integration with Other Layers

Memory optimization enhances other layers:

**Memory + Prompts**:
```
Optimized Memory: Includes past security finding
Optimized Prompt: "Reference similar past issues when available"
→ Agent says: "Similar to previous finding #47, this is SQL injection"
```

**Memory + RAG**:
```
Optimized Memory: Recalls "We used sql_injection.md doc before"
Optimized RAG: Retrieves same doc again for consistency
→ Consistent security recommendations across sessions
```

**Memory + Tools**:
```
Optimized Memory: "Last time complexity was 7, we refactored"
Optimized Tool: Calculates current complexity = 8
→ Agent says: "Similar to previous issue #23 (complexity 7). Recommend same refactoring approach"
```

---

## Real-World Example

### Use Case: Customer Support with Memory

**Agent Memory** (50 interactions over 2 weeks):

| ID | Content | Type | Importance | Age | Tokens |
|----|---------|------|-----------|-----|--------|
| M1 | Small talk about weather | short_term | 0.1 | 1h | 50 |
| M2 | Product feature question | short_term | 0.3 | 2h | 150 |
| M3 | **Order #12345 shipping issue reported** | long_term | **0.9** | 5 days | 400 |
| M4 | **Customer prefers email contact** | long_term | **0.8** | 5 days | 100 |
| M5 | Unrelated billing question | short_term | 0.4 | 1 day | 200 |
| ... | ... | ... | ... | ... | ... |
| M50 | Small talk yesterday | short_term | 0.1 | 1 day | 50 |

**Total**: 15,000 tokens, **Budget**: 2,000 tokens

**Query**: "What's the status of my shipping issue?"

**Before Memory Optimization**:
```
Selection: Last 20 memories chronologically (M31-M50)
Total Tokens: 2,100 (overflow!)
Relevance: 25% (mostly irrelevant recent chat)

Included:
- M50: Small talk about weather (irrelevant)
- M49: Product question (irrelevant)
- M48: Another product question (irrelevant)
- ... more irrelevant memories
- M31: Unrelated topic

Missing:
- M3: Actual shipping issue! (excluded because too old)
- M4: Contact preference (excluded)

Result: Agent can't answer the question!
```

**After GEPA Memory Optimization**:
```
GEPA-Learned Selection Strategy:

Step 1: Semantic Search
- Query: "shipping issue"
- M3 matches with 0.95 similarity ← Highly relevant!
- M4 matches with 0.60 similarity ← Contact info

Step 2: Importance Weighting
- M3: importance = 0.9 (high priority!)
- M4: importance = 0.8 (high priority!)

Step 3: Token Allocation
- M3: 400 tokens (full, most important)
- M4: 100 tokens (full, contact pref)
- M47-M50: 300 tokens (recent context, summarized)
- Total: 800 tokens (40% of budget)

Step 4: Final Selection
Selected: M3, M4, M47-M50 (6 memories)
Tokens: 800 (under budget)
Relevance: 85% (highly relevant)

Agent Response:
"Your order #12345 shipping issue status:

Original Report (Oct 15):
- Package delayed at distribution center
- Expected delivery: Oct 25

Current Status:
- Tracking updated yesterday
- Package in transit
- Estimated arrival: Oct 24 (1 day early!)

I'll send detailed tracking to your email (your preferred contact method).

Would you like me to set up delivery notifications?"
```

**Improvement**: From "no information" → Complete, personalized response

---

## Troubleshooting

### Issue: Context Overflow

**Symptoms**: Agent errors or truncated responses

**Solutions**:
1. Reduce `max_context_tokens`
2. Enable `enable_context_optimization: true`
3. Increase summarization aggressiveness
4. Use shorter memory formats

### Issue: Irrelevant Memories Selected

**Symptoms**: Agent includes off-topic memories

**Solutions**:
1. Add RSpec-style BDD scenarios with `given_memory` showing expected selection
2. Increase importance scores for critical memories
3. Tune semantic similarity threshold
4. Optimize with more diverse scenarios

### Issue: Important Memories Excluded

**Symptoms**: Agent misses key information

**Solutions**:
1. Increase `importance` score when storing critical info
2. Use `memory_type: long_term` for persistent info
3. Add category tags for better organization
4. Increase `max_context_tokens` budget

---

## Related Guides

- [💬 Prompt Optimization](prompts.md) - Optimize instructions
- [🔍 RAG Optimization](rag.md) - Optimize knowledge retrieval
- [🛠️ Tool Optimization](tools.md) - Optimize tool usage
- [🔌 Protocol Optimization](protocols.md) - Optimize protocols
- [🎯 Full-Stack Example](full-stack-example.md) - See all layers
- [Memory Optimization Guide](../memory-optimization.md) - Implementation details
- [Memory Systems Guide](../memory.md) - Memory architecture

---

**Next**: Learn how GEPA optimizes [protocol usage patterns (MCP) →](protocols.md)

