# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **learning scaffold**, not a working application. It's the user's own
from-scratch build of the `production-agentic-rag-course` (arXiv Paper
Curator, a 7-week RAG course) — deliberately written as plain Python
instead of that course's Jupyter notebooks, with the source laid out as
a real production FastAPI app. This project has its own local infra
(`compose.yml`: Postgres/OpenSearch/Ollama/Redis, same images/ports/
credentials as the course) so it's self-contained for everyday work.
The sibling checkout `../production-agentic-rag-course` still holds the
original notebooks and the course's own finished reference
implementation, and is only needed live for two things: Airflow (a
custom-built image, not replicated here) and Langfuse (Week 6, a
6-container stack of its own) — both explained in `compose.yml`'s
comments. Never run this project's `docker compose up -d` and the course
repo's at the same time; they claim the same host ports.

**Almost every function body in `src/` is `raise NotImplementedError`.**
That is intentional, not incomplete work to finish. The whole point is
for the user to write that logic themselves, week by week, guided by
`docs/week1.md` … `docs/week7.md`. **Do not fill in the TODOs / replace
`NotImplementedError` bodies with working implementations unless the
user explicitly asks you to write that specific piece.** If asked to
"help" generically, prefer explaining the approach (or reviewing code
the user wrote) over writing the implementation for them.

## Commands

```bash
uv sync                                              # install deps
cp .env.example .env                                 # then edit as needed
docker compose up -d                                 # this project's own Postgres/OpenSearch/Ollama/Redis — see compose.yml

uv run uvicorn src.main:app --reload --port 8100      # run the app (8100, not 8000 — avoids colliding with the course's own containerized API)

uv run python scripts/week1_verify_infra.py           # each week's check script, e.g. week2_test_arxiv_pipeline.py ... week7_test_agentic_rag.py

uv run ruff check .                                   # lint
uv run mypy src                                       # type check
uv run pytest                                         # tests (none exist yet — pytest is configured but no tests/ dir has been created)
```

Every `scripts/week*.py` imports from `src/`, so it will raise
`NotImplementedError` with a traceback pointing at the exact unfinished
function — that's the expected/desired behavior until the corresponding
week's TODOs are done, not a bug to fix.

## Architecture

- **Layering** (`src/routers` → `src/services/*` → `src/repositories` →
  `src/models`, with `src/schemas` for Pydantic I/O shapes) mirrors the
  course's own `src/` layout on purpose, so the user can cross-reference
  the two. There are no `factory.py` files (simplified out of the
  original course pattern) — services take plain constructor args, and
  routers/scripts build them directly from `get_settings()`.
- **`src/config.py`** grows incrementally: only Week 1's `Settings`
  fields (`debug`, `environment`, `app_port`) are implemented; every
  later week's fields are listed as commented TODOs (flat names, e.g.
  `opensearch_host`, `ollama_model` — no nested `__`-delimited settings
  groups). Scripts and other TODOs reference these exact flat names, so
  if you ever do add a field, keep the naming flat and consistent with
  what `.env.example` and the relevant `docs/weekN.md` already assume.
- **`docs/week1.md` … `week7.md` are the real guidance** — concept
  explanations and a file-by-file implementation approach for that week.
  `ROADMAP.md` is only a thin index into these. If the user asks a
  conceptual question ("why does chunking need overlap", "what does RRF
  do"), the matching `docs/weekN.md` likely already has the answer
  written out in this project's own words — check there before
  re-deriving from scratch.
- **`scripts/week*.py` are deliberately plain, linear, top-to-bottom
  code** — no shared helper module, no lambdas, no wrapper that catches
  `NotImplementedError` and reformats it. This was a deliberate choice
  after the user found an earlier `run_step()`-style abstraction hard to
  read; don't reintroduce that kind of indirection here even if it would
  reduce repetition across the seven scripts.
- Each script also does a best-effort `requests` call against the user's
  own running app (`http://localhost:{settings.app_port}`) for the
  relevant endpoint, skipping (not failing) if it isn't up.
