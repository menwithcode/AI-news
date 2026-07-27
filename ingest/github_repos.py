from datetime import datetime, timedelta, timezone

import requests

from .sources import GITHUB_MAX_RESULTS, GITHUB_MIN_STARS, GITHUB_TOPICS

SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_trending_ai_repos(hours: int = 24) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d")

    seen_ids = set()
    repos = []
    for topic in GITHUB_TOPICS:
        response = requests.get(
            SEARCH_URL,
            params={
                "q": f"topic:{topic} pushed:>{since}",
                "sort": "stars",
                "order": "desc",
                "per_page": 50,
            },
            headers={"Accept": "application/vnd.github+json"},
            timeout=30,
        )
        response.raise_for_status()
        for repo in response.json().get("items", []):
            if repo["id"] in seen_ids or repo["stargazers_count"] < GITHUB_MIN_STARS:
                continue
            seen_ids.add(repo["id"])
            repos.append(repo)

    repos.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return repos[:GITHUB_MAX_RESULTS]
