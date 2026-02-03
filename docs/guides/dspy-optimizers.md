# 🔬 DSPy Optimizers: Pure DSPy Mode

SuperOptiX provides **pure DSPy optimization** without mixing frameworks. Use DSPy's powerful optimization capabilities while maintaining clean, framework-specific workflows.

**🌟 Key Achievement**: DSPy agents optimized with GEPA achieve **37.5% → 80%** improvement (+42.5 points)!

## Overview

DSPy optimizers automatically improve your agent's prompts and reasoning patterns through systematic optimization. SuperOptiX enhances this with:

- **Pure DSPy Mode**: No SuperOptiX mixing - clean DSPy workflows
- **Universal GEPA Integration**: Same GEPA optimizer works across all frameworks
- **Memory-Optimized Configurations**: Safe defaults for various system specs
- **Advanced Feedback Metrics**: Domain-specific evaluation functions
- **Smart Answer Extraction**: Handles various output formats automatically
- **Integration with SuperSpec**: Seamless YAML-based configuration

## 🚀 GEPA: The Universal Optimizer

**GEPA (Genetic-Pareto)** is SuperOptiX's universal optimizer that works across **all 6 frameworks**, including DSPy. It's proven to deliver dramatic improvements with minimal training data.

### DSPy + GEPA Results

**Proven Performance on DSPy Agents:**
- **Sentiment Analysis**: 37.5% → 80% (+42.5 points improvement)
- **Variables Optimized**: 10+ (signature instructions, field descriptions, reasoning steps)
- **Sample Efficiency**: Achieves improvements with just 3-10 scenarios
- **Framework**: Pure DSPy (no mixing with other frameworks)

### GEPA Configuration for DSPy

```yaml
spec:
  target_framework: dspy  # Pure DSPy mode
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: medium                    # light, medium, intensive
        reflection_lm: qwen3:8b
        reflection_minibatch_size: 3
        skip_perfect_score: true
        add_format_failure_as_feedback: true
```

**Key Features:**
- **Reflective Learning**: Self-improving prompts through feedback
- **Auto Modes**: `light` (fast), `medium` (balanced), `intensive` (thorough)
- **Advanced Metrics**: 7 domain-specific feedback functions
- **Memory Usage**: ~25GB peak
- **Pure DSPy**: No framework mixing

**Best For:** Complex reasoning tasks, mathematical problems, domain-specific optimization

