from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Any

from agent_framework import (
    Agent,
    FileHistoryProvider,
    FileSessionStore,
    ResponseStream,
    tool,
)
from agent_framework_hosting import AgentState
from agent_framework_openai import OpenAIChatClient
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

SESSIONS_DIR = BASE_DIR / "storage" / "sessions"
SNAPSHOTS_DIR = SESSIONS_DIR / "snapshots"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

@tool(approval_mode="never_require")
def lookup_weather(
    location: Annotated[
        str,
        "The city to look up weather for.",
    ],
) -> str:
    """Return a deterministic weather report for a city."""

    high_temp = 5 + (sum(location.encode("utf-8")) % 21)

    reports = {
        "Seattle": f"Seattle is rainy with a high of {high_temp}°C.",
        "Amsterdam": f"Amsterdam is cloudy with a high of {high_temp}°C.",
        "Tokyo": f"Tokyo is clear with a high of {high_temp}°C.",
    }

    return reports.get(
        location,
        f"{location} is sunny with a high of {high_temp}°C.",
    )


def create_agent() -> Agent:
    """Create the weather agent."""
    return Agent(
        client=OpenAIChatClient(),
        name="WeatherAgent",
        instructions=(
            "You are a friendly weather assistant. "
            "Use the lookup_weather tool for any weather question "
            "and answer in one short sentence."
        ),
        tools=[lookup_weather],
        context_providers=[
            FileHistoryProvider(SESSIONS_DIR),
        ],
        default_options={
            "store": False,
        },
    )

app = FastAPI(
    title="Agent Framework API",
    description="Simple FastAPI + Agent Framework service",
    version="1.0.0",
)

state = AgentState(
    create_agent,
    session_store=FileSessionStore(SNAPSHOTS_DIR),
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = False

@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }

@app.post("/chat", response_model=None)
async def chat(
    request: ChatRequest,
) -> JSONResponse | StreamingResponse:
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="message cannot be empty",
        )
    agent = await state.get_target()
    session_id = request.session_id or str(uuid.uuid4())
    session = await state.get_or_create_session(session_id)
    # Streaming
    if request.stream:

        stream = agent.run(
            request.message,
            stream=True,
            session=session,
        )

        if not isinstance(stream, ResponseStream):
            raise HTTPException(
                status_code=500,
                detail="Agent did not return a response stream",
            )

        async def generate() -> AsyncIterator[str]:
            try:
                async for event in stream:
                    yield f"data: {event}\n\n"

            finally:
                # Persist session after stream completes.
                await state.set_session(
                    session_id,
                    session,
                )

                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
    # Normal response
    result = await agent.run(
        request.message,
        session=session,
    )

    await state.set_session(
        session_id,
        session,
    )

    return JSONResponse(
        {
            "response": result.text,
            "session_id": session_id,
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)

"""
curl -X POST "http://localhost:8001/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather in Tokyo?"
  }'
"""