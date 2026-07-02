import { useEffect, useRef, useState } from "react";
import { Settings, LogOut, ChevronsUpDown } from "lucide-react";

export default function ProfileMenu({ collapsed }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <div ref={ref} className="relative border-t border-border p-2">
      {open && (
        <div className="absolute bottom-[calc(100%+6px)] left-2 right-2 rounded-xl border border-border bg-white p-1 shadow-float">
          <button className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-ink hover:bg-panelHover">
            <Settings size={16} /> Settings
          </button>
          <button className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-ink hover:bg-panelHover">
            <LogOut size={16} /> Sign out
          </button>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 rounded-lg px-1.5 py-1.5 hover:bg-panelHover transition-colors"
      >
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-white">
          N
        </div>
        {!collapsed && (
          <>
            <div className="min-w-0 flex-1 text-left">
              <div className="truncate text-sm font-medium text-ink">
                Nexus User
              </div>
              <div className="truncate text-xs text-muted">Local</div>
            </div>
            <ChevronsUpDown size={14} className="text-muted" />
          </>
        )}
      </button>
    </div>
  );
}
