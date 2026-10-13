---
id: reliability.pass_at_k
version: "0.1"
type: deterministic
group: robustness
parameters: [k]
author: Superagentic AI
---

# `reliability.pass_at_k`

The proportion of tasks an agent solves on **at least one** of k independent
attempts.

## Why it exists

This is the capability ceiling: what the agent can do when it gets more than one
try. It is the right question when deciding whether an agent is worth pursuing
at all, and the wrong one when deciding whether to put it in front of a
customer, who gets one attempt.

Report it beside `reliability.pass_hat_k`. The distance between the two is the
consistency problem stated as a number, and that gap is usually the most useful
line in a first report.

## Computation

For each task `t`, run the agent `k` times under identical starting conditions
with independent sampling. Let `a(t)` be true when any attempt satisfies the
task's success condition.

```
pass@k = |{ t : a(t) }| / |T|
```

Report `k` and `n`. A value without `k` MUST be rejected by a validator.

The same independence requirements as `reliability.pass_hat_k` apply: no shared
conversation, cache or memory between attempts, and the working state reset so
attempt `i+1` never begins from state attempt `i` produced.

### Failure cases

| Case | Required behaviour |
|---|---|
| Fewer than `k` attempts for any task | Do not report |
| `k = 1` | Do not report; at `k = 1` this is `task.completion` |
| Attempts share state | Do not report; the value would be meaningless |

## Evidence required

`k` completed runs per task, each with its own run id, and a recorded reset
between attempts.

## Record entry

```yaml
- id: reliability.pass_at_k
  value: 0.94
  k: 5
  n: 12
```

## Backing a gate

Permitted but rarely advisable. Gating the ceiling rewards an agent that
occasionally succeeds. Gate the floor instead.

## Related

`reliability.pass_hat_k` is the measure this one should always accompany.
