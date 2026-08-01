import asyncio

from agent_framework import Agent, MCPStreamableHTTPTool

from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    async with Agent(
        client=OpenAIChatCompletionClient(),
        name="DocsAgent",
        instructions="You help with Microsoft documentation questions.",
        tools=MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ),
    ) as agent:
        query = "How do I create an Azure storage account using the az CLI?"
        print(f"User: {query}\nDocsAgent: ", end="", flush=True)
        async for chunk in agent.run(query, stream=True):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
