import asyncio

from agent_framework.openai import OpenAIChatClient
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

class OutputStruct(BaseModel):
    """A structured outputs model for testing purposes."""

    city: str
    description: str


async def non_streaming_example() -> None:
    print("=== Non-streaming example ===")

    agent = OpenAIChatCompletionClient().as_agent(
        name="CityAgent",
        instructions="You are a helpful agent that describes cities in a structured format.",
    )

    query = "Tell me about Paris, France"
    print(f"User: {query}")

    result = await agent.run(query, options={"response_format": OutputStruct, "max_tokens": 500})

    if structured_data := result.value:
        print("Structured Outputs Agent:")
        print(f"City: {structured_data.city}")
        print(f"Description: {structured_data.description}")
    else:
        print(f"Failed to parse response: {result.text}")


async def streaming_example() -> None:
    print("=== Streaming example ===")

    agent = OpenAIChatCompletionClient().as_agent(
        name="CityAgent",
        instructions="You are a helpful agent that describes cities in a structured format.",
    )

    query = "Tell me about Tokyo, Japan"
    print(f"User: {query}")

    # Stream updates in real time using ResponseStream
    stream = agent.run(query, stream=True, options={"response_format": OutputStruct,  "max_tokens": 500})
    async for update in stream:
        if update.text:
            print(update.text, end="", flush=True)
    print()

    # get_final_response() returns the AgentResponse with structured outputs parsed
    result = await stream.get_final_response()

    if structured_data := result.value:
        print("Structured Outputs (from streaming with ResponseStream):")
        print(f"City: {structured_data.city}")
        print(f"Description: {structured_data.description}")
    else:
        print(f"Failed to parse response: {result.text}")


async def main() -> None:
    print("=== OpenAI Responses Agent with Structured Outputs ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())