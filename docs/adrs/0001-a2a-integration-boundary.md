# ADR 0001: A2A Integration Boundary

## Status

Superseded on 2026-09-02. The protocol is implemented in
`superoptix.protocols.a2a` over FastAPI. `superoptix[a2a]` installs FastAPI,
uvicorn, and sse-starlette. The `a2a-sdk` package is not a runtime dependency.

The decisions below are kept as the original record. Decision 2's MVP pin of
`a2a-sdk[http-server]==0.3.25` no longer applies.

## Context

SuperOptiX reviews the official A2A protocol and SDK materials for design and implementation planning. Those sources are useful for understanding the protocol surface, but they must not become product code dependencies.

At the same time, SuperOptiX wants to expose agents built across multiple frameworks through a single A2A-compatible interface, without coupling the A2A layer to framework internals.

## Decision

1. A2A protocol source material is reference-only for design.
   - No runtime imports from vendored protocol source trees
   - No copying or vendoring protocol implementation code
   - No packaging or build-time dependency on local protocol source snapshots

2. A2A support is delivered only through an external dependency.
   - MVP dependency: `a2a-sdk[http-server]==0.3.25`
   - SuperOptiX exposes this through the optional extra `superoptix[a2a]`

3. SuperOptiX owns the integration layer.
   - The A2A bridge must live in SuperOptiX code
   - The bridge talks only to a SuperOptiX-owned runtime contract
   - Framework-specific details stay in runtime adapters, not in the A2A protocol layer

4. SuperOptiX targets the A2A `1.0` protocol at the adapter boundary.
   - The published Python SDK dependency remains pinned at `0.3.25` until an official `1.x` SDK release is available and validated
   - SuperOptiX therefore owns the protocol-compatibility layer in its adapter code
   - Any future SDK upgrade still requires an explicit compatibility review and versioned migration plan

## Consequences

- SuperOptiX can evolve its runtime layer without binding itself to SDK internals
- A2A remains an optional integration, not a vendored subsystem
- The repo has an explicit rule preventing accidental imports or copy-paste from local protocol source snapshots
- Protocol version upgrades remain intentional and reviewable even when protocol and SDK release trains diverge
