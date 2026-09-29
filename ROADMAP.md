# Roadmap

Check off weeks as you complete them. For each week: read the concept
explanation at the linked path first, then fill in the `# TODO`s in the
listed files, then run the script until it passes.

All course paths below are relative to
`../production-agentic-rag-course` (the course checkout next to this repo).

## Week 1 — Infrastructure Foundation

- [ ] **Concept:** `notebooks/week1/README.md`, `notebooks/week1/week1_setup.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py), [`src/main.py`](src/main.py), [`src/routers/health.py`](src/routers/health.py)
- [ ] **Run:** `uv run python scripts/week1_verify_infra.py`
- Goal: settings load from `.env`, FastAPI app boots, and it can see
  Postgres / OpenSearch / Ollama running from the course's `docker compose`.

## Week 2 — Data Ingestion Pipeline

- [ ] **Concept:** `notebooks/week2/README.md`, `notebooks/week2/week2_arxiv_integration.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 2 fields),
      [`src/db/session.py`](src/db/session.py), [`src/models/paper.py`](src/models/paper.py),
      [`src/schemas/paper.py`](src/schemas/paper.py), [`src/repositories/paper.py`](src/repositories/paper.py),
      [`src/services/arxiv/client.py`](src/services/arxiv/client.py),
      [`src/services/pdf_parser/parser.py`](src/services/pdf_parser/parser.py),
      [`src/services/metadata_fetcher.py`](src/services/metadata_fetcher.py),
      [`src/routers/papers.py`](src/routers/papers.py)
- [ ] **Run:** `uv run python scripts/week2_test_arxiv_pipeline.py`
- Goal: fetch papers from arXiv with rate limiting, download + parse their
  PDFs, and upsert them into Postgres.

## Week 3 — Keyword Search Foundation (BM25)

- [ ] **Concept:** `notebooks/week3/README.md`, `notebooks/week3/week3_opensearch.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 3 fields),
      [`src/services/opensearch/index_config.py`](src/services/opensearch/index_config.py),
      [`src/services/opensearch/query_builder.py`](src/services/opensearch/query_builder.py),
      [`src/services/opensearch/client.py`](src/services/opensearch/client.py),
      [`src/routers/search.py`](src/routers/search.py)
- [ ] **Run:** `uv run python scripts/week3_test_search.py`
- Goal: create the OpenSearch index, index the papers from Postgres, and
  get relevance-ranked BM25 search results back through your own API.

## Week 4 — Chunking & Hybrid Search

- [ ] **Concept:** `notebooks/week4/README.md`, `notebooks/week4/week4_hybrid_search.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 4 fields),
      [`src/services/opensearch/index_config.py`](src/services/opensearch/index_config.py) (chunk mapping),
      [`src/services/opensearch/client.py`](src/services/opensearch/client.py) (chunk-index methods),
      [`src/services/indexing/text_chunker.py`](src/services/indexing/text_chunker.py),
      [`src/services/embeddings/jina_client.py`](src/services/embeddings/jina_client.py),
      [`src/services/indexing/hybrid_indexer.py`](src/services/indexing/hybrid_indexer.py),
      [`src/routers/hybrid_search.py`](src/routers/hybrid_search.py)
- [ ] **Run:** `uv run python scripts/week4_test_hybrid_search.py`
- Goal: section-based chunking with overlap, real embeddings, and RRF
  fusion combining BM25 + vector search in one endpoint.

## Week 5 — Complete RAG Pipeline

- [ ] **Concept:** `notebooks/week5/README.md`, `notebooks/week5/week5_complete_rag_system.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 5 fields),
      [`src/services/ollama/client.py`](src/services/ollama/client.py),
      [`src/services/ollama/prompts.py`](src/services/ollama/prompts.py),
      [`src/routers/ask.py`](src/routers/ask.py)
- [ ] **Run:** `uv run python scripts/week5_test_rag.py`
- Goal: query → hybrid search → prompt assembly → local LLM answer, plus
  a streaming variant.

## Week 6 — Production Monitoring & Caching

- [ ] **Concept:** `notebooks/week6/README.md`, `notebooks/week6/week6_cache_testing.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 6 fields),
      [`src/services/cache/redis_cache.py`](src/services/cache/redis_cache.py),
      [`src/services/langfuse_tracer.py`](src/services/langfuse_tracer.py),
      update [`src/routers/ask.py`](src/routers/ask.py) to use both
- [ ] **Run:** `uv run python scripts/week6_test_cache_and_tracing.py`
- Goal: identical repeat queries hit Redis (~100ms) instead of the full
  pipeline (~15-20s), and every call is traced in Langfuse.

## Week 7 — Agentic RAG + Telegram Bot

- [ ] **Concept:** `notebooks/week7/README.md`, `notebooks/week7/week7_agentic_rag.ipynb`
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 7 fields),
      [`src/services/agents/state.py`](src/services/agents/state.py),
      [`src/services/agents/nodes.py`](src/services/agents/nodes.py),
      [`src/services/agents/graph.py`](src/services/agents/graph.py),
      [`src/routers/agentic_ask.py`](src/routers/agentic_ask.py),
      optionally [`src/services/telegram_bot.py`](src/services/telegram_bot.py)
- [ ] **Run:** `uv run python scripts/week7_test_agentic_rag.py`
- Goal: a LangGraph workflow that decides whether to retrieve, grades
  document relevance, rewrites the query on a miss, and exposes its
  reasoning steps.
