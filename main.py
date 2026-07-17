from __future__ import annotations

from contextlib import asynccontextmanager
import os

# Force all Hugging Face loaders to look ONLY at local cache
# os.environ["HF_HUB_OFFLINE"] = "1"

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.application.chat_use_case import ChatUseCase
from app.application.conversation_use_case import ConversationUseCase
from app.application.application_container import ApplicationContainer
from app.core.app import agent_context
from app.graph.workflow import build_workflow
from langchain_core.messages import HumanMessage
from app.api.routes.chat import router as chat_router
from app.api.routes.conversation import router as conversation_router
from fastapi.middleware.cors import CORSMiddleware

from configs.agent_settings import CHAT_IMAGES_DIR, MOUNTED_IMAGES_FOLDER

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

    # Application container inject to state, used by request
    chat_use_case = ChatUseCase(
        workflow=workflow,
        conversation_service=agent_context.conversation_service,
        vision_service=agent_context.vision_service,
        memory_ingestion_service = agent_context.memory_ingestion_service,
    )
    conversation_use_case = ConversationUseCase(
        conversation_service=agent_context.conversation_service,
    )
    container = ApplicationContainer(
        chat_use_case=chat_use_case,
        conversation_use_case=conversation_use_case,
    )

    app.state.application = container

    agent_context.initialize_resources()

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

# Ensure the directory exists
os.makedirs(CHAT_IMAGES_DIR, exist_ok=True)

# Mount the folder to the /images URL path
app.mount(MOUNTED_IMAGES_FOLDER, StaticFiles(directory=CHAT_IMAGES_DIR), name="chat_images")

app.include_router(chat_router)
app.include_router(conversation_router)

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