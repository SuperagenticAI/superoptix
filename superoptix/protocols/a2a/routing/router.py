"""Choose which agent skill a query should be routed to.

In A2A the *caller* decides. To score how well an agent describes itself we have
to stand in for that caller, so a router here takes the published Agent Cards
and a query and returns a skill.

Two implementations ship. The lexical router is deterministic and needs no
provider, which makes baselines reproducible and lets this run in CI; the LLM
router reads the cards the way a real calling agent would. Keeping the contract
pluggable matters for a specific reason: optimising descriptions against the
same router that scores them is circular, so a credible result optimises with
one and validates with another.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Sequence

_TOKEN = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "which",
    "who",
    "why",
    "will",
    "with",
    "you",
    "your",
    "can",
    "i",
    "my",
    "me",
    "do",
    "does",
    "into",
    "over",
    "using",
    "use",
    "returns",
    "given",
}


def tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(str(text or "").lower()) if t not in _STOPWORDS]


@dataclass(frozen=True)
class SkillRef:
    """One routable skill, flattened out of a card."""

    agent: str
    skill_id: str
    name: str
    description: str
    tags: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        return f"{self.agent}:{self.skill_id}"

    def routing_text(self) -> str:
        """Everything a caller reads when deciding. This is the surface GEPA optimises."""
        return " ".join(
            [self.name, self.description, " ".join(self.tags), " ".join(self.examples)]
        )


def skills_from_card(card: Dict[str, Any]) -> List[SkillRef]:
    agent = str(card.get("name") or "agent")
    refs: List[SkillRef] = []
    for skill in card.get("skills") or []:
        if not isinstance(skill, dict):
            continue
        refs.append(
            SkillRef(
                agent=agent,
                skill_id=str(skill.get("id") or skill.get("name") or "skill"),
                name=str(skill.get("name") or ""),
                description=str(skill.get("description") or ""),
                tags=tuple(str(t) for t in (skill.get("tags") or [])),
                examples=tuple(str(e) for e in (skill.get("examples") or [])),
            )
        )
    return refs


@dataclass
class RoutingChoice:
    """What the router picked, and how confidently."""

    skill: SkillRef | None
    score: float
    ranked: List[tuple[str, float]]


class Router(Protocol):
    name: str

    def route(self, query: str, skills: Sequence[SkillRef]) -> RoutingChoice:
        """Pick the skill this query should go to."""


class LexicalRouter:
    """TF-IDF cosine over each skill's routing text.

    Deterministic and provider-free, so a baseline is reproducible anywhere. It
    measures something real: whether a description carries terms that
    distinguish this skill from its neighbours.
    """

    name = "lexical"

    def _idf(self, skills: Sequence[SkillRef]) -> Dict[str, float]:
        n = len(skills) or 1
        seen: Counter[str] = Counter()
        for skill in skills:
            seen.update(set(tokenize(skill.routing_text())))
        return {
            term: math.log((n + 1) / (count + 1)) + 1.0 for term, count in seen.items()
        }

    def route(self, query: str, skills: Sequence[SkillRef]) -> RoutingChoice:
        if not skills:
            return RoutingChoice(skill=None, score=0.0, ranked=[])
        idf = self._idf(skills)
        q_terms = Counter(tokenize(query))
        if not q_terms:
            return RoutingChoice(skill=None, score=0.0, ranked=[])

        scored: List[tuple[SkillRef, float]] = []
        for skill in skills:
            terms = Counter(tokenize(skill.routing_text()))
            if not terms:
                scored.append((skill, 0.0))
                continue
            num = sum(
                q_terms[t] * terms.get(t, 0) * (idf.get(t, 1.0) ** 2) for t in q_terms
            )
            q_norm = math.sqrt(
                sum((c * idf.get(t, 1.0)) ** 2 for t, c in q_terms.items())
            )
            s_norm = math.sqrt(
                sum((c * idf.get(t, 1.0)) ** 2 for t, c in terms.items())
            )
            scored.append(
                (skill, num / (q_norm * s_norm) if q_norm and s_norm else 0.0)
            )

        scored.sort(key=lambda pair: (-pair[1], pair[0].key))
        best, best_score = scored[0]
        return RoutingChoice(
            skill=best if best_score > 0 else None,
            score=best_score,
            ranked=[(s.key, round(v, 4)) for s, v in scored],
        )


class LLMRouter:
    """Ask a model to choose, the way a real calling agent would.

    Used as the held-out validator: a gain that only shows up under the router
    it was optimised against is a gain in that router, not in interoperability.
    """

    name = "llm"

    def __init__(self, lm: Any):
        self._lm = lm

    def route(self, query: str, skills: Sequence[SkillRef]) -> RoutingChoice:
        if not skills:
            return RoutingChoice(skill=None, score=0.0, ranked=[])
        catalogue = "\n".join(
            f"{i + 1}. [{s.key}] {s.name}: {s.description}"
            for i, s in enumerate(skills)
        )
        prompt = (
            "You are an agent deciding which skill to call. Choose exactly one.\n\n"
            f"Available skills:\n{catalogue}\n\n"
            f"Request: {query}\n\n"
            "Answer with the bracketed identifier only."
        )
        reply = str(self._lm(prompt))
        for skill in skills:
            if skill.key in reply:
                return RoutingChoice(skill=skill, score=1.0, ranked=[(skill.key, 1.0)])
        return RoutingChoice(skill=None, score=0.0, ranked=[])
