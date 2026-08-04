import calendar
from datetime import datetime, timedelta, timezone

import feedparser
from bs4 import BeautifulSoup

from .citations import backfill_citations
from .codeberg_repos import fetch_trending_ai_repos as fetch_codeberg_repos
from .config import LOOKBACK_HOURS
from .db import get_existing_urls, upsert_articles
from .dblp import fetch_published_papers as fetch_dblp_papers
from .github_repos import fetch_trending_ai_repos as fetch_github_repos
from .gitlab_repos import fetch_trending_ai_repos as fetch_gitlab_repos
from .hf_trending import fetch_trending_datasets as fetch_hf_datasets
from .hf_trending import fetch_trending_models as fetch_hf_models
from .kaggle_data import fetch_trending_datasets as fetch_kaggle_datasets
from .kaggle_data import fetch_trending_models as fetch_kaggle_models
from .openreview import fetch_published_papers as fetch_openreview_papers
from .push_notify import notify_new_items
from .sources import RSS_SOURCES
from .zenodo import fetch_recent_records as fetch_zenodo_records


def _strip_html(html: str | None) -> str | None:
    if not html:
        return None
    return BeautifulSoup(html, "html.parser").get_text().strip() or None

CODE_REPO_CATEGORY = "Code Repo"


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


def _repo_row(source_name: str, repo: dict, *, url: str, stars: int, pushed_at: str) -> dict:
    published = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    return {
        "title": repo["title"],
        "original_url": url,
        "source_name": source_name,
        "ai_summary": repo.get("description"),
        "ai_keywords": repo.get("topics", []),
        "category": CODE_REPO_CATEGORY,
        "published_at": published.isoformat(),
        "popularity_score": stars,
    }


def _github_row(repo: dict) -> dict:
    return _repo_row(
        "GitHub",
        {"title": repo["full_name"], "description": repo.get("description"), "topics": repo.get("topics", [])},
        url=repo["html_url"],
        stars=repo["stargazers_count"],
        pushed_at=repo["pushed_at"],
    )


def _gitlab_row(repo: dict) -> dict:
    return _repo_row(
        "GitLab",
        {"title": repo["name_with_namespace"], "description": repo.get("description"), "topics": repo.get("topics", [])},
        url=repo["web_url"],
        stars=repo["star_count"],
        pushed_at=repo["last_activity_at"],
    )


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


def _kaggle_dataset_row(item: dict) -> dict:
    return {
        "title": item["title"],
        "original_url": item["url"],
        "source_name": "Kaggle",
        "ai_summary": item.get("subtitle"),
        "ai_keywords": [tag["name"] for tag in item.get("tags", [])],
        "category": "Dataset",
        "published_at": item["lastUpdated"],
        "popularity_score": item.get("voteCount"),
    }


def _kaggle_model_row(item: dict) -> dict:
    return {
        "title": item["title"],
        "original_url": f"https://www.kaggle.com/models/{item['ref']}",
        "source_name": "Kaggle",
        "ai_summary": item.get("subtitle"),
        "ai_keywords": [],
        "category": "Model",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "popularity_score": item.get("voteCount"),
    }


def _dblp_row(paper: dict) -> dict:
    published = datetime(int(paper["year"]), 1, 1, tzinfo=timezone.utc)
    return {
        "title": paper["title"],
        "original_url": paper.get("ee") or paper["url"],
        "source_name": f"DBLP ({paper.get('venue', 'unknown venue')})",
        "ai_summary": None,
        "ai_keywords": [],
        "category": "Research",
        "published_at": published.isoformat(),
        "popularity_score": None,
    }


def _openreview_row(note: dict) -> dict:
    content = note["content"]
    published = datetime.fromtimestamp(note["pdate"] / 1000, tz=timezone.utc)
    venue = content.get("venue", {}).get("value", "OpenReview")
    return {
        "title": content["title"]["value"],
        "original_url": content.get("html", {}).get("value")
        or f"https://openreview.net/forum?id={note['id']}",
        "source_name": f"OpenReview ({venue})",
        "ai_summary": (content.get("abstract", {}) or {}).get("value"),
        "ai_keywords": (content.get("keywords", {}) or {}).get("value", []),
        "category": "Research",
        "published_at": published.isoformat(),
        "popularity_score": None,
    }


def _zenodo_row(record: dict) -> dict:
    metadata = record["metadata"]
    keywords = []
    for kw in metadata.get("keywords", []):
        keywords.extend(part.strip() for part in kw.split(","))
    return {
        "title": metadata["title"],
        "original_url": record["doi_url"],
        "source_name": "Zenodo",
        "ai_summary": _strip_html(metadata.get("description")),
        "ai_keywords": keywords[:20],
        "category": "Dataset",
        "published_at": record["created"],
        "popularity_score": None,
    }


def _codeberg_row(repo: dict) -> dict:
    return {
        "title": repo["full_name"],
        "original_url": repo["html_url"],
        "source_name": "Codeberg",
        "ai_summary": repo.get("description"),
        "ai_keywords": repo.get("topics", []),
        "category": CODE_REPO_CATEGORY,
        "published_at": repo["updated_at"],
        "popularity_score": repo["stars_count"],
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
        rows.extend(_github_row(repo) for repo in fetch_github_repos(hours=LOOKBACK_HOURS))
    except Exception as exc:
        print(f"GitHub repo fetch failed: {exc}")

    try:
        rows.extend(_gitlab_row(repo) for repo in fetch_gitlab_repos(hours=LOOKBACK_HOURS))
    except Exception as exc:
        print(f"GitLab repo fetch failed: {exc}")

    try:
        rows.extend(_hf_row("Model", model) for model in fetch_hf_models())
    except Exception as exc:
        print(f"HF model fetch failed: {exc}")

    try:
        rows.extend(_hf_row("Dataset", dataset) for dataset in fetch_hf_datasets())
    except Exception as exc:
        print(f"HF dataset fetch failed: {exc}")

    try:
        rows.extend(_kaggle_model_row(model) for model in fetch_kaggle_models())
    except Exception as exc:
        print(f"Kaggle model fetch failed: {exc}")

    try:
        rows.extend(_kaggle_dataset_row(dataset) for dataset in fetch_kaggle_datasets())
    except Exception as exc:
        print(f"Kaggle dataset fetch failed: {exc}")

    try:
        rows.extend(_dblp_row(paper) for paper in fetch_dblp_papers())
    except Exception as exc:
        print(f"DBLP fetch failed: {exc}")

    try:
        rows.extend(_openreview_row(note) for note in fetch_openreview_papers())
    except Exception as exc:
        print(f"OpenReview fetch failed: {exc}")

    try:
        rows.extend(_zenodo_row(record) for record in fetch_zenodo_records())
    except Exception as exc:
        print(f"Zenodo fetch failed: {exc}")

    try:
        rows.extend(_codeberg_row(repo) for repo in fetch_codeberg_repos(hours=LOOKBACK_HOURS))
    except Exception as exc:
        print(f"Codeberg fetch failed: {exc}")

    # GitHub/GitLab/Codeberg/HF/Kaggle rows always get re-appended (to refresh
    # stars/likes/votes) even when already in the DB, so len(rows)
    # overcounts "new" items. Only rows whose URL wasn't already present
    # before this run are genuinely new -- that's what should drive the
    # notification count.
    new_count = sum(1 for row in rows if row["original_url"] not in existing_urls)

    upsert_articles(rows)
    print(f"Upserted {len(rows)} items ({new_count} new).")

    notify_new_items(new_count)

    backfill_citations()


if __name__ == "__main__":
    main()
