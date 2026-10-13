import os
import asyncio
import asyncpg
import requests
from dotenv import load_dotenv

load_dotenv()

NEON_URL = os.getenv("DATABASE_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

async def test_neon():
    print("Testing Neon PostgreSQL connection...")
    try:
        # Note: channel_binding might need to be stripped for asyncpg if not supported, or clean DSN
        dsn = NEON_URL
        if "channel_binding" in dsn:
            dsn = dsn.replace("&channel_binding=require", "").replace("channel_binding=require&", "")
        conn = await asyncpg.connect(dsn)
        val = await conn.fetchval("SELECT version();")
        print(f"Neon PostgreSQL connected successfully! Version: {val[:60]}...")
        await conn.close()
        return True
    except Exception as e:
        print(f"Neon connection error: {e}")
        return False

def test_telegram():
    print("\nTesting Telegram Bot notification...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🟢 *Pocket Option Harvester Initialized*\n\nConnection test to Telegram Bot successful!",
        "parse_mode": "Markdown",
    }
    try:
        r = requests.post(url, json=payload, timeout=8)
        data = r.json()
        if data.get("ok"):
            print("Telegram notification delivered successfully!")
            return True
        else:
            print(f"Telegram returned error: {data}")
            return False
    except Exception as e:
        print(f"Telegram test error: {e}")
        return False

async def main():
    neon_ok = await test_neon()
    tg_ok = test_telegram()
    print(f"\nSummary: Neon={neon_ok}, Telegram={tg_ok}")

if __name__ == "__main__":
    asyncio.run(main())
