"""Shared RLM mode resolution utilities for framework runners."""

from __future__ import annotations

from typing import Any, Dict, Tuple


def resolve_effective_rlm_mode(
    *,
    prompt: str,
    config: Dict[str, Any],
    default_mode: str = "assist",
) -> Tuple[str, str]:
    """
    Resolve effective RLM mode.

    Returns:
        (effective_mode, resolution_reason)

    Effective mode is one of:
    - "assist"
    - "replace"
    - "direct" (framework-native execution without invoking RLM)
    """
    mode = str(config.get("mode", default_mode)).strip().lower() or default_mode
    if mode not in {"assist", "replace", "auto"}:
        mode = default_mode

    if mode != "auto":
        return mode, "explicit"

    threshold_raw = config.get("auto_long_context_chars", 12000)
    try:
        threshold = int(threshold_raw or 12000)
    except Exception:
        threshold = 12000
    if threshold < 1:
        threshold = 1

    short_mode = (
        str(config.get("auto_short_context_mode", "direct")).strip().lower()
        or "direct"
    )
    if short_mode not in {"direct", "assist"}:
        short_mode = "direct"

    prompt_len = len(str(prompt or ""))
    if prompt_len >= threshold:
        return "replace", f"auto_long_context(len={prompt_len}, threshold={threshold})"
    if short_mode == "assist":
        return "assist", f"auto_short_context_assist(len={prompt_len}, threshold={threshold})"
    return "direct", f"auto_short_context_direct(len={prompt_len}, threshold={threshold})"
