# A2A Demo Guide

This page shows how to run the current A2A demos in SuperOptiX.

## Demo Goals

The current demo proves:

1. a DSPy-style agent can be exposed over A2A
2. a Pydantic AI agent can be exposed over A2A
3. the SuperOptiX A2A client wrapper can call either agent by URL

It does not yet prove:

- full multi-framework communication across DSPy, Pydantic AI, CrewAI, and Google ADK
- CLI-based A2A serving

## Option 1: Run the Packaged Demo Modules

This is the best path for users who installed SuperOptiX as a package.

### Install

```bash
pip install "superoptix[a2a,frameworks-pydantic-ai]"
```

### Start the DSPy A2A demo server

```bash
python -m superoptix.demos.a2a.dspy_server_demo --port 8101
```

Endpoints:

```text
http://127.0.0.1:8101/.well-known/agent-card.json
http://127.0.0.1:8101/a2a/jsonrpc
```

### Start the Pydantic AI A2A demo server

```bash
python -m superoptix.demos.a2a.pydantic_ai_server_demo --port 8102
```

Endpoints:

```text
http://127.0.0.1:8102/.well-known/agent-card.json
http://127.0.0.1:8102/a2a/jsonrpc
```

The Pydantic AI demo uses `pydantic_ai.models.test.TestModel`, so it does not require model API keys.

### Call the DSPy demo

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

### Call the Pydantic AI demo

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

## Option 2: Pull the Demo Playbooks Into Your Project

If you want the demo playbooks inside a normal SuperOptiX project:

```bash
super init a2a-demo
cd a2a-demo
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
```

Then compile them like normal agents:

```bash
super agent compile a2a-dspy-demo
super agent compile a2a-pydantic-demo --framework pydantic-ai
```

This gives you local playbooks you can inspect and customize.

## Source Checkout Example Scripts

If you are working from the source tree, the same demos also exist under:

- `examples/a2a/dspy_server_demo.py`
- `examples/a2a/pydantic_ai_server_demo.py`
- `examples/a2a/call_remote_a2a_agent.py`

Those are useful for development inside the repository, but package users should prefer the `python -m superoptix.demos.a2a...` form.

## Recommended Terminal Layout

Terminal 1:

```bash
python -m superoptix.demos.a2a.dspy_server_demo --port 8101
```

Terminal 2:

```bash
python -m superoptix.demos.a2a.pydantic_ai_server_demo --port 8102
```

Terminal 3:

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Terminal 4:

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

## Current Limitations

Current demo limitations:

- no CrewAI A2A demo yet
- no Google ADK A2A demo yet
- no single orchestrator demo that routes work among multiple framework agents
- no dedicated serve CLI command yet

## Next Demo Milestone

The next meaningful A2A demo should add:

1. DSPy agent
2. Pydantic AI agent
3. CrewAI agent
4. Google ADK agent
5. one orchestrator that discovers all four Agent Cards and delegates tasks between them

That would be the first complete cross-framework A2A demo for SuperOptiX.

