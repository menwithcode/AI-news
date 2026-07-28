export interface StoredMessage {
  role: "user" | "assistant";
  content: string;
  reasoning?: string;
  stopped?: boolean;
}

function storageKey(articleId: string): string {
  return `chat:${articleId}`;
}

export function loadChat(articleId: string): StoredMessage[] | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(storageKey(articleId));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveChat(articleId: string, messages: StoredMessage[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(storageKey(articleId), JSON.stringify(messages));
  } catch {
    // localStorage can fail (quota exceeded, private browsing) -- not critical
  }
}
