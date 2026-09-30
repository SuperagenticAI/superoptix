# Jev quality control and AQR emit

Optional System One (TypeSafe **Jev**) quality-control for SuperOptiX evaluations.
SuperOptiX emits Agent Quality Records; SuperGauge owns the AQR shape, gate
policy, and assurance pinning (RFC 0004 / RFC 0005). This guide covers the
optional SuperOptiX adapters only.

## Ownership split

| Owner | Responsibility |
| --- | --- |
| **SuperGauge** | AQR schema, gate policy, assurance pinning, RFC 0004 / 0005, assurance-export packs |
| **SuperOptiX** | Optional `dspy[typesafe]` adapters, Propose-Don't-Judge admission wiring, ReAnchor version tags, card-review typed Score/Choice, AQR emit when `--gauge-out` / `--gauge-jev` is used |

Choice `accept` supplies advice and retains an existing approval only when
deterministic gates pass and the split is sealed. `warn` holds and `reject`
rejects. Existing rejections remain in place. Release approval belongs to the
release policy and its approver.

## Enable

```bash
pip install "superoptix[typesafe]"
# alias: pip install "superoptix[jev]"
# equivalent peer install: pip install "dspy[typesafe]>=3.4"
export TYPESAFE_API_KEY=...
# Prefer a versioned model id when pinning:
export SUPEROPTIX_JEV_MODEL=jev-1.13.0
```

Needs **DSPy 3.4+** for `dspy.experimental` Choice / Score / Noul / ReAnchor /
TypeSafe. Works with DSPy 3.4+ typesafe / Jev. The optional extra declares
`dspy[typesafe]>=3.4` and does not block core installs.

## Evaluate with AQR + Jev QC

```bash
super agent evaluate my-agent \
  --gauge-out record.json \
  --gauge-jev \
  --gauge-jev-min-confidence 0.75 \
  --gauge-jev-model jev-1.13.0
```

Or set `SUPEROPTIX_JEV=1`. Without the typesafe extra or API key, SuperOptiX
writes a typed disposition from evaluate totals. The fallback is labelled
`heuristic-evaluate`, its confidence is a proxy, and it creates no Jev judge
pin. Live calls assess a pass-count and framework summary. This summary
provides limited evidence about individual answers and tool trajectories.

## What gets written

1. **Choice advice**: acceptance retains prior ship approval with passing checks;
   warning holds; rejection rejects. Evaluation records start on hold.
2. **Soft-hold**: Choice accept with confidence below
   `--gauge-jev-min-confidence` becomes `decision.verdict: hold` with rationale.
   No gate entry is invented for confidence.
3. **assurance.judge**: live-call `id`, versioned `model` and `pack_digest`.
4. **x-superoptix.jev**: source, confidence kind, disposition and threshold version.

Sample JSON (soft-hold):

```json
{
  "assurance": {
    "judge": {
      "id": "typesafe/jev@1",
      "model": "jev-1.13.0",
      "pack_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    "evaluator_independent": false
  },
  "decision": {
    "verdict": "hold",
    "actor": "you@example.com",
    "rationale": "Soft-hold: Choice accept with confidence 0.41 below emitter min_confidence 0.75. Deterministic gates (if any) are unchanged; judged confidence does not alone hard-gate ship."
  },
  "gates": []
}
```

## Conformance and release checks

An evaluation-only SuperOptiX record remains **L1**. Soft-hold and judged
measures do not create deterministic gates. A path to L2 needs
deterministic gates (compose [SuperQode](https://superqode.dev) policy /
SystemOne harness gates, or other policy probes). SuperOptiX does not invent
fake gates.

## Card review

`agent-card-review` still reports free-text severity findings. It also attaches
a typed disposition (`accept` / `warn` / `reject`) derived from the score and
finding severities, suitable for the same Choice→AQR mapping.

## Propose-Don't-Judge (GEPA admission)

Optimizers propose candidates. A frozen referee may admit via Score / Choice
using `superoptix.quality.admit_proposal` without making typesafe a core
dependency (lazy import). Low referee confidence soft-holds; it does not alone
admit to ship.

```python
from superoptix.quality import admit_proposal, DispositionJudgment

result = admit_proposal(
    referee=DispositionJudgment(choice="accept", confidence=0.41)
)
assert result.action == "hold"  # soft-hold
```

## ReAnchor / threshold moves

Tag every threshold or ReAnchor calibration with a version string and keep prior
outcome evidence for later calibration. Prefactor: swapping the Jev model or
question pack is a **component change**, not an invisible tweak.

```python
from superoptix.quality.typesafe_adapter import reanchor_version_tag

note = reanchor_version_tag(version="reanchor-2026-09-26.1")
```

## References (SuperGauge)

- [RFC 0004: Jev / SystemOne interop](https://github.com/SuperagenticAI/supergauge/blob/main/rfcs/0004-jev-systemone-interop.md)
- [RFC 0005: Test integrity / reward-hack evidence](https://github.com/SuperagenticAI/supergauge/blob/main/rfcs/0005-test-integrity-reward-hack.md)
- [Emitter: Jev / System One](https://github.com/SuperagenticAI/supergauge/blob/main/docs/emitters/jev-systemone.md)
- [Assurance export packs](https://github.com/SuperagenticAI/supergauge/blob/main/packs/assurance-export.md)

## Out of scope

- SuperGauge hosting or calling Jev
- Hard merge gate on confidence alone
- Adding `dspy[typesafe]` as a core SuperOptiX dependency
