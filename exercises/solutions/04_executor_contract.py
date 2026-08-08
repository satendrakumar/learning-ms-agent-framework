"""SOLUTION — 04 — Fix the executor contracts.  (module 6 · pairs with examples/12_executor_types.py)  (worked answer)

This workflow does not build. The logic is fine; the WorkflowContext type
parameters lie about what each node does, and the builder validates them.

Reminder:
    WorkflowContext              sends nothing, yields nothing
    WorkflowContext[T]           sends T downstream
    WorkflowContext[Never, U]    yields U as a workflow output
    WorkflowContext[T, U]        sends T downstream AND yields U

YOUR JOB
  TODO 1  `split` sends a list[str] and yields a progress string
  TODO 2  `measure` sends a dict and yields a progress string
  TODO 3  `summarise` only yields the final answer
  Fix the three annotations. Do not change the bodies.

No model needed.
Run:  uv run python exercises/04_executor_contract.py
"""

import asyncio

from agent_framework import WorkflowBuilder, WorkflowContext, executor
from typing_extensions import Never  # noqa: F401  (you will need this)

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from _check import check, note, report


@executor(id="split")
async def split(raw: str, ctx: WorkflowContext[list[str], str]) -> None:  # sends, yields
    words = [w for w in raw.split() if w]
    await ctx.yield_output(f"split into {len(words)} words")
    await ctx.send_message(words)


@executor(id="measure")
async def measure(words: list[str], ctx: WorkflowContext[dict[str, int], str]) -> None:
    lengths = {w: len(w) for w in words}
    await ctx.yield_output(f"measured {len(lengths)} words")
    await ctx.send_message(lengths)


@executor(id="summarise")
async def summarise(lengths: dict[str, int], ctx: WorkflowContext[Never, str]) -> None:
    longest = max(lengths, key=lambda w: lengths[w])
    await ctx.yield_output(f"longest word is {longest!r} ({lengths[longest]} chars)")


def build():
    return (
        WorkflowBuilder(
            start_executor=split,
            output_from=[summarise],
            intermediate_output_from=[split, measure],
        )
        .add_chain([split, measure, summarise])
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
    result = await workflow.run("the quick brown elephant jumped")
    outputs = result.get_outputs()
    intermediates = result.get_intermediate_outputs()
    note(f"outputs={outputs}")
    note(f"intermediate={intermediates}")

    check(
        "exactly one terminal output, from summarise",
        len(outputs) == 1 and "elephant" in outputs[0],
        f"got {outputs!r}",
    )
    check(
        "both progress lines came through as intermediate",
        len(intermediates) == 2,
        f"got {intermediates!r} — split and measure should each yield one",
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
