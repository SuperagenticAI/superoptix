# Framework Feature Matrix

Current capability snapshot for SuperOptiX framework integrations.

## 🎉 New: OpenAI Agents SDK (v0.14+)

Full support for the new OpenAI Agents SDK with **harness + sandbox** architecture:
- Native sandbox execution with manifest-based data staging
- Built-in snapshotting + rehydration for durability
- Partner sandboxes: Cloudflare, E2B, Modal, and more
- Compatible with Ollama and all major cloud providers

| Feature | DSPy | OpenAI Agents SDK | Claude SDK | Pydantic AI | CrewAI | Google ADK | DeepAgents | Microsoft (Legacy) |
|---|---|---|---|---|---|---|---|---|
| Minimal pipeline compile/run | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `--optimize` compile path | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| GEPA optimization flow | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| StackOne connector integration | Yes | ✅ Yes | Yes | Yes | Yes | Planned | Planned | Planned |
| RLM support | Yes | ✅ Yes | Planned | Yes | Yes | Yes | Yes | Planned |
| Native sandbox harness | - | ✅ Yes | - | - | - | - | - | - |
| Local Ollama-friendly path | Yes | ✅ Yes | No | Yes | Yes | No | No | Yes |
| Cloud model routing flags (`--cloud`) | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Sidecar compiled spec loading | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Notes

- Microsoft framework support is maintained in legacy mode.
- Cloud-only frameworks typically require function-calling-capable models.
