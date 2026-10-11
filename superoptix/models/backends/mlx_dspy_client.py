"""DSPy LM for local MLX servers, as a DSPy engine.

DSPy 3.4 deprecates custom ``BaseLM.forward`` LMs and DSPy 3.5 removes them
(https://dspy.ai/current/community/normalized-lm-api-migration/). This module
implements the replacement: an engine with ``complete(Request) -> Response``
that speaks the MLX server's OpenAI-compatible chat endpoint, wrapped in a
normal ``dspy.LM``.

    lm = create_mlx_lm("mlx-community/Llama-3.2-3B-Instruct-4bit")
    dspy.configure(lm=lm)

``MLXDSPyClient(...)`` is kept as a factory with the old constructor
arguments; it now returns a ``dspy.LM``, not a ``BaseLM`` subclass.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)

_FINISH_REASONS = {"stop", "length", "tool_call", "content_filter", "error"}


def _lm15():
    try:
        from dspy import lm15
    except ImportError as exc:  # pragma: no cover - floor is dspy>=3.4
        raise ImportError(
            "The MLX DSPy engine needs DSPy 3.4 or newer (dspy.lm15). "
            'Install with: pip install "dspy>=3.4"'
        ) from exc
    return lm15


def _request_to_chat(request: Any) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    system = request.system
    if system:
        if not isinstance(system, str):
            system = "".join(str(getattr(p, "text", "") or "") for p in system)
        messages.append({"role": "system", "content": system})
    for message in request.messages:
        role = str(message.role)
        if role == "developer":
            role = "system"
        messages.append({"role": role, "content": message.text or ""})
    return messages


class MLXEngine:
    """Synchronous DSPy engine for an MLX server (OpenAI-compatible API)."""

    def __init__(
        self,
        api_base: str = "http://localhost:8000",
        timeout: float = 120,
        session: requests.Session | None = None,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    def close(self) -> None:
        self._session.close()

    def complete(self, request: Any) -> Any:
        lm15 = _lm15()
        config = request.config
        payload: Dict[str, Any] = {
            "model": request.model.split("/", 1)[1]
            if request.model.startswith("mlx/")
            else request.model,
            "messages": _request_to_chat(request),
            "stream": False,
        }
        if config.max_tokens is not None:
            payload["max_tokens"] = config.max_tokens
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        if config.top_p is not None:
            payload["top_p"] = config.top_p
        if config.stop:
            payload["stop"] = list(config.stop)
        try:
            response = self._session.post(
                f"{self.api_base}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise lm15.TimeoutError(f"MLX server timed out: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise lm15.TransportError(f"Failed to reach MLX server: {exc}") from exc
        if response.status_code >= 500:
            raise lm15.ServerError(
                f"MLX API error: {response.status_code} - {response.text}"
            )
        if response.status_code != 200:
            raise lm15.InvalidRequestError(
                f"MLX API error: {response.status_code} - {response.text}"
            )
        data = response.json()
        choice = (data.get("choices") or [{}])[0]
        text = str((choice.get("message") or {}).get("content") or "")
        finish = str(choice.get("finish_reason") or "stop")
        if finish not in _FINISH_REASONS:
            finish = "stop"
        usage = data.get("usage") or {}
        return lm15.Response(
            id=data.get("id"),
            model=request.model,
            message=lm15.Message.assistant(text),
            finish_reason=finish,
            usage=lm15.Usage(
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
            ),
        )


def create_mlx_lm(
    model: str,
    api_base: str = "http://localhost:8000",
    temperature: float = 0.0,
    max_tokens: int = 4000,
    timeout: float = 120,
    **kwargs: Any,
) -> Any:
    """Return a ``dspy.LM`` backed by :class:`MLXEngine`."""
    import dspy

    _lm15()
    name = model if model.startswith("mlx/") else f"mlx/{model}"
    return dspy.LM(
        name,
        engine=MLXEngine(api_base=api_base, timeout=timeout),
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )


def MLXDSPyClient(  # noqa: N802 - kept for import compatibility
    model: str,
    api_base: str = "http://localhost:8000",
    temperature: float = 0.0,
    max_tokens: int = 4000,
    **kwargs: Any,
) -> Any:
    """Backward-compatible factory. Returns a ``dspy.LM`` (engine based)."""
    return create_mlx_lm(
        model,
        api_base=api_base,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
