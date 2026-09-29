"""
Week 4 — hybrid indexing pipeline.

Wires TextChunker -> JinaEmbeddingsClient -> OpenSearchClient together:
chunk a paper, embed every chunk, and index each chunk + its vector into
the chunk index. Call this after a paper is already stored (Week 2) and
its parent doc is already indexed (Week 3).
"""

from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.indexing.text_chunker import TextChunker
from src.services.opensearch.client import OpenSearchClient


class HybridIndexer:
    def __init__(
        self,
        chunker: TextChunker,
        embeddings_client: JinaEmbeddingsClient,
        opensearch_client: OpenSearchClient,
    ) -> None:
        self.chunker = chunker
        self.embeddings_client = embeddings_client
        self.opensearch_client = opensearch_client

    def index_paper_chunks(self, arxiv_id: str, raw_text: str) -> int:
        """Chunk a paper, embed each chunk, index it. Returns chunk count.

        TODO:
        - chunks = self.chunker.chunk_paper(arxiv_id, raw_text)
        - if not chunks: return 0
        - vectors = self.embeddings_client.embed([c.text for c in chunks])
        - for chunk, vector in zip(chunks, vectors, strict=True):
            self.opensearch_client.index_chunk({
                "chunk_id": chunk.chunk_id,
                "arxiv_id": arxiv_id,
                "section_name": chunk.section_name,
                "chunk_text": chunk.text,
                "embedding": vector,
            })
        - return len(chunks)
        """
        raise NotImplementedError
