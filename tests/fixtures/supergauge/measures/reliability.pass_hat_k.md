---
id: reliability.pass_hat_k
version: "0.1"
type: deterministic
group: robustness
parameters: [k]
author: Superagentic AI
---

# `reliability.pass_hat_k`

The proportion of tasks an agent solves on **every one of k independent
attempts**.

## Why it exists

`pass@k` — at least one of k attempts succeeds — describes a capability
ceiling. It is the right measure when asking what an agent is able to do at
all, and the wrong one when asking whether it can be relied upon, because it
rewards a system that succeeds occasionally and hides one that succeeds
inconsistently.

An agent with a 70% per-attempt success rate reads as roughly 97% on `pass@3`
and roughly 34% on `pass^3`. The same agent. Only the second number tells you
what a user experiences.

Release decisions are consistency decisions, so a reliability gate uses
`pass^k`.

## Computation

For each task `t` in the evaluated split, run the agent `k` times under
identical starting conditions with independent sampling. Let `s(t)` be true when
all `k` attempts satisfy the task's success condition.

```
pass^k = |{ t : s(t) }| / |T|
```

Report `k` and `n` (`|T|`) alongside the value. A value without `k` is
meaningless and MUST be rejected by a validator.

### Success condition

`pass^k` composes over whatever success condition the task declares — most
usefully `task.completion`, which asserts against the end state of the world
in place of the agent's description of it. It defines no success condition of
its own.

### Independence

The `k` attempts MUST be independent:

- No shared conversation, cache or memory carried between attempts.
- The working state reset between attempts, so attempt `i+1` never starts from
  a repository or database that attempt `i` modified.
- Same model, same harness digest, same authority grant across all attempts.

An implementation that cannot reset working state between attempts MUST NOT
report this measure.

### Failure cases

| Case | Required behaviour |
|---|---|
| Fewer than `k` attempts completed for any task | Do not report the measure |
| A task errored for infrastructure reasons | Exclude the task; reduce `n`; note the exclusion in the ledger |
| `k = 1` | Do not report. At `k = 1` this measure is `task.completion` under another name |

## Evidence required

- `k` completed runs per task, each present in the referenced ledger with its
  own run id.
- A recorded reset between attempts.
- The task-set manifest digest, so the evaluated split is identifiable.

## Record entry

```yaml
- id: reliability.pass_hat_k
  value: 0.66
  k: 5
  n: 12
  split: held-out
```

## Backing a gate

Permitted — this measure is deterministic.

```yaml
- {id: reliability.pass_hat_k, floor: 0.60, result: pass}
```

The floor comes from the profile, never from this document. See SPEC §4.3.

## Cost note

This measure multiplies evaluation cost by `k`. In practice `k` between 3 and 8
is where the signal appears; below 3 the estimate is too noisy to gate on, and
above 8 the cost rarely buys a different decision. Profiles at tier `T0` should
not require it.

## Related

- `reliability.pass_at_k` — the capability ceiling, reported alongside
- `task.completion` — the usual success condition this composes over
