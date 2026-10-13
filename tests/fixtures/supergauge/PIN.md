# Vendored SuperGauge conformance checker

Source: https://github.com/SuperagenticAI/supergauge
Revision: a5920cce2f81b55673756860143ba39835d35f1a (tag checker-v0.1.0, squash merge of PR #6)
License: Apache-2.0 (LICENSE in this directory)

Contents: `conformance/check.py`, `schema/`, `measures/` (the layout check.py
expects), plus `l3-superoptix-hardened-ship.yaml` as an upstream reference record.

Vendored instead of fetched so CI needs no network or secrets. Files are
byte-identical to the pinned revision; `scripts/refresh_supergauge_checker.sh`
re-fetches them.

The tag `checker-v0.1.0` points at this commit; the full SHA is pinned so a
moved tag cannot change what CI runs.
