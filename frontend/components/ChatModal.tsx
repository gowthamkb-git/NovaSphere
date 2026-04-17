"use client";

import Image from "next/image";
import { RefObject } from "react";

import { ChatSource, ConversationSummary } from "@/lib/api";

import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";

export interface WidgetMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

interface ChatModalProps {
  activeTitle: string;
  error: string | null;
  historyItems: ConversationSummary[];
  isHistoryOpen: boolean;
  inputValue: string;
  isOpen: boolean;
  isSending: boolean;
  isLoadingHistory: boolean;
  messages: WidgetMessage[];
  onBackdropClick: () => void;
  onChangeInput: (value: string) => void;
  onClose: () => void;
  onCreateConversation: () => void;
  onOpenConversation: (conversationId: string) => void;
  onSubmit: () => void;
  onToggleHistory: () => void;
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
  selectedConversationId: string | null;
}

export function ChatModal({
  activeTitle,
  error,
  historyItems,
  isHistoryOpen,
  inputValue,
  isOpen,
  isSending,
  isLoadingHistory,
  messages,
  onBackdropClick,
  onChangeInput,
  onClose,
  onCreateConversation,
  onOpenConversation,
  onSubmit,
  onToggleHistory,
  scrollAnchorRef,
  selectedConversationId,
}: ChatModalProps) {
  return (
    <div
      aria-hidden={!isOpen}
      className={`fixed inset-0 z-50 flex items-center justify-center bg-transparent px-4 transition duration-300 ${
        isOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
      }`}
      onClick={onBackdropClick}
    >
      <section
        aria-label="NovaSphere chat"
        className={`relative flex h-[500px] w-full origin-center overflow-hidden rounded-2xl border border-white/70 bg-white/82 shadow-2xl backdrop-blur-xl transition duration-300 ${
          isHistoryOpen ? "max-w-[680px]" : "max-w-[400px]"
        } ${
          isOpen ? "scale-100" : "scale-95"
        }`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex min-w-0 flex-1">
          <div className="flex min-w-0 flex-1 flex-col">
            <header className="flex items-center justify-between border-b border-slate-200 bg-white/84 px-4 py-3.5">
              <div className="flex min-w-0 items-center gap-2.5">
                <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-full bg-white/70 shadow-[0_8px_20px_rgba(68,97,214,0.2)] ring-1 ring-white/70">
                  <Image
                    alt="NovaSphere bot"
                    className="object-contain p-1"
                    fill
                    sizes="48px"
                    src="/images/novasphere-bot.png"
                  />
                </div>
                <div className="min-w-0">
                  <h2 className="truncate text-[1rem] font-semibold text-slate-700">
                    NovaSphere Bot
                  </h2>
                  <p className="truncate text-[0.72rem] text-slate-500">
                    {activeTitle || "How can I assist you today?"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full text-slate-500 transition duration-300 hover:bg-slate-100 hover:text-slate-900"
                  onClick={onCreateConversation}
                  type="button"
                >
                  <span className="sr-only">Start new chat</span>
                  <svg aria-hidden="true" className="h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <path
                      d="M12 5v14M5 12h14"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeWidth="1.8"
                    />
                  </svg>
                </button>
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full text-slate-500 transition duration-300 hover:bg-slate-100 hover:text-slate-900"
                  onClick={onToggleHistory}
                  type="button"
                >
                  <span className="sr-only">Toggle chat history</span>
                  <svg aria-hidden="true" className="h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <path
                      d="M8 7h11M8 12h11M8 17h11M4.5 7h.01M4.5 12h.01M4.5 17h.01"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeWidth="1.8"
                    />
                  </svg>
                </button>
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full text-slate-500 transition duration-300 hover:bg-slate-100 hover:text-slate-900"
                  onClick={onClose}
                  type="button"
                >
                  <span className="sr-only">Close chat</span>
                  <svg
                    aria-hidden="true"
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
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

            <div className="flex-1 overflow-y-auto bg-[#fbfbff]/88 px-3 py-4">
              <div className="space-y-3">
                {messages.map((message) => (
                  <ChatMessage
                    content={message.content}
                    key={message.id}
                    role={message.role}
                    sources={message.sources}
                  />
                ))}
                {isSending ? (
                  <ChatMessage
                    content="Thinking through your documents..."
                    role="assistant"
                  />
                ) : null}
                {error ? (
                  <p className="px-1 text-xs text-rose-600">{error}</p>
                ) : null}
                <div ref={scrollAnchorRef} />
              </div>
            </div>

            <ChatInput
              disabled={isSending}
              isSending={isSending}
              onChange={onChangeInput}
              onSubmit={onSubmit}
              value={inputValue}
            />
          </div>

          {isHistoryOpen ? (
            <aside className="w-[280px] border-l border-slate-200 bg-white/86">
              <div className="border-b border-slate-200 px-4 py-3">
                <h3 className="text-sm font-semibold text-slate-700">Chat history</h3>
                <p className="mt-1 text-[11px] text-slate-500">
                  All previous NovaSphere conversations
                </p>
              </div>
              <div className="max-h-[620px] overflow-y-auto px-2 py-2">
                {isLoadingHistory ? (
                  <p className="px-2 py-3 text-xs text-slate-500">Loading history...</p>
                ) : historyItems.length === 0 ? (
                  <p className="px-2 py-3 text-xs text-slate-500">
                    No saved chats yet. Start a conversation to see it here.
                  </p>
                ) : (
                  <div className="space-y-1">
                    {historyItems.map((conversation) => {
                      const isSelected =
                        selectedConversationId === conversation.conversation_id;
                      return (
                        <button
                          className={`block w-full rounded-2xl px-3 py-3 text-left transition duration-200 ${
                            isSelected
                              ? "bg-indigo-50 text-slate-900 shadow-sm ring-1 ring-indigo-200"
                              : "text-slate-600 hover:bg-slate-100"
                          }`}
                          key={conversation.conversation_id}
                          onClick={() => onOpenConversation(conversation.conversation_id)}
                          type="button"
                        >
                          <p className="truncate text-sm font-medium">
                            {conversation.title}
                          </p>
                          <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                            {conversation.preview || "Saved conversation"}
                          </p>
                          <p className="mt-2 text-[11px] text-slate-400">
                            {conversation.message_count} messages
                          </p>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </aside>
          ) : null}
        </div>
      </section>
    </div>
  );
}
