import asyncio

from agent_framework import create_harness_agent
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

agent = create_harness_agent(
    OpenAIChatCompletionClient(),
)

async def main() -> None:
    # A session carries the harness state (plan, todos, history) across turns.
    session = agent.create_session()

    print("Harness agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("> ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        # Stream this turn's output as the harness plans and works through the request.
        async for chunk in agent.run(user_input, session=session, stream=True,options={"max_tokens": 200}):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()

if __name__ == "__main__":
    asyncio.run(main())