"""
Shared helper for the week2+ scripts.

Turns a `NotImplementedError` from one of your still-unfinished src/
functions into a friendly pointer instead of a raw traceback, so each
script doubles as a running checklist of what to implement next.
"""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def run_step(description: str, hint_file: str, fn: Callable[[], T]) -> T | None:
    print(f"\n--- {description} ---")
    try:
        result = fn()
        print(f"[OK] {description}")
        return result
    except NotImplementedError:
        print(f"[TODO] Not implemented yet — see {hint_file}")
        return None
    except Exception as exc:  # noqa: BLE001 - surfacing the real error is the point
        print(f"[FAIL] {description}: {type(exc).__name__}: {exc}")
        return None
