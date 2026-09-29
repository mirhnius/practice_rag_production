"""
Week 4 — chunking, embeddings, and hybrid (BM25 + vector) search.

Read docs/week4.md first. This is the notebook replacement for
notebooks/week4/week4_hybrid_search.ipynb — a plain, top-to-bottom
script, already complete (nothing to implement here; it's your checking
harness).

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week4_test_hybrid_search.py

Needs OpenSearch running and a JINA_API_KEY set in .env.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.services.embeddings.jina_client import JinaEmbeddingsClient  # noqa: E402
from src.services.indexing.hybrid_indexer import HybridIndexer  # noqa: E402
from src.services.indexing.text_chunker import TextChunker  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402


def main() -> None:
    settings = get_settings()

    print("=" * 60)
    print("STEP 1 — grab a paper from Postgres that has parsed text")
    print("=" * 60)
    with get_session() as session:
        papers = [p for p in PaperRepository(session).list_papers(limit=50) if p.raw_text]
    if not papers:
        print(
            "No papers with parsed text yet. Re-run scripts/week2_test_arxiv_pipeline.py "
            "with a PDF that parses successfully, then come back."
        )
        return
    paper = papers[0]
    print(f"Using: [{paper.arxiv_id}] {paper.title[:70]}")

    print()
    print("=" * 60)
    print("STEP 2 — chunk it")
    print("=" * 60)
    chunker = TextChunker()
    chunks = chunker.chunk_paper(paper.arxiv_id, paper.raw_text)
    print(f"{len(chunks)} chunk(s). First one starts: {chunks[0].text[:100]!r}")

    print()
    print("=" * 60)
    print("STEP 3 — embed a test query with Jina")
    print("=" * 60)
    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    query_vector = embeddings_client.embed_query("machine learning")
    print(f"Got a {len(query_vector)}-dim vector.")

    print()
    print("=" * 60)
    print("STEP 4 — create the chunk index")
    print("=" * 60)
    opensearch_client = OpenSearchClient(settings.opensearch_host)
    created = opensearch_client.create_chunk_index_if_missing()
    print("Created a new chunk index." if created else "Chunk index already existed.")

    print()
    print("=" * 60)
    print("STEP 5 — chunk + embed + index that paper")
    print("=" * 60)
    indexer = HybridIndexer(chunker, embeddings_client, opensearch_client)
    indexed_count = indexer.index_paper_chunks(paper.arxiv_id, paper.raw_text)
    print(f"Indexed {indexed_count} chunk(s).")

    query = "neural networks"

    print()
    print("=" * 60)
    print(f"STEP 6a — BM25-only search for {query!r}")
    print("=" * 60)
    bm25_results = opensearch_client.search("neural networks", size=3)
    for hit in bm25_results.get("hits", []):
        print(f"  - {hit.get('chunk_text', hit.get('title', ''))[:80]!r} (score={hit.get('score')})")

    print()
    print("=" * 60)
    print(f"STEP 6b — vector-only search for {query!r}")
    print("=" * 60)
    query_vector = embeddings_client.embed_query(query)
    vector_results = opensearch_client.search_vector(query_vector, size=3)
    for hit in vector_results.get("hits", []):
        print(f"  - {hit.get('chunk_text', '')[:80]!r} (score={hit.get('score')})")

    print()
    print("=" * 60)
    print(f"STEP 6c — hybrid (RRF) search for {query!r}")
    print("=" * 60)
    hybrid_results = opensearch_client.search_hybrid(query, query_vector, size=3)
    for hit in hybrid_results.get("hits", []):
        print(f"  - {hit.get('chunk_text', '')[:80]!r} (score={hit.get('score')})")

    print()
    print("=" * 60)
    print("BONUS — hit your own HTTP endpoint, if it's running")
    print("=" * 60)
    port = settings.app_port
    try:
        response = requests.post(
            f"http://localhost:{port}/api/v1/hybrid-search",
            json={"query": query, "use_hybrid": True, "size": 3},
            timeout=10,
        )
        print(f"POST /api/v1/hybrid-search -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"Skipped — your app isn't running on port {port}.")

    print("\nAll steps ran without errors — Week 4 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week4.md for the plan."
        )
