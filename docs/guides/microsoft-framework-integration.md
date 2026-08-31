# Microsoft Agent Framework Integration

This integration is available in SuperOptiX as **legacy support**.

Use it when you already have Microsoft Agent Framework projects and want to keep a unified SuperSpec workflow. For new projects, prefer DSPy, Pydantic AI, OpenAI SDK, Claude SDK, Google ADK, or DeepAgents.

## Support Status

- Legacy-compatible support is maintained.
- Compile, run, evaluate, and optimize flows remain available.
- New feature investment is focused on the other active frameworks.

## Install

```bash
uv pip install -U "superoptix[frameworks-microsoft]"
```

Important:

- the published `frameworks-microsoft` extra should install a compatible prerelease `agent-framework` build
- the Microsoft Python SDK currently exposes `Agent` in newer builds, while some earlier prerelease examples used `ChatAgent`
- if `super agent run ... --framework microsoft` fails with `cannot import name 'ChatAgent' from 'agent_framework'`, your generated pipeline was compiled against the older API
- when running Microsoft with Gemini via `--provider google-genai`, set `GOOGLE_API_KEY` or `GEMINI_API_KEY`, not `OPENAI_API_KEY`
- reinstall the framework package with:

```bash
uv pip install -U --pre agent-framework azure-identity
```

- after that, recompile the Microsoft pipeline before rerunning so it regenerates against the updated template

If you are upgrading from an older release and the compiled Microsoft pipeline is still stale, use this reset flow:

```bash
uv pip install -U --force-reinstall "superoptix[frameworks-microsoft]"

rm -f surrealoptix/agents/assistant_microsoft/pipelines/assistant_microsoft_microsoft_pipeline.py
rm -f surrealoptix/agents/assistant_microsoft/pipelines/assistant_microsoft_microsoft_pipeline_compiled_spec.json

super agent pull assistant_microsoft
super agent compile assistant_microsoft --framework microsoft
```

## Basic Workflow

```bash
# Pull a demo agent
super agent pull assistant_microsoft

# Compile
super agent compile assistant_microsoft --framework microsoft

# Run
super agent run assistant_microsoft --framework microsoft --goal "Summarize the incident"

# Optional optimization path
super agent compile assistant_microsoft --framework microsoft --optimize
super agent optimize assistant_microsoft --framework microsoft --auto light
```

## Playbook Example

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: assistant_microsoft
spec:
  target_framework: microsoft
  language_model:
    provider: ollama
    model: qwen3.5:9b
    api_base: http://localhost:11434
  persona:
    role: Helpful Assistant
    goal: Provide clear and practical answers
  input_fields:
    - name: query
      type: string
  output_fields:
    - name: response
      type: string
```

## Notes

- Keep `--framework microsoft` explicit in `compile`, `run`, and `optimize`.
- If you hit a `ChatAgent` import error, your generated pipeline is stale or your `agent-framework` install is outdated. Reinstall with `uv pip install -U --pre agent-framework azure-identity` and recompile.
- If you hit a `Agent.__init__() missing 1 required positional argument: 'client'` error, your generated Microsoft pipeline was compiled from an older SuperOptiX release. Force reinstall SuperOptiX, delete the generated Microsoft pipeline files, and compile again.
