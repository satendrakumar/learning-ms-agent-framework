# Hands-on examples — Microsoft Agent Framework (Python)

Runnable versions of the code shown in the training deck
(`../slides/Microsoft-Agent-Framework-Training.pptx`). Work through them in order.

## Setup

```bash
# From the repo root
uv add agent-framework                 # install the framework
cp examples/.env.example examples/.env # add your OPENAI_API_KEY (or Azure/Foundry)
```

The examples default to **OpenAI** via `OpenAIChatClient`, which reads
`OPENAI_API_KEY` from your environment / `.env`. To use Azure OpenAI or Azure AI
Foundry, swap the client import (see comments in `.env.example`):

```python
# from agent_framework.openai import OpenAIChatClient      # default
# from agent_framework.azure  import AzureOpenAIChatClient  # Azure OpenAI
# from agent_framework.foundry import FoundryChatClient      # Azure AI Foundry
```

## The lab (run each one)

| # | File | Concept |
|---|------|---------|
| 1 | `01_hello_agent.py` | Create & run an agent; non-streaming + streaming |
| 2 | `02_add_tools.py` | Function tools with `@tool` and type hints |
| 3 | `03_multi_turn.py` | Multi-turn memory with a session |
| 4 | `04_memory.py` | Long-term memory via a `ContextProvider` |
| 5 | `05_mcp_docs_agent.py` | Connect an MCP tool server (Microsoft Learn) |
| 6 | `06_functional_workflow.py` | Two-agent functional workflow (`@workflow`) |
| 7a | `07_graph_workflow.py` | Graph workflow: executors + edges (no model needed) |
| 7b | `08_concurrent_orchestration.py` | Concurrent fan-out/fan-in orchestration |

```bash
uv run python examples/01_hello_agent.py
```

> `07_graph_workflow.py` runs without any API key — start there if you haven't
> set up credentials yet.

## Stretch goals

- Launch **DevUI** to chat with your agents in a browser:
  `uv run python -c "from agent_framework.devui import serve; serve(entities_dir='examples', auto_open=True)"`
- Rebuild example 6 with `SequentialBuilder` or `HandoffBuilder`.
- Add `approval_mode="always_require"` to a tool and observe the approval flow.

## Reference

- Docs: https://learn.microsoft.com/agent-framework
- Samples: https://github.com/microsoft/agent-framework/tree/main/python/samples
