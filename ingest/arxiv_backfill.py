import calendar
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests

from .db import get_existing_urls, upsert_articles

API_URL = "https://export.arxiv.org/api/query"
PAGE_SIZE = 100
DELAY_SECONDS = 3.0
MAX_PAGES = 150
MAX_RETRIES = 5
SOURCE_NAME = "arXiv cs.AI"


def _fetch_page(page: int):
    params = {
        "search_query": "cat:cs.AI",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": page * PAGE_SIZE,
        "max_results": PAGE_SIZE,
    }
    backoff = 10
    for attempt in range(MAX_RETRIES):
        response = requests.get(API_URL, params=params, timeout=30)
        if response.status_code == 200:
            return feedparser.parse(response.text)
        print(
            f"Page {page}: got HTTP {response.status_code} "
            f"(attempt {attempt + 1}/{MAX_RETRIES}), backing off {backoff}s"
        )
        time.sleep(backoff)
        backoff *= 2
    raise RuntimeError(f"Page {page}: arXiv API did not return 200 after {MAX_RETRIES} retries")


def _entry_published(entry):
    parsed = getattr(entry, "published_parsed", None)
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def _row(entry, published: datetime) -> dict:
    tags = getattr(entry, "tags", None) or []
    return {
        "title": entry.title,
        "original_url": entry.link,
        "source_name": SOURCE_NAME,
        "ai_summary": getattr(entry, "summary", None),
        "ai_keywords": [tag["term"] for tag in tags],
        "category": "Research",
        "published_at": published.isoformat(),
        "popularity_score": None,
    }


def backfill_arxiv(days: int = 30) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    existing_urls = get_existing_urls()
    rows = []

    for page in range(MAX_PAGES):
        feed = _fetch_page(page)
        if not feed.entries:
            print(f"Page {page}: no entries returned, stopping.")
            break

        reached_cutoff = False
        for entry in feed.entries:
            published = _entry_published(entry)
            if published is None:
                continue
            if published < cutoff:
                reached_cutoff = True
                break
            if entry.link in existing_urls:
                continue
            rows.append(_row(entry, published))

        print(f"Page {page}: {len(rows)} rows queued so far")
        if reached_cutoff:
            break
        time.sleep(DELAY_SECONDS)

    upsert_articles(rows)
    print(f"arXiv backfill complete: upserted {len(rows)} papers from the last {days} days.")


if __name__ == "__main__":
    backfill_arxiv()
