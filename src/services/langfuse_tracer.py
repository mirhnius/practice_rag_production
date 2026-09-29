"""
Week 6 — Langfuse tracing.

Wraps the RAG pipeline so every call shows up in the Langfuse dashboard:
retrieval latency, generation latency, cache hit/miss, and the
prompt/response themselves. Docs: https://langfuse.com/docs
"""

from langfuse import Langfuse


class LangfuseTracer:
    def __init__(self, enabled: bool, public_key: str, secret_key: str, host: str) -> None:
        self.enabled = enabled
        # TODO: if enabled:
        #     self.client = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
        self.client: Langfuse | None = None  # TODO

    def trace_rag_call(
        self, query: str, answer: str, cache_hit: bool, latency_ms: float
    ) -> None:
        """Record one RAG call as a Langfuse trace.

        TODO:
        - if not self.enabled: return
        - self.client.trace(name="rag-ask", input={"query": query},
              output={"answer": answer},
              metadata={"cache_hit": cache_hit, "latency_ms": latency_ms})
        - wrap the whole thing in try/except so a tracing failure never
          breaks the actual RAG response — log and move on
        """
        raise NotImplementedError
