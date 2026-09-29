"""
Week 2 — arXiv ingestion pipeline.

The notebook replacement for `notebooks/week2/week2_arxiv_integration.ipynb`.
This script is complete — it's your checking harness. It exercises, in
order: the arXiv client, the PDF parser, the database, and the full
MetadataFetcher pipeline. Each step reports [OK] / [TODO] / [FAIL] so you
always know exactly what's next.

    uv run python scripts/week2_test_arxiv_pipeline.py

Requires the shared infra running (`docker compose up -d` in the course
repo) so Postgres is reachable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._util import run_step  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.services.arxiv.client import ArxivClient  # noqa: E402
from src.services.metadata_fetcher import MetadataFetcher  # noqa: E402
from src.services.pdf_parser.parser import PDFParserService  # noqa: E402


def main() -> None:
    print("=== Week 2: arXiv ingestion pipeline ===")
    settings = get_settings()

    arxiv_client = ArxivClient(
        base_url=settings.arxiv_base_url,
        search_category=settings.arxiv_search_category,
        rate_limit_delay=settings.arxiv_rate_limit_delay,
        pdf_cache_dir=settings.arxiv_pdf_cache_dir,
    )
    pdf_parser = PDFParserService()

    papers = run_step(
        "Fetch 2 recent papers from arXiv",
        "src/services/arxiv/client.py (fetch_papers)",
        lambda: arxiv_client.fetch_papers(max_results=2),
    )
    if not papers:
        print("\nStopping here — later steps need at least one paper.")
        return

    for paper in papers:
        print(f"    [{paper.arxiv_id}] {paper.title[:70]}")

    pdf_path = run_step(
        "Download the PDF for the first paper",
        "src/services/arxiv/client.py (download_pdf)",
        lambda: arxiv_client.download_pdf(papers[0]),
    )

    if pdf_path:
        parsed = run_step(
            "Parse that PDF with Docling",
            "src/services/pdf_parser/parser.py (parse_pdf)",
            lambda: pdf_parser.parse_pdf(pdf_path),
        )
        if parsed:
            print(f"    {len(parsed.sections)} sections, {len(parsed.raw_text)} chars")

    def _store_first_paper():
        with get_session() as session:
            repo = PaperRepository(session)
            from src.schemas.paper import PaperCreate

            return repo.upsert(PaperCreate(**papers[0].model_dump()))

    stored = run_step(
        "Store the first paper in Postgres (upsert)",
        "src/repositories/paper.py (upsert) and src/db/session.py (get_session)",
        _store_first_paper,
    )
    if stored:
        print(f"    stored with id={stored.id}")

    fetcher = MetadataFetcher(arxiv_client, pdf_parser)

    def _run_pipeline():
        with get_session() as session:
            return fetcher.fetch_and_process_papers(
                session, max_results=2, process_pdfs=False
            )

    results = run_step(
        "Run the full MetadataFetcher pipeline end to end",
        "src/services/metadata_fetcher.py (fetch_and_process_papers)",
        _run_pipeline,
    )
    if results:
        for key, value in results.items():
            print(f"    {key}: {value}")

    print("\nDone. Re-run this script after each TODO you fill in.")


if __name__ == "__main__":
    main()
