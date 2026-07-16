import { API_BASE } from "../../api/client";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed ${
          isUser
            ? "bg-accent text-white"
            : "bg-panel text-ink border border-border"
        }`}
      >
        {message.attachments?.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {message.attachments.map((a, i) => (
              <img
                key={i}
                src={a.url || (API_BASE + a.storagePath)}
                alt={a.name || "attachment"}
                className="h-28 w-28 rounded-lg object-cover"
              />
            ))}
          </div>
        )}
        {message.content && (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>
    </div>
  );
}
