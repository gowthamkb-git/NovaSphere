"use client";

import { FormEvent } from "react";

interface ChatInputProps {
  disabled?: boolean;
  isSending?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  value: string;
}

export function ChatInput({
  disabled = false,
  isSending = false,
  onChange,
  onSubmit,
  value,
}: ChatInputProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form
      className="border-t border-slate-200 bg-white/92 px-3 py-3"
      onSubmit={handleSubmit}
    >
      <div className="flex items-center gap-2">
        <input
          className="h-10 flex-1 rounded-[14px] border border-slate-300 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#6a8ef8] focus:ring-2 focus:ring-[#d8e3ff]"
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Type a message..."
          value={value}
        />
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#4f83f7] to-[#2f64e4] text-white transition duration-300 hover:scale-105 hover:shadow-[0_10px_24px_rgba(79,70,229,0.28)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:scale-100"
          disabled={disabled || !value.trim()}
          type="submit"
        >
          <span className="sr-only">
            {isSending ? "Sending message" : "Send message"}
          </span>
          <svg
            aria-hidden="true"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              d="M4 12.75L20 4l-5.25 16-2.75-5.25L4 12.75Z"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.7"
            />
          </svg>
        </button>
      </div>
    </form>
  );
}
