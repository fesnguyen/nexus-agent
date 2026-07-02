import { useState } from "react";
import Sidebar from "./components/Sidebar/Sidebar.jsx";
import TopBar from "./components/TopBar/TopBar.jsx";
import ChatArea from "./components/Chat/ChatArea.jsx";
import PlaceholderView from "./components/PlaceholderView.jsx";
import { MOCK_MODELS, NAV_ITEMS } from "./constants/nav.js";
import { api } from "./api/client.js";
import { ChatRequest } from "./types/chat.js";

function newConversation() {
  const id = crypto.randomUUID();
  return { id, title: "New chat", messages: [] };
}

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeView, setActiveView] = useState("chat");
  const [activeModelId, setActiveModelId] = useState(MOCK_MODELS[0].id);
  const [sending, setSending] = useState(false);

  const [conversations, setConversations] = useState(() => [
    newConversation(),
  ]);
  const [activeConversationId, setActiveConversationId] = useState(
    conversations[0].id
  );

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId
  );

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
        model: activeModelId,
        toggles,
        messages: [...activeConversation.messages, userMessage].map((m) => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        })), 
      };

      const res = await api.sendMessage(payload);

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
        onSelectConversation={(id) => {
          setActiveConversationId(id);
          setActiveView("chat");
        }}
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
    </div>
  );
}
