"use client";

import { ChatProvider, useChat } from "@/lib/chatContext";
import ChatPanel from "@/components/ChatPanel";

function SplitView({ children }: { children: React.ReactNode }) {
  const { activeArticle } = useChat();

  return (
    <div className="flex min-h-screen">
      <div className={activeArticle ? "w-full md:w-1/2 md:overflow-y-auto" : "w-full"}>
        {children}
      </div>
      {activeArticle && (
        <div className="fixed inset-0 z-50 bg-white md:static md:z-auto md:w-1/2 md:h-screen md:sticky md:top-0 md:border-l">
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
