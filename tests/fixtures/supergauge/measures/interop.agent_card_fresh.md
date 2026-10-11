---
id: interop.agent_card_fresh
version: "0.1"
type: deterministic
group: effectiveness
parameters: []
author: Superagentic AI
---

# `interop.agent_card_fresh`

Whether the Agent Card digest and skill allowlist on the record match the
published card at emission time.

## Why it exists

An A2A-published agent is discovered through its Agent Card. A release can pin
a harness digest while the well-known card drifts: skills removed, endpoint
changed, or a different JSON body served at the same URL. Callers then route
against a surface that was never the one under review. Freshness makes that
mismatch visible as a deterministic check, and profiles MAY gate on it.

See `rfcs/0002-a2a-agent-card-binding.md`.

## Computation

Boolean. Requires `subject.agent_card` on the record. All conditions must hold:

| Condition | Meaning |
|---|---|
| Present | `well_known_url` and `card_digest` are populated |
| Digest match | SHA-256 of the card JSON bytes fetched or published for this emission equals `card_digest` |
| Skill subset | Every entry in `skill_ids` (when present) appears as a skill `id` on that card |

```
interop.agent_card_fresh = true when all conditions hold
```

When `skill_ids` is omitted, only presence and digest match are required.
Version and ETag fields are recorded for operators; they are not required for
the boolean unless a profile tightens the rule.

### Failure cases

| Case | Required behaviour |
|---|---|
| `subject.agent_card` absent | Do not report this measure |
| URL unreachable or card unauthenticated for the emitter | Report false, or omit the measure; never invent a digest |
| Digest mismatch | Report false |
| `skill_ids` contains an unknown skill id | Report false |
| Card body empty or not JSON | Report false |

## Evidence required

The Agent Card JSON bytes corresponding to `card_digest`, and the fetch or
publish step used at emission (URL, timestamp, optional ETag).

## Record entry

```yaml
- id: interop.agent_card_fresh
  value: true
```

## Backing a gate

Permitted. Useful when the subject is published for other agents to call and a
stale or divergent card would otherwise ship unnoticed.

## Related

`interop.routing_invocation` measures whether callers select the agent;
this measure checks that the card those callers read matches the release.
