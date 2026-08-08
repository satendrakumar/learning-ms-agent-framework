import asyncio
import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent

async def main():
    a2a_host = "http://0.0.0.0:9999"

    # 1. Discover the remote agent's capabilities
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_host)
        agent_card = await resolver.get_agent_card()
        print(f"Found agent: {agent_card.name}")

    # 2. Create an A2AAgent and send a message
    async with A2AAgent(
        name=agent_card.name,
        agent_card=agent_card,
        url=a2a_host,
    ) as agent:
        response = await agent.run("search flights for Europe")
        for message in response.messages:
            print(message.text)

asyncio.run(main())