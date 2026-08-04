from datetime import datetime, timedelta, timezone

import requests

from .sources import CODEBERG_MAX_RESULTS, CODEBERG_MIN_STARS, CODEBERG_TOPICS

SEARCH_URL = "https://codeberg.org/api/v1/repos/search"


def fetch_trending_ai_repos(hours: int = 24) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    seen_ids = set()
    repos = []
    for topic in CODEBERG_TOPICS:
        response = requests.get(
            SEARCH_URL,
            params={"q": topic, "sort": "stars", "order": "desc", "limit": 50},
            timeout=30,
        )
        response.raise_for_status()
        for repo in response.json().get("data", []):
            if repo["id"] in seen_ids or repo["stars_count"] < CODEBERG_MIN_STARS:
                continue
            updated = datetime.fromisoformat(repo["updated_at"])
            if updated < since:
                continue
            seen_ids.add(repo["id"])
            repos.append(repo)

    repos.sort(key=lambda r: r["stars_count"], reverse=True)
    return repos[:CODEBERG_MAX_RESULTS]
