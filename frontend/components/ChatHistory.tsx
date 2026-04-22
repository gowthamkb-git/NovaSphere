"use client";

import { Clock3 } from "lucide-react";

import type { ChatPanelMessage } from "@/components/ChatPanel";

export interface ChatHistoryItem {
  id: string;
  title: string;
  preview: string;
  messages: ChatPanelMessage[];
}

interface ChatHistoryProps {
  activeHistoryId: string | null;
  historyItems: ChatHistoryItem[];
  isOpen: boolean;
  onSelectHistory: (historyId: string) => void;
}

export function ChatHistory({
  activeHistoryId,
  historyItems,
  isOpen,
  onSelectHistory,
}: ChatHistoryProps) {
  return (
    <aside
      className={`border-r border-white/8 bg-[#0f1631] transition-all duration-300 ease-in-out ${
        isOpen ? "w-[220px] translate-x-0 opacity-100" : "w-0 -translate-x-6 opacity-0"
      } overflow-hidden`}
    >
      <div className="flex h-full w-[220px] flex-col">
        <div className="border-b border-white/8 px-4 py-4">
          <div className="flex items-center gap-2 text-cyan-200">
            <Clock3 className="h-4 w-4" />
            <p className="text-sm font-semibold">History</p>
          </div>
          <p className="mt-2 text-xs leading-6 text-slate-400">
            Recent NovaSphere assistant conversations
          </p>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-3">
          <div className="space-y-2">
            {historyItems.map((item) => {
              const isSelected = activeHistoryId === item.id;
              return (
                <button
                  className={`block w-full rounded-[20px] border px-3 py-3 text-left transition ${
                    isSelected
                      ? "border-cyan-400/35 bg-cyan-500/12 text-white"
                      : "border-white/8 bg-white/[0.03] text-slate-300 hover:bg-white/[0.06]"
                  }`}
                  key={item.id}
                  onClick={() => onSelectHistory(item.id)}
                  type="button"
                >
                  <p className="truncate text-sm font-medium">{item.title}</p>
                  <p className="mt-2 line-clamp-2 text-xs leading-6 text-slate-400">
                    {item.preview}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </aside>
  );
}
