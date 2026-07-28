"use client";

import { createContext, useContext, useState } from "react";
import { Article } from "./types";

interface ChatContextValue {
  activeArticle: Article | null;
  openChat: (article: Article) => void;
  closeChat: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [activeArticle, setActiveArticle] = useState<Article | null>(null);

  return (
    <ChatContext.Provider
      value={{
        activeArticle,
        openChat: setActiveArticle,
        closeChat: () => setActiveArticle(null),
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within a ChatProvider");
  return ctx;
}
