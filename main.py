"""
Nexus Backend

Single-file backend.

Architecture
------------
Browser
    │
HTTP / WebSocket
    │
FastAPI
    │
Application
    │
Agent
    │
RAG
    │
Memory
    │
Tools
    │
Local LLM
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

import tempfile
import os

# Force Unsloth to build its temporary files inside the system temp directory
os.environ["UNSLOTH_CACHE_DIR"] = os.path.join(tempfile.gettempdir(), "unsloth_compiled_cache")

from app.core.app import container
from app.graph.workflow import build_graph
from langchain_core.messages import HumanMessage

# ============================================================
# Application Lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and shutdown the application.
    """

    print()

    print("=" * 80)
    print("Starting Nexus...")
    print("=" * 80)

    container.initialize()

    print("Container initialize success!")

    app.state.workflow = build_graph()

    #
    # TODO:
    # Initialize RAG
    # Initialize Memory
    # Load Model
    #

    yield

    print()

    print("=" * 80)
    print("Stopping Nexus...")
    print("=" * 80)

# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="Nexus",
    description="Local AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================================
# Routes
# ============================================================

@app.get("/test")
async def test():
    print(">>> /test entered")

    workflow = app.state.workflow

    result = workflow.invoke(
        {
            "messages": [
                HumanMessage(content="Hello!")
            ]
        }
    )

    return result


@app.get("/")
async def root():

    return {
        "application": "Nexus",
        "status": "running",
    }


@app.get("/health")
async def health():

    return {
        "status": "ok",
    }

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_excludes=["unsloth_compiled_cache/*"],
    )