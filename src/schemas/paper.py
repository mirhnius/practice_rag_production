"""
Week 2 — Pydantic schemas for papers.

Keep the layers separate:
- `ArxivPaperMetadata`: what the arXiv client returns after parsing the
  Atom feed (before anything touches the database).
- `PaperCreate`: what PaperRepository.upsert() needs.
- `PaperOut`: what the API returns to callers (src/routers/papers.py).

Splitting these means a change to the DB schema doesn't automatically
leak into the API response, and vice versa.
"""

from datetime import datetime

from pydantic import BaseModel


class ArxivPaperMetadata(BaseModel):
    """One entry parsed out of the arXiv Atom feed."""

    # TODO: arxiv_id: str
    # TODO: title: str
    # TODO: authors: list[str]
    # TODO: abstract: str
    # TODO: categories: list[str]
    # TODO: published_date: datetime
    # TODO: pdf_url: str


class PaperCreate(BaseModel):
    """Input to PaperRepository.upsert()."""

    # TODO: same fields as ArxivPaperMetadata, plus:
    # raw_text: str | None = None


class PaperOut(BaseModel):
    """What GET /api/v1/papers and GET /api/v1/papers/{arxiv_id} return."""

    model_config = {"from_attributes": True}

    # TODO: id: int
    # TODO: arxiv_id: str
    # TODO: title: str
    # TODO: authors: list[str]
    # TODO: abstract: str
    # TODO: categories: list[str]
    # TODO: published_date: datetime
    # TODO: pdf_url: str
