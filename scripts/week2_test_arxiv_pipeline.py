"""
Week 2 — arXiv ingestion pipeline.

Read docs/week2.md first. This is the notebook replacement for
notebooks/week2/week2_arxiv_integration.ipynb — a plain, top-to-bottom
script, already complete (nothing to implement here; it's your checking
harness). It calls straight into your src/ code, in the same order the
original notebook's cells did.

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week2_test_arxiv_pipeline.py

Requires the shared infra running (`docker compose up -d` in the course
repo) so Postgres is reachable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.schemas.paper import PaperCreate  # noqa: E402
from src.services.arxiv.client import ArxivClient  # noqa: E402
from src.services.metadata_fetcher import MetadataFetcher  # noqa: E402
from src.services.pdf_parser.parser import PDFParserService  # noqa: E402


def main() -> None:
    settings = get_settings()

    arxiv_client = ArxivClient(
        base_url=settings.arxiv_base_url,
        search_category=settings.arxiv_search_category,
        rate_limit_delay=settings.arxiv_rate_limit_delay,
        pdf_cache_dir=settings.arxiv_pdf_cache_dir,
    )
    pdf_parser = PDFParserService()

    print("=" * 60)
    print("STEP 1 — fetch 2 recent papers from arXiv")
    print("=" * 60)
    papers = arxiv_client.fetch_papers(max_results=2)
    print(f"Fetched {len(papers)} paper(s):")
    for paper in papers:
        print(f"  [{paper.arxiv_id}] {paper.title[:70]}")

    print()
    print("=" * 60)
    print("STEP 2 — download the PDF for the first paper")
    print("=" * 60)
    pdf_path = arxiv_client.download_pdf(papers[0])
    print(f"Downloaded to {pdf_path}")

    print()
    print("=" * 60)
    print("STEP 3 — parse that PDF with Docling")
    print("=" * 60)
    parsed = pdf_parser.parse_pdf(pdf_path)
    if parsed is None:
        print("Parsing failed (this can happen on real PDFs — see docs/week2.md).")
    else:
        print(f"{len(parsed.sections)} section(s), {len(parsed.raw_text)} characters of text")

    print()
    print("=" * 60)
    print("STEP 4 — store the first paper in Postgres (upsert)")
    print("=" * 60)
    raw_text = parsed.raw_text if parsed else None
    with get_session() as session:
        repo = PaperRepository(session)
        stored = repo.upsert(PaperCreate(**papers[0].model_dump(), raw_text=raw_text))
        print(f"Stored with id={stored.id}")

        print("\nReading it back with get_by_arxiv_id() to confirm the round trip:")
        fetched = repo.get_by_arxiv_id(papers[0].arxiv_id)
        print(f"  {fetched.arxiv_id} -> {fetched.title[:70]}")

    print()
    print("=" * 60)
    print("STEP 5 — run the full MetadataFetcher pipeline end to end")
    print("=" * 60)
    print("(2 fresh papers, PDF processing on — this is the real thing)")
    fetcher = MetadataFetcher(arxiv_client, pdf_parser)
    with get_session() as session:
        results = fetcher.fetch_and_process_papers(session, max_results=2, process_pdfs=True)
    for key, value in results.items():
        print(f"  {key}: {value}")

    print("\nAll steps ran without errors — Week 2 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week2.md for the plan."
        )
