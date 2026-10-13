# Migrating to SuperOptiX 2.0

2.0 is pending review and unreleased. This guide lists every change that can
affect an existing 0.3.x project and what to do about it.

## 1. Optimization numbers changed meaning

GEPA used to select candidates on the same scenarios it trained on, so the one
gain it printed was measured on items it had just tuned against
(arXiv:2610.09239). In 2.0:

- A seeded 20% of scenarios is held out and never shown to GEPA
  (`optimization.optimizer.params.valset_fraction`, default `0.2`; the split is
  seeded by `seed`).
- `super agent optimize` prints and returns two gains: the reported (train)
  gain and the held-out gain. Quote the held-out gain.
- `training_examples` in the result is the train-split size.
- Datasets with fewer than 4 usable scenarios skip the split with a warning and
  report a train-only gain (`heldout_gain: null`).
- `optimize_routing(...)` takes `valset_fraction` and `seed`;
  `OptimizationResult.improvement` is the train gain and
  `heldout_improvement` the held-out gain.

To reproduce 0.3.x behaviour, set `valset_fraction: 0`. The output then says the
gain is train-only.

## 2. DSPy 3.4 or newer

`dspy>=3.4` is required. DSPy 3.5 removes OpenAI-style `lm(messages=...)`, custom
`BaseLM.forward` LMs and `LegacyEngine`
([DSPy migration notes](https://dspy.ai/current/community/normalized-lm-api-migration/)).

- `MLXDSPyClient(...)` now returns a `dspy.LM` backed by an engine. Call it
  like any LM (`lm("...")`) or pass a `dspy.lm15.Request`. Subclassing it or
  calling `.forward(messages=...)` no longer works. New code can use
  `create_mlx_lm(...)`.
- Your own custom LMs should move to the engine interface before DSPy 3.5.
- Keep importing `superoptix` before `dspy`.

## 3. Agent Quality Records

- `--gauge-sealed` no longer asserts that the held-out split was sealed. It
  checks the split recorded by the last GEPA run
  (`pipelines/<agent>_holdout.json`) against the playbook. With no split, or an
  edited held-out scenario, `sealed` is `false` and
  `record.superoptix.json` says why. Run `super agent optimize` again after
  editing held-out scenarios.
- `x-superoptix` is no longer inside the record file (the SuperGauge schema
  allows no extra top-level keys). It is written to `<stem>.superoptix.json`.
  Code that read `record["x-superoptix"]` from the file should read the sidecar.
- Records now carry `subject.authority.grant_digest` and reference an
  evaluation ledger `<stem>.ledger.jsonl`, so they validate against the
  SuperGauge schema. Capabilities are de-duplicated and sorted.
- Mark contamination probes with `canary: true`. They are excluded from GEPA
  training and count in the `evaluate` pass rate (they are expected to fail).
- New: `super agent test` and `--gauge-gates`, `--k`, `--gate-floor`. See
  [Testing agents](testing-agents.md). `evaluate --gauge-out` without them
  behaves as before: no gates, verdict `hold`, L1 at best.
- `super agent test` exits `0` only when SuperGauge checker-v0.1.0 would allow
  the release (`--require-ship`: level at least L2, `ship`, a named actor,
  passing gates), otherwise `1`. Set `--actor` or `SUPEROPTIX_RELEASE_ACTOR`.

## 4. A2A client

- When an Agent Card lists several interfaces, the client picks the highest
  `protocolVersion` (1.0 before 0.3), then binding (`HTTP+JSON`, `JSONRPC`),
  then card order. A peer listing 0.3 first is now reached over 1.0.
- `A2AClient` keeps one HTTP session; `disconnect()` and `close()` release it,
  and `with A2AClient(url) as client:` works. `A2ARegistry` reuses one client
  per URL; call `registry.close()` when done.

## 5. Removed

| Removed | Use instead |
| --- | --- |
| `super agent compile --local-models` | `--local-ollama` |
| `PipelineUtilities.get_optimizer(tier, k)` | `PipelineUtilities.get_custom_optimizer(...)` or `DSPyOptimizerFactory.create_tier_optimized_optimizer(...)` |
| `super agent tier-status` (`ts`) | Nothing needed. Playbook tiers stay in the playbook (`super agent pull --tier`, `super spec generate oracles` or `genies`). Bare `super agent` now prints help. |

## 6. CLI help and output

The CLI text now matches the 2.0 positioning: optimization and quality layer
for AI agents, with three pillars.

- `super --help` and `super agent --help` list commands pillar-first:
  optimize (`super agent optimize`), connect over A2A (`super a2a adapt`,
  `super agent serve`), ship with quality (`super agent evaluate`,
  `super agent test`). Only the listing order changed; every command and alias
  parses as before.
- `super docs`, `super init` and the `pull`/`compile` next steps point at
  `optimize --gauge-out`, `test` and `serve`. They no longer suggest
  `super agent run --interactive`, `compile --basic` or
  `super spec generate genie` (none existed; use `genies`).
- Scripts that parse the banner or help text should match the new wording.

## 7. Packaging

- Version `2.0.0`, classifier `Development Status :: 5 - Production/Stable`.
- `jsonschema` is in the `testing` extra (SuperGauge L1 validation in tests).
