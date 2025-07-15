import requests
import datetime
import time
import os
import logging
from keep_alive import keep_alive
import yfinance as yf
import json
import os

SEEN_FILE = "seen_filings.json"

# Load previously seen filings
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(tuple(entry) for entry in json.load(f))
else:
    seen = set()

def is_stock_active(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        exchange = info.get("exchange", "")
        tradable_exchanges = ["NMS", "NYQ", "ASE"]  # NASDAQ, NYSE, AMEX

        return (
            info.get("regularMarketPrice", 0) > 0 and
            info.get("regularMarketVolume", 0) > 0 and
            exchange in tradable_exchanges
        )
    except:
        return False

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CREDIBLE_INVESTORS = [
    "Carl Icahn", "Michael Burry", "Renaissance Technologies",
    "Citadel Advisors", "Soros Fund Management", "Ray Dalio",
    "Greenlight Capital", "Coatue Management", "Paul Tudor Jones"
]

EXCHANGES = ["OTC", "NASDAQ", "NYSE"]

def fetch_filings():
    try:
        filings = [
            {
                "ticker": "ABCD",
                "investor": "Michael Burry",
                "type": "13D",
                "url": "https://www.sec.gov/Archives/edgar/data/0000000000/0000000000-25-000001-index.htm",
                "exchange": "NASDAQ"
            },
        ]
        return filings
    except Exception as e:
        logging.error(f"Error fetching filings: {e}")
        return []

def find_news(ticker):
    try:
        return f"https://finance.yahoo.com/quote/{ticker}/news"
    except Exception as e:
        logging.error(f"Error finding news for {ticker}: {e}")
        return None

def send_discord_alert(filing, news_url=None):
    try:
        message = {
            "content": None,
            "embeds": [
                {
                    "title": f"🚨 Smart Money Alert - ${filing['ticker']}",
                    "color": 5814783,
                    "fields": [
                        {"name": "🏦 Investor", "value": filing["investor"], "inline": True},
                        {"name": "📄 Filing Type", "value": filing["type"], "inline": True},
                        {"name": "🏛️ Exchange", "value": filing["exchange"], "inline": True},
                        {"name": "🔗 Filing", "value": filing["url"], "inline": False},
                    ],
                    "footer": {
                        "text": "Smart Money Bot"
                    },
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
            ]
        }
        if news_url:
            message["embeds"][0]["fields"].append({"name": "🗞️ Related News", "value": news_url, "inline": False})

        requests.post(DISCORD_WEBHOOK_URL, json=message)
    except Exception as e:
        logging.error(f"Error sending Discord alert: {e}")

def run_bot():
    seen = set()
    while True:
        now = datetime.datetime.now(datetime.UTC)
        if now.weekday() >= 5 or not (13 <= now.hour < 20):
            print("Outside market hours. Sleeping...")
            time.sleep(60 * 15)
            continue
filings = fetch_filings()
for filing in filings:
    key = (filing['ticker'], filing['investor'], filing['type'])

    if key in seen:
        continue

    if (
        filing['investor'] in CREDIBLE_INVESTORS and
        filing['exchange'] in EXCHANGES and
        is_stock_active(filing['ticker'])
    ):
        news_url = find_news(filing['ticker'])
        send_discord_alert(filing, news_url)
        seen.add(key)

        # ✅ Save updated seen set to disk
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen), f)

time.sleep(60 * 15)  # Wait before checking again

if __name__ == "__main__":
    keep_alive()
    run_bot()
