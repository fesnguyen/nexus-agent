# Nexus Agent

Agentic RAG assistant powered by local LLMs.

## Prerequisites

- Micromamba
- Node.js + npm

## Create the environment

```bash
micromamba create -f environment.yml
micromamba activate nexus-agent-env
```

## Start the backend

Development:

```bash
fastapi dev app/main.py
```

Production:

```bash
fastapi run app/main.py
```

## Start the frontend

```bash
cd ui
npm install
npm run dev
```

## Project Structure

app/
├── api/
├── graph/
├── memory/
├── models/
├── prompt/
├── rag/
└── tools/

ui/