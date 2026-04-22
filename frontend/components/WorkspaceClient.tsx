"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

import API, {
  type ChatMessageRecord,
  type ChatResponse,
} from "@/lib/api";
import { clearAuthSession, storeAuthSession } from "@/lib/auth";
import type { AuthUser } from "@/lib/auth";
import { ChatPanel, type ChatPanelMessage } from "@/components/ChatPanel";
import { ModulePanel } from "@/components/ModulePanel";
import { MainWorkspace } from "@/components/MainWorkspace";
import { Sidebar, type WorkspaceModule } from "@/components/Sidebar";

const INITIAL_MESSAGE: ChatPanelMessage = {
  id: "assistant-welcome",
  role: "assistant",
  content:
    "Welcome to NovaSphere Bot. Ask about company policies, SOPs, onboarding, or internal knowledge.",
};

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

export function WorkspaceClient() {
  const router = useRouter();
  const scrollAnchorRef = useRef<HTMLDivElement>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [activeModule, setActiveModule] = useState<WorkspaceModule>("chat");
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedModuleItemId, setSelectedModuleItemId] = useState<string | null>("design");
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatPanelMessage[]>([INITIAL_MESSAGE]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    null,
  );
  const [activeTitle, setActiveTitle] = useState("NovaSphere Bot");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void hydrateUser();
  }, [router]);

  useEffect(() => {
    if (!isChatOpen) {
      return;
    }

    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [isChatOpen, messages, isSending]);

  async function hydrateUser() {
    try {
      const response = await API.get<AuthUser>("/auth/me");
      setUser(response.data);
      storeAuthSession({ user: response.data });
      setIsReady(true);
    } catch (requestError) {
      console.error("Failed to hydrate session:", requestError);
      clearAuthSession();
      router.replace("/login");
    }
  }

  function handleSidebarSelect(item: WorkspaceModule) {
    setActiveModule(item);
    setIsProfileMenuOpen(false);
    setSelectedModuleItemId(
      item === "chat"
        ? "design"
        : item === "people"
          ? "priya"
          : item === "activity"
            ? "activity-1"
            : item === "communities"
              ? "guild"
              : item === "calendar"
                ? "calendar-1"
                : null,
    );
  }

  async function handleSubmit() {
    const question = inputValue.trim();
    if (!question || isSending) {
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
        conversation_id: activeConversationId,
      });

      if (!activeConversationId) {
        setActiveConversationId(response.data.conversation_id);
        setActiveTitle(
          question.length > 48 ? `${question.slice(0, 45).trim()}...` : question,
        );
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
    void (async () => {
      try {
        await API.post("/auth/logout");
      } catch (requestError) {
        console.error("Failed to log out cleanly:", requestError);
      } finally {
        clearAuthSession();
        router.replace("/login");
      }
    })();
  }

  if (!isReady || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0b1028] text-white">
        <p className="text-sm text-slate-300">Loading your workspace...</p>
      </main>
    );
  }

  return (
    <main className="h-screen overflow-hidden bg-[linear-gradient(180deg,_#121a3d_0%,_#0f1530_100%)] text-white">
      <div className="flex h-full w-full">
        <Sidebar
          activeItem={activeModule}
          isProfileMenuOpen={isProfileMenuOpen}
          onChatClick={() => setIsChatOpen((current) => !current)}
          onCloseProfileMenu={() => setIsProfileMenuOpen(false)}
          onItemSelect={handleSidebarSelect}
          onLogout={handleLogout}
          onToggleProfileMenu={() => setIsProfileMenuOpen((current) => !current)}
          user={user}
        />

        <div className="flex min-w-0 flex-1">
          <ModulePanel
            activeModule={activeModule}
            onSelectItem={setSelectedModuleItemId}
            selectedItemId={selectedModuleItemId}
          />

          <div className="min-w-0 flex-1 transition-all duration-300 ease-in-out">
            <MainWorkspace
              activeModule={activeModule}
              selectedItemId={selectedModuleItemId}
            />
          </div>

          <ChatPanel
            activeTitle={activeTitle}
            error={error}
            inputValue={inputValue}
            isOpen={isChatOpen}
            isSending={isSending}
            messages={messages}
            onChangeInput={setInputValue}
            onClose={() => setIsChatOpen(false)}
            onNewChat={() => {
              setMessages([]);
              setInputValue("");
              setError(null);
              setActiveConversationId(null);
              setActiveTitle("New conversation");
            }}
            onSubmit={() => void handleSubmit()}
            scrollAnchorRef={scrollAnchorRef}
          />
        </div>
      </div>
    </main>
  );
}
