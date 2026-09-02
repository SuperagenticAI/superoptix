"""Build the public SuperOptiX Agent Card.

Deliberately mirrors the field shape SuperQode publishes at
super-agentic.ai/.well-known/agent-card.json, so the two products read as one
organisation's work while remaining independent implementations.
"""

from __future__ import annotations

from typing import Any, Dict

from superoptix.protocols.a2a.card_builder import build_a2a_agent_card_payload
from superoptix.protocols.a2a.public.skills import PUBLIC_SKILL_DEFINITIONS

# The address the card advertises. Keeping this on a domain you control
# means changing host later is a DNS change rather than a card change
# that every registry holding a copy has to re-fetch.
DEFAULT_SERVICE_URL = "https://a2a.superoptix.ai"
DOCUMENTATION_URL = "https://github.com/SuperagenticAI/superoptix"
ICON_URL = "https://superoptix.ai/uploads/logo.png"

def build_public_agent_card(
    *,
    service_url: str = DEFAULT_SERVICE_URL,
    rpc_url: str = "/a2a/jsonrpc",
) -> Dict[str, Any]:
    """Return the published SuperOptiX Agent Card payload.

    No ``securitySchemes``: the catalogue is anonymous and Cloud Run is
    unauthenticated. Declaring bearer without verifying it made 1.0 clients
    skip the agent.
    """
    return build_a2a_agent_card_payload(
        metadata={
            "name": "SuperOptiX",
            "description": (
                "The A2A interoperability layer for agent frameworks. Reports "
                "A2A readiness for DSPy, OpenAI Agents SDK, Claude Agent SDK, "
                "Pydantic AI, Google ADK, CrewAI, DeepAgents and Microsoft Agent "
                "Framework, and reviews Agent Cards for conformance and "
                "discoverability"
            ),
            "version": "1.0",
        },
        spec={},
        agent_url=service_url,
        rpc_url=rpc_url,
        protocol_version="1.0",
        legacy_protocol_version="0.3",
        skills_override=PUBLIC_SKILL_DEFINITIONS,
        icon_url=ICON_URL,
        documentation_url=DOCUMENTATION_URL,
        preferred_transport="JSONRPC",
    )
