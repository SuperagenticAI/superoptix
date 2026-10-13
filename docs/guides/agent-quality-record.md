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

Scenarios in the playbook are the task set. With `--gauge-sealed` the held-out
portion is the split `super agent optimize` held back from GEPA (see
[GEPA held-out split](gepa-optimization.md)). `sealed: true` is derived, not
asserted: it holds only when `pipelines/<agent>_holdout.json` exists, every
held-out scenario is unchanged in the playbook, the recomputed digest matches the
recorded one, and no canary probe passed. Otherwise `sealed` is false and the
sidecar file says why (for example "no held-out split recorded; run super agent
optimize (GEPA) first"). The record then also carries the deterministic measure
`assurance.holdout_sealed`.

`authority` is required by the specification and read from the compiled
playbook: tools become capabilities, and the runtime block supplies the sandbox
and egress posture. SuperGauge requires either an ACS policy version or a grant
digest; SuperOptiX has no ACS policy, so `grant_digest` is the sha256 of the
authority-relevant playbook content in force for the run (tools, runtime,
sandbox, network). A record naming the agent without naming its permissions can
be structurally valid and substantively wrong, so the field is not optional.

## Options

| Flag | Default | Purpose |
| --- | --- | --- |
| `--gauge-out PATH` | off | Write the record. `.json` selects JSON, otherwise YAML |
| `--gauge-tier {T0,T1,T2}` | `T1` | Risk tier the record claims |
| `--gauge-sealed` | off | Derive `sealed` from the GEPA held-out split (false with a reason when there is none) |
| `--gauge-gates` | off | Add deterministic gates and a deterministic decision (see below) |
| `--k N` | 1 | Repeat the suite N times for `reliability.pass_hat_k` (cache off; skipped when memory is enabled) |
| `--gate-floor ID=VALUE` | SuperOptiX defaults | Override a gate floor; repeatable |
| `--gauge-jev` | off | Optional Jev / System One QC (needs `superoptix[typesafe]` / `[jev]`) |
| `--gauge-jev-min-confidence` | emitter default | Soft-hold when Choice accept confidence is below this |
| `--gauge-jev-model` | env / default | Versioned judge model id pinned into `assurance.judge` |

Record emission never fails an evaluation. A problem writing the file prints a
warning and the evaluation result stands.

Three files are written:

- `record.yaml`: the Agent Quality Record. It contains only SuperGauge schema
  fields, so it validates against the published schema.
- `record.ledger.jsonl`: one row per scenario per attempt (status, parse result,
  output, error). It is the evidence the record references
  (`assurance.evidence.format: superoptix.bdd-ledger/1`, `replayable: false`
  because the ledger records outputs but cannot re-run the agent).
- `record.superoptix.json`: SuperOptiX metadata the schema has no slot for
  (framework, why the split is or is not sealed, Jev advice, GEPA gains).

## Deterministic gates (2.0)

With `--gauge-gates` (default in `super agent test`) the record carries one gate
per deterministic measure the run actually produced. Measure ids are canonical
SuperGauge registry ids; none is invented and none is judged.

| Measure / gate | Reported when | Gate |
| --- | --- | --- |
| `output.parse_rate` | The playbook declares output fields (`tasks[0].outputs` or `output_fields`) | floor, default 0.95 |
| `reliability.beats_trivial_baseline` | The built-in BDD evaluator ran (same success condition for agent and baseline) | pass when true |
| `reliability.pass_hat_k` | `--k 2` or more | floor, default 0.6 |
| `tool.correctness` | Tool calls were recorded (DSPy ReAct `trajectory`) and the playbook declares tools | floor, default 0.9 |
| `trajectory.valid` | A scenario declares `trajectory:` constraints and tool calls were recorded | floor, default 0.9 |
| `assurance.holdout_sealed` | `--gauge-sealed` | pass when true |

Notes on what each one means here:

- Parse rate checks the program output as returned: every declared field
  present, non-empty and of the declared simple type, with the declared contract
  fingerprinted as `schema_digest`. DSPy adapters can retry a failed parse
  internally (for example the ChatAdapter JSON fallback); that retry is not
  visible to SuperOptiX, so read the value as "parsed after the adapter's own
  handling".
- The trivial baseline is `echo-input`: the scenario input echoed back, scored
  by the same evaluator. It is declared before the run and never tuned.
- pass^k repeats the suite with the DSPy response cache disabled. Agents with
  memory enabled are skipped, because carried state breaks independence.
- No tool or trajectory data means no measure. Nothing is defaulted.
- Floors are SuperOptiX implementer defaults (SuperGauge publishes none at 0.1)
  and are written into each gate entry, so the record shows what was enforced.

The decision is deterministic: `ship` only when there is at least one gate,
every gate passes, the split is sealed, at least one canary scenario ran,
none passed, and a named release actor is known (`--actor`,
`SUPEROPTIX_RELEASE_ACTOR`, `GITHUB_ACTOR` or `USER`; never `unknown`). Otherwise `hold`, with the reasons in `decision.rationale`.

Canary scenarios are contamination probes: scenarios whose expected output
cannot be produced by legitimate means. Mark them in the playbook:

```yaml
feature_specifications:
  scenarios:
    - name: canary_unknowable_fact
      canary: true
      input: {query: "What is the internal ticket id for incident 7?"}
      expected_output: {answer: "TCK-55120-ZETA"}
```

The optimizer never sees canaries. Their outcomes are recorded under
`assurance.integrity.canaries` (SuperGauge RFC 0005); a passing canary
unseals the split and holds the release.

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

Be precise about what each level means here.

- `super agent evaluate --gauge-out` alone: **L1** at best. No gates, nothing
  sealed.
- `super agent test` (or `evaluate --gauge-sealed --gauge-gates`) after a GEPA
  run, with canary scenarios declared: **L2** when the gates pass. L2 means the
  record carries deterministic gates, a sealed and fingerprinted held-out split
  and contamination probes. It does not mean the agent is good; it means the
  claim is checkable.
- **L3** additionally needs `reliability.pass_hat_k` (use `--k 3`) and
  `assurance.evaluator_independent`. SuperOptiX does not assert evaluator
  independence today (the evaluator sees the agent's output text), so records
  stop at L2.
- **L4** needs a signed record, a rollback target and a replayable ledger.
  Not produced by SuperOptiX.

## Checking a record

Any SuperGauge implementation reads it. The published suite:

```bash
SG_REV=a5920cce2f81b55673756860143ba39835d35f1a   # tag checker-v0.1.0
git clone --filter=blob:none --no-checkout https://github.com/SuperagenticAI/supergauge .supergauge
git -C .supergauge sparse-checkout set conformance schema measures
git -C .supergauge checkout "$SG_REV"
pip install pyyaml jsonschema
python .supergauge/conformance/check.py record.yaml --level L2 --require-ship
```

`super agent test --checker .supergauge/conformance/check.py` runs the same
check as part of the CLI gate. Without `--checker` the CLI uses a built-in
precheck that mirrors the L1 presence and L2 rules; the SuperOptiX test suite
runs the pinned upstream checker against generated records to keep them in
step.

SuperQode reads the same format, so an organisation running both gets one record
shape across a repository harness and an agent on any supported runtime.

## See also

- [Testing agents with SuperOptiX](testing-agents.md)
- [Golden Workflow](golden-workflow.md)
- [Routing quality](a2a-routing.md)
- [SuperGauge specification](https://github.com/SuperagenticAI/supergauge)

## Optional Jev / System One quality control

When you also pass `--gauge-jev` (or set `SUPEROPTIX_JEV=1`), the emitter maps a
typed Choice disposition onto the record: accept→ship, warn→hold, reject→reject,
pins `assurance.judge`, and soft-holds on low confidence. Judged confidence
never alone hard-gates ship. See [Jev quality control and AQR emit](jev-quality-control.md).

Install the optional extra (DSPy 3.4+):

```bash
pip install "superoptix[typesafe]"
export TYPESAFE_API_KEY=...
super agent evaluate developer --gauge-out record.json --gauge-jev
```

Without the extra, a heuristic disposition is still recorded so the AQR shape
stays reviewable. Live Jev replaces it when configured.

