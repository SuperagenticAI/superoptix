"""Offline tests for the GEPA reflection LM output normalisation."""

import dspy
import pytest
from dspy.clients.call_result import AttributeDict

from superoptix.core.reflection_lm import ReflectionLM, coerce_lm_output


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("plain", "plain"),
        ({"text": "t"}, "t"),
        (AttributeDict({"text": "cached"}), "cached"),
        ({"text": None, "reasoning_content": "```new```"}, "```new```"),
        ({"text": "", "reasoning_content": None}, ""),
        (None, ""),
    ],
)
def test_coerce_lm_output(raw, expected):
    out = coerce_lm_output(raw)
    assert type(out) is str
    assert out == expected


def test_reflection_lm_returns_plain_strings(monkeypatch):
    def fake_call(self, *args, **kwargs):
        return [AttributeDict({"text": "```Be concise.```"}), {"text": None, "reasoning_content": "r"}]

    monkeypatch.setattr(dspy.LM, "__call__", fake_call)
    lm = ReflectionLM(model="ollama_chat/qwen3:8b", api_base="http://localhost:1/v1")
    assert lm("prompt") == ["```Be concise.```", "r"]


def test_gepa_stripped_lm_call_accepts_cached_outputs(monkeypatch):
    """GEPA's DspyAdapter rejects AttributeDict; ReflectionLM must not."""
    from dspy.teleprompt.gepa.gepa_utils import DspyAdapter

    def fake_call(self, *args, **kwargs):
        return [AttributeDict({"text": "```Improved instruction```"})]

    monkeypatch.setattr(dspy.LM, "__call__", fake_call)
    adapter = DspyAdapter.__new__(DspyAdapter)

    adapter.reflection_lm = dspy.LM(model="ollama_chat/qwen3:8b", api_base="http://localhost:1/v1")
    with pytest.raises(TypeError):
        adapter.stripped_lm_call("x")

    adapter.reflection_lm = ReflectionLM(model="ollama_chat/qwen3:8b", api_base="http://localhost:1/v1")
    assert adapter.stripped_lm_call("x") == ["```Improved instruction```"]

    from gepa.strategies.instruction_proposal import InstructionProposalSignature

    res = InstructionProposalSignature.run(
        lm=lambda p: adapter.stripped_lm_call(p)[0],
        input_dict={
            "current_instruction_doc": "old",
            "dataset_with_feedback": [{"Inputs": {"q": "a"}, "Generated Outputs": "b", "Feedback": "c"}],
        },
    )
    assert res["new_instruction"] == "Improved instruction"


def test_import_superoptix_after_dspy_subprocess():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-c", "import dspy, superoptix; import numpy; print(numpy.zeros(2).sum())"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr[-2000:]
