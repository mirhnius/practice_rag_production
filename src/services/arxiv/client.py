"""
Week 2 — arXiv API client.

Learning goals: polite polling of a public API (arXiv asks for a 3s
delay between requests), retry/backoff, and parsing the Atom XML feed
into `ArxivPaperMetadata` objects.

Reference: https://info.arxiv.org/help/api/user-manual.html

Query shape you'll build a URL for, e.g.:
    {base_url}?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=15
"""

import time
from pathlib import Path

import requests

from src.schemas.paper import ArxivPaperMetadata


class ArxivClient:
    def __init__(
        self,
        base_url: str,
        search_category: str,
        rate_limit_delay: float,
        pdf_cache_dir: str,
    ) -> None:
        self.base_url = base_url
        self.search_category = search_category
        self.rate_limit_delay = rate_limit_delay
        self.pdf_cache_dir = Path(pdf_cache_dir)
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
        self._last_request_at: float = 0.0

    def _respect_rate_limit(self) -> None:
        """Block until at least `self.rate_limit_delay` seconds have passed
        since the previous request.

        TODO:
        - elapsed = time.monotonic() - self._last_request_at
        - if elapsed < self.rate_limit_delay: time.sleep(the remainder)
        - self._last_request_at = time.monotonic()
        """
        raise NotImplementedError

    def fetch_papers(
        self,
        max_results: int = 15,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[ArxivPaperMetadata]:
        """Fetch recent papers for `self.search_category`.

        TODO:
        - self._respect_rate_limit()
        - build `search_query`: f"cat:{self.search_category}", AND'd with
          f"submittedDate:[{from_date}TO{to_date}]" if both dates given
          (arXiv expects YYYYMMDD strings)
        - requests.get(self.base_url, params={...sortBy, sortOrder,
          max_results...}, timeout=30) — wrap in a small retry loop
          (e.g. 3 attempts with exponential backoff) since arXiv
          occasionally returns 503s
        - parse the Atom XML response (xml.etree.ElementTree is enough —
          each <entry> has id, title, summary, author/name, category,
          published, and a link with title="pdf") into
          ArxivPaperMetadata objects
        """
        raise NotImplementedError

    def download_pdf(self, paper: ArxivPaperMetadata) -> Path:
        """Download and cache the PDF for one paper.

        TODO:
        - target = self.pdf_cache_dir / f"{paper.arxiv_id}.pdf"
        - if target.exists(): return target  (this is the "cache" part)
        - otherwise stream requests.get(paper.pdf_url) to that path and
          return it
        """
        raise NotImplementedError
