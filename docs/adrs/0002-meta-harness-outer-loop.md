# ADR 0002: Meta-Harness Outer Loop for SuperOptiX

## Status

Proposed on April 1, 2026.

## Context

SuperOptiX already supports several optimization layers:

1. `UniversalGEPA` optimizes a single `BaseComponent.variable` such as instructions or a system prompt.
2. DSPy optimizers such as GEPA, SIMBA, BootstrapFewShot, BetterTogether, and MIPROv2 optimize prompting or demo selection inside existing program structures.
3. Domain-specific adapters already expose optimization surfaces beyond plain prompts:
   - DeepAgents system prompts and backends
   - MCP tool descriptions and system prompts
   - RAG retrieval and answer-generation prompts
   - Evaluation harnesses, BDD scenarios, and benchmark runners

The Meta-Harness paper introduces a different search target. It does not optimize only prompt text. It searches over the executable harness itself: retrieval policies, memory updates, prompt-construction logic, orchestration, and environment bootstrapping. The outer loop logs every candidate's code, scores, and execution traces to a filesystem, then lets a coding-agent proposer inspect that history to generate the next candidates.

This maps well to SuperOptiX's direction because SuperOptiX already has:

- compiled pipelines and framework wrappers
- reusable evaluation entry points
- observability and trace capture
- multiple harness-like configuration surfaces across frameworks

But it is not a drop-in extension of `UniversalGEPA`, because the current GEPA path assumes a mostly fixed program with one mutable variable.

## Decision

1. SuperOptiX should treat Meta-Harness as a new outer-loop optimizer, not as a replacement for GEPA.

2. The first implementation should search over harness configuration and small generated code artifacts, while reusing the current evaluation stack.

3. GEPA should remain an inner-loop optimizer when the candidate harness still contains a short-feedback textual variable worth refining.

4. For tool-heavy or multi-step agents where GEPA is a poor fit, the default inner-loop choices should be:
   - no inner optimizer
   - `SIMBA`
   - `MIPROv2`
   - `BootstrapFewShot` or `BetterTogether`

5. The new Meta-Harness layer should optimize for Pareto objectives rather than a single scalar whenever the task naturally includes both quality and cost constraints.

## Rationale

### Why Meta-Harness Fits

- The paper's optimization target matches SuperOptiX's real bottlenecks better than prompt-only optimization in several areas:
  - DeepAgents backend selection and environment bootstrapping
  - RAG routing, retrieval modes, and context construction
  - MCP tool descriptions, tool selection policy, and fallback logic
  - long-horizon orchestration and memory update rules

- SuperOptiX already contains harness-like code that is visible and executable:
  - pipeline templates
  - runtime helpers
  - benchmark/evaluation harnesses
  - adapter-specific optimization modules

- Meta-Harness is especially attractive where behavior depends on several coupled design choices and where execution traces matter more than per-example text feedback.

### Why Meta-Harness Should Not Replace GEPA

- The Meta-Harness paper explicitly distinguishes its setting from GEPA:
  - GEPA is strong when a candidate can be judged through short per-candidate reflective feedback.
  - Meta-Harness is aimed at stateful programs whose failures are only understandable by comparing code and traces across many candidates.

- In SuperOptiX, `UniversalGEPA` still works well for:
  - single prompt or instruction fields
  - tool descriptions
  - short RAG prompt components
  - framework wrappers that flatten outputs into simple evaluation signals

- Replacing GEPA outright would discard a useful, cheaper inner loop.

## Proposed Architecture

### 1. New Package

Add a new package such as:

- `superoptix/meta_harness/`
  - `artifact_store.py`
  - `candidate.py`
  - `objectives.py`
  - `validator.py`
  - `evaluator.py`
  - `search_loop.py`
  - `skill_builder.py`

### 2. Candidate Model

Represent each candidate as one of:

- a config patch over a compiled agent spec
- a generated Python harness file
- a hybrid candidate containing both config deltas and code deltas

Start with config-first candidates. Only allow broader code edits after the workflow is stable.

