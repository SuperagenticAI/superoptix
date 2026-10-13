---
id: tool.correctness
version: "0.1"
type: deterministic
group: effectiveness
parameters: []
author: Superagentic AI
---

# `tool.correctness`

The proportion of tool invocations that were well formed and appropriate.

## Why it exists

Tool calls are where an agent touches the world, so they are where a mistake
stops being a bad sentence and starts being an effect. Malformed arguments,
plausible calls to the wrong tool, and the same call repeated because its result
was ignored are all invisible in the final answer and obvious in the ledger.

## Computation

For each invocation, four checks:

| Check | Fails when |
|---|---|
| Schema | Arguments do not validate against the tool's declared schema |
| Existence | The tool named is absent from the declared surface |
| Selection | The task declares an expected tool for a step and a different one was used |
| Redundancy | An identical call is repeated with an unchanged result |

```
tool.correctness = (invocations passing all checks) / (total invocations)
```

Selection is checked only where a task declares an expectation. A task that
declares none skips that check instead of failing it, so this measure never
punishes a legitimate alternative route.

### Failure cases

| Case | Required behaviour |
|---|---|
| A tool has no published schema | Skip the schema check, record the tool as unschematised |
| A retry follows a genuine transient failure | Not redundant; the preceding result must differ |
| Zero invocations in a run | Exclude the run from the denominator |

## Evidence required

Tool schemas as declared to the agent, and the invocation record with arguments
and results.

## Record entry

```yaml
- id: tool.correctness
  value: 0.97
  n: 412
```

## Backing a gate

Permitted. Schema and existence failures are usually worth gating tightly;
redundancy rarely is.

## Related

`safety.tool_abuse` covers calls that were well formed and should not have been
permitted.
