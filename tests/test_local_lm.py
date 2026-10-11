"""Shared local LM helper: one place for the DSPy 3.4+ Ollama credential fix."""

import http.server
import json
import pathlib
import re
import threading

import pytest

from superoptix.core import local_lm
from superoptix.core.local_lm import (
    LocalModelUnreachableError,
    build_dspy_lm,
    dspy_lm_kwargs,
    ensure_local_model_reachable,
    ollama_model_id,
)


@pytest.mark.parametrize(
    "spelling",
    ["qwen2.5:1.5b", "ollama:qwen2.5:1.5b", "ollama/qwen2.5:1.5b"],
)
def test_ollama_model_id_spellings(spelling):
    assert ollama_model_id(spelling) == "ollama_chat/qwen2.5:1.5b"


@pytest.mark.parametrize("key", ["", "   ", None, "ollama"])
def test_ollama_never_gets_empty_or_placeholder_key(key):
    kw = dspy_lm_kwargs(
        "m", provider="ollama", api_key=key, api_base="http://h:1/", temperature=0
    )
    assert "api_key" not in kw
    assert kw == {
        "model": "ollama_chat/m",
        "api_base": "http://h:1/v1",
        "temperature": 0,
    }


def test_ollama_real_key_kept_and_provider_dropped():
    kw = dspy_lm_kwargs(
        "ollama_chat/m", api_key="secret", provider="ollama", max_tokens=None
    )
    assert kw["api_key"] == "secret"
    assert "provider" not in kw and "max_tokens" not in kw


def test_hosted_provider_untouched_but_empty_key_dropped():
    assert dspy_lm_kwargs("openai/gpt-x", api_key="") == {"model": "openai/gpt-x"}
    assert dspy_lm_kwargs("openai/gpt-x", api_key="k")["api_key"] == "k"


def test_max_retries_mapped_to_num_retries():
    kw = dspy_lm_kwargs("m", provider="ollama", max_retries=2, timeout=30)
    assert "max_retries" not in kw
    assert kw["num_retries"] == 2 and kw["timeout"] == 30


def test_custom_openai_rewritten_for_dspy34():
    kw = dspy_lm_kwargs(
        "custom_openai/mlx-model", api_base="http://localhost:8000", api_key="dummy-key"
    )
    assert kw == {
        "model": "openai/mlx-model",
        "api_base": "http://localhost:8000/v1",
        "api_key": "local",
    }


def test_build_dspy_lm_constructs_keyless_ollama_lm(monkeypatch):
    import dspy

    seen = {}
    monkeypatch.setattr(dspy, "LM", lambda **kw: seen.update(kw) or "lm")
    assert build_dspy_lm("qwen2.5:1.5b", provider="ollama", api_key="") == "lm"
    assert seen == {
        "model": "ollama_chat/qwen2.5:1.5b",
        "api_base": "http://localhost:11434/v1",
    }


class _Tags(http.server.BaseHTTPRequestHandler):
    models = [{"name": "qwen2.5:1.5b", "model": "qwen2.5:1.5b"}]

    def do_GET(self):  # noqa: N802
        body = json.dumps({"models": self.models}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


@pytest.fixture
def fake_ollama():
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Tags)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_reachable_model_passes(fake_ollama):
    ensure_local_model_reachable("ollama_chat/qwen2.5:1.5b", f"{fake_ollama}/v1")


def test_missing_model_fails_loudly(fake_ollama):
    with pytest.raises(LocalModelUnreachableError, match="ollama pull llama9"):
        ensure_local_model_reachable("llama9", fake_ollama, provider="ollama")


def test_down_server_fails_loudly():
    with pytest.raises(LocalModelUnreachableError, match="not reachable"):
        ensure_local_model_reachable("ollama_chat/m", "http://127.0.0.1:9", timeout=0.5)


def test_hosted_models_are_not_probed():
    ensure_local_model_reachable("openai/gpt-x", "http://127.0.0.1:9")


def test_runner_preflight_raises_before_setup(monkeypatch):
    from superoptix.runners import dspy_runner

    with pytest.raises(LocalModelUnreachableError):
        dspy_runner._preflight_lm(
            {"model_name": "ollama_chat/m", "api_base": "http://127.0.0.1:9"}
        )


def test_no_hand_rolled_empty_ollama_keys_remain():
    """Guard: Ollama LM construction must go through superoptix.core.local_lm."""
    root = pathlib.Path(local_lm.__file__).resolve().parents[1]
    offenders = []
    for path in list(root.rglob("*.py")) + list(root.rglob("*.jinja2")):
        if path.name == "local_lm.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"api_key\s*=\s*(''|\"\")", text) or re.search(
            r"[\"']api_key[\"']\s*:\s*(''|\"\")", text
        ):
            offenders.append(str(path.relative_to(root)))
        if (
            "custom_openai/" in text
            and "build_dspy_lm" not in text
            and ("dspy_lm_kwargs" not in text)
        ):
            offenders.append(f"{path.relative_to(root)} (custom_openai)")
    assert offenders == []


def test_cli_detects_wrapped_transport_errors():
    from superoptix.cli.commands.agent import _is_lm_transport_error

    class LMTransportError(Exception):
        pass

    try:
        try:
            raise LMTransportError("refused")
        except LMTransportError as inner:
            raise RuntimeError("pipeline failed") from inner
    except RuntimeError as outer:
        assert _is_lm_transport_error(outer)
    assert not _is_lm_transport_error(ValueError("x"))
