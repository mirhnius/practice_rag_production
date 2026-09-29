"""
Week 7 — agentic RAG.

Notebook replacement for `notebooks/week7/week7_agentic_rag.ipynb`. Runs
the three scenarios the course specifically calls out: an out-of-scope
query, a query that should retrieve successfully, and a vague query that
should trigger a rewrite.

    uv run python scripts/week7_test_agentic_rag.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._util import run_step  # noqa: E402
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
    print("=== Week 7: agentic RAG ===")
    settings = get_settings()

    opensearch_client = OpenSearchClient(settings.opensearch_host)
    embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
    ollama_client = OllamaClient(settings.ollama_host, settings.ollama_model)

    graph = run_step(
        "Build the LangGraph workflow",
        "src/services/agents/graph.py (build_agentic_rag_graph)",
        lambda: build_agentic_rag_graph(opensearch_client, embeddings_client, ollama_client),
    )
    if not graph:
        return

    for label, query in SCENARIOS:
        def _run(query: str = query) -> dict:
            return graph.invoke(
                {"query": query, "reasoning_steps": [], "retrieval_attempts": 0}
            )

        result = run_step(
            f"Scenario: {label} — {query!r}",
            "src/services/agents/nodes.py + graph.py",
            _run,
        )
        if result:
            print(f"    answer: {result.get('answer', '')[:200]}")
            print(f"    reasoning: {result.get('reasoning_steps', [])}")


if __name__ == "__main__":
    main()
