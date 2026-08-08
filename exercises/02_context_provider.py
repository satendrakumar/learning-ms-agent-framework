"""Exercise 02 — Write a context provider.  (module 4 · pairs with examples/04_memory.py)

A provider has exactly two hooks: `before_run` injects context, `after_run`
records what happened. Build one that tells the agent which turn it is on.

YOUR JOB
  TODO 1  in before_run: read the turn count out of `state`, work out which turn
          this is, and inject it with context.extend_instructions(...)
  TODO 2  in after_run: increment the stored count so the next turn sees it

Note `state` is already scoped to this provider by source_id — you do not need
to namespace your keys.

Needs the local model server (./vllm-run.sh).
Run:  uv run python exercises/02_context_provider.py
"""

import asyncio
from typing import Any

from agent_framework import AgentSession, ContextProvider, SessionContext
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from _check import check, note, report

load_dotenv()


class TurnCounterProvider(ContextProvider):
    """Tells the agent which turn of the conversation it is currently on."""

    DEFAULT_SOURCE_ID = "turn_counter"

    def __init__(self) -> None:
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self, *, agent: Any, session: AgentSession | None,
        context: SessionContext, state: dict[str, Any],
    ) -> None:
        # TODO 1: turns_so_far = state.get("turns", 0); this turn is turns_so_far + 1.
        #         Inject a sentence naming the turn number, then stash the same
        #         sentence in state["last_injected"] so the self-check can see it.
        #
        #         context.extend_instructions(self.source_id, "<your sentence>")
        pass

    async def after_run(
        self, *, agent: Any, session: AgentSession | None,
        context: SessionContext, state: dict[str, Any],
    ) -> None:
        # TODO 2: record that a turn completed.
        pass


async def main() -> None:
    print(__doc__.splitlines()[0])
    agent = OpenAIChatCompletionClient().as_agent(
        name="CounterAgent",
        instructions="You are terse. One short sentence per answer.",
        context_providers=[TurnCounterProvider()],
    )
    session = agent.create_session()

    last = ""
    for prompt in ("Hello.", "Still there?", "Which turn is this?"):
        result = await agent.run(prompt, session=session, options={"max_tokens": 60})
        last = result.text or ""
    note(f"agent's third answer: {last.strip()[:70]!r}")

    stored = session.state.get("turn_counter", {})
    check(
        "provider wrote to its own slice of session.state",
        isinstance(stored, dict) and stored,
        "session.state['turn_counter'] is empty — is after_run writing anything?",
    )
    check(
        "turn count is 3 after three runs",
        stored.get("turns") == 3,
        f"state['turns'] was {stored.get('turns')!r}; increment it in after_run",
    )
    injected = str(stored.get("last_injected", ""))
    check(
        "before_run injected context naming turn 3",
        "3" in injected,
        f"state['last_injected'] was {injected!r}; it should name the current turn",
    )
    check(
        "injected text is a sentence, not just a number",
        len(injected.split()) >= 4,
        "give the model a readable instruction, e.g. 'This is turn 3 of the conversation.'",
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
