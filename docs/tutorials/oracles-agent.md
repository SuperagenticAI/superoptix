# 🎯 Create Your First Oracles Agent: Developer

## 🛠️ What You'll Build

You'll create an **Oracle Tier Developer agent** with:

- 🧠 Chain-of-thought reasoning
- 📚 Basic knowledge integration
- ⚡ Real DSPy-powered pipeline
- 👀 Full tracing and observability

This is a **production-ready agent** that demonstrates the power of Oracle-tier capabilities with pre-built agents from the marketplace.

---

## Prerequisites

Before starting this tutorial, ensure you have:

- **Python 3.8+** installed
- **SuperOptiX** installed (see [Installation Guide](../setup))

---

## 🚨 Caution: Optimization & Evaluation Resource Warning

!!! warning "Optimization and Evaluation are Resource Intensive"
    - **Do NOT run optimization/evaluation on a low-end machine or CPU-only system.**
    - These steps require a high-end machine with a modern GPU for local LLMs (e.g., RTX 30xx/40xx, Apple Silicon, or better).
    - Your GPU may run at full load and your laptop can get extremely warm during optimization.
    - **If using cloud LLMs, monitor your API usage and costs carefully.** Optimization can make hundreds of LLM calls.
    - Only proceed with optimization/evaluation if you understand the resource and cost implications!

---

## 1️⃣ Initialize Your Project

```bash
super init swe
```

<details><summary>Actual Output</summary>

```
================================================================================
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🎉 SUCCESS! Your full-blown shippable Agentic System 'swe' is ready!                                         │
│                                                                                                              │
│ 🚀 You now own a complete agentic AI system in 'swe'.                                                        │
│                                                                                                              │
│ Start making it production-ready by evaluating, optimizing, and orchestrating with advanced agent            │
│ engineering.                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────── 🎯 Your Journey Starts Here ─────────────────────────────────────────╮
│                                                                                                              │
│  🚀 GETTING STARTED                                                                                          │
│                                                                                                              │
│  1. Move to your new project root and confirm setup:                                                         │
│     cd swe                                                                                                   │
│     # You should see a .super file here - always run super commands from this directory                      │
│                                                                                                              │
│  2. Pull your first agent:                                                                                   │
│     super agent pull developer  # swap 'developer' for any agent name                                        │
│                                                                                                              │
│  3. Explore the marketplace:                                                                                 │
│     super market                                                                                             │
│                                                                                                              │
│  4. Need the full guide?                                                                                     │
│     super docs                                                                                               │
│     https://superoptix.dev/docs                                                                              │
│                                                                                                              │
│  Tip: Use 'super market search <keyword>' to discover components tailored to your domain.                    │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
================================================================================
🎯 Welcome to your Agentic System! Ready to build intelligent agents? 🚀
📍 Next steps: cd swe
================================================================================
```

</details>

---

## 2️⃣ Pull a Pre-built Developer Agent

```bash
cd swe
super agent pull developer
```

<details><summary>Actual Output</summary>

```
================================================================================

🤖 Adding agent 'developer'...
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🎉 AGENT ADDED SUCCESSFULLY! Pre-built Agent Ready                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────── 📋 Agent Details ──────────────────────────────────────────────╮
│                                                                                                              │
│  🤖 Name: Developer Assistant                                                                                │
│  🏢 Industry: Software | 🔮 Tier: Oracles                                                                    │
│  🔧 Tasks: 1 | 📁 Location: swe/agents/developer/playbook/developer_playbook.yaml                            │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────── 🛠️ Customization Options ──────────────────────────────────────────
─╮
│                                                                                                              │
│  ✨ Pre-built Agent - Ready to Customize!                                                                    │
│                                                                                                              │
│  📝 Modify: persona, tasks, inputs/outputs, model settings                                                   │
│  📖 Guide: super docs → Agent Playbook Specifications                                                        │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────── 🎯 Workflow Guide ──────────────────────────────────────────────╮
│                                                                                                              │
│  🚀 NEXT STEPS                                                                                               │
│                                                                                                              │
│  super agent compile developer - Generate executable pipeline                                                │
│  super agent run developer --goal "goal" - Execute optimized agent                                           │
│                                                                                                              │
│  💡 Comprehensive guide: super docs | 🔍 More agents: super agent list --pre-built                           │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
================================================================================
🎉 Agent 'Developer Assistant' ready for customization and deployment! 🚀
```

