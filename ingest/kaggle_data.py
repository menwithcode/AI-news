import requests

from .sources import KAGGLE_MAX_RESULTS

DATASETS_URL = "https://www.kaggle.com/api/v1/datasets/list"
MODELS_URL = "https://www.kaggle.com/api/v1/models/list"


def fetch_trending_datasets() -> list[dict]:
    response = requests.get(
        DATASETS_URL,
        params={"sortBy": "hottest"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()[:KAGGLE_MAX_RESULTS]


def fetch_trending_models() -> list[dict]:
    response = requests.get(
        MODELS_URL,
        params={"sortBy": "voteCount"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("models", [])[:KAGGLE_MAX_RESULTS]
