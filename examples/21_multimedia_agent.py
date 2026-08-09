import asyncio
from pathlib import Path

from dotenv import load_dotenv

from agent_framework import Agent, Content, Message
from agent_framework.openai import OpenAIChatClient


load_dotenv()


async def main() -> None:
    agent = Agent(
        client=OpenAIChatClient(),
        name="VisionAgent",
        instructions="""
        You are a helpful multimodal AI agent.

        You can analyze images provided by the user.
        Carefully inspect the image and answer questions about:
        - objects
        - people
        - text
        - tables
        - charts
        - documents
        - screenshots

        If something is unclear or cannot be reliably determined,
        explicitly say so.
        """,
    )

    image_path = Path("images/qwen-max.jpg")

    image_bytes = image_path.read_bytes()

    message = Message(
        role="user",
        contents=[
            Content.from_text(
                "Describe this image in detail. "
                "Identify the important objects, text, and context."
            ),
            Content.from_data(
                data=image_bytes,
                media_type="image/jpeg",
            ),
        ],
    )

    result = await agent.run(message)

    print("\nAgent:")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())