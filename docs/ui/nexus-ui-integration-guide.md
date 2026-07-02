# Nexus UI — Backend Integration Guide

This guide walks through connecting `nexus-ui` (React/Vite frontend) to your
`main.py` FastAPI backend, replacing the placeholder routes with real ones.

---

## 1. Prerequisites

- Backend running via `python main.py` (or `uvicorn main:app --reload`) on
  `127.0.0.1:8000`
- Frontend running via `npm run dev` on `localhost:5173`
- Both processes run side by side during development — they are separate
  servers, not one app

---

## 2. Enable CORS on the backend

Since the UI (`localhost:5173`) and API (`127.0.0.1:8000`) are different
origins, the browser will block requests until CORS is enabled.

In `main.py`, add this before your routes are defined:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, replace `allow_origins` with your deployed frontend's real
domain instead of `localhost:5173`.

---

## 3. Add a real `/chat` route

The UI currently calls `POST /chat` from `src/api/client.js`. Your backend
doesn't have this route yet — only `/`, `/health`, and `/test`.

### 3.1 Define the request/response shape

`ChatInput.jsx` sends this payload on every message:

```json
{
  "conversationId": "uuid-string",
  "model": "qwen3-4b-instruct-bnb-4bit",
  "toggles": { "think": false, "search": false, "code": false },
  "messages": [
    { "role": "user", "content": "Hello!" }
  ]
}
```

The UI expects this response shape:

```json
{ "content": "Assistant's reply text" }
```

### 3.2 Add the route

```python
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    conversationId: str
    model: str
    toggles: dict
    messages: list[ChatMessage]

@app.post("/chat")
async def chat(payload: ChatRequest):
    workflow = app.state.workflow

    # Convert incoming messages into LangChain message objects
    lc_messages = [
        HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
        for m in payload.messages
    ]

    result = workflow.invoke({"messages": lc_messages})

    reply = result["messages"][-1].content
    return {"content": reply}
```

Adjust the `workflow.invoke(...)` call and the `result["messages"][-1]`
lookup to match whatever shape `build_graph()` actually returns — this is a
minimal example assuming the graph returns a `messages` list like your
existing `/test` route.

### 3.3 Handle streaming (optional, recommended later)

The current UI waits for one JSON response per message (no streaming). If
you want token-by-token streaming later, you'd switch `/chat` to a
`StreamingResponse` and update `src/api/client.js`'s `sendMessage` to read
from a `ReadableStream` instead of `res.json()`. Not required for a first
integration pass.

---

## 4. Wire up real models (optional)

The UI currently shows a hardcoded model list from
`src/constants/nav.js` → `MOCK_MODELS`.

To make this dynamic, add a route:

```python
@app.get("/models")
async def list_models():
    return [
        {
            "id": "qwen3-4b-instruct-bnb-4bit",
            "name": "Qwen3-4B-Instruct-2507",
            "tag": "4-bit · local",
        }
    ]
```

Then in `App.jsx`, replace the `MOCK_MODELS` import with a `useEffect` that
calls `api.listModels()` on mount and stores the result in state.

---

## 5. Wire up conversation persistence (optional)

Conversations currently live only in React state (`App.jsx`) and are lost
on refresh. To persist them:

1. Add `GET /conversations` and `POST /conversations` routes backed by
   `SQLiteMemoryStore` (already wired in `container.py` as
   `container.memory_store`).
2. On app load, call `api.listConversations()` and populate the sidebar.
3. On `handleSend` in `App.jsx`, also persist the new user/assistant
   messages to the backend so they survive a refresh.

This is the natural next step once `/chat` works, since your container
already has a memory layer built for exactly this.

---

## 6. Image attachments

The chat input supports pasting (`Ctrl+V`) and drag-and-drop of images.
Right now these are held as local `URL.createObjectURL()` previews only —
they are **not** uploaded anywhere.

To send images to the backend, you have two options:

- **Base64 inline**: convert each attachment `File` to base64 in
  `handleSend` (`App.jsx`) and include it in the `/chat` payload as an
  `image` field per message; on the backend, decode and pass to a
  vision-capable model.
- **Separate upload endpoint**: add `POST /upload` that accepts
  `multipart/form-data`, stores the file, and returns a URL/ID to include
  in the chat payload instead of raw bytes.

Base64 inline is simplest to start with; move to a real upload endpoint if
image sizes become a problem.

---

## 7. Toggles (Think / Search / Code)

The `toggles` object (`{ think, search, code }`) is passed through to
`/chat` but nothing consumes it yet. Suggested mapping:

- `think` → pass a flag into your workflow to request a reasoning/CoT pass
  before the final answer
- `search` → route through `RAGService` / your retrieval layer instead of
  (or in addition to) the raw LLM call
- `code` → hint the model/tool registry to prefer code-execution tools

These can all be read off `payload.toggles` inside the `/chat` route and
branched on before calling `workflow.invoke(...)`.

---

## 8. Quick end-to-end test checklist

1. Start backend: `python main.py`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173`
4. Send a message with no image → confirm it hits `/chat` (check backend
   logs / browser Network tab) and a reply renders
5. Paste an image (`Ctrl+V`) → confirm the thumbnail appears before sending
6. Toggle `Think` / `Search` / `Code` → confirm they show up in the
   `/chat` request payload (Network tab → Payload)
7. Refresh the page → confirm conversations reset (expected until step 5
   / conversation persistence is added)

---

## 9. File reference

| Frontend file                     | What to change when backend changes            |
|-----------------------------------|--------------------------------------------------|
| `src/api/client.js`               | `API_BASE`, endpoint paths, request/response shape |
| `src/constants/nav.js`            | Remove `MOCK_MODELS` once `/models` is live       |
| `src/App.jsx`                     | Swap in-memory `conversations` state for API calls |
| `src/components/Chat/ChatInput.jsx` | Add base64 encoding if wiring real image upload |
