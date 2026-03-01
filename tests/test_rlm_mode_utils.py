"""Unit tests for RLM auto mode resolution utilities."""

from superoptix.runners.rlm_mode_utils import resolve_effective_rlm_mode


def test_resolve_mode_explicit_assist():
    mode, reason = resolve_effective_rlm_mode(
        prompt="hello",
        config={"mode": "assist"},
    )
    assert mode == "assist"
    assert reason == "explicit"


def test_resolve_mode_auto_selects_replace_for_long_context():
    mode, reason = resolve_effective_rlm_mode(
        prompt="x" * 200,
        config={"mode": "auto", "auto_long_context_chars": 100},
    )
    assert mode == "replace"
    assert reason.startswith("auto_long_context")


def test_resolve_mode_auto_selects_direct_for_short_context_by_default():
    mode, reason = resolve_effective_rlm_mode(
        prompt="x" * 20,
        config={"mode": "auto", "auto_long_context_chars": 100},
    )
    assert mode == "direct"
    assert reason.startswith("auto_short_context_direct")


def test_resolve_mode_auto_selects_assist_for_short_context_when_configured():
    mode, reason = resolve_effective_rlm_mode(
        prompt="x" * 20,
        config={
            "mode": "auto",
            "auto_long_context_chars": 100,
            "auto_short_context_mode": "assist",
        },
    )
    assert mode == "assist"
    assert reason.startswith("auto_short_context_assist")


def test_resolve_mode_invalid_values_fallback_to_safe_defaults():
    mode, reason = resolve_effective_rlm_mode(
        prompt="x",
        config={
            "mode": "auto",
            "auto_long_context_chars": "invalid",
            "auto_short_context_mode": "unknown",
        },
    )
    assert mode == "direct"
    assert reason.startswith("auto_short_context_direct")
