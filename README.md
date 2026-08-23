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
agent_deployment/ recommended agent deployment: Responses API host + Dockerfile
others/     Azure Functions hosting, A2A server and client
vllm-run.sh the local model server the lab runs against
```

## What is Microsoft Agent Framework?

An open-source SDK + runtime (Python & .NET) for building production AI agents
and multi-agent workflows. It unifies **AutoGen** (simple multi-agent
abstractions) and **Semantic Kernel** (enterprise state, telemetry, connectors),
and adds graph-based **workflows** for reliable orchestration.

## Prerequisites

Set these up before the workshop so the first session isn't spent installing:

- **Python 3.13+** — the project requires it (`requires-python = ">=3.13"`).
- **[uv](https://docs.astral.sh/uv/)** — used for all installs and script runs
  (`uv sync`, `uv run ...`). Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git** — to clone this repository.
- **A model endpoint** (any one of):
  - A machine with an **NVIDIA GPU** (~10 GB VRAM free) to run
    `./vllm-run.sh`, which serves `Qwen/Qwen3.5-4B` locally via vLLM.
    First run downloads ~8 GB of weights — do this on good Wi-Fi beforehand.
  - **Docker with the NVIDIA container runtime** — the containerised variant
    in `vllm-run.sh`.
  - Any **OpenAI-compatible endpoint** (hosted key works too): point
    `OPENAI_BASE_URL`, `OPENAI_MODEL`, and `OPENAI_API_KEY` at it in `.env`.
- **Graphviz** (system package) — needed for workflow visualisation in the
  workflow examples: `brew install graphviz` (macOS) or
  `apt install graphviz` (Linux).

Verify the setup with the offline example — it needs no model server:

```bash
uv sync
uv run python examples/11_graph_workflow.py
```

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
