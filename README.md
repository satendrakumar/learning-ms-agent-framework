# Learning: Microsoft Agent Framework

Training material for onboarding engineers to the **Microsoft Agent Framework**
(Python). Includes a slide deck and a runnable hands-on lab.

## Contents

```
slides/     build_deck.py  → generates the .pptx training deck
            Microsoft-Agent-Framework-Training.pptx  (39 slides)
examples/   01..08 runnable code (the lab), README.md, .env.example
```

## What is Microsoft Agent Framework?

An open-source SDK + runtime (Python & .NET) for building production AI agents
and multi-agent workflows. It unifies **AutoGen** (simple multi-agent
abstractions) and **Semantic Kernel** (enterprise state, telemetry, connectors),
and adds graph-based **workflows** for reliable orchestration.

## Quick start

```bash
uv sync                                 # install deps (agent-framework, python-pptx)
cp examples/.env.example examples/.env  # add your OPENAI_API_KEY

# Run the lab (07 needs no API key — start there):
uv run python examples/07_graph_workflow.py
uv run python examples/01_hello_agent.py

# Rebuild the slide deck:
uv run python slides/build_deck.py
```

See `examples/README.md` for the full lab walkthrough.

## The training path

1. Foundations — what an agent is, why a framework
2. Core building blocks — chat clients, agents, tools, sessions
3. Hands-on — first agent, tools, streaming, memory
4. Tools & MCP
5. Sessions & context providers (memory)
6. Workflows — functional (`@workflow`) & graph (`WorkflowBuilder`)
7. Multi-agent orchestration — sequential, concurrent, handoff, group chat, Magentic
8. Production — middleware, observability, DevUI, hosting

## References

- Docs: https://learn.microsoft.com/agent-framework
- GitHub: https://github.com/microsoft/agent-framework
- PyPI: https://pypi.org/project/agent-framework
