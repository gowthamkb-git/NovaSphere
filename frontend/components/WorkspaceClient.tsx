"use client";

import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

import API, {
  type ChatMessageRecord,
  type ChatResponse,
  type ConversationDetail,
  type ConversationSummary,
} from "@/lib/api";
import { clearAuthSession, getStoredUser } from "@/lib/auth";
import type { AuthUser } from "@/lib/auth";
import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";

interface WidgetMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: { source: string; page: number | null }[];
}

const INITIAL_MESSAGE: WidgetMessage = {
  id: "assistant-welcome",
  role: "assistant",
  content:
    "Welcome to NovaSphere Bot. Ask about company policies, SOPs, onboarding, or internal knowledge.",
};

function toWidgetMessages(messages: ChatMessageRecord[]): WidgetMessage[] {
  if (messages.length === 0) {
    return [INITIAL_MESSAGE];
  }

  return messages.map((message, index) => ({
    id: `${message.role}-${message.created_at}-${index}`,
    role: message.role,
    content: message.content,
    sources: message.sources,
  }));
}

export function WorkspaceClient() {
  const router = useRouter();
  const scrollAnchorRef = useRef<HTMLDivElement>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isBotOpen, setIsBotOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<WidgetMessage[]>([INITIAL_MESSAGE]);
  const [historyItems, setHistoryItems] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    null,
  );
  const [activeTitle, setActiveTitle] = useState("NovaSphere Bot");
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const nextUser = getStoredUser();
    if (!nextUser) {
      router.replace("/login");
      return;
    }
    setUser(nextUser);
    setIsReady(true);
  }, [router]);

  useEffect(() => {
    if (!isReady) {
      return;
    }

    void loadConversationList();
  }, [isReady]);

  useEffect(() => {
    if (!isBotOpen) {
      return;
    }
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [isBotOpen, messages, isSending]);

  const activePreview = useMemo(
    () => historyItems.find((item) => item.conversation_id === activeConversationId),
    [activeConversationId, historyItems],
  );

  async function loadConversationList() {
    setIsLoadingHistory(true);
    try {
      const response = await API.get<ConversationSummary[]>("/chat/history");
      setHistoryItems(response.data);
    } catch (requestError) {
      console.error("Failed to load user chat history:", requestError);
      if (axios.isAxiosError(requestError) && requestError.response?.status === 401) {
        clearAuthSession();
        router.replace("/login");
      }
    } finally {
      setIsLoadingHistory(false);
    }
  }

  async function openConversation(conversationId: string) {
    try {
      const response = await API.get<ConversationDetail>(
        `/chat/history/${conversationId}`,
      );
      setActiveConversationId(response.data.conversation_id);
      setActiveTitle(response.data.title);
      setMessages(toWidgetMessages(response.data.messages));
      setIsBotOpen(true);
      setError(null);
    } catch (requestError) {
      console.error("Failed to open conversation:", requestError);
      setError("Unable to load that conversation.");
    }
  }

  function startNewConversation() {
    setActiveConversationId(null);
    setActiveTitle("NovaSphere Bot");
    setMessages([INITIAL_MESSAGE]);
    setInputValue("");
    setError(null);
    setIsBotOpen(true);
  }

  async function handleSubmit() {
    const question = inputValue.trim();
    if (!question || isSending) {
      return;
    }

    const userMessage: WidgetMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
    };

    setMessages((current) => [...current, userMessage]);
    setInputValue("");
    setIsSending(true);
    setError(null);

    try {
      const response = await API.post<ChatResponse>("/chat", {
        question,
        conversation_id: activeConversationId,
      });

      if (!activeConversationId) {
        setActiveConversationId(response.data.conversation_id);
        setActiveTitle(question.length > 48 ? `${question.slice(0, 45).trim()}...` : question);
      }

      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.data.answer,
          sources: response.data.sources,
        },
      ]);

      await loadConversationList();
    } catch (requestError) {
      const message = axios.isAxiosError(requestError)
        ? requestError.response?.data?.detail ?? "The assistant request failed."
        : "The assistant request failed.";
      setError(message);
    } finally {
      setIsSending(false);
    }
  }

  function handleLogout() {
    clearAuthSession();
    router.replace("/login");
  }

  if (!isReady || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0b1028] text-white">
        <p className="text-sm text-slate-300">Loading your workspace...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen bg-[linear-gradient(180deg,_#121a3d_0%,_#0f1530_100%)] text-white">
      <aside className="flex w-24 shrink-0 flex-col items-center border-r border-white/8 bg-[#0b1028] py-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[linear-gradient(180deg,_#8b5cf6,_#6d28d9)] text-lg font-semibold shadow-[0_14px_34px_rgba(124,58,237,0.35)]">
          N
        </div>
        <nav className="mt-10 flex flex-col items-center gap-5 text-[11px] font-medium text-slate-300">
          <button className="w-16 rounded-2xl px-2 py-3 text-center text-white/80" type="button">
            Activity
          </button>
          <button
            className={`w-16 rounded-2xl px-2 py-3 text-center transition ${
              isBotOpen
                ? "bg-violet-500/18 text-white shadow-[0_10px_30px_rgba(124,58,237,0.2)]"
                : "text-white/80 hover:bg-white/6"
            }`}
            onClick={() => setIsBotOpen(true)}
            type="button"
          >
            Bot
          </button>
        </nav>
      </aside>

      <aside className="flex w-[320px] shrink-0 flex-col border-r border-white/8 bg-[#111736]/90 p-5">
        <div className="rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(124,58,237,0.22),rgba(255,255,255,0.05))] p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-violet-200/90">
            User Details
          </p>
          <div className="mt-4 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/12 text-lg font-semibold text-white">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="truncate text-base font-semibold text-white">
                {user.full_name}
              </p>
              <p className="truncate text-sm text-slate-300/75">{user.email}</p>
            </div>
          </div>
          <button
            className="mt-5 rounded-2xl border border-white/12 bg-white/6 px-4 py-2.5 text-sm font-medium text-white/90 transition hover:bg-white/10"
            onClick={handleLogout}
            type="button"
          >
            Log out
          </button>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-white">NovaSphere Bot</p>
            <p className="mt-1 text-xs text-slate-400">
              Registered user chat history
            </p>
          </div>
          <button
            className="rounded-full border border-white/12 bg-white/6 px-3 py-1.5 text-xs font-medium text-white/90 transition hover:bg-white/10"
            onClick={startNewConversation}
            type="button"
          >
            New
          </button>
        </div>

        <div className="mt-4 flex-1 overflow-y-auto">
          {isLoadingHistory ? (
            <p className="text-sm text-slate-400">Loading conversations...</p>
          ) : historyItems.length === 0 ? (
            <p className="rounded-2xl border border-dashed border-white/12 bg-white/4 px-4 py-5 text-sm leading-7 text-slate-400">
              No saved bot conversations yet. Start a chat and it will be stored for this registered user.
            </p>
          ) : (
            <div className="space-y-2">
              {historyItems.map((conversation) => {
                const isSelected = activeConversationId === conversation.conversation_id;
                return (
                  <button
                    className={`block w-full rounded-2xl border px-4 py-3 text-left transition ${
                      isSelected
                        ? "border-violet-400/35 bg-violet-500/15 text-white"
                        : "border-white/8 bg-white/4 text-slate-300 hover:bg-white/8"
                    }`}
                    key={conversation.conversation_id}
                    onClick={() => void openConversation(conversation.conversation_id)}
                    type="button"
                  >
                    <p className="truncate text-sm font-medium">{conversation.title}</p>
                    <p className="mt-1 line-clamp-2 text-xs text-slate-400">
                      {conversation.preview || "Saved conversation"}
                    </p>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </aside>

      <section className="relative flex min-w-0 flex-1 overflow-hidden">
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-white/8 px-8 py-6">
            <p className="text-sm uppercase tracking-[0.24em] text-violet-200/75">
              Workspace
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
              Teams-style company workspace
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300/80">
              This workspace is ready for future collaboration features. For now,
              the working product feature is your NovaSphere RAG chatbot, available
              from the bot entry in the left rail.
            </p>
          </header>

          <div className="grid flex-1 gap-6 px-8 py-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(31,39,90,0.88),rgba(18,26,61,0.78))] p-8">
              <p className="text-sm font-semibold text-violet-200">What works now</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                Company knowledge assistant for registered employees
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-300/80">
                Users can sign up, log in, and access their own bot conversation history.
                This keeps the chatbot as a separate working product feature inside
                the larger NovaSphere application.
              </p>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-white/6 p-8">
              <p className="text-sm font-semibold text-white">Current active conversation</p>
              <p className="mt-3 text-xl font-semibold text-white">
                {activePreview?.title ?? "No conversation selected"}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-300/80">
                Open the bot from the left rail to continue an existing conversation or start a new one.
              </p>
            </div>
          </div>
        </div>

        <aside
          className={`absolute right-0 top-0 z-10 flex h-full w-full max-w-[460px] flex-col border-l border-white/8 bg-[#0b1028]/96 shadow-[-24px_0_60px_rgba(5,10,28,0.42)] backdrop-blur-xl transition-transform duration-300 sm:w-[460px] ${
            isBotOpen ? "translate-x-0" : "translate-x-full"
          }`}
        >
          <header className="flex items-center justify-between border-b border-white/8 px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10">
                <Image
                  alt="NovaSphere bot"
                  className="object-contain p-1"
                  fill
                  sizes="48px"
                  src="/images/novasphere-bot.png"
                />
              </div>
              <div>
                <p className="text-base font-semibold text-white">NovaSphere Bot</p>
                <p className="text-xs text-slate-400">
                  {activeTitle || "Ask your company assistant"}
                </p>
              </div>
            </div>
            <button
              className="rounded-full p-2 text-slate-400 transition hover:bg-white/8 hover:text-white"
              onClick={() => setIsBotOpen(false)}
              type="button"
            >
              <span className="sr-only">Close bot panel</span>
              <svg aria-hidden="true" className="h-4 w-4" fill="none" viewBox="0 0 24 24">
                <path
                  d="M6 6l12 12M18 6L6 18"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeWidth="1.8"
                />
              </svg>
            </button>
          </header>

          <div className="flex-1 overflow-y-auto px-4 py-5">
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
                <p className="px-1 text-xs text-rose-400">{error}</p>
              ) : null}
              <div ref={scrollAnchorRef} />
            </div>
          </div>

          <ChatInput
            disabled={isSending}
            isSending={isSending}
            onChange={setInputValue}
            onSubmit={() => void handleSubmit()}
            value={inputValue}
          />
        </aside>
      </section>
    </main>
  );
}
