# A2A conformance

SuperOptiX implements the A2A 1.0 wire protocol directly over FastAPI. This page
covers how that implementation is verified, how version negotiation works, and
how to test an agent you have adapted.

## Current results

Measured with the [official A2A TCK](https://github.com/a2aproject/a2a-tck)
against the conformance harness:

| Level | Compliance |
| --- | --- |
| MUST | 100% |
| SHOULD | 100% |
| MAY | 100% |

The published SuperOptiX endpoint and agents produced by
[`super a2a adapt`](a2a-adapt.md) score 86.3% MUST. The difference is not a
defect: the remaining requirements are TCK scenario hooks that a production
agent should not implement. See [The conformance harness](#the-conformance-harness).

## The live endpoint

A SuperOptiX agent runs at `a2a.superoptix.ai`, hosted on Cloud Run.

| | |
| --- | --- |
| Agent Card, published | `superoptix.ai/.well-known/agent-card.json` |
| Agent Card, served by the agent | `a2a.superoptix.ai/.well-known/agent-card.json` |
| Endpoint | `https://a2a.superoptix.ai` |

Two copies of the card is the intended arrangement rather than duplication. The
published copy is a static file on the website, so discovery answers instantly
whether or not the service is warm. The served copy confirms the running agent
agrees with what was published. The two are byte-identical.

The agent exposes two skills, both deterministic. Neither calls a model, reads
user code, nor holds a credential, which is what makes the endpoint safe to
expose and inexpensive to run.

```bash
curl -X POST https://a2a.superoptix.ai/message:send \
  -H 'content-type: application/json' \
  -d '{"message":{"role":"ROLE_USER","parts":[{"text":"Does CrewAI support A2A?"}]}}'
```

Opening `https://a2a.superoptix.ai` in a browser returns a page describing the
endpoint rather than an error. The address appears in the Agent Card and in
registry listings, so people follow it, and a bare 404 reads as a broken
service.

### Hosting

The endpoint moved from Render to Cloud Run in August 2026. The reason was cold
start rather than cost:

| | Cold start | Warm |
| --- | --- | --- |
| Render free tier | 42.5 s | 0.41 s |
| Cloud Run, scale to zero | 1.7 s | 0.06 s |

A2A clients apply timeouts. A registry fetching a card with a 30 second timeout
records a 42.5 second endpoint as unreachable rather than slow, so the free tier
on Render was not viable for an agent meant to be discovered. Cloud Run keeps the
image staged and starts a container on demand, which brings the same
idle-to-first-request path inside those timeouts.

`deploy/a2a/README.md` covers the deployment and the migration.

## Running the TCK

The TCK is a pytest suite that exercises a running agent across the JSON-RPC,
HTTP+JSON and gRPC bindings, filtered by RFC 2119 level.

```bash
git clone https://github.com/a2aproject/a2a-tck.git
cd a2a-tck
uv venv && uv pip install --python .venv/bin/python -e .
```

Start the conformance harness and point the suite at it:

```bash
uvicorn superoptix.protocols.a2a.tck_sut:app --port 8000

.venv/bin/python run_tck.py --sut-host http://127.0.0.1:8000 --level must
```

Reports land in `reports/`: `compatibility.json` for machine reading,
`compatibility.html` for review.

To test an agent you have adapted, point the same command at its server instead.

## The conformance harness

The TCK drives an agent into specific protocol states using reserved
`messageId` prefixes. `tck-input-required` must leave a task non-terminal,
`tck-complete-task` must complete it, `tck-artifact-text` must return an
artifact. Reference implementations in the A2A project do the same.

Those hooks live in a separate application,
`superoptix/protocols/a2a/tck_sut.py`, rather than in the published endpoint. A
production agent that changes behaviour based on a client-supplied identifier is
honouring untrusted input. Both applications share the same server
implementation, so conformance measured against the harness holds for the
protocol layer that adapted agents use.

## Continuous integration

`.github/workflows/a2a-conformance.yml` runs the TCK against the harness on
changes to `superoptix/protocols/**` or `superoptix/runtime/**`. It publishes
the compatibility report as a build artifact and writes the score to the job
summary.

The job enforces a floor rather than demanding a perfect score:

```yaml
env:
  MIN_MUST_COMPLIANCE: "100.0"
```

A build fails when MUST-level compliance falls below the floor. Raise the value
as gaps close; conformance can then only be maintained or improved.

## Version negotiation

One endpoint serves both spec lines. Clients select with the `A2A-Version`
request header, and `1.0` is assumed when the header is absent.

```bash
curl -H 'A2A-Version: 1.0' localhost:8000/.well-known/agent-card.json
curl -H 'A2A-Version: 0.3' localhost:8000/.well-known/agent-card.json
```

What changes between the two:

| | 1.0 | 0.3 |
| --- | --- | --- |
| Task state | `TASK_STATE_COMPLETED` | `completed` |
| Message role | `ROLE_AGENT` | `agent` |
| Part shape | Unified, fields set directly | Wrapped, tagged with `kind` |
| File part | `raw` / `url` / `filename` / `mediaType` | `file.bytes` / `file.uri` / `file.name` / `file.mimeType` |
| Card | `supportedInterfaces` | Top-level `url` and `preferredTransport` |
| JSON-RPC method names | `SendMessage` | `message/send` |

Both sets of method names reach the same handlers, so a 0.3 client does not have
to know it is talking to a 1.0 implementation:

| 0.3 | 1.0 |
| --- | --- |
| `message/send` | `SendMessage` |
| `message/stream` | `SendStreamingMessage` |
| `tasks/get` | `GetTask` |
| `tasks/list` | `ListTasks` |
| `tasks/cancel` | `CancelTask` |
| `tasks/resubscribe` | `SubscribeToTask` |
| `agent/authenticatedExtendedCard` | `GetExtendedAgentCard` |
| `tasks/pushNotificationConfig/*` | `*TaskPushNotificationConfig` |

A method outside both sets returns `-32601`.

An unrecognised version returns `VersionNotSupportedError`: `-32009` over
JSON-RPC, HTTP 400 over REST.

Both lines matter because the installed base is on 0.3. Of the eight frameworks
SuperOptiX adapts, five declare no A2A dependency, and the three that do
(CrewAI, Google ADK and Pydantic AI) are pinned below 1.0. An endpoint that speaks only
1.0 is unreachable by most agents currently deployed.

Translation is available directly:

```python
from superoptix.protocols.a2a import bridge

legacy = bridge.task_to_v03(task)
current = bridge.task_to_v1(legacy)
card = bridge.card_to_v03(agent_card)
```

## Agent Card caching

The Agent Card is fixed for the life of the process, so it is served with
validators that let a caller skip the transfer on a repeat read.

```
Cache-Control: public, max-age=3600
ETag: "5b8e694cb6e718eb2633ad7de9a2909b"
Last-Modified: Mon, 31 Aug 2026 19:40:41 GMT
Vary: A2A-Version
```

A conditional request that matches returns `304` with no body:

```bash
curl -sI localhost:8000/.well-known/agent-card.json | grep -i etag
curl -si -H 'If-None-Match: "<etag>"' localhost:8000/.well-known/agent-card.json | head -1
```

The 1.0 and 0.3 renderings of the card are different documents and carry
different entity tags, which is what the `Vary` header exists to signal. A cache
holding one will not hand it to a client that asked for the other.

`If-None-Match` follows RFC 9110: a comma separated list is accepted, `*` matches
anything, and a weak validator compares equal to its strong form.

## Error handling

A2A binds each error to a JSON-RPC code, an HTTP status and an ErrorInfo reason.
`superoptix/protocols/a2a/errors.py` holds the table.

JSON-RPC errors are returned with **HTTP 200**. The transport succeeded; the
failure is inside the envelope. Returning 4xx alongside a JSON-RPC error causes
conformant clients to treat the response as a transport failure and never read
the code.

A2A-specific errors carry a `google.rpc.ErrorInfo` entry in `error.data`, per
specification section 9.5:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Task not found",
    "data": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "domain": "a2a-protocol.org",
      "reason": "TASK_NOT_FOUND"
    }]
  }
}
```

HTTP+JSON errors use AIP-193 bodies with the same ErrorInfo in `error.details`.

## Implemented surface

| Method | Status |
| --- | --- |
| `SendMessage` | Implemented |
| `SendStreamingMessage` | Implemented, SSE |
| `GetTask` | Implemented, honours `historyLength` |
| `ListTasks` | Implemented |
| `CancelTask` | Implemented; terminal tasks return `TaskNotCancelableError` |
| `SubscribeToTask` | Implemented |
| `GetExtendedAgentCard` | Returns `ExtendedAgentCardNotConfiguredError` |
| Push notification config methods | Return `PushNotificationNotSupportedError` |

Bindings: JSON-RPC 2.0 and HTTP+JSON. gRPC is not implemented.

The JSON-RPC route is served at both `/a2a/jsonrpc` and `/a2a/jsonrpc/`. A
client that treats the interface URL as an HTTP base and posts to `/` resolves
to the trailing-slash form, and a redirect there returns an empty body that
JSON-RPC clients cannot parse.

## Known gaps

Agent Cards are unsigned. Signed cards are the 1.0 mechanism for proving a card
was issued by the domain owner. The `agent-card-review` skill on the published
endpoint reports this against SuperOptiX's own card.

gRPC is not implemented. The TCK covers it, and the requirements are skipped
rather than failed.

The Agent Payments Protocol (AP2), published alongside 1.0, is out of scope.
