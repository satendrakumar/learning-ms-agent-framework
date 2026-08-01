"""Level 7a — Graph workflow (executors + edges).

The graph API gives you explicit control over topology. Executors are nodes;
edges route messages between them. This tiny graph needs no model at all.

Run:  uv run python examples/07_graph_workflow.py
"""

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    handler,
)
from typing_extensions import Never


# A class-based executor: receives a message, sends the next one.
class UpperCase(Executor):
    def __init__(self, id: str) -> None:
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())


# A function-based executor: yields the final workflow output.
@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(text[::-1])


def create_workflow():
    upper = UpperCase(id="upper_case")
    return (WorkflowBuilder(start_executor=upper)
            .add_edge(upper, reverse_text)
            .build())


async def main() -> None:
    workflow = create_workflow()
    events = await workflow.run("hello world")
    print(f"Output: {events.get_outputs()}")        # ['DLROW OLLEH']
    print(f"Final state: {events.get_final_state()}")


if __name__ == "__main__":
    asyncio.run(main())
