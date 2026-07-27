from datetime import datetime, timedelta, timezone

import requests

from .sources import GITHUB_MAX_RESULTS, GITHUB_MIN_STARS, GITHUB_TOPICS

SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_trending_ai_repos() -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%d")
    topic_clause = " OR ".join(f"topic:{topic}" for topic in GITHUB_TOPICS)
    query = f"({topic_clause}) pushed:>{since}"

    response = requests.get(
        SEARCH_URL,
        params={"q": query, "sort": "stars", "order": "desc", "per_page": 50},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()

    repos = [
        repo
        for repo in response.json().get("items", [])
        if repo["stargazers_count"] >= GITHUB_MIN_STARS
    ]
    return repos[:GITHUB_MAX_RESULTS]