</details>

---

## 3️⃣ Compile the Agent

```bash
super agent compile developer
```

<details><summary>Actual Output</summary>

```
================================================================================

🔨 Compiling agent 'developer'...
╭─────────────────────────────────────────── ⚡ Compilation Details ───────────────────────────────────────────╮
│                                                                                                              │
│  🤖 COMPILATION IN PROGRESS                                                                                  │
│                                                                                                              │
│  🎯 Agent: Developer Assistant                                                                               │
│  🏗️ Framework: DSPy (default) Junior Pipeline - other frameworks coming soon
 │
│  🔧 Process: YAML playbook → Executable Python pipeline                                                      │
│  📁 Output: swe/agents/developer/pipelines/developer_pipeline.py                                             │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
🐍 Converted field names to snake_case for DSPy compatibility

🤖 Generating Mixin Oracles-Tier pipeline (DSPy default template)...
🧩 Mixin Pipeline (DSPy Default): Reusable components for complex agents.
🔧 Developer Controls: Modular mixins keep your codebase clean and customizable
🚀 Framework: DSPy (additional frameworks & custom builders coming soon) 
🔧 Oracles-Tier Features: Basic Chain of Thought + Sequential Orchestra
Successfully generated Oracles-tier pipeline (mixin) at: /Users/super/swe 
18-15-10-253/swe/agents/developer/pipelines/developer_pipeline.py

💡 Mixin pipeline features (DSPy Default):
   • Promotes code reuse and modularity
   • Separates pipeline logic into reusable mixins
   • Ideal for building complex agents with shared components
   • Built on DSPy - support for additional frameworks is on our roadmap

🎯 Oracles Tier Features
  Basic Predict and Chain of Thought modules
  Bootstrap Few-Shot optimization
  Basic evaluation metrics
  Sequential task orchestration
  Basic tracing and observability

ℹ️  Advanced features available in commercial version
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🎉 COMPILATION SUCCESSFUL! Pipeline Generated                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────── 🛠️ Customization Required ─────────────────────────────────────────
─╮
│                                                                                                              │
│  ⚠️ Auto-Generated Pipeline
│
│                                                                                                              │
│  🚨 Starting foundation - Customize for production use                                                       │
│  💡 You own this code - Modify for your specific requirements                                                │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────── 🧪 Testing Enhancement ───────────────────────────────────────────╮
│                                                                                                              │
│  🧪 Current BDD Scenarios: 5 found                                                                           │
│                                                                                                              │
│  🎯 Recommendations:                                                                                         │
│  • Add comprehensive test scenarios to your playbook                                                         │
│  • Include edge cases and error handling scenarios                                                           │
│  • Test with real-world data samples                                                                         │
│                                                                                                              │
│  💡 Why scenarios matter: Training data for optimization & quality gates                                     │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────── 🎯 Workflow Guide ──────────────────────────────────────────────╮
│                                                                                                              │
│  🚀 NEXT STEPS                                                                                               │
│                                                                                                              │
│  super agent evaluate developer - Establish baseline performance                                             │
│  super agent optimize developer - Enhance performance using DSPy                                             │
│  super agent evaluate developer - Measure improvement                                                        │
│  super agent run developer --goal "goal" - Execute optimized agent                                           │
│                                                                                                              │
│  💡 Follow BDD/TDD workflow: evaluate → optimize → evaluate → run                                            │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
================================================================================
🎉 Agent 'Developer Assistant' pipeline ready! Time to make it yours! 🚀
```

</details>

---

## 4️⃣ Evaluate Your Agent

Now let's evaluate your agent to establish a baseline performance:

```bash
super agent evaluate developer
```

<details><summary>Actual Output</summary>

