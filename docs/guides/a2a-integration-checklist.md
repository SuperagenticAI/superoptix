# A2A Integration Checklist

This page maps the A2A protocol and Python SDK surfaces to SuperOptiX integration points.

It is based on analysis of the vendored material under `reference/`, which is treated as documentation only. SuperOptiX must integrate A2A through the declared external dependency, not by importing or copying code from `reference/`.

## Scope

Current implementation target:

- A2A Python SDK: `a2a-sdk[http-server]==0.3.25`
- SuperOptiX A2A dependency boundary: external SDK only

Reference sources reviewed:

- `reference/A2A-main/docs/specification.md`
- `reference/A2A-main/docs/whats-new-v1.md`
- `reference/a2a-python-main/src/a2a/client/*`
- `reference/a2a-python-main/src/a2a/server/*`
- `reference/a2a-python-main/src/a2a/types.py`

## Status Legend

- `done`: implemented and wired into SuperOptiX
- `partial`: initial support exists, but important protocol surfaces are still missing
- `missing`: not implemented yet

## Integration Matrix

| Area | Status | Current SuperOptiX Integration | Gap / Next Work |
| --- | --- | --- | --- |
| A2A dependency boundary | `done` | ADR and packaging pin the integration to external `a2a-sdk[http-server]==0.3.25` | Keep this boundary enforced during future work |
| Neutral protocol config | `done` | `spec.protocols[]` exists and legacy Agenspy config is translated | Keep deprecating old Agenspy terminology |
| Framework-neutral runtime layer | `partial` | `AgentRuntime` provides `invoke`, `metadata`, `capabilities` | Add `stream`, `cancel`, and task-aware context methods |
| Runtime adapter registry | `done` | Runtime registry exists and is independent of A2A | Add more concrete framework adapters |
| Compiled pipeline runtime adapter | `done` | Compiled pipeline wrapper works as the first runtime bridge | Keep as generic fallback |
| Dedicated DSPy runtime adapter | `missing` | No DSPy-specific runtime adapter yet | Add a DSPy adapter if streaming/cancel need DSPy-specific behavior |
| Dedicated Pydantic AI runtime adapter | `missing` | Demo exists, but not a dedicated runtime adapter layer | Add framework-specific adapter |
| Dedicated CrewAI runtime adapter | `missing` | None | Add adapter |
| Dedicated Google ADK runtime adapter | `missing` | None | Add adapter |
| Dedicated Microsoft runtime adapter | `missing` | None | Add adapter |
| Dedicated DeepAgents runtime adapter | `missing` | None | Add adapter |
| Inbound A2A server bridge | `partial` | SuperOptiX can expose a pipeline through `create_a2a_fastapi_app` | Server wiring is MVP only and needs more SDK hooks exposed |
| SDK `AgentExecutor` bridge | `partial` | `SuperOptiXA2AExecutor` maps blocking runtime calls into task updates | No runtime-native streaming, resume, or real cancellation |
| Task persistence | `partial` | Uses in-memory task store | Expose persistent task-store options |
| Request context propagation | `partial` | Basic message text extraction exists | Pass richer task, context, metadata, and tenant info into runtimes |
| Streaming task updates | `partial` | Status updates are emitted through SDK event queue | No artifact streaming or runtime-native stream support yet |
| Cancel task | `partial` | A cancel path exists in executor | Runtime contract does not yet support real cancellation |
| Resubscribe / task resume | `missing` | No SuperOptiX wrapper around this yet | Add support through runtime and server bridge |
| Push notification config | `missing` | Not exposed in SuperOptiX bridge | Wire SDK push config store and sender into server setup |
| Authenticated extended card | `missing` | Agent cards always declare this as false | Add optional extended-card support |
| Agent Card generation | `partial` | Name, description, skills, capabilities, provider, JSON-RPC interface are built | Add security, signatures, docs URL, icon URL, extensions, richer interfaces |
| Card security declarations | `missing` | No `security` or `security_schemes` emission | Map auth config into card fields |
| Card signature support | `missing` | No signature generation or verification policies | Add signing and validation hooks |
| Outbound A2A client connect/discovery | `done` | Connects to remote card URL and fetches card | Expand configuration surface |
| Outbound send message | `done` | Sends a message through SDK and captures returned events | Improve result parsing and task-aware orchestration |
| Outbound get task | `missing` | Not wrapped yet | Add SDK `get_task` support |
| Outbound cancel task | `missing` | Not wrapped yet | Add SDK `cancel_task` support |
| Outbound resubscribe | `missing` | Not wrapped yet | Add SDK `resubscribe` support |
| Outbound push callback config | `missing` | Not wrapped yet | Add `set_task_callback` and `get_task_callback` support |
| Client transport negotiation | `partial` | SDK factory handles transport negotiation internally | Expose client transport preferences in SuperSpec and CLI |
| Client middleware / auth interceptors | `missing` | No SuperOptiX API for SDK middleware yet | Add auth/interceptor configuration |
| Extensions negotiation | `missing` | No extension support surfaced in client or card builder | Add extension declaration and opt-in configuration |
| Observability / tracing | `missing` | No bridge-level A2A telemetry yet | Trace task ID, context ID, remote URL, skill, latency, terminal state |
| CLI serve flow | `missing` | No `super agent serve --protocol a2a` yet | Add packaged serve command |
| CLI card inspection | `missing` | No `super agent inspect-card` yet | Add card inspection command |
| Packaged demos | `done` | DSPy and Pydantic AI demos exist as packaged modules | Add more frameworks and orchestrated demo |
| Pullable A2A demos | `done` | `super agent pull` supports A2A DSPy and Pydantic demos | Add more demo aliases as coverage expands |
| Cross-framework A2A demo | `missing` | No DSPy + Pydantic AI + CrewAI + ADK interop demo yet | Build a single orchestrated multi-agent demo |
| Spec v1 migration boundary | `partial` | Current implementation is consciously aligned to SDK `0.3.25` | Add explicit compatibility layer for v1 changes |

