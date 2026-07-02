# nexus-agent
Agentic RAG assistant powered by local LLMs.

# Start
```
# Start API (wrapper with assumed preset names / base which specific names)
fastapi dev / uvicorn main:app reload

fastapi run / uvicorn main:app --host 0.0.0.0 --port 8000

Note: left / right have same meaning, can pass same arguments like --reload-exclude "unsloth_compiled_cache/*"

# Start UI
npm install
npm run dev
```