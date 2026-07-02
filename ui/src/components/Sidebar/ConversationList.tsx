import { useState } from "react";
import { ChevronRight } from "lucide-react";

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  collapsed,
}) {
  const [open, setOpen] = useState(true);

  if (collapsed) return null;

  return (
    <div className="mt-6">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 px-2 py-1 text-xs font-medium uppercase tracking-wide text-muted hover:text-ink transition-colors"
      >
        <ChevronRight
          size={13}
          className={`transition-transform ${open ? "rotate-90" : ""}`}
        />
        Recents
      </button>

      {open && (
        <ul className="mt-1 space-y-0.5">
          {conversations.length === 0 && (
            <li className="px-3 py-2 text-sm text-muted">
              No conversations yet
            </li>
          )}
          {conversations.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => onSelect(c.id)}
                className={`w-full truncate rounded-lg px-3 py-1.5 text-left text-sm transition-colors ${
                  c.id === activeId
                    ? "bg-accentSoft text-accentDim font-medium"
                    : "text-ink/80 hover:bg-panelHover"
                }`}
                title={c.title}
              >
                {c.title}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
