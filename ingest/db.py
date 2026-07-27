import psycopg2
from psycopg2.extras import execute_values

from .config import DATABASE_URL

TABLE = "news_articles"

UPSERT_SQL = f"""
    INSERT INTO {TABLE}
        (title, original_url, source_name, ai_summary, ai_keywords, category, published_at, popularity_score)
    VALUES %s
    ON CONFLICT (original_url) DO UPDATE SET
        title = EXCLUDED.title,
        source_name = EXCLUDED.source_name,
        ai_summary = EXCLUDED.ai_summary,
        ai_keywords = EXCLUDED.ai_keywords,
        category = EXCLUDED.category,
        published_at = EXCLUDED.published_at,
        popularity_score = EXCLUDED.popularity_score
"""


def get_existing_urls() -> set[str]:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT original_url FROM {TABLE}")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def upsert_articles(rows: list[dict]) -> None:
    if not rows:
        return
    values = [
        (
            row["title"],
            row["original_url"],
            row["source_name"],
            row["ai_summary"],
            row["ai_keywords"],
            row["category"],
            row["published_at"],
            row.get("popularity_score"),
        )
        for row in rows
    ]
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            execute_values(cur, UPSERT_SQL, values)
        conn.commit()
    finally:
        conn.close()


def get_uncited_arxiv_urls(limit: int) -> list[str]:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT original_url FROM {TABLE}
                WHERE category = 'Research' AND popularity_score IS NULL
                ORDER BY published_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def update_citation_count(url: str, count: int) -> None:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {TABLE} SET popularity_score = %s WHERE original_url = %s",
                (count, url),
            )
        conn.commit()
    finally:
        conn.close()
