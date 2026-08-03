"""Workflows — Running a workflow: shared state, events, and streaming.

Building the graph is half of it. This is the other half:

  ctx.set_state / ctx.get_state   scratch space shared by every executor in a run
  await workflow.run(x)           WorkflowRunResult — outputs, intermediates, state
  workflow.run(x, stream=True)    the event timeline as it happens

Event types you will see, in order: started, superstep_started, executor_invoked,
executor_completed, output / intermediate, superstep_completed, status. Workflows
advance in supersteps — each superstep delivers one round of messages, which is
why parallel branches appear grouped rather than interleaved.

Run:  uv run python examples/14_workflow_execution.py      (no model needed)
"""

import asyncio

from agent_framework import WorkflowBuilder, WorkflowContext, executor
from typing_extensions import Never


@executor(id="parse")
async def parse(raw: str, ctx: WorkflowContext[list[str], str]) -> None:
    """Sends list[str] downstream and yields a str as an intermediate output."""
    items = [part.strip() for part in raw.split(",") if part.strip()]
    # Shared state is visible to every executor in this run.
    ctx.set_state("raw_input", raw)
    ctx.set_state("item_count", len(items))
    await ctx.yield_output(f"parsed {len(items)} items")
    await ctx.send_message(items)


@executor(id="price")
async def price(items: list[str], ctx: WorkflowContext[dict[str, int], str]) -> None:
    prices = {item: len(item) * 10 for item in items}
    ctx.set_state("subtotal", sum(prices.values()))
    await ctx.yield_output(f"priced {len(prices)} items")
    await ctx.send_message(prices)


@executor(id="invoice")
async def invoice(prices: dict[str, int], ctx: WorkflowContext[Never, str]) -> None:
    """Reads state written by upstream executors — no need to thread it through."""
    count = ctx.get_state("item_count")
    subtotal = ctx.get_state("subtotal")
    raw = ctx.get_state("raw_input")
    lines = ", ".join(f"{k}={v}" for k, v in prices.items())
    await ctx.yield_output(
        f"invoice for {count} items from {raw!r}: {lines} — subtotal {subtotal}"
    )


def build():
    return (
        WorkflowBuilder(
            start_executor=parse,
            output_from=[invoice],                  # the terminal answer
            intermediate_output_from=[parse, price],  # progress, not the answer
        )
        .add_chain([parse, price, invoice])
        .build()
    )


async def non_streaming(workflow) -> None:
    print("=" * 72)
    print("1. await workflow.run(...) — everything at once")
    result = await workflow.run("keyboard, mouse, monitor")
    print(f"   outputs       {result.get_outputs()}")
    print(f"   intermediate  {result.get_intermediate_outputs()}")
    print(f"   final state   {result.get_final_state()}")


async def streaming(workflow) -> None:
    print("\n" + "=" * 72)
    print("2. workflow.run(..., stream=True) — the event timeline")

    stream = workflow.run("laptop, dock", stream=True)
    superstep = 0
    async for event in stream:
        if event.type == "superstep_started":
            superstep += 1
            print(f"   -- superstep {superstep}")
            continue
        if event.type in {"started", "status", "superstep_completed"}:
            continue
        who = getattr(event, "executor_id", None) or "-"
        detail = str(event.data)
        if len(detail) > 44:
            detail = detail[:41] + "..."
        print(f"      {event.type:19} {who:8} {detail}")

    # The stream still gives you the aggregated result afterwards.
    result = await stream.get_final_response()
    print(f"   outputs: {result.get_outputs()}")


async def state_is_per_run(workflow) -> None:
    print("\n" + "=" * 72)
    print("3. shared state is scoped to one run, not to the workflow object")
    first = await workflow.run("pen")
    second = await workflow.run("pen, paper, ink")
    print(f"   run A -> {first.get_outputs()[0]}")
    print(f"   run B -> {second.get_outputs()[0]}")
    print("   Run B did not inherit run A's item_count — state does not leak across runs.")


async def main() -> None:
    workflow = build()
    await non_streaming(workflow)
    await streaming(workflow)
    await state_is_per_run(workflow)
    print(
        "\nUse shared state for facts several executors need; use messages for the\n"
        "thing you are actually passing along. Stream when a human is waiting."
    )


if __name__ == "__main__":
    asyncio.run(main())
