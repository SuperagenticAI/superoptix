# Agent Quality Records

`super agent evaluate` runs an agent's BDD specification and tells you what
passed. It leaves nothing behind that a colleague, an auditor or your future
self can read months later to answer what was checked before the agent went
live.

The `--gauge-out` flag writes that down, in the format published at
[SuperGauge](https://github.com/SuperagenticAI/supergauge).

```bash
super agent evaluate developer --gauge-out record.yaml
```

```text
📋 Agent Quality Record: record.yaml
```

## What the record holds

```yaml
supergauge: "0.1"
profile: {id: sg/framework-agent, version: "0.1", tier: T1}

subject:
  agent: developer
  harness_digest: sha256:9c1e...        # the playbook, fingerprinted
  model: {provider: ollama, id: qwen3:8b}
  authority:                            # what the agent could do
    sandbox: docker
    egress: deny-by-default
    capabilities: [search, fetch]

task_set:
  manifest_digest: sha256:7d02...       # the scenarios, fingerprinted
  held_in: 6
  held_out: 2
  sealed: true

measures:
  - {id: task.completion, value: 0.83, n: 8}
  - {id: interop.routing_invocation, value: 0.75}

decision:
  verdict: hold
  actor: "you@example.com"
```

Scenarios in the playbook are the task set. A scenario marked `split: held-out`
counts toward the held-out portion; where the playbook declares no split, the
record reports zero held-out scenarios, which is accurate and caps the level it
can reach.

`authority` is required by the specification and read from the compiled
playbook: tools become capabilities, and the runtime block supplies the sandbox
and egress posture. A record naming the agent without naming its permissions can
be structurally valid and substantively wrong, so the field is not optional.

## Options

| Flag | Default | Purpose |
| --- | --- | --- |
| `--gauge-out PATH` | off | Write the record. `.json` selects JSON, otherwise YAML |
| `--gauge-tier {T0,T1,T2}` | `T1` | Risk tier the record claims |
| `--gauge-sealed` | off | Assert the held-out scenarios were closed to anything that tunes the agent |

Record emission never fails an evaluation. A problem writing the file prints a
warning and the evaluation result stands.

## Routing invocation

SuperOptiX reports one measure the coding-agent side has no equivalent for.

An agent published over A2A is selected by another agent reading its card, which
makes the description on that card a routing interface. Where selection fails,
the agent receives no work, and its completion rate describes traffic that never
arrived. `interop.routing_invocation` records how often a calling agent chooses
yours from a catalogue of candidates. The effect is substantial: four sibling
skills under identical queries, differing only in how each described itself,
moved invocation from 12.5% to 100%.

See [Routing quality](a2a-routing.md) for how the score is produced.

## Conformance levels

An evaluation-only record reaches **L1**, held there by two absent fields that
reflect what SuperOptiX is able to assert.

The first is the gate list. A gate is a deterministic condition that blocks a
release, and asserting one requires a policy engine that decides at runtime.
SuperOptiX has none, so it reports measures and leaves the gate list empty.
Where the agent runs under a harness that does enforce policy, such as SuperQode,
the gates are recorded there instead.

The second is contamination probes. A probe is a scenario whose success
condition is unreachable by legitimate means, so a passing result exposes
leakage into the held-out split. Declaring two in the playbook lets the record
report them, which is the remaining requirement for L2.

Reaching L3 additionally needs repeated independent attempts for
`reliability.pass_hat_k`. The emitter supports it through `add_reliability`, and
the CLI runs a single pass today.

## Checking a record

Any SuperGauge implementation reads it. The published suite:

```bash
git clone https://github.com/SuperagenticAI/supergauge
python supergauge/conformance/check.py record.yaml --level L1
```

SuperQode reads the same format, so an organisation running both gets one record
shape across a repository harness and an agent on any supported runtime.

## See also

- [Golden Workflow](golden-workflow.md)
- [Routing quality](a2a-routing.md)
- [SuperGauge specification](https://github.com/SuperagenticAI/supergauge)
