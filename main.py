from __future__ import annotations

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from app.application.chat_use_case import ChatUseCase
from app.core.app import agent_context
from app.graph.workflow import build_workflow
from langchain_core.messages import HumanMessage
from app.api.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

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

    # Initialize all agent relevant stuffs
    agent_context.initialize()

    print("Container initialize success!")

    workflow = build_workflow()

    chat_use_case = ChatUseCase(
        workflow=workflow,
        conversation_service=agent_context.conversation_service,
    )

    app.state.chat_use_case = chat_use_case

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

# 1. Define allowed origins based on your environment
ENV = os.getenv("APP_ENV", "development")

if ENV == "production":
    allowed_origins = [
        # "https://www.your-app-domain.com",
        # "https://your-app-domain.com"
    ]
else:
    allowed_origins = [
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ]

# 2. Apply the middleware safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"], # Explicitly list methods instead of "*"
    allow_headers=["Content-Type", "Authorization"],           # Explicitly list accepted headers
)

app.include_router(chat_router)

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