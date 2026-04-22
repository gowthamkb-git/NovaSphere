"use client";

import { useMemo, useState, type RefObject } from "react";

import type { ChatSource } from "@/lib/api";
import { ChatHeader } from "@/components/ChatHeader";
import {
  ChatHistory,
  type ChatHistoryItem,
} from "@/components/ChatHistory";
import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";

export interface ChatPanelMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

interface ChatPanelProps {
  activeTitle: string;
  error: string | null;
  inputValue: string;
  isOpen: boolean;
  isSending: boolean;
  messages: ChatPanelMessage[];
  onChangeInput: (value: string) => void;
  onClose: () => void;
  onNewChat: () => void;
  onSubmit: () => void;
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
}

const MOCK_HISTORY_ITEMS: ChatHistoryItem[] = [
  {
    id: "history-policy",
    title: "Leave policy follow-up",
    preview: "How many days in advance should annual leave be requested?",
    messages: [
      {
        id: "history-policy-user",
        role: "user",
        content: "How many days in advance should annual leave be requested?",
      },
      {
        id: "history-policy-assistant",
        role: "assistant",
        content:
          "For one- or two-day annual leave, the policy recommends submitting at least three business days in advance. Longer leave is usually requested at least ten business days ahead.",
      },
    ],
  },
  {
    id: "history-onboarding",
    title: "Onboarding setup",
    preview: "What access should be ready before a new employee joins?",
    messages: [
      {
        id: "history-onboarding-user",
        role: "user",
        content: "What access should be ready before a new employee joins?",
      },
      {
        id: "history-onboarding-assistant",
        role: "assistant",
        content:
          "Baseline access typically includes email, calendar, chat, HRIS, ticketing, documentation, MFA, and any role-based systems approved by the hiring manager.",
      },
    ],
  },
  {
    id: "history-deployment",
    title: "Deployment checklist",
    preview: "What should I verify after a deployment?",
    messages: [
      {
        id: "history-deployment-user",
        role: "user",
        content: "What should I verify after a deployment?",
      },
      {
        id: "history-deployment-assistant",
        role: "assistant",
        content:
          "Verify health checks, dashboards, critical user flows, error rates, latency, and any business indicators tied to the release.",
      },
    ],
  },
];

export function ChatPanel({
  activeTitle,
  error,
  inputValue,
  isOpen,
  isSending,
  messages,
  onChangeInput,
  onClose,
  onNewChat,
  onSubmit,
  scrollAnchorRef,
}: ChatPanelProps) {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);

  const historyMessages = useMemo(
    () =>
      MOCK_HISTORY_ITEMS.find((item) => item.id === activeHistoryId)?.messages ?? null,
    [activeHistoryId],
  );

  const displayMessages = historyMessages ?? messages;
  const displayTitle =
    MOCK_HISTORY_ITEMS.find((item) => item.id === activeHistoryId)?.title ?? activeTitle;

  function handleNewChat() {
    setActiveHistoryId(null);
    onNewChat();
  }

  return (
    <aside
      aria-hidden={!isOpen}
      className={`h-full overflow-hidden border-l border-white/10 bg-white/5 backdrop-blur-xl shadow-[0_0_0_1px_rgba(255,255,255,0.05),-24px_0_60px_rgba(5,10,28,0.18)] transition-all duration-200 ease-in-out ${
        isOpen
          ? `${isHistoryOpen ? "w-[620px]" : "w-[400px]"} translate-x-0 opacity-100`
          : "w-0 translate-x-8 opacity-0"
      }`}
    >
      <div className={`flex h-full ${isHistoryOpen ? "w-[620px]" : "w-[400px]"} transition-all duration-200 ease-in-out`}>
        <ChatHistory
          activeHistoryId={activeHistoryId}
          historyItems={MOCK_HISTORY_ITEMS}
          isOpen={isHistoryOpen}
          onSelectHistory={setActiveHistoryId}
        />

        <div className="flex h-full w-[400px] flex-col">
          <ChatHeader
            activeTitle={displayTitle}
            isHistoryOpen={isHistoryOpen}
            onClose={onClose}
            onNewChat={handleNewChat}
            onToggleHistory={() => setIsHistoryOpen((current) => !current)}
          />

          <div className="flex-1 overflow-y-auto px-5 py-5">
            <div className="space-y-3">
              {displayMessages.map((message) => (
                <ChatMessage
                  content={message.content}
                  key={message.id}
                  role={message.role}
                  sources={message.sources}
                />
              ))}
              {isSending && !historyMessages ? (
                <ChatMessage
                  content="Thinking through your documents..."
                  role="assistant"
                />
              ) : null}
              {error && !historyMessages ? (
                <p className="px-1 text-xs text-rose-400">{error}</p>
              ) : null}
              <div ref={scrollAnchorRef} />
            </div>
          </div>

          <div className="border-t border-white/10 bg-white/[0.02] backdrop-blur-md">
            <ChatInput
              disabled={isSending || Boolean(historyMessages)}
              isSending={isSending}
              onChange={onChangeInput}
              onFilesSelected={(files) => console.log("Files queued for upload:", files)}
              onSubmit={onSubmit}
              value={inputValue}
            />
          </div>
        </div>
      </div>
    </aside>
  );
}
