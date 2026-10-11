---
id: assurance.evaluator_independence
version: "0.1"
type: deterministic
group: assurance
parameters: []
author: Superagentic AI
---

# `assurance.evaluator_independence`

Whether the grader saw only the artifact and the resulting world state, and not
the worker's own account of what it did.

## Why it exists

Where the same process both does the work and produces the proof it worked,
the proof is worth less than it appears.
This is measured behaviour, not a hypothetical: severe cases of agents quietly
disabling tests and then reporting that a review passed have been observed in
roughly two percent of production coding-agent sessions, and benchmarks built
around impossible tasks record substantially higher rates of test modification
when the option is available.

Sealing the task set does not help here. The split can be perfectly clean while
the grader reads a self-report describing work that never happened.

## Computation

Boolean. All conditions must hold:

| Condition | Meaning |
|---|---|
| Grader input excludes the worker transcript | No assistant messages reached the grader |
| Grader input excludes the worker's plan | No self-authored plan or summary reached the grader |
| Grader input excludes worker-authored test results | Results were produced by a runner the worker cannot modify |
| Grader identity differs from worker identity | Separate credentials, separate process |

```
assurance.evaluator_independence = true when all conditions hold
```

### The subtle case

An agent that edits a test and then runs it produces a genuine result from a
compromised oracle. Independence requires that the test suite the grader trusts
lives outside the worker's write scope, or that modification is detected by
digest before results are accepted.

### Failure cases

| Case | Required behaviour |
|---|---|
| The grader runs in the worker's process | Report false |
| The worker can write to the test suite the grader uses | Report false unless the suite is digest-checked |
| A human read the transcript before deciding | Not a violation of this measure; record it in `decision` |

## Evidence required

The grader's input manifest, the identity under which it ran, and the write
scope granted to the worker.

## Record entry

```yaml
- id: assurance.evaluator_independence
  value: true
```

## Backing a gate

Permitted. Required at L3, where the record asserts it in
`assurance.evaluator_independent`.

## Related

`assurance.evidence_complete` covers whether the record can be reproduced at
all.
