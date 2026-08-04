RSS_SOURCES = [
    {"name": "OpenAI Blog", "feed_url": "https://openai.com/news/rss.xml", "category": "News"},
    {"name": "Hugging Face Blog", "feed_url": "https://huggingface.co/blog/feed.xml", "category": "News"},
    {
        "name": "Google AI Blog",
        "feed_url": "https://blog.google/technology/ai/rss/",
        "category": "News",
    },
    {
        "name": "NVIDIA Blog",
        "feed_url": "https://blogs.nvidia.com/feed/",
        "category": "News",
    },
    {
        "name": "TechCrunch AI",
        "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "Review",
    },
    {
        "name": "The Verge AI",
        "feed_url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "Review",
    },
    {
        "name": "MIT Technology Review AI",
        "feed_url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "Review",
    },
    {
        "name": "Ars Technica AI",
        "feed_url": "https://arstechnica.com/ai/feed/",
        "category": "Review",
    },
    {
        "name": "Wired AI",
        "feed_url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "category": "Review",
    },
    {
        "name": "VentureBeat AI",
        "feed_url": "https://venturebeat.com/category/ai/feed/",
        "category": "Review",
    },
]

GITHUB_TOPICS = ["artificial-intelligence", "machine-learning", "llm", "deep-learning"]
GITHUB_MIN_STARS = 100
GITHUB_MAX_RESULTS = 15

GITLAB_TOPICS = ["artificial-intelligence", "machine-learning", "llm", "deep-learning"]
GITLAB_MIN_STARS = 20
GITLAB_MAX_RESULTS = 15

CODEBERG_TOPICS = ["machine-learning", "deep-learning", "llm", "artificial-intelligence"]
CODEBERG_MIN_STARS = 5
CODEBERG_MAX_RESULTS = 15

HF_MAX_RESULTS = 15

KAGGLE_MAX_RESULTS = 15

# Genuinely peer-reviewed/published papers only (no arXiv preprints).
DBLP_QUERIES = ["large language model", "deep learning", "reinforcement learning"]
DBLP_MAX_RESULTS = 15

OPENREVIEW_QUERIES = ["large language model", "deep learning", "neural network"]
OPENREVIEW_MAX_RESULTS = 15

ZENODO_QUERIES = ["machine learning dataset", "artificial intelligence dataset"]
ZENODO_MAX_RESULTS = 15
