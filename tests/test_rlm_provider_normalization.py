"""Tests for framework RLM provider normalization and validation."""

import pytest

from superoptix.runners.crewai_runtime_helpers import get_crewai_rlm_config
from superoptix.runners.deepagents_runtime_helpers import get_deepagents_rlm_config
from superoptix.runners.google_adk_runtime_helpers import get_google_adk_rlm_config
from superoptix.runners.openai_runtime_helpers import (
    get_openai_rlm_config,
    get_openai_sandbox_config,
)
from superoptix.runners.pydantic_runtime_helpers import get_pydantic_rlm_config
from superoptix.superspec.validator import SuperSpecXValidator


CONFIG_GETTERS = [
    ("pydantic_ai", get_pydantic_rlm_config),
    ("openai_agent", get_openai_rlm_config),
    ("google_adk", get_google_adk_rlm_config),
    ("deepagents", get_deepagents_rlm_config),
    ("crewai", get_crewai_rlm_config),
]


@pytest.mark.parametrize(("framework_key", "get_config"), CONFIG_GETTERS)
def test_framework_rlm_provider_defaults_to_native(framework_key, get_config):
    spec = {framework_key: {"rlm": {"enabled": True}}}
    cfg = get_config(spec)
    assert cfg["provider"] == "native"
    assert cfg["auto_long_context_chars"] == 12000
    assert cfg["auto_short_context_mode"] == "direct"


@pytest.mark.parametrize(("framework_key", "get_config"), CONFIG_GETTERS)
def test_framework_rlm_provider_legacy_alias_maps_to_native(framework_key, get_config):
    spec = {framework_key: {"rlm": {"enabled": True, "provider": "legacy"}}}
    cfg = get_config(spec)
    assert cfg["provider"] == "native"


@pytest.mark.parametrize(("framework_key", "get_config"), CONFIG_GETTERS)
def test_framework_rlm_provider_rlm_code_preserved(framework_key, get_config):
    spec = {framework_key: {"rlm": {"enabled": True, "provider": "rlm_code"}}}
    cfg = get_config(spec)
    assert cfg["provider"] == "rlm_code"


@pytest.mark.parametrize(("framework_key", "get_config"), CONFIG_GETTERS)
def test_framework_rlm_auto_mode_fields_are_normalized(framework_key, get_config):
    spec = {
        framework_key: {
            "rlm": {
                "enabled": True,
                "mode": "auto",
                "auto_long_context_chars": 9000,
                "auto_short_context_mode": "assist",
            }
        }
    }
    cfg = get_config(spec)
    assert cfg["mode"] == "auto"
    assert cfg["auto_long_context_chars"] == 9000
    assert cfg["auto_short_context_mode"] == "assist"


VALIDATOR_METHODS = [
    ("_validate_pydantic_ai_config", "pydantic_ai"),
    ("_validate_openai_agent_config", "openai_agent"),
    ("_validate_google_adk_config", "google_adk"),
    ("_validate_deepagents_config", "deepagents"),
    ("_validate_crewai_config", "crewai"),
]


@pytest.mark.parametrize(("method_name", "label"), VALIDATOR_METHODS)
@pytest.mark.parametrize("provider", ["native", "rlm_code", "legacy"])
def test_validator_accepts_supported_framework_rlm_providers(
    method_name, label, provider
):
    validator = SuperSpecXValidator()
    validator.errors = []
    method = getattr(validator, method_name)

    method({"rlm": {"enabled": True, "provider": provider}})

    assert validator.errors == []


@pytest.mark.parametrize(("method_name", "label"), VALIDATOR_METHODS)
def test_validator_accepts_auto_mode_settings(method_name, label):
    validator = SuperSpecXValidator()
    validator.errors = []
    method = getattr(validator, method_name)

    method(
        {
            "rlm": {
                "enabled": True,
                "mode": "auto",
                "auto_long_context_chars": 9000,
                "auto_short_context_mode": "assist",
            }
        }
    )

    assert validator.errors == []


@pytest.mark.parametrize(("method_name", "label"), VALIDATOR_METHODS)
def test_validator_rejects_unknown_framework_rlm_provider(method_name, label):
    validator = SuperSpecXValidator()
    validator.errors = []
    method = getattr(validator, method_name)

    method({"rlm": {"enabled": True, "provider": "unknown"}})

    assert any(
        err.startswith(f"{label}.rlm.provider must be one of:")
        for err in validator.errors
    )


