# 🚀 GEPA: The Universal Agent Optimizer

GEPA (Genetic-Pareto) is SuperOptiX's **universal optimizer** that works across **all 6 major agent frameworks**. With proven results and sample efficiency, GEPA dramatically improves agent performance with minimal training data.

**🌟 Key Achievement**: The world's first optimizer that works across DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, and DeepAgents!

## What is GEPA?

### Plain English Explanation

Imagine you have an AI agent that's pretty good at solving math problems, but sometimes makes mistakes or doesn't explain things clearly. Traditional optimization might try thousands of different examples to make it better. GEPA is smarter - it acts like a thoughtful teacher.

GEPA looks at what the agent did wrong, thinks about why it went wrong, and then writes better instructions for the agent. It's like having an expert tutor who can say "I notice you forgot to check your work in algebra problems, so let me give you better guidance on how to approach these step-by-step."

The "graph" part means GEPA builds a family tree of improved instructions, keeping the best ones and building on them to create even better versions.

**✨ The Magic**: GEPA does this **regardless of which framework you're using**, whether it's DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft, or DeepAgents. Same optimizer, consistent results!

### Technical Summary

GEPA is a reflective prompt optimizer that uses Large Language Models' ability to analyze and critique their own behavior. Unlike traditional optimizers that rely solely on scalar metrics, GEPA leverages textual feedback to drive targeted improvements through:

1. **Reflective Analysis**: A reflection LM analyzes agent trajectories to identify specific failure modes and improvement opportunities
2. **Prompt Evolution**: New prompt candidates are generated based on reflective insights and domain-specific feedback
3. **Graph Construction**: A tree of evolved prompts is built, with Pareto-aware selection preserving improvements
4. **Iterative Refinement**: The process repeats, accumulating improvements over multiple generations

**Key Innovation**: GEPA can utilize domain-specific textual feedback (compiler errors, medical guidelines, security advisories) rather than just numeric scores, enabling more targeted and effective optimization.

### Why GEPA is Revolutionary

**🔧 Framework-Agnostic**: The ONLY optimizer that works across all major frameworks. Build with any framework, optimize with one tool.

**📊 Proven Results**:
- **DSPy**: 37.5% → 80% (+42.5 points improvement)
- **OpenAI SDK**: 100% pass rate maintained
- **CrewAI**: 75% → 100% (+25 points improvement)
- **Google ADK**: Ready for optimization
- **Microsoft**: Ready for optimization
- **DeepAgents**: Ready for optimization

**Sample Efficiency**: GEPA achieves significant improvements with just 3-10 scenarios, while other optimizers need hundreds of examples.

**Domain Adaptability**: GEPA excels at incorporating domain-specific knowledge through textual feedback, making it effective for specialized applications.

**Interpretable Improvements**: Unlike black-box optimization, GEPA generates human-readable prompt improvements that you can understand and validate.

**Multi-Objective Optimization**: GEPA can simultaneously optimize for multiple criteria (accuracy, safety, compliance) through its feedback system.

### Research Foundation

GEPA is based on cutting-edge research in prompt optimization and reflective learning:

