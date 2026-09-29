"""
Week 3 — OpenSearch keyword (BM25) search.

Read docs/week3.md first. This is the notebook replacement for
notebooks/week3/week3_opensearch.ipynb — a plain, top-to-bottom script,
already complete (nothing to implement here; it's your checking
harness).

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week3_test_search.py

Requires OpenSearch running (`docker compose up -d` in the course repo)
and at least one paper already stored in Postgres from Week 2.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402


def main() -> None:
    settings = get_settings()
    client = OpenSearchClient(settings.opensearch_host, settings.opensearch_index_name)

    print("=" * 60)
    print("STEP 1 — OpenSearch health check")
    print("=" * 60)
    healthy = client.health_check()
    print("OK" if healthy else "NOT healthy — is `docker compose up -d` running?")
    if not healthy:
        return

    print()
    print("=" * 60)
    print("STEP 2 — create the arxiv-papers index (no-op if it already exists)")
    print("=" * 60)
    created = client.create_index_if_missing()
    print("Created a new index." if created else "Index already existed.")

    print()
    print("=" * 60)
    print("STEP 3 — index every paper you stored in Postgres during Week 2")
    print("=" * 60)
    with get_session() as session:
        papers = PaperRepository(session).list_papers(limit=50)

    if not papers:
        print("No papers in Postgres yet — run scripts/week2_test_arxiv_pipeline.py first.")
        return

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
    print(f"Indexed {len(papers)} paper(s).")

    print()
    print("=" * 60)
    print("STEP 4 — search for 'learning'")
    print("=" * 60)
    results = client.search("learning", size=5)
    print(f"{results.get('total', 0)} total match(es)")
    for hit in results.get("hits", []):
        print(f"  - {hit.get('title', '')[:70]}  (score={hit.get('score')})")

    print()
    print("=" * 60)
    print("STEP 5 — search for 'neural', filtered to category cs.AI")
    print("=" * 60)
    filtered = client.search("neural", categories=["cs.AI"], size=5)
    print(f"{filtered.get('total', 0)} total match(es)")
    for hit in filtered.get("hits", []):
        print(f"  - {hit.get('title', '')[:70]}  (score={hit.get('score')})")

    print()
    print("=" * 60)
    print("BONUS — hit your own HTTP endpoint, if it's running")
    print("=" * 60)
    port = settings.app_port
    try:
        response = requests.get(
            f"http://localhost:{port}/api/v1/search", params={"q": "learning"}, timeout=5
        )
        print(f"GET /api/v1/search -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(
            f"Skipped — your app isn't running on port {port}. Start it with "
            f"`uv run uvicorn src.main:app --reload --port {port}` to try this step."
        )

    print("\nAll steps ran without errors — Week 3 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week3.md for the plan."
        )
