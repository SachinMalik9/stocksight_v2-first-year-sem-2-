import sys
import os
import time
import logging
import requests
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.database import es_client
from src.config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def fetch_and_store_price(symbol):
    try:
        # Use a high-quality User-Agent to avoid the "Line 1 Column 1" JSON error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://finance.yahoo.com/'
        }

        # Use a direct query-string approach which is harder to block than the Ticker object
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1m"
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        # Extract price from the raw JSON response
        result = data.get("chart", {}).get("result", [])
        if not result:
            logger.warning(f"⚠️ No result in Yahoo response for {symbol}. Might be rate-limited.")
            return

        meta = result[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        volume = meta.get("regularMarketVolume", 0)

        if price:
            document = {
                "symbol": symbol,
                "price_last": float(price),
                "vol": int(volume),
                "date": datetime.now(timezone.utc).isoformat()
            }

            if es_client:
                es_client.index(index="stocksight", document=document)
                logger.info(f"✅ Indexed {symbol} at ${price:.2f}")
        else:
            logger.warning(f"⚠️ Could not find price field for {symbol}")

    except Exception as e:
        logger.error(f"❌ Scraping Error for {symbol}: {str(e)[:50]}")

if __name__ == "__main__":
    logger.info(f"🚀 Starting Price Worker (Direct API Mode). Tracking: {config.TRACKED_SYMBOLS}")
    
    while True:
        try:
            for symbol in config.TRACKED_SYMBOLS:
                fetch_and_store_price(symbol)
                time.sleep(10) # 10s delay between symbols is much safer
            
            logger.info("Cycle complete. Waiting 1 minute...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(10)