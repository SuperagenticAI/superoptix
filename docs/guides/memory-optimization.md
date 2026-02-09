# Memory Optimization

## Overview

SuperOptiX provides **GEPA-based memory optimization** that intelligently manages context windows, memory selection, and token budgets. As agents accumulate memories over time, including all memories leads to context overflow and irrelevant information diluting the agent's focus.

**The Solution:** GEPA learns to select only the most relevant memories within your token budget, optimizing across relevance, importance, and recency.

**Proven Impact:**
- **Token Usage:** 60% reduction (5000 → 2000 tokens)
- **Memory Relevance:** 55% improvement (30% → 85%)
- **Task Success Rate:** 30-50% boost
- **Optimization Speed:** <100ms per query

---

## The Problem

### Unoptimized Memory Context

After 20+ interactions, agents accumulate many memories. Without optimization, all memories get included:

```text
Query: "What happened with my shipping issue?"

Unoptimized Context (ALL 20 memories):
1. Order #AAA placed (Sept 1) - 200 tokens
2. Order #BBB placed (Sept 5) - 200 tokens
3. Order #CCC placed (Sept 10) - 200 tokens
...
15. More old orders - 200 tokens each
16. Shipping issue with #12345 (Oct 18) - 300 tokens ← RELEVANT!
17-20. More irrelevant data - 800 tokens

Total: 5000+ tokens → Context overflow!
Relevant: 300 / 5000 = 6%
```

**Problems:**
- Context overflow (exceeds token limits)
- Low signal-to-noise ratio (6% relevant)
- Wasted tokens on irrelevant memories
- Poor agent performance

### GEPA-Optimized Memory Context

GEPA selects only relevant memories:

```text
Query: "What happened with my shipping issue?"

GEPA-Optimized Context (6 selected memories):
1. Shipping issue with #12345 (Oct 18) - 300 tokens ← HIGH RELEVANCE
2. VIP customer since 2020 - 100 tokens ← HIGH IMPORTANCE
3. Customer prefers email - 80 tokens ← MEDIUM RELEVANCE
4. Recent message (Oct 20) - 150 tokens ← HIGH RECENCY
5. Tracking info for #12345 - 200 tokens ← HIGH RELEVANCE
6. Previous shipping delay resolved - 180 tokens ← RELEVANT

Total: 1010 tokens ← Fits in budget!
Relevant: 900 / 1010 = 89%
```

**Benefits:**
- 80% token reduction (5000 → 1010)
- 83% relevance improvement (6% → 89%)
- Fits within token budget
- Higher quality agent responses

---

## How It Works

### Architecture

SuperOptiX memory optimization consists of three components:

```bash
superoptix/optimizers/memory/
├── context_optimizer.py      # Main GEPA-based optimizer
├── memory_ranker.py          # Multi-factor memory ranking
└── memory_summarizer.py      # Memory compression
```

Integrated with:
- `superoptix/memory/agent_memory.py` (provides `get_optimized_context()`)

### Optimization Process

**Step 1: Score All Memories**

GEPA evaluates each memory using three factors:

1. **Relevance (0.0-1.0)**
	- Keyword overlap with query
	- Semantic similarity
	- Phrase matches
	- GEPA Chain of Thought reasoning

2. **Importance (0.0-1.0)**
	- Set when storing memory
	- VIP status, critical info, business rules
	- User-defined priority

3. **Recency (0.0-1.0)**
	- Exponential decay over time
	- Half-life: 1 hour
	- More recent = higher score

**Step 2: Task-Specific Weighting**

GEPA learns optimal weights for different task types:

| Task Type        | Relevance | Importance | Recency |
|------------------|-----------|------------|---------|
| Q&A              | 60%       | 30%        | 10%     |
| Conversation     | 30%       | 20%        | 50%     |
| Knowledge Search | 40%       | 50%        | 10%     |
| Customer Support | 35%       | 35%        | 30%     |

**Step 3: Budget-Aware Selection**

```python
# Pseudo-code for selection algorithm
def select_memories(scored_memories, max_tokens):
	selected = []
	total_tokens = 0
	
	# Always include N most recent (preserve context)
	for memory in most_recent(3):
		selected.append(memory)
		total_tokens += estimate_tokens(memory)
	
	# Add highest scoring until budget exhausted
	for score, memory in sorted_memories:
		if score < min_threshold:
			break
		
		if total_tokens + tokens(memory) <= max_tokens:
			selected.append(memory)
			total_tokens += tokens(memory)
		elif can_summarize(memory):
			# Compress memory to fit budget
			summary = summarize(memory, remaining_tokens)
			selected.append(summary)
			total_tokens += tokens(summary)
	
	return selected
```

