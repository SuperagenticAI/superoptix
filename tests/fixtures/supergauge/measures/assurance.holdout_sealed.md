---
id: assurance.holdout_sealed
version: "0.1"
type: deterministic
group: assurance
parameters: []
author: Superagentic AI
---

# `assurance.holdout_sealed`

Whether the held-out split remained closed to everything that tunes the agent,
and whether the contamination probes stayed silent.

## Why it exists

A held-out split that something has read is a held-in split with a misleading
name, and every number computed on it is optimistic by an unknown margin. The
leak is rarely deliberate. A prompt author reads a failing case to understand
it. An optimizer is pointed at the whole directory. Someone copies an
interesting task into a system prompt as an example.

## Computation

Boolean. All conditions must hold:

| Condition | Established by |
|---|---|
| The manifest digest matches the sealed value | Recomputing the digest |
| No tuning process read the split | Access control on the manifest path |
| Every contamination probe returned its expected failure | Probe results |

```
assurance.holdout_sealed = true when all conditions hold
```

### Contamination probes

A probe is a task whose success condition is unreachable by legitimate means:
an answer depending on a fact absent from every permitted source, or a fixture
whose target state cannot be produced by the declared tools. An agent passing a
probe has seen something it should not have.

At least two probes SHOULD be present. One probe distinguishes leakage from
luck poorly.

### Failure cases

| Case | Required behaviour |
|---|---|
| The digest changed | Report false; the split is a different split |
| Access cannot be established | Report false; `task_set.sealed` MUST be false too |
| A probe passed | Report false, and quarantine the split |

## Evidence required

The sealed manifest digest, the recomputed digest, probe ids and their results.

## Record entry

```yaml
- id: assurance.holdout_sealed
  value: true
```

## Backing a gate

Permitted, and effectively mandatory at L2, where the specification already
forbids a ship verdict over an unsealed split.

## Related

`assurance.evaluator_independence` covers the adjacent failure, where the split
was clean and the evidence was not.
