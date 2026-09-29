"""
Week 5 — complete RAG pipeline (retrieval + local LLM).

Read docs/week5.md first. This is the notebook replacement for
notebooks/week5/week5_complete_rag_system.ipynb — a plain, top-to-bottom
script, already complete (nothing to implement here; it's your checking
harness).

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week5_test_rag.py

Needs OpenSearch (with chunks indexed from Week 4) and Ollama running,
with a model pulled, e.g.:
    docker exec rag-ollama ollama pull llama3.2:1b
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.services.embeddings.jina_client import JinaEmbeddingsClient  # noqa: E402
from src.services.ollama.client import OllamaClient  # noqa: E402
from src.services.ollama.prompts import build_rag_prompt  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402

QUERY = "What are transformers in machine learning?"


def main() -> None:
    settings = get_settings()

    opensearch_client = OpenSearchClient(settings.opensearch_host)
    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    ollama_client = OllamaClient(settings.ollama_host, settings.ollama_model)

    print("=" * 60)
    print(f"STEP 1 — embed the query: {QUERY!r}")
    print("=" * 60)
    query_vector = embeddings_client.embed_query(QUERY)
    print(f"Got a {len(query_vector)}-dim vector.")

    print()
    print("=" * 60)
    print("STEP 2 — hybrid search for relevant chunks")
    print("=" * 60)
    results = opensearch_client.search_hybrid(QUERY, query_vector, size=3)
    chunks = results.get("hits", [])
    if not chunks:
        print(
            "No chunks retrieved — run scripts/week4_test_hybrid_search.py first "
            "so there's something to search over."
        )
        return
    for hit in chunks:
        print(f"  - {hit.get('chunk_text', '')[:80]!r}")

    print()
    print("=" * 60)
    print("STEP 3 — build the RAG prompt")
    print("=" * 60)
    prompt = build_rag_prompt(QUERY, chunks)
    print(f"Prompt is {len(prompt)} characters.")

    print()
    print("=" * 60)
    print(f"STEP 4 — generate a full answer with {settings.ollama_model}")
    print("=" * 60)
    answer = ollama_client.generate(prompt)
    print(f"Answer: {answer[:500]}")

    print()
    print("=" * 60)
    print("STEP 5 — generate the same answer via streaming")
    print("=" * 60)
    streamed = "".join(ollama_client.generate_stream(prompt))
    print(f"Streamed answer: {streamed[:500]}")

    print()
    print("=" * 60)
    print("BONUS — hit your own HTTP endpoint, if it's running")
    print("=" * 60)
    port = settings.app_port
    try:
        response = requests.post(
            f"http://localhost:{port}/api/v1/ask",
            json={"query": QUERY, "top_k": 3},
            timeout=60,
        )
        print(f"POST /api/v1/ask -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"Skipped — your app isn't running on port {port}.")

    print("\nAll steps ran without errors — Week 5 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week5.md for the plan."
        )
