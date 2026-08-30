"""Public, vendor-neutral A2A skills served from the SuperOptiX agent card.

These skills are deliberately deterministic and dependency-light: they run no
model, touch no user code, and hold no credentials, so the public endpoint is
cheap to host and safe to expose. Mirrors the shape of SuperQode's
`harness-shortlist` skill.
"""

from superoptix.protocols.a2a.public.card import build_public_agent_card
from superoptix.protocols.a2a.public.runtime import PublicCatalogueRuntime
from superoptix.protocols.a2a.public.skills import (
    FRAMEWORK_A2A_STATUS,
    PUBLIC_SKILL_DEFINITIONS,
    agent_card_review,
    framework_a2a_readiness,
)

__all__ = [
    "FRAMEWORK_A2A_STATUS",
    "PublicCatalogueRuntime",
    "build_public_agent_card",
    "PUBLIC_SKILL_DEFINITIONS",
    "agent_card_review",
    "framework_a2a_readiness",
]
