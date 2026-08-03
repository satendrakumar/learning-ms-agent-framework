# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A learning/training repo for the **Microsoft Agent Framework** (Python, `agent-framework` 1.13.0). It is a
collection of standalone, runnable scripts — not a library or application. There is no package to import,
no test suite, and no lint config. `main.py` is an unused scaffold stub.

## Running

Python 3.13, dependencies managed by `uv` (`uv sync`). Every script is self-contained and run directly:

```bash
uv run python examples/01_hello_agent.py
uv run python dev_ui/agent.py          # DevUI on http://localhost:8080
uv run python agent_ui/server.py       # AG-UI FastAPI server on 127.0.0.1:8888
uv run python agent_ui/client.py       # client for the above (AGUI_SERVER_URL env var)
uv run python others/02_run_agent_on_a2a.py       # A2A server on :9999
uv run python others/03_connect_remote_a2a_agent.py
```

`examples/11_graph_workflow.py` needs no model at all — use it to sanity-check the install.

## Model backend: local vLLM, not hosted OpenAI

`.env` points the OpenAI client at a **local vLLM server**, with a placeholder API key:

```
OPENAI_API_KEY=test-key
OPENAI_MODEL=Qwen/Qwen3.5-4B
OPENAI_BASE_URL=http://localhost:8000/v1
```

Start the backend first with `./vllm-run.sh` (serves `Qwen/Qwen3.5-4B`, `--max-model-len=8192`,
`--enable-auto-tool-choice --tool-call-parser qwen3_coder`). Consequences to keep in mind when writing or
editing examples here:

- Use **`OpenAIChatCompletionClient`** (Chat Completions API). `OpenAIChatClient` targets the OpenAI
  Responses API, which vLLM does not serve — see the comment in `examples/01_hello_agent.py:14`.
- The 8192-token context is small, so examples pass explicit caps:
  `options={"max_tokens": ...}` per call, or `default_options={"max_tokens": ...}` on the `Agent`.
- `examples/07_context_compaction.py` additionally expects an **Ollama** endpoint on `localhost:11434`
  for its summarizer client.

Some scripts deliberately use other providers and will not work against vLLM without edits:
`examples/17_function_based_middleware.py`, `examples/18_decorator_middleware.py` (partly), and
`others/01_app_run.py` use `FoundryChatClient` / Azure credentials and require `az login`.

## Import convention

The framework ships as a namespace package plus per-provider distributions, so the same class is reachable
two ways and the repo uses both interchangeably:

```python
from agent_framework_openai import OpenAIChatCompletionClient   # provider distribution
from agent_framework.openai import OpenAIChatCompletionClient   # namespace re-export
```

Core types (`Agent`, `tool`, `WorkflowBuilder`, `Executor`, middleware types, compaction strategies) come
from the top-level `agent_framework`. Orchestration builders live in `agent_framework.orchestrations`,
DevUI in `agent_framework.devui`, A2A in `agent_framework.a2a`, AG-UI in `agent_framework_ag_ui`.

The `agent-framework` meta-package pulls in every provider (Anthropic, Bedrock, Gemini, Mistral, Ollama,
Redis, mem0, …), so those integrations are already installed and available for new examples without
touching `pyproject.toml`. `python-dotenv` and `pydantic` are transitive deps, not declared directly.

## Layout and the concepts each directory teaches

- `examples/01`–`20` — the curriculum, numbered in teaching order (work straight through):
  - `01`–`03` agents & tools — basics/streaming, `@tool`, sessions
  - `04`–`08` memory, context & persistence — custom `ContextProvider`, layered providers
    (transcript + Mem0 + audit), `FileHistoryProvider` / `session.to_dict()`, `CompactionProvider`,
    all seven compaction strategies compared via `apply_compaction`
  - `09` MCP tool servers
  - `10`–`15` workflows — `@workflow`, graph basics, the four executor forms and `WorkflowContext`
    type parameters, the six edge primitives, supersteps/event streaming/shared run state,
    `ConcurrentBuilder`
  - `16`–`18` middleware — class, function and decorator form
  - `19`–`20` production — structured output, harness agent
- `11`, `12`, `13`, `14` run with **no model at all** — use them to verify an install or to demo when the
  model server is cold. `08` needs a model only for its summarization strategy.
- The numbering is load-bearing: it is referenced by `examples/README.md`, `exercises/README.md`, the
  deck's lab-map and demo slides, and this file. Renumbering means updating all of them.
- `exercises/01`–`08` — self-checking practice tasks, each with `TODO`s and a set of `check(...)`
  assertions from `exercises/_check.py`; worked answers in `exercises/solutions/`. The contract is that
  **every exercise exits non-zero until finished and every solution exits zero** — `exercises/run_all.py`
  (`--solutions`, `--offline`) verifies both, so run it after touching either side. Exercises 02, 07 and
  08 need the model server; the other five are pure Python.
- `others/` — hosting and agent-to-agent: `AgentFunctionApp` (Azure Functions), A2A server via
  Starlette + `A2AExecutor`, and an `A2AAgent` client that discovers a remote agent card.
- `agent_ui/` — AG-UI protocol: FastAPI server (`add_agent_framework_fastapi_endpoint`) and a matching
  `AGUIChatClient` console client.
- `dev_ui/` — one-file DevUI launcher (`serve(entities=[agent], auth_enabled=False)`).

## Conventions in the example code

Each script: `load_dotenv()` at module top, an `async def main()`, and `asyncio.run(main())` under
`if __name__ == "__main__":`. Agents that own resources (MCP tools, middleware examples) are used as async
context managers. Tools are declared `@tool(approval_mode="never_require")` for brevity — the comments
flag that production code should use `"always_require"`.

## The training deck

`slides/build_deck.py` generates `slides/Microsoft-Agent-Framework-Training.pptx` (61 slides) from scratch
with `python-pptx` — the deck is a build artifact, so edit the script, never the `.pptx`:

```bash
uv run python slides/build_deck.py
```

The script is self-contained: a `Deck` helper (dark theme constants, a regex syntax highlighter for code
panels, card/callout/chip/arrow primitives) followed by one block per slide. Every slide carries speaker
notes. Layout is absolute inches on a 13.333×7.5 canvas, so it warns at build time when a callout or card
lands on top of a code panel — treat any `WARN` line as a real overlap and move the shape.

Slide content cites example filenames directly; if you rename anything under `examples/`, update the deck
too — the lab-map slide and the demo slides both list paths. `.sessions/` is a local store written by
example 06 and is gitignored. To check rendering, export with PowerPoint and read the PDF:

```bash
osascript -e 'tell application "Microsoft PowerPoint"
  open POSIX file "<abs>/slides/Microsoft-Agent-Framework-Training.pptx"
  save active presentation in POSIX file "<abs>/slides/preview.pdf" as save as PDF
  close active presentation saving no
end tell'
```