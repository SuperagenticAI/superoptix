"""Score how well a catalogue of agents can be routed to.

Three numbers, because "discoverable" and "unambiguous" fail differently:

- **discovery** — the skill was surfaced at all (top-3). A skill that never
  appears cannot be called, whatever else is true of it.
- **invocation** — the skill was the top choice. This is the number that
  corresponds to a caller getting the right agent.
- **disambiguation** — of the cases a skill lost, how often it lost to a
  *sibling* rather than being simply invisible. High confusion means two
  descriptions do not distinguish themselves from each other.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from superoptix.protocols.a2a.routing.queries import RoutingCase
from superoptix.protocols.a2a.routing.router import Router, SkillRef


@dataclass
class RoutingReport:
    """Scored result for one catalogue under one router."""

    router: str
    cases: int
    discovery_rate: float
    invocation_rate: float
    confusion_rate: float
    per_skill: Dict[str, Dict[str, float]] = field(default_factory=dict)
    misroutes: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "router": self.router,
            "cases": self.cases,
            "discoveryRate": round(self.discovery_rate, 4),
            "invocationRate": round(self.invocation_rate, 4),
            "confusionRate": round(self.confusion_rate, 4),
            "perSkill": self.per_skill,
            "misroutes": self.misroutes[:20],
        }

    def summary(self) -> str:
        return (
            f"{self.router}: invocation {self.invocation_rate:.1%} | "
            f"discovery {self.discovery_rate:.1%} | "
            f"confusion {self.confusion_rate:.1%} ({self.cases} cases)"
        )


def score_routing(
    router: Router,
    skills: Sequence[SkillRef],
    cases: Sequence[RoutingCase],
    *,
    discovery_k: int = 3,
    keep_misroutes: int = 20,
) -> RoutingReport:
    """Run every case through the router and score the catalogue."""
    if not cases:
        return RoutingReport(
            router=router.name,
            cases=0,
            discovery_rate=0.0,
            invocation_rate=0.0,
            confusion_rate=0.0,
        )

    hits = 0
    discovered = 0
    confused = 0
    misses = 0
    per_skill_total: Dict[str, int] = defaultdict(int)
    per_skill_hits: Dict[str, int] = defaultdict(int)
    misroutes: List[Dict[str, str]] = []

    known = {s.key for s in skills}

    for case in cases:
        choice = router.route(case.query, skills)
        chosen = choice.skill.key if choice.skill else None
        per_skill_total[case.expected] += 1

        top_k = [key for key, _ in choice.ranked[:discovery_k]]
        if case.expected in top_k:
            discovered += 1

        if chosen == case.expected:
            hits += 1
            per_skill_hits[case.expected] += 1
        else:
            misses += 1
            # Losing to a sibling is a different failure from not being seen.
            if chosen in known:
                confused += 1
            if len(misroutes) < keep_misroutes:
                misroutes.append(
                    {
                        "query": case.query,
                        "expected": case.expected,
                        "got": chosen or "-",
                    }
                )

    per_skill = {
        key: {
            "cases": per_skill_total[key],
            "invocationRate": round(per_skill_hits[key] / per_skill_total[key], 4),
        }
        for key in sorted(per_skill_total)
    }

    return RoutingReport(
        router=router.name,
        cases=len(cases),
        discovery_rate=discovered / len(cases),
        invocation_rate=hits / len(cases),
        confusion_rate=(confused / misses) if misses else 0.0,
        per_skill=per_skill,
        misroutes=misroutes,
    )
