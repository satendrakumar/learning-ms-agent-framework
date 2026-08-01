import asyncio
from typing import Any

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


class UserMemoryProvider(ContextProvider):
    """Remembers the user's name across turns via session state."""

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self) -> None:
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Always address them by name.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask for it politely.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        for msg in context.input_messages:
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                state["user_name"] = text.lower().split("my name is")[-1].strip().split()[0].capitalize()


async def main() -> None:
    agent = Agent(
        client=OpenAIChatCompletionClient(),
        name="MemoryAgent",
        instructions="You are a friendly assistant.",
        context_providers=[UserMemoryProvider()],
    )

    session = agent.create_session()
    print(f"User: Hello! What's the square root of 9?")
    result = await agent.run("Hello! What's the square root of 9?", session=session)
    print(f"Agent: {result}\n\n")

    print(f"User: My name is Alice \n")
    result = await agent.run("My name is Alice", session=session)
    print(f"Agent: {result}\n")

    print(f"User: What is 2 + 2? \n")
    result = await agent.run("What is 2 + 2?", session=session)
    print(f"Agent: {result}\n")


    stored = session.state.get("user_memory", {})
    print(f"[Session State] Stored user name: {stored.get('user_name')}")


if __name__ == "__main__":
    asyncio.run(main())
