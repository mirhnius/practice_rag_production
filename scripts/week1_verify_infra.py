"""
Week 1 — infrastructure verification.

The notebook replacement for `notebooks/week1/week1_setup.ipynb`. This
script is already complete — it's your checking harness, not something to
implement. Run it any time to confirm the shared infra (started from the
course repo's `docker compose up -d`) is reachable, and that your own
FastAPI app boots.

    uv run python scripts/week1_verify_infra.py
"""

import socket
import sys

import requests

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

    print("\n-- Shared infra (from the course repo's docker compose) --")
    check_tcp_port("PostgreSQL", "localhost", 5432)
    check_http("OpenSearch", "http://localhost:9200/_cluster/health")
    check_http("Ollama", "http://localhost:11434/api/version")
    check_http("Airflow (optional)", "http://localhost:8080/health")

    print("\n-- Your own app --")
    check_own_app()

    print(
        "\nIf anything failed above: start the shared infra with "
        "`docker compose up -d` from the course repo, wait a minute or two, "
        "and re-run this script."
    )


if __name__ == "__main__":
    main()
