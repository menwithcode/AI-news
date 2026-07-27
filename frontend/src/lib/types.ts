export interface Article {
  id: string;
  title: string;
  original_url: string;
  source_name: string;
  ai_summary: string | null;
  ai_keywords: string[];
  category: string | null;
  published_at: string;
  popularity_score: number | null;
}
