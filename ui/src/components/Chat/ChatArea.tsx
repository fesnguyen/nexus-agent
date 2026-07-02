import MessageList from "./MessageList.jsx";
import ChatInput from "./ChatInput.jsx";

export default function ChatArea({ messages, onSend, sending }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
      </div>
      <ChatInput onSend={onSend} disabled={sending} />
    </div>
  );
}
