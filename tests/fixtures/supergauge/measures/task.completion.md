---
id: task.completion
version: "0.1"
type: deterministic
group: effectiveness
parameters: [split]
author: Superagentic AI
---

# `task.completion`

The proportion of tasks whose declared end state was reached.

## Why it exists

An agent describes its own work, and the description is the cheapest part of the
run to get right. Grading the description rewards fluency. Grading the world
rewards completion.

The failure this catches is specific and common: a confident summary written
over a database that never changed, a branch that was never pushed, a ticket
that stayed open. Every other measure in the effectiveness group is diagnostic
once this one has failed.

## Computation

Each task declares an assertion over observable state after the run finishes.
Let `c(t)` be true when the assertion holds.

```
task.completion = |{ t : c(t) }| / |T|
```

The assertion MUST be evaluated against the system, not the transcript.
Acceptable subjects include a database row, a file in the working tree, a git
ref, an HTTP resource, or the exit status of a command the task names.

A task MAY declare partial credit as a set of independently checkable
assertions, in which case `c(t)` is their mean and the task contributes a
fraction. Partial credit MUST be declared by the task, never inferred by the
grader.

### Failure cases

| Case | Required behaviour |
|---|---|
| The assertion cannot be evaluated (environment gone) | Exclude the task, reduce `n`, note the exclusion |
| The agent reached the state before the run began | Task is invalid; exclude and repair the fixture |
| The agent reached the state by a forbidden route | Count as a failure; record the gate that fired |

## Evidence required

- The declared assertion for each task, and its result.
- A pre-run state capture, so "already satisfied" is distinguishable from
  "brought about".

## Record entry

```yaml
- id: task.completion
  value: 0.83
  split: held-out
  n: 12
```

## Backing a gate

Permitted. The floor comes from the profile, never from this document.

## Related

`trajectory.valid` explains a low value; `reliability.pass_hat_k` composes over
this measure's success condition.
