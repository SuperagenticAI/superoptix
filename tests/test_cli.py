"""Tests for SuperOptiX CLI."""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from superoptix.cli.commands.agent import _find_prebuilt_playbook, _run_framework_agent
from superoptix.cli.main import _requires_project_context
from superoptix.cli.utils import is_superoptix_project, validate_superoptix_project
from superoptix.runners.crewai_runtime_helpers import build_task_description


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
