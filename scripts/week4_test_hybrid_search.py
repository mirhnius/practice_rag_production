"""
Week 4 — chunking, embeddings, and hybrid (BM25 + vector) search.

Notebook replacement for `notebooks/week4/week4_hybrid_search.ipynb`.
Complete harness — chunks a paper you already parsed in Week 2, embeds
and indexes those chunks, then runs BM25-only, vector-only, and hybrid
search over them.

    uv run python scripts/week4_test_hybrid_search.py

Needs OpenSearch running and a JINA_API_KEY in .env.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from scripts._util import run_step  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.db.session import get_session  # noqa: E402
from src.repositories.paper import PaperRepository  # noqa: E402
from src.services.embeddings.jina_client import JinaEmbeddingsClient  # noqa: E402
from src.services.indexing.hybrid_indexer import HybridIndexer  # noqa: E402
from src.services.indexing.text_chunker import TextChunker  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402


def main() -> None:
    print("=== Week 4: chunking + hybrid search ===")
    settings = get_settings()

    with get_session() as session:
        papers = [p for p in PaperRepository(session).list_papers(limit=50) if p.raw_text]

    if not papers:
        print(
            "No papers with parsed text yet. Re-run scripts/week2_test_arxiv_pipeline.py "
            "with process_pdfs=True on a paper that parses successfully, then come back."
        )
        return

    paper = papers[0]
    chunker = TextChunker()
    chunks = run_step(
        f"Chunk '{paper.title[:50]}'",
        "src/services/indexing/text_chunker.py (chunk_paper)",
        lambda: chunker.chunk_paper(paper.arxiv_id, paper.raw_text),
    )
    if chunks:
        print(f"    {len(chunks)} chunks, first one: {chunks[0].text[:100]!r}")

    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    vector = run_step(
        "Embed a test query with Jina",
        "src/services/embeddings/jina_client.py (embed_query)",
        lambda: embeddings_client.embed_query("machine learning"),
    )
    if vector:
        print(f"    got a {len(vector)}-dim vector")

    opensearch_client = OpenSearchClient(settings.opensearch_host)
    run_step(
        "Create the chunk index",
        "src/services/opensearch/client.py (create_chunk_index_if_missing)",
        opensearch_client.create_chunk_index_if_missing,
    )

    indexer = HybridIndexer(chunker, embeddings_client, opensearch_client)
    indexed = run_step(
        f"Chunk + embed + index '{paper.title[:50]}'",
        "src/services/indexing/hybrid_indexer.py (index_paper_chunks)",
        lambda: indexer.index_paper_chunks(paper.arxiv_id, paper.raw_text),
    )
    if indexed:
        print(f"    indexed {indexed} chunks")

    run_step(
        "BM25-only search over chunks",
        "src/services/opensearch/client.py (search)",
        lambda: opensearch_client.search("neural networks", size=3),
    )

    if vector:
        run_step(
            "Vector-only search over chunks",
            "src/services/opensearch/client.py (search_vector)",
            lambda: opensearch_client.search_vector(vector, size=3),
        )
        run_step(
            "Hybrid (RRF) search over chunks",
            "src/services/opensearch/client.py (search_hybrid)",
            lambda: opensearch_client.search_hybrid("neural networks", vector, size=3),
        )

    port = settings.app_port
    try:
        response = requests.post(
            f"http://localhost:{port}/api/v1/hybrid-search",
            json={"query": "neural networks", "use_hybrid": True, "size": 3},
            timeout=10,
        )
        print(f"\n[OK] POST /api/v1/hybrid-search on your own app -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"\n[SKIP] Your app isn't running on port {port}.")


if __name__ == "__main__":
    main()
