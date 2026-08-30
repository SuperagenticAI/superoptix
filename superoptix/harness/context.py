"""Markdown context discovery for SuperOptiX harness sessions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from superoptix.harness.types import HarnessContext, Role, Skill


_FRONTMATTER_RE = re.compile(r"^---\s*\n(?P<meta>[\s\S]*?)\n---\s*\n(?P<body>[\s\S]*)$")


def parse_markdown_document(
    content: str,
    *,
    default_name: str,
) -> tuple[dict[str, Any], str, str]:
    """Parse YAML frontmatter from a Markdown document."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {"name": default_name}, content.strip(), default_name

    metadata = yaml.safe_load(match.group("meta")) or {}
    if not isinstance(metadata, dict):
        metadata = {}

    body = match.group("body").strip()
    name = str(metadata.get("name") or default_name).strip() or default_name
    metadata["name"] = name
    return metadata, body, name


def discover_context(cwd: str | Path) -> HarnessContext:
    """Discover AGENTS.md, skills, and roles from a working directory."""
    root = Path(cwd).expanduser().resolve()
    system_prompt = _read_system_prompt(root)
    skills = discover_skills(root)
    roles = discover_roles(root)
    return HarnessContext(
        cwd=root,
        system_prompt=compose_system_prompt(system_prompt, skills),
        skills=skills,
        roles=roles,
    )


def compose_system_prompt(
    base_prompt: str,
    skills: dict[str, Skill] | None = None,
) -> str:
    """Build the base harness system prompt."""
    parts: list[str] = []
    if base_prompt.strip():
        parts.append(base_prompt.strip())

    skill_items = list((skills or {}).values())
    if skill_items:
        skill_lines = ["Available skills:"]
        for skill in skill_items:
            suffix = f" - {skill.description}" if skill.description else ""
            skill_lines.append(f"- {skill.name}{suffix}")
        parts.append("\n".join(skill_lines))

    return "\n\n".join(parts).strip()


def discover_skills(cwd: str | Path) -> dict[str, Skill]:
    """Discover skills under `.agents/skills`."""
    root = Path(cwd).expanduser().resolve()
    skills_root = root / ".agents" / "skills"
    if not skills_root.exists():
        return {}

    skills: dict[str, Skill] = {}

    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        skill = _load_skill_file(skill_file, default_name=skill_file.parent.name)
        skills[skill.name] = skill

    for skill_file in sorted(skills_root.rglob("*.md")):
        if skill_file.name == "SKILL.md":
            continue
        rel = skill_file.relative_to(skills_root).as_posix()
        default_name = re.sub(r"\.(md|markdown)$", "", rel, flags=re.IGNORECASE)
        skill = _load_skill_file(skill_file, default_name=default_name)
        skills.setdefault(skill.name, skill)

    return skills


def discover_roles(cwd: str | Path) -> dict[str, Role]:
    """Discover role overlays under `roles` and `.agents/roles`."""
    root = Path(cwd).expanduser().resolve()
    roles: dict[str, Role] = {}

    for roles_root in [root / "roles", root / ".agents" / "roles"]:
        if not roles_root.exists():
            continue
        for role_file in sorted(roles_root.glob("*.md")):
            role = _load_role_file(
                role_file,
                default_name=re.sub(
                    r"\.(md|markdown)$", "", role_file.name, flags=re.IGNORECASE
                ),
            )
            roles[role.name] = role

    return roles


def _read_system_prompt(root: Path) -> str:
    parts: list[str] = []
    for filename in ["AGENTS.md", "CLAUDE.md"]:
        path = root / filename
        if path.exists() and path.is_file():
            parts.append(path.read_text(encoding="utf-8").strip())
    return "\n\n".join(part for part in parts if part)


def _load_skill_file(path: Path, *, default_name: str) -> Skill:
    metadata, body, name = parse_markdown_document(
        path.read_text(encoding="utf-8"),
        default_name=default_name,
    )
    return Skill(
        name=name,
        description=str(metadata.get("description") or "").strip(),
        instructions=body,
        path=path,
    )


def _load_role_file(path: Path, *, default_name: str) -> Role:
    metadata, body, name = parse_markdown_document(
        path.read_text(encoding="utf-8"),
        default_name=default_name,
    )
    return Role(
        name=name,
        description=str(metadata.get("description") or "").strip(),
        instructions=body,
        model=str(metadata.get("model") or "").strip() or None,
        path=path,
    )
