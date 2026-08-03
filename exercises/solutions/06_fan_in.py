"""SOLUTION — 06 — Fan out, then merge.  (module 6 · pairs with examples/13_edge_patterns.py)  (worked answer)

Three independent checks should run on the same document in parallel, then one
node combines their verdicts into a single report.

YOUR JOB
  TODO 1  fan `intake` out to all three checkers
  TODO 2  fan the three checkers in to `report_card`
  TODO 3  give `report_card` the right signature — a fan-in target does NOT
          receive three separate messages

That third TODO is the one that catches people. Read the type error carefully
if you get one.

No model needed.
Run:  uv run python exercises/06_fan_in.py
"""

import asyncio

from agent_framework import WorkflowBuilder, WorkflowContext, executor
from typing_extensions import Never

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from _check import check, note, report

DOC = "Payments API returned HTTP 500 on checkout. TODO: add retry."


@executor(id="intake")
async def intake(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text)


@executor(id="length_check")
async def length_check(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(f"length={len(text)}")


@executor(id="todo_check")
async def todo_check(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(f"has_todo={'TODO' in text}")


@executor(id="error_check")
async def error_check(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(f"mentions_500={'500' in text}")


# A fan-in target receives the collected results as a list, not one at a time.
@executor(id="report_card")
async def report_card(verdicts: list[str], ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(" | ".join(sorted(verdicts)))


def build():
    checkers = [length_check, todo_check, error_check]
    return (
        WorkflowBuilder(start_executor=intake)
        .add_fan_out_edges(intake, checkers)
        .add_fan_in_edges(checkers, report_card)
        .build()
    )


async def main() -> None:
    print(__doc__.splitlines()[0])
    try:
        workflow = build()
    except Exception as exc:
        check("workflow builds", False, f"{type(exc).__name__}: {exc}")
        report()
        return
    check("workflow builds", True)

    try:
        result = await workflow.run(DOC)
    except Exception as exc:
        check("workflow runs", False, f"{type(exc).__name__}: {exc}")
        report()
        return
    check("workflow runs", True)

    outputs = result.get_outputs()
    note(f"outputs={outputs}")
    check("exactly one merged report", len(outputs) == 1, f"got {len(outputs)} outputs")
    merged = outputs[0] if outputs else ""
    for fragment in (f"length={len(DOC)}", "has_todo=True", "mentions_500=True"):
        check(f"report includes {fragment}", fragment in merged, f"merged report was {merged!r}")
    check(
        "the three verdicts were merged, not concatenated character by character",
        merged.count("|") == 2,
        f"got {merged!r} — if this looks shredded, TODO 3 is still open",
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
