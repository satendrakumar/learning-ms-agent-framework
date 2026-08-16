# Deploying agents to production — the recommended way

Everything else in this repo runs an agent *inside your own process*. In
production you want the opposite: the agent as a **standalone service** behind
a standard protocol, so clients need nothing but an HTTP client.

The Agent Framework's answer is the hosting package
(`agent-framework-foundry-hosting`): wrap your agent in a
`ResponsesHostServer` and it becomes a web service that speaks the **OpenAI
Responses API** — the native protocol of Microsoft Foundry **Hosted Agents**,
and one every OpenAI SDK already understands.

```python
from agent_framework.foundry import ResponsesHostServer

app = ResponsesHostServer(agent)
app.run()          # 0.0.0.0:$PORT (default 8088)
```

## Files

| File | What it shows |
|------|---------------|
| `server.py` | An agent with a tool, wrapped in `ResponsesHostServer` |
| `workflow_server.py` | The alternative for **multi-agent workflows**: `workflow.as_agent()` behind the same host |
| `client.py` | Calling it with the plain `openai` SDK — one-shot, multi-turn, streaming |
| `Dockerfile` | The container image you ship |

## Run it

```bash
# Terminal 1 — the model (as for the rest of the lab)
./vllm-run.sh

# Terminal 2 — the agent service
uv run python agent_deployment/foundry_server.py

# Terminal 3 — probe it, then talk to it
curl http://localhost:8088/readiness
uv run python agent_deployment/client.py
```

## What the host gives you

- **`POST /responses`** — the OpenAI Responses API: one-shot, streaming
  (SSE), and multi-turn via `previous_response_id`. **The server stores the
  conversation**; clients never re-send history.
- **`GET /readiness`** — the health probe Kubernetes / Container Apps /
  Foundry point their checks at.
- **Graceful shutdown** on SIGTERM — in-flight requests drain before exit.
- **OpenTelemetry** — instrumentation is on by default; set
  `OTEL_EXPORTER_OTLP_ENDPOINT` to export traces and metrics.

Two rules the constructor enforces, because the process may be recycled
between requests:

1. No `HistoryProvider` with `load_messages=True` — history is the host's job.
2. No context providers that keep state in memory — externalise state
   (Redis, Cosmos, Mem0 — see `examples/05_memory_providers.py`).

> On startup off-Azure you'll see one connect-timeout trace for
> `169.254.169.254` — that's the Azure VM metadata probe failing, which is
> expected and harmless outside Azure.

## Ship it

```bash
docker build -f agent_deployment/Dockerfile -t support-agent .
docker run -p 8088:8088 --env-file .env support-agent
```

That image deploys unchanged to:

- **Microsoft Foundry (Hosted Agents)** — the recommended target. The
  platform manages conversation history, session storage and workflow
  checkpoints, and fronts the same Responses endpoint with auth.
- **Any container platform** — AKS, Azure Container Apps, etc. Point the
  liveness probe at `/readiness`, put your gateway's auth in front, and
  supply `OPENAI_*` credentials as secrets (never baked into the image).

## Deploying multi-agent workflows

A workflow deploys exactly like a single agent: call `.as_agent()` on it and
give the result to the same host. `workflow_server.py` ships a three-agent
support pipeline (triage → resolver → quality) this way:

```python
workflow = SequentialBuilder(participants=[triage, resolver, quality]).build()
app = ResponsesHostServer(workflow.as_agent(name="SupportPipeline"))
```

```bash
uv run python agent_deployment/workflow_server.py                          # port 8090
AGENT_HOST_URL=http://localhost:8090 uv run python agent_deployment/client.py
```

Callers can't tell it's a workflow — one Responses endpoint, one reply —
but each request runs the whole pipeline. This works for any workflow shape
from the lab: `SequentialBuilder`, `ConcurrentBuilder`, `GroupChatBuilder`,
`HandoffBuilder`, `MagenticBuilder`, `@workflow` functions, or hand-built
graphs (examples 10–15).

One extra rule for workflows: **don't configure checkpoint storage
yourself** — the host owns it (locally under `.checkpoints/`; on Foundry the
platform persists checkpoints between turns, which is how a hosted workflow
can pause for input and resume later).

If a workflow runs for minutes/hours and must survive process restarts
*mid-run*, use the durable alternative instead: Azure Functions hosting with
durable orchestrations (`others/01_app_run.py`), where every agent step is
checkpointed by the Durable Task framework and replayed after a crash.

## When to use the other hosting options in this repo

| Option | Where | Use it for |
|--------|-------|-----------|
| `ResponsesHostServer` | here | **Default for production** — serve an agent to apps and other services |
| Azure Functions + durable orchestrations | `others/01_app_run.py` | Long-running, resumable multi-agent orchestrations |
| A2A server | `others/02_run_agent_on_a2a.py` | Interop: let *third-party* agents discover and call yours |
| AG-UI server | `agent_ui/` | Driving your own chat frontend |
| DevUI | `dev_ui/` | Development only — never expose it |

Docs: https://learn.microsoft.com/agent-framework
