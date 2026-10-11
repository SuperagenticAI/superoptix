#!/usr/bin/env bash
# Re-vendor the SuperGauge conformance checker at a pinned revision.
# Usage: scripts/refresh_supergauge_checker.sh [REV]
set -euo pipefail
REV="${1:-a5920cce2f81b55673756860143ba39835d35f1a}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/tests/fixtures/supergauge"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --quiet --filter=blob:none --no-checkout https://github.com/SuperagenticAI/supergauge "$TMP/sg"
git -C "$TMP/sg" sparse-checkout set conformance schema measures
git -C "$TMP/sg" checkout --quiet "$REV"
rm -rf "$DEST/conformance" "$DEST/schema" "$DEST/measures"
mkdir -p "$DEST/conformance"
cp "$TMP/sg/conformance/check.py" "$DEST/conformance/check.py"
cp -r "$TMP/sg/schema" "$TMP/sg/measures" "$DEST/"
cp "$TMP/sg/conformance/examples/l3-superoptix-hardened-ship.yaml" "$DEST/" 2>/dev/null || true
echo "Vendored SuperGauge checker at $REV into $DEST; update PIN.md and SUPERGAUGE_CHECKER_REV."
