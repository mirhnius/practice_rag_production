"""
Week 7 — LangGraph nodes.

Each function takes the current GraphState and returns a partial update
to merge into it (LangGraph's convention — you don't mutate state in
place). Keep each node small and single-purpose, the way the course's
own nodes/ directory does (each node under ~30 lines).
"""

from src.services.agents.state import GraphState
from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.ollama.client import OllamaClient
from src.services.opensearch.client import OpenSearchClient


def guardrail_node(state: GraphState, ollama_client: OllamaClient) -> dict:
    """Decide whether `state["query"]` is in-scope for a research assistant.

    TODO: ask the LLM a short yes/no-style prompt — is this query a
    research question this arXiv assistant could plausibly answer, versus
    something clearly unrelated (e.g. "write me a poem about cats")?
    Return {"in_scope": bool, "reasoning_steps": [*state["reasoning_steps"], "..."]}.
    """
    raise NotImplementedError


def retrieve_node(
    state: GraphState,
    opensearch_client: OpenSearchClient,
    embeddings_client: JinaEmbeddingsClient,
) -> dict:
    """Run hybrid search for the (possibly rewritten) query.

    TODO:
    - query = state.get("rewritten_query") or state["query"]
    - query_embedding = embeddings_client.embed_query(query)
    - results = opensearch_client.search_hybrid(query, query_embedding)
    - return {"chunks": results["hits"],
              "retrieval_attempts": state.get("retrieval_attempts", 0) + 1,
              "reasoning_steps": [*state["reasoning_steps"], "..."]}
    """
    raise NotImplementedError


def grade_documents_node(state: GraphState, ollama_client: OllamaClient) -> dict:
    """Ask the LLM whether the retrieved chunks actually answer the query.

    TODO: build a short grading prompt (the query + chunk excerpts,
    "answer yes or no: are these relevant?"), parse the reply into a
    bool, return {"is_relevant": bool, "reasoning_steps": [...]}.
    """
    raise NotImplementedError


def rewrite_query_node(state: GraphState, ollama_client: OllamaClient) -> dict:
    """Rewrite a vague query into something more likely to retrieve well.

    TODO: ask the LLM to restate state["query"] as a more specific search
    query. Return {"rewritten_query": ..., "reasoning_steps": [...]}.
    """
    raise NotImplementedError


def generate_answer_node(state: GraphState, ollama_client: OllamaClient) -> dict:
    """TODO:
    from src.services.ollama.prompts import build_rag_prompt
    prompt = build_rag_prompt(state["query"], state["chunks"])
    answer = ollama_client.generate(prompt)
    return {"answer": answer, "reasoning_steps": [...]}
    """
    raise NotImplementedError


def out_of_scope_node(state: GraphState) -> dict:
    """TODO: return a canned decline, e.g.
    {"answer": "That's outside what this research assistant covers.",
     "reasoning_steps": [*state["reasoning_steps"], "Rejected as out of scope"]}
    """
    raise NotImplementedError
