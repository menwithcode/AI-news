import requests

from .sources import OPENREVIEW_MAX_RESULTS, OPENREVIEW_QUERIES

SEARCH_URL = "https://api2.openreview.net/notes/search"

# Venue strings that indicate the paper hasn't actually been accepted/
# published yet (still under review, an anonymized submission), or that
# "venue" just means an arXiv preprint listing rather than a real
# peer-reviewed venue -- "CoRR" is the formal bibliographic name for
# arXiv's CS repository itself, not a venue that reviews anything.
_UNPUBLISHED_MARKERS = ("submitted", "blind", "under review", "anonymous", "corr")


def fetch_published_papers() -> list[dict]:
    seen_ids = set()
    papers = []

    for query in OPENREVIEW_QUERIES:
        response = requests.get(
            SEARCH_URL,
            params={"query": query, "limit": 50},
            timeout=30,
        )
        response.raise_for_status()
        for note in response.json().get("notes", []):
            note_id = note.get("id")
            content = note.get("content", {})
            venue = (content.get("venue", {}) or {}).get("value", "")
            pdate = note.get("pdate")
            title = (content.get("title", {}) or {}).get("value")

            if not note_id or note_id in seen_ids:
                continue
            if not venue or not pdate or not title:
                continue
            if any(marker in venue.lower() for marker in _UNPUBLISHED_MARKERS):
                continue

            seen_ids.add(note_id)
            papers.append(note)

    papers.sort(key=lambda n: n["pdate"], reverse=True)
    return papers[:OPENREVIEW_MAX_RESULTS]