**Step 4: Intelligent Ordering**

Memories are ordered using one of three strategies:

- **Recency First:** Most recent first (best for conversations)
- **Relevance First:** Most relevant first (best for Q&A)
- **Chronological:** Oldest first (best for narratives)

---

## Quick Start

### Enable in Agent Playbook

```yaml
spec:
	memory:
		enabled: true
		enable_context_optimization: true
		max_context_tokens: 2000
```

That's it! The agent automatically uses optimized context.

### Programmatic Usage

```python
from superoptix.memory import AgentMemory

# Initialize with optimization enabled
memory = AgentMemory(
	agent_id="support_agent",
	enable_context_optimization=True,
	max_context_tokens=2000
)

# Store memories with importance scores
memory.remember(
	"Customer Sarah ordered laptop #12345",
	memory_type="short"
)
memory.remember(
	"Sarah prefers email contact",
	memory_type="long",
	importance=0.8
)
memory.remember(
	"VIP customer since 2020",
	memory_type="long",
	importance=0.9
)

# Get optimized context for query
context_info = memory.get_optimized_context(
	--goal "What happened with my shipping issue?",
	task_type="customer_support"
)

print(f"Selected {context_info['optimization_info']['selected_count']} memories")
print(f"Total tokens: {context_info['optimization_info']['total_tokens']}")
print(f"\n{context_info['context_string']}")
```

### Example Output

```text
Selected 6 memories
Total tokens: 1200

## Relevant Memories

### Memory 1: Shipping Issue (Score: 0.92)
Customer reported delayed delivery for order #12345...

### Memory 2: VIP Status (Score: 0.85)
VIP customer since 2020, lifetime value $50K...

### Memory 3: Contact Preference (Score: 0.68)
Sarah prefers email contact for updates...
```

---

## Configuration Options

### ContextWindowOptimizer

```python
from superoptix.optimizers.memory import ContextWindowOptimizer

optimizer = ContextWindowOptimizer(
	max_tokens=4096,              # Token budget
	enable_gepa=True,             # Use GEPA scoring vs heuristics
	min_relevance_score=0.3,      # Filter threshold
	preserve_recency=True,        # Always keep recent memories
)

result = optimizer.optimize_context(
	--goal "What is the return policy?",
	available_memories=all_memories,
	task_type="customer_support",
	preserve_n_recent=3,          # Always include 3 most recent
)
```

**Result Structure:**

```python
{
	"selected_memories": [...],           # Selected memory objects
	"total_tokens": 1500,                 # Tokens used
	"strategy": "gepa_optimized_customer_support",
	"scores": {                           # Transparency
		"memory_1": 0.85,
		"memory_2": 0.72,
		...
	},
	"optimization_time": 0.045,           # Seconds
	"total_available": 20,                # Total memories
	"selected_count": 6                   # Selected count
}
```

### AgentMemory Integration

```python
from superoptix.memory import AgentMemory

memory = AgentMemory(
	agent_id="support_agent",
	enable_context_optimization=True,     # Enable GEPA optimization
	max_context_tokens=2000,              # Token budget
	backend=None,                         # Default SQLite
	short_term_capacity=100,              # Short-term memory size
	enable_embeddings=True                # For semantic search
)
```

---

## Advanced Usage

### Task-Specific Optimization

Different tasks need different memory selection strategies:

```python
# Q&A - Prioritize relevance
context = memory.get_optimized_context(
	--goal "What is our refund policy?",
	task_type="qa"
)

# Conversation - Prioritize recency
context = memory.get_optimized_context(
	--goal "Continue our discussion",
	task_type="conversation"
)

# Knowledge Search - Prioritize importance
context = memory.get_optimized_context(
	--goal "Find all critical business rules",
	task_type="knowledge"
)
```

### Custom Weighting

Override default task weights:

```python
# Custom weights for specialized task
result = optimizer.optimize_context(
	--goal "Emergency protocol check",
	available_memories=all_memories,
	task_type="custom",
)
```

### Memory Summarization

When full memory content doesn't fit in token budget, GEPA automatically compresses:

