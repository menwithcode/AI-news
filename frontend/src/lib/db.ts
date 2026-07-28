import { Pool } from "pg";
import { Article } from "./types";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const SELECT_COLUMNS = `id, title, original_url, source_name, ai_summary, ai_keywords, category, published_at, popularity_score`;

export type TimeRange = "24h" | "week" | "month" | "top";

export async function getArticles(params: {
  category?: string;
  q?: string;
  range?: TimeRange;
}): Promise<Article[]> {
  const range = params.range ?? "24h";
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

  let orderBy = "published_at DESC";
  if (range === "24h") {
    conditions.push(`published_at > NOW() - INTERVAL '24 hours'`);
  } else if (range === "week") {
    conditions.push(`published_at > NOW() - INTERVAL '7 days'`);
  } else if (range === "month") {
    conditions.push(`published_at > NOW() - INTERVAL '30 days'`);
  } else if (range === "top") {
    conditions.push(`popularity_score IS NOT NULL`);
    orderBy = "popularity_score DESC";
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

  const result = await pool.query(
    `SELECT ${SELECT_COLUMNS}
     FROM news_articles
     ${where}
     ORDER BY ${orderBy}
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

export async function savePushSubscription(sub: {
  endpoint: string;
  p256dh: string;
  auth: string;
}): Promise<void> {
  await pool.query(
    `INSERT INTO push_subscriptions (endpoint, p256dh, auth)
     VALUES ($1, $2, $3)
     ON CONFLICT (endpoint) DO NOTHING`,
    [sub.endpoint, sub.p256dh, sub.auth]
  );
}

const LOGIN_RATE_LIMIT_MAX = 5;
const LOGIN_RATE_LIMIT_WINDOW_MINUTES = 15;

export async function isLoginRateLimited(ip: string): Promise<boolean> {
  const result = await pool.query(
    `SELECT count(*) FROM login_attempts
     WHERE ip = $1 AND attempted_at > NOW() - INTERVAL '${LOGIN_RATE_LIMIT_WINDOW_MINUTES} minutes'`,
    [ip]
  );
  return parseInt(result.rows[0].count, 10) >= LOGIN_RATE_LIMIT_MAX;
}

export async function recordFailedLogin(ip: string): Promise<void> {
  await pool.query(`INSERT INTO login_attempts (ip) VALUES ($1)`, [ip]);
}

export async function clearLoginAttempts(ip: string): Promise<void> {
  await pool.query(`DELETE FROM login_attempts WHERE ip = $1`, [ip]);
}
