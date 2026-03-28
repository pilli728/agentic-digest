"""
Telegram bot for quick-adding articles to Agentic Edge.

Setup:
  1. Message @BotFather on Telegram, create a bot, get the token
  2. Set TELEGRAM_BOT_TOKEN in .env
  3. Set QUICK_ADD_SECRET in .env (any random string)
  4. Run: python3 src/telegram_bot.py

Usage:
  Send a URL to the bot → it gets added to your digest
  Send a URL + text → URL gets added with your note as context
  Send /status → see how many articles are queued
"""

import os
import re
import json
import urllib.request
from pathlib import Path

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_URL = os.environ.get("SITE_URL", "http://localhost:8000").rstrip("/")
# If SITE_URL points to the frontend, use the API URL instead
if "vercel" in API_URL or "agenticedge" in API_URL:
    API_URL = os.environ.get("API_URL", "http://localhost:8000")
QUICK_ADD_SECRET = os.environ.get("QUICK_ADD_SECRET", "")

URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')


def send_telegram(chat_id: int, text: str):
    """Send a message back to the user."""
    data = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  Failed to send Telegram message: {e}")


def quick_add(url: str, note: str = "") -> dict:
    """Add an article via the API."""
    data = json.dumps({"url": url, "note": note, "secret": QUICK_ADD_SECRET}).encode()
    req = urllib.request.Request(
        f"{API_URL}/api/quick-add",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"success": False, "message": str(e)}


def handle_message(message: dict):
    """Process an incoming Telegram message."""
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    # /status command
    if text.lower() == "/status":
        try:
            req = urllib.request.Request(f"{API_URL}/api/articles/stats")
            with urllib.request.urlopen(req, timeout=10) as resp:
                stats = json.loads(resp.read())
            send_telegram(chat_id, f"📊 *Agentic Edge Status*\nArticles: {stats.get('total_articles', 0)}\nRanked: {stats.get('ranked', 0)}")
        except Exception as e:
            send_telegram(chat_id, f"Error: {e}")
        return

    # /start command
    if text.lower() == "/start":
        send_telegram(chat_id, "👋 Send me a URL and I'll add it to your digest.\n\nYou can also add a note:\n`https://example.com This is a great article about agents`")
        return

    # Extract URLs from message
    urls = URL_PATTERN.findall(text)

    if not urls:
        send_telegram(chat_id, "No URL found. Send me a link to add it to your digest.")
        return

    for url in urls:
        # Everything after the URL is the note
        note = text.replace(url, "").strip()
        result = quick_add(url, note)

        if result.get("success"):
            title = result.get("title", url)[:60]
            send_telegram(chat_id, f"✅ *Added:* {title}\n{url}")
        else:
            send_telegram(chat_id, f"❌ {result.get('message', 'Failed to add')}")


def poll():
    """Long-poll for Telegram updates."""
    print(f"\n🤖 Telegram bot started. Listening for messages...")
    print(f"   API: {API_URL}")
    print(f"   Press Ctrl+C to stop\n")

    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except Exception as e:
            print(f"  Poll error: {e}")
            import time
            time.sleep(5)


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN in .env")
        print("Get one from @BotFather on Telegram")
        exit(1)
    poll()
