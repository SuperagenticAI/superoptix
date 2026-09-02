<div align="center">
  <a href="https://superagenticai.github.io/superoptix/">
    <img src="https://raw.githubusercontent.com/SuperagenticAI/superoptix/main/docs/logo.png" alt="SuperOptiX Logo" width="260" />
  </a>
  <h1>SuperOptiX AI</h1>
  <h3><strong>Agent-to-Agent (A2A) Interoperability and Optimization Layer</strong></h3>
  <p><strong>Agent-to-agent communication, without framework lock-in.</strong></p>
  <p>Make the agents you already run callable by any other agent, and get them discovered.</p>

  <div style="margin: 20px 0;">
    <a href="https://badge.fury.io/py/superoptix">
      <img src="https://badge.fury.io/py/superoptix.svg" alt="PyPI version" />
    </a>
    <a href="LICENCE">
      <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0" />
    </a>
    <a href="https://www.python.org/downloads/">
      <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+" />
    </a>
    <img src="https://img.shields.io/badge/A2A%20TCK-0%20failures-1C6B48.svg" alt="Zero failures on the A2A TCK" />
    <img src="https://img.shields.io/badge/runtimes-8-purple.svg" alt="8 agent runtimes" />
  </div>
</div>

---

## What it does

Agents built on different frameworks cannot call each other. A2A is the protocol
that lets them, and SuperOptiX gives an agent an A2A interface without asking you
to rewrite it.

Point it at an agent you already run. SuperOptiX reads its structure, works out
the skills a calling agent would route on, and writes an Agent Card and a
conformant server. Your code is not modified.

Being reachable is only half the problem. Whether another agent chooses to call
yours depends on how its card describes it, so SuperOptiX also measures that and
improves it.

## Install

