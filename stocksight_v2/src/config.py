import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    # Database Configuration
    # Prioritize the full URL from .env, fallback to localhost
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

    # Individual fields for scripts that might need them separately
    ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
    ES_USER = os.getenv("ES_USER", "elastic")
    ES_PASSWORD = os.getenv("ES_PASSWORD", "")

# Twitter / X API credentials — loaded from .env only, no hardcoded fallbacks
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Target Tracking
TRACKED_SYMBOLS = ["TSLA", "AAPL", "MSFT", "NVDA", "GOOGL"]

# Keyword filters for sentiment analysis
REQUIRED_TOKENS = ["neuralink", "solar", "tesla", "tsla", "elonmusk", "elon", "spacex", "google", "googl", "alphabet"]
IGNORED_TOKENS = ["win", "giveaway", "crypto", "pump"]

config = Config()
