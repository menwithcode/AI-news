import time

import requests

from .config import SEMANTIC_SCHOLAR_API_KEY
from .db import get_uncited_arxiv_urls, update_citation_count

API_URL = "https://api.semanticscholar.org/graph/v1/paper/ARXIV:{arxiv_id}"
BATCH_SIZE = 20
DELAY_SECONDS = 1.1


def _arxiv_id_from_url(url: str) -> str | None:
    if "arxiv.org/abs/" not in url:
        return None
    return url.rstrip("/").split("/abs/")[-1]


def backfill_citations() -> None:
    if not SEMANTIC_SCHOLAR_API_KEY:
        print("No SEMANTIC_SCHOLAR_API_KEY set, skipping citation backfill.")
        return

    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}
    urls = get_uncited_arxiv_urls(BATCH_SIZE)
    updated = 0

    for url in urls:
        arxiv_id = _arxiv_id_from_url(url)
        if not arxiv_id:
            continue
        try:
            response = requests.get(
                API_URL.format(arxiv_id=arxiv_id),
                params={"fields": "citationCount"},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            citation_count = response.json().get("citationCount")
            if citation_count is not None:
                update_citation_count(url, citation_count)
                updated += 1
        except Exception as exc:
            print(f"Citation lookup failed for {url}: {exc}")
        time.sleep(DELAY_SECONDS)

    print(f"Backfilled citation counts for {updated} papers.")
