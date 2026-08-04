RSS_SOURCES = [
    {"name": "OpenAI Blog", "feed_url": "https://openai.com/news/rss.xml", "category": "News"},
    {"name": "Hugging Face Blog", "feed_url": "https://huggingface.co/blog/feed.xml", "category": "News"},
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
]

GITHUB_TOPICS = ["artificial-intelligence", "machine-learning", "llm", "deep-learning"]
GITHUB_MIN_STARS = 100
GITHUB_MAX_RESULTS = 15

GITLAB_TOPICS = ["artificial-intelligence", "machine-learning", "llm", "deep-learning"]
GITLAB_MIN_STARS = 20
GITLAB_MAX_RESULTS = 15

HF_MAX_RESULTS = 15

KAGGLE_MAX_RESULTS = 15

# Genuinely peer-reviewed/published papers only (no arXiv preprints).
DBLP_QUERIES = ["large language model", "deep learning", "reinforcement learning"]
DBLP_MAX_RESULTS = 15

OPENREVIEW_QUERIES = ["large language model", "deep learning", "neural network"]
OPENREVIEW_MAX_RESULTS = 15
