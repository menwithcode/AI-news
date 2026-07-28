"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "@/lib/chatContext";
import { Article } from "@/lib/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  reasoning?: string;
  stopped?: boolean;
}

function buildSystemPrompt(article: Article): string {
  return (
    `You are a helpful assistant embedded in a personal AI news dashboard. ` +
    `Keep answers SHORT and in plain, simple language: a few sentences or a ` +
    `short bullet list of the main points. Do NOT write long multi-section ` +
    `breakdowns, tables, or heavy jargon/technical deep-dives unless the ` +
    `user explicitly asks you to go deeper or explain in detail.\n\n` +
    `The user is looking at this item:\n\n` +
    `Title: ${article.title}\n` +
    `Category: ${article.category}\n` +
    `Source: ${article.source_name}\n` +
    `Link: ${article.original_url}\n` +
    (article.ai_summary ? `Description: ${article.ai_summary}\n` : "")
  );
}

export default function ChatPanel() {
  const { activeArticle, closeChat } = useChat();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!activeArticle) return;
    setMessages([]);
    send("What's new or notable about this? Summarize the key points.", []);
    return () => {
      abortControllerRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeArticle?.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(userText: string, history: Message[]) {
    if (!activeArticle) return;
    const nextMessages = [...history, { role: "user" as const, content: userText }];
    const assistantMessage: Message = { role: "assistant", content: "" };
    setMessages([...nextMessages, assistantMessage]);
    setLoading(true);

    const apiMessages = [
      { role: "system", content: buildSystemPrompt(activeArticle) },
      ...nextMessages,
    ];

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: apiMessages }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(await res.text());
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) continue;
          const data = trimmed.slice(5).trim();
          if (data === "[DONE]") continue;
          try {
            const parsed = JSON.parse(data);
            const delta = parsed.choices?.[0]?.delta;
            if (delta?.reasoning) {
              assistantMessage.reasoning = (assistantMessage.reasoning ?? "") + delta.reasoning;
              setMessages([...nextMessages, { ...assistantMessage }]);
            }
            if (delta?.content) {
              assistantMessage.content += delta.content;
              setMessages([...nextMessages, { ...assistantMessage }]);
            }
          } catch {
            // ignore malformed/partial SSE chunks
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        assistantMessage.stopped = true;
        setMessages([...nextMessages, { ...assistantMessage }]);
      } else {
        assistantMessage.content =
          assistantMessage.content || "Sorry, something went wrong reaching the AI.";
        setMessages([...nextMessages, { ...assistantMessage }]);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const text = input;
    setInput("");
    send(text, messages);
  }

  function handleStop() {
    abortControllerRef.current?.abort();
  }

  if (!activeArticle) return null;

  return (
    <div className="flex flex-col h-screen sticky top-0">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="min-w-0">
          <p className="text-xs text-gray-500">Chatting about</p>
          <p className="text-sm font-semibold truncate">{activeArticle.title}</p>
        </div>
        <button
          onClick={closeChat}
          className="text-gray-400 hover:text-gray-700 text-xl leading-none px-2"
        >
          &times;
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
              m.role === "user"
                ? "bg-blue-600 text-white ml-auto whitespace-pre-wrap"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {m.role === "assistant" && !m.content && m.reasoning ? (
              <span className="italic text-gray-400">
                Thinking… {m.reasoning.slice(-120)}
              </span>
            ) : m.role === "assistant" && m.content ? (
              <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-headings:my-2">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
              </div>
            ) : (
              m.content || (loading && i === messages.length - 1 ? "…" : "")
            )}
            {m.stopped && (
              <div className="text-xs text-gray-400 mt-1 not-italic">— stopped</div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a follow-up..."
          disabled={loading}
          className="flex-1 text-sm px-3 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
        />
        {loading ? (
          <button
            type="button"
            onClick={handleStop}
            className="px-4 py-2 text-sm font-semibold bg-red-600 text-white rounded-lg"
          >
            Stop
          </button>
        ) : (
          <button
            type="submit"
            className="px-4 py-2 text-sm font-semibold bg-blue-600 text-white rounded-lg disabled:opacity-50"
          >
            Send
          </button>
        )}
      </form>
    </div>
  );
}
