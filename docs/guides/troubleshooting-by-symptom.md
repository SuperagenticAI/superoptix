# Troubleshooting by Symptom

Use this page when you have an error and want the fastest fix path.

## Quick Symptom Table

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Pipeline not found` | Agent not compiled for that framework | Run `super agent compile <agent> --framework <framework>` |
| `OPENAI_API_KEY is required` while using Google | Runtime/provider mismatch | Pass `--cloud --provider google-genai --model gemini-2.5-flash` on both compile and run |
| `DefaultCredentialsError` from Vertex | Model/provider path resolved to Vertex instead of Google GenAI API-key flow | Ensure provider/model pair is `google-genai` + Gemini model and `GOOGLE_API_KEY` is set |
| `name 'false' is not defined` | JSON boolean leaked into generated Python | Recompile with latest templates, then rerun |
| `Exceeded maximum retries for output validation` | Structured output too strict for current model response | Increase retries, reduce strictness, or switch to stronger model |
| StackOne tool returns `400 Bad Request` | Tool args or account/provider mismatch | Verify `STACKONE_ACCOUNT_IDS`, action filters, and tool input args |
| `DSPy program timed out` | Tool/model latency exceeded timeout | Increase timeout env setting or simplify tools/model path |
| `No such file ... playbook` | Missing generated sidecar/spec artifacts | Re-run `super agent compile ...` and keep generated pipeline+sidecar together |

## Key Checks

```bash
# Verify keys in current shell
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $STACKONE_API_KEY
echo $STACKONE_ACCOUNT_IDS
```

```bash
# Recompile cleanly for target framework
super agent compile <agent_id> --framework <framework> --cloud --provider google-genai --model gemini-2.5-flash
```

```bash
# Run with matching provider/model flags
super agent run <agent_id> --framework <framework> --cloud --provider google-genai --model gemini-2.5-flash --goal "..."
```

## StackOne-specific Checks

- Confirm connector account is active for the target app (for example Calendly).
- Start with identity calls first (`*_get_current_user`) before list/query calls.
- For event listing calls, include explicit date/time window and timezone where required.

## RLM Note

RLM is currently experimental. Unified sandbox support is coming soon. If an RLM path is unstable for your use case, keep a non-RLM fallback module in the same agent.
