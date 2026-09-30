"""
Week 1 — hands-on service exploration.

The course's own Week 1 notebook spends most of its time not on code,
but on manually poking each service: pulling an Ollama model and
generating from it, checking what tables exist in Postgres, checking
OpenSearch's cluster health. That's genuinely worth doing — it's how
you build confidence that each dependency actually works before you
start writing the real pipeline against it.

This module is that, as code instead of notebook cells / clicking
through a UI. It's deliberately NOT the polished client you'll build in
later weeks (OllamaClient in Week 5, OpenSearchClient in Week 3) — just
raw, throwaway calls, the same way the notebook did it. Don't worry
about elegance here; the point is seeing each service respond.
"""

import psycopg2
import requests


def pull_ollama_model(host: str, model: str) -> None:
    """Pull an Ollama model, so Week 5 has something to generate with.

    TODO:
    - POST to f"{host}/api/pull" with json={"name": model, "stream": False}
    - This can take a couple of minutes the first time (the model is a
      few GB) — use a generous timeout (e.g. timeout=600)
    - response.raise_for_status() and print something so you know it worked
    - Reference: https://github.com/ollama/ollama/blob/main/docs/api.md#pull-a-model
    """
    raise NotImplementedError


def generate_test_response(host: str, model: str, prompt: str) -> str:
    """A rough one-off generation call — this is what you'll formalize
    into OllamaClient.generate() in Week 5, but for now just prove the
    model can actually respond.

    TODO:
    - POST to f"{host}/api/generate" with
      json={"model": model, "prompt": prompt, "stream": False}
    - return response.json()["response"]
    - print how long it took (time.monotonic() before/after) — the
      notebook specifically calls this out, since a model that "works"
      but takes 90 seconds for one sentence is a real problem you want
      to know about now, not while debugging Week 5's RAG pipeline
    """
    raise NotImplementedError


def list_postgres_tables(database_url: str) -> list[str]:
    """What tables already exist in the database right now?

    Right now the honest answer should be "none, or just Postgres's own
    internal ones" — that's fine, this function's job is just to prove
    you can connect and query, before Week 2 gives you something real
    to look at.

    TODO:
    - psycopg2.connect(database_url) (psycopg2 accepts a full DSN/URL
      string directly, no need to parse it apart yourself)
    - cursor.execute("SELECT table_name FROM information_schema.tables "
      "WHERE table_schema = 'public' ORDER BY table_name;")
    - return [row[0] for row in cursor.fetchall()]
    - remember to close the cursor and connection
    """
    raise NotImplementedError


def opensearch_cluster_health(host: str) -> dict:
    """The programmatic version of opening OpenSearch Dashboards and
    checking cluster health by hand.

    TODO:
    - response = requests.get(f"{host}/_cluster/health", timeout=10)
    - response.raise_for_status()
    - return response.json()
    - the "status" field ("green"/"yellow"/"red") is the headline number;
      print it specifically, not just the whole dict
    """
    raise NotImplementedError
