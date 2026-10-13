"""Shared construction of DSPy LMs for local model servers (Ollama first).

DSPy 3.4+ routes ``ollama_chat/`` and ``ollama/`` models through its lm15
engine. That engine treats an empty ``api_key`` as a missing credential
("empty credential under 'ollama'") and expects an OpenAI-compatible base URL
ending in ``/v1``. Ollama is keyless, so every code path that builds an Ollama
LM must omit the key and normalize the base. This module is the one place that
logic lives; call :func:`dspy_lm_kwargs` or :func:`build_dspy_lm` instead of
calling ``dspy.LM`` with hand-rolled Ollama arguments.

It also provides :func:`ensure_local_model_reachable`, a cheap preflight so
runtime paths fail loudly with a clear error instead of reporting success when
the local server is down or the model is not pulled.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

OLLAMA_DEFAULT_BASE = "http://localhost:11434"
OLLAMA_PREFIXES = ("ollama_chat/", "ollama/")
# Local OpenAI-compatible servers (MLX server, LM Studio, HF TGI/vLLM).
OPENAI_COMPATIBLE_LOCAL_PROVIDERS = {"mlx", "lmstudio", "lm_studio", "huggingface"}
LOCAL_PLACEHOLDER_KEY = "local"


class LocalModelUnreachableError(RuntimeError):
    """Raised when a local model server cannot serve the requested model."""


def is_ollama(model: Any, provider: Optional[str] = None) -> bool:
    """True when ``model``/``provider`` refer to an Ollama-served model."""
    if provider and str(provider).strip().lower() == "ollama":
        return True
    m = str(model or "")
    return m.startswith(OLLAMA_PREFIXES) or m.startswith("ollama:")


def ollama_model_id(model: str, chat: bool = True) -> str:
    """Return a DSPy model id for Ollama, accepting any common spelling.

    ``qwen2.5:1.5b``, ``ollama:qwen2.5:1.5b``, ``ollama/qwen2.5:1.5b`` and
    ``ollama_chat/qwen2.5:1.5b`` all map to ``ollama_chat/qwen2.5:1.5b``
    (or ``ollama/...`` when ``chat`` is False).
    """
    name = bare_ollama_name(model)
    return f"{'ollama_chat' if chat else 'ollama'}/{name}"


def bare_ollama_name(model: str) -> str:
    """Strip any Ollama provider prefix from ``model``."""
    m = str(model).strip()
    for prefix in (*OLLAMA_PREFIXES, "ollama:"):
        if m.startswith(prefix):
            return m[len(prefix) :]
    return m


def ollama_root(api_base: Optional[str]) -> str:
    """Server root (no ``/v1``), used for the native ``/api/*`` endpoints."""
    base = str(api_base or OLLAMA_DEFAULT_BASE).strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[: -len("/v1")]
    return base


def ollama_openai_base(api_base: Optional[str]) -> str:
    """OpenAI-compatible base (``.../v1``) that DSPy 3.4+ expects."""
    return f"{ollama_root(api_base)}/v1"


def dspy_lm_kwargs(
    model: str,
    *,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    **extra: Any,
) -> Dict[str, Any]:
    """Build ``dspy.LM`` kwargs, fixing Ollama for DSPy 3.4+.

    For Ollama the model id is normalized to ``ollama_chat/<name>``, the key
    is dropped (Ollama is keyless and lm15 rejects an empty one) and the base
    is forced to ``<root>/v1``. For every provider an empty/blank key is
    omitted rather than passed through, and ``None`` extras are dropped.
    """
    kwargs: Dict[str, Any] = {}
    prov = str(provider or "").strip().lower()
    if str(model).startswith("custom_openai/") or (
        prov in OPENAI_COMPATIBLE_LOCAL_PROVIDERS and api_base
    ):
        # DSPy 3.4 cannot route ``custom_openai/`` (it fails on import); the
        # ``openai/`` route with an explicit /v1 base works for any
        # OpenAI-compatible local server. The OpenAI client needs a non-empty
        # key, so a placeholder is used when none is configured.
        name = str(model).split("/", 1)[1] if "/" in str(model) else str(model)
        kwargs["model"] = f"openai/{name}"
        if api_base:
            base = str(api_base).strip().rstrip("/")
            kwargs["api_base"] = base if base.endswith("/v1") else f"{base}/v1"
        key = str(api_key or "").strip()
        kwargs["api_key"] = (
            key
            if key and key not in ("dummy_key", "dummy-key")
            else LOCAL_PLACEHOLDER_KEY
        )
    elif is_ollama(model, provider):
        kwargs["model"] = (
            str(model)
            if str(model).startswith(OLLAMA_PREFIXES)
            else ollama_model_id(model)
        )
        kwargs["api_base"] = ollama_openai_base(api_base)
        # A real key is still honored (e.g. an authenticating proxy).
        if api_key and str(api_key).strip() and str(api_key).strip() != "ollama":
            kwargs["api_key"] = api_key
    else:
        kwargs["model"] = model
        if api_key and str(api_key).strip():
            kwargs["api_key"] = api_key
        if api_base:
            kwargs["api_base"] = api_base
    for key, value in extra.items():
        if key in ("api_key", "api_base", "model", "provider"):
            continue
        if key == "max_retries":
            # DSPy 3.4 does not know ``max_retries``; passing it knocks the
            # call off the lm15 route onto a broken fallback. Its name for
            # the same thing is ``num_retries``.
            key = "num_retries"
            if extra.get("num_retries") is not None:
                continue
        if value is not None:
            kwargs[key] = value
    return kwargs


def build_dspy_lm(
    model: str,
    *,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    check: bool = False,
    **extra: Any,
):
    """Create a ``dspy.LM`` via :func:`dspy_lm_kwargs`.

    With ``check=True`` an Ollama model is preflighted with
    :func:`ensure_local_model_reachable` first.
    """
    import dspy

    kwargs = dspy_lm_kwargs(
        model, provider=provider, api_key=api_key, api_base=api_base, **extra
    )
    if check and is_ollama(kwargs["model"]):
        ensure_local_model_reachable(kwargs["model"], kwargs.get("api_base"))
    return dspy.LM(**kwargs)


def ensure_local_model_reachable(
    model: str,
    api_base: Optional[str] = None,
    *,
    provider: Optional[str] = None,
    timeout: float = 3.0,
) -> None:
    """Raise :class:`LocalModelUnreachableError` if Ollama cannot serve ``model``.

    Uses the native ``/api/tags`` endpoint, so it costs one small HTTP request
    and no generation. Non-Ollama models are not checked.
    """
    if not is_ollama(model, provider):
        return
    root = ollama_root(api_base)
    name = bare_ollama_name(model)
    try:
        with urllib.request.urlopen(f"{root}/api/tags", timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8") or "{}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        raise LocalModelUnreachableError(
            f"Ollama is not reachable at {root} ({reason}). "
            "Start it with 'ollama serve' or set language_model.api_base."
        ) from exc
    available = set()
    for entry in payload.get("models", []) or []:
        for key in ("name", "model"):
            if entry.get(key):
                available.add(str(entry[key]))
    candidates = {name} if ":" in name else {name, f"{name}:latest"}
    if available and not (candidates & available):
        raise LocalModelUnreachableError(
            f"Ollama at {root} does not have model '{name}'. "
            f"Run 'ollama pull {name}'. Available: {', '.join(sorted(available))}"
        )
    if not available:
        raise LocalModelUnreachableError(
            f"Ollama at {root} has no models. Run 'ollama pull {name}'."
        )
