"""Memory & context — Layered memory: transcript, audit trail.

Context providers compose. Each one gets the same `before_run`/`after_run` hooks
and its own namespace in `session.state` (keyed by `source_id`), so you can stack
several providers with different jobs:

  InMemoryHistoryProvider   the conversation transcript — loaded and stored
  RedisContextProvider      durable semantic memory across sessions (optional)
  InMemoryHistoryProvider   a write-only audit copy, including injected context

Order matters: providers run in list order, so the audit store goes last —
`store_context_messages=True` makes it record what the earlier providers added.

Run:  uv run python examples/05_memory_providers.py
"""

import asyncio

from agent_framework import InMemoryHistoryProvider
from agent_framework_openai import OpenAIChatCompletionClient
from agent_framework_redis import RedisContextProvider
from dotenv import load_dotenv

load_dotenv()


def build_providers() -> list[object]:
    """Three providers, three jobs, one session."""
    # 1. The transcript. load_messages=True replays it into every run, which is
    #    what makes the conversation multi-turn.
    transcript = InMemoryHistoryProvider(source_id="in_memory", load_messages=True)

    providers: list[object] = [transcript]

    # 2. Durable semantic memory. redis is a hosted service, so this one is
    #    opt-in — everything else in this example runs offline.
    #docker run -d --name redis -p 6379:6379 redis:latest
    providers.append(
        RedisContextProvider("redis_user_memory",agent_id="learning-agent",
                             redis_url = "redis://localhost:6379", index_name="context_memory_index",prefix="context_memory")
    )


    # 3. An audit copy. load_messages=False means it never feeds the model; it
    #    only records. store_context_messages=True captures context that other
    #    providers injected, which is exactly what you want in an audit log.
    providers.append(
        InMemoryHistoryProvider(
            "audit_memory",
            load_messages=False,
            store_context_messages=True,
        )
    )
    return providers


async def main() -> None:
    client = OpenAIChatCompletionClient()

    agent = client.as_agent(
        name="MemoryAgent",
        instructions="You are a friendly assistant. Keep answers to one sentence.",
        context_providers=build_providers(),  # audit store last
    )

    session = agent.create_session()

    for prompt in (
        "My name is Bob and I work on payments.",
        "What do you remember about me?",
    ):
        print(f"\nUser : {prompt}")
        result = await agent.run(prompt, session=session, options={"max_tokens": 120})
        print(f"Agent: {result.text}")

    # Each provider owns a slice of session.state, namespaced by source_id.
    print("\n[session state] namespaces:", sorted(session.state))
    for source_id in sorted(session.state):
        stored = session.state[source_id]
        if isinstance(stored, dict) and "messages" in stored:
            for n, message in enumerate(stored["messages"]):
                print(f"  {source_id:12} {n:2} {message.to_dict()}")
        else:
            print(f"  {source_id:12} {type(stored).__name__}")

    print(
        "\nThe transcript feeds the model; the audit copy never does. Same hooks, "
        "different jobs — that is the whole composition story."
    )


if __name__ == "__main__":
    asyncio.run(main())
