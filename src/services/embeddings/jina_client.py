"""
Week 4 — Jina AI embeddings client.

Turns text into 1024-dim vectors for semantic search.
Docs: https://jina.ai/embeddings/ — POST to
https://api.jina.ai/v1/embeddings with an `Authorization: Bearer <key>` header.
Get a free key at https://jina.ai/embeddings/ (see the Week 4 course README
for the exact signup flow).
"""

import requests


class JinaEmbeddingsClient:
    def __init__(self, api_key: str, model: str = "jina-embeddings-v3") -> None:
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.jina.ai/v1/embeddings"

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts, preserving input order.

        TODO:
        - response = requests.post(self.endpoint,
              headers={"Authorization": f"Bearer {self.api_key}"},
              json={"model": self.model, "input": texts}, timeout=30)
        - response.raise_for_status()
        - return [item["embedding"] for item in response.json()["data"]]
        - if `texts` can be long, consider batching (Jina caps request size)
        """
        raise NotImplementedError

    def embed_query(self, query: str) -> list[float]:
        """TODO: return self.embed([query])[0]"""
        raise NotImplementedError
