import { ChatSource } from "@/lib/api";

interface ChatMessageProps {
  content: string;
  role: "user" | "assistant";
  sources?: ChatSource[];
}

export function ChatMessage({
  content,
  role,
  sources,
}: ChatMessageProps) {
  const isAssistant = role === "assistant";

  return (
    <div className={`flex ${isAssistant ? "justify-start" : "justify-end"}`}>
      <article
        className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-[0.95rem] shadow-sm transition ${
          isAssistant
            ? "border border-slate-200 bg-[#eef1f7] text-[#4a5482]"
            : "bg-gradient-to-br from-[#4f83f7] to-[#3167e6] text-white"
        }`}
      >
        <p className="whitespace-pre-wrap leading-6">{content}</p>
        {isAssistant && sources && sources.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {sources.map((source, index) => (
              <span
                className="rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[11px] font-medium text-sky-900"
                key={`${source.source}-${index}`}
              >
                {source.source}
                {source.page ? ` | p.${source.page}` : ""}
              </span>
            ))}
          </div>
        ) : null}
      </article>
    </div>
  );
}
