"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import axios from "axios";

import API, {
  ChatMessageRecord,
  ChatResponse,
  ConversationDetail,
} from "@/lib/api";

import { ChatPanel, type ChatPanelMessage } from "@/components/ChatPanel";

const STORAGE_SESSION_KEY = "novasphere-session-id";
const STORAGE_CONVERSATION_KEY = "novasphere-active-conversation-id";

const INITIAL_MESSAGE: ChatPanelMessage = {
  id: "assistant-welcome",
  role: "assistant",
  content:
    "Hi, I'm NovaSphere Bot. Ask me about HR policies, SOPs, onboarding guides, or engineering documents.",
};

function createSessionId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}`;
}

function getBrowserSessionId() {
  const existing = window.localStorage.getItem(STORAGE_SESSION_KEY);
  if (existing) {
    return existing;
  }

  const sessionId = createSessionId();
  window.localStorage.setItem(STORAGE_SESSION_KEY, sessionId);
  return sessionId;
}

function toWidgetMessages(messages: ChatMessageRecord[]): ChatPanelMessage[] {
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

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatPanelMessage[]>([INITIAL_MESSAGE]);
  const [sessionId, setSessionId] = useState("");
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    null,
  );
  const [activeTitle, setActiveTitle] = useState("How can I assist you today?");
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  const loadConversationList = async (nextSessionId: string) => {
    try {
      await API.get("/chat/history", {
        params: { session_id: nextSessionId },
      });
    } catch (requestError) {
      console.error("Failed to load chat history:", requestError);
    }
  };

  const openConversation = async (
    conversationId: string,
    nextSessionId: string = sessionId,
  ) => {
    if (!nextSessionId) {
      return;
    }

    try {
      const response = await API.get<ConversationDetail>(
        `/chat/history/${conversationId}`,
        { params: { session_id: nextSessionId } },
      );
      setActiveConversationId(response.data.conversation_id);
      setActiveTitle(response.data.title);
      setMessages(toWidgetMessages(response.data.messages));
      window.localStorage.setItem(
        STORAGE_CONVERSATION_KEY,
        response.data.conversation_id,
      );
    } catch (requestError) {
      console.error("Failed to load conversation:", requestError);
      setError("Unable to load that conversation.");
    }
  };

  useEffect(() => {
    const nextSessionId = getBrowserSessionId();
    setSessionId(nextSessionId);

    const savedConversationId = window.localStorage.getItem(
      STORAGE_CONVERSATION_KEY,
    );

    void (async () => {
      await loadConversationList(nextSessionId);
      if (savedConversationId) {
        await openConversation(savedConversationId, nextSessionId);
      }
    })();
  }, []);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [isOpen, messages, isSending]);

  const handleSubmit = async () => {
    const question = inputValue.trim();
    if (!question || isSending || !sessionId) {
      return;
    }

    const userMessage: ChatPanelMessage = {
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
        session_id: sessionId,
        conversation_id: activeConversationId,
      });

      if (!activeConversationId) {
        setActiveConversationId(response.data.conversation_id);
        window.localStorage.setItem(
          STORAGE_CONVERSATION_KEY,
          response.data.conversation_id,
        );
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
      await loadConversationList(sessionId);
    } catch (requestError) {
      const message = axios.isAxiosError(requestError)
        ? requestError.response?.data?.detail ?? "The assistant request failed."
        : "The assistant request failed.";

      setError(message);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          content:
            "I couldn't reach the backend just now. Please make sure the API is running and try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      <div className="fixed inset-y-0 right-0 z-40">
        <ChatPanel
          activeTitle={activeTitle}
          error={error}
          inputValue={inputValue}
          isOpen={isOpen}
          isSending={isSending}
          messages={messages}
          onChangeInput={setInputValue}
          onClose={() => setIsOpen(false)}
          onSubmit={() => void handleSubmit()}
          scrollAnchorRef={scrollAnchorRef}
        />
      </div>

      <button
        aria-label="Open chat assistant"
        className="group fixed bottom-8 right-8 z-30 flex h-[70px] w-[70px] items-center justify-center rounded-full border border-white/40 bg-white/14 p-2 shadow-[0_14px_36px_rgba(43,26,143,0.42)] backdrop-blur-md transition duration-300 hover:scale-110 hover:shadow-[0_18px_42px_rgba(98,46,202,0.52)] focus:outline-none"
        onClick={() => setIsOpen(true)}
        type="button"
      >
        <span className="sr-only">Open chat assistant</span>
        <div className="relative h-full w-full overflow-hidden rounded-full">
          <Image
            alt="NovaSphere chatbot"
            className="object-contain"
            fill
            sizes="70px"
            src="/images/novasphere-bot.png"
          />
        </div>
      </button>
    </>
  );
}
