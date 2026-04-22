"use client";

import {
  CalendarDays,
  Clock3,
  Hash,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";

import type { WorkspaceModule } from "@/components/Sidebar";

interface ModulePanelProps {
  activeModule: WorkspaceModule;
  onSelectItem: (itemId: string | null) => void;
  selectedItemId: string | null;
}

const CHAT_ITEMS = [
  { id: "design", title: "Design review sync", preview: "Priya shared homepage updates", time: "9:28 AM" },
  { id: "launch", title: "Q2 launch prep", preview: "Ops updated the rollout checklist", time: "Today" },
  { id: "support", title: "Customer support handoff", preview: "Need clearer user guidance", time: "Yesterday" },
];

const PEOPLE_ITEMS = [
  { id: "priya", name: "Priya Raman", role: "Product Designer" },
  { id: "aaron", name: "Aaron Blake", role: "Frontend Engineer" },
  { id: "mina", name: "Mina Patel", role: "Program Manager" },
  { id: "lena", name: "Lena Brooks", role: "Support Lead" },
];

const ACTIVITY_ITEMS = [
  { id: "activity-1", title: "Design review updated", meta: "Priya posted a fresh revision" },
  { id: "activity-2", title: "Launch checklist edited", meta: "Operations changed a rollout step" },
  { id: "activity-3", title: "Support escalation resolved", meta: "Status moved to resolved" },
];

const COMMUNITY_ITEMS = [
  { id: "guild", title: "Design Systems Guild", meta: "28 members" },
  { id: "ai", title: "AI Enablement", meta: "42 members" },
  { id: "launch", title: "Launch Operations", meta: "16 members" },
];

const CALENDAR_ITEMS = [
  { id: "calendar-1", title: "Today", meta: "3 scheduled sessions" },
  { id: "calendar-2", title: "This week", meta: "12 events across teams" },
];

const MODULE_HEADERS: Record<WorkspaceModule, { title: string; description: string }> = {
  activity: {
    title: "Activity",
    description: "Recent changes, updates, and workspace signals",
  },
  chat: {
    title: "Chat",
    description: "Human messaging, threads, and recent conversations",
  },
  meet: {
    title: "Meet",
    description: "Upcoming collaboration surfaces and shared sessions",
  },
  people: {
    title: "People",
    description: "Contacts, teammates, and directory search",
  },
  communities: {
    title: "Communities",
    description: "Groups, guilds, and shared spaces",
  },
  calendar: {
    title: "Calendar",
    description: "Schedules, planning, and time-based coordination",
  },
};

export function ModulePanel({
  activeModule,
  onSelectItem,
  selectedItemId,
}: ModulePanelProps) {
  const header = MODULE_HEADERS[activeModule];

  return (
    <aside className="flex h-full w-[260px] shrink-0 flex-col border-r border-white/5 bg-white/5 backdrop-blur-xl transition-all duration-200 ease-in-out">
      <div className="border-b border-white/5 px-5 py-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-base font-semibold text-white">{header.title}</p>
            <p className="mt-1 text-xs text-slate-400">{header.description}</p>
          </div>

          {activeModule === "chat" ? (
            <div className="flex items-center gap-1">
              <button
                className="rounded-xl p-2 text-slate-400 transition-all duration-200 ease-in-out hover:bg-white/10 hover:text-white"
                onClick={() => onSelectItem("design")}
                type="button"
              >
                <span className="sr-only">New chat</span>
                <Plus className="h-4 w-4" />
              </button>
              <button
                className="rounded-xl p-2 text-slate-400 transition-all duration-200 ease-in-out hover:bg-white/10 hover:text-white"
                type="button"
              >
                <span className="sr-only">History</span>
                <Clock3 className="h-4 w-4" />
              </button>
            </div>
          ) : null}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeModule === "chat" ? (
          <div>
            <p className="px-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Recent Chats
            </p>
            <div className="mt-3 space-y-2">
              {CHAT_ITEMS.map((item) => {
                const isSelected = selectedItemId === item.id;
                return (
                  <button
                    className={`block w-full rounded-2xl px-4 py-3 text-left shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out ${
                      isSelected
                        ? "bg-white/10 text-white"
                        : "bg-white/5 text-slate-300 hover:bg-white/10"
                    }`}
                    key={item.id}
                    onClick={() => onSelectItem(item.id)}
                    type="button"
                  >
                    <p className="truncate text-sm font-medium">{item.title}</p>
                    <p className="mt-2 line-clamp-2 text-xs leading-6 text-slate-400">
                      {item.preview}
                    </p>
                    <p className="mt-3 text-[11px] text-slate-500">{item.time}</p>
                  </button>
                );
              })}
            </div>
          </div>
        ) : null}

        {activeModule === "people" ? (
          <div>
            <div className="flex items-center gap-3 rounded-2xl bg-white/5 px-3 py-3 text-sm text-slate-400 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out hover:bg-white/10">
              <Search className="h-4 w-4" />
              Search people
            </div>
            <div className="mt-4 space-y-2">
              {PEOPLE_ITEMS.map((person) => (
                <button
                  className="block w-full rounded-2xl bg-white/5 px-4 py-3 text-left text-slate-300 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10"
                  key={person.id}
                  onClick={() => onSelectItem(person.id)}
                  type="button"
                >
                  <p className="text-sm font-medium text-white">{person.name}</p>
                  <p className="mt-1 text-xs text-slate-400">{person.role}</p>
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {activeModule === "activity" ? (
          <div className="space-y-2">
            {ACTIVITY_ITEMS.map((item) => (
              <article
                className="rounded-2xl bg-white/5 px-4 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10"
                key={item.id}
              >
                <p className="text-sm font-medium text-white">{item.title}</p>
                <p className="mt-2 text-xs leading-6 text-slate-400">{item.meta}</p>
              </article>
            ))}
          </div>
        ) : null}

        {activeModule === "communities" ? (
          <div>
            <button
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-sm font-medium text-cyan-100 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10"
              type="button"
            >
              <Plus className="h-4 w-4" />
              Create community
            </button>
            <div className="mt-4 space-y-2">
              {COMMUNITY_ITEMS.map((community) => (
                <article
                  className="rounded-2xl bg-white/5 px-4 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10"
                  key={community.id}
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 text-cyan-200">
                      <Hash className="h-4 w-4" />
                    </span>
                    <div>
                      <p className="text-sm font-medium text-white">{community.title}</p>
                      <p className="mt-2 text-xs text-slate-400">{community.meta}</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        ) : null}

        {activeModule === "calendar" ? (
          <div className="space-y-2">
            {CALENDAR_ITEMS.map((item) => (
              <article
                className="rounded-2xl bg-white/5 px-4 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10"
                key={item.id}
              >
                <div className="flex items-center gap-3 text-cyan-200">
                  <CalendarDays className="h-4 w-4" />
                  <p className="text-sm font-medium text-white">{item.title}</p>
                </div>
                <p className="mt-2 text-xs text-slate-400">{item.meta}</p>
              </article>
            ))}
          </div>
        ) : null}

        {activeModule === "meet" ? (
          <div className="rounded-2xl bg-white/5 px-4 py-5 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10">
            <div className="flex items-start gap-3">
              <span className="text-cyan-200">
                <Sparkles className="h-5 w-5" />
              </span>
              <div>
                <p className="text-sm font-semibold text-white">Meet is coming next</p>
                <p className="mt-2 text-xs leading-6 text-slate-400">
                  This second panel is ready for future meetings, rooms, and session tools.
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
