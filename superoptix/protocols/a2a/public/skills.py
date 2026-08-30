"""Deterministic public skills exposed on the SuperOptiX agent card.

Both skills answer from local data or from the submitted payload. Nothing here
calls a model, reads the filesystem, or needs a credential, which is what makes
the public endpoint safe to serve and cheap to run.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Skill 1: framework A2A readiness
# ---------------------------------------------------------------------------
# Verified on 2026-08-30 by reading each package's published PyPI metadata.
# `dependency` is the A2A requirement the package itself declares, if any.
FRAMEWORK_A2A_STATUS: Dict[str, Dict[str, Any]] = {
    "crewai": {
        "display": "CrewAI",
        "state": "partial",
        "dependency": "a2a-sdk~=0.3.10 (extra: a2a)",
        "spec_line": "0.3",
        "note": "Ships A2A behind an optional extra, pinned to the pre-1.0 line. "
        "Reaches 1.0 orchestrators only after a spec upgrade.",
    },
    "google-adk": {
        "display": "Google ADK",
        "state": "partial",
        "dependency": "a2a-sdk[http-server]>=0.3.4,<2 (extras: a2a, all)",
        "spec_line": "0.3",
        "note": "Auto-generates Agent Cards but floors on the 0.3 line. Cards "
        "default to protocol version 0.3 unless set explicitly.",
    },
    "pydantic-ai": {
        "display": "Pydantic AI",
        "state": "partial",
        "dependency": "ships its own A2A package rather than declaring a2a-sdk",
        "spec_line": "0.3",
        "note": "A2A support exists but is not wired to the official SDK line.",
    },
    "dspy": {
        "display": "DSPy",
        "state": "none",
        "dependency": None,
        "spec_line": None,
        "note": "No A2A dependency declared. Needs an adapter to be reachable "
        "by any A2A client.",
    },
    "openai-agents": {
        "display": "OpenAI Agents SDK",
        "state": "none",
        "dependency": None,
        "spec_line": None,
        "note": "No A2A dependency declared.",
    },
    "claude-agent-sdk": {
        "display": "Claude Agent SDK",
        "state": "none",
        "dependency": None,
        "spec_line": None,
        "note": "No A2A dependency declared.",
    },
    "deepagents": {
        "display": "DeepAgents",
        "state": "none",
        "dependency": None,
        "spec_line": None,
        "note": "No A2A dependency declared.",
    },
    "agent-framework": {
        "display": "Microsoft Agent Framework",
        "state": "none",
        "dependency": None,
        "spec_line": None,
        "note": "No A2A dependency declared.",
    },
}

_ALIASES = {
    "crew": "crewai",
    "crew-ai": "crewai",
    "adk": "google-adk",
    "google": "google-adk",
    "googleadk": "google-adk",
    "pydantic": "pydantic-ai",
    "pydanticai": "pydantic-ai",
    "openai": "openai-agents",
    "openai-agents-sdk": "openai-agents",
    "claude": "claude-agent-sdk",
    "claude-sdk": "claude-agent-sdk",
    "anthropic": "claude-agent-sdk",
    "microsoft": "agent-framework",
    "msaf": "agent-framework",
    "semantic-kernel": "agent-framework",
    "autogen": "agent-framework",
    "deep-agents": "deepagents",
    "langchain": "deepagents",
}


def _match_frameworks(query: str) -> List[str]:
    """Return framework keys named in the query, or all of them."""
    text = re.sub(r"[^a-z0-9\-\s]", " ", (query or "").lower())
    tokens = {t for t in re.split(r"\s+", text) if t}
    joined = " ".join(sorted(tokens))

    hits: List[str] = []
    for key in FRAMEWORK_A2A_STATUS:
        if (
            key in joined.replace(" ", "-")
            or key in text
            or key.replace("-", "") in tokens
        ):
            hits.append(key)
    for alias, key in _ALIASES.items():
        if (alias in tokens or alias in text) and key not in hits:
            hits.append(key)
    return hits or list(FRAMEWORK_A2A_STATUS)


def framework_a2a_readiness(query: str) -> Dict[str, Any]:
    """Report A2A support for the agent frameworks named in the query."""
    keys = _match_frameworks(query)
    rows = []
    for key in keys:
        info = FRAMEWORK_A2A_STATUS[key]
        rows.append(
            {
                "framework": key,
                "name": info["display"],
                "a2a_support": info["state"],
                "declares": info["dependency"],
                "spec_line": info["spec_line"],
                "note": info["note"],
            }
        )

    none_count = sum(1 for r in rows if r["a2a_support"] == "none")
    lines = [
        f"A2A readiness for {len(rows)} framework(s) "
        f"({none_count} with no A2A support):",
        "",
    ]
    for row in rows:
        label = (
            "no A2A support"
            if row["a2a_support"] == "none"
            else (f"A2A {row['spec_line']} (pre-1.0)")
        )
        lines.append(f"- {row['name']}: {label}")
        if row["declares"]:
            lines.append(f"    declares: {row['declares']}")
        lines.append(f"    {row['note']}")
    lines.append("")
    lines.append(
        "None of these frameworks reach A2A 1.0 on their own. SuperOptiX "
        "generates a 1.0-conformant card and server for any of them without "
        "changing the agent."
    )

    return {
        "response": "\n".join(lines),
        "data": {"frameworks": rows, "checked": "2026-08-30"},
    }


# ---------------------------------------------------------------------------
# Skill 2: agent card review
# ---------------------------------------------------------------------------
_VAGUE = {
    "agent",
    "assistant",
    "helper",
    "tool",
    "does things",
    "general",
    "ai agent",
    "task",
    "handles requests",
    "misc",
    "utility",
}


def _extract_card(query: str) -> Dict[str, Any] | None:
    """Pull a JSON object out of the submitted text, if there is one."""
    text = (query or "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except (ValueError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _review_skill(skill: Dict[str, Any], index: int) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    label = str(skill.get("id") or skill.get("name") or f"skill[{index}]")
    description = str(skill.get("description") or "").strip()

    if not description:
        findings.append(
            {
                "severity": "high",
                "field": f"skills.{label}.description",
                "issue": "No description. Calling agents have nothing to route on.",
            }
        )
    elif len(description) < 40:
        findings.append(
            {
                "severity": "high",
                "field": f"skills.{label}.description",
                "issue": f"Description is {len(description)} characters. Too short to "
                "distinguish this skill from a similar one in another card.",
            }
        )
    elif description.lower().strip(" .") in _VAGUE:
        findings.append(
            {
                "severity": "high",
                "field": f"skills.{label}.description",
                "issue": "Description is generic. It will not separate this agent "
                "from any other in a directory.",
            }
        )

    if not skill.get("examples"):
        findings.append(
            {
                "severity": "medium",
                "field": f"skills.{label}.examples",
                "issue": "No examples. Examples are the strongest signal a caller "
                "has for how to phrase an invocation.",
            }
        )
    if not skill.get("tags"):
        findings.append(
            {
                "severity": "low",
                "field": f"skills.{label}.tags",
                "issue": "No tags, which reduces discoverability in directories.",
            }
        )
    return findings


def agent_card_review(query: str) -> Dict[str, Any]:
    """Score an A2A Agent Card for conformance and discoverability."""
    card = _extract_card(query)
    if card is None:
        return {
            "response": (
                "Send an A2A Agent Card as JSON and this skill returns a "
                "discoverability and conformance review: how a calling agent "
                "would read your skills, and which A2A 1.0 fields are missing.\n\n"
                "Example: paste the contents of your "
                "/.well-known/agent-card.json."
            ),
            "data": {"reviewed": False},
        }

    findings: List[Dict[str, str]] = []

    protocol_version = str(card.get("protocolVersion") or "").strip()
    if not protocol_version:
        findings.append(
            {
                "severity": "high",
                "field": "protocolVersion",
                "issue": "Absent. A 1.0 orchestrator cannot tell which spec you "
                "speak and may skip the agent.",
            }
        )
    elif protocol_version.startswith("0."):
        findings.append(
            {
                "severity": "high",
                "field": "protocolVersion",
                "issue": f"Declares {protocol_version}. Agents advertising only the "
                "pre-1.0 line are invisible to 1.0-only clients.",
            }
        )

    if not card.get("signature") and not card.get("signatures"):
        findings.append(
            {
                "severity": "high",
                "field": "signature",
                "issue": "Card is unsigned. Signed cards are the A2A 1.0 mechanism "
                "for proving the card came from the domain owner.",
            }
        )
    if not card.get("securitySchemes"):
        findings.append(
            {
                "severity": "medium",
                "field": "securitySchemes",
                "issue": "No security schemes declared, so callers cannot tell how "
                "to authenticate.",
            }
        )

    interfaces = card.get("supportedInterfaces") or card.get("interfaces") or []
    if not interfaces:
        findings.append(
            {
                "severity": "high",
                "field": "supportedInterfaces",
                "issue": "No interfaces advertised. Nothing can call this agent.",
            }
        )
    else:
        bindings = {
            str(i.get("protocolBinding") or i.get("protocol") or "")
            for i in interfaces
            if isinstance(i, dict)
        }
        versions = {
            str(i.get("protocolVersion") or "")
            for i in interfaces
            if isinstance(i, dict)
        }
        if "1.0" not in versions:
            findings.append(
                {
                    "severity": "high",
                    "field": "supportedInterfaces[].protocolVersion",
                    "issue": "No interface advertises A2A 1.0.",
                }
            )
        if len(bindings) < 2:
            findings.append(
                {
                    "severity": "low",
                    "field": "supportedInterfaces[].protocolBinding",
                    "issue": f"Only {', '.join(sorted(b for b in bindings if b)) or 'one'} "
                    "binding offered. Advertising both JSONRPC and HTTP+JSON widens "
                    "the set of clients that can reach you.",
                }
            )

    skills = card.get("skills") or []
    if not skills:
        findings.append(
            {
                "severity": "high",
                "field": "skills",
                "issue": "No skills declared. Callers have no basis to route to "
                "this agent at all.",
            }
        )
    for index, skill in enumerate(skills):
        if isinstance(skill, dict):
            findings.extend(_review_skill(skill, index))

    for field, severity in (
        ("description", "medium"),
        ("provider", "low"),
        ("documentationUrl", "low"),
        ("preferredTransport", "low"),
    ):
        if not card.get(field):
            findings.append(
                {
                    "severity": severity,
                    "field": field,
                    "issue": f"'{field}' is absent.",
                }
            )

    weights = {"high": 12, "medium": 5, "low": 2}
    score = max(0, 100 - sum(weights[f["severity"]] for f in findings))
    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: order[f["severity"]])

    name = str(card.get("name") or "unnamed agent")
    lines = [
        f"Agent Card review — {name}",
        f"Discoverability and conformance score: {score}/100",
        f"{len(findings)} finding(s).",
        "",
    ]
    for finding in findings:
        lines.append(
            f"[{finding['severity'].upper():6}] {finding['field']}: {finding['issue']}"
        )
    if not findings:
        lines.append("No issues found against the A2A 1.0 card checks.")

    return {
        "response": "\n".join(lines),
        "data": {"reviewed": True, "score": score, "findings": findings},
    }


# ---------------------------------------------------------------------------
# Card skill declarations
# ---------------------------------------------------------------------------
PUBLIC_SKILL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": "framework-a2a-readiness",
        "name": "Framework A2A Readiness",
        "description": (
            "Report whether a named agent framework supports the A2A protocol, "
            "which spec line it targets, and what is missing for A2A 1.0 "
            "interoperability. Covers DSPy, OpenAI Agents SDK, Claude Agent SDK, "
            "Pydantic AI, Google ADK, CrewAI, DeepAgents and Microsoft Agent "
            "Framework. Answers from published package metadata, not opinion"
        ),
        "tags": ["a2a", "interoperability", "frameworks", "discovery", "compatibility"],
        "examples": [
            "Does CrewAI support A2A?",
            "Which agent frameworks have no A2A support at all?",
            "What spec version does Google ADK target?",
            "Is DSPy reachable over A2A?",
        ],
        "inputModes": ["text/plain"],
        "outputModes": ["text/plain", "application/json"],
    },
    {
        "id": "agent-card-review",
        "name": "Agent Card Review",
        "description": (
            "Review an A2A Agent Card for conformance and discoverability. "
            "Returns a scored list of findings covering protocol version, card "
            "signing, security schemes, interface bindings and the quality of "
            "each skill description as a calling agent would read it. Submit the "
            "card as JSON"
        ),
        "tags": ["a2a", "agent-card", "conformance", "discoverability", "review"],
        "examples": [
            'Review this agent card: {"name": "my-agent", "skills": []}',
            "Why are other agents not discovering my agent?",
            "Is my agent card A2A 1.0 conformant?",
        ],
        "inputModes": ["text/plain", "application/json"],
        "outputModes": ["text/plain", "application/json"],
    },
]
