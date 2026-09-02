# A2A Integration Checklist

This page maps the A2A protocol and Python SDK surfaces to SuperOptiX integration points.

It is based on analysis of the official A2A protocol and Python SDK materials. SuperOptiX integrates A2A through declared external dependencies, not vendored protocol source code.

## Scope

Current implementation target:

- A2A protocol target: `1.0`
- Optional extra: `superoptix[a2a]`, which installs FastAPI, uvicorn, and sse-starlette. The `a2a-sdk` package is not used.
- SuperOptiX A2A dependency boundary: protocol implemented directly over FastAPI

Official sources reviewed:

- A2A specification
- A2A v1 release notes
- A2A Python SDK client surface
- A2A Python SDK server surface
- A2A Python SDK type models

## Status Legend

- `done`: implemented and wired into SuperOptiX
- `partial`: initial support exists, but important protocol surfaces are still missing
- `missing`: not implemented yet

## Integration Matrix

| Area | Status | Current SuperOptiX Integration | Gap / Next Work |
| --- | --- | --- | --- |
| A2A dependency boundary | `done` | ADR and packaging keep A2A behind an external dependency boundary | Keep this boundary enforced during future work |
| Neutral protocol config | `done` | `spec.protocols[]` exists and legacy Agenspy config is translated | Keep deprecating old Agenspy terminology |
| Framework-neutral runtime layer | `done` | `AgentRuntime` now provides `invoke`, `stream`, `cancel`, `metadata`, `capabilities`, plus structured runtime context | Keep the contract stable as more frameworks adopt it |
| Runtime adapter registry | `done` | Runtime registry exists and is independent of A2A | Add more concrete framework adapters |
| Compiled pipeline runtime adapter | `done` | Compiled pipeline wrapper works as the first runtime bridge | Keep as generic fallback |
| Dedicated DSPy runtime adapter | `done` | DSPy runtime adapter is registered and selected by the A2A serve flow | Expand once DSPy-native streaming/cancel semantics are added |
| Dedicated Pydantic AI runtime adapter | `done` | Pydantic AI runtime adapter is registered and selected by the A2A serve flow | Expand if deeper Pydantic AI streaming integration is needed |
| Dedicated CrewAI runtime adapter | `done` | CrewAI runtime adapter is registered and selected by the A2A serve flow | Expand if CrewAI-specific streaming/cancel behavior needs custom handling |
| Dedicated Google ADK runtime adapter | `done` | Google ADK runtime adapter is registered and selected by the A2A serve flow | Expand if ADK-specific task/session features need custom handling |
| Dedicated Microsoft runtime adapter | `missing` | None | Add adapter |
| Dedicated DeepAgents runtime adapter | `missing` | None | Add adapter |
| Inbound A2A server bridge | `partial` | SuperOptiX exposes A2A `1.0` card, REST, and JSON-RPC endpoints through `create_a2a_fastapi_app` | Task persistence, richer artifacts, and multi-tenant features are still missing |
| Runtime execution bridge | `partial` | The server bridge passes runtime context and supports blocking, background, cancel, and streaming execution | Resume and richer task artifact streaming are still missing |
| Task persistence | `partial` | Uses in-memory task store | Expose persistent task-store options |
| Request context propagation | `partial` | Basic message text extraction exists | Pass richer task, context, metadata, and tenant info into runtimes |
| Streaming task updates | `partial` | Status updates are emitted from the SuperOptiX bridge and can come from runtime `stream(...)` hooks | No artifact streaming mapper yet |
| Cancel task | `partial` | Runtime `cancel(...)` hook exists and is called by the bridge | Most frameworks still do not implement true cooperative cancellation |
| Resubscribe / task resume | `partial` | `SubscribeToTask` exists for non-terminal in-flight tasks | Persisted resume and richer replay behavior are still missing |
| Push notification config | `missing` | Not exposed in SuperOptiX bridge | Wire SDK push config store and sender into server setup |
| Authenticated extended card | `missing` | Agent cards currently declare `capabilities.extendedAgentCard: false` | Add optional extended-card support |
| Agent Card generation | `partial` | Name, description, skills, capabilities, provider, and v1 `supportedInterfaces[]` are built | Add security, signatures, docs URL, icon URL, extensions, richer interfaces |
| Card security declarations | `missing` | No `security` or `security_schemes` emission | Map auth config into card fields |
| Card signature support | `missing` | No signature generation or verification policies | Add signing and validation hooks |
| Outbound A2A client connect/discovery | `done` | Connects to remote card URL, fetches the well-known Agent Card, and normalizes legacy cards | Expand configuration surface |
| Outbound send message | `done` | Sends `SendMessage` over HTTP+JSON or JSON-RPC v1 bindings | Improve result parsing and task-aware orchestration |
| Outbound get task | `done` | Wraps `GetTask` | Extend result shaping if richer task rendering is needed |
| Outbound list tasks | `done` | Wraps `ListTasks` / `GET /tasks` | Add pagination helpers |
| Outbound cancel task | `done` | Wraps `CancelTask` | Improve terminal-state handling as more runtimes implement true cancellation |
| Outbound resubscribe | `done` | Wraps `SubscribeToTask` with SSE parsing | Improve event rendering once richer artifact streaming is added |
| Outbound push callback config | `missing` | Not wrapped yet | Add `set_task_callback` and `get_task_callback` support |
| Client transport negotiation | `partial` | SuperOptiX selects from `supportedInterfaces[]` with HTTP+JSON / JSON-RPC preference order | Expose client transport preferences in SuperSpec and CLI |
| Client middleware / auth interceptors | `missing` | No SuperOptiX API for SDK middleware yet | Add auth/interceptor configuration |
| Extensions negotiation | `missing` | No extension support surfaced in client or card builder | Add extension declaration and opt-in configuration |
| Observability / tracing | `missing` | No bridge-level A2A telemetry yet | Trace task ID, context ID, remote URL, skill, latency, terminal state |
| CLI serve flow | `done` | Compiled agents can be exposed with `super agent serve <name> --protocol a2a` | Expand serve flow as more framework adapters land |
| CLI card inspection | `missing` | No `super agent inspect-card` yet | Add card inspection command |
| Packaged demos | `done` | DSPy and Pydantic AI demos exist as packaged modules | Add more frameworks and orchestrated demo |
| Pullable A2A demos | `done` | `super agent pull` supports A2A DSPy and Pydantic demos | Add more demo aliases as coverage expands |
| Cross-framework A2A demo | `missing` | No DSPy + Pydantic AI + CrewAI + ADK interop demo yet | Build a single orchestrated multi-agent demo |
| Spec v1 migration boundary | `done` | SuperOptiX now emits and consumes A2A `1.0` shapes while preserving legacy-card normalization | Upgrade to an official `1.x` SDK release once available |

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
- subscribe to task
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
5. Add persistent task store and richer task replay behavior.
6. Add richer Agent Card support: security, extensions, signatures, extended card.
7. Add observability at the SuperOptiX bridge layer.
8. Build the multi-framework interop demo.
9. Upgrade to an official `1.x` SDK release once the SDK support story is ready.

