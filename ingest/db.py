from supabase import Client, create_client

from .config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

TABLE = "news_articles"


def get_existing_urls() -> set[str]:
    response = _client.table(TABLE).select("original_url").execute()
    return {row["original_url"] for row in response.data}


def upsert_articles(rows: list[dict]) -> None:
    if not rows:
        return
    _client.table(TABLE).upsert(rows, on_conflict="original_url").execute()
