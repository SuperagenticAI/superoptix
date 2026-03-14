# A2A Demo

This folder contains a minimal end-to-end A2A demo for SuperOptiX.

It proves:

- a DSPy-style SuperOptiX pipeline can be exposed as an A2A server
- a non-DSPy SuperOptiX pipeline can be exposed the same way
- the SuperOptiX A2A client wrapper can call either agent by URL

## Current Scope

Available now:

- DSPy-style agent served over A2A
- Pydantic AI agent served over A2A
- SuperOptiX A2A client calling either server by URL

Not included yet:

- CrewAI A2A demo
- Google ADK A2A demo
- multi-agent cross-framework conversation where DSPy, Pydantic AI, CrewAI, and ADK agents all talk to each other over A2A
- CLI command like `super agent serve --protocol a2a`

So the answer today is: we have DSPy and Pydantic AI A2A demos, but we do not yet have the full multi-framework A2A conversation demo for DSPy + Pydantic AI + CrewAI + ADK.

## Requirements

Install the A2A extra and the Pydantic AI extra:

```bash
pip install -e ".[a2a,frameworks-pydantic-ai]"
```

Run all commands from the repository root:

```bash
cd /path/to/superoptix
```

If you are using the installed package and want the demo playbooks inside your project, initialize a SuperOptiX project first and pull the demo agents:

```bash
super init a2a-demo
cd a2a-demo
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
```

These pulled agents are useful for inspection, customization, compile, and run flows.

## Package-Installed Demo Flow

If you installed SuperOptiX as a package, you can run the packaged demo modules directly:

```bash
python -m superoptix.demos.a2a.dspy_server_demo --port 8101
python -m superoptix.demos.a2a.pydantic_ai_server_demo --port 8102
python -m superoptix.demos.a2a.call_remote_a2a_agent --url http://127.0.0.1:8101 --message "Create a short research brief about A2A support in SuperOptiX."
python -m superoptix.demos.a2a.call_remote_a2a_agent --url http://127.0.0.1:8102 --message "What is this FAQ agent for?"
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

## 3. Call a remote A2A agent

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
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8101 \
  --message "Create a short research brief about A2A support in SuperOptiX."
```

Terminal 4:

```bash
python examples/a2a/call_remote_a2a_agent.py \
  --url http://127.0.0.1:8102 \
  --message "What is this FAQ agent for?"
```

## Pullable Demo Agents

Built-in pullable demo IDs:

```bash
super agent pull a2a-dspy-demo
super agent pull a2a-pydantic-demo
```

After pulling, you can inspect or compile them like normal agents:

```bash
super agent compile a2a-dspy-demo
super agent compile a2a-pydantic-demo --framework pydantic-ai
```

These pulled playbooks are packaged with SuperOptiX, so users do not need the repository source tree just to fetch the demo agents.

## Troubleshooting

If `import a2a` fails:

```bash
pip install -e ".[a2a]"
```

If the Pydantic AI demo fails to import:

```bash
pip install -e ".[frameworks-pydantic-ai]"
```

If both are needed:

```bash
pip install -e ".[a2a,frameworks-pydantic-ai]"
```

## Notes

- These demos focus on blocking request/response and basic task lifecycle.
- They intentionally avoid imports from `reference/`.
- They use the external `a2a-sdk` through `superoptix[a2a]`.

## Next Demo To Build

The next meaningful example should be:

1. DSPy agent served over A2A
2. Pydantic AI agent served over A2A
3. CrewAI agent served over A2A
4. Google ADK agent served over A2A
5. one orchestrator agent that discovers all four Agent Cards and delegates work between them

That would be the first true cross-framework A2A conversation demo for SuperOptiX.
