# Adapting an existing agent to A2A

`super a2a adapt` takes an agent that already exists in your codebase and
produces an A2A 1.0 Agent Card and a server for it. Your agent is not modified,
imported into a SuperOptiX project, or rewritten as a SuperSpec playbook.

Use this when you have agents built before you adopted SuperOptiX and want them
reachable by other agents, inside or outside your organisation.

## Quick start

```bash
super a2a adapt --entrypoint mycrew:crew --framework crewai
```

The command imports `mycrew`, reads the `crew` attribute, derives the skills a
calling agent would route on, and writes three files to `./a2a`:

| File | Purpose |
| --- | --- |
| `agent-card.json` | A2A 1.0 Agent Card, advertising both the 1.0 and 0.3 spec lines |
| `a2a_server.py` | ASGI application that imports your entrypoint and serves it |
| `agentspec.json` | The generated intermediate representation (see below) |

Run the server with any ASGI host:

```bash
uvicorn a2a.a2a_server:app --port 8000
curl localhost:8000/.well-known/agent-card.json
```

## Options

| Flag | Default | Meaning |
| --- | --- | --- |
| `--entrypoint` | required | Where your agent lives, as `module:attribute` |
| `--framework` | detected | Framework of the agent |
| `--out` | `a2a` | Directory for the generated files |
| `--url` | `http://127.0.0.1:8000` | Public URL the card advertises |
| `--project-root` | current directory | Directory to import your agent from |

`--framework` is optional. When omitted, each registered introspector is asked
whether it recognises the loaded object. Pass it explicitly if detection fails
or if you have wrapped the agent in something unusual.

`--url` must match the address the agent is actually reachable at. A card whose
advertised URL does not resolve is worse than no card: other agents discover it,
call it, and record the failure against your agent.

## Entrypoints

The entrypoint is `module:attribute`, resolved against `--project-root`.
Attribute paths may be nested:

```bash
--entrypoint mycrew:crew
--entrypoint app.agents.support:triage_crew
--entrypoint app.rag:program
```

A zero-argument factory function is called, so both of these work:

```python
crew = Crew(agents=[...], tasks=[...])       # --entrypoint mymod:crew

def build_crew():                             # --entrypoint mymod:build_crew
    return Crew(agents=[...], tasks=[...])
```

Agent objects are never called during introspection, even when they are
callable. A DSPy module accepts `**kwargs` and would run if invoked, which would
require a configured language model to read a card. Reading an agent's shape has
no side effects.

## Supported frameworks

Skills come from whichever part of each framework names a capability.

| Framework | `--framework` | Skills derived from |
| --- | --- | --- |
| CrewAI | `crewai` | Crew tasks; agent roles when there are no tasks |
| DSPy | `dspy` | Signature instructions, input and output fields |
| OpenAI Agents SDK | `openai` | Tool names and descriptions |
| Pydantic AI | `pydantic-ai` | Function toolset entries |
| Google ADK | `google-adk` | Agent description, plus sub-agents |
| Microsoft Agent Framework | `microsoft` | Agent description and instructions |
| Claude Agent SDK | `claude-sdk` | `AgentDefinition.description`, or `ClaudeAgentOptions.system_prompt` |
| DeepAgents | `deepagents` | Subagent names and descriptions |

### Notes per framework

**CrewAI.** A task is the closest thing CrewAI has to a named capability, so
tasks become skills and `expected_output` is appended to the description. A crew
with no tasks falls back to its agents' roles and goals.

**DSPy.** A signature already names its inputs and outputs with per-field
descriptions, and its docstring is the task instruction. The generated
description states the instruction, then what the skill takes and returns.
DSPy's own `reasoning` and `rationale` fields are excluded; they are internal
scratchpads rather than part of the declared interface.

**Google ADK.** The card uses `description`, not `instruction`. An instruction
steers the model ("Be concise"); a description tells other agents what the agent
does. Sub-agents are added as separate skills, since they are individually
routable.

**DeepAgents.** `create_deep_agent` returns a compiled LangGraph, which says
little about capability on its own. Subagents are the readable surface. A graph
whose subagents carry no descriptions cannot be adapted, and the command says
so rather than emitting an empty card.

## The generated intermediate representation

`agentspec.json` is a SuperSpec, generated rather than authored:

```json
{
  "apiVersion": "agent/v1",
  "kind": "AgentSpec",
  "metadata": {
    "name": "support-crew",
    "framework": "crewai",
    "entrypoint": "mycrew:crew"
  },
  "spec": { "skills": [ ... ] },
  "optimizable": ["skills[].description", "skills[].examples"]
}
```

It exists for three reasons.

Each framework needs one introspector and shares every emitter, so adding a
framework does not multiply the work of producing cards, servers or version
bridging.

It is inspectable. If a skill was read badly, you can see exactly how before
anything is published, and correct it.

The `optimizable` field records which parts of the card may be rewritten by
optimisation. Skill descriptions and examples are the routing interface other
agents read. Identity and protocol fields are not optimisable, so an optimiser
cannot change what your agent claims to be. See
[Routing quality](a2a-routing.md).

## What the generated server does

`a2a_server.py` imports your entrypoint lazily on first request and bridges A2A
messages onto each framework's own entry API: `Crew.kickoff` for CrewAI, the
signature's first input field for DSPy, `Runner.run` for the OpenAI Agents SDK,
`InMemoryRunner` for Google ADK, and so on.

Multi-field results are labelled rather than serialised raw. A DSPy prediction
returning `category` and `reply` is rendered as two labelled lines; a single
output field is returned on its own. Internal fields are dropped.

The file is generated once and then belongs to you. Edit it, commit it, deploy
it. Re-running `adapt` overwrites it, so move custom logic elsewhere or write to
a different `--out`.

## Verifying an adapted agent

Adapted agents are conformance-tested with the same suite as SuperOptiX's own
published endpoint. See [A2A conformance](a2a-conformance.md) for running the
Technology Compatibility Kit against one.

## Limitations

Introspection reads structure, not behaviour. A skill described vaguely in the
source produces a vaguely described skill in the card. Measuring that is what
[Routing quality](a2a-routing.md) is for.

Streaming is single-turn: the generated runtime yields one result rather than
incremental output. Frameworks that stream natively are not yet mapped onto A2A
streaming events.

Push notifications are not supported. The card declares
`pushNotifications: false`, and the configuration methods return
`PushNotificationNotSupportedError` rather than a 404.
