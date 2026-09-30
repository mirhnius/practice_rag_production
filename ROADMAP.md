# Roadmap

Check off weeks as you complete them. For each week, **read the guide in
`docs/` first** — that's where the concepts and the file-by-file plan
live, not just a checklist. This file is only the index.

## Week 1 — Infrastructure Foundation

- [ ] **Read:** [docs/week1.md](docs/week1.md)
- [ ] **Implement:** [`src/routers/health.py`](src/routers/health.py),
      [`src/services/exploration.py`](src/services/exploration.py) (optional hands-on exploration)
- [ ] **Run:** `uv run python scripts/week1_verify_infra.py`

## Week 2 — Data Ingestion Pipeline

- [ ] **Read:** [docs/week2.md](docs/week2.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 2 fields),
      [`src/db/session.py`](src/db/session.py), [`src/models/paper.py`](src/models/paper.py),
      [`src/schemas/paper.py`](src/schemas/paper.py), [`src/repositories/paper.py`](src/repositories/paper.py),
      [`src/services/arxiv/client.py`](src/services/arxiv/client.py),
      [`src/services/pdf_parser/parser.py`](src/services/pdf_parser/parser.py),
      [`src/services/metadata_fetcher.py`](src/services/metadata_fetcher.py),
      [`src/routers/papers.py`](src/routers/papers.py)
- [ ] **Run:** `uv run python scripts/week2_test_arxiv_pipeline.py`

## Week 3 — Keyword Search Foundation (BM25)

- [ ] **Read:** [docs/week3.md](docs/week3.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 3 fields),
      [`src/services/opensearch/index_config.py`](src/services/opensearch/index_config.py),
      [`src/services/opensearch/query_builder.py`](src/services/opensearch/query_builder.py),
      [`src/services/opensearch/client.py`](src/services/opensearch/client.py),
      [`src/routers/search.py`](src/routers/search.py)
- [ ] **Run:** `uv run python scripts/week3_test_search.py`

## Week 4 — Chunking & Hybrid Search

- [ ] **Read:** [docs/week4.md](docs/week4.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 4 fields),
      [`src/services/opensearch/index_config.py`](src/services/opensearch/index_config.py) (chunk mapping),
      [`src/services/opensearch/client.py`](src/services/opensearch/client.py) (chunk-index methods),
      [`src/services/indexing/text_chunker.py`](src/services/indexing/text_chunker.py),
      [`src/services/embeddings/jina_client.py`](src/services/embeddings/jina_client.py),
      [`src/services/indexing/hybrid_indexer.py`](src/services/indexing/hybrid_indexer.py),
      [`src/routers/hybrid_search.py`](src/routers/hybrid_search.py)
- [ ] **Run:** `uv run python scripts/week4_test_hybrid_search.py`

## Week 5 — Complete RAG Pipeline

- [ ] **Read:** [docs/week5.md](docs/week5.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 5 fields),
      [`src/services/ollama/client.py`](src/services/ollama/client.py),
      [`src/services/ollama/prompts.py`](src/services/ollama/prompts.py),
      [`src/routers/ask.py`](src/routers/ask.py)
- [ ] **Run:** `uv run python scripts/week5_test_rag.py`

## Week 6 — Production Monitoring & Caching

- [ ] **Read:** [docs/week6.md](docs/week6.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 6 fields),
      [`src/services/cache/redis_cache.py`](src/services/cache/redis_cache.py),
      [`src/services/langfuse_tracer.py`](src/services/langfuse_tracer.py),
      update [`src/routers/ask.py`](src/routers/ask.py) to use both
- [ ] **Run:** `uv run python scripts/week6_test_cache_and_tracing.py`

## Week 7 — Agentic RAG + Telegram Bot

- [ ] **Read:** [docs/week7.md](docs/week7.md)
- [ ] **Implement:** [`src/config.py`](src/config.py) (Week 7 fields),
      [`src/services/agents/state.py`](src/services/agents/state.py),
      [`src/services/agents/nodes.py`](src/services/agents/nodes.py),
      [`src/services/agents/graph.py`](src/services/agents/graph.py),
      [`src/routers/agentic_ask.py`](src/routers/agentic_ask.py),
      optionally [`src/services/telegram_bot.py`](src/services/telegram_bot.py)
- [ ] **Run:** `uv run python scripts/week7_test_agentic_rag.py`
