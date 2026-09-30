# Langfuse agent example

Follow the [Langfuse integration guide](../../guides/langfuse-integration.md)
to install the SDK and set credentials. Then run an agent:

```bash
super agent run my_agent --goal 'Explain the result' --observe langfuse
```

Open the trace in Langfuse and inspect the `agent_run` observation. Nested
operations appear under the same trace. DSPy model calls appear when the DSPy
OpenInference instrumentor is enabled as described in the guide.
