"""Sandbox adapters used by the SuperOptiX harness runtime."""

from __future__ import annotations

import fnmatch
import glob as globlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SandboxPolicy:
    """Capability policy for model-callable harness tools."""

    allow_read: bool = True
    allow_write: bool = False
    allow_shell: bool = False
    max_read_bytes: int = 50 * 1024
    max_read_lines: int = 2000
    max_grep_matches: int = 100
    max_grep_line_length: int = 500
    command_timeout: int = 30


class LocalSandbox:
    """Restricted local workspace sandbox."""

    def __init__(
        self,
        root: str | Path,
        *,
        policy: SandboxPolicy | None = None,
    ):
        self.root = Path(root).expanduser().resolve()
        self.policy = policy or SandboxPolicy()

    def read(
        self,
        path: str,
        *,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        """Read a file or list a directory inside the sandbox root."""
        self._require_read()
        target = self.resolve(path)
        if target.is_dir():
            return "\n".join(sorted(item.name for item in target.iterdir())) or "(empty)"
        if not target.exists():
            raise FileNotFoundError(path)

        content = target.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        start = max(0, int(offset or 1) - 1)
        selected = lines[start : start + limit] if limit else lines[start:]
        truncated = "\n".join(selected)
        return self._truncate_text(truncated, total_lines=len(lines), start=start)

    def write(self, path: str, content: str) -> str:
        """Write a file inside the sandbox root."""
        self._require_write()
        target = self.resolve(path, must_exist=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
        return f"Wrote {len(str(content))} bytes to {self.relative(target)}"

    def edit(
        self,
        path: str,
        old_text: str,
        new_text: str,
        *,
        replace_all: bool = False,
    ) -> str:
        """Replace exact text in a file inside the sandbox root."""
        self._require_write()
        target = self.resolve(path)
        content = target.read_text(encoding="utf-8", errors="replace")
        count = content.count(old_text)
        if count == 0:
            raise ValueError(f"Could not find requested text in {path}")
        if count > 1 and not replace_all:
            raise ValueError(
                f"Found {count} occurrences in {path}; set replace_all=true "
                "or provide a more specific old_text."
            )
        updated = content.replace(old_text, new_text) if replace_all else content.replace(old_text, new_text, 1)
        target.write_text(updated, encoding="utf-8")
        replaced = count if replace_all else 1
        return f"Replaced {replaced} occurrence(s) in {self.relative(target)}"

    def grep(
        self,
        pattern: str,
        *,
        path: str = ".",
        include: str | None = None,
    ) -> str:
        """Search files for a literal or regex pattern."""
        self._require_read()
        import re

        root = self.resolve(path)
        regex = re.compile(pattern)
        matches: list[str] = []
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for file_path in files:
            rel = self.relative(file_path)
            if include and not fnmatch.fnmatch(rel, include):
                continue
            try:
                lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if regex.search(line):
                    shown = line
                    if len(shown) > self.policy.max_grep_line_length:
                        shown = shown[: self.policy.max_grep_line_length] + "..."
                    matches.append(f"{rel}:{line_no}:{shown}")
                    if len(matches) >= self.policy.max_grep_matches:
                        matches.append("[truncated: too many matches]")
                        return "\n".join(matches)
        return "\n".join(matches) if matches else "(no matches)"

    def glob(self, pattern: str) -> str:
        """Glob files relative to the sandbox root."""
        self._require_read()
        raw_matches = globlib.glob(str(self.root / pattern), recursive=True)
        matches = []
        for raw in raw_matches:
            path = Path(raw).resolve()
            try:
                matches.append(self.relative(path))
            except ValueError:
                continue
        return "\n".join(sorted(matches)) if matches else "(no matches)"

    def bash(self, command: str, *, timeout: int | None = None) -> dict[str, Any]:
        """Execute a shell command inside the sandbox root."""
        self._require_shell()
        effective_timeout = timeout or self.policy.command_timeout
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                check=False,
            )
            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "exit_code": completed.returncode,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": exc.stdout or "",
                "stderr": (exc.stderr or "")
                + f"\nCommand timed out after {effective_timeout} seconds.",
                "exit_code": -1,
            }

    def resolve(self, path: str, *, must_exist: bool = True) -> Path:
        """Resolve a user path inside the sandbox root."""
        raw = Path(path).expanduser()
        candidate = raw if raw.is_absolute() else self.root / raw
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Path escapes sandbox root: {path}") from exc
        if must_exist and not resolved.exists():
            raise FileNotFoundError(path)
        return resolved

    def relative(self, path: str | Path) -> str:
        """Return a sandbox-relative path."""
        resolved = Path(path).resolve(strict=False)
        return resolved.relative_to(self.root).as_posix()

    def _truncate_text(self, text: str, *, total_lines: int, start: int) -> str:
        lines = text.splitlines()
        if len(lines) > self.policy.max_read_lines:
            lines = lines[: self.policy.max_read_lines]
            text = "\n".join(lines)
            text += (
                f"\n\n[Showing lines {start + 1}-{start + len(lines)} "
                f"of {total_lines}. Use offset to continue.]"
            )
        encoded = text.encode("utf-8", errors="replace")
        if len(encoded) > self.policy.max_read_bytes:
            truncated = encoded[: self.policy.max_read_bytes].decode(
                "utf-8",
                errors="replace",
            )
            return truncated + "\n\n[truncated: max_read_bytes exceeded]"
        return text

    def _require_read(self) -> None:
        if not self.policy.allow_read:
            raise PermissionError("Sandbox read access is disabled.")

    def _require_write(self) -> None:
        if not self.policy.allow_write:
            raise PermissionError("Sandbox write access is disabled.")

    def _require_shell(self) -> None:
        if not self.policy.allow_shell:
            raise PermissionError("Sandbox shell access is disabled.")

