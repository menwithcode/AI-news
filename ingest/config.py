import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
