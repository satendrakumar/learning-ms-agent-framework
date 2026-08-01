import asyncio

from agent_framework import Agent
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    agent = Agent(
        client=OpenAIChatCompletionClient(),
        name="ConversationAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )

    session = agent.create_session()


    print(f"User: My name is Alice and I love hiking")
    result = await agent.run("My name is Alice and I love hiking.", session=session)
    print(f"Agent: {result}\n")

    # Because we reuse `session`, the agent still knows the name and hobby.
    print(f"User: What do you remember about me?")
    result = await agent.run("What do you remember about me?", session=session)
    print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
