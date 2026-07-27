import calendar
from datetime import datetime, timedelta, timezone

import feedparser

from .db import get_existing_urls, upsert_articles
from .github_repos import fetch_trending_ai_repos
from .sources import RSS_SOURCES

CUTOFF_HOURS = 24


def _entry_published(entry):
    parsed = getattr(entry, "published_parsed", None)
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def _rss_row(source: dict, entry, published: datetime) -> dict:
    tags = getattr(entry, "tags", None) or []
    return {
        "title": entry.title,
        "original_url": entry.link,
        "source_name": source["name"],
        "ai_summary": getattr(entry, "summary", None),
        "ai_keywords": [tag["term"] for tag in tags],
        "category": source["category"],
        "published_at": published.isoformat(),
    }


def _github_row(repo: dict) -> dict:
    published = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
    return {
        "title": repo["full_name"],
        "original_url": repo["html_url"],
        "source_name": "GitHub",
        "ai_summary": repo.get("description"),
        "ai_keywords": repo.get("topics", []),
        "category": "GitHub Repo",
        "published_at": published.isoformat(),
    }


def main() -> None:
    existing_urls = get_existing_urls()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    new_rows = []

    for source in RSS_SOURCES:
        feed = feedparser.parse(source["feed_url"])
        for entry in feed.entries:
            if entry.link in existing_urls:
                continue
            published = _entry_published(entry)
            if published is None or published < cutoff:
                continue
            new_rows.append(_rss_row(source, entry, published))

    try:
        for repo in fetch_trending_ai_repos():
            if repo["html_url"] in existing_urls:
                continue
            new_rows.append(_github_row(repo))
    except Exception as exc:
        print(f"GitHub repo fetch failed: {exc}")

    upsert_articles(new_rows)
    print(f"Ingested {len(new_rows)} new items.")


if __name__ == "__main__":
    main()
