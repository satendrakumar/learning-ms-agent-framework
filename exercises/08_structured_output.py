"""Exercise 08 — Typed data across a boundary.  (module 8 · pairs with examples/19_response_format.py)

Turn a free-text bug report into a typed object your downstream service can
consume. Prose is for humans; anything crossing a service boundary should be
typed and validated.

YOUR JOB
  TODO 1  define the Ticket model: summary (str), severity (one of sev1/sev2/sev3),
          component (str), needs_oncall (bool)
  TODO 2  pass it as response_format so the model is constrained to that shape
  TODO 3  handle the failure branch — parsing can and does fail on small models

Needs the local model server (./vllm-run.sh).
Run:  uv run python exercises/08_structured_output.py
"""

import asyncio
from typing import Literal  # noqa: F401  (you will need this)

from agent_framework_openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import BaseModel

from _check import check, note, report

load_dotenv()

REPORT = (
    "Checkout is returning HTTP 500 for about a third of users since the 14:00 "
    "deploy. The payments service is throwing connection timeouts to the card "
    "vault. Revenue is affected right now and nobody is looking at it yet."
)


# TODO 1: describe the shape you want back.
class Ticket(BaseModel):
    """A triaged bug report."""


async def main() -> None:
    print(__doc__.splitlines()[0])

    fields = set(getattr(Ticket, "model_fields", {}))
    check(
        "Ticket declares all four fields",
        fields == {"summary", "severity", "component", "needs_oncall"},
        f"model_fields were {sorted(fields)}",
    )

    agent = OpenAIChatCompletionClient().as_agent(
        name="TriageAgent",
        instructions=(
            "You triage incident reports. sev1 means revenue or safety impact right "
            "now, sev2 means degraded, sev3 means minor."
        ),
    )

    result = await agent.run(
        f"Triage this report:\n{REPORT}",
        # TODO 2: add "response_format": Ticket alongside max_tokens
        options={"max_tokens": 400},
    )

    ticket = result.value
    if ticket is None:
        # TODO 3: this is the branch you must not skip in production. Decide
        # whether an unparseable response is a retry or an error, then say so.
        check("model returned a parsed Ticket", False,
              f"result.value was None. Raw text: {(result.text or '')[:120]!r}. "
              "Did you pass response_format?")
        report()
        return

    note(f"parsed: {ticket!r}")
    check("result.value is a Ticket instance", isinstance(ticket, Ticket))
    check("summary is populated", bool(str(getattr(ticket, "summary", "")).strip()))
    check(
        "severity is one of the three allowed values",
        str(getattr(ticket, "severity", "")) in {"sev1", "sev2", "sev3"},
        f"got {getattr(ticket, 'severity', None)!r} — constrain it with Literal[...]",
    )
    check("component is populated", bool(str(getattr(ticket, "component", "")).strip()))
    check(
        "needs_oncall is a real bool, not a string",
        isinstance(getattr(ticket, "needs_oncall", None), bool),
    )
    report()


if __name__ == "__main__":
    asyncio.run(main())
