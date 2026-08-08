import asyncio

from agent_framework import Agent, workflow
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()



client = OpenAIChatCompletionClient()



writer = Agent(
    name="WriterAgent",
    client=client,
    instructions="Write a short poem (4 lines max) about the given topic.",
)

reviewer = Agent(
    name="ReviewerAgent",
    client=client,
    instructions="Review the given poem in one sentence. Is it good?",
)


@workflow
async def poem_workflow(topic: str) -> str:
    poem = (await writer.run(f"Write a poem about: {topic}")).text
    review = (await reviewer.run(f"Review this poem: {poem}")).text
    return f"Poem:\n{poem}\n\nReview: {review}"


async def main() -> None:
    result = await poem_workflow.run("a cat learning to code")
    print(result.get_outputs()[0])


if __name__ == "__main__":
    asyncio.run(main())
