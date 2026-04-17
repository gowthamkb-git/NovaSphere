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
  session_id: string;
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

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
});

export default API;
