# A2A Demo Guide

This page shows how to run the current A2A demos in SuperOptiX.

These demos use the A2A `1.0` protocol shape exposed by the SuperOptiX adapter layer.
That means the demo servers publish a v1 Agent Card and support the v1 method surface such as `SendMessage`, `GetTask`, `CancelTask`, and `SubscribeToTask`.

## A2A v1 Demo Goals

The current demo proves:

1. a DSPy-style agent can be exposed over A2A
2. a Pydantic AI agent can be exposed over A2A
3. a Google ADK agent can be exposed over A2A
4. the SuperOptiX A2A client wrapper can call any of those agents by URL

It does not yet prove:

- full multi-framework communication across DSPy, Pydantic AI, CrewAI, and Google ADK
- full multi-framework orchestration through one A2A demo

## Option 1: Run the Packaged Demo Modules

This is the best path for users who installed SuperOptiX as a package.

### Prerequisites

Before you start, make sure you have:

- Python 3.11 or newer
- `pip`
- a clean shell session or virtual environment
- `GOOGLE_API_KEY` if you want to run the Google ADK demo

The packaged demo requirements are:

- DSPy demo: no model API key required
- Pydantic AI demo: no model API key required
- Google ADK demo: requires `GOOGLE_API_KEY`

### Install

```bash
pip install "superoptix[a2a,frameworks-pydantic-ai,frameworks-google]==0.2.20"
```

You can verify the install with:

```bash
python -m superoptix.cli.main version
```

Expected result:

```text
0.2.20
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

What this server is:

- a lightweight packaged DSPy-style A2A demo
- exposed through the SuperOptiX A2A server bridge
- no extra API key required for this packaged demo

Expected startup behavior:

- the process stays running
- it prints the A2A JSON-RPC URL
- you can open the Agent Card URL in a browser

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

Expected startup behavior:

- the process stays running
- it prints the A2A JSON-RPC URL
- it should behave deterministically because it uses the Pydantic AI test model

### Start the Google ADK A2A demo server

The ADK demo requires `GOOGLE_API_KEY` because it uses a real Google ADK + Gemini path.

```bash
export GOOGLE_API_KEY=your_google_api_key
python -m superoptix.demos.a2a.google_adk_server_demo --port 8103
```

Endpoints:

```text
http://127.0.0.1:8103/.well-known/agent-card.json
http://127.0.0.1:8103/a2a/jsonrpc
```

Important notes for the ADK demo:

- this is the only packaged A2A demo in the set that needs a real model API key
- if `GOOGLE_API_KEY` is missing, the demo exits with a clear runtime error
- the key must be available in the same shell where you start the ADK demo server

Expected startup behavior:

- the process stays running
- it prints the A2A JSON-RPC URL
- it will call the Google ADK + Gemini path when you send a request

### Call the DSPy demo

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Expected result:

- the client fetches the remote Agent Card
- the client sends a message to the remote agent
- you get back a response payload and task metadata

### Call the Pydantic AI demo

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

Expected result:

- the client connects successfully
- the Pydantic AI demo returns a short deterministic answer

### Call the Google ADK demo

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8103 \
  --message "Outline an enterprise rollout plan for A2A support."
```

Expected result:

- the client connects successfully
- the ADK demo returns a Gemini-backed answer
- if the key is invalid or missing, this is the first place you will usually see the failure

### End-To-End Checklist

If the packaged demo flow is working correctly, all of the following should be true:

- `python -m superoptix.cli.main version` prints `0.2.20`
- the DSPy server starts on `8101`
- the Pydantic AI server starts on `8102`
- the Google ADK server starts on `8103`
- each server exposes `/.well-known/agent-card.json`
- the client script can call each server by URL

### Common Setup Problems

- `No module named superoptix`
  The package is not installed in the current environment.

- `GOOGLE_API_KEY is required for the Google ADK A2A demo`
  Export the key before starting `google_adk_server_demo`.

- `Address already in use`
  Change the port with `--port`.

- `Connection refused`
  The target demo server is not running yet, or the client URL/port is wrong.

## Option 2: Pull the Demo Playbooks Into Your Project

If you want the demo playbooks inside a normal SuperOptiX project:

```bash
super init a2a-demo
cd a2a-demo
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
super agent pull a2a-adk-demo
```

Then compile them like normal agents:

```bash
super agent compile a2a-dspy-demo
super agent compile a2a-pydantic-demo --framework pydantic-ai
super agent compile a2a-adk-demo --framework google-adk
```

This gives you local playbooks you can inspect and customize.

If you want to run the ADK playbook after compile, make sure `GOOGLE_API_KEY` is exported in the shell where you run or serve the agent.

## Option 3: Serve a Compiled Agent Through the CLI

If you already compiled an agent inside a SuperOptiX project, you can expose it over A2A directly:

```bash
super agent serve a2a-dspy-demo --protocol a2a
```

Example with explicit host and port:

```bash
super agent serve a2a-dspy-demo --protocol a2a --host 127.0.0.1 --port 8101
super agent serve a2a-pydantic-demo --protocol a2a --framework pydantic-ai --host 127.0.0.1 --port 8102
super agent serve a2a-adk-demo --protocol a2a --framework google-adk --host 127.0.0.1 --port 8103
```

For the ADK CLI serve flow:

```bash
export GOOGLE_API_KEY=your_google_api_key
super agent serve a2a-adk-demo --protocol a2a --framework google-adk --host 127.0.0.1 --port 8103
```

## Source Checkout Example Scripts

If you are working from the source tree, the same demos also exist under:

- `examples/a2a/dspy_server_demo.py`
- `examples/a2a/pydantic_ai_server_demo.py`
- `examples/a2a/google_adk_server_demo.py`
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
export GOOGLE_API_KEY=your_google_api_key
python -m superoptix.demos.a2a.google_adk_server_demo --port 8103
```

Terminal 4:

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Terminal 5:

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

Terminal 6:

```bash
python -m superoptix.demos.a2a.call_remote_a2a_agent \
  --url http://127.0.0.1:8103 \
  --message "Outline an enterprise rollout plan for A2A support."
```

## Current Limitations

Current demo limitations:

- no CrewAI A2A demo yet
- no single orchestrator demo that routes work among multiple framework agents

## Next Demo Milestone

The next meaningful A2A demo should add:

1. DSPy agent
2. Pydantic AI agent
3. CrewAI agent
4. Google ADK agent
5. one orchestrator that discovers all four Agent Cards and delegates tasks between them

That would be the first complete cross-framework A2A demo for SuperOptiX.
