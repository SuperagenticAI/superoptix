"""DSPy 3.5 readiness: no legacy LM integration interfaces (2.0)."""

import re
import warnings
from pathlib import Path
from unittest import mock

import pytest

import superoptix  # noqa: F401  (import superoptix before dspy)
import dspy

# tests/test_pipeline_integration.py swaps sys.modules["dspy"] for a Mock at
# import time; keep the real module for these tests.
_REAL_DSPY = dspy


@pytest.fixture(autouse=True)
def _real_dspy(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "dspy", _REAL_DSPY)


PKG = Path(superoptix.__file__).parent

LEGACY_PATTERNS = {
    "BaseLM subclass": re.compile(r"class\s+\w+\(\s*(dspy\.)?BaseLM\s*\)"),
    "LegacyEngine": re.compile(r"\b(Async)?LegacyEngine\b"),
    "complete_legacy": re.compile(r"\bcomplete_legacy\b"),
    "dspy.clients.openai_format": re.compile(r"dspy\.clients\.openai_format"),
    "dspy.core.types": re.compile(r"dspy\.core\.types"),
}


def test_no_legacy_dspy_lm_interfaces_in_package():
    hits = []
    for path in PKG.rglob("*.py"):
        if "dspy-latest" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in LEGACY_PATTERNS.items():
            if pattern.search(text):
                hits.append(f"{path.relative_to(PKG)}: {label}")
    assert not hits, hits


def _mlx_response(content):
    resp = mock.Mock(status_code=200)
    resp.json.return_value = {
        "id": "r1",
        "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
    }
    return resp


def test_mlx_engine_runs_without_deprecation_warnings():
    from superoptix.models.backends.mlx_dspy_client import (
        MLXDSPyClient,
        create_mlx_lm,
    )

    lm = create_mlx_lm("mlx-community/tiny", cache=False)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        with mock.patch(
            "requests.Session.post", return_value=_mlx_response("hello")
        ) as post:
            assert lm("hi") == ["hello"]
    payload = post.call_args.kwargs["json"]
    assert payload["model"] == "mlx-community/tiny"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert isinstance(MLXDSPyClient("m"), dspy.LM)


def test_mlx_engine_typed_request_and_errors():
    from dspy.lm15 import Message, Request, ServerError

    from superoptix.models.backends.mlx_dspy_client import MLXEngine

    engine = MLXEngine()
    req = Request(model="mlx/m", system="Be brief.", messages=(Message.user("q"),))
    with mock.patch("requests.Session.post", return_value=_mlx_response("a")) as p:
        out = engine.complete(req)
    assert out.message.text == "a" and out.usage.total_tokens == 4
    assert p.call_args.kwargs["json"]["messages"][0] == {
        "role": "system",
        "content": "Be brief.",
    }
    bad = mock.Mock(status_code=503, text="down")
    with mock.patch("requests.Session.post", return_value=bad):
        try:
            engine.complete(req)
        except ServerError:
            pass
        else:  # pragma: no cover
            raise AssertionError("expected ServerError")
