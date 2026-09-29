"""
Week 1 — infrastructure verification.

Read docs/week1.md first. This is the notebook replacement for
notebooks/week1/week1_setup.ipynb — a plain script, already complete
(nothing to implement here; it's your checking harness). Run it any time
to confirm the local infra (`docker compose up -d`, right here in this
project) is reachable, and that your own FastAPI app boots.

    uv run python scripts/week1_verify_infra.py
"""

import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

CHECK_TIMEOUT = 5


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

    print("\n-- Course-repo-only, optional (not part of this project's compose) --")
    check_http("Airflow", "http://localhost:8080/health")
    print(
        "      Airflow only matters if you're trying the optional "
        "examples/weather_etl_demo Airflow step — start it from "
        "../production-agentic-rag-course instead of here."
    )

    print("\n-- Your own app --")
    check_own_app()

    print(
        "\nIf anything in the first section failed: run `docker compose up -d` "
        "in this project's root, wait a minute or two, and re-run this script."
    )


if __name__ == "__main__":
    main()
