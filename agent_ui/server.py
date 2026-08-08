"""AG-UI server example."""

import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

chat_client = OpenAIChatCompletionClient()

# Create the AI agent
agent = Agent(
    name="AGUIAssistant",
    instructions="You are a helpful assistant.",
    client=chat_client,
)

# Create FastAPI app
app = FastAPI(title="AG-UI Server")

# Register the AG-UI endpoint
add_agent_framework_fastapi_endpoint(app, agent, "/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8888)