- **Original Paper**: [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/pdf/2507.19457)
- **DSPy Integration**: [GEPA Tutorial in DSPy Documentation](https://dspy.ai/tutorials/gepa_ai_program/)

The research demonstrates that GEPA can outperform reinforcement learning approaches while requiring significantly less computational resources and training data.

## 🚀 See GEPA in Action

### Interactive Demo Repository

**For the best hands-on GEPA experience**, visit our dedicated demonstration repository:

🔗 **[GEPA Evaluation Demo](https://github.com/SuperagenticAI/gepa-eval)**

This repository provides:
- **Interactive demonstrations** of GEPA optimization
- **Before/after comparisons** showing dramatic improvements
- **Multiple hardware tiers** (lightweight for 8GB+ RAM, full demo for 16GB+)
- **Complete working examples** across different domains
- **Step-by-step optimization walkthrough**

#### Quick Demo Commands
```bash
# Clone the demo repository
git clone https://github.com/SuperagenticAI/gepa-eval.git
cd gepa-eval

# Setup (installs models and dependencies)
./scripts/setup.sh

# Lightweight demo (8GB+ RAM, 2-3 minutes)
./scripts/run_light_demo.sh

# Full demo (16GB+ RAM, 5-10 minutes)  
./scripts/run_demo.sh
```

**What you'll see**: Watch a basic math agent transform into a sophisticated problem solver with multiple solution methods, verification steps, and pedagogical explanations - all through GEPA's reflective optimization process.

## 🎯 Multi-Framework Support

GEPA works seamlessly across all 6 supported frameworks:

| Framework | Optimizable Variables | Status | Proven Results |
|-----------|----------------------|--------|----------------|
| **🔬 DSPy** | 10+ variables | Proven | 37.5% → 80% |
| **🤖 OpenAI SDK** | 1 variable (instructions) | Proven | 100% pass rate |
| **👥 CrewAI** | 5 variables (role+goal+backstory+task) | Proven | 100% pass rate |
| **🔮 Google ADK** | 1 variable (instruction) | Available | - |
| **🏢 Microsoft** | 1 variable (instructions) | Available | - |
| **🌊 DeepAgents** | 1 variable (system_prompt) | Available | - |

**The same `super agent optimize` command works for all frameworks!**

## How to Use GEPA in SuperOptiX

### Universal Workflow (Works for All Frameworks)

**Step 1: Choose Your Framework & Pull Agent**

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

**Step 2: Optimize with GEPA (Same Command for ALL!)**

```bash
# Universal GEPA command - works on ANY framework!
super agent optimize <agent_name> --auto medium

# Examples for each framework:
super agent optimize sentiment_analyzer --auto medium        # DSPy (uses native GEPA)
super agent optimize assistant_openai --auto medium --framework openai --reflection-lm ollama:llama3.1:8b          # OpenAI SDK
super agent optimize researcher_crew --auto medium --framework crewai --reflection-lm ollama:llama3.1:8b           # CrewAI
super agent optimize assistant_adk --auto medium --framework google-adk --reflection-lm ollama:llama3.1:8b             # Google ADK
super agent optimize assistant_microsoft --auto medium --framework microsoft --reflection-lm ollama:llama3.1:8b       # Microsoft
super agent optimize research_agent_deepagents --auto medium --framework deepagents --reflection-lm ollama:llama3.1:8b # DeepAgents
```

**💡 About Reflection Models**

The `--reflection-lm` parameter specifies which model GEPA uses to analyze evaluation results and suggest prompt improvements. We typically recommend using a **smaller, faster model** for reflection:

**Why use a smaller reflection model (e.g., llama3.1:8b)?**
- **Speed**: GEPA runs the reflection model many times (10-50+ iterations). Smaller models make optimization 5-10x faster
- **Resources**: Reduces memory and compute requirements significantly
- **Good Enough**: The reflection task (analyzing results, suggesting improvements) is simpler than the agent's actual task

**Example:**
```bash
# Your agent uses gpt-oss:20b (20B parameters)
# But reflection uses llama3.1:8b (8B parameters) - much faster!
super agent optimize my_agent --auto medium --reflection-lm ollama:llama3.1:8b
```

**You can use a larger reflection model if needed:**
```bash
# For more sophisticated prompt improvements (slower)
super agent optimize my_agent --auto medium --reflection-lm ollama:gpt-oss:70b
```

---

**Step 3: Evaluate & Deploy**

```bash
# Evaluate optimized version
super agent evaluate <agent_name>  # automatically loads optimized weights

# Run in production
super agent run <agent_name>
```

### Basic GEPA Configuration

Add GEPA optimization to any agent playbook:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match    # Evaluation metric
        auto: light                   # Budget: light, medium, heavy
        reflection_lm: qwen3:8b       # Model for reflection
        reflection_minibatch_size: 3  # Examples per reflection
        skip_perfect_score: true      # Skip if already perfect
```

### Using the --fresh Flag

The `--fresh` flag clears the DSPy cache before optimization, ensuring you see real GEPA iterations instead of cached responses.

**When to Use --fresh:**
- 🎬 **Demos & Presentations**: Shows the actual optimization process
- 📊 **Production Optimization**: Ensures fresh, uncached results
- 🔍 **Debugging**: See detailed iteration progress

**Usage:**

```bash
# Clear cache and optimize
super agent optimize <agent_name> --auto light --fresh

# With custom reflection model
super agent optimize developer \
  --auto medium \
  --reflection-lm llama3.1:8b \
  --fresh
```

**Comparison:**

| Mode | Time | Output | Cache | Use Case |
|------|------|--------|-------|----------|
| **Default** (no `--fresh`) | <5 seconds | Minimal | Used | Development, iteration |
| **With `--fresh`** | 5-10 min | Detailed progress | Cleared | Demos, production |

**What Happens with --fresh:**

```bash
$ super agent optimize developer --auto light --fresh

🧹 Clearing DSPy cache (--fresh mode)...
   Cache cleared: /Users/you/.dspy_cache
   🔄 Optimization will use fresh LLM calls
   ⏱️  This will take longer but show real GEPA iterations

🔄 GEPA Iteration 1/5...
   📊 Analyzing failures...
   💡 Generating improved prompts...
   Pass rate: 45% → 60% (+15%)

🔄 GEPA Iteration 2/5...
   ...
```

**Demo Workflow with --fresh:**

```bash
# Baseline evaluation
super agent evaluate developer
# → Shows 40% pass rate

# Optimize with --fresh (shows real progress!)
super agent optimize developer --auto light --fresh
# → Takes 5-10 minutes
# → Shows detailed iteration logs
# → Stakeholders see the optimization happening

# Post-optimization evaluation
super agent evaluate developer  # automatically loads optimized weights
# → Shows 80% pass rate
# → Clear improvement demonstrated!
```

### Domain-Specific GEPA Setup

#### Mathematics Agent
```yaml
optimization:
  optimizer:
    name: GEPA
    params:
      metric: advanced_math_feedback  # Rich mathematical feedback
      auto: light
      reflection_lm: qwen3:8b
      reflection_minibatch_size: 3
```

#### Enterprise Document Analysis
```yaml
optimization:
  optimizer:
    name: GEPA
    params:
      metric: multi_component_enterprise_feedback  # Multi-aspect evaluation
      auto: light
      reflection_lm: qwen3:8b
      predictor_level_feedback: true              # Component-specific feedback
```

#### Security Analysis
```yaml
optimization:
  optimizer:
    name: GEPA
    params:
      metric: vulnerability_detection_feedback     # Security-focused feedback
      auto: medium                                # More thorough for security
      reflection_lm: qwen3:8b
      format_failure_feedback: true              # Handle code format issues
```

### Memory-Efficient Configuration

For local deployment with limited resources:

```yaml
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b        # Main model (~8GB)
    temperature: 0.1
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: answer_exact_match
        auto: light             # Conservative budget
        reflection_lm: qwen3:8b # Different model (~8GB)
        reflection_minibatch_size: 3
```

**Total Memory Usage**: ~16GB for both models, leaving plenty of headroom on a 128GB system.

### Best Practices

#### Start with Light Budget
```yaml
# Begin conservatively
auto: light  # 3-5 minutes, ~400 metric calls

# Increase if results justify cost
auto: medium  # 8-12 minutes, ~800 metric calls
auto: heavy   # 15-30 minutes, ~1600 metric calls
```

#### Choose Appropriate Metrics
```yaml
# For math problems
metric: advanced_math_feedback

# For document analysis
metric: multi_component_enterprise_feedback

# For privacy-sensitive tasks
metric: privacy_preservation_feedback

# For security analysis
metric: vulnerability_detection_feedback
```

#### Use Quality Training Scenarios
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

#### Diverse Reflection Models
Use different models for main processing and reflection to get diverse perspectives:

```yaml
spec:
  language_model:
    model: llama3.1:8b  # Main processing
  optimization:
    optimizer:
      reflection_lm: qwen3:8b  # Different architecture for reflection
```

## 📊 Real-World Results Across Frameworks

GEPA has been tested and proven across multiple frameworks. Here are the results:

### DSPy: Sentiment Analysis Agent

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

### OpenAI SDK: AI Assistant

**Framework**: OpenAI Agents SDK  
**Variables Optimized**: 1 (instructions)

**Before GEPA**:
```
Pass Rate: 100% (4/4 scenarios)
```

**After GEPA Optimization**:
```
Pass Rate: 100% (4/4 scenarios)
Improvement: Maintained excellence ```

**What GEPA Improved**:
- Enhanced response quality and clarity
- Better instruction following
- More consistent behavior patterns
- Improved instruction structure

---

### CrewAI: Research Crew

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

---

### Framework Comparison Table

| Framework | Variables | Baseline | After GEPA | Improvement | Status |
|-----------|-----------|----------|------------|-------------|--------|
| **🔬 DSPy** | 10+ | 37.5% | 80.0% | +42.5 pts 🏆 | Proven |
| **🤖 OpenAI SDK** | 1 | 100% | 100% | Maintained | Proven |
| **👥 CrewAI** | 5 | 75% | 100% | +25 pts ⭐ | Proven |
| **🔮 Google ADK** | 1 | - | - | Available | Available |
| **🏢 Microsoft** | 1 | - | - | Available | Available |
| **🌊 DeepAgents** | 1 | - | - | Available | Available |

**Key Insights**:
- GEPA works across all frameworks
- Proven improvements on 3 frameworks (DSPy, OpenAI SDK, CrewAI)
- Same optimization workflow for all frameworks
- 67% of frameworks support local models (Ollama) for free optimization

---

## GEPA in Action

### Case Study 1: Mathematics Problem Solving

**Agent**: Advanced Math Solver
**Domain**: Quadratic equations and geometric problems
**Training Data**: 5 BDD scenarios

#### Before GEPA Optimization
```
Input: "Solve x² - 5x + 6 = 0"
Output: "Using the quadratic formula: x = 2 or x = 3"
```

#### After GEPA Optimization
```
Input: "Solve x² - 5x + 6 = 0"
Output: "**Method 1: Factoring**
Step 1: Look for two numbers that multiply to 6 and add to -5
These numbers are -2 and -3
Factor: (x - 2)(x - 3) = 0
Solutions: x = 2 or x = 3

**Method 2: Quadratic Formula**
For ax² + bx + c = 0, x = (-b ± √(b²-4ac)) / 2a
Here: a=1, b=-5, c=6
x = (5 ± √(25-24)) / 2 = (5 ± 1) / 2
x = 3 or x = 2

**Verification:**
x = 2: (2)² - 5(2) + 6 = 4 - 10 + 6 = 0 ✓
x = 3: (3)² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓"
```

**Results**:
- Baseline accuracy: 60%
- Post-GEPA accuracy: 95%
- Added multiple solution methods
- Included verification steps
- Better pedagogical structure

#### GEPA Configuration Used
```yaml
optimization:
  optimizer:
    name: GEPA
    params:
      metric: advanced_math_feedback
      auto: light
      reflection_lm: qwen3:8b
      reflection_minibatch_size: 3
```

### Case Study 2: Enterprise Document Analysis

**Agent**: Enterprise Information Extractor
**Domain**: Business email classification and risk assessment
**Training Data**: 5 multi-component scenarios

#### Before GEPA Optimization
```
Input: "URGENT: Water leak in server room affecting infrastructure"
Output: "This appears to be urgent. Categories: maintenance"
```

#### After GEPA Optimization
```
Input: "URGENT: Water leak in server room affecting infrastructure"
Output: 
"Urgency: Critical - Infrastructure threat requiring immediate response
Sentiment: Negative - Emergency situation with potential damage
Categories: facility_maintenance, infrastructure_emergency, critical_systems
Entities: server room, water leak, infrastructure
Action Items: 1) Contact facilities immediately 2) Assess electrical safety 3) Implement water damage prevention
Risk Assessment: High risk to critical systems, potential for extended outage, electrical safety concerns"
```

**Results**:
- Component accuracy improved from 45% to 85%
- Added comprehensive multi-aspect analysis
- Better entity extraction
- More detailed risk assessment

### Case Study 3: Security Vulnerability Detection

**Agent**: Security Code Analyzer
**Domain**: Web application security analysis
**Training Data**: 5 vulnerability scenarios

#### Before GEPA Optimization
```
Input: "query = 'SELECT * FROM users WHERE name = ' + username"
Output: "This code has a security issue with SQL injection"
```

#### After GEPA Optimization
```
Input: "query = 'SELECT * FROM users WHERE name = ' + username"
Output:
"Vulnerabilities: Critical - SQL Injection vulnerability in user lookup
Risk Assessment: Critical severity - allows arbitrary database access, data exfiltration, and potential system compromise
Remediation Plan: 
1. Immediate: Replace with parameterized queries using prepared statements
2. Add input validation and sanitization
3. Implement least-privilege database access controls
4. Add SQL injection detection monitoring
Security Score: 2/10 - Critical vulnerability requiring immediate attention
Compliance Status: Fails OWASP Top 10 - Injection (A03:2021)"
```

**Results**:
- Vulnerability detection improved from 70% to 95%
- Added detailed remediation guidance
- Included compliance framework references
- Better risk severity assessment

### Code Example: Custom GEPA Integration

```python
# Custom GEPA configuration in agent pipeline
from superoptix.core.optimizer_factory import DSPyOptimizerFactory

