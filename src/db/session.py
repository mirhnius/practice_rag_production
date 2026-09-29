"""
Week 2 — SQLAlchemy engine + session.

Everything in src/repositories/ and src/models/ depends on this. Keep it
boring: one engine, one sessionmaker, one declarative Base, one
context-managed helper to get a session.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    pass


# TODO: engine = create_engine(get_settings().postgres_database_url)
engine = None  # TODO

# TODO: SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
SessionLocal = None  # TODO


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a SQLAlchemy session, committing on success, rolling back on error.

    TODO:
    - session = SessionLocal()
    - try: yield session; session.commit()
    - except Exception: session.rollback(); raise
    - finally: session.close()
    """
    raise NotImplementedError
