"""Lean SurrealDB reliability harness for SuperOptiX.

Runs a focused set of SurrealDB-oriented test suites, reports timing/pass-fail,
and writes a machine-readable JSON summary under `.benchmarks/`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_PATH = REPO_ROOT / ".benchmarks" / "surrealdb_lean_harness_latest.json"


@dataclass
class SuiteResult:
    name: str
    command: List[str]
    return_code: int
    duration_s: float
    passed: bool
    summary_line: str


SUITES: list[tuple[str, list[str]]] = [
    ("framework_grounding", ["tests/adapters/test_surrealdb_rag_framework_grounding.py"]),
    ("framework_matrix", ["tests/adapters/test_surrealdb_lean_matrix.py"]),
    ("retrieval_modes", ["tests/test_surrealdb_rag_mixin.py"]),
    ("memory_temporal_mcp", ["tests/test_memory_system.py", "-k", "TemporalSurrealDBBackend or SurrealDBMCPTool"]),
    ("seed_setup", ["tests/test_surrealdb_seed_setup.py"]),
]


def _extract_summary_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not lines:
        return ""
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "skipped" in line:
            return line
    return lines[-1]


def _run_suite(name: str, test_args: list[str], *, dry_run: bool) -> SuiteResult:
    cmd = [sys.executable, "-m", "pytest", "-q", *test_args]
    if dry_run:
        return SuiteResult(
            name=name,
            command=cmd,
            return_code=0,
            duration_s=0.0,
            passed=True,
            summary_line="dry-run",
        )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)

    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    duration_s = time.perf_counter() - started
    summary = _extract_summary_line(proc.stdout or "")

    return SuiteResult(
        name=name,
        command=cmd,
        return_code=proc.returncode,
        duration_s=duration_s,
        passed=(proc.returncode == 0),
        summary_line=summary,
    )


def _print_table(results: list[SuiteResult]) -> None:
    print("\nSurrealDB Lean Harness")
    print("| Suite | Status | Duration (s) | Summary |")
    print("|---|---:|---:|---|")
    for result in results:
        status = "PASS" if result.passed else f"FAIL({result.return_code})"
        print(
            f"| {result.name} | {status} | {result.duration_s:.2f} | {result.summary_line} |"
        )


def _write_report(path: Path, results: list[SuiteResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_epoch_s": time.time(),
        "repo_root": str(REPO_ROOT),
        "results": [asdict(r) for r in results],
        "passed": all(r.passed for r in results),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lean SurrealDB reliability harness.")
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Output JSON report path (default: {DEFAULT_REPORT_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned suites without executing pytest.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = args.report.expanduser().resolve()

    results: list[SuiteResult] = []
    for name, test_args in SUITES:
        result = _run_suite(name, test_args, dry_run=bool(args.dry_run))
        results.append(result)

    _print_table(results)
    _write_report(report_path, results)
    print(f"\nReport written to: {report_path}")

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
