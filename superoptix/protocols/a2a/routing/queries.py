"""Build a routing eval set from published Agent Cards.

Hand-authoring queries does not scale past a demo, so the eval set is generated
from the agents themselves — the same shape as GEPA's `gskill`, which mines
tasks from a repository rather than asking anyone to write them.

One rule keeps this honest: **queries are never generated from the skill
description.** The description is what gets optimised, so deriving the test from
it would be circular. Queries come from the skill's name, tags and examples —
the parts that state what the agent *is* — and the description then has to earn
the routing by covering that space.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

from superoptix.protocols.a2a.routing.router import SkillRef, tokenize

_TEMPLATES = (
    "{phrase}",
    "I need help with {phrase}",
    "can you handle {phrase}",
    "who can do {phrase}",
)


@dataclass(frozen=True)
class RoutingCase:
    """One query and the skill that should win it."""

    query: str
    expected: str
    source: str


def _phrases(skill: SkillRef, *, hard: bool = True) -> List[str]:
    """Salient phrases describing the skill, excluding its description.

    In hard mode the skill's own name is withheld. A caller asks in their own
    words ("my card was charged twice"), they do not recite the skill's title,
    so a query that echoes the name lets a useless description win on the name
    alone. Hard mode is what makes the score mean something.
    """
    out: List[str] = []
    name = str(skill.name or "").strip()
    if name and not hard:
        out.append(name.lower())

    for example in skill.examples:
        text = re.sub(r"^\w+:\s*", "", str(example)).strip()
        if len(tokenize(text)) >= 2:
            out.append(text.lower())

    informative = [
        t
        for t in skill.tags
        if t
        and t.lower() not in {"crewai", "dspy", "task", "agent", "signature", "tools"}
    ]
    if informative:
        out.append(" ".join(informative).replace("-", " ").lower())

    seen, unique = set(), []
    for phrase in out:
        flat = re.sub(r"\s+", " ", phrase).strip()
        if flat and flat not in seen and len(tokenize(flat)) >= 1:
            seen.add(flat)
            unique.append(flat)
    return unique


def generate_cases(
    skills: Sequence[SkillRef], *, per_skill: int = 4, hard: bool = True
) -> List[RoutingCase]:
    """Generate labelled routing cases across a catalogue of skills.

    Args:
        hard: withhold each skill's own name from its queries, so a description
            has to carry the routing rather than the title doing it. Skills with
            no examples or distinguishing tags yield no cases in hard mode —
            which is itself the finding: nothing about them is routable.
    """
    cases: List[RoutingCase] = []
    for skill in skills:
        phrases = _phrases(skill, hard=hard)
        if not phrases:
            continue
        made = 0
        for phrase in phrases:
            for template in _TEMPLATES:
                if made >= per_skill:
                    break
                cases.append(
                    RoutingCase(
                        query=template.format(phrase=phrase),
                        expected=skill.key,
                        source=phrase,
                    )
                )
                made += 1
            if made >= per_skill:
                break
    return cases


def catalogue_from_cards(cards: Iterable[Dict[str, Any]]) -> List[SkillRef]:
    """Flatten several cards into one routable catalogue."""
    from superoptix.protocols.a2a.routing.router import skills_from_card

    skills: List[SkillRef] = []
    for card in cards:
        skills.extend(skills_from_card(card))
    return skills
