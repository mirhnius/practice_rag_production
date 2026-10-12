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
    """Return a page of stored papers, `limit` at a time, skipping the first `offset`"""
    with get_session() as session:
        return PaperRepository(session).list_papers(limit, offset)


@router.get("/{arxiv_id}", response_model=PaperOut)
def get_paper(arxiv_id: str) -> PaperOut:
    """Return one paper by arXiv ID, or 404 if it isn't stored."""
    with get_session() as session:
        paper = PaperRepository(session).get_by_arxiv_id(arxiv_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
