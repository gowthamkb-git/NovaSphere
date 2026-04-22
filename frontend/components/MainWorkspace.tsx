"use client";

import {
  BellRing,
  CalendarClock,
  Mail,
  Phone,
  Search,
  UsersRound,
} from "lucide-react";

import type { WorkspaceModule } from "@/components/Sidebar";

interface MainWorkspaceProps {
  activeModule: WorkspaceModule;
  selectedItemId: string | null;
}

const CHAT_THREADS = {
  design: {
    title: "Design review sync",
    participants: "Priya, Aaron, You",
    messages: [
      { author: "Priya", time: "9:14 AM", content: "Shared the revised homepage spacing in the Figma file." },
      { author: "You", time: "9:21 AM", content: "Looks cleaner. I want to keep the hero copy stronger on desktop." },
      { author: "Aaron", time: "9:28 AM", content: "I can align the implementation after the review notes are final." },
    ],
  },
  launch: {
    title: "Q2 launch prep",
    participants: "Ops, Marketing, You",
    messages: [
      { author: "Mina", time: "Yesterday", content: "Need final confirmation on rollout sequencing before we share the schedule." },
      { author: "You", time: "Yesterday", content: "Frontend shell is nearly ready. AI panel can stay optional during launch week." },
      { author: "Omar", time: "Today", content: "Great. I will update the checklist with the current dependencies." },
    ],
  },
  support: {
    title: "Customer support handoff",
    participants: "Support, Product",
    messages: [
      { author: "Lena", time: "11:02 AM", content: "We need a clearer workflow for when users should open the AI panel versus module chat." },
      { author: "You", time: "11:07 AM", content: "Agreed. The new workspace split makes that distinction much easier." },
    ],
  },
} as const;

const PEOPLE_ROWS = [
  { name: "Priya Raman", role: "Product Designer", team: "Design", status: "Available" },
  { name: "Aaron Blake", role: "Frontend Engineer", team: "Engineering", status: "In focus time" },
  { name: "Mina Patel", role: "Program Manager", team: "Operations", status: "In a meeting" },
  { name: "Lena Brooks", role: "Support Lead", team: "Support", status: "Available" },
];

const ACTIVITY_ITEMS = [
  {
    title: "Design review updated",
    description: "Priya posted a new revision for the workspace shell.",
    time: "12 minutes ago",
  },
  {
    title: "Launch checklist edited",
    description: "Operations added a deployment readiness note for the Q2 release.",
    time: "34 minutes ago",
  },
  {
    title: "Support escalation resolved",
    description: "The workspace navigation confusion issue was marked as addressed.",
    time: "1 hour ago",
  },
];

const COMMUNITY_CARDS = [
  {
    title: "Design Systems Guild",
    description: "Patterns, accessibility reviews, and UI consistency discussions.",
    members: "28 members",
  },
  {
    title: "AI Enablement",
    description: "Internal best practices for automation, copilots, and RAG workflows.",
    members: "42 members",
  },
  {
    title: "Launch Operations",
    description: "Cross-functional coordination for rollout planning and execution.",
    members: "16 members",
  },
];

const CALENDAR_ITEMS = [
  { title: "Design review", time: "1:00 PM - 1:45 PM", owner: "Product + Design" },
  { title: "Engineering sync", time: "3:00 PM - 3:30 PM", owner: "Platform Team" },
  { title: "Launch readiness", time: "5:00 PM - 5:45 PM", owner: "Operations" },
];

const MODULE_COPY: Record<
  WorkspaceModule,
  { eyebrow: string; title: string; description: string }
> = {
  activity: {
    eyebrow: "Activity",
    title: "Team signals and updates",
    description:
      "A central stream for approvals, mentions, changes, and important workspace activity.",
  },
  chat: {
    eyebrow: "Chat",
    title: "Human conversations and coordination",
    description:
      "This area is for teammate messaging only. The AI assistant stays separate in the right-side panel.",
  },
  meet: {
    eyebrow: "Meet",
    title: "Live collaboration and sessions",
    description:
      "A placeholder for calls, meeting spaces, and future real-time collaboration features.",
  },
  people: {
    eyebrow: "People",
    title: "Contacts and team directory",
    description:
      "A shared directory view for teammates, teams, roles, and collaboration context.",
  },
  communities: {
    eyebrow: "Communities",
    title: "Shared groups and team spaces",
    description:
      "A home for internal communities, guilds, and group knowledge sharing.",
  },
  calendar: {
    eyebrow: "Calendar",
    title: "Schedules and upcoming work",
    description:
      "A structured planning surface for time-based coordination and team events.",
  },
};

