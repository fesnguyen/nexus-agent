import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";
import Logo from "../icons/Logo.jsx";

export default function MessageList({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-accentSoft">
          <Logo size={30} />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Chat with your model
        </h1>
        <p className="mt-1.5 text-[15px] text-muted">
          Running fully local — text, images, and tool calls
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      <div ref={endRef} />
    </div>
  );
}
