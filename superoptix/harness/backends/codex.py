"""Codex CLI backend for SuperOptiX harness sessions."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any

from superoptix.harness.sandbox import LocalSandbox
from superoptix.harness.types import HarnessRunResult


class CodexHarnessBackend:
    """Run harness turns through the local Codex CLI."""

    name = "codex"

    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        agent_name: str,
        cwd: Path | None = None,
        sandbox: LocalSandbox | None = None,
        model: str | None = None,
        model_config: dict[str, Any] | None = None,
        spec_data: dict[str, Any] | None = None,
        tools: list[Any] | None = None,
    ) -> HarnessRunResult:
        _ = agent_name, spec_data, tools
        workdir = Path(cwd or Path.cwd()).expanduser().resolve()
        resolved_model = model or _model_from_config(model_config)
        codex_bin = _codex_bin_from_config(model_config)
        sandbox_mode = _codex_sandbox_mode(sandbox)
        full_prompt = _with_system_prompt(prompt=prompt, system_prompt=system_prompt)

        with tempfile.TemporaryDirectory(prefix="superoptix-codex-") as temp_dir:
            last_message_path = Path(temp_dir) / "last-message.txt"
            args = [
                codex_bin,
                "exec",
                "--skip-git-repo-check",
                "--color",
                "never",
                "--sandbox",
                sandbox_mode,
                "--cd",
                str(workdir),
                "--output-last-message",
                str(last_message_path),
            ]
            if resolved_model:
                args.extend(["--model", resolved_model])
            args.append(full_prompt)

            env = os.environ.copy()
            env.setdefault("NO_COLOR", "1")
            proc = await asyncio.create_subprocess_exec(
                *args,
                cwd=str(workdir),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await proc.communicate()

            stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
            if proc.returncode != 0:
                detail = (
                    stderr or stdout or f"codex exited with status {proc.returncode}"
                )
                raise RuntimeError(detail)

            text = ""
            if last_message_path.exists():
                text = last_message_path.read_text(
                    encoding="utf-8", errors="replace"
                ).strip()
            if not text:
                text = stdout

        return HarnessRunResult(
            text=text,
            raw={"stdout": stdout, "stderr": stderr, "returncode": proc.returncode},
            metadata={
                "framework": self.name,
                "model": resolved_model,
                "sandbox": sandbox_mode,
                "cwd": str(workdir),
            },
        )


def _codex_sandbox_mode(sandbox: LocalSandbox | None) -> str:
    if sandbox is not None and sandbox.policy.allow_write:
        return "workspace-write"
    return "read-only"


def _model_from_config(model_config: dict[str, Any] | None) -> str | None:
    if not isinstance(model_config, dict):
        return None
    value = str(model_config.get("model") or "").strip()
    return value or None


def _codex_bin_from_config(model_config: dict[str, Any] | None) -> str:
    if isinstance(model_config, dict):
        value = str(model_config.get("codex_bin") or "").strip()
        if value:
            return value
    return os.getenv("SUPEROPTIX_CODEX_BIN", "codex")


def _with_system_prompt(*, prompt: str, system_prompt: str) -> str:
    system = str(system_prompt or "").strip()
    user = str(prompt or "").strip()
    if not system:
        return user
    return (
        "System instructions for this SuperOptiX harness run:\n"
        f"{system}\n\n"
        "User request:\n"
        f"{user}"
    ).strip()