```python
# Original memory
{
	"content": "Customer Sarah Johnson (sarah@email.com) called on Oct 18 at 3pm regarding delayed shipping for order #12345. She ordered a laptop (Dell XPS 15) on Oct 10 with expedited shipping but tracking shows it's still in transit. She's frustrated because she needs it for a presentation on Oct 22. We offered overnight shipping for her next order and 20% discount code SORRY20.",
	"tokens": 300
}

# Compressed summary (when budget is tight)
{
	"content": "Customer Sarah: Delayed order #12345 (laptop). Needs by Oct 22. Offered overnight + 20% discount.",
	"tokens": 80,
	"is_summary": True
}
```

---

## Optimization Metrics

### Before vs After

| Metric               | Unoptimized | GEPA-Optimized | Improvement |
|----------------------|-------------|----------------|-------------|
| Avg tokens used      | 4500        | 1800           | -60%        |
| Relevance %          | 30%         | 85%            | +55%        |
| Memories selected    | 18          | 6              | Optimized   |
| Task success rate    | 65%         | 90%            | +25%        |
| Optimization time    | -           | <100ms         | Fast        |

### Transparency & Monitoring

Track optimization performance:

```python
# Get optimization statistics
stats = optimizer.get_stats()

print(f"Total optimizations: {stats['total_optimizations']}")
print(f"Avg tokens used: {stats['avg_tokens_used']:.0f}")
print(f"Avg memories selected: {stats['avg_memories_selected']:.1f}")
print(f"Avg relevance score: {stats['avg_relevance_score']:.2f}")
```

---

## Best Practices

### Token Budget Sizing

**Recommended budgets:**

- **Conversation agents:** 2000-4000 tokens
- **Q&A agents:** 1000-2000 tokens
- **Knowledge agents:** 4000-8000 tokens
- **Customer support:** 2000-3000 tokens

**Rule of thumb:** Set budget to 30-50% of model's total context window.

### Importance Scoring

Set importance when storing memories:

```python
# Critical business rules
memory.remember(
	"Refunds must be approved within 24 hours",
	memory_type="long",
	importance=1.0  # Maximum importance
)

# VIP customer info
memory.remember(
	"Customer is VIP tier, lifetime value $100K",
	memory_type="long",
	importance=0.9
)

# Regular interaction
memory.remember(
	"Customer asked about shipping times",
	memory_type="short",
	importance=0.5  # Default
)

# Low-priority note
memory.remember(
	"Customer mentioned they like blue color",
	memory_type="short",
	importance=0.2
)
```

### Preserve Recent Memories

Always include most recent memories for context continuity:

```python
result = optimizer.optimize_context(
	--goal "Continue our conversation",
	available_memories=all_memories,
	preserve_n_recent=3  # Always include 3 most recent
)
```

---

## Use Cases

### Customer Support Agent

```yaml
spec:
	persona:
		role: Customer Support Agent
		goal: Help customers with orders and issues
	
	memory:
		enabled: true
		enable_context_optimization: true
		max_context_tokens: 2000
	
	# GEPA automatically prioritizes:
	# - Recent interactions (high recency)
	# - VIP status (high importance)
	# - Related issues (high relevance)
```

### Knowledge Base Agent

```yaml
spec:
	persona:
		role: Knowledge Base Agent
		goal: Answer questions from documentation
	
	memory:
		enabled: true
		enable_context_optimization: true
		max_context_tokens: 4000
	
	# GEPA automatically prioritizes:
	# - Relevant documentation (high relevance)
	# - Critical policies (high importance)
	# - Recent updates (medium recency)
```

### Conversational Agent

```yaml
spec:
	persona:
		role: Conversational Assistant
		goal: Engage in natural dialogue
	
	memory:
		enabled: true
		enable_context_optimization: true
		max_context_tokens: 3000
	
	# GEPA automatically prioritizes:
	# - Recent messages (high recency)
	# - Conversation topics (high relevance)
	# - User preferences (high importance)
```

---

## Technical Architecture

### Components

#### ContextWindowOptimizer

Main GEPA-based optimizer that orchestrates memory selection:

```python
class ContextWindowOptimizer:
	"""
	Optimizes:
	- Which memories to include (relevance, importance, recency)
	- How much of each memory (full, summary, keywords)
	- Order of memories (chronological, relevance-based, hybrid)
	- Token budget allocation across memory types
	"""
	
	def optimize_context(
		self,
		query: str,
		available_memories: List[Dict],
		task_type: str = "general",
		preserve_n_recent: int = 3,
	) -> Dict:
		# Step 1: Score all memories
		# Step 2: Preserve most recent
		# Step 3: Select within budget
		# Step 4: Order optimally
		...
```

