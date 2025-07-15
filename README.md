# Smart Money Bot

This bot scans for 13D and 13F filings from credible investors in penny stocks and sends alerts to Discord.

## Features
- Filters only elite investors
- Includes exchange check and news proof
- Sends clean Discord embeds
- Designed for free 24/7 hosting

## Setup

1. Copy `.env.example` to `.env` and add your Discord webhook.
2. Install dependencies:
    pip install -r requirements.txt
3. Run the bot:
    python bot.py

## Deployment

Ready for Railway and UptimeRobot.

Add `DISCORD_WEBHOOK_URL` as a Railway environment variable.

---
