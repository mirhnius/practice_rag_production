"""
Week 7 — LangGraph workflow wiring.

    START -> guardrail --(out of scope)--> out_of_scope -> END
                     \\--(in scope)------> retrieve -> grade
                                              (relevant)--> generate -> END
                                              (not relevant, attempts left)
                                                  --> rewrite -> retrieve -> grade -> ...
                                              (not relevant, out of attempts)
                                                  --> generate -> END  (best effort)

Docs: https://langchain-ai.github.io/langgraph/
"""

from langgraph.graph import END, StateGraph

from src.services.agents.nodes import (
    generate_answer_node,
    grade_documents_node,
    guardrail_node,
    out_of_scope_node,
    retrieve_node,
    rewrite_query_node,
)
from src.services.agents.state import GraphState
from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.ollama.client import OllamaClient
from src.services.opensearch.client import OpenSearchClient

MAX_RETRIEVAL_ATTEMPTS = 2


def build_agentic_rag_graph(
    opensearch_client: OpenSearchClient,
    embeddings_client: JinaEmbeddingsClient,
    ollama_client: OllamaClient,
):
    """Wire the nodes in src/services/agents/nodes.py into a compiled graph.

    TODO:
    - graph = StateGraph(GraphState)
    - graph.add_node("guardrail", lambda s: guardrail_node(s, ollama_client))
    - graph.add_node("retrieve", lambda s: retrieve_node(s, opensearch_client, embeddings_client))
    - graph.add_node("grade", lambda s: grade_documents_node(s, ollama_client))
    - graph.add_node("rewrite", lambda s: rewrite_query_node(s, ollama_client))
    - graph.add_node("generate", lambda s: generate_answer_node(s, ollama_client))
    - graph.add_node("out_of_scope", out_of_scope_node)
    - graph.set_entry_point("guardrail")
    - graph.add_conditional_edges(
          "guardrail",
          lambda s: "in_scope" if s["in_scope"] else "out_of_scope",
          {"in_scope": "retrieve", "out_of_scope": "out_of_scope"},
      )
    - graph.add_edge("out_of_scope", END)
    - graph.add_edge("retrieve", "grade")
    - graph.add_conditional_edges(
          "grade",
          lambda s: (
              "generate" if s["is_relevant"]
              else "rewrite" if s["retrieval_attempts"] < MAX_RETRIEVAL_ATTEMPTS
              else "generate"  # give up gracefully, answer with what we have
          ),
          {"generate": "generate", "rewrite": "rewrite"},
      )
    - graph.add_edge("rewrite", "retrieve")
    - graph.add_edge("generate", END)
    - return graph.compile()
    """
    raise NotImplementedError