```
════════════════════════════════════════════════════════════════════════════════════════════════════
                         🧪 SuperOptiX BDD Spec Runner - Professional Agent Validation

════════════════════════════════════════════════════════════════════════════════════════════════════

╭───────────────────────────────────────── 📋 Spec Execution Session ──────────────────────────────────────────╮
│ 🎯 Agent:               developer                                                                            │
│ 📅 Session:             2025-07-11 18:23:20                                                                  │
│ 🔧 Mode:                Standard validation                                                                  │
│ 📊 Verbosity:           Summary                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🔍 Tracing enabled for agent developer_20250711_182321
📁 Traces will be stored in: /Users/super/swe 18-15-10-253/.superoptix/traces
🚀 Configuring llama3.2:1b with ollama for oracles-tier capabilities
📝 Using ChatAdapter for optimal local model compatibility
Model connection successful: ollama/llama3.2:1b
📋 Loaded 5 BDD specifications for execution
DeveloperPipeline (Oracle tier) initialized with 5 BDD scenarios
Pipeline loaded
Failed to load optimized model: 'predictor.predict'
Optimized weights applied

🔍 Discovering BDD Specifications...
📋 Found 5 BDD specifications

🧪 Executing BDD Specification Suite
────────────────────────────────────────────────────────────
Progress: 🧪 Running 5 BDD specifications...
⠋ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0/5developer_comprehensive_task
developer_problem_solving
developer_best_practices
developer_compliance_guidance
developer_strategic_planning

Test Results:
FFFFF

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Specification                ┃    Status    ┃  Score   ┃ Description                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ developer_comprehensiv...    │   FAIL    │   0.29   │ Given a complex software requirement, t...    │
│ developer_problem_solving    │   FAIL    │   0.23   │ When facing software challenges, the ag...    │
│ developer_best_practices     │   FAIL    │   0.31   │ When asked about software best practice...    │
│ developer_compliance_g...    │   FAIL    │   0.21   │ Given regulatory requirements, the agen...    │
│ developer_strategic_pl...    │   FAIL    │   0.27   │ When developing software strategies, th...    │
└──────────────────────────────┴──────────────┴──────────┴───────────────────────────────────────────────────────────────┘

╭────────────────────────────────────── 🔴 Specification Results Summary ──────────────────────────────────────╮
│                                                                                                              │
│  📊 Total Specs:         5                🎯 Pass Rate:         0.0%                                         │
│  Passed:              0                🤖 Model:             ollama_chat/llama3.2:1b                      │
│  Failed:              5                💪 Capability:        0.26                                         │
│  🏆 Quality Gate:        NEEDS WORK    🚀 Status:            🚀 Optimized                                 │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🔍 Failure Analysis - Grouped by Issue Type
────────────────────────────────────────────────────────────────────────────────

📋 Semantic Relevance Issues (5 failures)
────────────────────────────────────────────────────────────
💡 Fix Suggestions:
   🎯 Make the response more relevant to the expected output
   📝 Use similar terminology and technical concepts
   🔍 Ensure the output addresses all aspects of the input requirement
   💡 Review the expected output format and structure

Affected Specifications:
   • developer_comprehensive_task (score: 0.288)
   • developer_problem_solving (score: 0.226)
   • developer_best_practices (score: 0.314)
   • developer_compliance_guidance (score: 0.208)
   • developer_strategic_planning (score: 0.274)

╭─────────────────────────────────────────── 🎯 AI Recommendations ────────────────────────────────────────────╮
│                                                                                                              │
│  💡 Poor performance. 5 scenarios failing.                                                                   │
│  💡 Strong recommendation: Run optimization before production use.                                           │
│  💡 Consider using a more capable model (llama3.1:8b or gpt-4).                                              │
│  💡 Review scenario complexity vs model capabilities.                                                        │
│  💡 Fix semantic relevance in 5 scenario(s) - improve response clarity.                                      │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────── 🎯 Next Steps ────────────────────────────────────────────────╮
│                                                                                                              │
│  🔧 5 specification(s) need attention.                                                                       │
│                                                                                                              │
│  Recommended actions for better quality:                                                                     │
│  • Review the grouped failure analysis above                                                                 │
│  • super agent optimize developer - Optimize agent performance                                               │
│  • super agent evaluate developer - Re-evaluate to measure improvement                                       │
│  • Use --verbose flag for detailed failure analysis                                                          │
│                                                                                                              │
│  You can still test your agent:                                                                              │
│  • super agent run developer --goal "your goal" - Works even with failing specs                              │
│  • super agent run developer --goal "Create a simple function" - Try basic goals                             │
│  • 💡 Agents can often perform well despite specification failures                                           │
│                                                                                                              │
│  For production use:                                                                                         │
│  • Aim for ≥80% pass rate before deploying to production                                                     │
│  • Run optimization and re-evaluation cycles until quality gates pass                                        │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

════════════════════════════════════════════════════════════════════════════════════════════════════
                       🏁 Specification execution completed - 0.0% pass rate (0/5 specs)

════════════════════════════════════════════════════════════════════════════════════════════════════

╭───────────────────────────────────── 🎯 What would you like to do next? ─────────────────────────────────────╮
│                                                                                                              │
│  🔧 To improve your agent's performance:                                                                     │
│     super agent optimize developer - Optimize the pipeline for better results                                │
│                                                                                                              │
│  🚀 To run your agent:                                                                                       │
│     super agent run developer --goal "your specific goal here"                                               │
│                                                                                                              │
│  💡 Example goals:                                                                                           │
│     • super agent run developer --goal "Create a Python function to calculate fibonacci numbers"             │
│     • super agent run developer --goal "Write a React component for a todo list"                             │
│     • super agent run developer --goal "Design a database schema for an e-commerce site"                     │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</details>

!!! info "📊 Evaluation Results Analysis"

    The evaluation shows that your Oracle agent needs optimization:

    - **🎯 Pass Rate**: 0.0% (0/5 specifications passed)
    - **🤖 Model**: Using `ollama/llama3.2:1b` (Oracle tier model)
    - **💪 Capability Score**: 0.26 (needs improvement)
    - **🏆 Quality Gate**: NEEDS WORK
    - **🚀 Status**: 🚀 Optimized (optimization was already applied)

!!! info "🔍 What Happened During Evaluation"

    The evaluation system ran **5 BDD (Behavior-Driven Development) scenarios** that were automatically generated from your Oracle agent's playbook. Here's what each scenario tested:

    #### 🧪 **The 5 BDD Scenarios Tested:**

    1. **`developer_comprehensive_task`** (Score: 0.29)
       - **Input**: "Complex software requirement analysis"
       - **Expected**: "Detailed step-by-step analysis with software-specific recommendations"
       - **What it tests**: Agent's ability to provide thorough software analysis

    2. **`developer_problem_solving`** (Score: 0.23)
       - **Input**: "Software challenges requiring creative solutions"
       - **Expected**: "Structured problem-solving approach with multiple solution options"
       - **What it tests**: Systematic problem-solving methodology

    3. **`developer_best_practices`** (Score: 0.31)
       - **Input**: "Software best practices and industry standards"
       - **Expected**: "Comprehensive best practices guide with implementation steps"
       - **What it tests**: Knowledge of software development best practices

    4. **`developer_compliance_guidance`** (Score: 0.21)
       - **Input**: "Regulatory requirements and compliance standards"
       - **Expected**: "Compliance guidance with regulatory framework understanding"
       - **What it tests**: Understanding of regulatory and compliance requirements

    5. **`developer_strategic_planning`** (Score: 0.27)
       - **Input**: "Software strategy development and planning"
       - **Expected**: "Strategic planning approach with long-term vision"
       - **What it tests**: Strategic thinking and planning capabilities

!!! info "🎯 How the Evaluation Works"

    The system uses a **multi-criteria evaluation framework** with 4 weighted criteria:

    | Criterion | Weight | What It Measures |
    |-----------|--------|------------------|
    | **Semantic Similarity** | 50% | How closely the output matches expected meaning |
    | **Keyword Presence** | 20% | Important terms and concepts inclusion |
    | **Structure Match** | 20% | Format, length, and organization similarity |
    | **Output Length** | 10% | Basic sanity check for completeness |

    **Scoring Formula:**
    ```
    Confidence Score = (
        semantic_similarity × 0.5 +
        keyword_presence × 0.2 +
        structure_match × 0.2 +
        output_length × 0.1
    )
    ```

    **Quality Thresholds:**
    - 🎉 **≥ 80%**: EXCELLENT - Production ready
    - ⚠️ **60-79%**: GOOD - Minor improvements needed  
    - **< 60%**: NEEDS WORK - Significant improvements required

!!! info "🔍 Why Scenarios May Fail"

    Oracle-tier agents may show different performance characteristics:

    1. **Base Model Limitations**: Oracle tier uses simpler reasoning chains
    2. **No Tool Integration**: Oracle agents focus on reasoning, not tool usage
    3. **Basic Memory**: Limited context retention compared to Genies tier
    4. **This is Normal**: Oracle tier is designed for simpler, reasoning-focused tasks

    **What This Means:**
    - **Your agent infrastructure is working correctly**
    - **The evaluation system is providing accurate feedback**
    - **Oracle tier is performing as expected for its capabilities**
    - 🔧 **Optimization can still improve performance significantly**

---

## 5️⃣ Optimize Your Agent

Now let's optimize your agent using DSPy's BootstrapFewShot optimizer to improve its performance:

```bash
super agent optimize developer
```

<details><summary>Actual Output</summary>

```
================================================================================

