# 🚀 Agent Optimization Strategy

SuperOptiX provides **universal optimization** across all 6 major agent frameworks using GEPA (Genetic-Pareto) as the primary optimizer.

**🌟 Key Achievement**: The world's first framework-agnostic optimizer that delivers proven results across DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, and DeepAgents!

## Overview

Agent optimization in SuperOptiX follows a **GEPA-first strategy** that works seamlessly across all supported frameworks:

- **🔧 Universal Optimizer**: Same GEPA optimizer works for all frameworks
- **📊 Proven Results**: DSPy 37.5% → 80%, OpenAI/CrewAI 100% pass rates
- **⚡ Sample Efficient**: Achieves improvements with just 3-10 scenarios
- **🎯 Framework Agnostic**: Build with any framework, optimize with one tool
- **🔄 Consistent Workflow**: Same commands work regardless of framework

## 🎯 GEPA: The Universal Optimization Strategy

### Why GEPA-First?

**GEPA (Genetic-Pareto)** is SuperOptiX's universal optimizer that delivers consistent results across all frameworks:

| Framework | Variables Optimized | Proven Results | Status |
|-----------|-------------------|----------------|--------|
| **🔬 DSPy** | 10+ variables | 37.5% → 80% (+42.5 pts) | ✅ Proven |
| **🤖 OpenAI SDK** | 1 variable (instructions) | 100% pass rate | ✅ Proven |
| **👥 CrewAI** | 5 variables (role+goal+backstory+task) | 100% pass rate | ✅ Proven |
| **🔮 Google ADK** | 1 variable (instruction) | Ready for optimization | ✅ Ready |
| **🏢 Microsoft** | 1 variable (instructions) | Ready for optimization | ✅ Ready |
| **🌊 DeepAgents** | 1 variable (system_prompt) | Ready for optimization | ✅ Ready |

### GEPA's Advantages

**🔧 Framework Agnostic**: The ONLY optimizer that works across all major frameworks
**📊 Sample Efficiency**: Achieves significant improvements with just 3-10 scenarios
**🎯 Domain Adaptable**: Incorporates domain-specific feedback effectively
**💡 Interpretable**: Generates human-readable prompt improvements
**🔄 Multi-Objective**: Optimizes for multiple criteria simultaneously

## 🚀 Universal Optimization Workflow

### **Step 1: Choose Your Framework & Pull Agent**

=== "🔬 DSPy"
    ```bash
    super agent pull sentiment_analyzer
    super agent compile sentiment_analyzer
    super agent evaluate sentiment_analyzer
    ```

=== "🤖 OpenAI SDK"
    ```bash
    super agent pull assistant_openai
    super agent compile assistant_openai
    super agent evaluate assistant_openai
    ```

=== "👥 CrewAI"
    ```bash
    super agent pull researcher_crew
    super agent compile researcher_crew
    super agent evaluate researcher_crew
    ```

=== "🔮 Google ADK"
    ```bash
    super agent pull assistant_adk
    super agent compile assistant_adk
    super agent evaluate assistant_adk
    ```

=== "🏢 Microsoft"
    ```bash
    super agent pull assistant_microsoft
    super agent compile assistant_microsoft
    super agent evaluate assistant_microsoft
    ```

=== "🌊 DeepAgents"
    ```bash
    super agent pull research_agent_deepagents
    super agent compile research_agent_deepagents
    super agent evaluate research_agent_deepagents
    ```

### **Step 2: Optimize with GEPA (Same Command for ALL!)**

```bash
# Universal GEPA command - works on ANY framework!
super agent optimize <agent_name> --auto medium

# Examples for each framework:
super agent optimize sentiment_analyzer --auto medium        # DSPy
super agent optimize assistant_openai --auto medium          # OpenAI SDK
super agent optimize researcher_crew --auto medium           # CrewAI
super agent optimize assistant_adk --auto medium             # Google ADK
super agent optimize assistant_microsoft --auto medium       # Microsoft
super agent optimize research_agent_deepagents --auto medium # DeepAgents
```

### **Step 3: Evaluate & Deploy**

```bash
# Evaluate optimized version
super agent evaluate <agent_name>  # automatically loads optimized weights

# Run in production
super agent run <agent_name>
```

## ⚙️ GEPA Configuration Options

### **Automatic Mode** (Recommended) ⭐

```bash
# Works for ANY framework!
super agent optimize <agent_name> --auto [light|medium|intensive]
```

**Optimization Levels:**
- `light`: Quick optimization (2-3 iterations, ~5 minutes)
- `medium`: Balanced optimization (5 iterations, ~10-15 minutes) ⭐ **Recommended**
- `intensive`: Thorough optimization (10+ iterations, ~30+ minutes)

### **Manual Configuration**

```bash
super agent optimize <agent_name> --optimizer gepa --max-iterations 5
```

### **Advanced Configuration** (via playbook)

