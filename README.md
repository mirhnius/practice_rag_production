# Practice RAG Production

My own build-along of the **arXiv Paper Curator** course
(`production-agentic-rag-course`), written as plain Python instead of
Jupyter notebooks. Same architecture, same week-by-week progression — but
every file here is a skeleton I fill in myself so I actually learn it,
instead of running someone else's notebook cells.

## How this is organized

- **`docs/`** — one guide per week (`week1.md` ... `week7.md`). This is
  where the actual teaching lives: what the concept is and why it works
  the way it does, then a file-by-file walkthrough of the approach for
  everything you'll implement that week. Read the guide *before* opening
  any code — the TODO comments in `src/` are short reminders, not the
  explanation.
- **`src/`** — the actual application, laid out the same way a real
  production RAG service would be (routers / services / repositories /
  models), growing by one or two modules each week. Every file starts
  as a stub: docstring explaining *what* it's for and *why*, function/class
  signatures already typed out, and `# TODO` comments instead of a
  finished body.
- **`scripts/`** — one plain script per week (`week1_verify_infra.py`,
  `week2_test_arxiv_pipeline.py`, ...). These replace the course's
  Jupyter notebooks: same step-by-step flow, printed section by section,
  no helper framework of their own — every line is visible top to bottom,
  the same way a notebook reads cell by cell. Each script calls straight
  into the `src/` modules for that week, so it will raise
  `NotImplementedError` — with a traceback pointing at the exact file and
  line — until I've actually written the code. That's the point: it's my
  checklist, not something to debug.
- **`ROADMAP.md`** — the week-by-week index: which guide to read, which
  files to implement, which script proves it works.

## Setup

```bash
uv sync
cp .env.example .env
```

This repo does **not** duplicate the course's Docker/Postgres/OpenSearch/
Airflow/Redis setup — that's infrastructure config, not something worth
retyping by hand. Start it from the course checkout instead:

```bash
cd ../production-agentic-rag-course
docker compose up -d
```

Then come back here — `.env` already points at `localhost` for every
service, the same way the course notebooks do when run outside Docker.

## Working through it

1. Open [ROADMAP.md](ROADMAP.md) and pick the next unchecked week.
2. Read that week's guide in `docs/` — the concept, then the plan for
   every file you're about to touch.
3. Implement the `# TODO`s in the files it lists.
4. Run that week's script in `scripts/`. When it runs to the end without
   a `NotImplementedError` traceback, move on.
5. If you get properly stuck on a specific function, the course's own
   `README.md`/notebook for that week (linked at the bottom of each
   guide) has more context, and the finished reference implementation is
   sitting right next to this repo at
   `../production-agentic-rag-course/src/...` — try for real first, then
   peek only at the one function you're stuck on.

## Layout

```
docs/                        # week1.md ... week7.md — read these first
src/
├── config.py                 # Week 1 — settings from .env
├── main.py                   # Week 1 — FastAPI app, wires up routers
├── db/session.py              # Week 2 — SQLAlchemy engine/session
├── models/paper.py             # Week 2 — Paper ORM model
├── repositories/paper.py       # Week 2 — Paper CRUD / upsert
├── schemas/                  # Pydantic request/response/data models
├── services/
│   ├── arxiv/client.py         # Week 2 — rate-limited arXiv API client
│   ├── pdf_parser/parser.py    # Week 2 — Docling PDF parsing
│   ├── metadata_fetcher.py     # Week 2 — orchestrates the ingestion pipeline
│   ├── opensearch/            # Week 3 — index config, query builder, client
│   ├── indexing/               # Week 4 — chunking + indexing pipeline
│   ├── embeddings/jina_client.py  # Week 4 — Jina embeddings client
│   ├── ollama/                # Week 5 — local LLM client + prompts
│   ├── cache/redis_cache.py    # Week 6 — response caching
│   ├── langfuse_tracer.py      # Week 6 — pipeline tracing
│   ├── agents/                # Week 7 — LangGraph agentic RAG
│   └── telegram_bot.py         # Week 7 — Telegram bot integration
└── routers/                  # FastAPI endpoints, one set per week
scripts/                     # Week 1-7 runnable scripts (the notebook replacement)
```
