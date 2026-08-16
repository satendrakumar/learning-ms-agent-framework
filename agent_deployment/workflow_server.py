""" hosting — deploying a MULTI-AGENT WORKFLOW as one service.

The alternative to hosting a single agent (foundry_server.py): build a workflow of
several agents, call `.as_agent()` on it, and hand that to the same
`ResponsesHostServer`. To callers it is indistinguishable from a single
agent — one Responses endpoint — but every request runs the whole pipeline.

Any workflow shape works: SequentialBuilder / ConcurrentBuilder /
GroupChatBuilder / HandoffBuilder / MagenticBuilder, a @workflow function,
or a hand-built graph (examples 10-15). For a WorkflowAgent the host also
takes over CHECKPOINT storage — so the workflow must not configure its own
checkpointing; on Foundry the platform persists checkpoints between turns.

Run:   uv run python agent_deployment/workflow_server.py       # port 8090
Call:  AGENT_HOST_URL=http://localhost:8090 uv run python agent_deployment/client.py

For long-running workflows that must survive process restarts mid-run,
the other alternative is durable hosting on Azure Functions
(agent-framework-azurefunctions) — see others/01_app_run.py.
"""

import os

from agent_framework import Agent
from agent_framework.foundry import ResponsesHostServer
from agent_framework.orchestrations import SequentialBuilder
from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

client = OpenAIChatCompletionClient()

triage = Agent(
    client=client,
    name="TriageAgent",
    instructions=(
        "Classify the customer message (billing / shipping / product / other) "
        "and restate the problem in one sentence."
    ),
    default_options={"max_tokens": 200},
)
resolver = Agent(
    client=client,
    name="ResolverAgent",
    instructions="Draft a short, concrete resolution for the triaged issue.",
    default_options={"max_tokens": 300},
)
quality = Agent(
    client=client,
    name="QualityAgent",
    instructions=(
        "Rewrite the draft as the final customer reply: polite, brief, "
        "no internal jargon. Output only the reply."
    ),
    default_options={"max_tokens": 300},
)

# triage -> resolver -> quality, each seeing the conversation so far.
workflow = SequentialBuilder(participants=[triage, resolver, quality]).build()

# The whole pipeline, packaged as one agent.
app = ResponsesHostServer(workflow.as_agent(name="SupportPipeline"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8090")))
