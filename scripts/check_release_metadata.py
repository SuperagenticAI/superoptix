#!/usr/bin/env python3
"""Validate version metadata, optionally against a release tag.

Run before building so a release fails on a stale file rather than on PyPI,
where a wrong version cannot be withdrawn and the number is spent.
"""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def release_metadata_errors(tag: str | None = None) -> list[str]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(pyproject["project"]["version"])
    errors: list[str] = []

    # The console script has to point at a callable that exists, or the wheel
    # installs and `super` does nothing.
    expected_entry = "superoptix.cli.main:main"
    scripts = pyproject.get("project", {}).get("scripts", {})
    if scripts.get("super") != expected_entry:
        errors.append(
            f"project script 'super' is {scripts.get('super')!r}, expected {expected_entry!r}"
        )

    # uv.lock carries the project's own version. A stale entry means the lock was
    # not regenerated after the bump, and `uv sync --frozen` in CI will disagree
    # with pyproject.toml.
    lock_path = ROOT / "uv.lock"
    if lock_path.exists():
        lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
        locked = [
            str(package.get("version") or "")
            for package in lock.get("package", [])
            if package.get("name") == "superoptix"
        ]
        if locked != [version]:
            errors.append(
                f"uv.lock has SuperOptiX versions {locked!r}, expected [{version!r}]. Run: uv lock"
            )

    # The release body is taken from this heading, so a missing section produces
    # a release with no notes.
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        errors.append(f"CHANGELOG.md has no release heading for {version}")

    # `__version__` is read from installed metadata rather than a literal, so it
    # cannot drift. The source-checkout fallback is checked instead: it should
    # never exceed the released version, which would mean an uninstalled
    # checkout reporting a version that was never published.
    init_text = (ROOT / "superoptix" / "__init__.py").read_text(encoding="utf-8")
    fallback = re.search(r'^\s*__version__ = "([^"]+)"', init_text, re.MULTILINE)
    if fallback and _as_tuple(fallback.group(1)) > _as_tuple(version):
        errors.append(
            f"superoptix/__init__.py fallback version {fallback.group(1)} is ahead of {version}"
        )

    if tag and tag != f"v{version}":
        errors.append(f"release tag is {tag!r}, expected 'v{version}'")
    return errors


def _as_tuple(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in version.split("."):
        digits = re.match(r"\d+", chunk)
        parts.append(int(digits.group()) if digits else 0)
    return tuple(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Tag name to compare with project.version")
    args = parser.parse_args()
    errors = release_metadata_errors(args.tag)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Release metadata is consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
