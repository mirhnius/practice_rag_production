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
        """Insert a paper, or update it in place if arxiv_id already exists.

        TODO:
        - existing = self.get_by_arxiv_id(paper.arxiv_id)
        - if existing: set its fields from paper.model_dump() and return it
        - else: construct Paper(**paper.model_dump()), self.session.add(it),
          self.session.flush(), return it
        """
        raise NotImplementedError

    def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        """TODO: self.session.query(Paper).filter_by(arxiv_id=arxiv_id).first()"""
        raise NotImplementedError

    def list_papers(self, limit: int = 20, offset: int = 0) -> list[Paper]:
        """TODO: paginate over all papers, most recently published first.

        self.session.query(Paper).order_by(Paper.published_date.desc())
            .offset(offset).limit(limit).all()
        """
        raise NotImplementedError
