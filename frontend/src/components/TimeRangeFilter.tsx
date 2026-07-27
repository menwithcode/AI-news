"use client";

import { useRouter, useSearchParams } from "next/navigation";

const RANGES = [
  { value: "24h", label: "Last 24 Hours" },
  { value: "week", label: "Last Week" },
  { value: "month", label: "Last Month" },
  { value: "top", label: "Top Rated" },
];

export default function TimeRangeFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("range") || "24h";

  const select = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("range", value);
    router.push(`/?${params.toString()}`);
  };

  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {RANGES.map((r) => (
        <button
          key={r.value}
          onClick={() => select(r.value)}
          className={`px-3 py-1 rounded-full text-xs font-semibold border transition whitespace-nowrap ${
            current === r.value
              ? "bg-amber-500 text-white border-amber-500"
              : "bg-white text-gray-600 border-gray-200 hover:border-amber-300"
          }`}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}
