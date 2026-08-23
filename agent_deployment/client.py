"""Client for the agent_deployment host — plain OpenAI SDK, no framework needed.

The hosted agent speaks the OpenAI Responses API, so any Responses-capable
client works: the openai SDK (below), curl, or another agent. This is the
point of the recommended deployment — consumers do not need
agent-framework installed at all.

Start the server first:  python agent_deployment/foundry_server.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("AGENT_HOST_URL", "http://localhost:8090"),
    api_key="not-used",  # auth is the platform's job (Foundry / your gateway)
)


def main() -> None:
    # 1. One-shot request. `model` is ignored by the host — the deployed
    #    agent already knows which model it runs on.
    first = client.responses.create(
        model="hosted-agent",
        input="Where is order ORD-1042?",
    )
    print(f"Agent: {first.output_text}\n")

    # 2. Multi-turn: chain on previous_response_id. The HOST stores the
    #    conversation — the client never re-sends history.
    follow_up = client.responses.create(
        model="hosted-agent",
        input="And is that later than order ORD-7?",
        previous_response_id=first.id,
    )
    print(f"Agent: {follow_up.output_text}\n")

    # 3. Streaming: the host relays the agent's stream as Responses events.
    print("Agent (streaming): ", end="", flush=True)
    stream = client.responses.create(
        model="hosted-agent",
        input="Summarise both orders in one sentence.",
        previous_response_id=follow_up.id,
        stream=True,
    )
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
