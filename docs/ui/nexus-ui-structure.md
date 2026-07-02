# Nexus UI — Project Structure

```
ui/
└── src/
    ├── api/
    │   └── client.js
    ├── components/
    │   ├── Chat/
    │   ├── icons/
    │   ├── Sidebar/
    │   ├── TopBar/
    │   └── PlaceholderView.jsx
    ├── constants/
    │   └── nav.js
    ├── App.jsx
    ├── index.css
    └── main.jsx
├── index.html
├── package.json
├── postcss.config.js
├── README.md
├── tailwind.config.js
└── vite.config.js
```

## Root config files

| File | Responsibility |
|---|---|
| `index.html` | Vite's HTML entry point — mounts the `#root` div that React renders into. |
| `main.jsx` | React entry point — creates the root and renders `<App />` into the DOM. |
| `vite.config.js` | Vite build/dev-server config (React plugin, dev port). |
| `tailwind.config.js` | Design tokens — the custom color palette (`bg`, `panel`, `accent`, etc.), fonts, shadows used across every component. |
| `postcss.config.js` | Wires Tailwind + Autoprefixer into the CSS build pipeline. |
| `package.json` | Dependencies (`react`, `lucide-react`, `tailwindcss`, `vite`) and npm scripts (`dev`, `build`, `preview`). |
| `README.md` | Setup instructions and a summary of how to wire the UI to your FastAPI backend. |

## `src/index.css`

Global stylesheet: imports the Inter/JetBrains Mono fonts, Tailwind's base/components/utilities layers, and small hand-written bits (scrollbar styling, the pulsing status-dot animation) that don't belong in a component.

## `src/App.jsx`

The top-level component and single source of truth for app state:

- `conversations` — in-memory list of chat threads
- `activeConversationId` / `activeView` / `activeModelId` — what's currently shown
- `handleSend` — sends a message to the backend via `api.sendMessage()`, appends the reply (or a fallback error message if the backend call fails)

It composes `Sidebar`, `TopBar`, and either `ChatArea` or `PlaceholderView` depending on which nav item is active.

## `src/api/client.js`

The only file that talks to the network. Defines `API_BASE` (`http://127.0.0.1:8000`) and one `request()` helper wrapping `fetch`. Exposes `api.health()`, `api.sendMessage()`, `api.listModels()`, `api.listConversations()` — currently placeholders pointing at routes your backend doesn't have yet (see the integration guide).

## `src/constants/nav.js`

Static data, not components:

- `NAV_ITEMS` — the sidebar's nav entries (New Chat, Compare, Search, Train, Recipes, Export) with their icons and whether they're an `"action"` (New Chat) or a `"view"` (switches the main panel)
- `MOCK_MODELS` — placeholder model list shown in the `TopBar` dropdown until `/models` is wired up

## `src/components/Sidebar/`

| File | Responsibility |
|---|---|
| `Sidebar.jsx` | Composes the whole left rail: logo/header, nav buttons, conversation list, profile menu. Handles the collapsed/expanded width transition. |
| `ConversationList.jsx` | The collapsible "Recents" section — renders conversation titles, highlights the active one. |
| `ProfileMenu.jsx` | Bottom-left avatar + name, with a small popup menu (Settings / Sign out). |

## `src/components/TopBar/`

| File | Responsibility |
|---|---|
| `TopBar.jsx` | Model-select dropdown (top-left of the main panel) plus a "local runtime" status pill on the right. |

## `src/components/Chat/`

| File | Responsibility |
|---|---|
| `ChatArea.jsx` | Thin wrapper combining `MessageList` + `ChatInput` into the full chat panel. |
| `MessageList.jsx` | Renders the empty state ("Chat with your model") or the scrollable list of messages, auto-scrolling to the latest. |
| `MessageBubble.jsx` | A single message — user bubbles right-aligned/filled, assistant bubbles left-aligned/outlined, plus inline image attachments. |
| `ChatInput.jsx` | The composer: auto-resizing textarea, paste/drag-drop image handling, attachment previews, the Think/Search/Code toggle pills, and the send button. Owns its own local state (draft text, attachments, toggles) until a message is sent. |

## `src/components/icons/Logo.jsx`

The app's mark — a small original SVG (not Unsloth's mascot), used in the sidebar header and the chat empty state.

## `src/components/PlaceholderView.jsx`

Generic "Coming soon" panel shown for any nav item other than Chat (Compare, Search, Train, Recipes, Export) — keeps the sidebar structurally complete without those pages being built out yet.
