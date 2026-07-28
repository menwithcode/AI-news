"use client";

import { useChat } from "@/lib/chatContext";
import { Article } from "@/lib/types";

export default function AskAIButton({ item }: { item: Article }) {
  const { openChat } = useChat();

  return (
    <button
      onClick={() => openChat(item)}
      title="Ask AI about this"
      className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
    >
      <span aria-hidden>✨</span>
      Ask AI
    </button>
  );
}
