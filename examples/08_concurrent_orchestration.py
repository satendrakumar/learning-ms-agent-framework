"""Level 7b — Concurrent multi-agent orchestration (fan-out / fan-in).

ConcurrentBuilder sends the same prompt to every participant in parallel, then
aggregates their responses. Great for gathering diverse perspectives fast.

Run:  uv run python examples/08_concurrent_orchestration.py
"""

import asyncio

from agent_framework import Agent
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    client = OpenAIChatCompletionClient()

    researcher = Agent(
        client=client,
        name="researcher",
        instructions="You are a market researcher. Give concise, factual insights.",
        default_options={"max_tokens": 500}
    )
    marketer = Agent(
        client=client,
        name="marketer",
        instructions="You are a marketing strategist. Craft compelling value propositions.",
        default_options={"max_tokens": 500}
    )
    legal = Agent(
        client=client,
        name="legal",
        instructions="You are a compliance reviewer. Highlight constraints and policy concerns.",
        default_options={"max_tokens": 500}
    )

    workflow = ConcurrentBuilder(participants=[researcher, marketer, legal]).build()

    events = await workflow.run(
        "We are launching a budget-friendly electric bike for urban commuters.",
    )
    outputs = events.get_outputs()

    response = outputs[0]

    for i, msg in enumerate(response.messages, start=1):
        print("-" * 50)
        print(f"{i:02d} [{msg.author_name}]")
        print(msg.text)


if __name__ == "__main__":
    asyncio.run(main())
