"""Memory & context — Persistence: surviving a process restart.

An in-memory session dies with the process. Two ways to outlive it:

  1. FileHistoryProvider  — the provider writes an append-only file per session.
  2. session.to_dict()    — serialise the whole session yourself and store it
                            wherever you already keep state (Redis, a DB, a queue).

Both are shown below. Run this twice: the file-backed conversation keeps growing,
because turn one is still on disk from the previous run.

Run:  uv run python examples/06_persistent_history.py
"""

import asyncio
import json
from pathlib import Path

from agent_framework import AgentSession, FileHistoryProvider, InMemoryHistoryProvider
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

STORE = Path(__file__).parent.parent / ".sessions"
SESSION_ID = "demo-session"


async def file_backed() -> None:
    """The provider owns persistence — you just give it a directory.

    Note: FileHistoryProvider is marked experimental in 1.13 and warns on use.
    It is ideal for local development; for a service, prefer a real store
    (RedisHistoryProvider, Cosmos) or serialise the session yourself — see below.
    """
    print("=" * 68)
    print("1. FileHistoryProvider — the provider writes to disk")
    STORE.mkdir(exist_ok=True)

    client = OpenAIChatCompletionClient()
    agent = client.as_agent(
        name="PersistentAgent",
        instructions="You are concise. One short sentence per answer.",
        context_providers=[FileHistoryProvider(STORE)],
    )

    # Reusing the same session_id is what picks up the previous run's history.
    session = agent.create_session(session_id=SESSION_ID)
    result = await agent.run(
        "Remember this item: milk. Then list every item you have been asked "
        "to remember so far.",
        session=session,
        options={"max_tokens": 120},
    )
    print(f"Agent: {result.text}")

    files = sorted(STORE.glob("*"))
    print(f"\n[disk] {STORE.name}/ contains: {[f.name for f in files]}")
    if files:
        raw = files[0].read_text().splitlines()
        print(f"[disk] {len(raw)} appended record(s) — run again and this grows")


async def serialise_yourself() -> None:
    """You own persistence — the session is just a dict."""
    print("\n" + "=" * 68)
    print("2. session.to_dict() — serialise the session and rehydrate it later")

    client = OpenAIChatCompletionClient()

    def make_agent():
        return client.as_agent(
            name="PersistentAgent",
            instructions="You are concise. One short sentence per answer.",
            context_providers=[InMemoryHistoryProvider(load_messages=True)],
        )

    # --- process A: have a turn, then serialise ------------------------------
    agent_a = make_agent()
    session = agent_a.create_session()
    await agent_a.run("My favourite colour is white.", session=session,options={"max_tokens": 60})

    blob = json.dumps(session.to_dict())
    print(f"[serialise] {len(blob)} bytes of JSON — store this anywhere")

    # --- process B: a brand-new agent, restored session ----------------------
    del agent_a, session
    agent_b = make_agent()
    restored = AgentSession.from_dict(json.loads(blob))

    result = await agent_b.run("What is my favourite colour?", session=restored,options={"max_tokens": 60})
    print(f"Agent (new instance, restored session): {result.text}")
    print("\nSame conversation, different agent object. That is the persistence seam.")


async def main() -> None:
    await file_backed()
    await serialise_yourself()
    print(f"\nDelete {STORE} to start the file-backed conversation over.")


if __name__ == "__main__":
    asyncio.run(main())