One line, on macOS, Linux and WSL. It installs [uv](https://docs.astral.sh/uv/)
if it is missing, then installs SuperOptiX into an isolated tool environment.
It never uses sudo.

```bash
curl -fsSL https://superoptix.ai/install.sh | sh
```

Extras and an exact version can be selected with environment variables:

```bash
curl -fsSL https://superoptix.ai/install.sh | SUPEROPTIX_EXTRAS=a2a sh
curl -fsSL https://superoptix.ai/install.sh | SUPEROPTIX_VERSION=0.3.2 sh
```

If you already have uv and would rather run it yourself:

```bash
uv tool install superoptix
```

To adapt or serve agents over A2A:

```bash
uv tool install superoptix --with "superoptix[a2a]"
```

To add SuperOptiX to an existing project:

```bash
uv add superoptix
```

## Adapt an existing agent

```bash
super a2a adapt --entrypoint mycrew:crew --framework crewai
```

This writes three files to `./a2a`:

| File | Contents |
|---|---|
| `agent-card.json` | A2A 1.0 Agent Card, advertising both the 1.0 and 0.3 spec lines |
| `a2a_server.py` | ASGI application that imports your agent and serves it |
| `agentspec.json` | The generated intermediate representation |

Serve it with any ASGI host:

```bash
uvicorn a2a.a2a_server:app --port 8000
curl localhost:8000/.well-known/agent-card.json
```

The framework is detected when you omit `--framework`. Use `--url` to set the
address the card advertises, and `--out` to choose the output directory.

## Supported runtimes

| Runtime | `--framework` | Skills derived from |
|---|---|---|
| DSPy | `dspy` | Signature instructions, inputs and outputs |
| CrewAI | `crewai` | Crew tasks, or agent roles when there are none |
| OpenAI Agents SDK | `openai` | Tool names and descriptions |
| Pydantic AI | `pydantic-ai` | Function toolset entries |
| Google ADK | `google-adk` | Agent description, plus sub-agents |
| Claude Agent SDK | `claude-sdk` | Agent definition or system prompt |
| DeepAgents | `deepagents` | Subagent names and descriptions |
| Microsoft Agent Framework | `microsoft` | Agent description and instructions |

Install the matching extra to work with a runtime, for example
`uv tool install superoptix --with "superoptix[frameworks-openai]"`.

CrewAI installs separately, because it requires `chromadb~=1.1.0` while the
vector store extras require `chromadb>=1.5.5`:

```bash
uv tool install superoptix --with "crewai>=1.15"
```

## Conformance

Measured against the [official A2A Technology Compatibility Kit](https://github.com/a2aproject/a2a-tck):

| Level | Passed / exercised | Not exercised |
|---|---|---|
| MUST | 73 / 73 | 21 |
| SHOULD | 7 / 7 | 4 |
| MAY | 4 / 4 | 0 |

Zero failures. Every requirement the TCK is able to exercise against the
conformance harness passes.

The TCK also prints a headline percentage, currently 77.7% at MUST. That figure
counts the 25 requirements it cannot exercise here as non-compliant. They break
down as 13 for authentication and TLS, 4 for Agent Card JWS signatures, 4 for
cross-binding equivalence, 3 for version negotiation probes and 1 for the gRPC
binding. None of them are failures, and none can be exercised until those
features exist. Authentication, card signing and a gRPC binding are not
implemented today.

Run it yourself with `super a2a adapt`, the TCK SUT harness and
`.github/workflows/a2a-conformance.yml`, which is a manual workflow that fails
on any conformance failure rather than on a percentage.

An adapted agent scores lower on the headline figure than the SuperOptiX
endpoint because the TCK drives protocol states through magic messageId
prefixes that a production agent should not honour.

A live endpoint runs at
[a2a.superoptix.ai](https://a2a.superoptix.ai/.well-known/agent-card.json), with
its Agent Card published at
[superoptix.ai/.well-known/agent-card.json](https://superoptix.ai/.well-known/agent-card.json).

## Protocol surface

All eleven A2A 1.0 methods answer. Push notification configuration and the
extended agent card return the errors the specification defines for an agent
that does not offer them.

Both the JSON-RPC 2.0 and HTTP+JSON bindings are served. One endpoint handles
A2A 1.0 and 0.3, selected with the `A2A-Version` request header, because five of
the eight supported runtimes declare no A2A dependency and the three that do sit
below 1.0.

gRPC and signed Agent Cards are not implemented.

Agents adapted by SuperOptiX keep using their MCP tools. SuperOptiX changes how
an agent is reached rather than how it works, and exposing an agent as an MCP
server is not supported.

## Discoverability

A calling agent decides whether to invoke yours by reading `skills[].description`
on your card. Those strings are the routing interface.

Four sibling skills, identical queries, differing only in how each describes
itself:

| Catalogue | Invocation | Discovery |
|---|---|---|
| Vague | 12.5% | 75% |
| Specific | 100% | 100% |

`superoptix.protocols.a2a.routing` scores this, and GEPA improves it by
rewriting the descriptions. On the vague catalogue above it raises invocation
from 12.5% to 75%.

## Compiling from a specification

SuperOptiX also compiles agents from SuperSpec, a declarative YAML format, into
native code for any supported runtime.

```bash
super agent pull developer
super agent compile developer --framework dspy
super agent run developer --framework dspy --goal "Design a migration strategy"
```

GEPA optimization is available on the compiled agent:

```bash
super agent compile developer --framework dspy --optimize
super agent optimize developer --framework dspy --auto light
```

## Documentation

- [Adapting an existing agent](https://superagenticai.github.io/superoptix/guides/a2a-adapt/)
- [A2A conformance](https://superagenticai.github.io/superoptix/guides/a2a-conformance/)
- [Routing quality](https://superagenticai.github.io/superoptix/guides/a2a-routing/)
- [Quick start](https://superagenticai.github.io/superoptix/quick-start/)
- [CLI reference](https://superagenticai.github.io/superoptix/guides/cli-complete-guide/)
- [Runtime feature matrix](https://superagenticai.github.io/superoptix/guides/framework-feature-matrix/)
- [Troubleshooting](https://superagenticai.github.io/superoptix/guides/troubleshooting-by-symptom/)

Full documentation is at
[superagenticai.github.io/superoptix](https://superagenticai.github.io/superoptix/).

## Telemetry

SuperOptiX collects anonymous usage data. Disable it with:

```bash
export SUPEROPTIX_TELEMETRY=false
```

## Links

- Website: [superoptix.ai](https://superoptix.ai)
- Package: [pypi.org/project/superoptix](https://pypi.org/project/superoptix/)
- Source: [github.com/SuperagenticAI/superoptix](https://github.com/SuperagenticAI/superoptix)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## License

Apache License 2.0. See [LICENCE](LICENCE).
