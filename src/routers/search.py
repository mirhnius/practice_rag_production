"""
Week 3 — search API.

Remember to add `app.include_router(search.router)` in src/main.py once
this works.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
def search(q: str, category: str | None = None, size: int = 10) -> dict:
    """TODO:
    from src.config import get_settings
    from src.services.opensearch.client import OpenSearchClient

    settings = get_settings()
    client = OpenSearchClient(settings.opensearch_host, settings.opensearch_index_name)
    return client.search(q, categories=[category] if category else None, size=size)

    (Constructing the client per-request is fine for now; a nice later
    upgrade is building it once at startup and sharing it via FastAPI's
    dependency injection instead.)
    """
    raise NotImplementedError
