from pathlib import Path

from superoptix.runners.dspy_runner import DSPyRunner


def test_find_pipeline_file_detects_claude_sdk_variant(tmp_path: Path):
    pipelines_dir = tmp_path / "pipelines"
    pipelines_dir.mkdir()
    claude_pipeline = pipelines_dir / "developer_claude_sdk_pipeline.py"
    claude_pipeline.write_text("# test")

    runner = DSPyRunner.__new__(DSPyRunner)
    runner.agent_name = "developer"

    result = runner._find_pipeline_file(pipelines_dir)

    assert result == claude_pipeline