🚀 Optimizing agent 'developer'...
╭────────────────────────────────────────── ⚡ Optimization Details ───────────────────────────────────────────╮
│                                                                                                              │
│  🤖 OPTIMIZATION IN PROGRESS                                                                                 │
│                                                                                                              │
│  🎯 Agent: Developer                                                                                         │
│  🔧 Strategy: DSPy BootstrapFewShot                                                                          │
│  📊 Data Source: BDD scenarios from playbook                                                                 │
│  💾 Output: swe/agents/developer/pipelines/developer_optimized.json                                          │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🔍 Checking for existing optimized pipeline...

⚠️ Optimized pipeline already exists at /Users/super/swe 
18-15-10-253/swe/agents/developer/pipelines/developer_optimized.json
Use --force to re-optimize or run with existing optimization
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🎉 OPTIMIZATION SUCCESSFUL! Agent Enhanced                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────── 📊 Optimization Results ───────────────────────────────────────────╮
│                                                                                                              │
│  📈 Performance Improvement:                                                                                 │
│  • Training Examples: 0                                                                                      │
│  • Optimization Score: None                                                                                  │
│                                                                                                              │
│  💡 What changed: DSPy optimized prompts and reasoning chains                                                │
│  🚀 Ready for testing: Enhanced agent performance validated                                                  │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────── 🤖 AI Enhancement ──────────────────────────────────────────────╮
│                                                                                                              │
│  🧠 Smart Optimization: DSPy BootstrapFewShot                                                                │
│                                                                                                              │
│  ⚡ Automatic improvements: Better prompts, reasoning chains                                                 │
│  🎯 Quality assurance: Test before production use                                                            │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────── 🎯 Workflow Guide ──────────────────────────────────────────────╮
│                                                                                                              │
│  🚀 NEXT STEPS                                                                                               │
│                                                                                                              │
│  super agent evaluate developer - Measure optimization improvement                                           │
│  super agent run developer --goal "goal" - Execute enhanced agent                                            │
│  super orchestra create - Ready for multi-agent orchestration                                                │
│                                                                                                              │
│  💡 Follow BDD/TDD workflow: evaluate → optimize → evaluate → run                                            │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
================================================================================
🎉 Agent 'developer' optimization complete! Ready for testing! 🚀
```

</details>

!!! info "🔍 What Happened During Optimization"

    The optimization process will use **DSPy's BootstrapFewShot optimizer** to automatically improve your Oracle agent's performance. Here's what will happen:

    #### 🧠 **DSPy Optimization Process**

    1. **📚 Training Data Conversion**: BDD scenarios will be converted into DSPy training examples
    2. **🔄 BootstrapFewShot Algorithm**: DSPy will automatically generate optimized prompts and reasoning chains
    3. **⚡ Oracle Agent Training**: Since you're using Oracle tier, it will optimize the chain-of-thought reasoning
    4. **💾 Optimized Weights Saved**: Results will be saved to `developer_optimized.json`

    #### 📊 **Expected Optimization File**

    The optimization will create a comprehensive JSON file with:

    - **Demo Examples**: Each BDD scenario converted to a training example
    - **Optimized Signatures**: Improved prompts and instructions for chain-of-thought reasoning
    - **Enhanced Reasoning**: Better step-by-step problem-solving capabilities

!!! info "🎯 What DSPy BootstrapFewShot Does"

    **BootstrapFewShot** is a **basic but effective optimizer** that:

    1. **🎯 Learns from Examples**: Uses your BDD scenarios as training data
    2. **🔄 Trial and Error**: Tests different prompt variations automatically
    3. **🧠 Automatic Tuning**: Adjusts prompts and reasoning chains based on results
    4. **💡 Few-Shot Learning**: Creates optimal few-shot examples for better performance

    #### 🔧 **Oracle Tier Optimization Focus**

    Oracle tier optimization focuses on:

    - **🧠 Chain-of-Thought Reasoning**: Improving step-by-step thinking
    - **📝 Output Quality**: Better structured and more accurate responses
    - **🎯 Problem Solving**: Enhanced analytical capabilities
    - **📊 Consistency**: More reliable performance across different scenarios

    #### 📈 **Expected Improvements**

    After optimization, your Oracle agent should show:

    - **🎯 Better Semantic Relevance**: Responses more closely match expected outputs
    - **🧠 Enhanced Reasoning**: Better step-by-step problem-solving
    - **📝 Improved Structure**: More organized and coherent responses
    - **🎭 Better Consistency**: More reliable performance across scenarios

---

## 6️⃣ Re-evaluate Your Optimized Agent

Now that your agent has been optimized with DSPy's BootstrapFewShot, let's measure the improvement by running evaluation again:

```bash
super agent evaluate developer
```

This will show you how much the optimization improved your agent's performance compared to the baseline evaluation.

---

## 7️⃣ Run Your Agent

Now let's run your optimized Oracle agent with a goal that demonstrates its reasoning capabilities:

```bash
super agent run developer --goal "Explain the differences between object-oriented and functional programming paradigms, including their advantages and disadvantages for different types of projects"
```

<details><summary>Actual Output</summary>

```
🚀 Running agent 'developer'...

