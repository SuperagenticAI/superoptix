# Langfuse integration

SuperOptix exports agent operations to Langfuse using the Python SDK v4. A
single `agent_run` observation contains its nested operations and DSPy spans.
SuperOptix also keeps its local JSONL traces.

## Install and configure

```bash
uv pip install 'superoptix[observability]'
export LANGFUSE_PUBLIC_KEY='pk-lf-...'
export LANGFUSE_SECRET_KEY='sk-lf-...'
export LANGFUSE_BASE_URL='https://cloud.langfuse.com'
```

Use the base URL of your own Langfuse region or self-hosted deployment. Keep
credentials in environment variables or a secret manager, not in playbooks.
For a local server, follow the [official Langfuse v4 Docker Compose
guide](https://langfuse.com/self-hosting/deployment/docker-compose). Its stack
includes the services needed by Langfuse v4.

Run an agent with Langfuse tracing:

```bash
super agent run my_agent --goal 'Summarize this document' --observe langfuse
```

The CLI flushes the Langfuse client before it exits. If credentials or the SDK
are missing, it logs a warning and still records local traces. Set
`LANGFUSE_DEBUG=True` while diagnosing missing observations. Langfuse's
[`auth_check()`](https://langfuse.com/docs/observability/sdk/troubleshooting-and-faq)
can be used as a separate connectivity check during setup.

## DSPy instrumentation

To record DSPy model calls, install the DSPy OpenInference instrumentor:

```bash
uv pip install openinference-instrumentation-dspy
```

The CLI enables this instrumentor automatically for a DSPy agent run with
`--observe langfuse` when the package is installed. For direct use of
`ObservabilityEnhancedDSPyAdapter`, set `observability.enable_langfuse: true`
in its configuration. Agent CLI operations and DSPy spans then share the
active OpenTelemetry trace. See
[Langfuse's DSPy integration](https://langfuse.com/integrations/frameworks/dspy).

## Data controls

SuperOptix exports structural metadata by default: agent and component names,
status, duration, and numeric metrics. It excludes queries, outputs, prompts,
and GEPA prompt history from its own observations. The Langfuse client also
uses an export-stage mask for common SDK and OpenInference prompt, response,
and tool payload attributes. Review traces from any other instrumentors you
enable, since they may use additional attribute names. Set
`SUPEROPTIX_LANGFUSE_CAPTURE_CONTENT=1` only when your deployment permits
sending that content to Langfuse. See [Langfuse's masking
guide](https://langfuse.com/docs/observability/features/masking).

Langfuse sends all traces by default. Set `LANGFUSE_SAMPLE_RATE` to a value
between `0` and `1` to reduce volume, for example `0.2` for 20% of traces.
See [Langfuse sampling](https://langfuse.com/docs/observability/features/sampling).

## Verify

Run a short agent task and open its trace in Langfuse. Check that one agent
observation contains nested operations, with any DSPy LLM calls beneath it.
The CLI should log a clear warning if Langfuse is unavailable. The integration
can be tested without a server with:

```bash
uv run --frozen --extra dev pytest tests/test_langfuse_observability.py -q
```

## Next steps

Langfuse v4 provides observation-based monitors, code evaluators, and fast
Metrics and Observations APIs. Once trace export is verified, create monitors
for error rate, latency, and cost; then evaluate tool outcomes and optimization
runs with deterministic code evaluators. See the [Langfuse v4
overview](https://langfuse.com/changelog/2026-08-17-langfuse-v4).
