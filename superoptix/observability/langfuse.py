"""Optional Langfuse SDK v4 integration for SuperOptix traces."""

import logging
import os
import threading
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)
_clients = {}
_clients_lock = threading.Lock()
_dspy_instrumented = False
_instrument_lock = threading.Lock()


def instrument_dspy() -> bool:
    """Enable DSPy model spans when its optional instrumentor is installed."""
    global _dspy_instrumented
    with _instrument_lock:
        if _dspy_instrumented:
            return True
        try:
            from openinference.instrumentation.dspy import DSPyInstrumentor

            DSPyInstrumentor().instrument()
            _dspy_instrumented = True
            return True
        except ImportError:
            logger.warning(
                "DSPy Langfuse spans unavailable: install openinference-instrumentation-dspy"
            )
        except Exception:
            logger.exception("DSPy Langfuse instrumentation failed")
    return False


def mask_otel_spans(*, params):
    """Remove common LLM payload attributes from SDK and OpenInference spans."""
    if os.getenv("SUPEROPTIX_LANGFUSE_CAPTURE_CONTENT") == "1":
        return None
    from langfuse.types import MaskOtelSpansResult, OtelSpanPatch

    content_names = {
        "input.value",
        "output.value",
        "llm.prompts",
        "llm.completions",
        "llm.input_messages",
        "llm.output_messages",
        "llm.invocation_parameters",
        "tool.parameters",
        "tool.result",
        "retrieval.documents",
        "gen_ai.input.messages",
        "gen_ai.output.messages",
    }
    content_prefixes = (
        "gen_ai.prompt.",
        "gen_ai.completion.",
        "langfuse.observation.input",
        "langfuse.observation.output",
        "llm.input_messages.",
        "llm.output_messages.",
    )
    patches = {}
    for identifier, span in params.spans.items():
        sensitive = tuple(
            key
            for key in span.attributes
            if key in content_names or key.startswith(content_prefixes)
        )
        if sensitive:
            patches[identifier] = OtelSpanPatch(delete_attributes=sensitive)
    return MaskOtelSpansResult(span_patches=patches) if patches else None


def setup_langfuse():
    """Create a client only when credentials are configured.

    The SDK exports asynchronously. Connectivity checks belong in an explicit
    setup or diagnostic command, not in every agent run.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    if not (public_key and secret_key):
        logger.warning(
            "Langfuse tracing disabled: set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY"
        )
        return None
    config_key = (public_key, secret_key, os.getenv("LANGFUSE_BASE_URL"))
    try:
        from langfuse import Langfuse

        with _clients_lock:
            if config_key not in _clients:
                _clients[config_key] = Langfuse(mask_otel_spans=mask_otel_spans)
            return _clients[config_key]
    except ImportError:
        logger.warning("Langfuse tracing disabled: install superoptix[observability]")
    except Exception:
        logger.exception("Langfuse client initialization failed")
    return None


def safe_attributes(data: Any) -> dict:
    """Export structural fields only unless content capture is explicitly enabled."""
    if not isinstance(data, dict):
        return {}
    if os.getenv("SUPEROPTIX_LANGFUSE_CAPTURE_CONTENT") == "1":
        return data
    allowed = {
        "agent_id",
        "agent_name",
        "component",
        "operation",
        "framework",
        "event_type",
        "status",
        "duration_ms",
        "accuracy",
        "cost_usd",
        "tokens_used",
        "latency_ms",
        "success_rate",
        "optimizer_name",
        "initial_score",
        "final_score",
        "improvement",
        "iterations",
        "population_size",
        "generations",
        "duration_seconds",
        "protocol_type",
        "tools_discovered",
        "total_calls",
    }
    return {
        key: value
        for key, value in data.items()
        if key in allowed and isinstance(value, (str, int, float, bool))
    }


@contextmanager
def operation(client, name: str, component: str, agent_id: str, metadata: dict):
    """Keep a Langfuse observation active for the actual operation duration."""
    if client is None:
        yield
        return
    try:
        observation = client.start_as_current_observation(
            name=name,
            as_type="agent" if component.startswith("agent.") else "span",
            metadata=safe_attributes(
                {"agent_id": agent_id, "component": component, **metadata}
            ),
        )
    except Exception:
        logger.exception("Langfuse observation could not start")
        yield
        return
    try:
        span = observation.__enter__()
    except Exception:
        logger.exception("Langfuse observation could not open")
        yield
        return
    try:
        yield
    except BaseException as exc:
        try:
            span.update(level="ERROR", status_message=type(exc).__name__)
            observation.__exit__(type(exc), exc, exc.__traceback__)
        except Exception:
            logger.exception("Langfuse error status could not be recorded")
        raise
    else:
        try:
            observation.__exit__(None, None, None)
        except Exception:
            logger.exception("Langfuse observation export failed")


def log_event(client, name: str, agent_id: str, component: str, data: dict):
    if client is None:
        return
    try:
        with client.start_as_current_observation(
            name=name,
            as_type="span",
            metadata=safe_attributes(
                {"agent_id": agent_id, "component": component, **data}
            ),
        ):
            pass
    except Exception:
        logger.exception("Langfuse event export failed")


def flush(client):
    if client is not None:
        try:
            client.flush()
        except Exception:
            logger.exception("Langfuse flush failed")