🎯 **See GEPA in Action**: Check out our [interactive GEPA demo repository](https://github.com/SuperagenticAI/gepa-eval) for hands-on examples with before/after comparisons.

---

### ⚡ **SIMBA** - Alternative DSPy Optimizer
*Stochastic introspective mini-batch ascent (when GEPA isn't needed)*

```yaml
spec:
  target_framework: dspy  # Pure DSPy mode
  optimization:
    optimizer:
      name: SIMBA
      params:
        metric: answer_exact_match
        bsize: 8                       # Mini-batch size
        num_candidates: 4              # Candidate prompts per step
        max_steps: 4                   # Optimization steps
        max_demos: 3                   # Few-shot examples
        temperature_for_sampling: 0.2
        temperature_for_candidates: 0.2
```

**Key Features:**
- **Mini-Batch Processing**: Efficient batch optimization
- **Candidate Generation**: Multiple prompt variations per step
- **Temperature Control**: Fine-tuned sampling parameters
- **Memory Usage**: ~28GB peak
- **Pure DSPy**: No framework mixing

**When to Use SIMBA Instead of GEPA:**
- Large datasets (SIMBA handles batches better)
- Performance-critical applications (faster than GEPA)
- When you prefer statistical optimization over reflective learning
- When you have abundant training data

**Performance Comparison:**
- **GEPA**: 37.5% → 80% (+42.5 points) - Better for complex reasoning
- **SIMBA**: Good for systematic improvement with large datasets

---

### 🔧 **MIPROv2** - Multi-step Instruction Prompt Optimization
*Sophisticated prompt engineering with multiple steps*

```yaml
optimization:
  optimizer:
    name: MIPROv2
    params:
      metric: answer_exact_match
      num_candidates: 8              # Reduced from default 20
      init_temperature: 1.0
```

**Key Features:**
- **Multi-Step Optimization**: Iterative prompt refinement
- **Instruction Engineering**: Focus on instruction clarity
- **Candidate Exploration**: Multiple prompt variations
- **Memory Usage**: ~20GB peak

**Best For:** Instruction-following tasks, complex workflows, detailed reasoning

---

### 📚 **BootstrapFewShot** - Traditional Few-Shot Learning
*Reliable bootstrapping with few-shot examples*

```yaml
optimization:
  optimizer:
    name: BootstrapFewShot
    params:
      metric: answer_exact_match
      max_bootstrapped_demos: 4      # Generated examples
      max_labeled_demos: 16          # Manual examples
      max_rounds: 1                  # Optimization rounds
```

**Key Features:**
- **Bootstrap Learning**: Generate examples from existing data
- **Labeled Examples**: Incorporate manual examples
- **Round Control**: Multi-round optimization
- **Memory Usage**: ~18GB peak

**Best For:** Getting started, reliable baselines, limited training data

---

### 🤝 **BetterTogether** - Ensemble Few-Shot Learning
*Collaborative optimization with ensemble methods*

```yaml
optimization:
  optimizer:
    name: BetterTogether
    params:
      metric: answer_exact_match
      max_bootstrapped_demos: 3      # Generated examples
      max_labeled_demos: 12          # Manual examples
```

**Key Features:**
- **Ensemble Learning**: Combine multiple approaches
- **Collaborative Optimization**: Synergistic improvements
- **Example Integration**: Bootstrap + labeled examples
- **Memory Usage**: ~20GB peak

**Best For:** Robust performance, ensemble methods, collaborative learning

---

## 🎯 Choosing the Right Optimizer

### **Recommended: Start with GEPA** ⭐

For most DSPy use cases, **GEPA is the recommended choice**:

```yaml
spec:
  target_framework: dspy
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium  # Start here!
```

**Why GEPA?**
- ✅ **Proven Results**: 37.5% → 80% improvement
- ✅ **Sample Efficient**: Works with 3-10 scenarios
- ✅ **Universal**: Same optimizer works across all frameworks
- ✅ **Reflective Learning**: Self-improving prompts
- ✅ **Domain Adaptable**: Incorporates domain-specific feedback

### **When to Use Alternatives**

| Optimizer | Use When | Memory | Speed | Best For |
|-----------|----------|--------|-------|----------|
| **GEPA** | Most cases ⭐ | ~25GB | Medium | Complex reasoning, domain-specific |
| **SIMBA** | Large datasets | ~28GB | Fast | Batch processing, systematic improvement |
| **MIPROv2** | Instruction tasks | ~20GB | Medium | Multi-step workflows, detailed reasoning |
| **BootstrapFewShot** | Getting started | ~18GB | Fast | Baselines, limited data |
| **BetterTogether** | Ensemble needs | ~20GB | Medium | Robust performance, collaboration |

### **Quick Decision Guide**

```bash
# Start here for most cases
super agent optimize <agent> --auto medium  # Uses GEPA

# For large datasets
super agent optimize <agent> --optimizer simba

# For instruction-following tasks  
super agent optimize <agent> --optimizer miprov2

# For getting started
super agent optimize <agent> --optimizer bootstrapfewshot
```

---

### 🔍 **COPRO** - Collaborative Prompt Optimization
*Advanced collaborative optimization* ⚠️

```yaml
optimization:
  optimizer:
    name: COPRO
    params:
      metric: answer_exact_match
      breadth: 6                     # Search breadth
      depth: 2                       # Search depth
      init_temperature: 1.2
```

**Status:** ⚠️ Requires `LITELLM_DROP_PARAMS=true` environment variable

**Best For:** Collaborative optimization, search-based improvement

---

### 🎯 **KNNFewShot** - K-Nearest Neighbor Learning
*Pattern-based optimization* ⚠️

```yaml
optimization:
  optimizer:
    name: KNNFewShot
    params:
      k: 3                          # Nearest neighbors
```

**Status:** ⚠️ Requires vectorizer configuration (coming soon)

**Best For:** Pattern recognition, similarity-based learning

## Memory Optimization

SuperOptiX includes memory-optimized configurations for different system specifications:

### For 128GB Systems (M4 Max, High-End Workstations)
- **SIMBA**: `bsize: 8`, `candidates: 4`, `steps: 4`
- **MIPROv2**: `candidates: 8` (reduced from 20)
- **Peak Usage**: ~28GB (22% of available memory)

### For 64GB Systems
- **SIMBA**: `bsize: 4`, `candidates: 2`, `steps: 3`
- **MIPROv2**: `candidates: 4`
- **Peak Usage**: ~15GB (23% of available memory)

### For 32GB Systems
- **BootstrapFewShot**: Recommended default
- **BetterTogether**: `max_bootstrapped_demos: 2`
- **Peak Usage**: ~8GB (25% of available memory)

## Advanced Features

### Smart Answer Extraction

SuperOptiX automatically handles various answer formats:

```python
# LaTeX boxed format
"$\\boxed{345}$" → "345"

# Natural language
"The answer is 42." → "42"

# Algebraic format
"x = 3 or x = -1/2" → "3, -1/2"

# Numeric extraction
"The result is 25 square units" → "25"
```

### Domain-Specific Feedback Metrics

Advanced GEPA feedback functions for specialized domains:

- **`advanced_math_feedback`**: Mathematical accuracy with step validation
- **`medical_accuracy_feedback`**: Safety-focused medical information
- **`legal_analysis_feedback`**: Legal compliance and risk assessment
- **`vulnerability_detection_feedback`**: Security analysis
- **`privacy_preservation_feedback`**: Data privacy compliance
- **`data_science_methodology_feedback`**: Scientific rigor
- **`multi_component_enterprise_feedback`**: Enterprise information extraction

### Tier-Optimized Defaults

SuperOptiX automatically selects optimizers based on agent tier:

```python
# Oracles Tier (≤5 examples)
optimizer = "LabeledFewShot"

# Oracles Tier (>5 examples)  
optimizer = "BootstrapFewShot"

# Genies Tier
optimizer = "BetterTogether"

# Advanced Tiers (≥20 examples)
optimizer = "GEPA"
```

## 🚀 DSPy Workflow with GEPA

### **Recommended Workflow** (GEPA-First)

```bash
# 1. Initialize project
super init my_dspy_project
cd my_dspy_project

# 2. Pull a DSPy agent
super agent pull sentiment_analyzer  # Pure DSPy agent

# 3. Compile (pure DSPy mode)
super agent compile sentiment_analyzer

# 4. Baseline evaluation
super agent evaluate sentiment_analyzer

# 5. Optimize with GEPA (recommended!)
super agent optimize sentiment_analyzer --auto medium

# 6. Evaluate optimized version
super agent evaluate sentiment_analyzer  # automatically loads optimized weights

# 7. Run the optimized agent
super agent run sentiment_analyzer
```

### **Alternative Workflows**

=== "SIMBA (Large Datasets)"
    ```bash
    super agent optimize sentiment_analyzer --optimizer simba
    ```

=== "MIPROv2 (Instructions)"
    ```bash
    super agent optimize sentiment_analyzer --optimizer miprov2
    ```

=== "BootstrapFewShot (Getting Started)"
    ```bash
    super agent optimize sentiment_analyzer --optimizer bootstrapfewshot
    ```

### **Pure DSPy Configuration**

```yaml
# agent_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: sentiment_analyzer
spec:
  target_framework: dspy  # Pure DSPy mode
  optimization:
    optimizer:
      name: GEPA  # Recommended optimizer
      params:
        auto: medium
        metric: answer_exact_match
```
      reflection_lm: qwen3:8b
      reflection_minibatch_size: 3
      skip_perfect_score: true
      add_format_failure_as_feedback: true
```

### Custom Metrics

```python
# In optimizer factory
def custom_domain_feedback(example, pred, trace=None, *args, **kwargs):
    """Custom domain-specific feedback function."""
    expected = getattr(example, "answer", "")
    actual = getattr(pred, "answer", "")
    
    # Your custom evaluation logic
    score = evaluate_domain_specific_accuracy(expected, actual)
    feedback = generate_improvement_suggestions(expected, actual)
    
    return Prediction(score=score, feedback=feedback)
```

## Best Practices

### 1. **Start Simple, Scale Up**
```yaml
# Begin with BootstrapFewShot
optimizer:
  name: BootstrapFewShot
  
# Then move to GEPA for advanced needs
optimizer:
  name: GEPA
  params:
    auto: light  # Start with light mode
```

### 2. **Monitor Memory Usage**
```bash
# Check system memory before optimization
htop

# Use memory-safe configurations
# SuperOptiX provides optimized defaults
```

### 3. **Leverage BDD Scenarios**
```yaml
feature_specifications:
  scenarios:
    - name: quadratic_equation
      input:
        problem: "Solve 2x² - 5x - 3 = 0"
      expected_output:
        answer: "x = 3 or x = -1/2"
```

### 4. **Domain-Specific Optimization**
```yaml
# For mathematical problems
optimization:
  optimizer:
    name: GEPA
    params:
      metric: advanced_math_feedback
      
# For enterprise applications
optimization:
  optimizer:
    name: GEPA
    params:
      metric: multi_component_enterprise_feedback
```

### 5. **Iterative Improvement**
```bash
# Test baseline performance
super agent evaluate my_agent

# Optimize with light settings
super agent optimize my_agent

# Evaluate improvement
super agent evaluate my_agent

# Scale up if needed
# Edit playbook: auto: light → medium → heavy
```

## Troubleshooting

### Common Issues

#### Memory Errors
```bash
# Reduce batch sizes in playbook
bsize: 4          # Instead of 8
num_candidates: 2 # Instead of 4
```

#### COPRO Parameter Issues
```bash
# Set environment variable
export LITELLM_DROP_PARAMS=true
super agent optimize my_agent
```

#### Zero Scores
- Check answer format compatibility
- Use smart answer extraction (enabled by default)
- Verify BDD scenario expected outputs

#### Timeout Issues
- GEPA optimization takes 3-5 minutes (normal)
- Use `auto: light` for faster optimization
- Monitor system resources

### Performance Tips

1. **Use Appropriate Optimizer**: Match optimizer complexity to task complexity
2. **Optimize Memory**: Use provided memory-safe configurations
3. **Start Local**: Test with local models before cloud deployment
4. **Monitor Resources**: Watch memory and CPU usage during optimization
5. **Incremental Improvement**: Use `auto: light` → `medium` → `heavy` progression

## Integration Examples

### With Different Model Backends

```yaml
# Ollama (Local)
language_model:
  provider: ollama
  model: llama3.1:8b
  
optimization:
  optimizer:
    name: GEPA
    params:
      reflection_lm: qwen3:8b
```

```yaml
# OpenAI (Cloud)
language_model:
  provider: openai
  model: gpt-4-turbo
  
optimization:
  optimizer:
    name: MIPROv2
    params:
      num_candidates: 12  # Can use more with cloud
```

### With RAG Systems

```yaml
# Vector store integration
tools:
  - vectorstore_search

optimization:
  optimizer:
    name: BetterTogether  # Good for RAG workflows
    params:
      max_bootstrapped_demos: 4
```

### With Multi-Agent Systems

```yaml
# Orchestra coordination
optimization:
  optimizer:
    name: SIMBA          # Efficient for coordination
    params:
      bsize: 6
      max_steps: 3
```

## Performance Benchmarks

Based on testing with llama3.1:8b on M4 Max (128GB):

| Optimizer | Training Time | Memory Peak | Accuracy Gain | Best Use Case |
|-----------|---------------|-------------|---------------|---------------|
| BootstrapFewShot | 2-3 min | 18GB | +15-25% | Getting started |
| BetterTogether | 3-4 min | 20GB | +20-30% | Robust baselines |
| MIPROv2 | 4-6 min | 20GB | +25-35% | Instruction tasks |
| SIMBA | 5-7 min | 28GB | +30-40% | Performance critical |
| GEPA | 3-5 min | 25GB | +35-50% | Complex reasoning |

## Related Documentation

- [DSPy Official Documentation](https://dspy.ai/)
- [DSPy Optimization Overview](https://dspy.ai/learn/optimization/overview/)
- [GEPA Optimization Guide](gepa-optimization.md)
- [Agent Development Guide](agent-development.md)
- [Evaluation & Testing](evaluation-testing.md)
- [Memory Management](memory.md)
- [Model Management](model-management.md)

## Quick Start Guide

### 🚀 Complete DSPy Optimizer Workflow

Here are ready-to-run commands for each DSPy optimizer. Each example includes pull, compile, optimize, and test steps.

#### GEPA - Genetic-Pareto
**Best for**: Oracle-tier agents, complex reasoning, mathematical problems

```bash
# Quick start with GEPA demo agent
super agent pull gepa_demo
super agent compile gepa_demo
super agent optimize gepa_demo --timeout 300
super agent evaluate gepa_demo
super agent run gepa_demo --goal "Demonstrate reflective optimization capabilities"

# Advanced math with GEPA
super agent pull advanced_math_gepa
super agent compile advanced_math_gepa
super agent optimize advanced_math_gepa --timeout 300
super agent run advanced_math_gepa --goal "Solve x² + 5x - 6 = 0 showing all steps"
```

#### SIMBA - Stochastic Introspective Mini-Batch Ascent
**Best for**: Performance-critical applications, systematic improvement

```bash
# Mathematics problems with SIMBA
super agent pull simba_math
super agent compile simba_math
super agent optimize simba_math --timeout 300
super agent evaluate simba_math
super agent run simba_math --goal "Calculate the area of a circle with radius 7"

# General SIMBA optimization
super agent pull simba_playbook
super agent compile simba_playbook
super agent optimize simba_playbook --timeout 300
super agent run simba_playbook --goal "Optimize reasoning with mini-batch processing"
```

#### MIPROv2 - Multi-step Instruction Prompt Optimization
**Best for**: Instruction-following tasks, detailed reasoning

```bash
# Mathematics with MIPROv2
super agent pull miprov2_math
super agent compile miprov2_math
super agent optimize miprov2_math --timeout 300
super agent evaluate miprov2_math
super agent run miprov2_math --goal "Solve quadratic equation using multiple methods"

# General MIPROv2 optimization
super agent pull miprov2_playbook
super agent compile miprov2_playbook
super agent optimize miprov2_playbook --timeout 300
super agent run miprov2_playbook --goal "Demonstrate multi-step instruction optimization"
```

#### BootstrapFewShot - Traditional Few-Shot Learning
**Best for**: Getting started, reliable baselines, tool-calling agents

```bash
# Mathematics with Bootstrap
super agent pull bootstrap_math
super agent compile bootstrap_math
super agent optimize bootstrap_math --timeout 300
super agent evaluate bootstrap_math
super agent run bootstrap_math --goal "Solve algebraic equation with step-by-step explanation"

# General Bootstrap optimization
super agent pull bootstrapfewshot_playbook
super agent compile bootstrapfewshot_playbook
super agent optimize bootstrapfewshot_playbook --timeout 300
super agent run bootstrapfewshot_playbook --goal "Demonstrate traditional few-shot learning"
```

#### BetterTogether - Ensemble Few-Shot Learning
**Best for**: Robust performance, collaborative learning

```bash
# Mathematics with BetterTogether
super agent pull bettertogether_math
super agent compile bettertogether_math
super agent optimize bettertogether_math --timeout 300
super agent evaluate bettertogether_math
super agent run bettertogether_math --goal "Solve geometry problem using ensemble methods"

# General BetterTogether optimization
super agent pull bettertogether_playbook
super agent compile bettertogether_playbook
super agent optimize bettertogether_playbook --timeout 300
super agent run bettertogether_playbook --goal "Demonstrate ensemble optimization"
```

#### COPRO - Collaborative Prompt Optimization
**Best for**: Search-based improvement (requires special setup)

```bash
# Set required environment variable
export LITELLM_DROP_PARAMS=true

# Mathematics with COPRO
super agent pull copro_math
super agent compile copro_math
super agent optimize copro_math --timeout 300
super agent evaluate copro_math
super agent run copro_math --goal "Solve calculus problem with collaborative optimization"

# General COPRO optimization
super agent pull copro_playbook
super agent compile copro_playbook
super agent optimize copro_playbook --timeout 300
super agent run copro_playbook --goal "Demonstrate collaborative prompt optimization"
```

#### KNNFewShot - K-Nearest Neighbor Learning
**Best for**: Pattern recognition, similarity-based learning

```bash
# Mathematics with KNN
super agent pull knn_math
super agent compile knn_math
super agent optimize knn_math --timeout 300
super agent evaluate knn_math
super agent run knn_math --goal "Solve trigonometry using pattern recognition"

# General KNN optimization
super agent pull knnfewshot_playbook
super agent compile knnfewshot_playbook
super agent optimize knnfewshot_playbook --timeout 300
super agent run knnfewshot_playbook --goal "Demonstrate K-nearest neighbor optimization"
```

#### LabeledFewShot - Traditional Labeled Learning
**Best for**: Small datasets, simple scenarios

```bash
# Traditional labeled learning
super agent pull labeledfewshot_playbook
super agent compile labeledfewshot_playbook
super agent optimize labeledfewshot_playbook --timeout 300
super agent evaluate labeledfewshot_playbook
super agent run labeledfewshot_playbook --goal "Demonstrate traditional labeled few-shot learning"
```

---

### 📊 Comparison Workflow

Compare multiple optimizers on the same task:

```bash
# Test all optimizers on math problems
agents=("bootstrap_math" "bettertogether_math" "simba_math" "miprov2_math")

for agent in "${agents[@]}"; do
    echo "Testing $agent optimizer..."
    super agent pull $agent
    super agent compile $agent
    super agent evaluate $agent > baseline_$agent.txt
    super agent optimize $agent --timeout 300
    super agent evaluate $agent > optimized_$agent.txt
    echo "Results saved for $agent"
done

# Compare results
echo "Baseline vs Optimized Performance:"
for agent in "${agents[@]}"; do
    echo "=== $agent ==="
    echo "Baseline:" && cat baseline_$agent.txt
    echo "Optimized:" && cat optimized_$agent.txt
    echo ""
done
```

---

### 🎯 Domain-Specific Quick Starts

#### For Mathematical Problem Solving
```bash
# Try different optimizers for math
super agent pull advanced_math_gepa    # GEPA for complex reasoning
super agent pull simba_math           # SIMBA for performance
super agent pull miprov2_math         # MIPROv2 for instruction clarity
super agent pull bootstrap_math       # Bootstrap for reliability

# Pick one and optimize
super agent compile simba_math
super agent optimize simba_math --timeout 300
super agent run simba_math --goal "Find the integral of 2x³ + 3x² - x + 5"
```

#### For General Purpose Optimization
```bash
# Try general-purpose optimizers
super agent pull gepa_demo            # GEPA demonstration
super agent pull simba_playbook       # SIMBA optimization
super agent pull bettertogether_playbook  # Ensemble methods
super agent pull bootstrapfewshot_playbook  # Traditional approach

# Pick one and test
super agent compile bettertogether_playbook
super agent optimize bettertogether_playbook --timeout 300
super agent run bettertogether_playbook --goal "Demonstrate optimization capabilities"
```

#### For Tool-Calling Agents (Genies Tier+)
```bash
# GEPA doesn't work with tool-calling agents
# Use these optimizers instead:

super agent pull bootstrapfewshot_playbook  # Recommended default
super agent compile bootstrapfewshot_playbook
super agent optimize bootstrapfewshot_playbook --timeout 300

# Alternative: SIMBA for complex tool interactions
super agent pull simba_playbook
super agent compile simba_playbook
super agent optimize simba_playbook --timeout 300

# Alternative: BetterTogether for robust tool usage
super agent pull bettertogether_playbook
super agent compile bettertogether_playbook
super agent optimize bettertogether_playbook --timeout 300
```

---

## Available DSPy Optimizer Agents

SuperOptiX provides pre-configured agents demonstrating each DSPy optimizer:

### 🧮 Mathematics-Focused Agents

| Agent ID | Optimizer | Best For | Command |
|----------|-----------|----------|---------|
| `bootstrap_math` | BootstrapFewShot | Reliable baselines | `super agent pull bootstrap_math` |
| `bettertogether_math` | BetterTogether | Robust performance | `super agent pull bettertogether_math` |
| `simba_math` | SIMBA | Performance critical | `super agent pull simba_math` |
| `miprov2_math` | MIPROv2 | Instruction clarity | `super agent pull miprov2_math` |
| `copro_math` | COPRO | Search-based optimization | `super agent pull copro_math` |
| `knn_math` | KNNFewShot | Pattern recognition | `super agent pull knn_math` |

### 🔧 General Purpose Agents

| Agent ID | Optimizer | Best For | Command |
|----------|-----------|----------|---------|
| `gepa_demo` | GEPA | Complex reasoning demo | `super agent pull gepa_demo` |
| `bootstrapfewshot_playbook` | BootstrapFewShot | Traditional optimization | `super agent pull bootstrapfewshot_playbook` |
| `bettertogether_playbook` | BetterTogether | Ensemble learning | `super agent pull bettertogether_playbook` |
| `simba_playbook` | SIMBA | Advanced optimization | `super agent pull simba_playbook` |
| `miprov2_playbook` | MIPROv2 | Multi-step instructions | `super agent pull miprov2_playbook` |
| `copro_playbook` | COPRO | Collaborative optimization | `super agent pull copro_playbook` |
| `knnfewshot_playbook` | KNNFewShot | Similarity-based learning | `super agent pull knnfewshot_playbook` |
| `labeledfewshot_playbook` | LabeledFewShot | Traditional labeled learning | `super agent pull labeledfewshot_playbook` |

---

## Examples

Explore working examples in `/superoptix/agents/dspy_optimizers/`:

### Mathematical Problem Solving
- `bootstrap_math_playbook.yaml` - Traditional few-shot for math
- `bettertogether_math_playbook.yaml` - Ensemble learning for math
- `simba_math_playbook.yaml` - SIMBA for mathematics
- `miprov2_math_playbook.yaml` - MIPROv2 advanced prompting
- `copro_math_playbook.yaml` - Collaborative optimization for math
- `knn_math_playbook.yaml` - K-nearest neighbor for math

### General Purpose Optimization
- `gepa_playbook.yaml` - GEPA configuration and demonstration
- `bootstrapfewshot_playbook.yaml` - Traditional few-shot learning
- `bettertogether_playbook.yaml` - Ensemble learning methods
- `simba_playbook.yaml` - SIMBA optimization
- `miprov2_playbook.yaml` - Multi-step instruction optimization
- `copro_playbook.yaml` - Collaborative prompt optimization
- `knnfewshot_playbook.yaml` - K-nearest neighbor learning
- `labeledfewshot_playbook.yaml` - Traditional labeled few-shot

## Contributing

To add support for new DSPy optimizers:

1. **Update Factory Registry**:
```python
# In optimizer_factory.py
OPTIMIZER_REGISTRY = {
    "new_optimizer": NewOptimizer,
    # ...
}
```

2. **Add Default Parameters**:
```python
DEFAULT_PARAMS = {
    "new_optimizer": {
        "metric": "answer_exact_match",
        # optimizer-specific params
    }
}
```

3. **Create Configuration Method**:
```python
def _configure_new_optimizer(cls, optimizer_class, params):
    # Custom configuration logic
    return optimizer_class(**params)
```

4. **Add Documentation**: Update this guide with the new optimizer details.

5. **Create Test Agent**: Add example playbook in `/agents/dspy_optimizers/`.

---

SuperOptiX's DSPy integration provides a powerful, memory-efficient platform for prompt optimization that scales from simple few-shot learning to advanced graph-based optimization algorithms.