"""
Week 2 — Paper ORM model.

Mirrors what the course stores per arXiv paper: enough metadata to
display and search it, plus the raw text pulled out by the PDF parser.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    arxiv_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    authors: Mapped[list[str]] = mapped_column(JSON)
    abstract: Mapped[str] = mapped_column(Text)
    categories: Mapped[list[str]] = mapped_column(JSON)
    published_date: Mapped[datetime] = mapped_column(DateTime)
    pdf_url: Mapped[str] = mapped_column(String)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
