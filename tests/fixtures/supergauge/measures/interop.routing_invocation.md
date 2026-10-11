---
id: interop.routing_invocation
version: "0.1"
type: deterministic
group: effectiveness
parameters: []
author: Superagentic AI
---

# `interop.routing_invocation`

The rate at which a calling agent selects this agent from a catalogue of
candidates, given queries the agent should handle.

## Why it exists

An agent published over a protocol such as A2A is chosen by another agent
reading its card. The description on that card is a routing interface, and an
agent nobody routes to has a completion rate nobody observes.

This is a quality dimension that only appears once agents call each other. It
sits in effectiveness because failing to be selected for work you can do is an
effectiveness failure, and it is invisible to every other measure in the group:
the agent completes the tasks it receives, and receives the wrong ones.

The effect is large enough to matter. A published comparison of four sibling
skills under identical queries, differing only in how each described itself,
moved invocation from 12.5% to 100%.

## Computation

Assemble a catalogue containing this agent and at least three plausible
alternatives. For each query in a set the agent should handle, record which
candidate the router selected.

```
interop.routing_invocation = queries where this agent was selected / total queries
```

Report the catalogue size, since a rate against three candidates and a rate
against thirty are different quantities. Recording it in `n` alongside the
query count is the minimum; a profile MAY require the catalogue digest.

### Router dependence

The value is a property of the pair, not of the agent. A record MUST name the
router used, as a `pack` reference or a local extension field, or two values
cannot be compared.

### Failure cases

| Case | Required behaviour |
|---|---|
| The catalogue holds no alternatives | Do not report; selection was forced |
| Queries were written from this agent's own card | Do not report; the set is contaminated |
| The router is non-deterministic | Repeat and report the mean, with the repeat count |

## Evidence required

The catalogue, the query set, the router identity and version, and the
selection made for each query.

## Record entry

```yaml
- id: interop.routing_invocation
  value: 0.75
  n: 40
```

## Backing a gate

Permitted. Useful where an agent is published for others to call and a
regression in its card would otherwise go unnoticed until traffic disappeared.

## Related

`task.completion` measures the work that arrives; this measures whether it
arrives at all.
