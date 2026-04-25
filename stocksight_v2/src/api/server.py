import sys
import os
import logging
import time  # <-- Added for caching
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf  # <-- Moved to top for instant loading!

# This ensures we can import from src regardless of where the script is executed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.database import es_client

app = Flask(__name__)
# Enable CORS for all routes so the HTML frontend can fetch data
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 🚀 IN-MEMORY CACHE DICTIONARY
# This stores historical data in RAM so switching tabs is instant
history_cache = {}

# ===== POLARITY =====
@app.route("/summary", methods=["GET"])
def summary():
    if not es_client:
        return jsonify({"polarity": 0, "symbol": "N/A"}), 503

    try:
        symbol = request.args.get("symbol", "TSLA")
        # Ensure we match the symbol exactly and sort by newest first
        query = {"match": {"symbol": symbol}}

        res = es_client.search(
            index="stocksight",
            body={
                "query": query,
                "sort": [{"date": {"order": "desc"}}] # Get the latest news
            },
            size=100
        )

        total, count = 0, 0
        for hit in res["hits"]["hits"]:
            pol = hit["_source"].get("polarity")
            if pol is not None:
                total += float(pol) # Force it to a float just in case
                count += 1

        avg = total / count if count > 0 else 0.0
        
        # We return the polarity AND the symbol so the dashboard knows it's the right data
        return jsonify({
            "polarity": round(avg, 2),
            "symbol": symbol,
            "count": count
        })

    except Exception as e:
        logger.error(f"Error in /summary endpoint: {e}")
        return jsonify({"polarity": 0, "symbol": "ERROR"}), 500


# ===== TWEETS =====
@app.route("/tweets", methods=["GET"])
def tweets():
    if not es_client:
        return jsonify([]), 503

    try:
        symbol = request.args.get("symbol")
        must_clauses = [{"exists": {"field": "message"}}]
        if symbol:
            must_clauses.append({"match": {"symbol": symbol}})

        res = es_client.search(
            index="stocksight",
            body={
                "query": {"bool": {"must": must_clauses}},
                "sort": [{"date": {"order": "desc"}}],
                "size": 15
            }
        )

        data = []
        for hit in res["hits"]["hits"]:
            src = hit["_source"]
            data.append({
                "author": src.get("author", "unknown"),
                "message": src.get("message", ""),
                "sentiment": src.get("sentiment", "neutral"),
                "polarity": src.get("polarity", 0)
            })

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error in /tweets endpoint: {e}")
        return jsonify([]), 500


# ===== PRICE =====
@app.route("/price", methods=["GET"])
def price():
    try:
        symbol = request.args.get("symbol", "TSLA")
        time_range = request.args.get("range", "1d")
# ─── SCENARIO A: LIVE 1-DAY DATA (From Elasticsearch, only Today) ───
        if time_range == "1d":
            if not es_client:
                return jsonify({"labels": [], "prices": []}), 503

            # We use "now/d" to only get data from the start of the current day
            res = es_client.search(
                index="stocksight",
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"exists": {"field": "price_last"}},
                                {"match": {"symbol": symbol}}
                            ],
                            "filter": [
                                {"range": {"date": {"gte": "now/d"}}} 
                            ]
                        }
                    },
                    "sort": [{"date": {"order": "asc"}}],
                    "size": 1000 # Increased to show the WHOLE day
                }
            )

            labels = []
            prices = []
            for hit in res["hits"]["hits"]:
                src = hit["_source"]
                raw_date = src.get("date", "")
                # Format time to HH:MM:SS for a clean X-axis
                label = raw_date[11:19] if len(raw_date) >= 19 else raw_date
                labels.append(label)
                prices.append(src.get("price_last", 0))

            return jsonify({"labels": labels, "prices": prices})

        # ─── SCENARIO B: HISTORICAL DATA (Fetched from Yahoo & Cached in RAM) ───
        else:
            # 1. CHECK THE CACHE FIRST
            cache_key = f"{symbol}_{time_range}"
            current_time = time.time()
            
            # If we fetched this exact data in the last 5 minutes (300 seconds), serve it instantly!
            if cache_key in history_cache and (current_time - history_cache[cache_key]['time'] < 300):
                return jsonify(history_cache[cache_key]['data'])

            # 2. NOT IN CACHE? FETCH IT.
            ticker = yf.Ticker(symbol)
            
            interval_map = {
                "5d": "15m",   # 1 Week: 15-minute candles
                "1mo": "1d",   # 1 Month: Daily candles
                "1y": "1d",    # 1 Year: Daily candles
                "5y": "1wk"    # 5 Years: Weekly candles
            }
            interval = interval_map.get(time_range, "1d")
            
            hist = ticker.history(period=time_range, interval=interval)
            
            labels = []
            prices = []
            
            if not hist.empty:
                for date, row in hist.iterrows():
                    if time_range == "5d":
                        labels.append(date.strftime("%m-%d %H:%M"))
                    else:
                        labels.append(date.strftime("%Y-%m-%d"))
                        
                    prices.append(round(row['Close'], 2))

            # 3. SAVE THE RESULT TO RAM CACHE FOR NEXT TIME
            response_data = {"labels": labels, "prices": prices}
            history_cache[cache_key] = {'time': current_time, 'data': response_data}

            return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in /price endpoint: {e}")
        return jsonify({"labels": [], "prices": []}), 500


if __name__ == "__main__":
    logger.info("Starting Stocksight API Server...")
    app.run(host="0.0.0.0", port=5000, debug=True)