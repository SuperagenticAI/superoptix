---
title: Quick Start - SuperOptiX
---

# 🚀 Quick Start Guide

<div align="center">

**Three hands-on paths through the SuperOptiX workflow**

</div>

!!! abstract "Choose Your Path"

    **Part 1 - Adapt an agent to A2A:** Take an agent you already have and give it an A2A endpoint. Five minutes, no model required.

    **Part 2 - Sentiment Analyzer Demo:** A lightweight project that walks through evaluation and GEPA optimization.

    **Part 3 - SWE Orchestration:** A multi-agent software engineering workflow that shows the orchestration features.

!!! tip "Getting Started"
    Each part stands on its own. Part 1 is the fastest way to see what SuperOptiX does.

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

=== "One line (recommended)"

    Installs `uv` when it is missing, then SuperOptiX into an isolated tool
    environment. It never uses sudo.

    ```bash
    curl -fsSL https://superoptix.ai/install.sh | sh
    super --version
    ```

=== "uv"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv tool install superoptix
    super --version
    ```

=== "Into an existing project"

    ```bash
    uv add superoptix
    super --version
    ```

---

## 🔌 Part 1 - Adapt an Agent to A2A

!!! info "Overview"
    `super a2a adapt` reads an agent you already wrote, derives the skills a calling agent would
    route on, and writes an Agent Card plus a conformant A2A server. Your agent is not modified.

### Write an agent

Any agent on a supported runtime works. This example uses DSPy because it needs no extra setup.

```python title="sentiment.py"
import dspy


class ClassifySentiment(dspy.Signature):
    """Classify the sentiment of a customer review as positive, negative or neutral."""

    review: str = dspy.InputField(desc="the customer review text")
    sentiment: str = dspy.OutputField(desc="positive, negative or neutral")


program = dspy.Predict(ClassifySentiment)
```

### Adapt it

```bash
super a2a adapt --entrypoint sentiment:program --framework dspy
```

Three files are written to `./a2a`:

| File | Contents |
|---|---|
| `agent-card.json` | The Agent Card other agents read to decide whether to call yours |
| `a2a_server.py` | A FastAPI application serving A2A 1.0 and 0.3 |
| `agentspec.json` | The intermediate representation the card was derived from |

The card carries the skill the introspector found:

```json
{
  "id": "program",
  "name": "ClassifySentiment",
  "description": "Classify the sentiment of a customer review as positive, negative or neutral. Takes review (the customer review text); returns sentiment (positive, negative or neutral).",
  "tags": ["dspy", "signature", "review"]
}
```

### Serve it

```bash
uvicorn a2a.a2a_server:app --port 8000
```

### Call it

```bash
curl localhost:8000/.well-known/agent-card.json

curl -X POST localhost:8000/message:send \
  -H 'content-type: application/json' \
  -d '{"message":{"role":"ROLE_USER","parts":[{"text":"This product exceeded my expectations"}]}}'
```

!!! tip "A live example"
    A SuperOptiX agent runs at [a2a.superoptix.ai](https://a2a.superoptix.ai), with its Agent Card
    published at [superoptix.ai/.well-known/agent-card.json](https://superoptix.ai/.well-known/agent-card.json).
    Call it to see the shape of a response before you deploy your own.

Further reading: [Adapt an existing agent](guides/a2a-adapt.md), [Conformance](guides/a2a-conformance.md),
[Routing quality](guides/a2a-routing.md).

---

## 🎨 Part 2 - Sentiment Analyzer Demo (Evaluation & Optimization)

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
    - DSPy configured the local Ollama model `qwen3.5:9b` (temperature 0.3, max 512 tokens).
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

## 🏗️ Part 3 - SWE Multi-Agent Orchestration

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

    **Part 1:** Gave an existing agent an A2A endpoint without changing its code.

    **Part 2:** Demonstrated evaluation-first development using a sentiment analyzer, including GEPA optimization.

    **Part 3:** Showed the full SWE orchestration flow with multiple agents collaborating on an SDLC task.

!!! note "Next Steps"
    From here you can explore the marketplace (`super market`), design custom agents (`super agent design`), or build orchestras tailored to your workflows. Happy building! 🎉
