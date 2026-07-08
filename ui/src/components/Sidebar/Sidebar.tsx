import { PanelLeft } from "lucide-react";
import Logo from "../icons/Logo.jsx";
import ConversationList from "./ConversationList.jsx";
import ProfileMenu from "./ProfileMenu.jsx";
import { NAV_ITEMS } from "../../constants/nav.js";

export default function Sidebar({
  collapsed,
  onToggleCollapsed,
  activeView,
  onNavigate,
  onNewChat,
  conversations,
  activeConversationId,
  onSelectConversation,
  loading,
}) {
  return (
    <aside
      className={`flex h-full flex-col border-r border-border bg-panel transition-all duration-200 ${
        collapsed ? "w-[68px]" : "w-[260px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-3">
        <Logo />
        {!collapsed && (
          <span className="text-[15px] font-semibold tracking-tight text-ink">
            Nexus
          </span>
        )}
        <button
          onClick={onToggleCollapsed}
          className="ml-auto flex h-7 w-7 items-center justify-center rounded-md text-muted hover:bg-panelHover hover:text-ink transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <PanelLeft size={16} />
        </button>
      </div>

      {/* Nav */}
      <nav className="px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = item.kind === "view" && activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() =>
                item.kind === "action" ? onNewChat() : onNavigate(item.id)
              }
              className={`mt-0.5 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-accentSoft text-accentDim font-medium"
                  : "text-ink/85 hover:bg-panelHover"
              } ${collapsed ? "justify-center px-2" : ""}`}
              title={item.label}
            >
              <Icon size={17} strokeWidth={2} />
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto px-2">
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={onSelectConversation}
          collapsed={collapsed}
          loading={loading}
        />
      </div>

      <ProfileMenu collapsed={collapsed} />
    </aside>
  );
}
