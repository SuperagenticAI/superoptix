"""Reflection LM wrapper for GEPA under DSPy 3.4+.

DSPy 3.4 returns LM outputs as ``dict`` objects (or ``AttributeDict``, a dict
subclass, when a response is replayed from the cache) of the form
``{"text": ..., "reasoning_content": ...}``. GEPA's default
``InstructionProposalSignature`` path (``DspyAdapter.stripped_lm_call``)
checks ``type(output) == dict`` exactly, so an ``AttributeDict`` raises
``TypeError: Unexpected output type from the base LM! Expected str or dict``
and the iteration silently proposes nothing. Thinking models such as
qwen3 can also return ``text=None`` with only ``reasoning_content``.

``ReflectionLM`` normalises every output to a plain ``str`` so the GEPA
proposer always receives text it can parse.
"""

from __future__ import annotations

from typing import Any, List

import dspy


def coerce_lm_output(output: Any) -> str:
    """Return the text of one DSPy LM output as a plain ``str``."""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        text = output.get("text")
        if isinstance(text, str) and text.strip():
            return text
        reasoning = output.get("reasoning_content")
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning
        return text if isinstance(text, str) else ""
    if output is None:
        return ""
    return str(output)


class ReflectionLM(dspy.LM):
    """``dspy.LM`` whose call results are always a list of plain strings."""

    def __call__(self, *args: Any, **kwargs: Any) -> List[str]:  # type: ignore[override]
        outputs = super().__call__(*args, **kwargs)
        if not isinstance(outputs, list):
            return outputs
        return [coerce_lm_output(o) for o in outputs]
