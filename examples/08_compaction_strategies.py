"""Memory & context — The compaction strategy catalogue.

Compaction decides what to throw away when a conversation outgrows the context
window. Six strategies ship in the box, and they answer different questions:

  SlidingWindowStrategy        keep the last N turns, drop the rest
  TruncationStrategy           over N messages? cut back to M, oldest first
  ToolResultCompactionStrategy replace old tool groups with a readable summary line
  SelectiveToolCallCompaction  fully exclude old tool groups instead of summarising
  ContextWindowCompaction      derive the budget from the model's window size
  TokenBudgetComposedStrategy  run several strategies until a token budget is met
  SummarizationStrategy        fold old turns into a summary (needs a model)

Everything except summarization runs with no model at all, so this file is a
fast way to build intuition for what each one actually does.

Run:  uv run python examples/08_compaction_strategies.py
"""

import asyncio
import json

from agent_framework import (
    CharacterEstimatorTokenizer,
    Content,
    ContextWindowCompactionStrategy,
    Message,
    SelectiveToolCallCompactionStrategy,
    SlidingWindowStrategy,
    SummarizationStrategy,
    TokenBudgetComposedStrategy,
    ToolResultCompactionStrategy,
    TruncationStrategy,
    apply_compaction,
)
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

TOKENIZER = CharacterEstimatorTokenizer()


def sample_history(turns: int = 4) -> list[Message]:
    """A realistic transcript: system prompt, chat, and fat tool results.

    Built fresh for every strategy on purpose — apply_compaction annotates the
    messages it is given, so reusing one list would feed each strategy the
    previous strategy's output.
    """
    messages = [Message("system", ["You are a helpful travel assistant."])]
    for i in range(turns):
        messages.append(Message("user", [f"What is the weather in city {i}?"]))
        messages.append(
            Message("assistant", [Content.from_function_call(
                call_id=f"call-{i}", name="get_weather", arguments={"location": f"city {i}"},
            )])
        )
        # Tool results are where context goes to die — verbose JSON, rarely
        # needed once the model has answered.
        messages.append(
            Message("tool", [Content.from_function_result(
                call_id=f"call-{i}",
                result=f"{{'city': 'city {i}', 'forecast': " + "'detailed hourly data' " * 25 + "}",
            )])
        )
        messages.append(Message("assistant", [f"City {i} is sunny with a high of 24C."]))
    return messages


def size(messages: list[Message]) -> str:
    """Approximate the real cost of a transcript.

    Note `Message.text` is empty for tool-call and tool-result content, so
    counting only `.text` would badly undercount exactly the messages that
    dominate a tool-heavy history. Measure the serialised message instead.
    """
    tokens = sum(TOKENIZER.count_tokens(json.dumps(m.to_dict())) for m in messages)
    return f"{len(messages):2} msgs / ~{tokens:5} tokens"


async def show(label: str, strategy: object, note: str) -> None:
    before = sample_history()
    after = await apply_compaction(before, strategy=strategy, tokenizer=TOKENIZER)
    print(f"\n{label}")
    print(f"   before  {size(sample_history())}")
    print(f"   after   {size(after)}")
    print(f"   {note}")


async def main() -> None:
    baseline = sample_history()
    print("=" * 74)
    print(f"Baseline transcript: {size(baseline)}")
    print("=" * 74)

    await show(
        "SlidingWindowStrategy(keep_last_groups=2)",
        SlidingWindowStrategy(keep_last_groups=2),
        "Bluntest option. Keeps the system prompt and the last 2 groups.",
    )

    await show(
        "TruncationStrategy(max_n=12, compact_to=6)",
        TruncationStrategy(max_n=12, compact_to=6, tokenizer=TOKENIZER),
        "Triggers above max_n messages, then trims oldest-first down to compact_to.",
    )

    await show(
        "ToolResultCompactionStrategy(keep_last_tool_call_groups=1)",
        ToolResultCompactionStrategy(keep_last_tool_call_groups=1),
        "Replaces old call/result pairs with a '[Tool results: ...]' line. Reclaims the\n"
        "   message structure and keeps a readable trace — the payload text survives.",
    )

    await show(
        "SelectiveToolCallCompactionStrategy(keep_last_tool_call_groups=2)",
        SelectiveToolCallCompactionStrategy(keep_last_tool_call_groups=2),
        "Excludes old tool groups outright instead of summarising them. Bigger token\n"
        "   saving than the strategy above, at the cost of losing the trace.",
    )

    await show(
        "ContextWindowCompactionStrategy(window=2000, output=500)",
        ContextWindowCompactionStrategy(
            max_context_window_tokens=2000, max_output_tokens=500, tokenizer=TOKENIZER,
        ),
        "Describe the model, not the tactic — it derives the budget for you.",
    )

    await show(
        "TokenBudgetComposedStrategy(token_budget=400)",
        TokenBudgetComposedStrategy(
            token_budget=400,
            tokenizer=TOKENIZER,
            strategies=[
                ToolResultCompactionStrategy(keep_last_tool_call_groups=1),
                SlidingWindowStrategy(keep_last_groups=3),
            ],
        ),
        "Runs strategies in order until the budget is met — cheap ones first.",
    )

    # Summarization is the only strategy that costs a model call.
    print("\nSummarizationStrategy(target_count=2)")
    try:
        summariser = OpenAIChatCompletionClient()
        after = await apply_compaction(
            sample_history(),
            strategy=SummarizationStrategy(client=summariser, target_count=2, threshold=1),
            tokenizer=TOKENIZER,
        )
        print(f"   before  {size(sample_history())}")
        print(f"   after   {size(after)}")
        print("   Old turns replaced by generated summary text. Point this at a cheap model.")
    except Exception as exc:  # no model server reachable
        print(f"   skipped — needs a reachable model ({type(exc).__name__}: {exc})")

    print(
        "\nNote the two tool strategies differ on purpose: one preserves a readable\n"
        "trace, the other reclaims more tokens. Compose cheap structural wins first,\n"
        "then summarise, then hard-window as a backstop — example 07 wires that into\n"
        "a live agent via CompactionProvider."
    )


if __name__ == "__main__":
    asyncio.run(main())
