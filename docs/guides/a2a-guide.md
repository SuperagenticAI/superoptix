# A2A Guide

This guide explains how A2A support works in SuperOptiX and how to use it today.

## Installation

Install the A2A extra:

```bash
pip install "superoptix[a2a]"
```

If you want to run the packaged Pydantic AI A2A demo too:

```bash
pip install "superoptix[a2a,frameworks-pydantic-ai]"
```

## A2A in the Architecture

SuperOptiX splits A2A into two sides:

1. Inbound A2A
   SuperOptiX exposes a local agent or pipeline as an A2A server.
2. Outbound A2A
   SuperOptiX acts as an A2A client and calls a remote A2A agent.

## Inbound A2A: Exposing a SuperOptiX Agent

Inbound A2A uses:

- a SuperOptiX pipeline or runtime adapter
- the framework-neutral runtime contract
- the A2A server bridge
- the external `a2a-sdk`

The bridge is created through:

- `superoptix.protocols.a2a.create_a2a_fastapi_app`

At a high level:

```python
from superoptix.protocols.a2a import create_a2a_fastapi_app

app = create_a2a_fastapi_app(
    pipeline=my_pipeline,
    agent_url="http://127.0.0.1:8101",
)
```

What the bridge does:

- reads metadata/spec from the runtime adapter
- builds an Agent Card
- maps incoming A2A messages into runtime inputs
- executes the runtime
- converts runtime output back into A2A task/message responses

## Outbound A2A: Calling a Remote Agent

Outbound A2A uses:

- `superoptix.protocols.a2a.A2AClient`

Typical flow:

1. connect to the remote agent URL
2. fetch the Agent Card
3. inspect capabilities and skills
4. send a blocking message
5. consume the response

Basic example:

```python
from superoptix.protocols.a2a import A2AClient

client = A2AClient(agent_url="http://127.0.0.1:8101")

if client.connect():
    print(client.get_capabilities())
    result = client._handle_request(query="Summarize A2A in one paragraph.")
    print(result.response)
```

## Runtime Layer

The A2A layer does not call framework internals directly.

Instead, it depends on the runtime contract in:

- `superoptix/runtime/base.py`

Current packaged adapter:

- `CompiledPipelineRuntimeAdapter`

This gives A2A a stable surface:

- `invoke(inputs, context=None)`
- `metadata()`
- `capabilities()`

That separation is what allows A2A support to scale across multiple frameworks.

## Current Demo Support

Current packaged demos:

- DSPy A2A demo
- Pydantic AI A2A demo

Current pullable demo playbooks:

- `a2a-dspy-demo`
- `a2a-pydantic-demo`

Current non-demo status:

- the A2A layer is available in code
- there is not yet a dedicated `super agent serve --protocol a2a` CLI command

## Pullable Demo Agents

If you want the demo playbooks inside a SuperOptiX project:

```bash
super init a2a-demo
cd a2a-demo
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
```

Then inspect or compile them:

```bash
super agent compile a2a-dspy-demo
super agent compile a2a-pydantic-demo --framework pydantic-ai
```

## Protocol Config

SuperOptiX is moving away from older Agenspy-named protocol config.

Use the neutral protocol-first shape:

```yaml
spec:
  tool_backend: protocols
  protocols:
    - type: mcp
      url: mcp://localhost:8080/github
    - type: a2a
      url: https://planner.example.com
```

Compatibility notes:

- `tool_backend: agenspy` is treated as a legacy alias
- `mcp_servers` is still accepted as legacy MCP-only config
- new playbooks should prefer `protocols`

## What Exists Today vs Planned

Exists today:

- A2A bridge package
- packaged demos
- pullable A2A demo playbooks
- runtime contract
- integration checklist and gap map

Planned next:

- CLI command for serving agents over A2A
- more framework runtime adapters
- multi-agent cross-framework A2A demo
- richer observability around A2A task execution

The current implementation status is tracked in:

- `docs/guides/a2a-integration-checklist.md`

## Troubleshooting

If `import a2a` fails:

```bash
pip install "superoptix[a2a]"
```

If the Pydantic AI demo import fails:

```bash
pip install "superoptix[frameworks-pydantic-ai]"
```

If you want both:

```bash
pip install "superoptix[a2a,frameworks-pydantic-ai]"
```

If the server starts but client calls fail:

- confirm the `agent_url` matches the host and port being served
- confirm the server is reachable at `/.well-known/agent-card.json`
- confirm the A2A extra is installed in the same environment