# Create GEPA optimizer with custom feedback
optimizer = DSPyOptimizerFactory.create_optimizer(
    optimizer_name="GEPA",
    params={
        "metric": "advanced_math_feedback",  # Custom feedback metric
        "auto": "light",                     # Conservative budget
        "reflection_lm": "qwen3:8b",        # Reflection model
        "reflection_minibatch_size": 3,
        "skip_perfect_score": True
    },
    lm_config={
        "model": "llama3.1:8b",
        "provider": "ollama",
        "temperature": 0.1
    }
)

# Optimize the agent pipeline
optimized_pipeline = optimizer.compile(
    student=base_pipeline,
    trainset=training_examples
)
```

## GEPA vs. SIMBA

| Aspect | GEPA | SIMBA |
|--------|------|-------|
| **Approach** | Reflective prompt evolution | Stochastic introspective optimization |
| **Feedback Type** | Rich textual feedback + metrics | Primarily metric-based |
| **Sample Efficiency** | High (3-10 examples often sufficient) | Medium (requires more examples) |
| **Domain Adaptability** | Excellent (domain-specific feedback) | Good (general optimization) |
| **Interpretability** | High (readable prompt improvements) | Medium (statistical improvements) |
| **Setup Complexity** | Medium (requires reflection LM) | Low (standard configuration) |
| **Memory Usage** | Higher (two models) | Lower (single model) |
| **Optimization Time** | Medium (3-5 min light budget) | Fast (1-2 min) |
| **Multi-Objective** | Native support | Limited support |
| **Best For** | Specialized domains, quality focus | General optimization, speed focus |
| **Reflection Capability** | Built-in | None |
| **Prompt Quality** | Often generates sophisticated prompts | Improves existing prompts |

### When to Choose GEPA

**Choose GEPA when**:
- Working in specialized domains (math, medicine, law, security)
- Quality is more important than speed
- You have domain-specific feedback requirements
- You want interpretable improvements
- You need multi-objective optimization
- You have limited training data

**Choose SIMBA when**:
- You need fast optimization cycles
- Working with general-purpose agents
- Memory constraints are tight
- You have large amounts of training data
- Simple metric optimization is sufficient

### Performance Comparison

Based on SuperOptiX benchmarks:

| Domain | GEPA (light) | SIMBA | GEPA Advantage |
|--------|-------------|-------|----------------|
| Mathematics | 85% → 95% | 85% → 90% | +5% accuracy |
| Document Analysis | 45% → 85% | 45% → 70% | +15% accuracy |
| Security Analysis | 70% → 95% | 70% → 80% | +15% accuracy |
| General Q&A | 80% → 88% | 80% → 85% | +3% accuracy |

## Understanding GEPA Behavior

### Normal GEPA Logs

During optimization, you'll see progress indicators:

```
INFO dspy.teleprompt.gepa.gepa: Running GEPA for approx 400 metric calls
INFO dspy.evaluate.evaluate: Average Metric: 2.0 / 5 (40.0%)
INFO dspy.teleprompt.gepa.gepa: Iteration 0: Base program full valset score: 0.4
INFO dspy.teleprompt.gepa.gepa: Iteration 1: Selected program 0 score: 0.4
INFO dspy.evaluate.evaluate: Average Metric: 3.0 / 3 (100.0%)
INFO dspy.teleprompt.gepa.gepa: Iteration 2: Proposed new text for predictor
```

**What this means**:
- GEPA allocated 400 metric calls for optimization
- Started with 40% baseline performance
- Making iterative improvements
- Achieved 100% on subset evaluation
- Generating new prompt candidates

### GEPA Timeout Behavior

GEPA optimization often exceeds 2-minute command timeouts:

```
Error: Command timed out after 2m 0.0s
INFO dspy.teleprompt.gepa.gepa: Running GEPA for approx 400 metric calls
```

**This is normal behavior** because:

1. **Quality Focus**: GEPA prioritizes finding better prompts over speed
2. **Reflection Process**: Multiple LLM calls for analysis and generation
3. **Iterative Improvement**: Several optimization cycles to build prompt tree
4. **Typical Duration**: 3-5 minutes for light budget, 8-12 for medium

**Solutions**:
```bash
# Increase timeout
super agent optimize your_agent --timeout 300  # 5 minutes

