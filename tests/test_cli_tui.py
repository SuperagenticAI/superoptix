"""Tests for TUI helpers."""

from superoptix.cli.commands.tui import (
    _default_acp_command,
    _default_byok_base_url,
    _default_local_endpoint,
    _extract_openai_text,
    _fmt_kvs,
    _normalize_local_endpoint,
    _split_provider_model_token,
)


def test_default_acp_command_mapping():
    assert _default_acp_command("opencode") == "opencode acp"
    assert _default_acp_command("claude-code") == "claude-code acp"
    assert _default_acp_command("unknown-agent") is None


def test_fmt_kvs_handles_missing_values():
    data = {"provider": "openai", "model": "gpt-4o", "api_key_env": ""}
    result = _fmt_kvs(data, ["provider", "model", "api_key_env"])
    assert "provider=openai" in result
    assert "model=gpt-4o" in result
    assert "api_key_env" not in result


def test_extract_openai_text_from_payload():
    payload = {
        "choices": [
            {
                "message": {
                    "content": "hello world",
                }
            }
        ]
    }
    assert _extract_openai_text(payload) == "hello world"
    assert _extract_openai_text({}) == ""


def test_default_endpoint_and_byok_url_resolution():
    assert _default_local_endpoint("ollama", None).endswith("/api/chat")
    assert _default_local_endpoint("vllm", None).endswith("/v1/chat/completions")
    assert _default_local_endpoint("ollama", "http://127.0.0.1:11434/api/chat") == "http://127.0.0.1:11434/api/chat"
    assert _default_local_endpoint("ollama", "http://localhost:11434") == "http://localhost:11434/api/chat"
    assert _default_local_endpoint("lmstudio", "http://localhost:1234/v1") == "http://localhost:1234/v1/chat/completions"
    assert _default_byok_base_url("openai", None).startswith("https://api.openai.com/")
    assert _default_byok_base_url("anthropic", None).endswith("/v1/messages")


def test_split_provider_model_token():
    assert _split_provider_model_token("openai/gpt-4o") == ("openai", "gpt-4o")
    assert _split_provider_model_token("ollama", "llama3.2:3b") == ("ollama", "llama3.2:3b")
    assert _split_provider_model_token(None) == (None, None)


def test_normalize_local_endpoint():
    assert _normalize_local_endpoint("ollama", "http://localhost:11434") == "http://localhost:11434/api/chat"
    assert _normalize_local_endpoint("ollama", "http://localhost:11434/api/tags") == "http://localhost:11434/api/chat"
    assert _normalize_local_endpoint("lmstudio", "http://localhost:1234/v1") == "http://localhost:1234/v1/chat/completions"
