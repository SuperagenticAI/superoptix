"""Tests for SuperOptiX CLI."""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from superoptix.cli.commands.agent import _find_prebuilt_playbook, _run_framework_agent
from superoptix.cli.commands.harness import (
    _build_model_config,
    _build_playbook_system_prompt,
    _find_harness_playbook,
    _parse_key_value_args,
)
from superoptix.cli.main import _requires_project_context
from superoptix.cli.utils import is_superoptix_project, validate_superoptix_project
from superoptix.runners.crewai_runtime_helpers import build_task_description
from superoptix.runners.microsoft_runtime_helpers import (
    GOOGLE_OPENAI_BASE_URL,
    resolve_client_config,
)


def test_is_superoptix_project_with_super_file():
    """Test is_superoptix_project returns True when .super file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .super file
        super_file = Path(temp_dir) / ".super"
        super_file.write_text("project: test\nversion: 0.1.0\n")

        # Change to the temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            assert is_superoptix_project() is True
        finally:
            os.chdir(original_cwd)


def test_is_superoptix_project_without_super_file():
    """Test is_superoptix_project returns False when .super file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            assert is_superoptix_project() is False
        finally:
            os.chdir(original_cwd)


def test_validate_superoptix_project_with_super_file():
    """Test validate_superoptix_project doesn't raise when .super file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .super file
        super_file = Path(temp_dir) / ".super"
        super_file.write_text("project: test\nversion: 0.1.0\n")

        # Change to the temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Should not raise an exception
            validate_superoptix_project()
        finally:
            os.chdir(original_cwd)


def test_validate_superoptix_project_without_super_file():
    """Test validate_superoptix_project raises SystemExit when .super file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            with pytest.raises(SystemExit) as exc_info:
                validate_superoptix_project()
            assert exc_info.value.code == 1
        finally:
            os.chdir(original_cwd)


