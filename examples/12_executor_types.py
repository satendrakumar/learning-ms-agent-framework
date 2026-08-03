"""Workflows — Executors: every way to declare a workflow node.

Executors are the nodes. Four things to learn, all in this file:

  1. Class-based executors      `Executor` + `@handler`
  2. Multiple input types       several `@handler` methods on one executor
  3. Function-based executors   `@executor(id=...)` on an async function
  4. Explicit type parameters   `@handler(input=..., output=...)` instead of hints

The `WorkflowContext` type parameters are load-bearing — they are how the
framework knows what each node sends and yields, and it validates them at build
time:

  WorkflowContext              side effects only (sends nothing, yields nothing)
  WorkflowContext[T]           sends T downstream
  WorkflowContext[Never, U]    yields U as a workflow output, sends nothing
  WorkflowContext[T, U]        sends T downstream and yields U

Which nodes' outputs the caller actually sees is a *build-time* decision on
WorkflowBuilder (`output_from` / `intermediate_output_from`), not a per-call flag.

Docs: https://learn.microsoft.com/agent-framework/workflows/executors
Run:  uv run python examples/12_executor_types.py      (no model needed)
"""

import asyncio

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, executor, handler
from typing_extensions import Never


# --- 1 & 2. a class-based executor handling two different input types ----------
class Ingest(Executor):
    """One node, two accepted message types. Routing is by type annotation."""

    @handler
    async def from_text(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text)

    @handler
    async def from_lines(self, lines: list[str], ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(" ".join(lines))


# --- 3. a function-based executor ---------------------------------------------
@executor(id="normalise")
async def normalise(text: str, ctx: WorkflowContext[str]) -> None:
    """Plain async function, same capabilities as the class form."""
    await ctx.send_message(" ".join(text.split()).lower())


# --- side effects only: no type parameters at all -----------------------------
@executor(id="audit")
async def audit(text: str, ctx: WorkflowContext) -> None:
    """Sends nothing, yields nothing — a sink. Logging, metrics, tracing."""
    print(f"   [audit] observed {text!r}")


# --- 4. explicit type parameters instead of annotations -----------------------
class WordCount(Executor):
    """When you declare types on the decorator you must declare all of them."""

    @handler(input=str, output=str, workflow_output=int)
    async def count(self, text, ctx) -> None:  # note: no annotations needed
        words = len(text.split())
        await ctx.yield_output(words)          # an int, per workflow_output=int
        await ctx.send_message(f"{text} ({words} words)")


# --- yields only ---------------------------------------------------------------
@executor(id="finalise")
async def finalise(text: str, ctx: WorkflowContext[Never, str]) -> None:
    """Never means 'sends nothing downstream'. It is the end of the line."""
    await ctx.yield_output(f"final: {text}")


def build():
    ingest = Ingest(id="ingest")
    words = WordCount(id="word_count")
    return (
        WorkflowBuilder(
            start_executor=ingest,
            # Only finalise contributes to get_outputs(); WordCount's int is
            # observational. Same yield_output() call, different designation.
            output_from=[finalise],
            intermediate_output_from=[words],
        )
        .add_chain([ingest, normalise, words, finalise])
        .add_edge(normalise, audit)  # fan out to the sink as well
        .build()
    )


async def main() -> None:
    workflow = build()

    print("run 1 — start executor receives a str")
    result = await workflow.run("  The   Quick  Brown Fox  ")
    print(f"   outputs      {result.get_outputs()}")
    print(f"   intermediate {result.get_intermediate_outputs()}")

    print("\nrun 2 — same executor, same graph, a list[str] instead")
    result = await workflow.run(["Hello", "from", "the", "OTHER", "handler"])
    print(f"   outputs      {result.get_outputs()}")
    print(f"   intermediate {result.get_intermediate_outputs()}")

    print(
        "\nThe start executor accepted both types because Ingest declares two\n"
        "handlers. Dispatch is on the message type, not on the edge."
    )


if __name__ == "__main__":
    asyncio.run(main())
