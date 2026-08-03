# Hands-on exercises

Eight self-checking exercises. Each file has a few `TODO`s and a set of checks at
the bottom. Run it, read the FAILs, edit, run again:

```bash
uv run python exercises/01_tool_design.py
```

Every exercise exits non-zero until all its checks pass, so you always know where
you stand. Worked answers are in `exercises/solutions/` — read them *after* you
have something failing for the right reason.

## The set

| # | File | You practise | Needs a model |
|---|------|--------------|---------------|
| 01 | `01_tool_design.py` | Docstrings and `Field` descriptions as the model's API | no |
| 02 | `02_context_provider.py` | `before_run` / `after_run` and provider state | yes |
| 03 | `03_compaction_budget.py` | Composing compaction strategies under a budget | no |
| 04 | `04_executor_contract.py` | `WorkflowContext` type parameters | no |
| 05 | `05_routing.py` | `Case` / `Default` switch-case routing | no |
| 06 | `06_fan_in.py` | Fan-out, fan-in, and what a fan-in target receives | no |
| 07 | `07_guardrail_middleware.py` | Short-circuiting middleware; function middleware | yes |
| 08 | `08_structured_output.py` | `response_format` and the failure branch | yes |

Five of the eight need no model at all — start there if `./vllm-run.sh` is still
downloading weights. The three that do need one use the same local server as the
examples.

## Which example to read first

| Exercise | Read this example first | Deck module |
|---|---|---|
| 01 | `examples/02_add_tools.py` | 3 · Tools |
| 02 | `examples/04_memory.py`, `examples/05_memory_providers.py` | 4 · Memory & context |
| 03 | `examples/08_compaction_strategies.py` | 4 · Memory & context |
| 04 | `examples/12_executor_types.py` | 6 · Workflows |
| 05, 06 | `examples/13_edge_patterns.py` | 6 · Workflows |
| 07 | `examples/16_class_based_middleware.py` | 7 · Middleware |
| 08 | `examples/19_response_format.py` | 8 · Production |

## Run them all

```bash
uv run python exercises/run_all.py            # your work
uv run python exercises/run_all.py --solutions # verify the answers still pass
```

## What each one is really teaching

- **01** — the docstring and `Field(description=...)` *are* the prompt. The check
  reads the generated JSON schema, so a vague docstring fails mechanically.
- **02** — `state` is already namespaced per provider; `before_run` injects,
  `after_run` records. Nothing else.
- **03** — `TokenBudgetComposedStrategy` always hits the budget, falling back to
  dropping whole groups (and eventually the system prompt). The skill is keeping
  *more useful conversation* at the same budget, not hitting the number.
- **04** — the context type parameters are a contract validated at `build()`.
  You will see the real `WorkflowValidationError` before you fix it.
- **05** — why switch-case beats three conditional edges: one branch wins, and a
  `Default` is mandatory so nothing falls through.
- **06** — a fan-in target receives a **list**. Getting this wrong shreds the
  merge in a way that is obvious once you see it.
- **07** — returning without awaiting `call_next()` means the model is never
  called: no tokens, no leak. Compare that with filtering output afterwards.
- **08** — `result.value` is a parsed model and can be `None`. The exercise makes
  you write the branch most demos skip.
