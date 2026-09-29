"""
Week 7 — agentic RAG API.

POST /api/v1/ask-agentic — same question-answering job as /api/v1/ask,
but routed through the LangGraph workflow so it can decide not to
retrieve, grade its own results, and rewrite the query on a miss.
Remember to add `app.include_router(agentic_ask.router)` in src/main.py.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["agentic-ask"])


class AgenticAskRequest(BaseModel):
    query: str
    top_k: int = 3
    use_hybrid: bool = True


class AgenticAskResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]
    reasoning_steps: list[str]
    retrieval_attempts: int


@router.post("/ask-agentic", response_model=AgenticAskResponse)
def ask_agentic(request: AgenticAskRequest) -> AgenticAskResponse:
    """TODO:
    graph = build_agentic_rag_graph(opensearch_client, embeddings_client, ollama_client)
    final_state = graph.invoke(
        {"query": request.query, "reasoning_steps": [], "retrieval_attempts": 0}
    )
    sources = sorted({chunk["arxiv_id"] for chunk in final_state.get("chunks", [])})
    return AgenticAskResponse(
        query=request.query,
        answer=final_state["answer"],
        sources=sources,
        reasoning_steps=final_state["reasoning_steps"],
        retrieval_attempts=final_state.get("retrieval_attempts", 0),
    )
    """
    raise NotImplementedError
