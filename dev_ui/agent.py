from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_framework.devui import serve
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv(verbose=True)

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F and sunny"

# Create your agent
agent = Agent(
    name="WeatherAgent",
    client=OpenAIChatCompletionClient(),
    tools=[get_weather]
)

# Launch DevUI
serve(entities=[agent], auto_open=True,auth_enabled=False)
# Opens browser to http://localhost:8080