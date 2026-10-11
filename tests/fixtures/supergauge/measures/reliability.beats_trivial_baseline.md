---
id: reliability.beats_trivial_baseline
version: "0.1"
type: deterministic
group: robustness
parameters: [baseline]
author: Superagentic AI
---

# `reliability.beats_trivial_baseline`

Whether the candidate beat a declared trivial baseline on the same split, under
the same success condition, by at least a declared margin.

## Why it exists

A success rate means little without a floor to compare it with. On many task
sets a constant answer, the majority label, an echo of the input or an empty
patch already scores well, and an optimizer can converge on something no better
than that while every absolute number looks healthy.

Comparing against the cheapest thing that could possibly work catches that
case mechanically, before anyone reads a dashboard.

## Computation

Boolean. The emitter declares a trivial baseline (for example `majority-label`,
`constant-empty`, `echo-input`, `no-op-patch`) and runs it over the same split
and the same success condition used for the candidate's headline measure.

Let `c` be the candidate's value and `b` the baseline's value on the compared
measure, and `m` the declared margin (default `0`).

```
reliability.beats_trivial_baseline = c > b + m
```

The comparison is strict: a tie does not beat the baseline.

The record entry MUST carry a `baseline` object naming the baseline and its
value, so a reader can reproduce the comparison without the emitter.

| `baseline` field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable id of the trivial baseline, for example `majority-label` |
| `value` | yes | The baseline's value on the compared measure |
| `measure` | recommended | Registry id of the compared measure, for example `task.completion` |
| `candidate_value` | recommended | The candidate's value on that measure |
| `margin` | optional | Required lead over the baseline, default `0` |

### Failure cases

| Case | Required behaviour |
|---|---|
| Baseline run on a different split or success condition | Do not report the measure |
| Baseline not declared before the candidate run | Do not report the measure |
| Baseline is itself trained or tuned on the evaluated split | Not trivial; do not report the measure |
| Candidate value equals baseline plus margin | Report false |

## Evidence required

- Baseline runs in the referenced ledger, with their own run ids.
- The baseline definition (a short description or its digest).
- The task-set manifest digest, so both runs are identifiably on one split.

## Record entry

```yaml
- id: reliability.beats_trivial_baseline
  value: true
  split: held-out
  n: 50
  baseline:
    id: majority-label
    value: 0.42
    measure: task.completion
    candidate_value: 0.84
    margin: 0.1
```

## Backing a gate

Permitted. Gate with `result: pass` when the value is true; the boolean carries
no floor.

## Related

`task.completion` and `reliability.pass_hat_k` are the usual compared measures.
This measure adds no score of its own; it records a comparison.
