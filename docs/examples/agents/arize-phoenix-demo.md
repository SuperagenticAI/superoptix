# Arize Phoenix Trace Demo

This example shows how to connect a SuperOptiX DSPy agent to Arize Phoenix so you can inspect traces in the Phoenix UI.

The focus is intentionally narrow:

- pull an agent with `super agent pull`
- enable Phoenix tracing
- run the agent once
- open Phoenix and inspect the trace

You do not need to run evaluation or optimization for this demo.

## What This Demo Covers

This page covers two user-facing setups:

1. Pull the dedicated demo agent with `super agent pull arize-phoenix-demo`
2. Pull an existing agent such as `developer` and add a `phoenix` block to its playbook

Both paths produce Phoenix traces from a normal `super agent run`.

## Prerequisites

Install SuperOptiX with Phoenix support:

```bash
pip install "superoptix[phoenix]"
pip install arize-phoenix
```

You also need a working model backend.

Common options:

- local Ollama model
- cloud model such as Google Gemini
- another supported provider you already use with SuperOptiX

If you are using Gemini, set an API key first:

```bash
export GOOGLE_API_KEY="your_google_api_key"
```

## Start Phoenix

Start the local Phoenix server:

```bash
python -m phoenix.server.main serve
```

Phoenix defaults:

- UI: `http://localhost:6006`
- HTTP trace collector: `http://localhost:6006/v1/traces`

If your environment prevents Phoenix from writing to its default working directory, set one explicitly:

```bash
export PHOENIX_WORKING_DIR=/tmp/phoenix
python -m phoenix.server.main serve
```

## Option 1: Pull the Dedicated Demo Agent

This is the simplest path.

### Step 1: Create a project

```bash
super init swe
cd swe
```

### Step 2: Pull the Phoenix demo

```bash
super agent pull arize-phoenix-demo
```

This installs a prebuilt playbook into your project.

### Step 3: Compile the demo

If you want to use the playbook defaults:

```bash
super agent compile arize-phoenix-demo
```

If you want to force a cloud Gemini run:

```bash
super agent compile arize-phoenix-demo --cloud --provider google-genai --model gemini-2.5-flash
```

### Step 4: Run the demo

```bash
super agent run arize-phoenix-demo --goal "Summarize why tracing helps debug AI agents."
```

Or with explicit cloud settings:

```bash
super agent run arize-phoenix-demo --cloud --provider google-genai --model gemini-2.5-flash --goal "Summarize why tracing helps debug AI agents."
```

### Step 5: Inspect Phoenix

Open:

```text
http://localhost:6006
```

You should see a Phoenix project named:

```text
superoptix-phoenix-demo
```

The trace should include a top-level SuperOptiX DSPy run span plus nested DSPy spans when instrumentation is available.

## Option 2: Pull an Existing Agent and Add Phoenix

If you want to demo Phoenix with a familiar agent such as `developer`, use this flow.

### Step 1: Pull the agent

```bash
super init swe
cd swe

super agent pull developer
```

### Step 2: Add Phoenix config to the playbook

Open:

```text
swe/agents/developer/playbook/developer_playbook.yaml
```

Add a `phoenix` block under `spec`:

```yaml
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434

  phoenix:
    enabled: true
    project_name: swe-developer-phoenix-demo
    endpoint: http://127.0.0.1:6006
    protocol: http/protobuf
    batch: false
    auto_instrument: true
```

Key fields:

- `enabled`: turns Phoenix tracing on for this agent
- `project_name`: the project name shown in Phoenix
- `endpoint`: Phoenix collector base URL
- `protocol`: `http/protobuf` is the easiest local default
- `batch`: `false` is useful for demos because spans flush quickly
- `auto_instrument`: enables OpenInference instrumentation when the matching packages are installed

### Step 3: Compile

```bash
super agent compile developer
```

Or override the model at compile time:

```bash
super agent compile developer --cloud --provider google-genai --model gemini-2.5-flash
```

### Step 4: Run

```bash
super agent run developer --goal "Write a short Python function that returns factorial(n) and explain the base case in one sentence."
```

Or with explicit cloud settings:

```bash
super agent run developer --cloud --provider google-genai --model gemini-2.5-flash --goal "Write a short Python function that returns factorial(n) and explain the base case in one sentence."
```

### Step 5: Inspect Phoenix

Open the Phoenix UI and look for:

```text
swe-developer-phoenix-demo
```

## Example Playbook Used by the Dedicated Demo

The dedicated demo agent is pullable with:

```bash
super agent pull arize-phoenix-demo
```

Its playbook lives in the SuperOptiX demo agents catalog and is designed specifically to generate traces without requiring eval or optimization.

## Expected Result

After a run, Phoenix should show:

- a project for your agent
- one or more traces for the run
- a top-level span such as `superoptix.dspy.run`
- nested DSPy spans if OpenInference DSPy instrumentation is active

Even if the model call fails, Phoenix can still be useful. Error traces will still show the execution path and where the failure occurred.

## Troubleshooting

### Phoenix UI does not start

Install the server package:

```bash
pip install arize-phoenix
```

Then retry:

```bash
python -m phoenix.server.main serve
```

### Phoenix cannot write to its working directory

Set a writable directory:

```bash
export PHOENIX_WORKING_DIR=/tmp/phoenix
python -m phoenix.server.main serve
```

### No traces appear in Phoenix

Check the agent playbook:

- `spec.phoenix.enabled: true`
- `spec.phoenix.endpoint: http://127.0.0.1:6006`

Check Phoenix is running:

```bash
curl http://localhost:6006
```

Run the agent again after Phoenix is already up.

### The agent runs but auto-instrumentation is missing

Install the Phoenix/OpenInference extras:

```bash
pip install "superoptix[phoenix]"
```

### The model request fails

Phoenix tracing is separate from model credentials.

For Gemini:

```bash
export GOOGLE_API_KEY="your_google_api_key"
```

For Ollama, make sure the server is running and the configured model exists.

## Demo Summary

Fastest path:

```bash
pip install "superoptix[phoenix]"
pip install arize-phoenix

python -m phoenix.server.main serve

super init swe
cd swe
super agent pull arize-phoenix-demo
super agent compile arize-phoenix-demo
super agent run arize-phoenix-demo --goal "Summarize why tracing helps debug AI agents."
```

That is the recommended user-facing demo when the goal is simply to show traces in Phoenix.
