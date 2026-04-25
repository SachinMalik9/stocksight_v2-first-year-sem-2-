import time
import logging
from datetime import datetime
import yfinance as yf
from textblob import TextBlob
from elasticsearch import Elasticsearch
import feedparser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.config import config

# Connect using credentials from environment variables (via config)
es = Elasticsearch(config.ELASTICSEARCH_URL)

SYMBOLS = ['TSLA', 'AAPL', 'MSFT', 'NVDA', 'GOOGL']

def fetch_and_score_news():
    for symbol in SYMBOLS:
        logger.info(f"Fetching RSS news for {symbol}...")
        try:
            rss_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                logger.warning(f"No RSS entries found for {symbol}")
                continue

            count = 0
            for entry in feed.entries:
                title = entry.get('title', '')
                source = entry.get('source', {}).get('title', 'Yahoo Finance')

                if not title:
                    continue

                blob = TextBlob(title)
                polarity = blob.sentiment.polarity

                sentiment_label = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"

                doc = {
                    "symbol": symbol,
                    "date": datetime.now().isoformat(),
                    "author": source,
                    "message": title,
                    "sentiment": sentiment_label,
                    "polarity": polarity
                }

                es.index(index="stocksight", document=doc)
                count += 1

            logger.info(f"✅ RSS SUCCESS! Analyzed and stored {count} articles for {symbol}")

        except Exception as e:
            logger.error(f"Error processing RSS for {symbol}: {e}")

if __name__ == "__main__":
    logger.info("Starting API-Free Sentiment Worker...")

    try:
        if es.ping():
            logger.info("✅ Successfully connected to Elasticsearch!")
        else:
            logger.error("❌ Elasticsearch is running but ping failed. Check credentials.")
    except Exception as e:
        logger.error(f"❌ Could not connect to Elasticsearch: {e}")

    while True:
        fetch_and_score_news()
        logger.info("Sleeping for 120 seconds...")
        time.sleep(120)
