"""Exercise 03 — Compact well, not just hard.  (module 4 · pairs with examples/08_compaction_strategies.py)

A support conversation has grown to ~2,200 tokens, and most of that is verbose
tool payloads nobody needs any more. You have a 300-token budget.

Here is the thing worth learning: TokenBudgetComposedStrategy ALWAYS gets you
under budget. If your strategies do not do the job, it falls back to excluding
whole groups oldest-first — and will even drop the system prompt as a last
resort. So "did I hit the budget" is not the question.

The question is how much useful conversation survives at that budget. Leave
`strategies=[]` and the blunt fallback keeps 3 messages. A tool-aware strategy
throws away the fat and keeps twice as many real turns for the same budget.

YOUR JOB
  TODO  fill in `strategies=[...]` so at least 6 messages survive, with no
        verbose tool payload left in them.

Available: SelectiveToolCallCompactionStrategy(keep_last_tool_call_groups=...)
           ToolResultCompactionStrategy(keep_last_tool_call_groups=...)
           SlidingWindowStrategy(keep_last_groups=...)
           TruncationStrategy(max_n=..., compact_to=..., tokenizer=...)

No model needed.
Run:  uv run python exercises/03_compaction_budget.py
"""

import asyncio
import json

from agent_framework import (
    CharacterEstimatorTokenizer,
    Content,
    Message,
    SelectiveToolCallCompactionStrategy,  # noqa: F401
    SlidingWindowStrategy,  # noqa: F401
    TokenBudgetComposedStrategy,
    ToolResultCompactionStrategy,  # noqa: F401
    TruncationStrategy,  # noqa: F401
    apply_compaction,
)

from _check import check, note, report

TOKENIZER = CharacterEstimatorTokenizer()
BUDGET = 300
LAST_QUESTION = "summarise every ticket you looked at"
PAYLOAD_MARKER = "verbose audit entry"


def support_history(turns: int = 5) -> list[Message]:
    """Fresh every call — apply_compaction annotates the list you hand it."""
    messages = [Message("system", ["You are a support assistant. Always cite the ticket id."])]
    for i in range(turns):
        messages.append(Message("user", [f"ticket {i}: what is the status?"]))
        messages.append(Message("assistant", [Content.from_function_call(
            call_id=f"call-{i}", name="lookup_ticket", arguments={"id": i})]))
        messages.append(Message("tool", [Content.from_function_result(
            call_id=f"call-{i}",
            result="{'status': 'open', 'log': " + f"'{PAYLOAD_MARKER}' " * 20 + "}")]))
        messages.append(Message("assistant", [f"Ticket {i} is open."]))
    messages.append(Message("user", [LAST_QUESTION]))
    return messages


def rough_tokens(messages: list[Message]) -> int:
    """Serialised size — a caller's view of cost, not the framework's internal metric."""
    return sum(TOKENIZER.count_tokens(json.dumps(m.to_dict())) for m in messages)


def build_strategy() -> TokenBudgetComposedStrategy:
    return TokenBudgetComposedStrategy(
        token_budget=BUDGET,
        tokenizer=TOKENIZER,
        # TODO: compose one or more strategies. Get rid of the tool payloads first.
        strategies=[],
    )


async def main() -> None:
    print(__doc__.splitlines()[0])
    before = support_history()
    note(f"before: {len(before)} messages / ~{rough_tokens(before)} serialised tokens")

    strategy = build_strategy()
    check(
        "at least one strategy is composed",
        len(list(strategy.strategies)) >= 1,
        "with strategies=[] you are just accepting the blunt fallback",
    )

    after = await apply_compaction(support_history(), strategy=strategy, tokenizer=TOKENIZER)
    note(f"after:  {len(after)} messages / ~{rough_tokens(after)} serialised tokens")

    check(
        "system prompt survived",
        any(m.role == "system" for m in after),
        "the strict fallback drops even this when the budget cannot be met",
    )
    check(
        "the user's latest question survived",
        any(LAST_QUESTION in (m.text or "") for m in after),
        "you compacted away the thing the model was asked to answer",
    )
    check(
        "at least 6 messages survived",
        len(after) >= 6,
        f"only {len(after)} left — the fallback alone keeps 3. Drop the tool payloads "
        "instead of windowing the conversation, and do not stack a tight window on top.",
    )
    leftover = [m for m in after if PAYLOAD_MARKER in json.dumps(m.to_dict())]
    check(
        "no verbose tool payload is left",
        not leftover,
        f"{len(leftover)} message(s) still carry the payload — note that summarising a "
        "tool group keeps its text, while excluding it does not",
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
