# Microsoft Agent Framework Integration

This integration is available in SuperOptiX as **legacy support**.

Use it when you already have Microsoft Agent Framework projects and want to keep a unified SuperSpec workflow. For new projects, prefer DSPy, Pydantic AI, OpenAI SDK, Claude SDK, Google ADK, or DeepAgents.

## Support Status

- Legacy-compatible support is maintained.
- Compile, run, evaluate, and optimize flows remain available.
- New feature investment is focused on the other active frameworks.

## Install

```bash
pip install superoptix[frameworks-microsoft]
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
    model: llama3.1:8b
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
- If you need stronger active support for new capabilities (StackOne, RLM, fast template evolution), use one of the actively expanded frameworks.
