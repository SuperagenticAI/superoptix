# Framework Feature Matrix

Current capability snapshot for SuperOptiX framework integrations.

| Feature | DSPy | OpenAI SDK | Claude SDK | Pydantic AI | CrewAI | Google ADK | DeepAgents | Microsoft (Legacy) |
|---|---|---|---|---|---|---|---|---|
| Minimal pipeline compile/run | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `--optimize` compile path | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| GEPA optimization flow | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| StackOne connector integration | Yes | Yes | Yes | Yes | Yes | Planned | Planned | Planned |
| RLM support | Yes (experimental) | Yes (experimental) | Planned | Yes (experimental) | Yes (experimental) | Yes (experimental) | Yes (experimental) | Planned |
| Local Ollama-friendly path | Yes | Yes | No | Yes | Yes | No | No | Yes |
| Cloud model routing flags (`--cloud`) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Sidecar compiled spec loading | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Notes

- RLM is experimental and still evolving.
- Unified sandbox support for RLM is coming soon.
- Microsoft framework support is maintained in legacy mode.
- Cloud-only frameworks typically require function-calling-capable models.