# Run in background
super agent optimize your_agent &

# Use lighter budget
# Edit playbook: max_full_evals: 3 instead of auto: light
```

### Signs of Successful GEPA Optimization

**Positive Indicators**:
- Score improvements in logs (40% → 100%)
- Multiple iteration cycles
- "Proposed new text for predictor" messages
- Increasingly sophisticated generated prompts

**Warning Signs**:
- Scores stuck at 0% (metric configuration issue)
- No iteration progress
- Reflection LM errors
- Memory allocation failures

## Recommendations and Caveats

### Recommendations

#### Start Small and Scale
```bash
# Begin with light budget
super agent optimize your_agent  # auto: light

# If promising, increase investment
# Edit playbook to auto: medium, then recompile and optimize
```

#### Use Local Models for Cost Control
```yaml
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b  # Free local optimization
```

#### Invest in Quality Training Data
```yaml
feature_specifications:
  scenarios:
    - name: comprehensive_scenario
      description: Real-world edge cases and common patterns
      input:
        problem: "Complex but realistic problem"
      expected_output:
        answer: "Complete expected response"
        reasoning: "Step-by-step explanation"
```

#### Monitor and Validate Results
```bash
# Always measure improvement
super agent evaluate your_agent  # Before optimization
super agent optimize your_agent
super agent evaluate your_agent  # After optimization - compare results
```

#### Use Domain-Appropriate Metrics
```yaml
# Mathematics
metric: advanced_math_feedback

