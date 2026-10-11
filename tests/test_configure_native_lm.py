"""Standalone evaluate/test must configure the task LM for native DSPy modules."""

from pathlib import Path

from superoptix.runners.dspy_runner import DSPyRunner


class _Module:
    ALLOW_LOCAL_OLLAMA = True
    RUNTIME_MODE = "local"

    def __init__(self):
        self.calls = []

    def setup_lm(self, **params):
        self.calls.append(params)


def test_configure_native_lm_uses_playbook_model(tmp_path: Path):
    playbook = tmp_path / "p.yaml"
    playbook.write_text(
        "spec:\n  language_model:\n    provider: ollama\n    model: qwen2.5:1.5b\n"
    )
    runner = DSPyRunner.__new__(DSPyRunner)
    runner.playbook_path = playbook
    runner._configure_dspy_adapter = lambda spec, module: None
    module = _Module()
    runner.configure_native_lm(module)
    assert module.calls and module.calls[0]["model_name"] == "ollama_chat/qwen2.5:1.5b"
    assert not module.calls[0].get("api_key")
