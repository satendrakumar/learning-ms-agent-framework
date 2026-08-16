"""Production hosting — the recommended way to deploy an agent.

Wrap the agent in `ResponsesHostServer` (agent-framework-foundry-hosting).
That turns it into a standalone HTTP service speaking the **OpenAI Responses
API** — the same protocol every OpenAI SDK already understands — plus a
`GET /readiness` probe for orchestrators.

The same image runs unchanged in three places:

  1. Locally:            python agent_deployment/foundry_server.py
  2. Any container host: docker build … && docker run …  (AKS, Container Apps)
  3. Microsoft Foundry:  deploy the image as a **Hosted Agent** — the platform
                         then manages conversation history, sessions and
                         workflow checkpoints for you.

Two hosting rules the server enforces (see the constructor docs):
  - no HistoryProvider with load_messages=True — history belongs to the host
  - no in-memory context providers — the process may be recycled between calls
"""

import os
from random import randint
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.foundry import ResponsesHostServer
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


@tool(approval_mode="never_require")
def get_order_status(
    order_id: Annotated[str, Field(description="The order id, e.g. ORD-1042.")],
) -> str:
    """Look up the shipping status of an order."""
    statuses = ["packed", "shipped", "out for delivery", "delivered"]
    return f"Order {order_id} is {statuses[randint(0, 3)]}."


agent = Agent(
    client=OpenAIChatCompletionClient(),
    name="SupportAgent",
    instructions=(
        "You are a customer-support agent. Use the get_order_status tool "
        "when asked about an order. Keep answers brief."
    ),
    tools=[get_order_status],
)

app = ResponsesHostServer(agent)

if __name__ == "__main__":
    # Binds 0.0.0.0; port comes from $PORT (the contract container hosts use),
    # defaulting to 8088. Telemetry is on by default — point
    # OTEL_EXPORTER_OTLP_ENDPOINT at your collector to export traces/metrics.
    app.run( host="0.0.0.0", port= 8088)
