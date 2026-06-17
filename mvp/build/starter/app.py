"""Minimal, deployable Claude app. Fork this and build your product on top.

Local:
    pip install -r starter/requirements.txt
    export ANTHROPIC_API_KEY=...            # from console.anthropic.com
    uvicorn starter.app:app --reload        # http://localhost:8000

Deploy: see starter/README.md (Docker, Fly.io, or Render).
"""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Default to the cheap junior rung: a simple chat endpoint only needs a lookup.
# Override CLAUDE_MODEL (e.g. claude-sonnet-4-6) to climb the ladder for harder work.
MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")
SYSTEM = os.environ.get(
    "CLAUDE_SYSTEM",
    "You are a concise, honest assistant for a startup. If you do not know "
    "something, say so plainly instead of inventing an answer.",
)

HERE = Path(__file__).parent
app = FastAPI(title="claude-starter")


class Turn(BaseModel):
    message: str


@app.get("/health")
def health() -> dict:
    return {"ok": True, "model": MODEL}


@app.get("/")
def home() -> FileResponse:
    return FileResponse(HERE / "static" / "index.html")


@app.post("/api/chat")
def chat(turn: Turn) -> JSONResponse:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return JSONResponse(
            {"error": "Set ANTHROPIC_API_KEY first. Get one at console.anthropic.com."},
            status_code=503,
        )
    client = anthropic.Anthropic()
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM,
            messages=[{"role": "user", "content": turn.message}],
        )
    except anthropic.RateLimitError:
        return JSONResponse({"error": "Rate limited. Retry in a moment."}, status_code=429)
    except (anthropic.APIStatusError, anthropic.APIConnectionError):
        # Overload (529) or a transient upstream error should not 500 a forked app.
        return JSONResponse({"error": "The model is busy. Retry shortly."}, status_code=503)
    reply = "".join(b.text for b in resp.content if b.type == "text")
    return JSONResponse(
        {
            "reply": reply,
            "model": MODEL,
            "usage": {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
        }
    )
