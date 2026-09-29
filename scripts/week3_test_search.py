"""
Week 3 — OpenSearch keyword (BM25) search.

Notebook replacement for `notebooks/week3/week3_opensearch.ipynb`.
Complete harness — indexes whatever papers you already stored in Week 2,
then runs BM25 searches against them.

    uv run python scripts/week3_test_search.py

Requires OpenSearch running (`docker compose up -d` in the course repo)
and at least one paper already stored in Postgres from Week 2.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from scripts._util import run_step  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402


def main() -> None:
    print("=== Week 3: OpenSearch keyword search ===")
    settings = get_settings()
    client = OpenSearchClient(settings.opensearch_host, settings.opensearch_index_name)

    healthy = run_step(
        "OpenSearch health check",
        "src/services/opensearch/client.py (health_check)",
        client.health_check,
    )
    if not healthy:
        print("\nStopping here — start OpenSearch before continuing.")
        return

    run_step(
        "Create the arxiv-papers index",
        "src/services/opensearch/client.py (create_index_if_missing)",
        client.create_index_if_missing,
    )

    with get_session() as session:
        papers = PaperRepository(session).list_papers(limit=50)

    if not papers:
        print("\nNo papers in Postgres yet — run scripts/week2_test_arxiv_pipeline.py first.")
        return

    def _index_all():
        for paper in papers:
            client.index_paper(
                {
                    "arxiv_id": paper.arxiv_id,
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "authors": paper.authors,
                    "categories": paper.categories,
                    "published_date": paper.published_date.isoformat(),
                    "pdf_url": paper.pdf_url,
                }
            )
        return len(papers)

    indexed = run_step(
        f"Index {len(papers)} paper(s) from Postgres into OpenSearch",
        "src/services/opensearch/client.py (index_paper)",
        _index_all,
    )
    if not indexed:
        return

    results = run_step(
        "Search for 'learning'",
        "src/services/opensearch/query_builder.py + client.py (search)",
        lambda: client.search("learning", size=5),
    )
    if results:
        print(f"    {results.get('total', 0)} total matches")
        for hit in results.get("hits", []):
            print(f"    - {hit.get('title', '')[:70]} (score={hit.get('score')})")

    run_step(
        "Search with a category filter (cs.AI)",
        "src/services/opensearch/query_builder.py (build_filtered_query)",
        lambda: client.search("neural", categories=["cs.AI"], size=5),
    )

    # Best-effort: also hit your own API if it happens to be running.
    port = settings.app_port
    try:
        response = requests.get(
            f"http://localhost:{port}/api/v1/search", params={"q": "learning"}, timeout=5
        )
        print(f"\n[OK] GET /api/v1/search on your own app -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(
            f"\n[SKIP] Your app isn't running on port {port}. Start it with "
            f"`uv run uvicorn src.main:app --reload --port {port}` to test the HTTP endpoint too."
        )


if __name__ == "__main__":
    main()
