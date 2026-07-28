import calendar
from datetime import datetime, timedelta, timezone

import feedparser

from .citations import backfill_citations
from .config import LOOKBACK_HOURS
from .db import get_existing_urls, upsert_articles
from .github_repos import fetch_trending_ai_repos
from .hf_trending import fetch_trending_datasets, fetch_trending_models
from .push_notify import notify_new_items
from .sources import RSS_SOURCES


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
        "popularity_score": None,
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
        "popularity_score": repo["stargazers_count"],
    }


def _hf_row(category: str, item: dict) -> dict:
    published = datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00"))
    url_prefix = "datasets/" if category == "Dataset" else ""
    return {
        "title": item["id"],
        "original_url": f"https://huggingface.co/{url_prefix}{item['id']}",
        "source_name": "Hugging Face",
        "ai_summary": item.get("description"),
        "ai_keywords": item.get("tags", [])[:20],
        "category": category,
        "published_at": published.isoformat(),
        "popularity_score": item.get("likes"),
    }


def main() -> None:
    existing_urls = get_existing_urls()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    rows = []

    for source in RSS_SOURCES:
        feed = feedparser.parse(source["feed_url"])
        for entry in feed.entries:
            if entry.link in existing_urls:
                continue
            published = _entry_published(entry)
            if published is None or published < cutoff:
                continue
            rows.append(_rss_row(source, entry, published))

    try:
        rows.extend(
            _github_row(repo) for repo in fetch_trending_ai_repos(hours=LOOKBACK_HOURS)
        )
    except Exception as exc:
        print(f"GitHub repo fetch failed: {exc}")

    try:
        rows.extend(_hf_row("Model", model) for model in fetch_trending_models())
    except Exception as exc:
        print(f"HF model fetch failed: {exc}")

    try:
        rows.extend(_hf_row("Dataset", dataset) for dataset in fetch_trending_datasets())
    except Exception as exc:
        print(f"HF dataset fetch failed: {exc}")

    # GitHub/HF rows always get re-appended (to refresh stars/likes) even
    # when already in the DB, so len(rows) overcounts "new" items. Only
    # rows whose URL wasn't already present before this run are genuinely
    # new -- that's what should drive the notification count.
    new_count = sum(1 for row in rows if row["original_url"] not in existing_urls)

    upsert_articles(rows)
    print(f"Upserted {len(rows)} items ({new_count} new).")

    notify_new_items(new_count)

    backfill_citations()


if __name__ == "__main__":
    main()
