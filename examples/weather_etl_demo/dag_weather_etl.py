"""
Airflow DAG, written to match the REAL course's authoring style — not
the TaskFlow-decorator style the original reference repo used
(github.com/krishnaik06/ETLWeather). Open this side by side with the
real one and compare:
    ../production-agentic-rag-course/airflow/dags/arxiv_paper_ingestion.py
Same shape: PythonOperator tasks + explicit `>>` dependencies + a full
default_args block with a real retry/catchup policy + a real cron
schedule. Just 3 tasks instead of the real DAG's 5, and everything in
one file instead of a separate arxiv_ingestion/ package, to keep this
demo readable in one sitting.

To actually run this under Airflow (optional — pipeline.py already
proves the ETL logic works without Airflow at all):
    cp examples/weather_etl_demo/dag_weather_etl.py \
        ../production-agentic-rag-course/airflow/dags/
Then open http://localhost:8080, find "weather_etl_demo", un-pause it,
and trigger it (▶) — or just leave it and let the schedule fire it.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

LATITUDE = "51.5074"  # London
LONGITUDE = "-0.1278"

# This writes to the COURSE's shared Postgres, not this folder's
# standalone one (docker-compose.yml) that pipeline.py/api.py use — a
# container can only reach services on its own docker-compose network,
# and this DAG runs inside the course's Airflow container, on the
# course's network. It can see "postgres" (the course's service name)
# but has no route to weather-demo-postgres at all.
PG_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "rag_db",
    "user": "rag_user",
    "password": "rag_password",
}


def extract_weather_data(**context) -> None:
    """EXTRACT — same job as pipeline.py's extract_weather_data(), but as
    a PythonOperator task. Airflow 2.x auto-injects `context` (the
    `**context` here) into any PythonOperator callable, and `context["ti"]`
    ("task instance") is how tasks hand data to each other: this pushes
    its result instead of returning it directly.

    Worth knowing: the real course DAG's tasks don't pass data this way
    at all — each one reads/writes the shared Postgres database itself
    rather than handing Python objects to the next task (fetch stores to
    Postgres; the indexing task then reads from Postgres). XCom (what
    this is called) is shown here because it's the standard mechanism
    worth seeing explicitly at least once, not because the real DAG uses it.
    """
    import requests

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": LATITUDE, "longitude": LONGITUDE, "current_weather": True},
        timeout=10,
    )
    response.raise_for_status()
    context["ti"].xcom_push(key="raw_weather", value=response.json())


def transform_weather_data(**context) -> None:
    """TRANSFORM — pulls extract's output back out of XCom."""
    raw = context["ti"].xcom_pull(key="raw_weather", task_ids="extract_weather_data")
    current = raw["current_weather"]
    clean = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "temperature": current["temperature"],
        "windspeed": current["windspeed"],
        "winddirection": current["winddirection"],
        "weathercode": current["weathercode"],
    }
    context["ti"].xcom_push(key="clean_weather", value=clean)


def load_weather_data(**context) -> None:
    """LOAD — pulls transform's output, writes it into Postgres."""
    import psycopg2

    data = context["ti"].xcom_pull(key="clean_weather", task_ids="transform_weather_data")

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            latitude FLOAT,
            longitude FLOAT,
            temperature FLOAT,
            windspeed FLOAT,
            winddirection FLOAT,
            weathercode INT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        INSERT INTO weather_data
            (latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES
            (%(latitude)s, %(longitude)s, %(temperature)s, %(windspeed)s, %(winddirection)s, %(weathercode)s);
        """,
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


# Same fields, same shape as the real course DAG's default_args — every
# task in the pipeline inherits these unless it overrides them itself.
default_args = {
    "owner": "weather-demo",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,  # same as the real DAG: retry a failed task twice before giving up
    "retry_delay": timedelta(minutes=5),  # real DAG waits 30 min — arXiv + PDF parsing is slow and rate-limited; 5 min is plenty for one free weather API call
    "catchup": False,  # harmless here (Airflow ignores it as a task-level default) — the DAG()-level catchup below is the one that actually does something; the real course file sets it in both places too
}

dag = DAG(
    "weather_etl_demo",
    default_args=default_args,
    description="Demo ETL: fetch current weather -> transform -> store in Postgres",
    schedule="0 */6 * * *",  # every 6 hours, on the hour. Same cron syntax as the real DAG's "0 6 * * 1-5" (weekdays at 6am) — 5 fields: minute hour day-of-month month day-of-week. */6 means "every 6th hour."
    max_active_runs=1,  # same as the real DAG: never let two runs overlap
    catchup=False,  # the one that matters: don't backfill a run for every missed 6-hour slot since start_date
    tags=["demo"],
)

extract_task = PythonOperator(
    task_id="extract_weather_data",
    python_callable=extract_weather_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_weather_data",
    python_callable=transform_weather_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_weather_data",
    python_callable=load_weather_data,
    dag=dag,
)

# Task dependencies — same `>>` syntax as the real DAG's five-task chain
# (setup_task >> fetch_task >> index_hybrid_task >> report_task >> cleanup_task):
extract_task >> transform_task >> load_task