@patch("superoptix.cli.utils.console.print")
def test_validate_superoptix_project_error_message(mock_print):
    """Test that validate_superoptix_project shows appropriate error message."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temp directory (no .super file)
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            with pytest.raises(SystemExit):
                validate_superoptix_project()

            # Check that error message was printed
            mock_print.assert_called()
            # Get all calls and check if any contains the error message
            all_calls = [str(call) for call in mock_print.call_args_list]
            # Rich formatting includes tags, so check for the text content in any call
            assert any(
                "❌ Not in a SuperOptiX project directory" in str(call)
                for call in all_calls
            )
        finally:
            os.chdir(original_cwd)


def test_find_prebuilt_playbook_resolves_framework_specific_surrealdb_variant(
    tmp_path: Path,
):
    package_root = tmp_path / "superoptix"
    playbook_path = (
        package_root / "agents" / "demo" / "rag_surrealdb_dspy_demo_playbook.yaml"
    )
    playbook_path.parent.mkdir(parents=True)
    playbook_path.write_text(
        yaml.safe_dump(
            {
                "metadata": {
                    "id": "rag_surrealdb_dspy_demo",
                    "name": "RAG SurrealDB DSPy Demo",
                }
            }
        )
    )

    resolved = _find_prebuilt_playbook(package_root, "rag_surrealdb_dspy_demo")

    assert resolved == playbook_path


def test_find_prebuilt_playbook_matches_normalized_metadata_id(tmp_path: Path):
    package_root = tmp_path / "superoptix"
    playbook_path = (
        package_root / "agents" / "demo" / "rag_surrealdb_openai_demo_playbook.yaml"
    )
    playbook_path.parent.mkdir(parents=True)
    playbook_path.write_text(
        yaml.safe_dump(
            {
                "metadata": {
                    "id": "rag_surrealdb_openai_demo",
                    "name": "RAG SurrealDB OpenAI Demo",
                }
            }
        )
    )

    resolved = _find_prebuilt_playbook(package_root, "rag-surrealdb-openai-demo")

    assert resolved == playbook_path


def test_requires_project_context_allows_prebuilt_agent_listing():
    args = SimpleNamespace(command="agent", agent_command="list", pre_built=True)

    assert _requires_project_context(args) is False


def test_requires_project_context_still_requires_project_for_agent_pull():
    args = SimpleNamespace(
        command="agent", agent_command="pull", pre_built=False, name="developer"
    )

    assert _requires_project_context(args) is True


def test_requires_project_context_for_harness_commands():
    args = SimpleNamespace(command="harness", harness_command="run")

    assert _requires_project_context(args) is True


def test_find_harness_playbook_resolves_project_agent(tmp_path: Path):
    playbook_path = (
        tmp_path / "demo" / "agents" / "developer" / "playbook" / "developer_playbook.yaml"
    )
    playbook_path.parent.mkdir(parents=True)
    playbook_path.write_text("metadata:\n  name: Developer\n")

    assert _find_harness_playbook(tmp_path, "demo", "developer") == playbook_path


def test_build_playbook_system_prompt_includes_persona_tasks_and_constraints():
    prompt = _build_playbook_system_prompt(
        {
            "metadata": {"description": "Writes code"},
            "spec": {
                "persona": {
                    "role": "Developer",
                    "goal": "Ship working changes",
                    "instructions": "Use tests.",
                },
                "tasks": [{"instruction": "Inspect the codebase first."}],
                "constraints": ["Keep changes scoped."],
            },
        }
    )

    assert "Agent description: Writes code" in prompt
    assert "Role:\nDeveloper" in prompt
    assert "1. Inspect the codebase first." in prompt
    assert "- Keep changes scoped." in prompt


def test_parse_key_value_args_coerces_json_scalars():
    parsed = _parse_key_value_args(
        ["issue=123", "dry_run=true", "labels=[\"bug\"]", "note=hello"]
    )

    assert parsed == {
        "issue": 123,
        "dry_run": True,
        "labels": ["bug"],
        "note": "hello",
    }


def test_build_model_config_prefers_explicit_values_over_local_defaults():
    args = SimpleNamespace(
        provider="google-genai",
        model="gemini-2.5-flash",
        local=True,
        codex_bin=None,
        pydantic_request_limit=None,
        pydantic_tool_calls_limit=None,
        pydantic_input_tokens_limit=None,
        pydantic_output_tokens_limit=None,
        pydantic_total_tokens_limit=None,
        pydantic_count_tokens_before_request=False,
        pydantic_code_mode=False,
    )

    assert _build_model_config(args) == {
        "provider": "google-genai",
        "model": "gemini-2.5-flash",
    }


def test_build_model_config_includes_codex_bin():
    args = SimpleNamespace(
        provider=None,
        model="gpt-5.4",
        local=False,
        codex_bin="/opt/bin/codex",
        pydantic_request_limit=None,
        pydantic_tool_calls_limit=None,
        pydantic_input_tokens_limit=None,
        pydantic_output_tokens_limit=None,
        pydantic_total_tokens_limit=None,
        pydantic_count_tokens_before_request=False,
        pydantic_code_mode=False,
    )

    assert _build_model_config(args) == {
        "model": "gpt-5.4",
        "codex_bin": "/opt/bin/codex",
    }


def test_build_model_config_includes_pydantic_ai_controls():
    args = SimpleNamespace(
        provider=None,
        model=None,
        local=False,
        codex_bin=None,
        pydantic_request_limit=5,
        pydantic_tool_calls_limit=12,
        pydantic_input_tokens_limit=None,
        pydantic_output_tokens_limit=1000,
        pydantic_total_tokens_limit=None,
        pydantic_count_tokens_before_request=True,
        pydantic_code_mode=True,
    )

    assert _build_model_config(args) == {
        "pydantic_usage_limits": {
            "request_limit": 5,
            "tool_calls_limit": 12,
            "output_tokens_limit": 1000,
            "count_tokens_before_request": True,
        },
        "pydantic_code_mode": True,
    }


def test_build_model_config_includes_deepagents_controls():
    args = SimpleNamespace(
        provider=None,
        model=None,
        local=False,
        codex_bin=None,
        pydantic_request_limit=None,
        pydantic_tool_calls_limit=None,
        pydantic_input_tokens_limit=None,
        pydantic_output_tokens_limit=None,
        pydantic_total_tokens_limit=None,
        pydantic_count_tokens_before_request=False,
        pydantic_code_mode=False,
        deepagents_skill_source=["/.agents/skills"],
        deepagents_memory=["/AGENTS.md"],
        deepagents_checkpointer="memory",
        deepagents_debug=True,
    )

    assert _build_model_config(args) == {
        "deepagents": {
            "skills": ["/.agents/skills"],
            "memory": ["/AGENTS.md"],
            "checkpointer": "memory",
            "debug": True,
        }
    }


def test_crewai_task_description_includes_runtime_query_placeholder():
    description = build_task_description(
        {
            "tasks": [
                {
                    "instruction": "Answer the user query directly from retrieved context.",
                }
            ]
        }
    )

    assert "{query}" in description


def test_run_framework_agent_passes_model_config_to_crewai_pipeline(tmp_path: Path):
    project_root = tmp_path
    (project_root / ".super").write_text("project: demo\n")

    pipeline_dir = (
        project_root / "demo" / "agents" / "demo_agent" / "pipelines"
    )
    pipeline_dir.mkdir(parents=True)
    capture_path = project_root / "captured_model_config.json"

    pipeline_file = pipeline_dir / "demo_agent_crewai_pipeline.py"
    pipeline_file.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "",
                "class DemoAgentPipeline:",
                "    def __init__(self, model_config=None):",
                "        capture_path = os.environ['SUPEROPTIX_CAPTURE_MODEL_CONFIG']",
                "        with open(capture_path, 'w', encoding='utf-8') as handle:",
                "            json.dump(model_config or {}, handle)",
                "",
                "    def run(self, query=None, **inputs):",
                "        return {'retrieved_response': query or inputs.get('query', '')}",
            ]
        )
    )

    args = SimpleNamespace(
        name="demo_agent",
        goal="What is NEON-FOX-742?",
        provider="google-genai",
        model="gemini-2.5-flash",
        local=False,
        gateway=False,
        direct=False,
        gateway_url=None,
        gateway_key_env=None,
    )

    original_cwd = os.getcwd()
    original_capture = os.environ.get("SUPEROPTIX_CAPTURE_MODEL_CONFIG")
    os.chdir(project_root)
    os.environ["SUPEROPTIX_CAPTURE_MODEL_CONFIG"] = str(capture_path)

    try:
        _run_framework_agent(args, "crewai")
    finally:
        os.chdir(original_cwd)
        if original_capture is None:
            os.environ.pop("SUPEROPTIX_CAPTURE_MODEL_CONFIG", None)
        else:
            os.environ["SUPEROPTIX_CAPTURE_MODEL_CONFIG"] = original_capture

    captured = yaml.safe_load(capture_path.read_text())
    assert captured == {
        "provider": "google-genai",
        "model": "gemini-2.5-flash",
    }


def test_resolve_microsoft_client_config_for_google_genai(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key")

    config = resolve_client_config(
        {"provider": "ollama", "model": "qwen3.5:9b", "api_base": "http://localhost:11434"},
        {"provider": "google-genai", "model": "gemini-2.5-flash"},
    )

    assert config == {
        "client_type": "openai",
        "kwargs": {
            "api_key": "google-test-key",
            "base_url": GOOGLE_OPENAI_BASE_URL,
            "model_id": "gemini-2.5-flash",
        },
    }


def test_run_framework_agent_passes_model_config_to_microsoft_pipeline(tmp_path: Path):
    project_root = tmp_path
    (project_root / ".super").write_text("project: demo\n")

    pipeline_dir = project_root / "demo" / "agents" / "demo_agent" / "pipelines"
    pipeline_dir.mkdir(parents=True)
    capture_path = project_root / "captured_microsoft_model_config.json"

    pipeline_file = pipeline_dir / "demo_agent_microsoft_pipeline.py"
    pipeline_file.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "",
                "class DemoAgentPipeline:",
                "    def __init__(self, model_config=None):",
                "        capture_path = os.environ['SUPEROPTIX_CAPTURE_MODEL_CONFIG']",
                "        with open(capture_path, 'w', encoding='utf-8') as handle:",
                "            json.dump(model_config or {}, handle)",
                "",
                "    async def run(self, query=None, **inputs):",
                "        return {'retrieved_response': query or inputs.get('query', '')}",
            ]
        )
    )

    args = SimpleNamespace(
        name="demo_agent",
        goal="What is NEON-FOX-742?",
        provider="google-genai",
        model="gemini-2.5-flash",
        local=False,
        gateway=False,
        direct=False,
        gateway_url=None,
        gateway_key_env=None,
    )

    original_cwd = os.getcwd()
    original_capture = os.environ.get("SUPEROPTIX_CAPTURE_MODEL_CONFIG")
    os.chdir(project_root)
    os.environ["SUPEROPTIX_CAPTURE_MODEL_CONFIG"] = str(capture_path)

    try:
        _run_framework_agent(args, "microsoft")
    finally:
        os.chdir(original_cwd)
        if original_capture is None:
            os.environ.pop("SUPEROPTIX_CAPTURE_MODEL_CONFIG", None)
        else:
            os.environ["SUPEROPTIX_CAPTURE_MODEL_CONFIG"] = original_capture

    captured = yaml.safe_load(capture_path.read_text())
    assert captured == {
        "provider": "google-genai",
        "model": "gemini-2.5-flash",
    }


def test_run_framework_agent_passes_primary_input_field_from_playbook(tmp_path: Path):
    project_root = tmp_path
    (project_root / ".super").write_text("project: demo\n")

    pipeline_dir = project_root / "demo" / "agents" / "demo_agent" / "pipelines"
    pipeline_dir.mkdir(parents=True)
    capture_path = project_root / "captured_primary_input.json"

    pipeline_file = pipeline_dir / "demo_agent_microsoft_pipeline.py"
    pipeline_file.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "",
                "class DemoAgentPipeline:",
                "    def __init__(self, model_config=None):",
                "        self.playbook = {",
                "            'spec': {",
                "                'input_fields': [{'name': 'knowledge_query'}],",
                "            }",
                "        }",
                "",
                "    async def run(self, query=None, knowledge_query=None, **inputs):",
                "        capture_path = os.environ['SUPEROPTIX_CAPTURE_PRIMARY_INPUT']",
                "        with open(capture_path, 'w', encoding='utf-8') as handle:",
                "            json.dump({",
                "                'query': query,",
                "                'knowledge_query': knowledge_query,",
                "                'inputs': inputs,",
                "            }, handle)",
                "        return {'retrieved_response': knowledge_query or query or ''}",
            ]
        )
    )

    args = SimpleNamespace(
        name="demo_agent",
        goal="What is NEON-FOX-742?",
        provider="google-genai",
        model="gemini-2.5-flash",
        local=False,
        gateway=False,
        direct=False,
        gateway_url=None,
        gateway_key_env=None,
    )

    original_cwd = os.getcwd()
    original_capture = os.environ.get("SUPEROPTIX_CAPTURE_PRIMARY_INPUT")
    os.chdir(project_root)
    os.environ["SUPEROPTIX_CAPTURE_PRIMARY_INPUT"] = str(capture_path)

    try:
        _run_framework_agent(args, "microsoft")
    finally:
        os.chdir(original_cwd)
        if original_capture is None:
            os.environ.pop("SUPEROPTIX_CAPTURE_PRIMARY_INPUT", None)
        else:
            os.environ["SUPEROPTIX_CAPTURE_PRIMARY_INPUT"] = original_capture

    captured = yaml.safe_load(capture_path.read_text())
    assert captured["query"] == "What is NEON-FOX-742?"
    assert captured["knowledge_query"] == "What is NEON-FOX-742?"


def test_run_framework_agent_falls_back_to_component_input_fields(tmp_path: Path):
    project_root = tmp_path
    (project_root / ".super").write_text("project: demo\n")

    pipeline_dir = project_root / "demo" / "agents" / "demo_agent" / "pipelines"
    pipeline_dir.mkdir(parents=True)
    capture_path = project_root / "captured_component_input.json"

    pipeline_file = pipeline_dir / "demo_agent_microsoft_pipeline.py"
    pipeline_file.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "from types import SimpleNamespace",
                "",
                "class DemoAgentPipeline:",
                "    def __init__(self, model_config=None):",
                "        self.playbook = {'spec': {}}",
                "        self.component = SimpleNamespace(input_fields=['knowledge_query'])",
                "",
                "    async def run(self, query=None, knowledge_query=None, **inputs):",
                "        capture_path = os.environ['SUPEROPTIX_CAPTURE_COMPONENT_INPUT']",
                "        with open(capture_path, 'w', encoding='utf-8') as handle:",
                "            json.dump({",
                "                'query': query,",
                "                'knowledge_query': knowledge_query,",
                "                'inputs': inputs,",
                "            }, handle)",
                "        return {'retrieved_response': knowledge_query or query or ''}",
            ]
        )
    )

    args = SimpleNamespace(
        name="demo_agent",
        goal="What is NEON-FOX-742?",
        provider="google-genai",
        model="gemini-2.5-flash",
        local=False,
        gateway=False,
        direct=False,
        gateway_url=None,
        gateway_key_env=None,
    )

    original_cwd = os.getcwd()
    original_capture = os.environ.get("SUPEROPTIX_CAPTURE_COMPONENT_INPUT")
    os.chdir(project_root)
    os.environ["SUPEROPTIX_CAPTURE_COMPONENT_INPUT"] = str(capture_path)

    try:
        _run_framework_agent(args, "microsoft")
    finally:
        os.chdir(original_cwd)
        if original_capture is None:
            os.environ.pop("SUPEROPTIX_CAPTURE_COMPONENT_INPUT", None)
        else:
            os.environ["SUPEROPTIX_CAPTURE_COMPONENT_INPUT"] = original_capture

    captured = yaml.safe_load(capture_path.read_text())
    assert captured["query"] == "What is NEON-FOX-742?"
    assert captured["knowledge_query"] == "What is NEON-FOX-742?"
