"""Mapping helpers between A2A transport objects and SuperOptiX runtime payloads."""

from __future__ import annotations

import json
from typing import Any, Dict


def extract_text_from_message(message: Any) -> str:
    """Best-effort extraction of user text from an A2A message."""
    parts = list(getattr(message, "parts", []) or [])
    texts = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            texts.append(str(text))
    return "\n".join(texts).strip()


def runtime_result_to_text(result: Dict[str, Any]) -> str:
    """Render a runtime result as agent-visible text for A2A responses."""
    if "response" in result:
        return str(result["response"])
    if len(result) == 1:
        return str(next(iter(result.values())))
    return json.dumps(result, sort_keys=True)
