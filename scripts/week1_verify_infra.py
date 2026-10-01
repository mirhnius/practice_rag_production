"""
Week 1 — infrastructure verification.

Read docs/week1.md first. The connectivity checks below are already
complete (nothing to implement there). The "hands-on exploration"
section at the end is different — it calls the functions you write in
src/services/exploration.py, so it will raise NotImplementedError until
you've filled those in. That's expected; the traceback tells you exactly
which function to go write next.

    uv run python scripts/week1_verify_infra.py
"""

import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.services.exploration import (  # noqa: E402
    generate_test_response,
    list_postgres_tables,
    opensearch_cluster_health,
    pull_ollama_model,
)

CHECK_TIMEOUT = 5
OLLAMA_HOST = "http://localhost:11434"
OPENSEARCH_HOST = "http://localhost:9200"
POSTGRES_URL = "postgresql://rag_user:rag_password@localhost:5432/rag_db"


def check_python_version() -> None:
    major, minor = sys.version_info.major, sys.version_info.minor
    status = "OK" if (major, minor) >= (3, 12) else "FAIL"
    print(f"[{status}] Python {major}.{minor}")


def check_tcp_port(name: str, host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=CHECK_TIMEOUT):
            print(f"[OK] {name} is accepting connections on {host}:{port}")
            return True
    except OSError as exc:
        print(f"[FAIL] {name} not reachable on {host}:{port} ({exc})")
        return False


def check_http(name: str, url: str) -> bool:
    try:
        response = requests.get(url, timeout=CHECK_TIMEOUT)
        if response.status_code == 200:
            print(f"[OK] {name} responded 200 at {url}")
            return True
        print(f"[WARN] {name} responded {response.status_code} at {url}")
        return False
    except requests.exceptions.RequestException as exc:
        print(f"[FAIL] {name} not reachable at {url} ({exc})")
        return False


def check_own_app() -> None:
    try:
        from src.config import get_settings

        port = get_settings().app_port
    except Exception as exc:  # noqa: BLE001 - this is a diagnostic script
        print(f"[FAIL] Could not import src.config.get_settings() ({exc})")
        return

    url = f"http://localhost:{port}/api/v1/health"
    ok = check_http("Your FastAPI app", url)
    if not ok:
        print(
            f"      Start it with: uv run uvicorn src.main:app --reload --port {port}"
        )


def main() -> None:
    print("=== Week 1: infrastructure check ===\n")
    check_python_version()

    print("\n-- Local infra (this project's own docker compose) --")
    check_tcp_port("PostgreSQL", "localhost", 5432)
    check_http("OpenSearch", "http://localhost:9200/_cluster/health")
    check_http("Ollama", "http://localhost:11434/api/version")
    airflow_ok = check_http("Airflow", "http://localhost:8080/health")
    if not airflow_ok:
        print(
            "      Airflow's image takes a few minutes to build on the first "
            "`docker compose up -d` — give it time, then re-run this script."
        )

    print("\n-- Your own app --")
    check_own_app()

    print(
        "\nIf anything in the first section failed: run `docker compose up -d` "
        "in this project's root, wait a minute or two, and re-run this script."
    )


def explore_services() -> None:
    """Hands-on exploration, mirroring the course notebook's Week 1 cells.

    Unlike everything above, this part calls your own code
    (src/services/exploration.py) and will raise NotImplementedError
    until you've written it.
    """
    print("\n" + "=" * 60)
    print("STEP 1 — pull an Ollama model (this can take a couple of minutes)")
    print("=" * 60)
    pull_ollama_model(OLLAMA_HOST, "llama3.2:1b")
    print("Pulled.")

    print()
    print("=" * 60)
    print("STEP 2 — generate one test response and see how long it takes")
    print("=" * 60)
    answer = generate_test_response(
        OLLAMA_HOST, "llama3.2:1b", "What is machine learning in one sentence?"
    )
    print(f"Response: {answer}")

    print()
    print("=" * 60)
    print("STEP 3 — list tables currently in Postgres")
    print("=" * 60)
    tables = list_postgres_tables(POSTGRES_URL)
    print(f"{len(tables)} table(s): {tables}" if tables else "No tables yet — expected before Week 2.")

    print()
    print("=" * 60)
    print("STEP 4 — check OpenSearch's cluster health")
    print("=" * 60)
    health = opensearch_cluster_health(OPENSEARCH_HOST)
    print(f"status: {health.get('status')}, nodes: {health.get('number_of_nodes')}")


if __name__ == "__main__":
    main()

    try:
        explore_services()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week1.md for the plan."
        )
