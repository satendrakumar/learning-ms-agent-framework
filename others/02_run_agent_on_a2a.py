import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from agent_framework import Agent
from agent_framework.a2a import A2AExecutor
from agent_framework.openai import OpenAIChatClient
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv(verbose=True)

flight_skill = AgentSkill(
    id="Flight_Booking",
    name="Flight Booking",
    description="Search and book flights across Europe.",
    tags=["flights", "travel", "europe"],
    examples=[],
)

public_agent_card = AgentCard(
    name="Europe Travel Agent",
    description="Helps users search and book flights and hotels across Europe.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url="http://localhost:9999/", protocol_binding="JSONRPC"),
    ],
    skills=[flight_skill],
)

agent = Agent(
    client=OpenAIChatCompletionClient(),
    name="Europe Travel Agent",
    instructions="You are a helpful Europe Travel Agent.",
)

request_handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(agent, stream=True),
    task_store=InMemoryTaskStore(),
    agent_card=public_agent_card,
)

server = Starlette(
    routes=[
        *create_agent_card_routes(public_agent_card),
        *create_jsonrpc_routes(request_handler, "/"),
    ]
)

uvicorn.run(server, host="0.0.0.0", port=9999)