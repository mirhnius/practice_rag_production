"""
Standalone ETL example — NOT part of the Week 1-7 curriculum, just a
side reference for understanding how the pieces connect. Same
Extract/Transform/Load shape as the reference repo this was built from
(github.com/krishnaik06/ETLWeather), simplified to run with zero setup:
no API key, no Airflow install needed for this file.

Needs this folder's own Postgres running first (its own docker-compose.yml,
separate from the course's — nothing else required):
    cd examples/weather_etl_demo && docker compose up -d

Then run it directly from the project root:
    uv run python examples/weather_etl_demo/pipeline.py
"""

import psycopg2
import requests

LATITUDE = "51.5074"  # London
LONGITUDE = "-0.1278"

PG_CONFIG = {
    "host": "localhost",
    "port": 5434,  # this demo's own Postgres (see docker-compose.yml) — not the course's 5432 or its Langfuse Postgres's 5433
    "dbname": "weather_db",
    "user": "weather_user",
    "password": "weather_password",
}


def extract_weather_data() -> dict:
    """EXTRACT: pull current weather from the free, keyless Open-Meteo API."""
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": LATITUDE, "longitude": LONGITUDE, "current_weather": True},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def transform_weather_data(raw: dict) -> dict:
    """TRANSFORM: pull just the fields we care about out of the API's response shape."""
    current = raw["current_weather"]
    return {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "temperature": current["temperature"],
        "windspeed": current["windspeed"],
        "winddirection": current["winddirection"],
        "weathercode": current["weathercode"],
    }


def load_weather_data(data: dict) -> None:
    """LOAD: write it into Postgres — same table every run, one new row per run."""
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


if __name__ == "__main__":
    print("EXTRACT...")
    raw = extract_weather_data()
    print(f"  got: {raw['current_weather']}")

    print("TRANSFORM...")
    clean = transform_weather_data(raw)
    print(f"  clean record: {clean}")

    print("LOAD...")
    load_weather_data(clean)
    print("  inserted into weather_data")

    print("\nDone. Check it: docker exec -it weather-demo-postgres psql -U weather_user -d weather_db "
          "-c 'SELECT * FROM weather_data ORDER BY recorded_at DESC LIMIT 5;'")
