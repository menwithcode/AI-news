import { Article } from "@/lib/types";

export default function ArticleCard({ item }: { item: Article }) {
  return (
    <article className="border rounded-xl p-5 mb-4 shadow-sm bg-white">
      <div className="flex gap-2 mb-2 flex-wrap">
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-700">
          {item.category}
        </span>
        <span className="text-xs text-gray-500">{item.source_name}</span>
        {item.ai_keywords.slice(0, 6).map((tag) => (
          <span
            key={tag}
            className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600"
          >
            {tag}
          </span>
        ))}
      </div>
      <h2 className="text-lg font-bold mb-1 leading-snug">
        <a
          href={item.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-blue-600 hover:underline"
        >
          {item.title}
        </a>
      </h2>
      <p className="text-xs text-gray-500 mb-2">
        {new Date(item.published_at).toLocaleString()}
      </p>
      {item.ai_summary && (
        <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded border-l-2 border-blue-300 line-clamp-3">
          {item.ai_summary}
        </p>
      )}
    </article>
  );
}
