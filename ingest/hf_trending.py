import requests

from .sources import HF_MAX_RESULTS

MODELS_URL = "https://huggingface.co/api/models"
DATASETS_URL = "https://huggingface.co/api/datasets"


def fetch_trending_models() -> list[dict]:
    response = requests.get(
        MODELS_URL,
        params={"sort": "likes", "direction": -1, "limit": HF_MAX_RESULTS},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_trending_datasets() -> list[dict]:
    response = requests.get(
        DATASETS_URL,
        params={"sort": "likes", "direction": -1, "limit": HF_MAX_RESULTS},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
