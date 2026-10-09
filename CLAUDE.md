# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **learning scaffold**, not a working application. It's the user's own
from-scratch build of the `production-agentic-rag-course` (arXiv Paper
Curator, a 7-week RAG course) — deliberately written as plain Python
instead of that course's Jupyter notebooks, with the source laid out as
a real production FastAPI app. This project has its own local infra —
`compose.yml` is a full 12-container stack (Postgres, OpenSearch +
Dashboards, Ollama, Redis, Airflow, and all 6 Langfuse pieces:
ClickHouse, langfuse-postgres/-redis/-minio/-web/-worker) — so nothing
requires touching the course repo for everyday work, including Week 6.
Airflow builds from `./airflow`, a local copy of the course's own
Dockerfile; Langfuse's services are straight copies of the course's own
service definitions. The sibling checkout
`../production-agentic-rag-course` is needed only for the original
notebooks and the course's finished reference `src/` implementation
(for when the user wants to peek at one function). Never run this
project's `docker compose up -d` and the course repo's at the same
time; they claim the same host ports (5432, 5433, 6380, 8080, 9200,
11434, ...).

**Three real bugs were found and fixed while copying this infra in —
don't "clean up" or revert these, they're deliberate:**
1. `airflow/entrypoint.sh` additionally removes
   `airflow-webserver-monitor.pid` (the course's own entrypoint only
   clears `-webserver.pid`/`-scheduler.pid`, missing this one — it
   survives container restarts on the persistent volume and makes the
   webserver refuse to start with "already running under PID X" after
   any unclean shutdown).
2. `compose.yml`'s `langfuse-web` healthcheck uses `wget`, not `curl` —
   the `langfuse/langfuse:3` image doesn't have `curl` installed (the
   course's own compose.yml does, so its healthcheck silently always
   fails too).
3. `compose.yml`'s `langfuse-web` sets `HOSTNAME: "0.0.0.0"` explicitly
   — Docker auto-sets `HOSTNAME` to the container ID, and this image's
   Next.js standalone server binds to exactly that address instead of
   all interfaces, breaking any in-container loopback request (the
   healthcheck, or anything else hitting `localhost`/`127.0.0.1` from
   inside the container) even though the published port still works
   fine from outside.

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
docker compose up -d                                 # full local infra: Postgres/OpenSearch/Ollama/Redis/Airflow/Langfuse — see compose.yml (first run builds Airflow's image, several minutes)

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
- **`src/services/exploration.py`** is a deliberate exception to the
  "real production app" framing above — four throwaway stub functions
  (pull an Ollama model, generate a test response, list Postgres tables,
  check OpenSearch health) mirroring the course notebook's hands-on
  Week 1 cells, called from the end of `week1_verify_infra.py`. Not the
  polished client you'd build in later weeks; don't hold it to that bar.
- **Tables are created by `init_db()` in `src/db/session.py`**
  (`Base.metadata.create_all`), called as Step 0 of
  `scripts/week2_test_arxiv_pipeline.py` — there are no migrations
  (Alembic is installed but unused), so `create_all` never alters an
  existing table; a column change means dropping the table. The model
  import lives *inside* `init_db()` on purpose: a top-level import is
  circular, and without the import `create_all` silently creates nothing.
  When the FastAPI app gets DB-backed routes, it needs to call `init_db()`
  too (e.g. in a lifespan hook) — it doesn't yet, deliberately, so the
  app still boots without Postgres.
