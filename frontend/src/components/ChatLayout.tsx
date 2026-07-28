"use client";

import { ChatProvider, useChat } from "@/lib/chatContext";
import ChatPanel from "@/components/ChatPanel";

function SplitView({ children }: { children: React.ReactNode }) {
  const { activeArticle } = useChat();

  return (
    <div className="flex min-h-screen">
      <div className={activeArticle ? "w-1/2 overflow-y-auto" : "w-full"}>
        {children}
      </div>
      {activeArticle && (
        <div className="w-1/2 border-l bg-white">
          <ChatPanel />
        </div>
      )}
    </div>
  );
}

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <ChatProvider>
      <SplitView>{children}</SplitView>
    </ChatProvider>
  );
}
