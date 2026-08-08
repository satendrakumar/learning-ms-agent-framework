import os
from agent_framework.azure import AgentFunctionApp
from agent_framework.openai import OpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv(verbose=True)

# Create an AI agent following the standard Microsoft Agent Framework pattern
agent = OpenAIChatCompletionClient(
).as_agent(
    instructions="You are good at telling jokes.",
    name="Joker"
)

# Configure the function app to host the agent with durable thread management
# This automatically creates HTTP endpoints and manages state persistence

app = AgentFunctionApp(agents=[agent])


@app.orchestration_trigger(context_name="context")
def my_orchestration(context):
    writer = app.get_agent(context, "WeatherAgent")
    session = writer.create_session()
    forecast_task = writer.run("What's the forecast?", session=session)
    forecast = yield forecast_task
    return forecast