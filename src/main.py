"""
Week 1 — FastAPI application entrypoint.

Run it with:
    uv run uvicorn src.main:app --reload --port 8100

(Port 8100 by default, configurable via APP_PORT in .env, so it doesn't
collide with the course's own containerized API on port 8000 if you
happen to have both running at once.)
"""

from fastapi import FastAPI

from src.config import get_settings
from src.routers import health

settings = get_settings()

app = FastAPI(title="Practice RAG Production", debug=settings.debug)

app.include_router(health.router)

# TODO (Week 2): app.include_router(papers.router)
# TODO (Week 3): app.include_router(search.router)
# TODO (Week 4): app.include_router(hybrid_search.router)
# TODO (Week 5): app.include_router(ask.router)
# TODO (Week 7): app.include_router(agentic_ask.router)
