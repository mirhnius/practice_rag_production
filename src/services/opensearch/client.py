"""
Week 3 — OpenSearch client.

A thin wrapper around opensearch-py that the rest of the app depends on,
instead of importing OpenSearch directly everywhere. Health checks, index
management, indexing, and search all live here (factory pattern: build
one of these from settings once, reuse it everywhere).
"""

from opensearchpy import OpenSearch

from src.services.opensearch import query_builder
from src.services.opensearch.index_config import (
    CHUNK_INDEX_MAPPING,
    CHUNK_INDEX_NAME,
    INDEX_MAPPING,
    INDEX_NAME,
)


class OpenSearchClient:
    def __init__(self, host: str, index_name: str = INDEX_NAME) -> None:
        self.index_name = index_name
        # TODO: self.client = OpenSearch(hosts=[host], use_ssl=False, verify_certs=False)
        self.client: OpenSearch | None = None  # TODO

    def health_check(self) -> bool:
        """TODO: return self.client.cluster.health()["status"] in {"green", "yellow"}"""
        raise NotImplementedError

    def create_index_if_missing(self) -> bool:
        """TODO:
        if not self.client.indices.exists(self.index_name):
            self.client.indices.create(self.index_name, body=INDEX_MAPPING)
            return True
        return False
        """
        raise NotImplementedError

    def index_paper(self, paper: dict) -> None:
        """TODO: self.client.index(index=self.index_name, id=paper["arxiv_id"], body=paper)"""
        raise NotImplementedError

    def search(
        self, query: str, categories: list[str] | None = None, size: int = 10
    ) -> dict:
        """Run a BM25 search and return a simplified result.

        TODO:
        - body = query_builder.build_filtered_query(query, categories, size)
        - response = self.client.search(index=self.index_name, body=body)
        - reshape response["hits"]["hits"] into
          {"total": <int>, "hits": [{"arxiv_id", "title", "score", ...}, ...]}
          so callers don't need to know OpenSearch's raw response shape
        """
        raise NotImplementedError

    # --- Week 4: chunk-level hybrid search ---

    def create_chunk_index_if_missing(self) -> bool:
        """TODO: same idea as create_index_if_missing, but targeting
        CHUNK_INDEX_NAME / CHUNK_INDEX_MAPPING.
        """
        raise NotImplementedError

    def index_chunk(self, chunk: dict) -> None:
        """TODO: self.client.index(index=CHUNK_INDEX_NAME, id=chunk["chunk_id"], body=chunk)"""
        raise NotImplementedError

    def search_vector(self, query_embedding: list[float], size: int = 10) -> dict:
        """A k-NN similarity search over the chunk index.

        TODO: query body along the lines of
        {"size": size, "query": {"knn": {"embedding": {"vector": query_embedding, "k": size}}}}
        against CHUNK_INDEX_NAME. Reshape the response the same way `search()` does.
        """
        raise NotImplementedError

    def search_hybrid(
        self, query: str, query_embedding: list[float], size: int = 10
    ) -> dict:
        """Combine BM25 + vector search with Reciprocal Rank Fusion (RRF).

        TODO:
        - run a BM25 query (query_builder.build_match_query) and a vector
          query (search_vector) against CHUNK_INDEX_NAME, each returning
          more than `size` results (e.g. size * 2) so fusion has room to
          re-rank
        - RRF score for a doc = sum, over every ranking it appears in, of
          1 / (k + rank) — k is conventionally 60. A doc that ranks well
          in *both* BM25 and vector search wins.
        - merge on arxiv_id/chunk_id, sort by RRF score descending,
          truncate to `size`
        """
        raise NotImplementedError
