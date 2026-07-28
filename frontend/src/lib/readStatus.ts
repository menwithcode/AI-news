const STORAGE_KEY = "read-articles";

function loadReadIds(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return new Set(raw ? JSON.parse(raw) : []);
  } catch {
    return new Set();
  }
}

export function isRead(articleId: string): boolean {
  return loadReadIds().has(articleId);
}

export function markRead(articleId: string): void {
  if (typeof window === "undefined") return;
  try {
    const ids = loadReadIds();
    ids.add(articleId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
  } catch {
    // localStorage can fail (quota exceeded, private browsing) -- not critical
  }
}
