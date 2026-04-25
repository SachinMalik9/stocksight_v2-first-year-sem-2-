# 📈 StockSight Terminal

> **A Containerized Real-Time Market Intelligence & Sentiment Correlation Suite**

![StockSight Terminal](https://via.placeholder.com/1000x500.png?text=Replace+This+With+A+Screenshot+Of+Your+Terminal)

## 🚀 Overview
StockSight Terminal is a professional-grade financial dashboard designed to solve the "latency gap" between breaking financial news and retail price action. By combining high-frequency market data with Natural Language Processing (NLP), this suite provides real-time correlation between global sentiment and tick-by-tick price movement. 

Built on a fully decoupled **Microservices Architecture**, StockSight ensures sub-millisecond query performance and 100% crash-proof UI stability.

## ✨ Key Features
* **Dual-Stream Data Engine:** Seamlessly toggles between Elasticsearch for live tick data and the Yahoo Finance API for instant historical timeframes (1W, 1M, 1Y).
* **NLP Polarity Scoring:** Live text parsing of financial news and social signals, mapping market "mood" from `-1.0` (Bearish) to `+1.0` (Bullish).
* **Rolling Window Database Logic:** Utilizes custom Elasticsearch `now/d` queries to automatically clean the active session, preventing browser memory bloat and crashing.
* **1-Hour Fallback Seeder:** Ensures the live dashboard is never empty upon container boot by pre-fetching the previous hour of market data while the background workers initialize.
* **Pro-Trading UI:** An immersive, asynchronous "Obsidian" dark-mode terminal powered by ES6+ and Chart.js, polling via REST API without page reloads.

## 🛠️ Technical Stack
* **Backend:** Python 3.10, Flask (RESTful API), Pandas, `yfinance`.
* **Database:** Elasticsearch (NoSQL Time-Series Storage).
* **Frontend:** HTML5, CSS3, vanilla JavaScript (ES6+), Chart.js.
* **Infrastructure:** Docker, Docker Compose (Multi-container Service Discovery).

## 🏗️ Microservices Architecture
The system is divided into isolated Docker containers communicating securely over a private Docker network:
1. **API Node (`api`):** The Flask orchestration layer that handles CORS, serves the frontend data, and manages In-Memory RAM caching.
2. **Database Node (`es_stocksight`):** The Elasticsearch cluster optimized for high-speed time-series indexing.
3. **Async Workers (`price_worker` / `sentiment_worker`):** Independent Python scripts that ingest web data and push it to Elasticsearch without blocking the main API thread.

## ⚙️ Quick Start Installation

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR_USERNAME/stocksight-terminal.git](https://github.com/YOUR_USERNAME/stocksight-terminal.git)
cd stocksight-terminal
