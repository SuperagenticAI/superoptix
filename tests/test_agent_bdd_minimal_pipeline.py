from pathlib import Path
from types import SimpleNamespace

import yaml

from superoptix.cli.commands.agent import _MinimalDSPyBDDEvaluator


class _ProgramEcho:
    def __init__(self):
        self.loaded_path = None

    def __call__(self, **inputs):
        requirement = str(inputs.get("feature_requirement", "")).strip()
        return f"Implemented: {requirement}"

    def load(self, path: str):
        self.loaded_path = path


def test_minimal_dspy_bdd_evaluator_runs_scenarios(tmp_path: Path):
    playbook_path = tmp_path / "developer_playbook.yaml"
    playbook_path.write_text(
        yaml.safe_dump(
            {
                "spec": {
                    "feature_specifications": {
                        "scenarios": [
                            {
                                "name": "echo_requirement",
                                "description": "Returns implemented text",
                                "input": {
                                    "feature_requirement": "add retry support",
                                },
                                "expected_output": {
                                    "implementation": "Implemented: add retry support",
                                },
                            }
                        ]
                    }
                }
            }
        )
    )

    module = SimpleNamespace(build_program=lambda: _ProgramEcho())
    evaluator = _MinimalDSPyBDDEvaluator(module, playbook_path)

    results = evaluator.run_bdd_test_suite()

    assert results["success"] is True
    assert results["summary"]["total"] == 1
    assert results["summary"]["passed"] == 1
    assert results["summary"]["failed"] == 0


def test_minimal_dspy_bdd_evaluator_loads_optimized_weights(tmp_path: Path):
    playbook_path = tmp_path / "developer_playbook.yaml"
    playbook_path.write_text(
        yaml.safe_dump({"spec": {"feature_specifications": {"scenarios": []}}})
    )

    program = _ProgramEcho()
    module = SimpleNamespace(build_program=lambda: program)
    evaluator = _MinimalDSPyBDDEvaluator(module, playbook_path)

    evaluator.load_optimized(str(tmp_path / "developer_optimized.json"))

    assert program.loaded_path is not None