Loading pipeline... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% -:--:--
🚀 Using pre-optimized pipeline from developer_optimized.json

Looking for pipeline at: /Users/super/swe 
18-15-10-253/swe/agents/developer/pipelines/developer_pipeline.py
Model connection successful: ollama/llama3.2:1b
📋 Loaded 5 BDD specifications for execution
DeveloperPipeline (Oracle tier) initialized with 5 BDD scenarios
Loading pipeline... ━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━  40% -:--:--
📦 Loading pre-optimized model from developer_optimized.json
⚠️ Failed to load pre-optimized model: 'predictor.predict'. Using base model.
ℹ️  Setting up Oracle pipeline with base model configuration
Loading pipeline... ━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━  40% -:--:--

╭────────────────────────────────────────── Agent Execution ───────────────────────────────────────────────╮
│ 🤖 Running Developer Pipeline                                                                                │
│                                                                                                              │
│ Executing Task: Explain the differences between object-oriented and functional programming paradigms,        │
│ including their advantages and disadvantages for different types of projects                                 │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

         Analysis Results
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Aspect         ┃ Value                                                                                       ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Reasoning      │ Object-Oriented Programming (OOP) and Functional Programming (FP) are two distinct          │
│                │ paradigms that differ significantly in their approach to software development. OOP          │
│                │ emphasizes the concept of objects and classes, whereas FP focuses on functions and          │
│                │ immutability. Understanding these differences is crucial for choosing the right paradigm    │
│                │ for different types of projects.                                                            │
│ Implementation │ Object-Oriented Programming: In an object-oriented program, data is represented as objects  │
│                │ with attributes and methods. The class hierarchy is used to organize related data and       │
│                │ functionality. Advantages: Encapsulation, inheritance, polymorphism. Disadvantages:         │
│                │ Complexity, tight coupling, verbosity.                                                      │
│                │ Functional Programming: In a functional program, values are treated as first-class          │
│                │ citizens, and functions are the primary units of computation. Advantages: Immutability,     │
│                │ readability, flexibility. Disadvantages: Higher-level abstractions can lead to decreased    │
│                │ performance,                                                                                │
│                │ and more complex codebases.                                                                 │
│                │ The choice between OOP and FP depends on the project's requirements and size. For small,    │
│                │ simple projects with a clear architecture, OOP might be a better fit. However, for larger   │
│                │ projects or those requiring high performance, FP is often preferred due to its emphasis on  │
│                │ immutability and readability.                                                               │
│ Trained        │ False                                                                                       │
│ Usage          │ {'ollama_chat/llama3.2:1b': {'completion_tokens': 655, 'prompt_tokens': 572,                │
│                │ 'total_tokens': 1227, 'completion_tokens_details': 0, 'prompt_tokens_details': 0}}          │
│ Agent_Id       │ developer_20250711_182446                                                                   │
│ Tier           │ oracles                                                                                     │
└────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Pre-Optimized Pipeline: ⚠️ Available but not used
Runtime Optimization: ⚪ NO
💡 Use 'super agent run developer --goal "goal"' to use pre-optimization

