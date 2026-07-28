"use client";

import { useEffect, useState } from "react";
import { Article } from "@/lib/types";
import { getLastVisit, setLastVisit } from "@/lib/lastVisit";

export default function NewSinceLastVisit({ articles }: { articles: Article[] }) {
  const [newCount, setNewCount] = useState(0);

  useEffect(() => {
    const last = getLastVisit();
    if (last) {
      const lastDate = new Date(last);
      const count = articles.filter(
        (a) => new Date(a.published_at) > lastDate
      ).length;
      setNewCount(count);
    }
    setLastVisit(new Date().toISOString());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (newCount === 0) return null;

  return (
    <div className="mb-4 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-sm text-amber-800">
      {newCount} new item{newCount === 1 ? "" : "s"} since your last visit
    </div>
  );
}
