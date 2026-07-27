import { Pool } from "pg";
import { Article } from "./types";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const SELECT_COLUMNS = `id, title, original_url, source_name, ai_summary, ai_keywords, category, published_at, popularity_score`;

export async function getArticles(params: {
  category?: string;
  q?: string;
}): Promise<Article[]> {
  const conditions: string[] = [];
  const values: string[] = [];

  if (params.category) {
    values.push(params.category);
    conditions.push(`category = $${values.length}`);
  }
  if (params.q) {
    values.push(`%${params.q}%`);
    conditions.push(`title ILIKE $${values.length}`);
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

  const result = await pool.query(
    `SELECT ${SELECT_COLUMNS}
     FROM news_articles
     ${where}
     ORDER BY published_at DESC
     LIMIT 100`,
    values
  );
  return result.rows;
}

export async function getCategories(): Promise<string[]> {
  const result = await pool.query(
    `SELECT DISTINCT category FROM news_articles WHERE category IS NOT NULL ORDER BY category`
  );
  return result.rows.map((row) => row.category);
}

export async function getTopByCategory(
  category: string,
  limit = 10
): Promise<Article[]> {
  const result = await pool.query(
    `SELECT ${SELECT_COLUMNS}
     FROM news_articles
     WHERE category = $1 AND popularity_score IS NOT NULL
     ORDER BY popularity_score DESC
     LIMIT $2`,
    [category, limit]
  );
  return result.rows;
}
