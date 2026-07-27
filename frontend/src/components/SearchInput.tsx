"use client";

import { useRouter, useSearchParams } from "next/navigation";

export default function SearchInput() {
  const router = useRouter();
  const params = useSearchParams();
  const current = params.get("q") || "";

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const q = formData.get("q") as string;
    const urlParams = new URLSearchParams(params.toString());
    if (q) urlParams.set("q", q);
    else urlParams.delete("q");
    router.push(`/?${urlParams.toString()}`);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full md:w-72">
      <input
        name="q"
        defaultValue={current}
        placeholder="Search titles..."
        className="w-full px-3 py-1.5 text-xs rounded-lg border bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </form>
  );
}
