# Nexus Agent

A local-first, modular AI agent framework built with Python, FastAPI, and LangGraph.

Nexus Agent is designed around clean architecture principles, separating API, application logic, orchestration, memory, retrieval, and model management into independent modules. The framework currently supports Retrieval-Augmented Generation (RAG), persistent conversations, tool calling, and incremental knowledge indexing, with multimodal (VLM) support under active development.

---

# Features

- 🤖 Local LLM-powered AI Agent
- 📚 Retrieval-Augmented Generation (RAG)
- 🔄 Incremental Knowledge Indexing
- 💬 Persistent Conversations
- 🧠 LangGraph Workflow Orchestration
- 🔧 Modular Tool System
- 📦 Lazy Model Loading
- ⚡ FastAPI Backend
- 🖥️ React Frontend
- 📝 SQLite Storage
- 🔍 FAISS Semantic Search

---

# Overall Architecture

```
                 Client (React)
                        │
                        ▼
                FastAPI Controllers
                        │
                        ▼
                Application Use Cases
        (Chat / Conversation / Future APIs)
                        │
                        ▼
              LangGraph Workflow Engine
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
     Memory          Retrieval        Tool System
        │               │                │
        ▼               ▼                ▼
Conversation DB    Knowledge Index     External Tools
(SQLite)          (FAISS + SQLite)

                        │
                        ▼
                 Model Managers
        (LLM / Embedding / Cross Encoder)
```

Main Flow:

1. FastAPI receives requests.
2. Application Use Cases coordinate the request.
3. LangGraph orchestrates the reasoning workflow.
4. Memory, Retrieval, and Tools act as services.
5. Model Managers provide the required AI models.

---

# Workflow Design

Nexus Agent is designed around a message-centric workflow where conversations are reconstructed for every request. Instead of maintaining mutable prompt state, the backend rebuilds the model context from the conversation history, memory, and retrieved knowledge each time the user sends a message.

## Message-Centric Architecture

The conversation history is the single source of truth.

For every user request:

1. Load the conversation history from the database.
2. Build the workflow state.
3. Execute the LangGraph workflow.
4. Persist newly generated messages.

The prompt is rebuilt on every request rather than being stored in memory.

### Why?

- Stateless model execution
- Deterministic prompt construction
- Easy debugging
- Reproducible responses
- Flexible context injection

---

## Backend as the Source of Truth

The frontend remains intentionally lightweight.

Instead of sending the full conversation every request:

```text
Frontend
    │
    ├── conversation_id
    └── user_message
```

the backend loads everything it needs:

- Conversation history
- System prompt
- Memory
- Retrieved knowledge
- Agent state

This guarantees consistency and prevents clients from modifying conversation history.

---

## LangGraph Orchestration

LangGraph coordinates the agent workflow.

```
                           HumanMessage
                                │
                                ▼
                         ┌────────────┐
                         │ Agent Node │◄──────────────────────────┐
                         └────────────┘                           │
                                │                                 │
                                ▼                                 │
                          Language Model                          │
                                │                                 │
                                ▼                                 │
                         AgentDecision                            │
                                │                                 │
                 ┌──────────────┴──────────────┐                  │
                 │                             │                  │
         response exists                tool_calls exist          │
                 │                             │                  │
                 ▼                             ▼                  │
            AIMessage                   AIMessage                 │
                 │                             │                  │
                 ▼                     ┌───────────┐              │
              Finish                   │ Tool Node │              │
                                       └───────────┘              │
                                             │                    │
                                             ▼                    │
                                        ToolMessage───────────────┘
```

The workflow is driven by the latest message in the conversation.

The `agent_node` is responsible for the agent's reasoning. It decides whether the model can answer immediately or whether additional actions (such as tool execution) are required.

---

## Prompt Reconstruction

Every inference builds a fresh prompt from multiple sources.

```
System Prompt
        │
Conversation History
        │
Memory Context
        │
Retrieved Context
        │
Current User Message
        │
        ▼
      Final Prompt
```

No prompt is permanently stored.

Each request reconstructs the complete context.

---

## Memory Injection

Memory is not continuously attached to the conversation.

Instead:

1. The workflow determines the user's request.
2. Relevant memories are retrieved.
3. Memory is injected into the prompt context.
4. The model reasons using the additional information.

This keeps prompts concise while allowing personalized responses.

---

## Retrieval as a Service

Retrieval is implemented as an independent service instead of being tightly coupled to the agent.

The retrieval pipeline includes:

```
User Query
     │
Query Rewrite
     │
Semantic Search
     │
Reranking
     │
Context Compression
     │
Retrieved Context
```

The retrieved context is injected into the prompt before model inference.

Because retrieval is isolated behind a service interface, the workflow remains independent of the underlying retrieval implementation.

---

## Model-Agnostic Design

AI components are abstracted behind managers.

Examples include:

- LLM Manager
- Embedding Manager
- Cross Encoder Manager

This allows different models and AI backends to be evaluated without changing the application workflow.

---

## Lazy Resource Initialization

Large AI resources are loaded only when required.

Benefits include:

- Faster application startup
- Lower memory usage
- Shared model instances
- Easier runtime model switching

---

## Separation of Responsibilities

```
FastAPI
    │
    ▼
Application Layer
    │
    ▼
LangGraph Workflow
    │
 ┌──┴───────────────┐
 ▼                  ▼
Memory          Retrieval
 │                  │
 ▼                  ▼
SQLite      FAISS + SQLite
 │
 ▼
Model Managers
```

Each layer has a single responsibility:

- **FastAPI** — HTTP communication
- **Application** — Business use cases
- **LangGraph** — Workflow orchestration
- **Memory** — Conversation and long-term memory
- **Retrieval** — Knowledge search
- **Model Managers** — AI model lifecycle

---

# Project Structure

```
nexus-agent/
│
├── app/
│   │
│   ├── api/                 # FastAPI routers & request handlers
│   ├── application/         # Application use cases
│   ├── contracts/           # Shared interfaces and abstractions
│   ├── core/                # Shared utilities and infrastructure
│   ├── graph/               # LangGraph workflow implementation
│   ├── memory/              # Conversation & long-term memory
│   ├── models/              # AI model managers
│   ├── prompt/              # Prompt templates
│   ├── ranking/             # Retrieval reranking
│   ├── retrieval/           # RAG pipeline
│   └── tools/               # Agent tools
│
├── configs/                 # Configuration files
├── data/                    # Databases and vector stores
├── docker/                  # Docker configuration
├── docs/                    # Project documentation
├── tests/                   # Unit & integration tests
├── ui/                      # React frontend
│
├── environment.yml          # Conda environment
├── pyproject.toml
└── main.py                  # Application entry point
```

---

# Retrieval Pipeline

```
Knowledge Files
       │
       ▼
Document Loader
       │
       ▼
Parser
       │
       ▼
Chunker
       │
       ▼
Embedding
       │
       ▼
FAISS + SQLite
```

Current capabilities:

- Document discovery
- Parsing
- Chunking
- Embedding generation
- Semantic search
- Context compression
- Query rewriting
- Incremental indexing
- File modification detection
- Deleted file cleanup
- Selective re-embedding

---

# Running the Project

Create the Conda environment:

```bash
micromamba env create -f environment.yml
```

Activate it:

```bash
micromamba activate nexus-agent
```

Run the backend:

```bash
python main.py
```

Run the frontend:

```bash
cd ui

npm install

npm run dev
```

---

# Technology Stack

### Backend

- Python
- FastAPI
- LangGraph

### AI

- Unsloth FastAPI
- Hugging Face Transformers
- Sentence Transformers
- FAISS

### Storage

- SQLite
- FAISS

### Frontend

- React
- TypeScript
- Tailwind CSS
- Vite

---

# Roadmap

## ✅ Completed

- FastAPI backend
- LangGraph workflow
- Conversation persistence
- RAG pipeline
- Incremental knowledge indexing
- Tool framework
- Lazy model management
- React UI

---

## 🚧 In Progress

- Multimodal (VLM) Brain
- Multiple tool calls (simultaneously)
- Docker deployment

---

## 📌 Planned

- Memory summarization
- MCP support
- Multi-agent workflow
- Voice interaction
- Advanced RAG
- Runtime model management
- Swappable AI technology stack

---

# Design Principles

- Local-first
- Model agnostic
- Clean Architecture
- Modular components
- Dependency Injection
- Lazy initialization
- Service-oriented design
- Production-oriented architecture

---

## Acknowledgements

Building Nexus Agent was a long journey, and I definitely wasn't coding alone.

Special thanks to:

- 🤖 ChatGPT — for patiently answering thousands of questions.
- 🧠 Claude — for thoughtful architecture discussions.
- ✨ Gemini — for alternative perspectives and ideas.
- 💻 GitHub Copilot — for saving me from typing the same boilerplate over and over.

Thanks for being excellent coding companions throughout this project. 🚀

---

# License

Licensed under the MIT License.