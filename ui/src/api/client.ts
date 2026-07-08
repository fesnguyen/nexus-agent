// Placeholder API client for the Nexus FastAPI backend (see main.py).
// Swap API_BASE / endpoint paths once your real routes exist beyond
// /, /health and /test.

import { ChatRequest } from "../types/chat";

export const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`Nexus API error ${res.status}: ${res.statusText}`);
  }

  return res.json();
}

export const api = {
  health: () => request("/health"),

  // Placeholder — wire this up to your real chat/workflow endpoint
  // (e.g. a POST /chat route that invokes app.state.workflow).
  sendMessage: (payload: ChatRequest) =>
    request("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listModels: () => request("/models"),

  getConversations: () => 
    request("/api/conversations", {
      method: "POST",
    }),
};
