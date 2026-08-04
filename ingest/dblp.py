import requests

from .sources import DBLP_MAX_RESULTS, DBLP_QUERIES

SEARCH_URL = "https://dblp.org/search/publ/api"


def fetch_published_papers() -> list[dict]:
    seen_keys = set()
    papers = []

    for query in DBLP_QUERIES:
        response = requests.get(
            SEARCH_URL,
            params={"q": query, "format": "json", "h": 30},
            timeout=30,
        )
        response.raise_for_status()
        hits = response.json().get("result", {}).get("hits", {}).get("hit", [])
        for hit in hits:
            info = hit.get("info", {})
            key = info.get("key")
            year = info.get("year")
            if not key or key in seen_keys or not year:
                continue
            seen_keys.add(key)
            papers.append(info)

    papers.sort(key=lambda p: p.get("year", "0"), reverse=True)
    return papers[:DBLP_MAX_RESULTS]
