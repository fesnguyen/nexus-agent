import { useRef, useState } from "react";
import {
  Plus,
  Mic,
  ArrowUp,
  BrainCircuit,
  Globe,
  Code2,
  X,
} from "lucide-react";

const TOGGLES = [
  { id: "think", label: "Think", icon: BrainCircuit },
  { id: "search", label: "Search", icon: Globe },
  { id: "code", label: "Code", icon: Code2 },
];

function filesToAttachments(files) {
  return Array.from(files)
    .filter((f) => f.type.startsWith("image/"))
    .map((f) => ({
      id: crypto.randomUUID(),
      name: f.name,
      url: URL.createObjectURL(f),
      file: f,
    }));
}

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [toggles, setToggles] = useState({
    think: false,
    search: false,
    code: false,
  });
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const canSend = (text.trim().length > 0 || attachments.length > 0) && !disabled;

  function addFiles(fileList) {
    const next = filesToAttachments(fileList);
    if (next.length) setAttachments((prev) => [...prev, ...next]);
  }

  function handlePaste(e) {
    if (e.clipboardData?.files?.length) {
      addFiles(e.clipboardData.files);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer?.files?.length) addFiles(e.dataTransfer.files);
  }

  function removeAttachment(id) {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  }

  function toggle(id) {
    setToggles((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  function autoResize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }

  function handleSend() {
    if (!canSend) return;
    onSend({ text: text.trim(), attachments, toggles });
    setText("");
    setAttachments([]);
    requestAnimationFrame(autoResize);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-5">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`rounded-2xl border bg-white shadow-float transition-colors ${
          dragOver ? "border-accent bg-accentSoft" : "border-border"
        }`}
      >
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 px-4 pt-3.5">
            {attachments.map((a) => (
              <div key={a.id} className="relative">
                <img
                  src={a.url}
                  alt={a.name}
                  className="h-16 w-16 rounded-lg object-cover"
                />
                <button
                  onClick={() => removeAttachment(a.id)}
                  className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-ink text-white"
                >
                  <X size={11} />
                </button>
              </div>
            ))}
          </div>
        )}

        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          placeholder="Send a message… (paste or drop an image)"
          onChange={(e) => {
            setText(e.target.value);
            autoResize();
          }}
          onPaste={handlePaste}
          onKeyDown={handleKeyDown}
          className="max-h-[200px] w-full resize-none bg-transparent px-4 py-3.5 text-[15px] text-ink placeholder:text-muted"
        />

        <div className="flex items-center gap-1.5 px-3 pb-2.5">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              addFiles(e.target.files);
              e.target.value = "";
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-panelHover hover:text-ink transition-colors"
            title="Attach image"
          >
            <Plus size={18} />
          </button>

          {TOGGLES.map((t) => {
            const Icon = t.icon;
            const active = toggles[t.id];
            return (
              <button
                key={t.id}
                onClick={() => toggle(t.id)}
                className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[13px] font-medium transition-colors ${
                  active
                    ? "border-accent bg-accentSoft text-accentDim"
                    : "border-border text-muted hover:bg-panelHover"
                }`}
              >
                <Icon size={14} />
                {t.label}
              </button>
            );
          })}

          <div className="ml-auto flex items-center gap-1.5">
            <button
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-panelHover hover:text-ink transition-colors"
              title="Voice input"
            >
              <Mic size={17} />
            </button>
            <button
              onClick={handleSend}
              disabled={!canSend}
              className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors ${
                canSend
                  ? "bg-accent text-white hover:bg-accentDim"
                  : "bg-border text-white/70 cursor-not-allowed"
              }`}
              title="Send"
            >
              <ArrowUp size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
