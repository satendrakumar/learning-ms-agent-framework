# Learning: Microsoft Agent Framework

Training material for onboarding engineers to the **Microsoft Agent Framework**
(Python). Includes a slide deck and a runnable hands-on lab.

## Contents

```
slides/     Microsoft-Agent-Framework-Training.pptx  (61 slides, speaker notes)
examples/   01..20 runnable code (the lab, in teaching order), README.md
exercises/  01..08 self-checking practice tasks + solutions/, README.md
dev_ui/     one-file DevUI launcher
agent_ui/   AG-UI protocol server + console client
others/     Azure Functions hosting, A2A server and client
vllm-run.sh the local model server the lab runs against
```

## What is Microsoft Agent Framework?

An open-source SDK + runtime (Python & .NET) for building production AI agents
and multi-agent workflows. It unifies **AutoGen** (simple multi-agent
abstractions) and **Semantic Kernel** (enterprise state, telemetry, connectors),
and adds graph-based **workflows** for reliable orchestration.

## Quick start

```bash
uv sync                # install deps
cp .env.example .env   # defaults to a local vLLM server — no hosted key needed
./vllm-run.sh          # start the model server (first run downloads weights)

# 11 needs no model at all — start there to check the install:
uv run python examples/11_graph_workflow.py
uv run python examples/01_hello_agent.py

# Then practise. Each exercise self-checks and tells you what is missing:
uv run python exercises/01_tool_design.py
uv run python exercises/run_all.py --offline   # the 5 that need no model

# Rebuild the slide deck:
uv run python slides/build_deck.py
```

`examples/README.md` is the lab walkthrough; `exercises/README.md` maps each
practice task to the example and deck module it belongs to.

## The training path

1. Why a framework — the gap between a completion and an agent
2. Core concepts — chat clients, agents, sessions, the run lifecycle
3. Tools — typed functions, the call loop, approval gates
4. Memory & context — sessions, providers, persistence, compaction
5. MCP — standardised tool servers
6. Workflows — executors, edges, execution, orchestration patterns
7. Middleware — guardrails and cross-cutting concerns
8. A2A Protocol — Agent to Agent communication

Each module has runnable examples in `examples/` and at least one exercise in
`exercises/`.

## References

- Docs: https://learn.microsoft.com/agent-framework
- GitHub: https://github.com/microsoft/agent-framework
- PyPI: https://pypi.org/project/agent-framework
