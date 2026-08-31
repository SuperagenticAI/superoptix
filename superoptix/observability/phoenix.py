"""Phoenix observability helpers for SuperOptiX.

Provides a lightweight integration layer around ``arize-phoenix-otel`` so the
rest of SuperOptiX can treat Phoenix as an optional backend without taking a
hard dependency on OpenTelemetry/OpenInference packages.
"""

from __future__ import annotations

import importlib
import json
import logging
import os
from contextlib import contextmanager, nullcontext
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
_PHOENIX_HANDLE_CACHE: Dict[tuple, Dict[str, Any]] = {}
_PHOENIX_INSTRUMENTED_FRAMEWORKS: set[str] = set()
_FRAMEWORK_INSTRUMENTORS = {
    "openai": [
        (
            "openinference.instrumentation.openai",
            "OpenAIInstrumentor",
            "openai",
        ),
    ],
    "openai_agents": [
        (
            "openinference.instrumentation.openai_agents",
            "OpenAIAgentsInstrumentor",
            "openai_agents",
        ),
        (
            "openinference.instrumentation.openai",
            "OpenAIInstrumentor",
            "openai",
        ),
    ],
    "crewai": [
        (
            "openinference.instrumentation.crewai",
            "CrewAIInstrumentor",
            "crewai",
        ),
    ],
    "dspy": [
        (
            "openinference.instrumentation.dspy",
            "DSPyInstrumentor",
            "dspy",
        ),
    ],
    "google_adk": [
        (
            "openinference.instrumentation.google_adk",
            "GoogleADKInstrumentor",
            "google_adk",
        ),
    ],
    "pydantic_ai": [
        (
            "openinference.instrumentation.pydantic_ai",
            "PydanticAIInstrumentor",
            "pydantic_ai",
        ),
    ],
}


def normalize_phoenix_endpoint(
    endpoint: Optional[str], protocol: Optional[str] = None
) -> Optional[str]:
    """Normalize Phoenix collector endpoint.

    Phoenix OTEL accepts either a base Phoenix URL or a full traces endpoint.
    For HTTP/protobuf we normalize base URLs to ``/v1/traces``.
    """
    if not endpoint:
        return endpoint

    normalized = endpoint.strip()
    if not normalized:
        return None

    if protocol == "grpc":
        return normalized.rstrip("/")

    if normalized.endswith("/v1/traces"):
        return normalized

    return normalized.rstrip("/") + "/v1/traces"


