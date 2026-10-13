# Testing agents with SuperOptiX

`super agent test` is the CI gate for a SuperOptiX agent. It runs the agent's
BDD scenarios, writes a [SuperGauge](https://github.com/SuperagenticAI/supergauge)
Agent Quality Record, and exits non-zero unless the record's verdict is `ship`.

```bash
super agent optimize my_agent              # GEPA; holds out 20% of scenarios
super agent test my_agent --k 3 --gauge-out record.yaml
```

Exit codes follow SuperGauge `check.py --level L2 --require-ship`
(checker-v0.1.0): `0` only when the release is allowed (level at least L2 and
`--gate`, verdict `ship`, a named actor, all gates passing); `1` otherwise,
including when the run failed. The actor comes from `--actor`,
`SUPEROPTIX_RELEASE_ACTOR`, `GITHUB_ACTOR` or `USER`; an unnamed actor holds.

## What it does

`super agent test` is `super agent evaluate` with these defaults:

| Setting | Value |
| --- | --- |
| Held-out split | Sealed from the last GEPA run (`--gauge-sealed`) |
| Gates | Deterministic gates on what the run produced (`--gauge-gates`) |
| Decision | `ship` only if every gate passes, the split is sealed and no canary passed |
| Conformance | Built-in L2 precheck; add `--checker PATH` for the pinned SuperGauge checker |
| Jev | Off. `--jev` adds advisory live Jev review that can hold or reject, never ship |

## Before it can pass

1. Declare output fields in the playbook (`tasks[0].outputs`) so
   `output.parse_rate` has a contract to check.
2. Add at least two canary scenarios (`canary: true`) whose expected output the
   agent cannot legitimately produce.
3. Have enough scenarios for a held-out split (at least 4 non-canary scenarios;
   20% are held out, minimum 2).
4. Run `super agent optimize` (GEPA) so a held-out split exists. Without it the
   record says `sealed: false` with the reason and the test holds.
5. Use `--k 3` (or more) for `reliability.pass_hat_k`.

Editing a held-out scenario after optimizing breaks the seal; re-run optimize.

## In GitHub Actions

```yaml
- run: super agent test my_agent --k 3 --gauge-out record.yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: agent-quality-record
    path: |
      record.yaml
      record.ledger.jsonl
      record.superoptix.json
```

## Honest limits

- L2 means the claim is checkable (deterministic gates, sealed split, probes),
  not that the agent is good. Records stop at L2: SuperOptiX does not assert
  evaluator independence.
- Floors are SuperOptiX defaults, not SuperGauge published floors. Set your own
  with `--gate-floor output.parse_rate=0.99`.
- `tool.correctness` and `trajectory.valid` appear only when tool calls were
  recorded; otherwise they are omitted, never defaulted.
- Jev is experimental advice: its confidence is not a calibrated probability,
  it is not a zero-shot router, and it is never release authority.

## Optimize with a record

`super agent optimize my_agent --gauge-out record.yaml` evaluates the optimized
agent on the sealed split after a successful GEPA run and writes the same kind
of record. GEPA's reported (train) and held-out gains go into the
`record.superoptix.json` sidecar, since they are optimizer metrics rather than
SuperGauge measures.

See [Agent Quality Records](agent-quality-record.md) for every field.
