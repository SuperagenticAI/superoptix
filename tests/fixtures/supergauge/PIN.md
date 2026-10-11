# Vendored SuperGauge conformance checker

Source: https://github.com/SuperagenticAI/supergauge
Revision: 5ce6b583af317928956ebd182d63b9ce1bd2aca9 (branch superoptix-l2-integration, PR #6)
License: Apache-2.0 (LICENSE in this directory)

Contents: `conformance/check.py`, `schema/`, `measures/` (the layout check.py
expects), plus `l3-superoptix-hardened-ship.yaml` as an upstream reference record.

Vendored instead of fetched so CI needs no network or secrets. Files are
byte-identical to the pinned revision; `scripts/refresh_supergauge_checker.sh`
re-fetches them.

TODO: switch the pin to tag `checker-v0.1.0` once SuperGauge PR #6 merges
(SuperGauge tags the merge commit). Do not pin main eb59184.
