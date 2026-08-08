import asyncio

from agent_framework import Agent, CompactionProvider, InMemoryHistoryProvider
from agent_framework import (
    CharacterEstimatorTokenizer,
    SlidingWindowStrategy,
    SummarizationStrategy,
    TokenBudgetComposedStrategy,
    ToolResultCompactionStrategy,
)
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()




async def main() -> None:
    tokenizer = CharacterEstimatorTokenizer()

    summarizer_client = OpenAIChatCompletionClient(model="gemma4:e2b",base_url="http://localhost:11434/v1", api_key="test")

    client = OpenAIChatCompletionClient()

    pipeline = TokenBudgetComposedStrategy(
        token_budget=2_000, #Maximum included token count allowed after compaction.
        tokenizer=tokenizer,
        strategies=[
            ToolResultCompactionStrategy(keep_last_tool_call_groups=1),
            SummarizationStrategy(client=summarizer_client, target_count=2, threshold=1),
            SlidingWindowStrategy(keep_last_groups=20),
        ],
    )

    history = InMemoryHistoryProvider()

    compaction = CompactionProvider(
        before_strategy=pipeline,
        history_source_id=history.source_id,
    )

    agent = Agent(
        client=client,
        name="ShoppingAssistant",
        instructions="You are a helpful shopping assistant.",
        context_providers=[history, compaction],
    )

    session = agent.create_session()

    print(await agent.run("What's the price of a laptop?", session=session))
    print(await agent.run("compare top 4 laptop", session=session))
    print(await agent.run("find best laptop with in $200", session=session))

    print(await agent.run("what are tips to keep laptop better", session=session))



if __name__ == "__main__":
    asyncio.run(main())
