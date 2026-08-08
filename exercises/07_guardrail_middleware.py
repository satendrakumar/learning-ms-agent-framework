"""Exercise 07 — A guardrail that costs nothing.  (module 7 · pairs with examples/16_class_based_middleware.py)

Write agent middleware that refuses a request BEFORE the model is called. Done
right, a blocked request spends no tokens and leaks nothing — which is the whole
argument for guarding on the way in rather than filtering on the way out.

YOUR JOB
  TODO 1  in RefusalMiddleware.process: if the last user message mentions
          anything in BANNED, set context.result to a refusal and return
          WITHOUT awaiting call_next()
  TODO 2  otherwise await call_next() so the run proceeds
  TODO 3  in TimingMiddleware.process: record one entry in CALLS per tool
          invocation, around call_next()

The blocked path never touches the model, so that check is deterministic. The
allowed path does need the local model server (./vllm-run.sh).

Run:  uv run python exercises/07_guardrail_middleware.py
"""

import asyncio
from collections.abc import Awaitable, Callable

from agent_framework import (
    AgentContext,
    AgentMiddleware,
    AgentResponse,
    FunctionInvocationContext,
    FunctionMiddleware,
    Message,
    tool,
)
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from _check import check, note, report

load_dotenv()

BANNED = ("password", "secret", "api key")
REFUSAL = "I can't help with credentials."
CALLS: list[str] = []


@tool(approval_mode="never_require")
def get_time(city: str) -> str:
    """Get the current local time for a city."""
    return f"It is 14:05 in {city}."


class RefusalMiddleware(AgentMiddleware):
    """Blocks credential requests before the model sees them."""

    async def process(
        self, context: AgentContext, call_next: Callable[[], Awaitable[None]],
    ) -> None:
        # TODO 1: inspect context.messages[-1].text, and if it mentions anything in
        #         BANNED, set context.result = AgentResponse(messages=[
        #             Message("assistant", [REFUSAL])]) and return early.
        # TODO 2: otherwise let the run continue.
        await call_next()


class TimingMiddleware(FunctionMiddleware):
    """Records every tool invocation."""

    async def process(
        self, context: FunctionInvocationContext, call_next: Callable[[], Awaitable[None]],
    ) -> None:
        # TODO 3: append context.function.name to CALLS, around call_next().
        await call_next()


async def main() -> None:
    print(__doc__.splitlines()[0])
    agent = OpenAIChatCompletionClient().as_agent(
        name="GuardedAgent",
        instructions="You are helpful. Use get_time when asked about the time.",
        tools=[get_time],
        middleware=[RefusalMiddleware(), TimingMiddleware()],
    )

    # --- the blocked path: deterministic, no model call ----------------------
    CALLS.clear()
    blocked = await agent.run("What is the admin password?", options={"max_tokens": 60})
    note(f"blocked response: {(blocked.text or '').strip()[:60]!r}")
    check(
        "banned request is refused with our exact message",
        (blocked.text or "").strip() == REFUSAL,
        "set context.result before returning, or the caller gets an empty response",
    )
    check(
        "no tool ran on the blocked path",
        not CALLS,
        f"CALLS was {CALLS!r} — the run should stop before any tool",
    )

    # --- the allowed path: needs the model ----------------------------------
    CALLS.clear()
    allowed = await agent.run("What time is it in Pune?", options={"max_tokens": 80})
    note(f"allowed response: {(allowed.text or '').strip()[:60]!r}")
    check(
        "allowed request was not refused",
        (allowed.text or "").strip() != REFUSAL,
        "call_next() must be awaited when nothing is banned",
    )
    check(
        "function middleware recorded the tool call",
        CALLS == ["get_time"],
        f"CALLS was {CALLS!r}. If it is empty the model may simply not have called the "
        "tool — re-run; if it stays empty, check TODO 3.",
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
