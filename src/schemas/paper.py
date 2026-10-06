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

    arxiv_id:str
    title:str
    authors:list[str]
    abstract:str
    categories:list[str]
    published_date:datetime
    pdf_url:str


class PaperCreate(BaseModel):
    """Input to PaperRepository.upsert()."""

    arxiv_id:str
    title:str
    authors:list[str]
    abstract:str
    categories:list[str]
    published_date:datetime
    pdf_url:str
    raw_text: str | None = None


class PaperOut(BaseModel):
    """What GET /api/v1/papers and GET /api/v1/papers/{arxiv_id} return."""

    model_config = {"from_attributes": True}

    id:int
    arxiv_id:str
    title:str
    authors:list[str]
    abstract:str
    categories:list[str]
    published_date:datetime
    pdf_url:str