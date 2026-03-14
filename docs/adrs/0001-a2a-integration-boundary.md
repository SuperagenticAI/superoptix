# ADR 0001: A2A Integration Boundary

## Status

Accepted on March 14, 2026.

## Context

SuperOptiX keeps local A2A protocol and SDK source trees under `reference/` for design review and implementation planning. Those files are useful for understanding the protocol surface, but they must not become product code dependencies.

At the same time, SuperOptiX wants to expose agents built across multiple frameworks through a single A2A-compatible interface, without coupling the A2A layer to framework internals.

## Decision

1. `reference/` is documentation-only.
   - No runtime imports from `reference/`
   - No copying or vendoring code from `reference/`
   - No packaging or build-time dependency on files under `reference/`

2. A2A support is delivered only through an external dependency.
   - MVP dependency: `a2a-sdk[http-server]==0.3.25`
   - SuperOptiX exposes this through the optional extra `superoptix[a2a]`

3. SuperOptiX owns the integration layer.
   - The A2A bridge must live in SuperOptiX code
   - The bridge talks only to a SuperOptiX-owned runtime contract
   - Framework-specific details stay in runtime adapters, not in the A2A protocol layer

4. MVP compatibility target is A2A SDK `0.3.25`.
   - The local protocol reference includes newer protocol material, but the supported SDK surface for MVP is the Python SDK release `0.3.25`
   - Any future move to protocol `1.x` requires an explicit compatibility review and versioned migration plan

## Consequences

- SuperOptiX can evolve its runtime layer without binding itself to SDK internals
- A2A remains an optional integration, not a vendored subsystem
- The repo has an explicit rule preventing accidental imports or copy-paste from `reference/`
- Protocol version upgrades become intentional and reviewable