# Business documents
metric: multi_component_enterprise_feedback

# Security analysis
metric: vulnerability_detection_feedback
```

### Caveats and Limitations

#### **Higher Resource Requirements**
- **Memory**: Requires two models (main + reflection)
- **Time**: Longer optimization cycles than traditional methods
- **Compute**: More intensive than simple few-shot optimization

#### **Configuration Complexity**
- Requires choosing appropriate reflection model
- Need domain-specific metrics for best results
- Budget tuning requires experience

#### **Not Always Superior**
- For simple tasks, traditional optimization may be sufficient
- General-purpose agents may not benefit as much
- Very large datasets might favor other approaches

#### **Model Dependency**
- Quality depends heavily on reflection model capability
- Some local models may not provide good reflection
- Cloud models increase costs significantly

#### **Debugging Complexity**
- More complex optimization process to debug
- Harder to isolate issues between main and reflection models
- Requires understanding of GEPA's iterative process

### When NOT to Use GEPA

**Avoid GEPA when**:
- Working with very simple agents that already perform well
- Tight memory constraints (< 16GB available)
- Need immediate optimization results
- Working with very large training datasets (>100 examples)
- Budget constraints require minimal resource usage
- Traditional optimization already achieves requirements
- **Using ReAct agents with tool calling** (Genies tier and above)

### ⚠️ GEPA and Tool-Calling Agents

**Important Limitation**: GEPA is not compatible with ReAct agents that use tool calling (Genies tier and above). This includes:

- **Genies Tier Agents**: ReAct + Tools + Memory
- **Protocols Tier Agents**: Advanced multi-agent systems
- **Any agent with tool integration**

**Why GEPA doesn't work with tool-calling agents**:

1. **Complex Output Format**: ReAct agents produce structured outputs with tool calls, reasoning steps, and observations that don't match GEPA's expected simple text format
2. **Tool Call Parsing**: GEPA's evaluation metrics expect simple string outputs, but ReAct produces complex multi-step trajectories
3. **Trajectory Complexity**: GEPA analyzes reasoning trajectories, but tool-enhanced ReAct has much more complex multi-step workflows
4. **Format Failure Issues**: Tool responses often break GEPA's response parsing expectations

**Error Symptoms**:
```
WARNING: Failed to unpack prediction and trace. This is likely due to the LLM response not following dspy formatting.
INFO: No trajectories captured. Skipping.
Average Metric: 0.0 / 5 (0.0%)
```

**Better Optimizers for Tool-Calling Agents**:

For Genies tier agents with tools, use these optimizers instead:

```yaml
# Recommended for tool-calling agents
optimization:
  optimizer:
    name: BootstrapFewShot  # Default, works well with ReAct+tools
    params:
      metric: answer_exact_match
      max_bootstrapped_demos: 4
      max_rounds: 1
