# A2A Demo

This folder contains a minimal end-to-end A2A demo for SuperOptiX.

The demo uses the A2A `1.0` protocol shape at the SuperOptiX adapter boundary.
So the demo servers expose a v1-style Agent Card and v1 operations such as `SendMessage`, `GetTask`, `CancelTask`, and `SubscribeToTask`.

It proves:

- a DSPy-style SuperOptiX pipeline can be exposed as an A2A server
- a non-DSPy SuperOptiX pipeline can be exposed the same way
- the SuperOptiX A2A client wrapper can call either agent by URL

## Current Scope

Available now:

- DSPy-style agent served over A2A
- Pydantic AI agent served over A2A
- Google ADK agent served over A2A
- SuperOptiX A2A client calling those servers by URL

Not included yet:

- CrewAI A2A demo
- Google ADK A2A demo
- multi-agent cross-framework conversation where DSPy, Pydantic AI, CrewAI, and ADK agents all talk to each other over A2A
- full multi-framework orchestrated A2A showcase

So the answer today is: we have DSPy and Pydantic AI A2A demos, but we do not yet have the full multi-framework A2A conversation demo for DSPy + Pydantic AI + CrewAI + ADK.

## Requirements

Install the A2A extra and the Pydantic AI extra:

```bash
uv pip install -e ".[a2a,frameworks-pydantic-ai,frameworks-google]"
```

Run all commands from the repository root.

If you are using the installed package and want the demo playbooks inside your project, initialize a SuperOptiX project first and pull the demo agents:

```bash
super init a2a-demo
cd a2a-demo
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
super agent pull a2a-adk-demo
```

These pulled agents are useful for inspection, customization, compile, and run flows.

## Package-Installed Demo Flow

If you installed SuperOptiX as a package, you can run the packaged demo modules directly:

```bash
python -m superoptix.demos.a2a.dspy_server_demo --port 8101
python -m superoptix.demos.a2a.pydantic_ai_server_demo --port 8102
export GOOGLE_API_KEY=your_google_api_key
python -m superoptix.demos.a2a.google_adk_server_demo --port 8103
python -m superoptix.demos.a2a.call_remote_a2a_agent --url http://127.0.0.1:8101 --message "Create a short research brief about A2A support in SuperOptiX."
python -m superoptix.demos.a2a.call_remote_a2a_agent --url http://127.0.0.1:8102 --message "What is this FAQ agent for?"
python -m superoptix.demos.a2a.call_remote_a2a_agent --url http://127.0.0.1:8103 --message "Outline an enterprise rollout plan for A2A support."
```

This path does not require the source checkout examples directory.

## 1. Start the DSPy demo server

```bash
python examples/a2a/dspy_server_demo.py --port 8101
```

Endpoint:

```text
http://127.0.0.1:8101/.well-known/agent-card.json
http://127.0.0.1:8101/a2a/jsonrpc
```

What this server does:

- exposes a small DSPy-style research brief agent through the SuperOptiX A2A bridge
- returns a short deterministic response so the demo is easy to validate locally

## 2. Start the Pydantic AI demo server

```bash
python examples/a2a/pydantic_ai_server_demo.py --port 8102
```

Endpoint:

```text
http://127.0.0.1:8102/.well-known/agent-card.json
http://127.0.0.1:8102/a2a/jsonrpc
```

This demo uses `pydantic_ai.models.test.TestModel`, so it does not require API keys.

What this server does:

- exposes a small Pydantic AI FAQ-style agent through the same A2A bridge
- uses Pydantic AI's local test model so it can run without OpenAI or Anthropic credentials

## 3. Start the Google ADK demo server

```bash
export GOOGLE_API_KEY=your_google_api_key
python examples/a2a/google_adk_server_demo.py --port 8103
```

Endpoint:

```text
http://127.0.0.1:8103/.well-known/agent-card.json
http://127.0.0.1:8103/a2a/jsonrpc
```

What this server does:

- exposes a real Google ADK agent through the same SuperOptiX A2A bridge
- uses Gemini through Google ADK, so it requires `GOOGLE_API_KEY`

## 4. Call a remote A2A agent

Call the DSPy demo:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Call the Pydantic AI demo:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

Call the Google ADK demo:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8103 \
  --message "Outline an enterprise rollout plan for A2A support."
```

The caller script will:

- connect to the remote A2A endpoint
- fetch the Agent Card
- print discovered capabilities
- send a blocking message
- print the response

## Recommended Local Demo Flow

Terminal 1:

```bash
python examples/a2a/dspy_server_demo.py --port 8101
```

Terminal 2:

```bash
python examples/a2a/pydantic_ai_server_demo.py --port 8102
```

Terminal 3:

```bash
export GOOGLE_API_KEY=your_google_api_key
python examples/a2a/google_adk_server_demo.py --port 8103
```

Terminal 4:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Terminal 5:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

Terminal 6:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8103 \
  --message "Outline an enterprise rollout plan for A2A support."
```

## Pullable Demo Agents

Built-in pullable demo IDs:

```bash
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
super agent pull a2a-adk-demo
```

After pulling, you can inspect or compile them like normal agents:

```bash
super agent compile a2a-dspy-demo
super agent compile a2a-pydantic-demo --framework pydantic-ai
super agent compile a2a-adk-demo --framework google-adk
```

These pulled playbooks are packaged with SuperOptiX, so users do not need the repository source tree just to fetch the demo agents.

## Troubleshooting

If `import a2a` fails:

```bash
uv pip install -e ".[a2a]"
```

If the Pydantic AI demo fails to import:

```bash
uv pip install -e ".[frameworks-pydantic-ai]"
```

If the Google ADK demo fails to import:

```bash
uv pip install -e ".[frameworks-google]"
```

If both are needed:

```bash
uv pip install -e ".[a2a,frameworks-pydantic-ai,frameworks-google]"
```

## Notes

- These demos focus on blocking request/response and basic task lifecycle.
- They intentionally avoid vendored protocol source code.
- They use the external `a2a-sdk` through `superoptix[a2a]`.

## Next Demo To Build

The next meaningful example should be:

1. DSPy agent served over A2A
2. Pydantic AI agent served over A2A
3. Google ADK agent served over A2A
4. CrewAI agent served over A2A
5. one orchestrator agent that discovers all four Agent Cards and delegates work between them

That would be the first true cross-framework A2A conversation demo for SuperOptiX.
