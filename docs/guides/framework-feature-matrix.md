# Framework Feature Matrix

Current capability snapshot for SuperOptiX framework integrations.

Every framework listed here can be adapted to A2A 1.0 with
[`super a2a adapt`](a2a-adapt.md), including agents built outside SuperOptiX.

## OpenAI Agents SDK (v0.20+)

Full support for the new OpenAI Agents SDK with **harness + sandbox** architecture:
- Native sandbox execution with manifest-based data staging
- Built-in snapshotting + rehydration for durability
- Partner sandboxes: Cloudflare, E2B, Modal, and more
- Compatible with Ollama and all major cloud providers

| Feature | DSPy | OpenAI Agents SDK | Claude SDK | Pydantic AI | CrewAI | Google ADK | DeepAgents | Microsoft |
|---|---|---|---|---|---|---|---|---|
| Minimal pipeline compile/run | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `--optimize` compile path | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| GEPA optimization flow | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `super a2a adapt` introspection | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Native sandbox harness | - | ✅ Yes | - | - | - | - | - | - |
| Local Ollama-friendly path | Yes | ✅ Yes | No | Yes | Yes | No | No | Yes |
| Cloud model routing flags (`--cloud`) | Yes | ✅ Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Sidecar compiled spec loading | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Notes

- Microsoft framework support is maintained in legacy mode.
- Cloud-only frameworks typically require function-calling-capable models.
