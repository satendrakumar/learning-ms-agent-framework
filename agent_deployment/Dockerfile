# Production image for the hosted agent (agent_deployment/foundry_server.py).
# Same image runs locally, on any container platform, or as a
# Microsoft Foundry Hosted Agent.

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Dependency layer first so code changes don't bust the cache.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY production/ production/

# The host binds 0.0.0.0:$PORT (default 8088) and serves:
#   POST /responses    — OpenAI Responses API
#   GET  /readiness    — health probe for the orchestrator
ENV PORT=8088
EXPOSE 8088

# Model credentials come in as env vars at run time, never baked in:
#   OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
CMD ["/app/.venv/bin/python", "production/server.py"]
