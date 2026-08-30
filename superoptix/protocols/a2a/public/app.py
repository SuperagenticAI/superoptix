"""ASGI entrypoint for the published SuperOptiX A2A endpoint.

Deployed as a small web service (Render, Fly, Cloud Run, anything that runs an
ASGI app). It serves the public Agent Card and the deterministic catalogue
skills — no model calls, no user code, no credentials.

    uvicorn superoptix.protocols.a2a.public.app:app

Configuration comes from the environment so the card always advertises the URL
the service is actually reachable at:

    SUPEROPTIX_A2A_PUBLIC_URL   public base URL (default: the Render service)
"""

from __future__ import annotations

import os
from typing import Any

from superoptix.protocols.a2a.public.card import (
    DEFAULT_SERVICE_URL,
    build_public_agent_card,
)
from superoptix.protocols.a2a.public.runtime import PublicCatalogueRuntime  # noqa: F401
from superoptix.protocols.a2a.server import create_a2a_fastapi_app

RPC_URL = "/a2a/jsonrpc"


def public_service_url() -> str:
    """Base URL this service is reachable at, as advertised in the card."""
    return (
        os.environ.get("SUPEROPTIX_A2A_PUBLIC_URL", "").strip().rstrip("/")
        or DEFAULT_SERVICE_URL
    )


def create_public_app(service_url: str | None = None) -> Any:
    """Build the ASGI app that serves the public SuperOptiX agent."""
    url = (service_url or public_service_url()).rstrip("/")
    return create_a2a_fastapi_app(
        pipeline=None,
        agent_url=url,
        rpc_url=RPC_URL,
        runtime_adapter="superoptix_public",
        agent_card=build_public_agent_card(service_url=url, rpc_url=RPC_URL),
    )


app = create_public_app()
