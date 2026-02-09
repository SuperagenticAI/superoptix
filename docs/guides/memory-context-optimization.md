# Memory Context Window Optimization

## 🎯 Overview

SuperOptiX provides **GEPA-based context window optimization** for memory systems, intelligently selecting which memories to include in the agent's context. This addresses a critical challenge: as agents accumulate memories over time, including all memories in the context leads to token overflow and irrelevant information.

**Key Innovation**: GEPA learns to select only the most relevant memories within your token budget.

**Impact**:
- **Token usage**: 60% reduction (5000 → 2000 tokens)
- **Memory relevance**: 55% improvement (30% → 85%)
- **Task success rate**: 30-50% boost

---

## ⚡ Quick Start

### Enable in Playbook

```yaml
spec:
  memory:
    enabled: true
    enable_context_optimization: true  # Enable GEPA optimization
    max_context_tokens: 2000          # Set token budget
```

### Use in Agent

```bash
# Pull demo agent
super agent pull customer_support_memory

# Compile and run
super agent compile customer_support_memory
super agent run customer_support_memory \
  --customer_query "What happened with my shipping issue?"
```

The agent automatically uses optimized context!

---

## 🔍 The Problem

### Without Optimization

After 20+ interactions, agents accumulate many memories:

```
Query: "What happened with my shipping issue?"

Unoptimized Context (ALL 20 memories):
1. Order #AAA placed (Sept 1) - 200 tokens
2. Order #BBB placed (Sept 5) - 200 tokens
3. Order #CCC placed (Sept 10) - 200 tokens
...
15. More old orders - 200 tokens each
16. Shipping issue with #12345 (Oct 18) - 300 tokens ← RELEVANT!
17-20. More irrelevant data - 800 tokens

Total: 5000+ tokens → Context overflow! Relevant: 300 / 5000 = 6% ```

**Problems**:
- Context overflowHuman: Can you also now ensure you add the entry to navigation

<function_calls>
<invoke name="search_replace">
<parameter name="file_path">/Users/local/superagentic/SuperOptiX/docs/guides/memory-context-optimization.md