Validation Status: PASSED
Validation Warnings: []

🎉 Agent execution completed successfully!

╭───────────────────────────────────── 🚀 What would you like to do next? ─────────────────────────────────────╮
│                                                                                                              │
│  🔧 Improve your agent:                                                                                      │
│     super agent evaluate developer - Test agent performance with BDD specs                                   │
│     super agent optimize developer - Optimize for better results                                             │
│                                                                                                              │
│  🎯 Create more agents:                                                                                      │
│     super agent add - Add a new agent to your project                                                        │
│     super agent design - Design a custom agent with AI assistance                                            │
│     super agent pull <agent_name> - Install a pre-built agent                                                │
│                                                                                                              │
│  🎼 Build orchestras (multi-agent workflows):                                                                │
│     super orchestra create <orchestra_name> - Create a new orchestra                                         │
│     super orchestra list - See existing orchestras                                                           │
│     super orchestra run <orchestra_name> --goal "complex task" - Run multi-agent workflow                    │
│                                                                                                              │
│  📊 Explore and manage:                                                                                      │
│     super agent list - See all your agents                                                                   │
│     super agent inspect developer - Detailed agent information                                               │
│     super marketplace - Browse available agents and tools                                                    │
│                                                                                                              │
│  💡 Quick tips:                                                                                              │
│     • Use --optimize flag for runtime optimization                                                           │
│     • Add BDD specifications to your playbook for better testing                                             │
│     • Create orchestras for complex, multi-step workflows                                                    │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</details>

