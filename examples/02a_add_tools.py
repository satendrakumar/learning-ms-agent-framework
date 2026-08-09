import asyncio
from random import randint
from typing import Annotated

from agent_framework import Agent, Message, tool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


@tool(approval_mode="always_require")
def get_weather(
    location: Annotated[
        str,
        Field(description="The location to get the weather for."),
    ],
) -> str:
    """Get the weather for a given location."""

    conditions = ["sunny", "cloudy", "rainy", "stormy"]

    return (
        f"The weather in {location} is "
        f"{conditions[randint(0, 3)]} "
        f"with a high of {randint(10, 30)}C."
    )


async def main() -> None:

    agent = Agent(
        client=OpenAIChatClient(),
        name="WeatherAgent",
        instructions=(
            "You are a helpful weather agent. "
            "Always use get_weather to answer weather questions."
        ),
        tools=[get_weather],
    )

    query = "What's the weather like in Seattle?"

    # First run
    result = await agent.run(query)

    # Check whether the agent is waiting for approval
    if result.user_input_requests:

        for request in result.user_input_requests:

            if request.function_call is None:
                continue

            print("\nTool approval required")
            print("----------------------")
            print(f"Tool: {request.function_call.name}")
            print(f"Arguments: {request.function_call.arguments}")

            answer = input("\nApprove tool call? [y/n]: ").strip().lower()

            approved = answer in ("y", "yes")

            # Create approval response
            approval_message = Message(
                role="user",
                contents=[
                    request.to_function_approval_response(approved)
                ],
            )

            # Continue agent execution
            result = await agent.run(
                [
                    query,
                    Message(
                        role="assistant",
                        contents=[request],
                    ),
                    approval_message,
                ]
            )

    print("\nAgent:", result.text)


if __name__ == "__main__":
    asyncio.run(main())