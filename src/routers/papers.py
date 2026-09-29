"""
Week 2 — papers API.

Read-only endpoints over whatever MetadataFetcher has stored so far.
Remember to add `app.include_router(papers.router)` in src/main.py once
this works.
"""

from fastapi import APIRouter, HTTPException

from src.db.session import get_session
from src.repositories.paper import PaperRepository
from src.schemas.paper import PaperOut

router = APIRouter(prefix="/api/v1/papers", tags=["papers"])


@router.get("", response_model=list[PaperOut])
def list_papers(limit: int = 20, offset: int = 0) -> list[PaperOut]:
    """TODO:
    with get_session() as session:
        return PaperRepository(session).list_papers(limit, offset)
    """
    raise NotImplementedError


@router.get("/{arxiv_id}", response_model=PaperOut)
def get_paper(arxiv_id: str) -> PaperOut:
    """TODO: look up by arxiv_id via the repository; if it's None, raise
    HTTPException(status_code=404, detail="Paper not found").
    """
    raise NotImplementedError
