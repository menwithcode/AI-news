import ArticleCard from "@/components/ArticleCard";
import FilterBar from "@/components/FilterBar";
import SearchInput from "@/components/SearchInput";
import TimeRangeFilter from "@/components/TimeRangeFilter";
import { getArticles, getCategories, TimeRange } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function Home({
  searchParams,
}: {
  searchParams?: { [key: string]: string | undefined };
}) {
  const category = searchParams?.category || undefined;
  const q = searchParams?.q || undefined;
  const range = (searchParams?.range as TimeRange) || "24h";

  const [articles, categories] = await Promise.all([
    getArticles({ category, q, range }),
    getCategories(),
  ]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b px-6 py-4">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl font-extrabold tracking-tight mb-1">
            AI Update <span className="text-blue-600">Hub</span>
          </h1>
          <p className="text-xs text-gray-500">
            AI news, research, models, and GitHub repos — no AI rewriting, titles as published
          </p>
        </div>
      </header>

      <section className="max-w-3xl mx-auto px-6 py-8">
        <div className="flex flex-col gap-3 mb-6">
          <TimeRangeFilter />
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <FilterBar categories={categories} />
            <SearchInput />
          </div>
        </div>

        <div className="space-y-2">
          {articles.length === 0 && (
            <p className="text-gray-400 text-sm">No updates found.</p>
          )}
          {articles.map((item) => (
            <ArticleCard key={item.id} item={item} />
          ))}
        </div>
      </section>
    </main>
  );
}
