import axios from "axios";

export type Department =
  | "all"
  | "engineering"
  | "hr"
  | "onboarding"
  | "operations"
  | "sop";

export interface ChatSource {
  source: string;
  page: number | null;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  sources: ChatSource[];
}

export interface ChatRequest {
  question: string;
  conversation_id?: string | null;
  department?: Department | null;
}

export interface ChatMessageRecord {
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[];
  created_at: string;
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  preview: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  conversation_id: string;
  title: string;
  updated_at: string;
  messages: ChatMessageRecord[];
}

function resolveApiBaseUrl() {
  const configuredBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  if (typeof window === "undefined") {
    return configuredBaseUrl;
  }

  try {
    const parsedUrl = new URL(configuredBaseUrl);
    const isLocalBackendHost =
      parsedUrl.hostname === "localhost" || parsedUrl.hostname === "127.0.0.1";
    const isLocalFrontendHost =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1";

    if (isLocalBackendHost && isLocalFrontendHost) {
      parsedUrl.hostname = window.location.hostname;
      return parsedUrl.toString().replace(/\/$/, "");
    }
  } catch {
    return configuredBaseUrl;
  }

  return configuredBaseUrl;
}

const API = axios.create({
  baseURL: resolveApiBaseUrl(),
  withCredentials: true,
});

export default API;
