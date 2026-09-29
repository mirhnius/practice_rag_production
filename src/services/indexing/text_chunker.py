"""
Week 4 — section-based chunking.

Splits a paper into overlapping ~600-word chunks instead of embedding the
whole paper as one vector (which would blur together unrelated parts of a
long document). Overlap keeps context from being lost right at a chunk
boundary.
"""

from dataclasses import dataclass

from src.services.pdf_parser.parser import ParsedSection


@dataclass
class Chunk:
    chunk_id: str
    section_name: str
    text: str


class TextChunker:
    def __init__(
        self,
        target_words: int = 600,
        overlap_words: int = 100,
        min_words: int = 100,
    ) -> None:
        self.target_words = target_words
        self.overlap_words = overlap_words
        self.min_words = min_words

    def chunk_paper(
        self,
        arxiv_id: str,
        raw_text: str,
        sections: list[ParsedSection] | None = None,
    ) -> list[Chunk]:
        """Turn a paper into overlapping chunks.

        TODO:
        - if `sections` is given (non-empty), chunk each section
          separately using `_chunk_text` below, tagging each Chunk with
          that section's title
        - otherwise (unstructured input), treat the whole `raw_text` as
          one section titled "Full Text" and chunk that
        - build a stable chunk_id per chunk, e.g.
          f"{arxiv_id}-{section_title}-{index}"
        """
        raise NotImplementedError

    def _chunk_text(self, text: str) -> list[str]:
        """Split `text` into overlapping windows of words.

        TODO:
        - words = text.split()
        - step = self.target_words - self.overlap_words
        - walk `words` in windows of `self.target_words`, advancing by
          `step` each time, joining each window back into a string
        - drop a trailing window shorter than `self.min_words` unless
          it's the only window produced
        """
        raise NotImplementedError
