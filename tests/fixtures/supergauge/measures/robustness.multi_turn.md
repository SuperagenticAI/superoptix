---
id: robustness.multi_turn
version: "0.1"
type: judged
group: robustness
parameters: []
author: Superagentic AI
---

# `robustness.multi_turn`

Whether output quality holds across an extended session, or decays as context
accumulates.

## Why it exists

Most evaluation is short. Most production sessions are not. Degradation that
appears at turn thirty is invisible in a suite whose cases end at turn three,
and it is a common shape of complaint: fine at first, drifting later, eventually
contradicting itself or losing an instruction given early on.

## Type

**Judged.** Deciding whether a later answer is worse than an earlier one on the
same thread requires reading both in context. This measure MUST NOT back a gate.

Where degradation has a deterministic signature in your domain — an instruction
from turn one measurably violated at turn thirty, a required disclosure dropped
— prefer a local `x-` measure that checks it. A deterministic check on a
specific regression beats a judged score on a general one.

## Computation

Run a scripted multi-turn session. The judge scores each turn on the same
rubric, and the measure reports quality retention:

```
robustness.multi_turn = mean(score of last quartile of turns)
                      / mean(score of first quartile of turns)
```

Values at or above 1.0 are clamped to 1.0; this measures decay, and improvement
over a session is a different question.

Sessions MUST be at least twelve turns. Below that the quartiles are too small
for the ratio to mean anything.

### Judge requirements

At L3 the judge record MUST pin `id` and `model`, and carry
`human_agreement_kappa`. The rubric MUST be identical across turns, since a
rubric that drifts measures the rubric.

## Evidence required

The full session, per-turn scores, the rubric, and the pinned judge version.

## Record entry

```yaml
- id: robustness.multi_turn
  value: 0.82
  n: 6
```

## Backing a gate

Never. See §4.1 of the specification.

## Related

`assurance.judge_agreement` is what makes this value interpretable.
