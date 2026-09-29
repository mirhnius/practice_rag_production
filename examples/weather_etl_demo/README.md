# Weather ETL demo (side reference, not part of the curriculum)

Built from the same pattern as
[krishnaik06/ETLWeather](https://github.com/krishnaik06/ETLWeather) —
an Airflow DAG that extracts weather from a public API, transforms it,
and loads it into Postgres. This folder exists purely to make the
Postgres ↔ Airflow ↔ FastAPI connection concrete with something you can
run in two minutes, fully separate from Week 2's real (and more
involved) arXiv pipeline. It doesn't touch anything in `src/`, and it
runs its **own** Postgres — you don't need the course's Docker infra up
at all for steps 1-2 below.

## The four files

| File | Role | Needs |
|---|---|---|
| `docker-compose.yml` | This demo's own tiny Postgres | nothing — just Docker |
| `pipeline.py` | Extract → Transform → Load, as one plain script | the Postgres above |
| `api.py` | Reads back the latest row over HTTP | the Postgres above |
| `dag_weather_etl.py` | The *same* extract/transform/load, wrapped so Airflow runs it on a schedule — written in the real course's `PythonOperator` + `>>` style, not the tutorial's `@task()` style | the course's Airflow (optional — see step 3) |
| Adminer (web UI, started by the same compose file) | Browse the `weather_data` table visually, like the video does | the Postgres above |

## 0. Start this demo's own Postgres (+ a table-browser UI)

```bash
cd examples/weather_etl_demo
docker compose up -d
```

That's two completely separate containers — `weather-demo-postgres`
(port `5434`) and `weather-demo-adminer` (port `8090`, a lightweight
web UI for browsing tables) — from the course's own Postgres (`5432`)
and Langfuse's Postgres (`5433`). All three can run at once without
conflicting.

**To see the table in a UI** (this is the "look at the data" part):
open `http://localhost:8090`, and log in with:
- System: `PostgreSQL`
- Server: `postgres`
- Username: `weather_user`
- Password: `weather_password`
- Database: `weather_db`

Then click into the `weather_data` table — same idea as pgAdmin/DBeaver,
just zero-install since it's already running as a container.

## 1. Run the pipeline directly — no Airflow needed

```bash
uv run python examples/weather_etl_demo/pipeline.py
```

You'll see `EXTRACT... / TRANSFORM... / LOAD...` printed, then a row in
Postgres. Check it:

```bash
docker exec -it weather-demo-postgres psql -U weather_user -d weather_db \
  -c "SELECT * FROM weather_data ORDER BY recorded_at DESC LIMIT 5;"
```

Run it again — you'll get a second row. This script *is* the pipeline;
everything else in this folder is just a different way of triggering the
same three functions.

## 2. Read it back through FastAPI

```bash
uv run uvicorn api:app --app-dir examples/weather_etl_demo --reload --port 8200
```

Then in another terminal:

```bash
curl http://localhost:8200/weather/latest
```

You should get back the exact row `pipeline.py` just inserted. This is
the whole lesson: **FastAPI didn't create that data — it's just reading
what's already sitting in Postgres.**

## 3. (Optional) See it run under real Airflow

This step is different from steps 1-2: it uses the **course's** Airflow
and the **course's** Postgres, not this folder's standalone one —
explained below. `pipeline.py` already proves the ETL logic works, so
treat this as "bonus: watch a scheduler run it," not a requirement.

```bash
cp examples/weather_etl_demo/dag_weather_etl.py \
  ../production-agentic-rag-course/airflow/dags/
```

Open `http://localhost:8080` (user `admin`, password in
`../production-agentic-rag-course/airflow/simple_auth_manager_passwords.json.generated`),
find `weather_etl_demo` in the DAG list, un-pause it, and hit the
trigger (▶) button.

**How it's structured, matching the real DAG:** open
`dag_weather_etl.py` next to
`../production-agentic-rag-course/airflow/dags/arxiv_paper_ingestion.py`
— same pieces, same order:

| Real course DAG | This demo | Purpose |
|---|---|---|
| `default_args` (owner, retries=2, retry_delay=30min, catchup) | same fields, retry_delay=5min | retry policy every task inherits |
| `schedule="0 6 * * 1-5"` (weekdays, 6am) | `schedule="0 */6 * * *"` (every 6 hours) | real cron, not the `@daily` shorthand |
| `catchup=False`, `max_active_runs=1` | identical | don't backfill missed runs; never overlap runs |
| `PythonOperator(task_id=..., python_callable=..., dag=dag)` ×5 | same, ×3 (extract/transform/load) | one task per pipeline step |
| `setup >> fetch >> index >> report >> cleanup` | `extract >> transform >> load` | explicit `>>` dependency chain |

One thing this demo shows that the real DAG's file doesn't: how tasks
actually hand data to each other. `dag_weather_etl.py` uses Airflow's
**XCom** (`context["ti"].xcom_push` / `.xcom_pull`) to pass the weather
dict from `extract` → `transform` → `load`. The real DAG doesn't do
this — each of its tasks independently reads/writes the shared Postgres
database instead, which is why its `PythonOperator` calls don't show any
data being threaded through them. XCom is worth seeing at least once
since it's the standard mechanism, but "communicate through the
database" is the pattern actually used at pipeline scale (XCom has a
size limit and isn't meant for large payloads like PDF text).

**Why it writes to a different database than steps 1-2:** the DAG runs
*inside* the course's Airflow container, which sits on the course's own
Docker network — it can only reach services on that same network (like
`postgres`, the course's Postgres). It has no route at all to this
folder's standalone `weather-demo-postgres`, which lives on its own,
separate network from a separate `docker compose up`. So the row this
step inserts lands in the course's `rag_db` (a new `weather_data` table
there, alongside `papers`), not in the `weather_db` from steps 1-2 —
querying `api.py` afterward won't show it. This is a genuine, common
Docker networking gotcha, not a mistake in the setup: every
`docker compose up` gets its own isolated network by default.

## What this proves about the architecture

```
   pipeline.py, run by hand              dag_weather_etl.py, run by Airflow
   OR curl → api.py                      on a timer ("0 */6 * * *")
              │                                     │
              ▼                                     ▼
   weather-demo-postgres (port 5434)      the course's rag-postgres (port 5432)
      — this demo's own DB, browsable        — reachable only from inside
        via Adminer at :8090                   the course's Docker network
```

Airflow and FastAPI never call each other, in either version. Airflow's
job is *writing* data unattended, on a schedule; FastAPI's job is
*reading* (or writing) data the moment someone asks, over HTTP. Swap
"weather" for "arXiv papers" and you have Week 2: `ArxivClient` +
`PDFParserService` + `PaperRepository` are `extract` / `transform` /
`load`, just with more steps in each one; the real
`airflow/dags/arxiv_paper_ingestion.py` is `dag_weather_etl.py`'s bigger
sibling; and `src/routers/papers.py` is `api.py`'s bigger sibling.
