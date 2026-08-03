"""Run every exercise and summarise which ones still have work left.

  uv run python exercises/run_all.py              # your work
  uv run python exercises/run_all.py --solutions  # check the worked answers pass
  uv run python exercises/run_all.py --offline    # skip the three that need a model
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
NEEDS_MODEL = {"02_context_provider", "07_guardrail_middleware", "08_structured_output"}


def main() -> int:
    solutions = "--solutions" in sys.argv
    offline = "--offline" in sys.argv
    folder = HERE / "solutions" if solutions else HERE

    files = sorted(f for f in folder.glob("[0-9][0-9]_*.py"))
    if not files:
        print(f"no exercises found in {folder}")
        return 1

    print(f"Running {len(files)} {'solutions' if solutions else 'exercises'}"
          f"{' (offline only)' if offline else ''}\n")
    failed: list[str] = []
    skipped: list[str] = []

    for f in files:
        name = f.stem
        if offline and name in NEEDS_MODEL:
            skipped.append(name)
            print(f"  {name:28} skipped (needs a model)")
            continue
        proc = subprocess.run([sys.executable, str(f)], capture_output=True, text=True)
        tally = re.search(r"(\d+/\d+) checks passed", proc.stdout)
        score = tally.group(1) if tally else "?"
        if proc.returncode == 0:
            print(f"  {name:28} done      {score}")
        else:
            failed.append(name)
            print(f"  {name:28} todo      {score}")

    done = len(files) - len(failed) - len(skipped)
    print(f"\n{done} complete, {len(failed)} to go"
          + (f", {len(skipped)} skipped" if skipped else ""))
    if failed:
        print("Next up: " + failed[0])
        print(f"  uv run python {folder.name}/{failed[0]}.py")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
