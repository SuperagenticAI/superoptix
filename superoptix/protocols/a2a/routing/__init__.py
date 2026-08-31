"""Measure and improve how well other agents can route to yours."""

from superoptix.protocols.a2a.routing.metrics import RoutingReport, score_routing
from superoptix.protocols.a2a.routing.queries import (
    RoutingCase,
    catalogue_from_cards,
    generate_cases,
)
from superoptix.protocols.a2a.routing.router import (
    LexicalRouter,
    LLMRouter,
    Router,
    RoutingChoice,
    SkillRef,
    skills_from_card,
)

__all__ = [
    "LLMRouter",
    "LexicalRouter",
    "Router",
    "RoutingCase",
    "RoutingChoice",
    "RoutingReport",
    "SkillRef",
    "catalogue_from_cards",
    "generate_cases",
    "score_routing",
    "skills_from_card",
]