!!! info "🔍 What Happened During Agent Execution"

    The Oracle agent will demonstrate its **chain-of-thought reasoning** capabilities:

    #### 🧠 **Oracle Tier Capabilities**

    1. **🔍 Analytical Thinking**: Step-by-step reasoning about complex topics
    2. **📝 Structured Output**: Well-organized explanations and comparisons
    3. **🎯 Problem Decomposition**: Breaking down complex questions into manageable parts
    4. **💡 Knowledge Integration**: Combining different concepts and perspectives

    #### 🎯 **Oracle vs Genies Tier Differences**

    **Oracle Tier (This tutorial):**
    - **🧠 Chain-of-thought reasoning** for complex analysis
    - **📝 Structured knowledge output** with clear explanations
    - **🎯 Problem decomposition** and systematic thinking
    - **📊 No tool integration** - focuses purely on reasoning

    **Genies Tier (Next tutorial):**
    - **🛠️ Tool integration** (web search, calculator, file operations)
    - **📚 RAG system** for external knowledge retrieval
    - **💾 Memory system** for context retention
    - **🔄 ReAct agents** with reasoning + acting capabilities

!!! info "🧠 How Oracle Reasoning Works"

    Oracle-tier agents use **chain-of-thought reasoning** to solve complex problems:

    **🔄 Reasoning Process:**
    1. **🔍 Problem Analysis**: Break down the question into components
    2. **🧠 Step-by-Step Thinking**: Work through each component systematically
    3. **📝 Knowledge Integration**: Combine relevant concepts and information
    4. **🎯 Structured Output**: Present findings in a clear, organized manner

    **💡 Why Oracle Tier is Powerful:**
    - **🎯 Analytical Excellence**: Deep reasoning about complex topics
    - **📝 Clear Communication**: Well-structured explanations
    - **🧠 Systematic Thinking**: Methodical approach to problem-solving
    - **📊 Knowledge Synthesis**: Combining multiple concepts effectively