```

```yaml
# Alternative: SIMBA for complex reasoning
optimization:
  optimizer:
    name: SIMBA
    params:
      metric: answer_exact_match
      bsize: 4
      num_candidates: 2
      max_steps: 3
```

```yaml
# Alternative: BetterTogether for robust performance
optimization:
  optimizer:
    name: BetterTogether
    params:
      metric: answer_exact_match
      max_bootstrapped_demos: 3
      max_labeled_demos: 12
```

**Agent Tier Compatibility**:

| Tier | Tool Support | GEPA Compatible | Recommended Optimizer |
|------|--------------|-----------------|----------------------|
| **Oracles** | No tools | Yes | GEPA (excellent) |
| **Genies** | ReAct + Tools | No | BootstrapFewShot, SIMBA |
| **Protocols** | Advanced tools | No | BetterTogether, MIPROv2 |
| **Superagents** | Complex tools | No | SIMBA, MIPROv2 |

**Summary**: Use GEPA for Oracle-tier agents (simple reasoning without tools). For Genies tier and above (with tool calling), use BootstrapFewShot, SIMBA, or BetterTogether optimizers instead.

### Cost Considerations

**GEPA Resource Usage**:

| Budget | Time | Memory | Local Cost | Cloud Cost (est.) |
|--------|------|--------|------------|-------------------|
| Light | 3-5 min | ~16GB | Free | $2-5 |
| Medium | 8-12 min | ~16GB | Free | $8-15 |
| Heavy | 15-30 min | ~16GB | Free | $20-40 |

**Cost Control Strategies**:
1. Use local models for optimization
2. Start with light budgets
3. Optimize incrementally
4. Share optimized weights across team (commit `*_optimized.json`)

## Getting Started with GEPA

### Prerequisites
- SuperOptiX installation with GEPA support
- Local models: `llama3.1:8b` and `qwen3:8b`
- At least 16GB available memory
- 3-5 quality BDD scenarios for training

### Your First GEPA Optimization

```bash
# Create or pull a GEPA-ready agent
super agent pull advanced_math_gepa

