"use client";

import { useRouter, useSearchParams } from "next/navigation";

export default function FilterBar({ categories }: { categories: string[] }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("category") || "All";
  const options = ["All", ...categories];

  const select = (cat: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (cat === "All") params.delete("category");
    else params.set("category", cat);
    router.push(`/?${params.toString()}`);
  };

  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {options.map((c) => (
        <button
          key={c}
          onClick={() => select(c)}
          className={`px-3 py-1 rounded-full text-xs font-semibold border transition whitespace-nowrap ${
            current === c
              ? "bg-blue-600 text-white border-blue-600"
              : "bg-white text-gray-600 border-gray-200 hover:border-blue-300"
          }`}
        >
          {c}
        </button>
      ))}
    </div>
  );
}
