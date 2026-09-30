# Week 1 — Infrastructure Foundation

**Read this before opening any code.** It explains what you're building
and why, so the TODO comments in the files make sense instead of feeling
like random instructions.

## What you're building this week

Nothing "AI" yet — just the plumbing every later week depends on: your
own FastAPI app, plus confirmation that the local services (Postgres,
OpenSearch, Ollama) are reachable. Getting this boring part solid now is
what makes weeks 2-7 feel like adding one piece at a time instead of
debugging infrastructure and RAG logic at once.

## The pieces

| Service | What it's for | Where it runs |
|---|---|---|
| **Your FastAPI app** | The app you're building (`src/main.py`) | locally, port 8100 |
| **PostgreSQL** | Stores paper metadata (Week 2+) | Docker, port 5432 |
| **OpenSearch** | Search engine for BM25 + vectors (Week 3+) | Docker, port 9200 |
| **Ollama** | Runs a local LLM (Week 5+) | Docker, port 11434 |
| **Redis** | Response caching (Week 6+) | Docker, port 6379 |
| **Airflow** *(course repo only)* | Optional workflow scheduler | Docker, port 8080 |

You don't build any of the Docker services — Postgres/OpenSearch/Ollama/
Redis come from this project's own `docker compose up -d` (see
`compose.yml` at the repo root). Airflow is real, live infrastructure in
the actual course (it's what runs `arxiv_paper_ingestion`, the real DAG)
— it's just not in *this project's* compose.yml, since it needs a
custom-built image rather than an off-the-shelf one. Start it from
`../production-agentic-rag-course` whenever you want to look at it; the
Week 1 script below checks for it too, it just doesn't require it. What
you *do* build here is the app that talks to all of these.

## Files to implement

### `src/config.py`

This is a `Settings` class (using `pydantic-settings`) that reads
`.env` and gives you typed, validated access to every config value —
`get_settings().debug` instead of `os.environ.get("DEBUG") == "true"`
scattered everywhere. Two fields are already there (`debug`,
`environment`) as a working example; leave them as reference and don't
touch them.

**Nothing to implement in Week 1** — the fields you'll add for later
weeks are listed as TODO comments already. You'll come back to this file
every week and add a few more fields.

### `src/main.py`

Already fully written for you (it's glue code, not something to learn
by re-deriving). It creates the FastAPI app and includes `health.router`.
Each later week, you'll uncomment one more `include_router(...)` line as
you build that week's router.

### `src/routers/health.py`

**This is your one real task this week.** Implement `health_check()` so
it returns a dict FastAPI can serialize to JSON, at minimum:

```
{"status": "ok"}
```

That's genuinely enough for Week 1. The interesting version of this
function — checking Postgres/OpenSearch/Ollama are all actually
reachable and reporting per-service status — only makes sense once you
have clients for those services, which starts in Week 3. Come back and
extend it then if you want; it's not required.

### `src/services/exploration.py`

**Optional, but worth doing.** The course's own Week 1 notebook spends
most of its time not writing code, but manually poking each service:
pulling an Ollama model and generating from it, checking what's in
Postgres, checking OpenSearch's cluster health. That's genuinely useful
— it's how you build confidence each dependency actually works, before
you write the real pipeline against it in later weeks. Is this "real
production" practice? Mostly yes — smoke-testing your dependencies
before relying on them is standard (often called a "preflight" or
"readiness" check). The one part of the notebook that *isn't* really a
production pattern is clicking through a UI by hand — writing the
equivalent as code, which is what this file is, is the more
production-realistic version of the same idea.

Four functions, each a small, throwaway call — not the polished client
you'll build in later weeks (that's `OllamaClient` in Week 5,
`OpenSearchClient` in Week 3):

- `pull_ollama_model` — `POST /api/pull` so you have a model to
  generate with (a few GB the first time; give it a long timeout)
- `generate_test_response` — one `POST /api/generate` call, timed, so
  you know now if generation is painfully slow rather than discovering
  it while debugging Week 5
- `list_postgres_tables` — query `information_schema.tables`; expect an
  empty (or near-empty) list before Week 2 exists
- `opensearch_cluster_health` — `GET /_cluster/health`, the same thing
  you'd otherwise check by opening OpenSearch Dashboards

## Running it

```bash
uv sync
cp .env.example .env
docker compose up -d
```

That last command starts Postgres/OpenSearch/Ollama/Redis right here
(only needs doing once per reboot). Then start your own app in one
terminal:

```bash
uv run uvicorn src.main:app --reload --port 8100
```

And in another terminal, run the Week 1 check:

```bash
uv run python scripts/week1_verify_infra.py
```

## What the script actually does

It's a plain top-to-bottom script, no framework of its own — read it,
it's not hiding anything:

1. Prints your Python version and checks it's 3.12+.
2. Opens a raw TCP socket to `localhost:5432` to confirm Postgres is
   listening (a "can I even connect" check, nothing fancier).
3. `GET`s OpenSearch's `/_cluster/health` and Ollama's `/api/version` —
   if either doesn't respond, the corresponding Docker service isn't up
   yet.
4. `GET`s Airflow's `/health` too — but this one's allowed to fail. It's
   only there if you've separately started Airflow from the course repo.
5. `GET`s `http://localhost:8100/api/v1/health` — this is the one that
   depends on *your* code. It only succeeds once `health_check()` in
   `src/routers/health.py` actually returns something.

After that, it moves on to the hands-on exploration section, which
calls the four functions in `src/services/exploration.py` in order
(pull a model → generate from it → list Postgres tables → check
OpenSearch health) and stops at the first one you haven't implemented
yet, same as every other week's script.

## Success criteria

- [ ] `docker compose up -d` services all show healthy
- [ ] `uv run uvicorn src.main:app --reload --port 8100` starts without errors
- [ ] `scripts/week1_verify_infra.py` prints `[OK]` for every connectivity line
- [ ] `llama3.2:1b` is pulled and responds to a test prompt
- [ ] You can see what tables exist in Postgres (even if the answer is "none yet")
- [ ] OpenSearch reports cluster status `green` or `yellow`

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week1/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week1/week1_setup.ipynb`
- Blog post: [The Infrastructure That Powers RAG Systems](https://jamwithai.substack.com/p/the-infrastructure-that-powers-rag)

Next: [Week 2 — Data Ingestion Pipeline](week2.md)
