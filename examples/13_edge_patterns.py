"""Workflows — Edges: the six ways WorkflowBuilder wires nodes together.

Executors are the nodes; edges decide what runs next. WorkflowBuilder gives you
five wiring primitives, and picking the right one is most of graph design:

  add_chain(...)                   A -> B -> C, the common case
  add_edge(a, b, condition=...)    take this edge only if a predicate holds
  add_fan_out_edges(a, [b, c])     same message to several nodes, in parallel
  add_fan_in_edges([b, c], d)      d receives a list of the collected results
  add_switch_case_edge_group(...)  Case/Default routing — exactly one branch
  add_multi_selection_edge_group() pick a subset of targets at runtime

Every section below is a complete workflow and needs no model.

Run:  uv run python examples/13_edge_patterns.py
"""

import asyncio

from agent_framework import (
    Case,
    Default,
    WorkflowBuilder,
    WorkflowContext,
    executor, WorkflowViz,
)
from typing_extensions import Never


async def chain_example() -> None:
    """add_chain — linear pipeline, the 90% case."""
    print("=" * 72)
    print("1. add_chain — A -> B -> C")

    @executor(id="strip")
    async def strip_(t: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(t.strip())

    @executor(id="title")
    async def title(t: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(t.title())

    @executor(id="emit")
    async def emit(t: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(t)

    wf = WorkflowBuilder(start_executor=strip_).add_chain([strip_, title, emit]).build()
    print(f"   '{'  urgent login failure  '}' -> {(await wf.run('  urgent login failure  ')).get_outputs()}")


async def conditional_example() -> None:
    """add_edge(condition=...) — the edge is only taken when the predicate holds.

    Note both edges are evaluated, so make the conditions mutually exclusive
    unless you actually want both branches to run.
    """
    print("\n" + "=" * 72)
    print("2. add_edge(condition=...) — guard each edge with a predicate")

    @executor(id="intake")
    async def intake(length: int, ctx: WorkflowContext[int]) -> None:
        await ctx.send_message(length)

    @executor(id="short_path")
    async def short_path(n: int, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"{n} chars -> handled inline")

    @executor(id="long_path")
    async def long_path(n: int, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"{n} chars -> escalated for review")

    wf = (
        WorkflowBuilder(start_executor=intake)
        .add_edge(intake, short_path, condition=lambda n: n < 100)
        .add_edge(intake, long_path, condition=lambda n: n >= 100)
        .build()
    )
    for n in (42, 512):
        print(f"   {n:3} -> {(await wf.run(n)).get_outputs()}")


async def fan_out_in_example() -> None:
    """Fan out to run in parallel, fan in to merge. The target takes a list."""
    print("\n" + "=" * 72)
    print("3. add_fan_out_edges / add_fan_in_edges — parallel then merge")

    @executor(id="dispatch")
    async def dispatch(text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text)

    @executor(id="words")
    async def words(t: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(f"words={len(t.split())}")

    @executor(id="chars")
    async def chars(t: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(f"chars={len(t)}")

    @executor(id="upper")
    async def upper(t: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(f"caps={sum(c.isupper() for c in t)}")

    @executor(id="merge")
    async def merge(parts: list[str], ctx: WorkflowContext[Never, str]) -> None:
        # A fan-in target receives the collected results as a list.
        await ctx.yield_output(" | ".join(sorted(parts)))

    wf = (
        WorkflowBuilder(start_executor=dispatch)
        .add_fan_out_edges(dispatch, [words, chars, upper])
        .add_fan_in_edges([words, chars, upper], merge)
        .build()
    )
    workflow_viz = WorkflowViz(wf)
    print(workflow_viz.save_png("fan_out_in_example.png"))
    print(f"   {(await wf.run('Payment API returned HTTP 500')).get_outputs()}")


async def switch_case_example() -> None:
    """Switch/case — exactly one branch runs, Default catches the rest."""
    print("\n" + "=" * 72)
    print("4. add_switch_case_edge_group — Case / Default, one branch wins")

    @executor(id="triage")
    async def triage(priority: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(priority)

    @executor(id="pager")
    async def pager(p: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"{p}: page the on-call engineer")

    @executor(id="queue")
    async def queue(p: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"{p}: add to the sprint queue")

    @executor(id="backlog")
    async def backlog(p: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"{p}: park in the backlog")

    wf = (
        WorkflowBuilder(start_executor=triage)
        .add_switch_case_edge_group(
            triage,
            [
                Case(condition=lambda p: p == "sev1", target=pager),
                Case(condition=lambda p: p == "sev2", target=queue),
                Default(target=backlog),  # required — the fallback branch
            ],
        )
        .build()
    )
    for p in ("sev1", "sev2", "sev4"):
        print(f"   {p} -> {(await wf.run(p)).get_outputs()}")


async def multi_selection_example() -> None:
    """Multi-selection — choose any subset of targets at runtime."""
    print("\n" + "=" * 72)
    print("5. add_multi_selection_edge_group — pick N of M targets")

    @executor(id="notify")
    async def notify(event: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(event)

    @executor(id="email")
    async def email(e: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output("email sent")

    @executor(id="slack")
    async def slack(e: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output("slack posted")

    @executor(id="sms")
    async def sms(e: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output("sms sent")

    def choose(event: str, target_ids: list[str]) -> list[str]:
        """Receives the message and every candidate id; returns the chosen ids."""
        if event == "outage":
            return target_ids                      # everything
        return [i for i in target_ids if i != "sms"]  # skip the noisy channel

    wf = (
        WorkflowBuilder(start_executor=notify)
        .add_multi_selection_edge_group(notify, [email, slack, sms], selection_func=choose)
        .build()
    )
    for event in ("outage", "deploy"):
        print(f"   {event:7} -> {sorted((await wf.run(event)).get_outputs())}")


async def main() -> None:
    await chain_example()
    await conditional_example()
    await fan_out_in_example()
    await switch_case_example()
    await multi_selection_example()
    print(
        "\nPick the simplest wiring that expresses the intent: chain, then\n"
        "conditional, then switch/case. Reach for fan-out only when the branches\n"
        "are genuinely independent — it multiplies cost as well as speed."
    )


if __name__ == "__main__":
    asyncio.run(main())