export function MainWorkspace({
  activeModule,
  selectedItemId,
}: MainWorkspaceProps) {
  const copy = MODULE_COPY[activeModule];
  const activeThread =
    activeModule === "chat" && selectedItemId && selectedItemId in CHAT_THREADS
      ? CHAT_THREADS[selectedItemId as keyof typeof CHAT_THREADS]
      : CHAT_THREADS.design;

  return (
    <section className="flex h-full min-w-0 flex-1 flex-col">
      <header className="border-b border-white/5 px-8 py-6 transition-all duration-200 ease-in-out">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200/75">
          {copy.eyebrow}
        </p>
        <h1 className="mt-2 max-w-3xl text-3xl font-semibold tracking-tight text-white">
          {copy.title}
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300/80">
          {copy.description}
        </p>
      </header>

      <div className="flex-1 overflow-y-auto px-8 py-8">
        {activeModule === "chat" ? (
          <div className="mx-auto flex h-full max-w-5xl flex-col rounded-2xl bg-white/5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out">
            <div className="border-b border-white/5 px-5 py-5">
              <p className="text-lg font-semibold text-white">{activeThread.title}</p>
              <p className="mt-1 text-sm text-slate-400">{activeThread.participants}</p>
            </div>
            <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
              {activeThread.messages.map((message) => (
                <div
                  className="max-w-2xl rounded-2xl bg-white/5 px-5 py-4 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out"
                  key={`${message.author}-${message.time}-${message.content}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-500/15 text-sm font-semibold text-cyan-200">
                      {message.author.charAt(0)}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-white">{message.author}</p>
                      <p className="text-xs text-slate-500">{message.time}</p>
                    </div>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-slate-300/85">
                    {message.content}
                  </p>
                </div>
              ))}
            </div>
            <div className="border-t border-white/5 px-5 py-4">
              <div className="flex items-center gap-3 rounded-2xl bg-white/5 px-4 py-3 text-sm text-slate-400 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10">
                <Mail className="h-4 w-4" />
                Message composer placeholder for the human chat module
              </div>
            </div>
          </div>
        ) : null}

        {activeModule === "people" ? (
          <div className="mx-auto max-w-5xl rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out">
            <div className="flex items-center gap-3 rounded-2xl bg-white/5 px-4 py-3 text-sm text-slate-400 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10">
              <Search className="h-4 w-4" />
              Search people, roles, or teams
            </div>
            <div className="mt-6 overflow-hidden rounded-2xl bg-white/5 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md">
              <div className="grid grid-cols-[1.2fr_1fr_0.8fr_0.8fr] border-b border-white/5 bg-white/[0.04] px-5 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                <span>Name</span>
                <span>Role</span>
                <span>Team</span>
                <span>Status</span>
              </div>
              {PEOPLE_ROWS.map((person) => (
                <div
                  className="grid grid-cols-[1.2fr_1fr_0.8fr_0.8fr] items-center border-b border-white/5 px-5 py-4 text-sm text-slate-300 transition-all duration-200 ease-in-out last:border-b-0 hover:bg-white/[0.04]"
                  key={person.name}
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-500/14 text-xs font-semibold text-cyan-200">
                      {person.name
                        .split(" ")
                        .map((part) => part[0])
                        .join("")
                        .slice(0, 2)}
                    </span>
                    <span>{person.name}</span>
                  </div>
                  <span>{person.role}</span>
                  <span>{person.team}</span>
                  <span className="text-slate-400">{person.status}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {activeModule === "activity" ? (
          <div className="mx-auto max-w-4xl space-y-4">
            {ACTIVITY_ITEMS.map((item) => (
              <article
                className="rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out hover:bg-white/10"
                key={item.title}
              >
                <div className="flex items-start gap-4">
                  <span className="mt-1 flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-500/14 text-cyan-200">
                    <BellRing className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-base font-semibold text-white">{item.title}</p>
                    <p className="mt-2 text-sm leading-7 text-slate-300/85">
                      {item.description}
                    </p>
                    <p className="mt-3 text-xs uppercase tracking-[0.16em] text-slate-500">
                      {item.time}
                    </p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : null}

        {activeModule === "communities" ? (
          <div className="mx-auto max-w-5xl">
            <div className="grid gap-5 lg:grid-cols-3">
              {COMMUNITY_CARDS.map((community) => (
                <article
                  className="rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out hover:bg-white/10"
                  key={community.title}
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/14 text-cyan-200">
                    <UsersRound className="h-5 w-5" />
                  </div>
                  <p className="mt-5 text-lg font-semibold text-white">{community.title}</p>
                  <p className="mt-3 text-sm leading-7 text-slate-300/85">
                    {community.description}
                  </p>
                  <p className="mt-5 text-xs uppercase tracking-[0.16em] text-slate-500">
                    {community.members}
                  </p>
                </article>
              ))}
            </div>
          </div>
        ) : null}

        {activeModule === "calendar" ? (
          <div className="mx-auto max-w-4xl rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out">
            <div className="grid gap-4 md:grid-cols-3">
              {CALENDAR_ITEMS.map((event) => (
                <article
                  className="rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out hover:bg-white/10"
                  key={event.title}
                >
                  <div className="flex items-center gap-3 text-cyan-200">
                    <CalendarClock className="h-5 w-5" />
                    <span className="text-xs uppercase tracking-[0.16em]">
                      Upcoming
                    </span>
                  </div>
                  <p className="mt-4 text-base font-semibold text-white">{event.title}</p>
                  <p className="mt-2 text-sm text-slate-300/80">{event.time}</p>
                  <p className="mt-4 text-xs text-slate-500">{event.owner}</p>
                </article>
              ))}
            </div>
          </div>
        ) : null}

        {activeModule === "meet" ? (
          <div className="mx-auto max-w-4xl rounded-2xl bg-white/5 p-5 backdrop-blur-md shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out">
            <div className="flex items-start gap-4">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/14 text-cyan-200">
                <Phone className="h-5 w-5" />
              </span>
              <div>
                <p className="text-lg font-semibold text-white">Meet module placeholder</p>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300/80">
                  This main workspace area is reserved for future live collaboration,
                  calls, and meeting surfaces. It remains separate from the AI panel.
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