@pytest.mark.parametrize(("method_name", "label"), VALIDATOR_METHODS)
def test_validator_rejects_invalid_auto_mode_fields(method_name, label):
    validator = SuperSpecXValidator()
    validator.errors = []
    method = getattr(validator, method_name)

    method(
        {
            "rlm": {
                "enabled": True,
                "mode": "auto",
                "auto_long_context_chars": 0,
                "auto_short_context_mode": "bad-mode",
            }
        }
    )

    assert any(
        err == f"{label}.rlm.auto_long_context_chars must be an integer >= 1"
        for err in validator.errors
    )
    assert any(
        err == f"{label}.rlm.auto_short_context_mode must be one of: direct, assist"
        for err in validator.errors
    )


def test_openai_sandbox_config_defaults_disabled():
    cfg = get_openai_sandbox_config({})
    assert cfg["enabled"] is False
    assert cfg["client"] == "unix_local"
    assert cfg["docker_image"] == "python:3.14-slim"
    assert cfg["manifest_local_dirs"] == []
    assert cfg["manifest_local_files"] == []
    assert cfg["manifest_git_repos"] == []


def test_openai_sandbox_config_normalizes_manifest_entries():
    cfg = get_openai_sandbox_config(
        {
            "openai_agent": {
                "sandbox": {
                    "enabled": True,
                    "client": "unix-local",
                    "manifest": {
                        "root": "/workspace",
                        "local_dirs": [
                            {"path": "data", "src": "./data"},
                            {"path": "", "src": "./skip"},
                        ],
                        "local_files": [
                            {"path": "README.md", "src": "./README.md"},
                        ],
                        "git_repos": [
                            {
                                "path": "sdk",
                                "url": "https://github.com/openai/openai-agents-python.git",
                                "ref": "main",
                            }
                        ],
                    },
                }
            }
        }
    )
    assert cfg["enabled"] is True
    assert cfg["client"] == "unix_local"
    assert cfg["manifest_root"] == "/workspace"
    assert cfg["manifest_local_dirs"] == [{"path": "data", "src": "./data"}]
    assert cfg["manifest_local_files"] == [{"path": "README.md", "src": "./README.md"}]
    assert cfg["manifest_git_repos"] == [
        {
            "path": "sdk",
            "url": "https://github.com/openai/openai-agents-python.git",
            "ref": "main",
        }
    ]


def test_openai_validator_accepts_sandbox_config():
    validator = SuperSpecXValidator()
    validator.errors = []
    validator._validate_openai_agent_config(
        {
            "sandbox": {
                "enabled": True,
                "client": "docker",
                "docker_image": "python:3.14-slim",
                "workflow_name": "sandbox workflow",
                "manifest": {
                    "root": "/workspace",
                    "local_dirs": [{"path": "data", "src": "./data"}],
                    "local_files": [{"path": "task.md", "src": "./task.md"}],
                    "git_repos": [
                        {
                            "path": "repo",
                            "url": "https://github.com/openai/openai-agents-python.git",
                            "ref": "main",
                        }
                    ],
                },
            }
        }
    )
    assert validator.errors == []


def test_openai_validator_rejects_unknown_sandbox_client():
    validator = SuperSpecXValidator()
    validator.errors = []
    validator._validate_openai_agent_config(
        {"sandbox": {"enabled": True, "client": "unknown"}}
    )
    assert (
        "openai_agent.sandbox.client must be one of: unix_local, docker"
        in validator.errors
    )


def test_openai_validator_rejects_bad_manifest_entries():
    validator = SuperSpecXValidator()
    validator.errors = []
    validator._validate_openai_agent_config(
        {
            "sandbox": {
                "enabled": True,
                "manifest": {"local_dirs": [{"path": "", "src": ""}]},
            }
        }
    )
    assert any(
        err.startswith("openai_agent.sandbox.manifest.local_dirs[0].path")
        for err in validator.errors
    )
    assert any(
        err.startswith("openai_agent.sandbox.manifest.local_dirs[0].src")
        for err in validator.errors
    )
