# ADR 0003: OpenAI Harness + Sandbox Adoption (Main SuperOptiX)

## Status

Accepted - April 15, 2026

## Context

Main SuperOptiX already supports OpenAI Agents SDK pipelines and optional RLM orchestration.
OpenAI Agents SDK introduced a production runtime split (`harness + sandbox`) with `SandboxAgent`,
manifest staging, and sandbox run config. This aligns with SuperOptiX's optimization-first model
while reducing custom runtime glue code.

## Decision

Adopt sandbox support in the **main** OpenAI framework path using official SDK APIs from
`openai-agents>=0.14.0`, without importing code from local protocol snapshots.

## Scope Implemented

1. SuperSpec additions:
- `spec.openai_agent.sandbox.enabled`
- `spec.openai_agent.sandbox.client` (`unix_local` or `docker`)
- `spec.openai_agent.sandbox.docker_image`
- `spec.openai_agent.sandbox.workflow_name`
- `spec.openai_agent.sandbox.manifest` (`root`, `local_dirs`, `local_files`, `git_repos`)

2. Runtime:
- OpenAI runner helpers build `SandboxAgent` when sandbox is enabled.
- Runner helpers build `RunConfig(sandbox=SandboxRunConfig(...))`.
- Non-sandbox and low-version fallback remains supported with warnings.

3. Templates:
- OpenAI minimal/optimized templates use sandbox-aware helper functions.

4. Dependency floor:
- `openai-agents>=0.14.0` in OpenAI-related extras.

## Best Path Forward (Phase 2+)

1. Durable resume integration:
- Persist and reuse sandbox resume state across `run/serve/optimize`.
- Add explicit resume hooks in runtime and CLI entrypoints.

2. Partner clients abstraction:
- Add provider adapters for Cloudflare, E2B, Modal, Daytona, etc.
- Keep a shared SuperOptiX sandbox client interface to avoid framework lock-in.

3. Security policy layer:
- Add policy controls for tool approvals, mount permissions, and secret boundaries.
- Expose defaults in SuperSpec for enterprise-safe settings.

4. Evaluation surface:
- Add BDD/eval cases for long-running sandbox jobs, crash/restart, and recovery behavior.
- Track durability metrics in observability traces.

## Consequences

- OpenAI path in main SuperOptiX now supports production-style sandbox execution.
- Existing OpenAI agents remain backward-compatible when sandbox is disabled.
- Further scalability and durability work should happen at runtime/CLI orchestration layers.
