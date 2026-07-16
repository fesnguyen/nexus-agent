// Placeholder API client for the Nexus FastAPI backend (see main.py).
// Swap API_BASE / endpoint paths once your real routes exist beyond
// /, /health and /test.

import { ChatRequest, ChatResponse } from "../types/chat";
import { ConversationResponse, ConversationsResponse } from "../types/conversation";

export const API_BASE = "http://127.0.0.1:8000";

async function request<T>(path: string, options = {}): Promise<T>  {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`Nexus API error ${res.status}: ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  health: () => request("/health"),

  sendMessage: (payload: FormData) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: payload,
      headers: {

      }
    }),

  listModels: () => request("/models"),

  getConversations: () => 
    request<ConversationsResponse>("/api/conversations", {
      method: "GET",
    }),

  getConversation: (conversationId: string) =>
    request<ConversationResponse>(
      `/api/conversations/${encodeURIComponent(conversationId)}`,
      {
        method: "GET",
      }
    ),
};
