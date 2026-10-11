---
id: assurance.evidence_complete
version: "0.1"
type: deterministic
group: assurance
parameters: []
author: Superagentic AI
---

# `assurance.evidence_complete`

Whether the referenced ledger is present, well formed, and reproduces the
verdict the record carries.

## Why it exists

A record is an assertion. An immutable record is an unchanging assertion, which
is a different thing from a true one. What converts one into the other is a
third party recomputing the result from the underlying events and arriving at
the same place.

This measure is the difference between an audit trail and an audit.

## Computation

Boolean. All conditions must hold:

| Condition | Meaning |
|---|---|
| Present | The ledger resolves at the referenced location |
| Well formed | It parses under the declared `assurance.evidence.format` |
| Complete | Every run referenced by a measure appears, with a terminal event |
| Reproducing | Recomputing each deterministic measure from the ledger yields the recorded value |

```
assurance.evidence_complete = true when all conditions hold
```

Judged measures are excluded from the reproduction check, since re-running a
judge does not reproduce a prior verdict. Their presence in the ledger is
checked; their values are taken as recorded.

### Tolerance

Recomputed values MUST match exactly for boolean and counting measures. For
measures reported as ratios, a difference within one part in the sample size is
acceptable and MUST be recorded.

### Failure cases

| Case | Required behaviour |
|---|---|
| The ledger was pruned by retention policy | Report false, and note the retention window |
| A run is missing its terminal event | Report false; the run is unfinished or truncated |
| A recomputed value differs beyond tolerance | Report false, and name the measure |

## Evidence required

The ledger, the declared format, and the recomputation output.

## Record entry

```yaml
- id: assurance.evidence_complete
  value: true
```

## Backing a gate

Permitted. Required in substance at L4, where an independent party performs the
reproduction in place of the emitter.

## Related

`assurance.evaluator_independence` covers who was allowed to see what;
this measure covers whether any of it survived.
