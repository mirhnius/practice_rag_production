"""
Week 1 — health check endpoint.

`scripts/week1_verify_infra.py` polls this to confirm your own FastAPI
app (not the course's) is up and importable.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Return a liveness payload.

    TODO:
    - Return at least `{"status": "ok"}`.
    - Once you build the DB/OpenSearch/Ollama clients in later weeks,
      extend this to ping each one and report per-service status —
      that's the pattern the course's own /api/v1/health endpoint uses.
    """
    raise NotImplementedError
