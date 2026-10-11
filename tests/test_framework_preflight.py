"""Non-DSPy runs fail loudly (exit 1) when their local Ollama model is down."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import yaml

import superoptix  # noqa: F401  (import superoptix before dspy)

DEAD_BASE = "http://127.0.0.1:9"  # discard port: nothing listens here


def _args(**kw):
    base = dict(provider=None, model=None, local=False, gateway=False, direct=False)
    base.update(kw)
    return SimpleNamespace(**base)


def _playbook(tmp_path, lm):
    path = tmp_path / "bot_playbook.yaml"
    path.write_text(yaml.safe_dump({"spec": {"language_model": lm}}))
    return path


def test_preflight_raises_for_unreachable_ollama(tmp_path):
    from superoptix.cli.commands.agent import _preflight_framework_model
    from superoptix.core.local_lm import LocalModelUnreachableError

    path = _playbook(
        tmp_path,
        {"provider": "ollama", "model": "qwen2.5:1.5b", "api_base": DEAD_BASE},
    )
    for framework in ("crewai", "openai", "google-adk", "pydantic-ai"):
        with pytest.raises(LocalModelUnreachableError, match="not reachable"):
            _preflight_framework_model(_args(), framework, path)


def test_preflight_accepts_loaded_playbook_dict():
    from superoptix.cli.commands.agent import _preflight_framework_model
    from superoptix.core.local_lm import LocalModelUnreachableError

    playbook = {
        "spec": {
            "language_model": {
                "provider": "ollama",
                "model": "llama3",
                "api_base": DEAD_BASE,
            }
        }
    }
    with pytest.raises(LocalModelUnreachableError):
        _preflight_framework_model(_args(), "microsoft", playbook)


def test_preflight_skips_hosted_and_claude(tmp_path):
    from superoptix.cli.commands.agent import _preflight_framework_model

    hosted = _playbook(tmp_path, {"provider": "openai", "model": "gpt-test"})
    _preflight_framework_model(_args(), "openai", hosted)
    local = _playbook(
        tmp_path, {"provider": "ollama", "model": "x", "api_base": DEAD_BASE}
    )
    _preflight_framework_model(_args(), "claude-sdk", local)


def test_cli_override_wins_over_playbook(tmp_path):
    from superoptix.cli.commands.agent import _framework_model_target

    path = _playbook(tmp_path, {"provider": "openai", "model": "gpt-test"})
    target = _framework_model_target(
        _args(provider="ollama", model="qwen2.5:1.5b"), "crewai", path
    )
    assert target["provider"] == "ollama" and target["model"] == "qwen2.5:1.5b"


def test_run_exits_one_when_model_unreachable(tmp_path, monkeypatch, capsys):
    from superoptix.cli.commands.agent import _run_framework_agent

    (tmp_path / ".super").write_text("project: demo\n")
    agent = tmp_path / "demo" / "agents" / "bot"
    (agent / "pipelines").mkdir(parents=True)
    (agent / "playbook").mkdir()
    (agent / "pipelines" / "bot_crewai_pipeline.py").write_text(
        "raise AssertionError('pipeline must not be imported')\n"
    )
    _playbook(
        agent / "playbook",
        {"provider": "ollama", "model": "qwen2.5:1.5b", "api_base": DEAD_BASE},
    )
    monkeypatch.chdir(tmp_path)
    args = _args(name="bot", goal="hi", observe="superoptix")
    with pytest.raises(SystemExit) as exc:
        _run_framework_agent(args, "crewai")
    assert exc.value.code == 1
    assert "Model unreachable" in capsys.readouterr().out
    assert "bot_crewai_pipeline" not in sys.modules


def test_microsoft_ollama_name_tag_is_not_a_provider_prefix():
    from superoptix.runners.microsoft_runtime_helpers import resolve_client_config

    cfg = resolve_client_config(
        {"provider": "ollama", "model": "qwen2.5:1.5b", "api_base": "http://h:11434"}
    )
    assert cfg["kwargs"]["model_id"] == "qwen2.5:1.5b"
    assert cfg["kwargs"]["base_url"] == "http://h:11434/v1"
    hosted = resolve_client_config({"provider": "ollama", "model": "openai:gpt-test"})
    assert hosted["kwargs"]["model_id"] == "gpt-test"


def test_deepagents_ollama_gets_context_window():
    from superoptix.runners.deepagents_runtime_helpers import chat_model_kwargs

    kw = chat_model_kwargs({"api_base": "http://h:11434/v1"}, "ollama:qwen2.5:1.5b")
    assert kw == {"base_url": "http://h:11434", "num_ctx": 16384}
    assert chat_model_kwargs({}, "openai:gpt-test") == {}


def test_minimal_dspy_serve_maps_a2a_query_to_playbook_input(tmp_path):
    from superoptix.cli.commands.agent import _MinimalDSPyServePipeline

    path = tmp_path / "dev_playbook.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "spec": {
                    "input_fields": [{"name": "feature_requirement"}],
                    "output_fields": [{"name": "implementation"}],
                }
            }
        )
    )

    class Module:
        @staticmethod
        def build_program():
            return lambda feature_requirement: {"implementation": feature_requirement}

    pipeline = _MinimalDSPyServePipeline(Module, path)
    assert pipeline.run(query="add two numbers") == {
        "implementation": "add two numbers"
    }
