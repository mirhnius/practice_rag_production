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
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests

from src.schemas.paper import ArxivPaperMetadata

MAX_RETRIES = 3
ATOM = "http://www.w3.org/2005/Atom"

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
        since the previous request."""

        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_at = time.monotonic()

    def fetch_papers(
        self,
        max_results: int = 15,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[ArxivPaperMetadata]:
        """Fetch recent papers for `self.search_category`."""
        search_query = f"cat:{self.search_category}"

        if from_date and to_date:
            search_query += f" AND submittedDate:[{from_date}TO{to_date}]"

        params = {
            "search_query": search_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
        for attempt in range(MAX_RETRIES):
            self._respect_rate_limit()
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
            except requests.RequestException:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(2**attempt)
                continue

            if response.status_code == 503:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                time.sleep(2**attempt)
                continue

            response.raise_for_status()
            break

        root = ET.fromstring(response.content)
        papers: list[ArxivPaperMetadata] = []
        for entry in root.findall(f"{{{ATOM}}}entry"):
            arxiv_url = entry.findtext(f"{{{ATOM}}}id", default="")
            arxiv_id = arxiv_url.rsplit("/abs/", 1)[-1]
            title = entry.findtext(f"{{{ATOM}}}title", default="").strip()
            abstract = entry.findtext(f"{{{ATOM}}}summary", default="").strip()
            authors = [
                author.findtext(f"{{{ATOM}}}name", default="").strip()
                for author in entry.findall(f"{{{ATOM}}}author")
            ]
            categories = [
                category.get("term", "")
                for category in entry.findall(f"{{{ATOM}}}category")
            ]
            published_text = entry.findtext(f"{{{ATOM}}}published", default="")
            published_date = datetime.fromisoformat(
                published_text.replace("Z", "+00:00")
            )
            pdf_url = next(
                (
                    link.get("href")
                    for link in entry.findall(f"{{{ATOM}}}link")
                    if link.get("title") == "pdf"
                ),
                f"https://arxiv.org/pdf/{arxiv_id}",
            )
            papers.append(
                ArxivPaperMetadata(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    categories=categories,
                    published_date=published_date,
                    pdf_url=pdf_url,
                )
            )

        return papers


    def download_pdf(self, paper: ArxivPaperMetadata) -> Path:
        """Download and cache the PDF for one paper."""

        target = self.pdf_cache_dir / f"{paper.arxiv_id}.pdf"
        if target.exists():
            return target

        self._respect_rate_limit()
        response = requests.get(paper.pdf_url, stream=True, timeout=60)
        response.raise_for_status()

        with open(target, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return target
