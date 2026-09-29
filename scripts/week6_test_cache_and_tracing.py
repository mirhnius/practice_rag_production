"""
Week 6 — caching + observability.

Notebook replacement for `notebooks/week6/week6_cache_testing.ipynb`.
Sends the same query to your /api/v1/ask endpoint twice and times both
calls — the second should be dramatically faster once RedisCache is
wired into src/routers/ask.py.

    uv run python scripts/week6_test_cache_and_tracing.py

Needs Redis running and your own app running:
    uv run uvicorn src.main:app --reload --port 8100
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from scripts._util import run_step  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.services.cache.redis_cache import RedisCache  # noqa: E402


def _roundtrip(cache: RedisCache):
    cache.set("test query", {"answer": "42"}, top_k=3)
    return cache.get("test query", top_k=3)


def main() -> None:
    print("=== Week 6: caching + tracing ===")
    settings = get_settings()

    cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_ttl_hours)
    run_step(
        "Write + read back a test cache entry",
        "src/services/cache/redis_cache.py (get/set)",
        lambda: _roundtrip(cache),
    )

    port = settings.app_port
    payload = {"query": "What are transformers?", "top_k": 3}
    url = f"http://localhost:{port}/api/v1/ask"

    try:
        t0 = time.monotonic()
        first = requests.post(url, json=payload, timeout=60)
        first_elapsed = time.monotonic() - t0

        t0 = time.monotonic()
        second = requests.post(url, json=payload, timeout=60)
        second_elapsed = time.monotonic() - t0

        print(f"\nFirst call:  {first.status_code} in {first_elapsed:.2f}s (expect a cache MISS)")
        print(f"Second call: {second.status_code} in {second_elapsed:.2f}s (expect a cache HIT, much faster)")
        if second_elapsed < first_elapsed / 2:
            print("[OK] Second call was meaningfully faster — caching looks wired up.")
        else:
            print("[TODO] No speedup yet — wire RedisCache into src/routers/ask.py.")
    except requests.exceptions.RequestException:
        print(
            f"\n[SKIP] Your app isn't running on port {port}. Start it with "
            f"`uv run uvicorn src.main:app --reload --port {port}` and re-run this script."
        )

    if settings.langfuse_enabled:
        print(f"\nCheck {settings.langfuse_host} for traces of the calls above.")
    else:
        print("\nLANGFUSE_ENABLED is false in .env — set it (plus your keys) to see traces.")


if __name__ == "__main__":
    main()