### 3. Artifact Store

For every candidate, persist:

- source code or config patch
- validation results
- metric summary
- latency and token-cost summary
- execution traces
- diff against parent or baseline

Use a queryable directory layout under a path such as:

- `.superoptix/meta_harness/<agent>/<run_id>/<candidate_id>/`

The proposer should inspect this filesystem rather than receiving compressed summaries only.

### 4. Validation Before Full Eval

Every candidate should pass a cheap validation gate before expensive evaluation:

- import/compile check
- pipeline instantiation
- one or two smoke-test examples
- schema and interface checks

This follows a core Meta-Harness recommendation and is especially important for generated DeepAgents, RAG, and MCP candidates.

### 5. Evaluation Reuse

Reuse existing SuperOptiX evaluation pathways instead of inventing a new scoring stack:

- BDD scenarios for standard agents
- benchmark runners for special domains
- existing RAG and MCP metrics where available

Wrap these as a common candidate evaluator that writes machine-readable outputs for the proposer.

### 6. Pareto Frontier

Track at least:

- quality metric
- latency
- input context or token cost
- optional safety or validity score

Do not force a single scalar objective unless the domain truly has one.

## Recommended Integration Order

### Phase 1: Config-Space Meta-Harness

Target only high-value, low-risk knobs already exposed in SuperOptiX:

- DeepAgents:
  - system prompt
  - backend type
  - backend routing
  - environment bootstrap on or off
  - RLM mode
- RAG:
  - retrieval mode
  - `top_k`
  - routing predicates
  - reranking weights
  - prompt templates
- MCP:
  - tool descriptions
  - base system prompt
  - two-pass vs one-pass flow
  - fallback behavior

This phase gives most of the Meta-Harness value without unrestricted code mutation.

### Phase 2: Code-Space Harness Search

Allow the proposer to synthesize small harness modules or edit generated pipeline helpers with:

- strict writable directories
- deterministic validation
- artifact logging
- diff and frontier tooling

This is the phase that most closely matches the paper.

### Phase 3: Hybrid Inner/Outer Optimization

For each outer-loop candidate:

1. instantiate candidate harness
2. optionally run inner-loop GEPA or another optimizer on eligible textual subcomponents
3. run full evaluation
4. log both outer and inner artifacts

This gives SuperOptiX a layered optimizer:

- outer loop: harness search
- inner loop: prompt/tool-description refinement

## When to Use GEPA vs Alternatives Inside Meta-Harness

Use `GEPA` inside a candidate when:

- the mutable target is primarily text
- traces are short
- the evaluation loop is relatively cheap
- the component already conforms to `BaseComponent`

Prefer `SIMBA`, `MIPROv2`, `BootstrapFewShot`, or `BetterTogether` when:

- the agent is tool-heavy
- the output format is complex or multi-step
- the task is closer to demonstration selection than prompt reflection

Use no inner optimizer when:

- the outer-loop harness change is the main intervention
- evaluation is already expensive
- the harness logic, not prompt wording, is the bottleneck

## Consequences

### Positive

- SuperOptiX can optimize the real harness surfaces that dominate multi-step agent quality.
- Existing GEPA investments remain useful as inner-loop optimizers.
- The same mechanism can cover DeepAgents, RAG, MCP, and future orchestration frameworks.
- The artifact-store pattern aligns well with coding-agent workflows.

### Negative

- Search cost will be much higher than prompt-only optimization.
- Good artifact logging and validation become mandatory, not optional.
- Safety boundaries around writable files and shell commands must be tighter than current optimizer flows.
- Results will depend heavily on proposer quality and the skill text used to steer it.

## Immediate Recommendation

Implement Meta-Harness in SuperOptiX, but do it as a phased outer-loop system and do not position it as "GEPA but better."

The correct framing is:

- Meta-Harness for searching harness structure
- GEPA and other existing optimizers for refining subcomponents inside a chosen harness

That combination is more faithful to the paper and a better fit for SuperOptiX's current architecture than trying to stretch `UniversalGEPA` into a full harness-search engine.
