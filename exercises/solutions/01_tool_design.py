"""SOLUTION — 01 — Tool design.  (module 3 · pairs with examples/02_add_tools.py)  (worked answer)

The model never sees your implementation. It sees the name, the docstring, and
the JSON schema generated from your type hints. This exercise checks that
schema, so it needs no model at all.

YOUR JOB
  TODO 1  annotate both parameters with Annotated[..., Field(description=...)]
  TODO 2  write a docstring that tells the model WHEN to reach for this tool
  TODO 3  return a string that carries its units — "231.50" is ambiguous,
          "231.50 USD" is not

Run:  uv run python exercises/01_tool_design.py
"""

from typing import Annotated  # noqa: F401  (you will need this)

from agent_framework import tool
from pydantic import Field  # noqa: F401  (and this)

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))

from _check import check, report

PRICES = {"AAPL": 231.50, "MSFT": 468.20, "NVDA": 174.05}
RATES = {"USD": 1.0, "EUR": 0.92, "INR": 88.40}


@tool(approval_mode="never_require")
def get_stock_price(
    symbol: Annotated[str, Field(description="Ticker symbol, e.g. AAPL or MSFT.")],
    currency: Annotated[str, Field(description="ISO 4217 code to quote in, e.g. USD or EUR.")],
) -> str:
    """Look up the latest share price for a ticker, quoted in a given currency.

    Use this whenever the user asks what a stock costs or is worth.
    """
    price = PRICES.get(symbol.upper())
    if price is None:
        # Returning a readable string (rather than raising) lets the model recover.
        return f"No price found for {symbol!r}. Known symbols: {', '.join(PRICES)}."
    converted = price * RATES.get(currency.upper(), 1.0)
    # Units belong in the value. "231.50" is ambiguous; "231.50 USD" is not.
    return f"{symbol.upper()}: {converted:.2f} {currency.upper()}"


def main() -> None:
    print(__doc__.splitlines()[0])
    schema = get_stock_price.parameters()
    props = schema.get("properties", {})

    check("tool is registered as a FunctionTool", type(get_stock_price).__name__ == "FunctionTool")
    check("tool name is get_stock_price", get_stock_price.name == "get_stock_price")

    described = get_stock_price.description or ""
    check(
        "docstring says when to use the tool (>= 25 chars, not 'TODO')",
        len(described.strip()) >= 25 and "todo" not in described.lower(),
        "The docstring IS the prompt. 'Gets data' is not enough.",
    )

    check(
        "both parameters appear in the schema",
        set(props) == {"symbol", "currency"},
        f"schema properties were {sorted(props)}",
    )
    missing_desc = [n for n, spec in props.items() if not spec.get("description")]
    check(
        "every parameter has a description",
        not missing_desc,
        f"no description for: {missing_desc or '-'} — use Annotated[str, Field(description=...)]",
    )
    untyped = [n for n, spec in props.items() if not spec.get("type")]
    check("every parameter has a type", not untyped, f"untyped: {untyped or '-'}")

    result = get_stock_price.func("AAPL", "USD")
    check(
        "result carries its units",
        "USD" in result,
        f"got {result!r} — a bare number is ambiguous to the model and to the caller",
    )
    unknown = get_stock_price.func("XXXX", "USD")
    check(
        "unknown symbol returns a recoverable message, not an exception",
        isinstance(unknown, str) and "XXXX" in unknown,
    )
    report()


if __name__ == "__main__":
    main()