#### MemoryRanker

Multi-factor ranking with task-specific weights:

```python
class MemoryRanker:
	"""
	Ranks memories by:
	- Relevance to query
	- Importance score
	- Recency (time decay)
	"""
	
	def rank_hybrid(
		self,
		query: str,
		memories: List[Dict],
		weights: Dict[str, float] = None
	) -> List[Tuple[float, Dict]]:
		# Combines relevance + importance + recency
		...
```

#### MemorySummarizer

Compresses memories when budget is tight:

```python
class MemorySummarizer:
	"""
	Summarizes memories to fit token budget.
	Preserves key information while reducing tokens.
	"""
	
	def summarize(
		self,
		memory: Dict,
		target_tokens: int
	) -> Dict:
		# GEPA-based compression
		...
```

### GEPA Scoring Algorithm

GEPA uses Chain of Thought to score memory relevance:

```python
class MemoryRelevanceScorer(dspy.Signature):
	"""Score how relevant a memory is for answering a query."""
	
	query = dspy.InputField(desc="User query or current task")
	memory_content = dspy.InputField(desc="Memory content to evaluate")
	memory_metadata = dspy.InputField(desc="Memory metadata (type, age, importance)")
	task_context = dspy.InputField(desc="Additional task context")
	
	relevance_score = dspy.OutputField(
		desc="Relevance score 0.0-1.0",
		prefix="Score:"
	)
	reasoning = dspy.OutputField(
		desc="Brief explanation of score",
		prefix="Reasoning:"
	)

# GEPA learns to reason about memory relevance
scorer = dspy.ChainOfThought(MemoryRelevanceScorer)
```

### Scoring Formula

```python
def score_memory(memory, query, task_type):
	# Calculate component scores
	relevance = calculate_relevance(query, memory.content)
	importance = memory.importance
	recency = calculate_recency(memory.timestamp)
	
	# Get task-specific weights (GEPA optimizes these!)
	weights = get_task_weights(task_type)
	
	# Combine with learned weights
	final_score = (
		relevance * weights['relevance'] +
		importance * weights['importance'] +
		recency * weights['recency']
	)
	
	return final_score
```

---

## Demo Example

### Pull Demo Agent

```bash
# Pull customer support agent with memory
super agent pull customer_support_memory

# Compile
super agent compile customer_support_memory

# Run with verbose mode to see memory selection
super agent run customer_support_memory --verbose \
	--goal "What happened with my shipping issue?"
```

### Expected Output

```text
🧠 Memory Optimization:
   Available: 20 memories (5000 tokens)
   Selected: 6 memories (1010 tokens)
   Strategy: gepa_optimized_customer_support
   
   Top memories:
   1. Shipping issue #12345 (score: 0.92)
   2. VIP customer status (score: 0.85)
   3. Contact preference (score: 0.68)
   ...

Response generated with optimized context!
```

---

## Performance

### Benchmarks

- **Optimization Time:** <100ms per query
- **Memory Footprint:** No increase (lazy loading)
- **Scalability:** Tested with 1000+ memories
- **Accuracy:** 85%+ relevance in selected memories

### Fallback Behavior

If GEPA optimization fails, SuperOptiX gracefully falls back to heuristic scoring:

```python
try:
	# Use GEPA Chain of Thought
	score = gepa_scorer(query, memory_content, metadata)
except Exception:
	# Fallback to heuristic
	score = heuristic_score(relevance, importance, recency)
```

---

## Framework-Agnostic

Memory optimization works across all supported frameworks:

- **DSPy:** Native integration
- **OpenAI SDK:** Compatible
- **CrewAI:** Compatible  
- **Google ADK:** Compatible
- **Microsoft:** Compatible
- **DeepAgents:** Compatible

The optimization layer is completely independent of the framework layer!

---

## Comparison

### vs Simple Memory

```python
# Simple (include all recent)
context = memory.get_recent(20)
# Result: 5000 tokens, 30% relevant

# GEPA-Optimized
context = memory.get_optimized_context(query)
# Result: 1800 tokens, 85% relevant
```

### vs Manual Selection