Works for **all frameworks**! Edit your agent playbook:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match    # Evaluation metric
        auto: medium                  # Budget: light, medium, intensive
        reflection_lm: qwen3:8b       # Model for reflection
        reflection_minibatch_size: 3   # Examples per reflection
        skip_perfect_score: true      # Skip if already perfect
```

## 📊 Optimization Results by Framework

### **DSPy: Sentiment Analysis Agent**

**Framework**: DSPy (Stanford Research Framework)  
**Variables Optimized**: 10+ (signature instructions, field descriptions, reasoning steps, etc.)

**Before GEPA**:
```
Pass Rate: 37.5% (3/8 scenarios)
```

**After GEPA Optimization** (5 iterations, medium mode):
```
Pass Rate: 80.0% (6.5/8 scenarios)
Improvement: +42.5 percentage points 🏆
```

**What GEPA Improved**:
- Better nuanced sentiment identification
- Improved sarcasm and context handling
- More accurate confidence scores
- Clearer reasoning chains

---

### **OpenAI SDK: AI Assistant**

**Framework**: OpenAI Agents SDK  
**Variables Optimized**: 1 (instructions)

**Before GEPA**:
```
Pass Rate: 100% (4/4 scenarios)
```

**After GEPA Optimization**:
```
Pass Rate: 100% (4/4 scenarios)
Improvement: Maintained excellence ✅
```

**What GEPA Improved**:
- Enhanced response quality and clarity
- Better instruction following
- More consistent behavior patterns
- Improved instruction structure

---

### **CrewAI: Research Crew (Phase 2)**

**Framework**: CrewAI (Multi-Agent Collaboration)  
**Variables Optimized**: 5 (role, goal, backstory, task description, expected output)

**Before GEPA**:
```
Pass Rate: 75% (3/4 scenarios)
```

**After GEPA Optimization** (combined agent+task optimization):
```
Pass Rate: 100% (4/4 scenarios)
Improvement: +25 percentage points ⭐
```

**What GEPA Improved**:
- Clearer role definitions
- Better goal alignment with tasks
- Improved agent-task coordination
- Enhanced task output quality
- Better multi-agent collaboration patterns

## 🎯 When to Use Alternative Optimizers

While GEPA is recommended for most cases, here are alternatives for specific scenarios:

### **SIMBA** (DSPy Only)
**Use When**: Large datasets, performance-critical applications
```bash
super agent optimize <agent> --optimizer simba
```

### **MIPROv2** (DSPy Only)
**Use When**: Instruction-following tasks, multi-step workflows
```bash
super agent optimize <agent> --optimizer miprov2
```

### **BootstrapFewShot** (DSPy Only)
**Use When**: Getting started, limited training data
```bash
super agent optimize <agent> --optimizer bootstrapfewshot
```

## 📈 Best Practices

### **1. Always Establish Baseline**

```bash
# CRITICAL: Always evaluate before optimizing
super agent evaluate <agent_name>
```

### **2. Start with Medium Budget**

```bash
# Start with balanced optimization
super agent optimize <agent_name> --auto medium

# Increase if results justify cost
super agent optimize <agent_name> --auto intensive
```

### **3. Validate Improvements**

```bash
# Always re-evaluate after optimization
super agent evaluate <agent_name>  # automatically loads optimized weights
```

### **4. Use Quality Training Scenarios**

```yaml
feature_specifications:
  scenarios:
    - name: comprehensive_test
      description: Cover main patterns and edge cases
      input:
        problem: "Well-defined, realistic problem"
      expected_output:
        answer: "Complete expected response with reasoning"
```

### **5. Monitor Resource Usage**

**Memory Requirements**:
- **GEPA**: ~25GB peak (main model + reflection model)
- **Local Models**: Ollama works great for free optimization
- **Cloud Models**: Monitor API usage for cost control

## 🔧 Troubleshooting

### **Common Issues**

**Issue**: "Optimization failed"
**Solution**: Check BDD scenarios are well-defined and evaluable

**Issue**: "Memory error"
**Solution**: Use `--auto light` or switch to smaller models

**Issue**: "No improvement after optimization"
**Solution**: Check evaluation metrics and scenario quality

### **Performance Tips**

- **Local Models**: Use Ollama for free, unlimited optimization
- **Cloud Models**: Start with `light` budget to test effectiveness
- **Batch Processing**: Run multiple agents in parallel for efficiency

## 🚀 Next Steps

After optimization:

1. **Deploy**: Use `super agent run` with optimized weights
2. **Monitor**: Track performance in production
3. **Iterate**: Re-optimize when adding new scenarios
4. **Scale**: Apply same workflow to other frameworks

**Learn More**:
- [GEPA Optimization Guide](gepa-optimization.md) - Detailed GEPA documentation
- [Multi-Framework Support](multi-framework.md) - Framework comparisons
- [Evaluation & Testing](evaluation-testing.md) - Testing strategies