"""Shared helpers for A2A demo servers."""

from __future__ import annotations

from typing import Any


def serve_pipeline(
    *,
    pipeline: Any,
    agent_url: str,
    host: str,
    port: int,
) -> None:
    """Serve a pipeline as an A2A app using the SuperOptiX bridge."""
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError(
            "uvicorn is required to run the A2A demo servers. Install superoptix[a2a]."
        ) from exc

    from superoptix.protocols.a2a import create_a2a_fastapi_app

    app = create_a2a_fastapi_app(pipeline=pipeline, agent_url=agent_url)
    uvicorn.run(app, host=host, port=port, log_level="info")
