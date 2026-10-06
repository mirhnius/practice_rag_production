"""
Week 2 — PDF parsing with Docling.

Docling turns a scientific PDF into structured sections instead of one
undifferentiated blob of text — that structure is what Week 4's chunker
will lean on. Docs: https://docling-project.github.io/docling/

Expect some PDFs to fail to parse; that's normal (the course sees an
80-90% success rate on real arXiv PDFs) — handle it, don't let one bad
PDF crash a whole batch.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItemLabel

logger = logging.getLogger(__name__)

SKIP_LABELS = {DocItemLabel.PAGE_FOOTER, DocItemLabel.PAGE_HEADER}


@dataclass
class ParsedSection:
    title: str
    content: str


@dataclass
class ParsedPdf:
    raw_text: str
    sections: list[ParsedSection]


class PDFParserService:
    def __init__(self, max_pages: int = 30, max_file_size_mb: int = 20) -> None:
        self.max_pages = max_pages
        self.max_file_size_mb = max_file_size_mb

    def parse_pdf(self, pdf_path: Path) -> ParsedPdf | None:
        """Parse one PDF into raw text + structured sections.

        TODO:
        - return None early if pdf_path.stat().st_size exceeds
          self.max_file_size_mb (converted to bytes)
        - from docling.document_converter import DocumentConverter
        - converter = DocumentConverter(); result = converter.convert(str(pdf_path))
        - result.document.num_pages() (or similar) to enforce max_pages
        - pull the plain text via result.document.export_to_text() (or
          equivalent) for raw_text
        - walk the document's structure to build ParsedSection entries
          (heading + the text under it) — if Docling doesn't expose clean
          sections for a given PDF, falling back to one big
          ParsedSection("Full Text", raw_text) is a reasonable degrade
        - wrap all of this in try/except, logging and returning None on
          failure instead of raising, so a batch job can continue past a
          bad PDF
        """

        try:
          max_file_size_bytes = self.max_file_size_mb * 1024 * 1024
          if pdf_path.stat().st_size > max_file_size_bytes:
            logger.warning(
              "Skipping PDF %s: file size exceeds %d MB",
              pdf_path,
              self.max_file_size_mb,
            )
            return None

          converter = DocumentConverter()
          result = converter.convert(str(pdf_path))
          document = result.document

          if document.num_pages() > self.max_pages:
            logger.warning(
              "Skipping PDF %s: number of pages exceeds %d",
              pdf_path,
              self.max_pages,
            )
            return None

          raw_text = document.export_to_text()
          sections: list[ParsedSection] = []
          paragraphs: list[str] = []
          title = "Full Text"

          for item, _level in document.iterate_items():
            if item.label in SKIP_LABELS:
              continue

            text = getattr(item, "text", None)
            if not text:
              continue

            if item.label == DocItemLabel.SECTION_HEADER:
              if paragraphs:
                sections.append(
                  ParsedSection(
                    title=title,
                    content="\n".join(paragraphs),
                  )
                )
              title = text.strip()
              paragraphs = []
            else:
              paragraphs.append(text.strip())

          if paragraphs:
            sections.append(
              ParsedSection(
                title=title,
                content="\n".join(paragraphs),
              )
            )

          if not sections and raw_text.strip():
            sections = [
              ParsedSection(
                title="Full Text",
                content=raw_text.strip(),
              )
            ]

          return ParsedPdf(raw_text=raw_text, sections=sections)

        except Exception:
          logger.exception("Error parsing PDF %s", pdf_path)
          return None