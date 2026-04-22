"use client";

import { type FormEvent, type KeyboardEvent, useEffect, useRef } from "react";
import { Mic, Paperclip, SendHorizonal } from "lucide-react";

interface ChatInputProps {
  disabled?: boolean;
  isSending?: boolean;
  onFilesSelected?: (files: File[]) => void;
  onChange: (value: string) => void;
  onSubmit: () => void;
  value: string;
}

type BrowserSpeechRecognition = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((event: Event) => void) | null;
  start: () => void;
};

declare global {
  interface Window {
    SpeechRecognition?: new () => BrowserSpeechRecognition;
    webkitSpeechRecognition?: new () => BrowserSpeechRecognition;
  }
}

export function ChatInput({
  disabled = false,
  isSending = false,
  onFilesSelected,
  onChange,
  onSubmit,
  value,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    adjustTextareaHeight();
  }, [value]);

  function adjustTextareaHeight() {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = "40px";
    const nextHeight = Math.min(Math.max(textarea.scrollHeight, 40), 160);
    textarea.style.height = `${nextHeight}px`;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    handleSend();
  }

  function handleSend() {
    if (!value.trim() || disabled) {
      return;
    }

    onSubmit();
    onChange("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  function handleFileSelection(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) {
      return;
    }

    console.log("Selected files for future upload:", files);
    onFilesSelected?.(files);
    event.target.value = "";
  }

  function handleMicClick() {
    const SpeechRecognition =
      window.SpeechRecognition ?? window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? "")
        .join(" ")
        .trim();

      if (!transcript) {
        return;
      }

      onChange(value ? `${value.trim()} ${transcript}` : transcript);
    };
    recognition.onerror = (event) => {
      console.warn("Speech recognition failed:", event);
    };
    recognition.start();
  }

  return (
    <form className="p-4" onSubmit={handleSubmit}>
      <input
        accept=".pdf,.doc,.docx,.txt,.md,image/*"
        className="hidden"
        multiple
        onChange={handleFileSelection}
        ref={fileInputRef}
        type="file"
      />

      <div className="flex items-end gap-2 rounded-xl bg-white/5 px-3 py-2 backdrop-blur-lg shadow-[0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-200 ease-in-out hover:bg-white/10">
        <div className="flex w-full items-end gap-3">
          <button
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-slate-400 transition-all duration-200 ease-in-out hover:bg-white/10 hover:text-white"
            onClick={() => fileInputRef.current?.click()}
            type="button"
          >
            <span className="sr-only">Attach files</span>
            <Paperclip className="h-4 w-4" />
          </button>

          <textarea
            className="min-h-10 max-h-40 flex-1 resize-none bg-transparent px-1 py-2 text-sm leading-6 text-white outline-none placeholder:text-white/40"
            disabled={disabled}
            onChange={(event) => onChange(event.target.value)}
            onInput={adjustTextareaHeight}
            onKeyDown={handleKeyDown}
            placeholder="Message NovaSphere..."
            ref={textareaRef}
            rows={1}
            value={value}
          />

          <div className="flex shrink-0 items-center gap-2">
            <button
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-slate-400 transition-all duration-200 ease-in-out hover:bg-white/10 hover:text-white"
              onClick={handleMicClick}
              type="button"
            >
              <span className="sr-only">Use microphone</span>
              <Mic className="h-4 w-4" />
            </button>
            <button
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#38bdf8] to-[#2563eb] text-white shadow-[0_0_0_1px_rgba(255,255,255,0.08)] transition-all duration-200 ease-in-out hover:scale-[1.03] hover:shadow-[0_10px_24px_rgba(37,99,235,0.24)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:scale-100"
              disabled={disabled || !value.trim()}
              type="submit"
            >
              <span className="sr-only">
                {isSending ? "Sending message" : "Send message"}
              </span>
              <SendHorizonal className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}
