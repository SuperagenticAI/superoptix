---
title: Quick Start - SuperOptiX
---

# 🚀 Quick Start Guide: Two Paths to SuperOptiX Mastery

<div align="center">

**Two hands-on experiences that highlight the SuperOptiX workflow**

</div>

!!! abstract "Choose Your Path"

    **Part 1 – Sentiment Analyzer Demo:** A lightweight project that walks through evaluation and GEPA optimization in minutes.

    **Part 2 – SWE Orchestration:** A full multi-agent software engineering workflow that showcases the orchestration features.

!!! tip "Getting Started"
    You can complete Part 1 on its own, then move on to Part 2 when you're ready to build larger teams.

---

## 📋 Requirements

### 🖥️ Hardware

| Component | Requirement |
|-----------|-------------|
| **GPU RAM** | 16 GB recommended if you plan to run GEPA optimization |
| **System RAM** | 8 GB+ for smooth execution |

### 🐍 Software

| Software | Version/Details |
|----------|-----------------|
| **Python** | 3.11 or higher |
| **SuperOptiX** | Install via uv (recommended) or pip |
| **Ollama** | For local LLMs (alternatives like MLX or Hugging Face also work) |

**Install Ollama** (if needed):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 🔧 Install SuperOptiX

We recommend using `uv` for fast, reliable installation.

=== "uv (Recommended)"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install superoptix
    super --version
    ```

=== "pip"

    ```bash
    pip install superoptix
    super --version
    ```

---

## 🎨 Part 1 — Sentiment Analyzer Demo (Evaluation & Optimization)

!!! info "Overview"
    This mini-project validates that your environment is ready. You'll initialize a project, pull a sample dataset, run the agent, evaluate it, and apply GEPA optimization.

### Step 1. Initialize the Project

```bash
super init sentiment_analyzer
cd sentiment_analyzer
```

### Step 2. Pull the Dataset

```bash
super dataset pull sentiment_reviews
```

!!! success "Dataset Location"
    This stores `sentiment_reviews.csv` in your project's `data/` directory.

### Step 3. Pull & Compile the Agent

```bash
super agent pull sentiment_analyzer
super agent compile sentiment_analyzer
```

---

### Step 4. Run the Agent

```bash
super agent run sentiment_analyzer \
    --goal "Classify the sentiment of the review: 'I love this product but the shipping was slow.'"
```

!!! example "Output"
    The agent responds with a sentiment label and a confidence score.

??? info "What Happened"
    - The pipeline (`agents/sentiment_analyzer/pipelines/sentiment_analyzer_pipeline.py`) executed end-to-end with your goal.
    - DSPy configured the local Ollama model `llama3.1:8b` (temperature 0.3, max 512 tokens).
    - The ReAct chain generated both the structured fields (`sentiment`, `confidence`) and the reasoning trace.
    - Output is shown in the terminal and the pipeline remains inspectable under `agents/sentiment_analyzer/pipelines/`.

---

### Step 5. Evaluate the Agent

```bash
super agent evaluate sentiment_analyzer
```

!!! info "What This Does"
    Runs the playbook scenarios plus the dataset samples.

??? info "What Happened"
    - Evaluation pulled every BDD scenario defined in `agents/sentiment_analyzer/playbook/sentiment_analyzer_playbook.yaml`.
    - Each scenario is scored with the `answer_exact_match` metric (threshold 0.7).
    - Examples from `data/sentiment_reviews.csv` were converted into DSPy `Example`s and included in the run.
    - A rich pass/fail summary (capability score, recommendations) was printed to the terminal.

---

### Step 6. Optimize with GEPA & Re-evaluate

```bash
super agent optimize sentiment_analyzer --auto light
super agent evaluate sentiment_analyzer
```

!!! tip "GEPA Optimization"
    GEPA tunes prompts based on failed scenarios; the follow-up evaluation measures any change.

??? info "What Happened"
    - GEPA iteratively mutated the sentiment pipeline and scored each candidate against the same evaluation set.
    - Optimized weights were saved to `agents/sentiment_analyzer/pipelines/sentiment_analyzer_optimized.json`.
    - The second `evaluate` command automatically loaded those weights before re-running the scenarios.

!!! success "Part 1 Complete!"
    You've now completed the full evaluation-first loop! Continue exploring or move on to the multi-agent SWE workflow below.

---

## 🏗️ Part 2 — SWE Multi-Agent Orchestration

!!! info "Overview"
    In this section you'll build an end-to-end software development workflow with multiple cooperating agents.

### Step 1. Initialize the SWE Project

```bash
cd ..          # if you're still inside sentiment_analyzer
super init swe
cd swe
```

---

### Step 2. Pull & Compile the Developer Agent

```bash
super agent pull developer
super agent compile developer
```

!!! note "Compilation Output"
    Compilation generates an explicit DSPy pipeline at `agents/developer/pipelines/developer_pipeline.py`. This is your starting point for customization.

---

### Step 3. Run the Developer Agent

```bash
super agent run developer \
    --goal "Create a Python function that validates email addresses using regex"
```

!!! example "What to Expect"
    Watch the agent reason about the task and emit code along with explanations. The output file is stored in `pipelines/` and the CLI displays the result inline.

---

### Step 4. Add QA & DevOps Agents

```bash
super agent pull qa_engineer
super agent pull devops_engineer
super agent compile qa_engineer
super agent compile devops_engineer
```

---

### Step 5. Create & Run the Orchestra

```bash
super orchestra create sdlc
super orchestra list
super orchestra run sdlc --goal "Build a task management web app with auth, CRUD, tests, and deployment config"
```

!!! info "Orchestra Workflow"
    This generates `orchestras/sdlc_orchestra.yaml` and a compiled entry-point under `pipelines/orchestras/`. The sample goal walks through a three-phase SDLC:

    1. **Developer**: analyzes the goal, outlines the plan, and produces implementation artifacts.
    2. **DevOps Engineer**: translates the plan into CI/CD configuration and deployment notes.
    3. **QA Engineer**: derives comprehensive manual + automated test coverage from the preceding outputs.

!!! example "Output Files"
    Orchestra results are saved to the project root (e.g., `implement_feature_implementation.txt`, `configure_ci_pipeline_result.json`, `create_test_plan_test_plan.txt`).

---

### Step 6. Observe and Monitor

```bash
super observe traces developer
super observe dashboard
```

!!! info "Observability Tools"
    - **Traces**: Step through each agent's reasoning, model calls, and artifacts
    - **Dashboard**: Higher-level view for debugging orchestration runs or comparing pre/post optimization behavior

---

## Summary

!!! success "What You've Accomplished"

    **Part 1:** Demonstrated evaluation-first development using a sentiment analyzer, including GEPA optimization.

    **Part 2:** Showed the full SWE orchestration flow with multiple agents collaborating on an SDLC task.

!!! note "Next Steps"
    From here you can explore the marketplace (`super market`), design custom agents (`super agent design`), or build orchestras tailored to your workflows. Happy building! 🎉