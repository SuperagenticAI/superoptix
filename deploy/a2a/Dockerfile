# Container image for the public SuperOptiX A2A endpoint.
#
# Built for Cloud Run, which sets PORT at runtime and requires the process to
# bind 0.0.0.0. The image installs only the a2a extra, so it carries neither the
# framework integrations nor the ML stack.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SUPEROPTIX_TELEMETRY=false

WORKDIR /app

# uv resolves and installs considerably faster than pip, which matters because
# Cloud Run rebuilds the image on every source deploy.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml README.md LICENCE ./
COPY superoptix ./superoptix

RUN uv pip install --system --no-cache ".[a2a]"

# Cloud Run injects PORT. The default keeps `docker run` working locally.
ENV PORT=8080
EXPOSE 8080

CMD exec uvicorn superoptix.protocols.a2a.public.app:app \
    --host 0.0.0.0 --port ${PORT} --workers 1
