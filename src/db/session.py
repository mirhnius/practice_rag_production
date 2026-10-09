"""
Week 2 — SQLAlchemy engine + session.

Everything in src/repositories/ and src/models/ depends on this. Keep it
boring: one engine, one sessionmaker, one declarative Base, one
context-managed helper to get a session.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().postgres_database_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session, committing on success, rolling back on error."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create any missing tables (safe to call repeatedly; never alters existing ones)."""
    # Imported here, not at the top: models/paper.py imports Base from this
    # file, so a top-level import would be circular. The import itself is what
    # registers Paper on Base — without it, create_all() silently creates nothing.
    from src.models import paper  # noqa: F401

    Base.metadata.create_all(bind=engine)