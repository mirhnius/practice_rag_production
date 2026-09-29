"""
Week 5 — complete RAG pipeline (retrieval + local LLM).

Notebook replacement for
`notebooks/week5/week5_complete_rag_system.ipynb`. Complete harness —
retrieves chunks, builds the prompt, and generates an answer both as a
single response and streamed token-by-token.

    uv run python scripts/week5_test_rag.py

Needs OpenSearch (with chunks indexed from Week 4) and Ollama running,
with a model pulled, e.g.:
    docker exec rag-ollama ollama pull llama3.2:1b
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from scripts._util import run_step  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.services.embeddings.jina_client import JinaEmbeddingsClient  # noqa: E402
from src.services.ollama.client import OllamaClient  # noqa: E402
from src.services.ollama.prompts import build_rag_prompt  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402


def main() -> None:
    print("=== Week 5: complete RAG pipeline ===")
    settings = get_settings()
    query = "What are transformers in machine learning?"

    opensearch_client = OpenSearchClient(settings.opensearch_host)
    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    ollama_client = OllamaClient(settings.ollama_host, settings.ollama_model)

    query_vector = run_step(
        "Embed the query",
        "src/services/embeddings/jina_client.py (embed_query)",
        lambda: embeddings_client.embed_query(query),
    )

    results = None
    if query_vector:
        results = run_step(
            "Hybrid search for relevant chunks",
            "src/services/opensearch/client.py (search_hybrid)",
            lambda: opensearch_client.search_hybrid(query, query_vector, size=3),
        )

    chunks = (results or {}).get("hits", [])
    if not chunks:
        print(
            "\nNo chunks retrieved — run scripts/week4_test_hybrid_search.py first "
            "so there's something to search over."
        )
        return

    prompt = run_step(
        "Build the RAG prompt",
        "src/services/ollama/prompts.py (build_rag_prompt)",
        lambda: build_rag_prompt(query, chunks),
    )
    if not prompt:
        return

    answer = run_step(
        f"Generate an answer with {settings.ollama_model}",
        "src/services/ollama/client.py (generate)",
        lambda: ollama_client.generate(prompt),
    )
    if answer:
        print(f"\n    Answer: {answer[:500]}")

    run_step(
        "Generate the same answer via streaming",
        "src/services/ollama/client.py (generate_stream)",
        lambda: "".join(ollama_client.generate_stream(prompt)),
    )

    port = settings.app_port
    try:
        response = requests.post(
            f"http://localhost:{port}/api/v1/ask",
            json={"query": query, "top_k": 3},
            timeout=60,
        )
        print(f"\n[OK] POST /api/v1/ask on your own app -> {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"\n[SKIP] Your app isn't running on port {port}.")


if __name__ == "__main__":
    main()
