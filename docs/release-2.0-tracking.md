# SuperOptiX 2.0 tracking

Status: in review. Not released, not tagged, not published.

This file exists so the `release/2.0` -> `main` draft PR has a diff while the
feature PRs below are reviewed. Remove it before 2.0 merges to `main`.

| Order | PR | Scope |
| --- | --- | --- |
| 1 | #21 | A2A keep-alive session and version-aware interface selection |
| 2 | #22 | GEPA held-out split, train and held-out gains |
| 3 | #23 | DSPy 3.5 readiness, engine-based MLX LM, dspy>=3.4 |
| 4 | #24 | SuperGauge sealed holdout, deterministic L2 gates, integrity, pinned checker (stacked on #22) |
| 5 | #25 | `super agent test`, `optimize --gauge-out` (stacked on #24) |
| 6 | #26 | 2.0.0 version (unreleased), removals, migration guide (stacked on #25) |
