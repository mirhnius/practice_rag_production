"""
Standalone example — reads back whatever pipeline.py (or the Airflow DAG
version of it) wrote into Postgres. This is the other half of the loop:
Airflow/the pipeline script WRITES data on its own schedule, FastAPI
READS it out whenever an HTTP request asks for it. Neither one knows the
other exists — they only share the database.

    uv run uvicorn api:app --app-dir examples/weather_etl_demo --reload --port 8200

Then: curl http://localhost:8200/weather/latest

Needs this folder's own Postgres running (cd examples/weather_etl_demo
&& docker compose up -d) and at least one row from pipeline.py.
"""

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException

app = FastAPI()

PG_CONFIG = {
    "host": "localhost",
    "port": 5434,  # this demo's own Postgres (see docker-compose.yml) — not the course's 5432 or its Langfuse Postgres's 5433
    "dbname": "weather_db",
    "user": "weather_user",
    "password": "weather_password",
}


@app.get("/weather/latest")
def latest_weather() -> dict:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM weather_data ORDER BY recorded_at DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise HTTPException(404, "No weather data yet — run pipeline.py first.")
    return dict(row)
