import requests

from .sources import ZENODO_MAX_RESULTS, ZENODO_QUERIES

SEARCH_URL = "https://zenodo.org/api/records"


def fetch_recent_records() -> list[dict]:
    seen_ids = set()
    records = []

    for query in ZENODO_QUERIES:
        response = requests.get(
            SEARCH_URL,
            params={"q": query, "sort": "mostrecent", "size": 20},
            timeout=30,
        )
        response.raise_for_status()
        for record in response.json().get("hits", {}).get("hits", []):
            record_id = record.get("id")
            if not record_id or record_id in seen_ids:
                continue
            seen_ids.add(record_id)
            records.append(record)

    records.sort(key=lambda r: r.get("created", ""), reverse=True)
    return records[:ZENODO_MAX_RESULTS]