## Current SuperOptiX Integration Points

These are the main places where A2A is already attached to the product:

- `superoptix/runtime/base.py`
- `superoptix/runtime/registry.py`
- `superoptix/runtime/adapters/pipeline.py`
- `superoptix/protocols/config.py`
- `superoptix/protocols/a2a/client.py`
- `superoptix/protocols/a2a/server.py`
- `superoptix/protocols/a2a/card_builder.py`
- `superoptix/protocols/a2a/mappers.py`
- `superoptix/protocols/registry.py`
- `superoptix/cli/commands/agent.py`
- `superoptix/demos/a2a/*`

## SDK / Spec Surfaces We Should Cover

From the A2A Python SDK and spec, these are the main surfaces SuperOptiX should explicitly map:

### Discovery and identity

- public Agent Card
- optional authenticated extended Agent Card
- skills and capabilities
- transport interfaces
- signatures and security declarations

### Inbound server behavior

- send message
- send streaming message
- get task
- cancel task
- resubscribe to task
- optional push notification configuration
- task persistence
- task history

### Outbound client behavior

- card resolution from base URL
- transport negotiation
- send message
- get task
- cancel task
- resubscribe
- client middleware and auth
- extension opt-in

### Product integration

- playbook schema for protocol config
- runtime bridge for every supported framework
- CLI serve flow
- CLI inspect/debug flow
- observability and tracing
- docs and demos

## Recommended Delivery Order

1. Expand `AgentRuntime` to support `cancel` and `stream`.
2. Add real framework adapters for DSPy and Pydantic AI.
3. Add `super agent serve --protocol a2a`.
4. Expose persistent task-store and request-context hooks in the server bridge.
5. Upgrade the A2A client wrapper with `get_task`, `cancel_task`, and `resubscribe`.
6. Add richer Agent Card support: security, extensions, signatures, extended card.
7. Add observability at the SuperOptiX bridge layer.
8. Build the multi-framework interop demo.
9. Add a v1 compatibility adapter once the SDK support story is ready.

## Immediate Acceptance Bar

The A2A integration should not be considered complete until all of the following are true:

- no SuperOptiX product code imports from `reference/`
- A2A support works only through declared external dependencies
- inbound A2A serving works from the CLI
- outbound A2A client supports task follow-up operations, not just initial send
- at least one DSPy agent and one non-DSPy agent are servable over A2A
- a multi-framework A2A interop demo exists
- A2A bridge telemetry is visible in SuperOptiX observability

## Version Note

The current SuperOptiX integration is built around the pinned Python SDK `0.3.25`.

The A2A protocol reference in `reference/A2A-main` is already at `1.0.0`, and that release introduces breaking changes around:

- operation names
- event payload shapes
- Agent Card structure
- per-interface protocol versioning
- task listing and multi-tenancy

SuperOptiX should therefore keep the A2A layer behind a compatibility boundary, so the runtime bridge, CLI, and playbook schema do not need to be redesigned when the product upgrades from the `0.3.x` SDK line to the `1.0` protocol model.
