---
id: answer.grounded
version: "0.1"
type: judged
group: effectiveness
parameters: []
author: Superagentic AI
---

# `answer.grounded`

The proportion of claims in an agent's output that are supported by the context
it retrieved or the results its tools returned.

## Why it exists

An agent with retrieval can produce an answer that is fluent, plausible and
unsupported by anything it read. Completion does not catch it, because a
well-formed answer was produced. Trajectory does not catch it, because the
retrieval happened.

## Type

**Judged.** Deciding whether a sentence is supported by a passage requires
reading both, and no deterministic procedure does that across open domains.
This measure MUST NOT back a gate.

Where a domain admits a deterministic check — a citation resolving to a live
document id, a figure matching a returned field exactly — prefer a local `x-`
measure that performs it. A deterministic check on a narrow claim is worth more
than a judged score on a broad one.

## Computation

Segment the output into checkable claims. For each, the judge returns supported,
unsupported, or not-a-claim.

```
answer.grounded = supported / (supported + unsupported)
```

Segmentation MUST be recorded, because it moves the result: an implementation
that segments per sentence and one that segments per paragraph will disagree on
the same output.

### Judge requirements

At conformance L3 the judge record MUST pin `id` and `model`, and carry
`human_agreement_kappa` from a sampled human pass. A judge whose agreement with
human review is not measured produces a number of unknown meaning.

## Evidence required

The retrieved context and tool results available at generation time, the
segmentation, and the per-claim verdicts.

## Record entry

```yaml
- id: answer.grounded
  value: 0.88
  n: 240
```

## Backing a gate

Never. See §4.1 of the specification.

## Related

`assurance.judge_agreement` is what makes this value interpretable.
