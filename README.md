# Pocket Option 24/7 Market Data Harvester (AI/ML Pipeline)

Production-grade, asynchronous continuous financial candlestick data collector for Pocket Option regular and OTC markets, streaming directly into **Neon Serverless PostgreSQL** with a real-time **FastAPI Web Dashboard** and **Telegram Bot alerts**.

---

## 1. System Architecture

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                       LOCAL MACHINE / RESIDENTIAL AGENT                     │
 │                                                                             │
 │   ┌───────────────────────────────┐     ┌───────────────────────────────┐   │
 │   │   FastAPI Web Dashboard       │◄────┤   1-Click Chrome Bookmarklet  │   │
 │   │   (http://localhost:8000)     │     │   (Client Session Assistant)  │   │
 │   └───────────────┬───────────────┘     └───────────────────────────────┘   │
 │                   │ Controls & Telemetry                                    │
 │                   ▼                                                         │
 │   ┌───────────────────────────────┐     ┌───────────────────────────────┐   │
 │   │  WebSocket Harvester Engine   │────►│     Telegram Notifier Bot     │   │
 │   │  (Engine.IO v4, Auto-Backoff) │     │   (Disconnections & Recovery) │   │
 │   └───────────────┬───────────────┘     └───────────────────────────────┘   │
 └───────────────────┼─────────────────────────────────────────────────────────┘
                     │ SSL Batch Upsert (ON CONFLICT DO NOTHING)
                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                      NEON POSTGRESQL (AWS Cloud Serverless)                 │
 │                                                                             │
 │   • Table: `candles` (Indexed, deduplicated, zero lookahead bias)           │
 │   • Accessible anywhere by your Python AI/ML, PyTorch, & Pandas models      │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Features

- **Continuous 24/7 Collection:** Supports both regular Forex/stocks and proprietary Pocket Option OTC pairs (`EURUSD_otc`, `#AAPL_otc`, etc.).
- **Neon Serverless PostgreSQL:** Configured with connection pooling and atomic deduplication (`UNIQUE(symbol, timeframe, timestamp)`).
- **Zero Lookahead Bias for AI/ML:** Automatically filters out incomplete forming bars so models train exclusively on finalized candles.
- **Client Session Assistant:** Includes a **1-Click Bookmarklet** that enables non-technical clients to sync their session directly from Pocket Option with zero DevTools.
- **Telegram Bot Integration:** Immediate notifications for disconnections, reconnection recoveries, session expirations, and daily totals.
- **Real-Time Web Dashboard:** Single-page dark-mode terminal with live event logs, candle preview tables, telemetry KPIs, and 1-click **Export to CSV**.

---

## 3. Quick Start (Running on Your Local Machine)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Launch the Web Dashboard
```powershell
python run_dashboard.py
```

### Step 3: Open in Browser
Navigate to:
```text
http://localhost:8000
```
- Click **START** to begin harvesting.
- Click **PAUSE** to temporarily pause streaming.
- Click **STOP** to safely shut down the collector.

---

## 4. Client Session Sync (Zero-DevTools)

Because Pocket Option cryptographically binds sessions to the user's public IP address via HMAC signatures, non-technical clients can sync their session in 1 click:

1. Open the Web Dashboard at `http://localhost:8000` and switch to the **Session Assistant** tab.
2. Drag the button labeled **`[Sync Harvester]`** to your browser's **Bookmarks Bar**.
3. In another tab, open and log into [Pocket Option](https://pocketoption.com).
4. Click the **[Sync Harvester]** bookmark.
5. The dashboard will flash green: **"Session updated successfully"**, and the harvester will resume streaming automatically.

---

## 5. Connecting AI/ML Models to Neon PostgreSQL

Your machine learning training scripts (Jupyter Notebook, Google Colab, or PyTorch) can read the collected data directly from Neon:

```python
import pandas as pd
import psycopg2

NEON_URL = os.getenv("DATABASE_URL", "postgresql://username:password@your-neon-host.aws.neon.tech/neondb?sslmode=require")

# Load 1-minute OTC candles directly into Pandas
query = """
    SELECT timestamp, open, high, low, close, volume
    FROM candles
    WHERE symbol = 'EURUSD_otc' AND timeframe = 60
    ORDER BY timestamp ASC;
"""

df = pd.read_sql(query, NEON_URL)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
print(df.head())
```

---

## 6. Docker & Cloud Deployment

### A. Local Container Run (Docker Compose)
```bash
# 1. Copy sample env and edit credentials
cp .env.example .env

# 2. Build and launch container
docker compose up -d --build

# 3. View live logs
docker compose logs -f
```

### B. Heroku Cloud Deployment (Container Stack)
Heroku dynamically provides the web dyno port via `$PORT` and requires no hardcoded ports:

```bash
# 1. Log in to Heroku & Container Registry
heroku login
heroku container:login

# 2. Create your Heroku application
heroku create your-pocket-option-harvester

# 3. Set the stack to Container
heroku stack:set container -a your-pocket-option-harvester

# 4. Configure production environment variables in Heroku
heroku config:set DATABASE_URL="postgresql://user:pass@host/neondb?sslmode=require" -a your-pocket-option-harvester
heroku config:set TELEGRAM_BOT_TOKEN="your_bot_token" -a your-pocket-option-harvester
heroku config:set TELEGRAM_CHAT_ID="your_chat_id" -a your-pocket-option-harvester
heroku config:set PO_UID="142286757" -a your-pocket-option-harvester
heroku config:set PO_SESSION="your_session_string" -a your-pocket-option-harvester
heroku config:set DEFAULT_TIMEFRAME="60" -a your-pocket-option-harvester

# 5. Push code and deploy via Git
git push heroku main

# (Alternatively, deploy via Heroku Container Registry)
# heroku container:push web -a your-pocket-option-harvester
# heroku container:release web -a your-pocket-option-harvester

# 6. Stream live application logs
heroku logs --tail -a your-pocket-option-harvester
```

---

## 7. Configuration (.env)

Copy `.env.example` to `.env`:

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | Neon PostgreSQL pooled connection string |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for alert delivery |
| `PO_SESSION` | Cryptographic PHP-serialized session string |
| `PO_UID` | Pocket Option User ID |
| `DEFAULT_TIMEFRAME` | Default candle bar interval (seconds, default: `60`) |
| `DEFAULT_SYMBOLS` | Comma-separated list of instruments |
| `PORT` | Dynamic port set by Heroku (fallback to `DASHBOARD_PORT`) |
