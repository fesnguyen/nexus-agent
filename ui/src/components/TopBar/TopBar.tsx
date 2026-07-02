import { useEffect, useRef, useState } from "react";
import { ChevronDown, Check, Wifi } from "lucide-react";
import { MOCK_MODELS } from "../../constants/nav.js";

export default function TopBar({ activeModelId, onSelectModel }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const activeModel = MOCK_MODELS.find((m) => m.id === activeModelId);

  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <header className="flex h-14 items-center justify-between border-b border-border px-4">
      <div ref={ref} className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[15px] font-medium text-ink hover:bg-panelHover transition-colors"
        >
          {activeModel?.name ?? "Select model"}
          <ChevronDown size={16} className="text-muted" />
        </button>

        {open && (
          <div className="absolute left-0 top-[calc(100%+6px)] w-72 rounded-xl border border-border bg-white p-1 shadow-float z-10">
            {MOCK_MODELS.map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  onSelectModel(m.id);
                  setOpen(false);
                }}
                className="flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left hover:bg-panelHover"
              >
                <div>
                  <div className="text-sm font-medium text-ink">{m.name}</div>
                  <div className="text-xs text-muted">{m.tag}</div>
                </div>
                {m.id === activeModelId && (
                  <Check size={16} className="text-accent shrink-0" />
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-xs text-muted">
        <span className="status-dot h-1.5 w-1.5 rounded-full bg-emerald-500" />
        Local runtime
      </div>
    </header>
  );
}
