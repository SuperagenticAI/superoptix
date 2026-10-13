---
id: trajectory.valid
version: "0.1"
type: deterministic
group: effectiveness
parameters: []
author: Superagentic AI
---

# `trajectory.valid`

The proportion of runs whose execution path satisfied the structural
constraints the task declared.

## Why it exists

Two runs can both complete and differ by an order of magnitude in cost, risk and
reviewability. One reads three files and edits one. The other reads ninety,
edits the same one, and revisits the same file eleven times.

Completion cannot see that difference. The path is where wandering, looping and
skipped verification become visible, and it becomes visible before the invoice
does.

## Computation

A run is valid when all declared constraints hold:

| Constraint | Meaning |
|---|---|
| `required_steps` | Every named step appears at least once in the ledger |
| `forbidden_steps` | No named step appears |
| `max_steps` | Total tool invocations stay within budget |
| `no_cycles` | No identical (tool, arguments) triple repeats more than `cycle_threshold` times, default 2 |

```
trajectory.valid = |{ t : all constraints hold }| / |T|
```

A run that fails any constraint is invalid; the measure reports no partial
credit, because a partially valid path is a failing path with extra steps.

### Cycle detection

Compare on tool name plus normalised arguments. Normalisation MUST remove
timestamps, request ids and other values that differ between otherwise identical
calls, and the normalisation rule MUST be recorded, since two implementations
that normalise differently will disagree.

## Evidence required

A ledger with ordered tool invocations carrying tool name, arguments and
outcome. `assurance.evidence.format` must be a format that preserves ordering.

## Record entry

```yaml
- id: trajectory.valid
  value: 0.91
  n: 46
```

## Backing a gate

Permitted, and most useful at a low floor. Gating this near 1.0 tends to encode
one team's preferred path and penalise a shorter one.

## Related

`tool.correctness` grades the calls themselves; `efficiency.tokens_per_success`
prices the wandering this measure detects.
