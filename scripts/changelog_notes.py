#!/usr/bin/env python3
"""Print the CHANGELOG section for a version or git tag.

The release workflow pipes this into the GitHub release body, so the notes
published alongside a tag are the same notes committed to the repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def changelog_notes(version: str, text: str) -> str:
    """Return the body under `## [version]`, up to the next release heading.

    A missing section falls back to a bare title. Publishing a release with thin
    notes is preferable to failing a workflow that has already built and tested
    the package.
    """
    heading = f"## [{version}]"
    start = text.find(heading)
    if start == -1:
        return f"SuperOptiX {version}"
    start = text.find("\n", start) + 1
    nxt = text.find("\n## [", start)
    body = text[start : nxt if nxt != -1 else None].strip()
    return body or f"SuperOptiX {version}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag", help="Tag or version, for example v0.3.7")
    args = parser.parse_args()
    version = str(args.tag).removeprefix("v")
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    print(changelog_notes(version, text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