## Core Support Acceptance Bar

SuperOptiX can reasonably claim core A2A support when all of the following are true:

- no vendored A2A protocol code in SuperOptiX product modules
- A2A support works only through declared external dependencies
- inbound A2A serving works from the CLI
- outbound A2A client supports task follow-up operations, not just initial send
- at least one DSPy agent and one non-DSPy agent are servable over A2A

## Advanced Completion Bar

The broader A2A integration can be considered more complete later when the following are also true:

- a multi-framework A2A interop demo exists
- A2A bridge telemetry is visible in SuperOptiX observability
- richer Agent Card security, signatures, and extensions are implemented
- persistent task storage and richer replay behavior are available

## Version Note

The current SuperOptiX integration emits and consumes the A2A `1.0` protocol model.

SuperOptiX implements the protocol directly, so there is no SDK version to
track. Both the `1.0` and `0.3` lines are served from one endpoint and selected
with the `A2A-Version` header; see [A2A conformance](a2a-conformance.md).

- operation names
- event payload shapes
- Agent Card structure
- per-interface protocol versioning
- task listing and multi-tenancy

SuperOptiX should therefore keep the A2A layer behind a compatibility boundary, so the runtime bridge, CLI, and playbook schema do not need to be redesigned when the product later upgrades from the `0.3.x` SDK line to an official `1.x` SDK release.