def _sanitize_attribute_value(value: Any) -> Any:
    """Convert values to OTEL-safe attribute payloads."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        sanitized_items = [
            item
            for item in (_sanitize_attribute_value(v) for v in value)
            if item is not None
        ]
        if all(isinstance(item, (bool, int, float, str)) for item in sanitized_items):
            return sanitized_items
    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def _event_attributes(agent_id: str, event: Any) -> Dict[str, Any]:
    """Build Phoenix/OpenTelemetry span attributes from a trace event."""
    attributes: Dict[str, Any] = {
        "superoptix.agent_id": agent_id,
        "superoptix.event_type": getattr(event, "event_type", "unknown"),
        "superoptix.component": getattr(event, "component", "unknown"),
        "superoptix.status": getattr(event, "status", "info"),
    }

    parent_id = getattr(event, "parent_id", None)
    duration_ms = getattr(event, "duration_ms", None)
    metadata = getattr(event, "metadata", None)
    data = getattr(event, "data", None)

    if parent_id:
        attributes["superoptix.parent_id"] = parent_id
    if duration_ms is not None:
        attributes["superoptix.duration_ms"] = float(duration_ms)
    if metadata:
        attributes["superoptix.metadata"] = _sanitize_attribute_value(metadata)

    if isinstance(data, dict):
        for key, value in data.items():
            sanitized = _sanitize_attribute_value(value)
            if sanitized is not None:
                attributes[f"superoptix.data.{key}"] = sanitized
    elif data is not None:
        attributes["superoptix.data"] = _sanitize_attribute_value(data)

    return attributes


def setup_phoenix(
    *,
    agent_id: str,
    project_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    protocol: Optional[str] = None,
    batch: bool = True,
    auto_instrument: bool = False,
) -> Optional[Dict[str, Any]]:
    """Initialize Phoenix OTEL tracing.

    Returns a handle dict that can be stored in ``external_tracers`` or ``None``
    when Phoenix dependencies are unavailable or configuration fails.
    """
    try:
        from phoenix.otel import register
    except ImportError:
        logger.warning(
            "⚠️  Phoenix not available - install with: uv pip install superoptix[phoenix]"
        )
        return None

    try:
        from openinference.instrumentation import using_session
    except ImportError:
        using_session = None

    phoenix_project = (
        project_name or os.getenv("PHOENIX_PROJECT_NAME") or f"SuperOptiX-{agent_id}"
    )
    phoenix_endpoint = normalize_phoenix_endpoint(
        endpoint or os.getenv("PHOENIX_COLLECTOR_ENDPOINT"), protocol=protocol
    )
    phoenix_api_key = api_key or os.getenv("PHOENIX_API_KEY")

    try:
        tracer_provider = register(
            project_name=phoenix_project,
            endpoint=phoenix_endpoint,
            api_key=phoenix_api_key,
            protocol=protocol,
            batch=batch,
            auto_instrument=auto_instrument,
            set_global_tracer_provider=False,
            verbose=False,
        )
        tracer = tracer_provider.get_tracer("superoptix.observability")
    except Exception as exc:
        logger.warning(f"⚠️  Phoenix tracing initialization failed: {exc}")
        return None

    return {
        "type": "phoenix",
        "project_name": phoenix_project,
        "endpoint": phoenix_endpoint,
        "protocol": protocol,
        "tracer_provider": tracer_provider,
        "tracer": tracer,
        "using_session": using_session,
    }


def get_phoenix_config(spec_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Resolve Phoenix config from a SuperSpec-like dict."""
    spec = dict(spec_data or {})
    cfg = spec.get("phoenix")
    if not isinstance(cfg, dict):
        cfg = {}

    observe_backend = str(os.getenv("SUPEROPTIX_OBSERVE_BACKEND", "")).strip().lower()
    enabled_from_backend = observe_backend in {"phoenix", "all"}
    enabled = bool(cfg.get("enabled", False) or enabled_from_backend)

    return {
        "enabled": enabled,
        "project_name": str(cfg.get("project_name", "")).strip() or None,
        "endpoint": str(cfg.get("endpoint", "")).strip() or None,
        "api_key_env": str(cfg.get("api_key_env", "PHOENIX_API_KEY")).strip()
        or "PHOENIX_API_KEY",
        "protocol": str(cfg.get("protocol", "")).strip() or None,
        "batch": bool(cfg.get("batch", True)),
        "auto_instrument": bool(cfg.get("auto_instrument", enabled_from_backend)),
    }


