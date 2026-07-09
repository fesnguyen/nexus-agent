import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar/Sidebar.jsx";
import TopBar from "./components/TopBar/TopBar.jsx";
import ChatArea from "./components/Chat/ChatArea.jsx";
import PlaceholderView from "./components/PlaceholderView.jsx";
import { MOCK_MODELS, NAV_ITEMS } from "./constants/nav.js";
import { api } from "./api/client.js";
import { ChatRequest } from "./types/chat.js";
import { Conversation } from "./types/conversation.js"

function newConversation() {
  const id = crypto.randomUUID();
  return { id, title: "New chat", messages: [] };
}

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeView, setActiveView] = useState("chat");
  const [activeModelId, setActiveModelId] = useState(MOCK_MODELS[0].id);
  const [sending, setSending] = useState(false);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loading, setLoading] = useState(true);

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId
  );

  // Load conversation list onload
  useEffect(() => {
    async function fetchConversations() {
      try {
        setLoading(true);
        const response = await api.getConversations(); 
        
        if (response?.items?.length) {
          setConversations(response.items);
          setActiveConversationId(response.items[0].id);
        } else {
          // Fallback: No conversation available, create new one
          const fallbackChat = newConversation();
          setConversations([fallbackChat]);
          setActiveConversationId(fallbackChat.id);
        }
      } catch (err) {
        console.error("Failed to load conversations:", err);
        // Fallback on error so the app remains usable
        const fallbackChat = newConversation();
        setConversations([fallbackChat]);
        setActiveConversationId(fallbackChat.id);
      } finally {
        setLoading(false);
      }
    }

    fetchConversations();
  }, []);

  /**
   * Find conversation with this ID and replace it.
   * @param id - conversation id
   * @param updater - callable function use to update id
   */
  function updateConversation(id: string, updater: Function) {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? updater(c) : c))
    );
  }

  function handleNewChat() {
    const conv = newConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveConversationId(conv.id);
    setActiveView("chat");
  }

  function handleNavigate(viewId) {
    setActiveView(viewId);
  }

  /**
   * Loads a conversation from the backend and updates the local state.
   *
   * @param id - The ID of the conversation to load.
   */
  async function handleChangeConversation(id: string) {
    try {
      setLoading(true);

      // Fetch the full conversation (including messages).
      const res = await api.getConversation(id);
      
      // Update the selected conversation with the latest messages.
      setConversations((prev) =>
        prev.map(conversation =>
          conversation.id === id
            ? {
                ...conversation,
                messages: res.data.messages,
              }
            : conversation
        )
      );

      // Switch to the selected conversation.
      setActiveConversationId(id);
      setActiveView("chat");
    }
    catch (err) {
      console.error(err);
    }
    finally {
      setLoading(false);
    }
  }

  /**
   * Chat to Nexus agent
   * @param param0 
   * @returns 
   */
  async function handleSend({ text, attachments, toggles }) {
    if (!activeConversation) return;
    const convId = activeConversation.id;

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      attachments,
    };

    // Add this new message to the conversation it's belong to
    updateConversation(convId, (c) => ({
      ...c,
      // Set its title if this is the first message
      title: 
        c.messages.length === 0 && text 
          ? text.slice(0, 40) 
          : c.title,
      messages: [...c.messages, userMessage],
    }));

    setSending(true);
    try {
      // Construct the explicit payload payload matching ChatRequest
      const payload: ChatRequest = {
        conversationId: convId,
        toggles,
        message: text, 
      };

      const res = await api.sendMessage(payload);

      // Add reponse message to conversation
      updateConversation(convId, (c) => ({
        ...c,
        messages: [
          ...c.messages,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: res?.content ?? "(no content returned)",
          },
        ],
      }));
    } catch (err) {
      updateConversation(convId, (c) => ({
        ...c,
        messages: [
          ...c.messages,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content:
              "Couldn't reach the backend at 127.0.0.1:8000/chat. This is a placeholder route — wire it to your workflow endpoint in api/client.js.",
          },
        ],
      }));
      console.error(err);
    } finally {
      setSending(false);
    }
  }

  const activeLabel = NAV_ITEMS.find((n) => n.id === activeView)?.label;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg font-sans text-ink">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapsed={() => setCollapsed((c) => !c)}
        activeView={activeView}
        onNavigate={handleNavigate}
        onNewChat={handleNewChat}
        conversations={conversations}
        activeConversationId={activeConversationId}
        loading={loading}
        onSelectConversation={handleChangeConversation}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar activeModelId={activeModelId} onSelectModel={setActiveModelId} />

        <main className="min-h-0 flex-1">
          {activeView === "chat" ? (
            <ChatArea
              messages={activeConversation?.messages ?? []}
              onSend={handleSend}
              sending={sending}
            />
          ) : (
            <PlaceholderView label={activeLabel} />
          )}
        </main>
      </div>
      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="loading-spinner" />
            <div>
              <p className="loading-title">Processing request</p>
              <p className="loading-subtitle">
                Please wait...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
