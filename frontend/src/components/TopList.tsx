import ArticleCard from "@/components/ArticleCard";
import { Article } from "@/lib/types";

export default function TopList({
  title,
  items,
}: {
  title: string;
  items: Article[];
}) {
  if (items.length === 0) return null;

  return (
    <section className="mb-10">
      <h2 className="text-sm font-bold uppercase tracking-wide text-gray-500 mb-3">
        {title}
      </h2>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {items.map((item) => (
          <div key={item.id} className="min-w-[320px] max-w-[320px] flex-shrink-0">
            <ArticleCard item={item} />
          </div>
        ))}
      </div>
    </section>
  );
}
