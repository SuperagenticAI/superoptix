# A2A Introduction

Agent2Agent, or A2A, is an interoperability protocol for agents.

In SuperOptiX, A2A is the protocol layer used to:

- expose SuperOptiX-built agents as A2A-compatible servers
- discover and call remote A2A agents
- keep framework-specific runtime details behind SuperOptiX-owned adapters

This matters because SuperOptiX already supports multiple agent frameworks. A2A gives those agents a common interoperability surface without forcing them into the same framework runtime.

## A2A v1 Changes In SuperOptiX

In plain terms, SuperOptiX now speaks the newer A2A v1 protocol shape.

That means:

- SuperOptiX agents can introduce themselves using the newer v1 Agent Card format
- SuperOptiX can call other A2A agents using the newer v1 method names
- task states and message roles now follow the v1 naming model
- the CLI and demo flows use the same v1 A2A bridge

So if you are using A2A with SuperOptiX today, you are using the core A2A v1 interoperability model, not the older 0.3-style protocol shape.

## What A2A Means in SuperOptiX

SuperOptiX treats A2A as a protocol, not as a framework.

That means:

- DSPy, Pydantic AI, OpenAI SDK, CrewAI, Google ADK, DeepAgents, and other frameworks remain separate build targets
- A2A sits above them as a communication and exposure layer
- the A2A bridge talks to a framework-neutral runtime contract in `superoptix/runtime/`

Conceptually:

```mermaid
graph TD
    A[SuperSpec Playbook] --> B[Framework Compile Path]
    B --> C1[DSPy Runtime]
    B --> C2[Pydantic AI Runtime]
    B --> C3[Other Framework Runtimes]
    C1 --> D[SuperOptiX Runtime Adapter]
    C2 --> D
    C3 --> D
    D --> E[A2A Server Bridge]
    F[Remote A2A Client] --> E
```

## Why Use A2A

Use A2A when you want:

- one agent to call another agent as an agent, not just as a raw tool
- framework-neutral exposure of SuperOptiX agents
- remote capability discovery through Agent Cards
- blocking or task-based agent-to-agent workflows

Use MCP when you want:

- tool discovery
- context/tool server integration
- protocol-driven tool use

MCP and A2A are complementary:

- MCP: agent to tool/context server
- A2A: agent to agent

## Design Rules in This Repo

Runtime A2A support in SuperOptiX follows these rules:

- no vendored A2A implementation
- A2A support comes through the external dependency `a2a-sdk`
- SuperOptiX owns the protocol adapter layer on top of that dependency boundary

See the decision record:

- [ADR 0001: A2A Integration Boundary](../adrs/0001-a2a-integration-boundary.md)

## A2A v1 Protocol And SDK Version

SuperOptiX now targets the A2A `1.0` protocol at the adapter boundary.

Official A2A v1 release announcement:

- [Announcing A2A 1.0](https://a2a-protocol.org/latest/announcing-1.0/)

The optional dependency remains pinned to:

```text
a2a-sdk[http-server]==0.3.25
```

This split exists because the published Python SDK release line still lags the latest protocol spec, so SuperOptiX normalizes protocol `1.0` shapes in its own adapter layer.

This is exposed through the optional package extra:

```bash
pip install "superoptix[a2a]"
```

## Current SuperOptiX A2A Scope

Available now:

- native A2A integration package in `superoptix/protocols/a2a/`
- framework-neutral runtime layer in `superoptix/runtime/`
- A2A Agent Card builder
- A2A server bootstrap for SuperOptiX pipelines
- A2A client wrapper for calling remote agents
- packaged DSPy demo
- packaged Pydantic AI demo

Not complete yet:

- richer Agent Card security and signatures
- full cross-framework demo with DSPy + Pydantic AI + CrewAI + ADK talking to each other
- advanced streaming and push notification demo flows

## Main Components

Relevant modules:

- `superoptix/runtime/base.py`
- `superoptix/runtime/registry.py`
- `superoptix/runtime/adapters/pipeline.py`
- `superoptix/protocols/a2a/card_builder.py`
- `superoptix/protocols/a2a/mappers.py`
- `superoptix/protocols/a2a/server.py`
- `superoptix/protocols/a2a/client.py`

## Next Reading

- [A2A Guide](a2a-guide.md)
- [A2A Demo Guide](a2a-demo-guide.md)