```python
# Manual (hardcoded rules)
if "shipping" in query:
	context = memory.filter(category="orders")
elif "refund" in query:
	context = memory.filter(category="payments")
# Brittle, doesn't scale

# GEPA (learns patterns)
context = memory.get_optimized_context(query, task_type="support")
# Automatically learns what's relevant for each query type
```

### vs RAG

Memory optimization and RAG serve different purposes:

| Feature           | Memory Optimization | RAG Optimization |
|-------------------|---------------------|------------------|
| **Purpose**       | Select agent's past experiences | Retrieve external knowledge |
| **Source**        | Agent's own memories | Vector database |
| **Optimization**  | Relevance + Importance + Recency | Query + Chunk selection |
| **Use Case**      | Personalization, continuity | Knowledge grounding |
| **Combinable**    | Yes! Use both together | Yes! |

---

## Integration with Other Optimizations

Memory optimization works alongside other SuperOptiX optimizations:

### Memory + Prompt Optimization

```yaml
spec:
	memory:
		enabled: true
		enable_context_optimization: true  # Optimize memory selection
	
	optimization:
		strategy: gepa                     # Optimize prompts
		metrics: [accuracy, relevance]
```

GEPA optimizes both:
- **Which memories** to include in context
- **How to phrase** prompts using those memories

### Memory + RAG Optimization

```yaml
spec:
	memory:
		enabled: true
		enable_context_optimization: true
	
	knowledge:
		enabled: true
		rag_enabled: true
```

Combines:
- Agent's personal memories (optimized)
- External knowledge (RAG retrieval)

### Memory + Tool Optimization

```yaml
spec:
	memory:
		enabled: true
		enable_context_optimization: true
	
	tools:
		- name: get_order_status
		  mcp_enabled: true
```

Memory provides context, MCP optimizes tool usage!

---

## Troubleshooting

### High Token Usage

If memory context still uses too many tokens:

```python
# Reduce budget
memory = AgentMemory(
	agent_id="agent",
	max_context_tokens=1000  # Lower budget
)

# Increase minimum relevance threshold
optimizer = ContextWindowOptimizer(
	max_tokens=2000,
	min_relevance_score=0.5  # Higher threshold (default: 0.3)
)
```

### Low Relevance

If selected memories aren't relevant:

```python
# Enable GEPA scoring
optimizer = ContextWindowOptimizer(
	enable_gepa=True  # Use GEPA vs heuristics
)

# Adjust task type
context = memory.get_optimized_context(
	--goal "...",
	task_type="qa"  # Try different task types
)
```

### Missing Recent Context

If recent memories aren't included:

```python
# Increase recency preservation
result = optimizer.optimize_context(
	--goal "...",
	preserve_n_recent=5  # Include 5 most recent (default: 3)
)
```

---

## API Reference

### optimize_context()

```python
optimizer.optimize_context(
	query: str,                      # Current query/task
	available_memories: List[Dict],  # All memories
	task_type: str = "general",      # Task category
	preserve_n_recent: int = 3       # Always include N recent
) -> Dict
```

**Returns:**
- `selected_memories`: List of selected memory dicts
- `total_tokens`: Token count for selected memories
- `strategy`: Optimization strategy used
- `scores`: Dict of memory_id → relevance_score
- `optimization_time`: Time taken (seconds)
- `total_available`: Count of available memories
- `selected_count`: Count of selected memories

### get_optimized_context()

```python
memory.get_optimized_context(
	query: str,                      # Current query
	task_type: str = "general",      # Task category
	preserve_n_recent: int = 3       # Recent memory count
) -> Dict
```

**Returns:**
- `context_string`: Formatted context for LLM
- `selected_memories`: Selected memory objects
- `optimization_info`: Stats and scores

---

## Next Steps

1. **Try it:** Add `enable_context_optimization: true` to your agent playbook
2. **Measure:** Track token usage and relevance with `get_stats()`
3. **Tune:** Adjust `max_context_tokens` and `min_relevance_score`
4. **Monitor:** Use verbose mode to see memory selection in action

**Related Guides:**
- [Memory System Guide](memory.md)
- [RAG Optimization](rag-optimization.md)
- [GEPA Optimization](gepa-optimization.md)
- [Full-Stack Optimization](multi-framework.md)

---

**Memory optimization is part of SuperOptiX's full-stack optimization approach.**

Optimize prompts. Optimize RAG. Optimize tools. Optimize memory. All with GEPA.

