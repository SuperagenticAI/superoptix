"""DSPy 3.4+ LM kwargs: Ollama is keyless and uses an OpenAI-compatible /v1 base."""

from superoptix.runners.dspy_runner import _dspy_lm_kwargs


def test_ollama_drops_empty_key_and_adds_v1():
    kw = _dspy_lm_kwargs(
        {
            "model_name": "ollama_chat/qwen2.5:1.5b",
            "api_key": "",
            "api_base": "http://localhost:11434/",
            "temperature": 0.0,
            "max_tokens": 64,
        }
    )
    assert "api_key" not in kw
    assert kw["api_base"] == "http://localhost:11434/v1"
    assert kw["model"] == "ollama_chat/qwen2.5:1.5b"
    assert kw["temperature"] == 0.0 and kw["max_tokens"] == 64


def test_ollama_without_base_and_existing_v1():
    # No base configured: the default Ollama /v1 base is used explicitly.
    assert _dspy_lm_kwargs({"model_name": "ollama_chat/m"})["api_base"] == (
        "http://localhost:11434/v1"
    )
    kw = _dspy_lm_kwargs({"model_name": "ollama/m", "api_base": "http://h:1/v1"})
    assert kw["api_base"] == "http://h:1/v1"


def test_cloud_keeps_key_and_extras_override():
    kw = _dspy_lm_kwargs(
        {"model_name": "openai/gpt-x", "api_key": "k", "temperature": 0.2},
        temperature=1.0,
        max_tokens=32000,
    )
    assert kw["api_key"] == "k"
    assert kw["temperature"] == 1.0 and kw["max_tokens"] == 32000
    assert "api_base" not in kw
