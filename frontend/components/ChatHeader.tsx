"use client";

import Image from "next/image";
import { Clock3, Plus } from "lucide-react";

interface ChatHeaderProps {
  activeTitle: string;
  isHistoryOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onToggleHistory: () => void;
}

export function ChatHeader({
  activeTitle,
  isHistoryOpen,
  onClose,
  onNewChat,
  onToggleHistory,
}: ChatHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-white/8 px-5 py-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="relative h-10 w-10 overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10">
          <Image
            alt="NovaSphere bot"
            className="object-contain p-1"
            fill
            sizes="40px"
            src="/images/novasphere-bot.png"
          />
        </div>
        <div className="min-w-0">
          <p className="truncate text-base font-semibold text-white">
            NovaSphere Bot
          </p>
          <p className="truncate text-xs text-slate-400">
            {activeTitle || "Ask your company assistant"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <button
          className={`rounded-full p-2 transition ${
            isHistoryOpen
              ? "bg-cyan-500/12 text-cyan-100"
              : "text-slate-400 hover:bg-white/8 hover:text-white"
          }`}
          onClick={onToggleHistory}
          type="button"
        >
          <span className="sr-only">Toggle history</span>
          <Clock3 className="h-4 w-4" />
        </button>
        <button
          className="rounded-full p-2 text-slate-400 transition hover:bg-white/8 hover:text-white"
          onClick={onNewChat}
          type="button"
        >
          <span className="sr-only">Start new chat</span>
          <Plus className="h-4 w-4" />
        </button>
        <button
          className="rounded-full p-2 text-slate-400 transition hover:bg-white/8 hover:text-white"
          onClick={onClose}
          type="button"
        >
          <span className="sr-only">Close chat panel</span>
          <svg aria-hidden="true" className="h-4 w-4" fill="none" viewBox="0 0 24 24">
            <path
              d="M6 6l12 12M18 6L6 18"
              stroke="currentColor"
              strokeLinecap="round"
              strokeWidth="1.8"
            />
          </svg>
        </button>
      </div>
    </header>
  );
}
