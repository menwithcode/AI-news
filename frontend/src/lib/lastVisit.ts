const STORAGE_KEY = "last-visit";

export function getLastVisit(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setLastVisit(iso: string): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, iso);
  } catch {
    // localStorage can fail (quota exceeded, private browsing) -- not critical
  }
}
