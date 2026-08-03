"""Exercise 05 — Route a ticket.  (module 6 · pairs with examples/13_edge_patterns.py)

Build the routing half of a support triage workflow. Four severities go in,
four different handlers must fire — and anything unrecognised must still land
somewhere rather than vanishing.

YOUR JOB
  TODO 1  wire `triage` to the three handlers with a switch-case edge group
  TODO 2  make sure an unknown severity still reaches `backlog`

Use Case(condition=..., target=...) and Default(target=...).
Ask yourself why switch-case is the right primitive here rather than three
conditional add_edge calls.

No model needed.
Run:  uv run python exercises/05_routing.py
"""

import asyncio

from agent_framework import (
    Case,  # noqa: F401
    Default,  # noqa: F401
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from typing_extensions import Never

from _check import check, note, report


@executor(id="triage")
async def triage(severity: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(severity.strip().lower())


@executor(id="pager")
async def pager(sev: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(f"{sev}: paged the on-call engineer")


@executor(id="queue")
async def queue(sev: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(f"{sev}: queued for this sprint")


@executor(id="backlog")
async def backlog(sev: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(f"{sev}: parked in the backlog")


def build():
    builder = WorkflowBuilder(start_executor=triage)
    # TODO 1 + 2: add a switch-case edge group so that
    #   "sev1"        -> pager
    #   "sev2"        -> queue
    #   anything else -> backlog
    return builder.build()


async def main() -> None:
    print(__doc__.splitlines()[0])
    try:
        workflow = build()
    except Exception as exc:
        check("workflow builds", False, f"{type(exc).__name__}: {exc}")
        report()
        return
    check("workflow builds", True)

    expected = {
        "sev1": "paged the on-call engineer",
        "sev2": "queued for this sprint",
        "sev3": "parked in the backlog",
        "wishlist": "parked in the backlog",  # never seen before — must not vanish
    }
    for severity, want in expected.items():
        outputs = (await workflow.run(severity)).get_outputs()
        note(f"{severity:9} -> {outputs}")
        check(
            f"{severity} routed correctly",
            len(outputs) == 1 and want in outputs[0],
            f"expected one output containing {want!r}, got {outputs!r}",
        )
    report()


if __name__ == "__main__":
    asyncio.run(main())
