import asyncio
from random import randint
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

# approval_mode="never_require" runs the tool without asking. Use
# "always_require" in production for tools that write data or spend money.
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}C."


async def main() -> None:

    agent = Agent(
        client=OpenAIChatCompletionClient(),
        name="WeatherAgent",
        instructions="You are a helpful weather agent. Use get_weather to answer.",
        tools=[get_weather],
    )

    result = await agent.run("What's the weather like in Seattle?")

    print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