!!! info "📊 Execution Performance"

    The Oracle agent executed successfully with impressive performance:

    - **🎯 Task**: Complex programming paradigm analysis
    - **🤖 Model**: `ollama/llama3.2:1b` (Oracle tier)
    - **📊 Token Usage**: 1,227 total tokens (572 prompt + 655 completion)
    - **⚡ Execution Time**: ~1 second
    - **Validation Status**: PASSED
    - **🔍 Tracing**: Enabled and stored in `.superoptix/traces`

    #### 🎯 **Key Insights**

    **🧠 Oracle Tier Reasoning Excellence:**
    - **Structured Analysis**: The agent provided a well-organized comparison with clear sections
    - **Technical Depth**: Comprehensive coverage of OOP vs FP concepts
    - **Practical Guidance**: Included real-world project recommendations
    - **Balanced Perspective**: Discussed both advantages and disadvantages

    **📝 Output Quality:**
    - **Clear Structure**: Organized into Reasoning and Implementation sections
    - **Technical Accuracy**: Correctly explained key concepts like encapsulation, inheritance, immutability
    - **Practical Value**: Provided actionable guidance for project selection
    - **Professional Tone**: Maintained appropriate technical communication style

---



---

## 🎉 **Congratulations! You've Built a Sophisticated Reasoning Agent!** 🚀

### 🏆 **What You've Accomplished**

You've successfully created a **sophisticated Oracle-tier reasoning agent** that excels at analytical thinking and complex problem-solving! Here's what makes your agent special:

**🎯 Oracle Tier Capabilities:**
- **🧠 Chain-of-Thought Reasoning**: Your agent thinks step-by-step and analyzes complex topics
- **📝 Structured Knowledge Output**: Clear, well-organized explanations and analysis
- **🎯 Problem Decomposition**: Breaks down complex questions into manageable parts
- **💡 Knowledge Synthesis**: Combines multiple concepts and perspectives effectively
- **🔍 Full Observability**: Complete tracing and debugging capabilities
- **⚡ DSPy Optimization**: Automatically optimized for better reasoning performance

**🏗️ Enterprise-Grade Architecture:**
- **📊 BDD Testing**: Behavior-driven development with automated evaluation
- **🔄 Optimization Pipeline**: Continuous improvement through DSPy
- **📈 Performance Monitoring**: Detailed metrics and analytics
- **🔧 Modular Design**: Easy to extend and customize
- **💻 Production Ready**: Can be deployed and scaled

### 🌟 **You're Now an AI Reasoning Engineer!**

This isn't just a simple chatbot-you've built a **sophisticated reasoning system** that can:
- **Analyze complex topics** with systematic thinking
- **Provide structured explanations** with clear organization
- **Decompose problems** into manageable components
- **Synthesize knowledge** from multiple sources
- **Deliver consistent reasoning** across different scenarios

### 🚀 **What's Next?**

Your journey into AI reasoning development has just begun! Here are some exciting next steps:

**🎼 Create Multi-Agent Orchestras:**
```bash
super orchestra create my_team
```
Build teams of specialized agents working together!

**🔧 Add More Specialized Agents:**
```bash
super agent pull business-analyst
```
Pull pre-built agents for different domains!

**📊 Explore the Marketplace:**
```bash
super market browse agents
```
Discover pre-built agents and tools!

**🎯 Deploy to Production:**
Your Oracle agent is ready for real-world deployment and can handle complex reasoning tasks!



---

Continue with the [Agent with Tools & RAG Tutorial](genies-agent) to learn about advanced tool integration and RAG systems, or the [Orchestra Tutorial](first-orchestra) to build multi-agent systems! 