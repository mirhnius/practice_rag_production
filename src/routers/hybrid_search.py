"""
Week 4 — hybrid search API.

POST /api/v1/hybrid-search — one endpoint supporting BM25, vector, or
hybrid (RRF) search depending on `use_hybrid`. Remember to add
`app.include_router(hybrid_search.router)` in src/main.py once this works.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/hybrid-search", tags=["hybrid-search"])


class HybridSearchRequest(BaseModel):
    query: str
    use_hybrid: bool = True
    size: int = 10
    categories: list[str] | None = None


@router.post("")
def hybrid_search(request: HybridSearchRequest) -> dict:
    """TODO:
    settings = get_settings()
    client = OpenSearchClient(settings.opensearch_host)
    if request.use_hybrid:
        embeddings_client = JinaEmbeddingsClient(settings.jina_api_key)
        query_embedding = embeddings_client.embed_query(request.query)
        return client.search_hybrid(request.query, query_embedding, request.size)
    return client.search(request.query, request.categories, request.size)

    Add a fallback: if embedding generation raises, log it and fall back
    to plain BM25 rather than 500ing the whole request (that's the
    "graceful degradation" behavior the Week 4 README describes).
    """
    raise NotImplementedError
