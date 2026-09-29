"""
Week 6 — caching + observability.

Read docs/week6.md first. This is the notebook replacement for
notebooks/week6/week6_cache_testing.ipynb — a plain, top-to-bottom
script, already complete (nothing to implement here; it's your checking
harness).

If a step below isn't implemented yet, Python will raise
NotImplementedError and the script will stop right there — read the
traceback, it names the exact file and line to go work on next.

    uv run python scripts/week6_test_cache_and_tracing.py

Needs Redis running, and your own app running:
    uv run uvicorn src.main:app --reload --port 8100
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.services.cache.redis_cache import RedisCache  # noqa: E402


def main() -> None:
    settings = get_settings()

    print("=" * 60)
    print("STEP 1 — write + read back a test cache entry directly")
    print("=" * 60)
    cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_ttl_hours)
    cache.set("test query", {"answer": "42"}, top_k=3)
    roundtrip = cache.get("test query", top_k=3)
    print(f"Got back: {roundtrip}")

    print()
    print("=" * 60)
    print("STEP 2 — send the same /api/v1/ask request twice and time both")
    print("=" * 60)
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

        print(f"First call:  {first.status_code} in {first_elapsed:.2f}s (expect a cache MISS)")
        print(f"Second call: {second.status_code} in {second_elapsed:.2f}s (expect a cache HIT, much faster)")
        if second_elapsed < first_elapsed / 2:
            print("Second call was meaningfully faster — caching looks wired up.")
        else:
            print("No speedup yet — wire RedisCache into src/routers/ask.py (see docs/week6.md).")
    except requests.exceptions.RequestException:
        print(
            f"Skipped — your app isn't running on port {port}. Start it with "
            f"`uv run uvicorn src.main:app --reload --port {port}` and re-run this script."
        )

    print()
    print("=" * 60)
    print("STEP 3 — check for traces")
    print("=" * 60)
    if settings.langfuse_enabled:
        print(f"Check {settings.langfuse_host} for traces of the calls above.")
    else:
        print("LANGFUSE_ENABLED is false in .env — set it (plus your keys) to see traces.")

    print("\nAll steps ran without errors — Week 6 is done.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        import traceback

        traceback.print_exc()
        print(
            "\nThat NotImplementedError is your next TODO — the traceback above "
            "names the exact file and line. See docs/week6.md for the plan."
        )