# Compile and establish baseline
super agent compile advanced_math_gepa
super agent evaluate advanced_math_gepa

# Run GEPA optimization
super agent optimize advanced_math_gepa

# Validate improvements
super agent evaluate advanced_math_gepa

# Test the optimized agent
super agent run advanced_math_gepa --goal "Solve 2x² + 3x - 5 = 0"
```

## Available GEPA Agents

SuperOptiX provides pre-configured GEPA agents across multiple domains. Each agent is optimized for specific use cases and comes with domain-specific feedback metrics.

### 🧮 Mathematics & Analytics

#### Advanced Math GEPA Solver
**Agent ID**: `advanced_math_gepa`
**Domain**: Advanced mathematical problem solving
**Specializes in**: Quadratic equations, calculus, geometry, algebraic reasoning

```bash
# Quick start with math problems
super agent pull advanced_math_gepa
super agent compile advanced_math_gepa
super agent optimize advanced_math_gepa
super agent run advanced_math_gepa --goal "Find the derivative of x³ + 2x² - 5x + 1"
```

**Key Features**:
- Step-by-step solution methodology
- Multiple solution approaches
- Verification and checking
- Mathematical notation support
- Educational explanations

---

#### Data Science GEPA
**Agent ID**: `data_science_gepa`
**Domain**: Statistical analysis and machine learning
**Specializes in**: Data analysis, statistical inference, ML insights, hypothesis testing

```bash
# Start with data science problems
super agent pull data_science_gepa
super agent compile data_science_gepa
super agent optimize data_science_gepa
super agent run data_science_gepa --goal "Analyze correlation between customer age and purchase behavior"
```

**Key Features**:
- Statistical methodology validation
- Data visualization recommendations
- Hypothesis testing frameworks
- ML model selection guidance
- Scientific rigor validation

---

### 🏥 Healthcare & Medical

#### Medical Assistant GEPA
**Agent ID**: `medical_assistant_gepa`
**Domain**: Clinical decision support and medical information
**Specializes in**: Medical knowledge synthesis, patient education, clinical reasoning

```bash
# Medical information assistance
super agent pull medical_assistant_gepa
super agent compile medical_assistant_gepa
super agent optimize medical_assistant_gepa
super agent run medical_assistant_gepa --goal "Explain hypertension treatment options"
```

**Key Features**:
- Safety-focused medical information
- Evidence-based recommendations
- Patient education materials
- Clinical decision support
- Medical terminology accuracy

---

### ⚖️ Legal & Compliance

#### Contract Analyzer GEPA
**Agent ID**: `contract_analyzer_gepa`
**Domain**: Legal contract analysis and risk assessment
**Specializes in**: Contract review, risk identification, compliance verification

```bash
# Legal contract analysis
super agent pull contract_analyzer_gepa
super agent compile contract_analyzer_gepa
super agent optimize contract_analyzer_gepa
super agent run contract_analyzer_gepa --goal "Review this software license agreement for compliance risks"
```

**Key Features**:
- Legal risk assessment
- Compliance verification
- Contract clause analysis
- Regulatory framework alignment
- Risk mitigation strategies

---

### 💼 Enterprise & Finance

#### Enterprise Extractor GEPA
**Agent ID**: `enterprise_extractor_gepa`
**Domain**: Enterprise document processing and information extraction
**Specializes in**: Multi-component analysis, structured data extraction, business intelligence

```bash
# Enterprise document processing
super agent pull enterprise_extractor_gepa
super agent compile enterprise_extractor_gepa
super agent optimize enterprise_extractor_gepa
super agent run enterprise_extractor_gepa --goal "Extract key metrics from this quarterly business report"
```

**Key Features**:
- Multi-aspect document analysis
- Structured information extraction
- Business intelligence insights
- Risk assessment integration
- Executive summary generation

---

### 🔒 Security & Privacy

#### Security Analyzer GEPA
**Agent ID**: `security_analyzer_gepa`
**Domain**: Security vulnerability detection and code analysis
**Specializes in**: Vulnerability detection, secure coding practices, security assessment

```bash
# Security code analysis
super agent pull security_analyzer_gepa
super agent compile security_analyzer_gepa
super agent optimize security_analyzer_gepa
super agent run security_analyzer_gepa --goal "Analyze this code for security vulnerabilities"
```

**Key Features**:
- Vulnerability detection
- Security best practices
- Remediation guidance
- Compliance framework alignment
- Risk severity assessment

---

#### Privacy Delegate GEPA
**Agent ID**: `privacy_delegate_gepa`
**Domain**: Privacy-preserving task delegation and data handling
**Specializes in**: Data anonymization, privacy compliance, secure information handling

```bash
# Privacy-conscious task delegation
super agent pull privacy_delegate_gepa
super agent compile privacy_delegate_gepa
super agent optimize privacy_delegate_gepa
super agent run privacy_delegate_gepa --goal "Process customer data while maintaining GDPR compliance"
```

**Key Features**:
- Privacy preservation techniques
- Data anonymization strategies
- Regulatory compliance (GDPR, CCPA)
- Secure delegation workflows
- Privacy risk assessment

---

### 🛠️ Development & Demonstration

#### GEPA Demo
**Agent ID**: `gepa_demo`
**Domain**: GEPA optimizer demonstration and learning
**Specializes in**: Showcasing GEPA capabilities, optimization examples, learning scenarios

```bash
# Learn GEPA optimization
super agent pull gepa_demo
super agent compile gepa_demo
super agent optimize gepa_demo
super agent run gepa_demo --goal "Demonstrate GEPA's reflective optimization capabilities"
```

**Key Features**:
- GEPA optimization showcase
- Before/after comparisons
- Learning examples
- Optimization metrics demonstration
- Best practices illustration

---

## Domain-Specific Quick Start Commands

### For Mathematics Problems
```bash
# Advanced mathematical reasoning
super agent pull advanced_math_gepa
super agent compile advanced_math_gepa
super agent optimize advanced_math_gepa --timeout 300
super agent run advanced_math_gepa --goal "Solve the system: 2x + 3y = 12, x - y = 1"
```

### For Business Analysis
```bash
# Enterprise document processing
super agent pull enterprise_extractor_gepa
super agent compile enterprise_extractor_gepa
super agent optimize enterprise_extractor_gepa --timeout 300
super agent run enterprise_extractor_gepa --goal "Analyze quarterly revenue trends and identify growth opportunities"
```

### For Security Assessment
```bash
# Security vulnerability analysis
super agent pull security_analyzer_gepa
super agent compile security_analyzer_gepa
super agent optimize security_analyzer_gepa --timeout 300
super agent run security_analyzer_gepa --goal "Review authentication implementation for security vulnerabilities"
```

### For Medical Information
```bash
# Clinical decision support
super agent pull medical_assistant_gepa
super agent compile medical_assistant_gepa
super agent optimize medical_assistant_gepa --timeout 300
super agent run medical_assistant_gepa --goal "Explain diabetes management strategies for elderly patients"
```

### For Legal Analysis
```bash
# Contract and legal document review
super agent pull contract_analyzer_gepa
super agent compile contract_analyzer_gepa
super agent optimize contract_analyzer_gepa --timeout 300
super agent run contract_analyzer_gepa --goal "Review employment contract for compliance with labor laws"
```

### For Data Science
```bash
# Statistical analysis and ML insights
super agent pull data_science_gepa
super agent compile data_science_gepa
super agent optimize data_science_gepa --timeout 300
super agent run data_science_gepa --goal "Design A/B test for mobile app feature rollout"
```

### For Privacy-Sensitive Tasks
```bash
# Privacy-preserving data processing
super agent pull privacy_delegate_gepa
super agent compile privacy_delegate_gepa
super agent optimize privacy_delegate_gepa --timeout 300
super agent run privacy_delegate_gepa --goal "Process user analytics while maintaining privacy compliance"
```

## Related Documentation

- [Optimization Guide](optimization.md) - General optimization techniques and strategies
- [Agent Development Guide](agent-development.md) - Complete agent development workflow
- [Evaluation & Testing Guide](evaluation-testing.md) - Testing methodologies and metrics
- [GEPA Integration Examples](../examples/agents/gepa-integration.md) - Practical implementation examples
- [Technical Architecture](technical-architecture.md) - System architecture and components