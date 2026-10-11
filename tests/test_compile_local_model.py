"""compile --local keeps the playbook's Ollama model instead of baking qwen3.5:9b."""

from superoptix.compiler.agent_compiler import _local_default_model


def test_playbook_ollama_model_is_kept():
    spec = {"language_model": {"provider": "ollama", "model": "qwen2.5:1.5b"}}
    assert _local_default_model(spec) is None


def test_default_used_when_playbook_has_no_local_model():
    assert _local_default_model({}) == "qwen3.5:9b"
    assert _local_default_model(None) == "qwen3.5:9b"
    cloud = {"language_model": {"provider": "openai", "model": "gpt-x"}}
    assert _local_default_model(cloud) == "qwen3.5:9b"
