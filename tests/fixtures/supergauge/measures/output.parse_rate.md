---
id: output.parse_rate
version: "0.1"
type: deterministic
group: effectiveness
parameters: [schema_digest]
author: Superagentic AI
---

# `output.parse_rate`

The proportion of runs whose final output parsed against the output contract
the task declared.

## Why it exists

An agent that answers correctly in a shape no caller can read has not answered.
Structured-output agents (typed signatures, JSON tool results, function-call
arguments) fail this way more often than they fail on content, and the failure
is invisible to a judged score that reads the text generously.

Parsing is mechanical. It needs no model in the loop, so it is a natural floor
to gate on before any content measure is consulted.

## Computation

For each run `r` in the evaluated split, let `p(r)` be true when the final
output parses under the declared contract (a JSON Schema, a typed signature, a
grammar, or a documented parser) without repair.

```
output.parse_rate = |{ r : p(r) }| / |R|
```

Report `n` (`|R|`) alongside the value. The contract SHOULD be fingerprinted in
the entry as `schema_digest` when the emitter holds it.

### What counts as a parse

| Case | Counts as parsed |
|---|---|
| Output validates against the declared contract as emitted | Yes |
| Output parses only after a retry, repair prompt or lenient fixer | No |
| Output parses but a required field is missing or mistyped | No |
| Output is empty, truncated or a refusal string | No |

A run whose output parsed after repair MAY be reported separately by the
emitter under an `x-` id; it MUST NOT be counted here.

### Failure cases

| Case | Required behaviour |
|---|---|
| Task declares no output contract | Do not report the measure |
| Run errored for infrastructure reasons | Exclude the run; reduce `n`; note the exclusion in the ledger |
| Contract changed between runs in the same split | Do not report the measure |

## Evidence required

- The raw final output of every counted run, in the referenced ledger.
- The declared contract, or its digest.

## Record entry

```yaml
- id: output.parse_rate
  value: 0.98
  split: held-out
  n: 50
  schema_digest: sha256:...
```

## Backing a gate

Permitted. Typical floors are high (0.95 or above), since an unparseable output
is a hard failure for any caller.

## Related

`task.completion` asserts on the end state; this measure asserts only that the
output was readable. A run can parse and still fail the task.
