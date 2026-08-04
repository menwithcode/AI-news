from datetime import datetime, timedelta, timezone

import requests

from .sources import GITLAB_MAX_RESULTS, GITLAB_MIN_STARS, GITLAB_TOPICS

SEARCH_URL = "https://gitlab.com/api/v4/projects"


def fetch_trending_ai_repos(hours: int = 24) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    seen_ids = set()
    repos = []
    for topic in GITLAB_TOPICS:
        response = requests.get(
            SEARCH_URL,
            params={
                "topic": topic,
                "last_activity_after": since,
                "order_by": "star_count",
                "sort": "desc",
                "per_page": 50,
            },
            timeout=30,
        )
        response.raise_for_status()
        for repo in response.json():
            if repo["id"] in seen_ids or repo["star_count"] < GITLAB_MIN_STARS:
                continue
            seen_ids.add(repo["id"])
            repos.append(repo)

    repos.sort(key=lambda r: r["star_count"], reverse=True)
    return repos[:GITLAB_MAX_RESULTS]
