# Hands-on examples — Microsoft Agent Framework (Python)

Runnable versions of the code shown in the training deck
(`../slides/Microsoft-Agent-Framework-Training.pptx`). Numbered in teaching order — work straight through.

## Setup

```bash
uv sync                # from the repo root
./vllm-run.sh          # start the local model server (first run downloads weights)
```

The examples read `OPENAI_API_KEY`, `OPENAI_MODEL` and `OPENAI_BASE_URL` from `.env`
and default to a **local vLLM server** on `http://localhost:8000/v1`, so no hosted
API key is needed. To point at a real provider, change `.env` — or swap the client:

```python
from agent_framework_openai import OpenAIChatCompletionClient  # default (Chat Completions)
from agent_framework.azure import AzureOpenAIChatClient         # Azure OpenAI
from agent_framework.foundry import FoundryChatClient           # Azure AI Foundry
```

> Use `OpenAIChatCompletionClient`, not `OpenAIChatClient`. The latter targets the
> OpenAI Responses API, which vLLM does not serve — you get a 404 that looks like
> an auth error.

## The lab

**Foundations**

| # | File | Concept |
|---|------|---------|
| 01 | `01_hello_agent.py` | Create & run an agent; streaming, per-call options |
| 02 | `02_add_tools.py` | Function tools with `@tool`, typed args, approvals |
| 03 | `03_multi_turn.py` | Multi-turn conversation with a session |

**Memory, context & persistence**

| # | File | Concept |
|---|------|---------|
| 04 | `04_memory.py` | A custom `ContextProvider` (`before_run` / `after_run`) |
| 05 | `05_memory_providers.py` | Layering providers: transcript + Mem0 + audit trail |
| 06 | `06_persistent_history.py` | `FileHistoryProvider` and `session.to_dict()` round-trip |
| 07 | `07_context_compaction.py` | `CompactionProvider` wired into a live agent |
| 08 | `08_compaction_strategies.py` | All seven compaction strategies side by side |

**Tools beyond your process**

| # | File | Concept |
|---|------|---------|
| 09 | `09_mcp_docs_agent.py` | Connect an MCP tool server (Microsoft Learn) |

**Workflows**

| # | File | Concept |
|---|------|---------|
| 10 | `10_functional_workflow.py` | Two-agent functional workflow (`@workflow`) |
| 11 | `11_graph_workflow.py` | Graph workflow: executors + edges |
| 12 | `12_executor_types.py` | Four ways to declare an executor; `WorkflowContext` types |
| 13 | `13_edge_patterns.py` | chain · conditional · fan-out/in · switch-case · multi-select |
| 14 | `14_workflow_execution.py` | Supersteps, event streaming, shared run state |
| 15 | `15_concurrent_orchestration.py` | Concurrent fan-out/fan-in orchestration |

**Middleware**

| # | File | Concept |
|---|------|---------|
| 16 | `16_class_based_middleware.py` | Class-based middleware: guardrail + timing |
| 17 | `17_function_based_middleware.py` | Function-based middleware (**needs `az login`**) |
| 18 | `18_decorator_middleware.py` | `@agent_middleware` / `@function_middleware` |

**Production**

| # | File | Concept |
|---|------|---------|
| 19 | `19_response_format.py` | Structured output via `response_format` |
| 20 | `20_harness_agent.py` | Harness agent with a planning loop |

```bash
uv run python examples/01_hello_agent.py
```

### Runs with no model at all

`11`, `12`, `13` and `14` are pure Python — start there if the model server is
still warming up, or to check the install:

```bash
uv run python examples/11_graph_workflow.py
```

Example `08` runs six of its seven strategies without a model (only summarization
needs one). Example `07` expects a second, cheaper summariser model on
`http://localhost:11434/v1` (Ollama).

## Practice

Reading is not the same as writing. `../exercises/` has eight self-checking tasks
that make you build the thing yourself — five need no model:

```bash
uv run python exercises/01_tool_design.py     # then follow the FAILs
uv run python exercises/run_all.py --offline
```

`exercises/README.md` maps each task back to the example above that it drills.

## Stretch goals

- Launch **DevUI** to chat with your agents in a browser:
  `uv run python dev_ui/agent.py`
- Rebuild example 10 with `SequentialBuilder` or `HandoffBuilder`.
- Add `approval_mode="always_require"` to a tool and observe the approval flow.
- Set `MEM0_API_KEY` and re-run example 05 to add semantic memory.

## Reference

- Docs: https://learn.microsoft.com/agent-framework
- Executors: https://learn.microsoft.com/agent-framework/workflows/executors
- Samples: https://github.com/microsoft/agent-framework/tree/main/python/samples
