"""Tiny self-check helper shared by the exercises.

Each exercise ends with a handful of `check(...)` calls and one `report()`.
Run the file, read the FAILs, edit the TODOs, run again. `report()` exits
non-zero while anything is still failing, so these also work in CI.
"""

from __future__ import annotations

import sys

_results: list[tuple[str, bool]] = []


def check(label: str, ok: bool, hint: str = "") -> bool:
    """Record one assertion. Never raises — you always see the whole list."""
    _results.append((label, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok and hint:
        print(f"         hint: {hint}")
    return bool(ok)


def note(message: str) -> None:
    """Print an observation that is not pass/fail (model output, timings, …)."""
    print(f"  [note] {message}")


def report() -> None:
    passed = sum(1 for _, ok in _results if ok)
    total = len(_results)
    print(f"\n{passed}/{total} checks passed")
    if passed != total:
        print("Not done yet — fix the TODOs above and run it again.")
        sys.exit(1)
    print("All checks passed. Compare with exercises/solutions/ when you're curious.")
