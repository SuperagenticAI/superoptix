# Troubleshooting by Symptom

Use this page when you have an error and want the fastest fix path.

## Quick Symptom Table

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Pipeline not found` | Agent not compiled for that framework | Run `super agent compile <agent> --framework <framework>` |
| `OPENAI_API_KEY is required` while using Google | Runtime/provider mismatch | Pass `--cloud --provider google-genai --model gemini-3.7-flash` on both compile and run |
| `DefaultCredentialsError` from Vertex | Model/provider path resolved to Vertex instead of Google GenAI API-key flow | Ensure provider/model pair is `google-genai` + Gemini model and `GOOGLE_API_KEY` is set |
| `name 'false' is not defined` | JSON boolean leaked into generated Python | Recompile with latest templates, then rerun |
| `Exceeded maximum retries for output validation` | Structured output too strict for current model response | Increase retries, reduce strictness, or switch to stronger model |
| `DSPy program timed out` | Tool/model latency exceeded timeout | Increase timeout env setting or simplify tools/model path |
| `No such file ... playbook` | Missing generated sidecar/spec artifacts | Re-run `super agent compile ...` and keep generated pipeline+sidecar together |

## Key Checks

```bash
# Verify keys in current shell
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

```bash
# Recompile cleanly for target framework
super agent compile <agent_id> --framework <framework> --cloud --provider google-genai --model gemini-3.7-flash
```

```bash
# Run with matching provider/model flags
super agent run <agent_id> --framework <framework> --cloud --provider google-genai --model gemini-3.7-flash --goal "..."
```