def setup_phoenix_for_spec(
    *,
    agent_id: str,
    spec_data: Optional[Dict[str, Any]],
    default_project_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Initialize Phoenix from SuperSpec or CLI-derived config."""
    cfg = get_phoenix_config(spec_data)
    if not cfg.get("enabled", False):
        return None

    api_key_env = str(cfg.get("api_key_env", "PHOENIX_API_KEY")).strip()
    api_key = os.getenv(api_key_env, "").strip() or None
    project_name = (
        cfg.get("project_name") or default_project_name or f"SuperOptiX-{agent_id}"
    )

    cache_key = (
        agent_id,
        project_name,
        cfg.get("endpoint"),
        cfg.get("protocol"),
        bool(cfg.get("batch", True)),
        bool(cfg.get("auto_instrument", False)),
        api_key_env,
    )
    cached = _PHOENIX_HANDLE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    handle = setup_phoenix(
        agent_id=agent_id,
        project_name=project_name,
        endpoint=cfg.get("endpoint"),
        api_key=api_key,
        protocol=cfg.get("protocol"),
        batch=bool(cfg.get("batch", True)),
        auto_instrument=bool(cfg.get("auto_instrument", False)),
    )
    if handle is not None:
        _PHOENIX_HANDLE_CACHE[cache_key] = handle
    return handle


def instrument_framework_with_phoenix(
    handle: Optional[Dict[str, Any]], framework: str
) -> bool:
    """Register an OpenInference instrumentor for a framework when available."""
    if not handle:
        return False

    tracer_provider = handle.get("tracer_provider")
    if tracer_provider is None:
        return False

    normalized = str(framework or "").strip().lower()
    if normalized == "openai-agent":
        normalized = "openai_agents"
    elif normalized == "google-adk":
        normalized = "google_adk"
    elif normalized == "pydantic-ai":
        normalized = "pydantic_ai"

    candidates = _FRAMEWORK_INSTRUMENTORS.get(normalized, [])
    if not candidates:
        return False

    instrumented_any = False
    for module_name, class_name, cache_key in candidates:
        if cache_key in _PHOENIX_INSTRUMENTED_FRAMEWORKS:
            instrumented_any = True
            continue
        try:
            module = importlib.import_module(module_name)
            instrumentor_cls = getattr(module, class_name)
            instrumentor = instrumentor_cls()
            instrumentor.instrument(tracer_provider=tracer_provider)
        except ImportError:
            continue
        except Exception as exc:
            logger.warning(
                "Phoenix instrumentation failed for %s via %s.%s: %s",
                normalized,
                module_name,
                class_name,
                exc,
            )
            continue

        _PHOENIX_INSTRUMENTED_FRAMEWORKS.add(cache_key)
        instrumented_any = True
        logger.info(
            "Phoenix OpenInference instrumentation enabled for %s via %s.%s",
            normalized,
            module_name,
            class_name,
        )

    return instrumented_any


@contextmanager
def phoenix_session_span(
    handle: Optional[Dict[str, Any]],
    *,
    span_name: str,
    session_id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    input_data: Any = None,
):
    """Create a Phoenix span scoped to an optional session."""
    if not handle or not handle.get("tracer"):
        yield None
        return

    tracer = handle["tracer"]
    using_session = handle.get("using_session")
    session_value = session_id or "superoptix-session"
    session_context = (
        using_session(session_id=session_value)
        if callable(using_session)
        else nullcontext()
    )
    attrs = dict(attributes or {})

    with session_context:
        with tracer.start_as_current_span(span_name) as span:
            for key, value in attrs.items():
                sanitized = _sanitize_attribute_value(value)
                if sanitized is not None:
                    span.set_attribute(key, sanitized)
            if input_data is not None and hasattr(span, "set_input"):
                try:
                    span.set_input(input_data)
                except Exception:
                    logger.debug(
                        "Phoenix span %s does not support OpenInference input payloads",
                        span_name,
                        exc_info=True,
                    )
            yield span


def log_phoenix_event(handle: Dict[str, Any], agent_id: str, event: Any) -> None:
    """Log a SuperOptiX trace event to Phoenix as an OTEL span."""
    tracer = handle.get("tracer")
    if tracer is None:
        return

    using_session = handle.get("using_session")
    session_context = (
        using_session(session_id=agent_id) if callable(using_session) else nullcontext()
    )
    span_name = f"{getattr(event, 'component', 'unknown')}.{getattr(event, 'event_type', 'event')}"
    attributes = _event_attributes(agent_id=agent_id, event=event)

    try:
        with session_context:
            with tracer.start_as_current_span(span_name) as span:
                for key, value in attributes.items():
                    if value is not None:
                        span.set_attribute(key, value)

                data = getattr(event, "data", None)
                if hasattr(span, "set_input") and data is not None:
                    span.set_input(data)
                if hasattr(span, "set_output"):
                    span.set_output(
                        {
                            "status": getattr(event, "status", "info"),
                            "duration_ms": getattr(event, "duration_ms", None),
                        }
                    )
    except Exception as exc:
        logger.warning(f"Phoenix event logging failed: {exc}")
