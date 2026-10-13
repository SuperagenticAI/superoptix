---
id: efficiency.cost_per_success
version: "0.1"
type: deterministic
group: efficiency
parameters: [unit]
author: Superagentic AI
---

# `efficiency.cost_per_success`

Spend divided by the number of tasks completed.

## Why it exists

Cost per completed task is what makes an agent that retries its way to an
answer comparable with one that arrives first time.

An average taken over all runs flatters an agent that fails cheaply. Dividing by
successes prices what the agent delivered, so a cheap failure makes the
number worse instead of better.

## Computation

```
efficiency.cost_per_success = total cost across all runs / |{ t : task.completion(t) }|
```

The numerator covers every run in the evaluation, including failed ones. The
denominator counts only completed tasks. Where no task completed, the measure is
undefined and MUST be omitted.

`unit` MUST be an ISO 4217 currency code, lowercased.

### Failure cases

| Case | Required behaviour |
|---|---|
| Provider reports no usage for a call | Record the run as unmetered and exclude it, noting the exclusion |
| Cached or discounted pricing applied | Record the effective figure, and note the arrangement |
| Zero completions | Omit the measure |

## Evidence required

Per-run usage from the provider, and the completion result for each task, so the
denominator is reproducible.

## Record entry

```yaml
- id: efficiency.cost_per_success
  value: 0.24
  n: 46
```

## Backing a gate

Permitted, and worth pairing with a completion gate. On its own an efficiency
floor is satisfiable by an agent that refuses hard tasks.

## Related

The other two efficiency measures, and `task.completion`, which supplies the
denominator.
