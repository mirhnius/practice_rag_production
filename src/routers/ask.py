"""
Week 5 — RAG API.

Two endpoints: /api/v1/ask (single response) and /api/v1/stream (Server-
Sent Events). Both run the same retrieve -> prompt -> generate pipeline.
Remember to add `app.include_router(ask.router)` in src/main.py.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["ask"])


class AskRequest(BaseModel):
    query: str
    top_k: int = 3
    use_hybrid: bool = True


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """TODO:
    - retrieve chunks the same way src/routers/hybrid_search.py does
      (embed the query, call OpenSearchClient.search_hybrid or .search)
    - prompt = build_rag_prompt(request.query, chunks)
    - answer = OllamaClient(settings.ollama_host, settings.ollama_model).generate(prompt)
    - sources = sorted a set of the arxiv_ids the chunks came from
    - return AskResponse(query=request.query, answer=answer, sources=sources)

    TODO (Week 6): wrap this in caching + tracing:
    - cache = RedisCache(...); hit = cache.get(request.query, top_k=request.top_k)
    - if hit: return AskResponse(**hit)
    - time the retrieve+generate work, cache.set(...) the result, then
      tracer.trace_rag_call(request.query, answer, cache_hit=False, latency_ms=...)
    """
    raise NotImplementedError


@router.post("/stream")
def ask_stream(request: AskRequest) -> StreamingResponse:
    """TODO:
    - same retrieval + prompt assembly as ask()
    - return StreamingResponse(
          ollama_client.generate_stream(prompt), media_type="text/event-stream"
      )
    """
    raise NotImplementedError
