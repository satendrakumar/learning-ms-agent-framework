import asyncio

from agent_framework import Agent
from agent_framework_openai import OpenAIChatCompletionClient, OpenAIChatOptions
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    agent = Agent(
        client=OpenAIChatCompletionClient(),  # OpenAIChatClient() is uses the response api
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )

    # Non-streaming: wait for the full response.
    result = await agent.run("What is the capital of France?")
    print(f"Agent: {result}\n")

    # Non-streaming: wait for the full response with request options
    options = {
        "temperature": 0.3,
        "max_tokens": 150
    }
    result = await agent.run("What is the capital of France?", options=options)
    print(f"Agent: {result}\n")

    # Streaming: print tokens as they arrive.
    print("Agent (streaming): ", end="", flush=True)
    async for chunk in agent.run("Tell me a one-sentence fun fact.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
