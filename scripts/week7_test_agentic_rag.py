"""
Week 7 — agentic RAG.

Read docs/week7.md first. This is the notebook replacement for
notebooks/week7/week7_agentic_rag.ipynb — a plain, top-to-bottom script,
already complete (nothing to implement here; it's your checking
harness).

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week7_test_agentic_rag.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_settings  # noqa: E402
from src.services.agents.graph import build_agentic_rag_graph  # noqa: E402
from src.services.embeddings.jina_client import JinaEmbeddingsClient  # noqa: E402
from src.services.ollama.client import OllamaClient  # noqa: E402
from src.services.opensearch.client import OpenSearchClient  # noqa: E402

SCENARIOS = [
    ("Out-of-scope rejection", "Write me a poem about cats"),
    ("Successful retrieval", "What are attention mechanisms in transformers?"),
    ("Vague query, may need a rewrite", "Tell me about ML stuff"),
]


def main() -> None:
    settings = get_settings()

    opensearch_client = OpenSearchClient(settings.opensearch_host)
    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    ollama_client = OllamaClient(settings.ollama_host, settings.ollama_model)

    print("=" * 60)
    print("STEP 1 — build the LangGraph workflow")
    print("=" * 60)
    graph = build_agentic_rag_graph(opensearch_client, embeddings_client, ollama_client)
    print("Graph built.")

    for i, (label, query) in enumerate(SCENARIOS, start=2):
        print()
        print("=" * 60)
        print(f"STEP {i} — scenario: {label} — {query!r}")
        print("=" * 60)
        result = graph.invoke({"query": query, "reasoning_steps": [], "retrieval_attempts": 0})
        print(f"Answer: {result.get('answer', '')[:200]}")
        print(f"Reasoning steps: {result.get('reasoning_steps', [])}")
        print(f"Retrieval attempts: {result.get('retrieval_attempts', 0)}")

    print("\nAll steps ran without errors — Week 7 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week7.md for the plan."
        )
