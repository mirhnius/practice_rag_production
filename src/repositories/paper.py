"""
Week 2 — Paper repository.

The only place in the codebase that should write SQLAlchemy queries for
Paper rows. Routers and services call this, never the ORM model
directly — that's what keeps the persistence layer swappable and easy to
test with a fake/in-memory session later.
"""

from sqlalchemy.orm import Session

from src.models.paper import Paper
from src.schemas.paper import PaperCreate


class PaperRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, paper: PaperCreate) -> Paper:
        """Insert a paper, or update it in place if arxiv_id already exists."""
        existing = self.get_by_arxiv_id(paper.arxiv_id)
        if existing:
            for field, value in paper.model_dump().items():
                setattr(existing, field, value)
            self.session.flush()
            return existing
        
        new_paper = Paper(**paper.model_dump())
        self.session.add(new_paper)
        self.session.flush()
        return new_paper


    def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        """Return the Paper with the given arxiv_id, or None if not found."""
        return self.session.query(Paper).filter_by(arxiv_id=arxiv_id).first()

    def list_papers(self, limit: int = 20, offset: int = 0) -> list[Paper]:
        """Paginate over all papers, most recently published first."""
        return self.session.query(Paper).order_by(Paper.published_date.desc()).offset(offset).limit(limit).all()
