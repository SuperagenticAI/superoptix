# Framework Feature Matrix

Current capability snapshot for SuperOptiX framework integrations.

| Feature | DSPy | OpenAI Agents SDK | Claude SDK | Pydantic AI | CrewAI | Google ADK | DeepAgents | Microsoft (Legacy) |
|---|---|---|---|---|---|---|---|---|
| Minimal pipeline compile/run | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `--optimize` compile path | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| GEPA optimization flow | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| StackOne connector integration | Yes | Yes | Yes | Yes | Yes | Planned | Planned | Planned |
| RLM support | Yes | Yes | Planned | Yes | Yes | Yes | Yes | Planned |
| Native sandbox harness | Planned | Yes (`openai_agent.sandbox`) | Planned | Planned | Planned | Planned | Planned | Planned |
| Local Ollama-friendly path | Yes | Yes | No | Yes | Yes | No | No | Yes |
| Cloud model routing flags (`--cloud`) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Sidecar compiled spec loading | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Notes

- OpenAI Agents SDK path supports native sandbox harness configuration via `spec.openai_agent.sandbox`.
- Cross-framework unified sandbox support is still coming.
- Microsoft framework support is maintained in legacy mode.
- Cloud-only frameworks typically require function-calling-capable models.
