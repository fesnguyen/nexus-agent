# Nexus Agent Roadmap

## Vision

Build a local-first AI agent system demonstrating:

* Agent architecture
* Tool calling
* Retrieval-Augmented Generation (RAG)
* Long-term memory
* Planning and reasoning
* Multimodal understanding
* Production-style project structure

This project serves as a portfolio piece for AI Engineer and Multimodal AI Engineer positions.

---

# Phase 1 — Core Agent

## Goal

Create a working agent capable of:

* Receiving user requests
* Calling tools
* Returning responses

## Phase 1 — Agent Foundation

### Infrastructure
- [x] Python project structure
- [x] pyproject.toml
- [x] Editable install (pip install -e .)

### Tool System
- [x] BaseTool
- [x] ToolRegistry
- [x] Pydantic input schemas

### Tools
- [x] CalculatorTool
- [x] FileReaderTool
- [x] WebSearchTool (SearXNG)

### Search Infrastructure
- [x] Dockerized SearXNG
- [x] Local search API

### Model Layer
- [x] BaseModel abstraction
- [x] UnslothVLM backend
- [x] Qwen3-VL-4B-Instruct (4-bit)

### Agent Core
- [x] ToolRouter
- [x] ToolArgumentExtractor
- [x] Agent orchestration
- [x] End-to-end tool execution

### Remaining
- [ ] Structured tool calling
- [ ] Memory
- [ ] RAG
- [ ] Planning
- [ ] Multi-step workflows

---

# Phase 2 — RAG System

## Goal

Allow the agent to answer questions using local knowledge.

## Components

* Document Loader
* Chunking
* Embedding Model
* FAISS Vector Store
* Retriever

## Data Sources

knowledge/

* ai/
* llm/
* ml/
* notes/

## Success Criteria

User:
"What is LoRA?"

Agent:

* Retrieves relevant chunks
* Uses retrieved context
* Generates grounded answer

---

# Phase 3 — Memory

## Goal

Provide persistent user memory.

## Components

* Memory Manager
* User Profile Store
* Conversation History Store

## Success Criteria

User:
"I prefer Python."

Later:

"What language should I use?"

Agent remembers preference.

---

# Phase 4 — Planning Agent

## Goal

Support multi-step reasoning and execution.

## Components

* Planner
* Executor
* Observation Loop

## Example

User:
"Summarize transformers and save notes."

Plan:

1. Retrieve information
2. Generate summary
3. Save file

---

# Phase 5 — Multimodal Agent

## Goal

Enable image understanding.

## Candidate Models

* Qwen3-VL
* Gemma Vision
* InternVL

## Capabilities

* Image Captioning
* Screenshot Analysis
* Document Understanding
* Visual Question Answering

---

# Phase 6 — User Interface

## Goal

Provide an interactive interface.

## Candidate Frameworks

* Streamlit
* Gradio

## Features

* Chat
* File Upload
* Image Upload
* Tool Logs
* Memory Viewer

---

# Phase 7 — Benchmarking

## Goal

Measure system performance.

## Metrics

* Latency
* Retrieval Time
* Tool Execution Time
* Token Usage

## Output

benchmark_results.csv

---

# Phase 8 — Model Adaptation & Fine-Tuning

## Goal

Customize local LLM/VLM models for domain-specific tasks.

## Framework

- Unsloth
- PEFT
- LoRA
- QLoRA

## Candidate Models

- Qwen3-4B
- Qwen3-VL-4B
- Gemma 3
- Llama 3

## Tasks

- Instruction Tuning
- Domain Adaptation
- Vision-Language Fine-Tuning
- Tool-Use Fine-Tuning

## Deliverables

- Training pipeline
- Evaluation pipeline
- Adapter management
- Benchmark reports

# Stretch Goals

## Advanced RAG

* Hybrid Search
* Query Rewrite
* Reranking
* Context Compression

## Agent Enhancements

* Multi-Agent Collaboration
* Reflection Loop
* Self-Correction

## Deployment

* Docker
* FastAPI
* Local API Server
* Hugging Face Space Demo
